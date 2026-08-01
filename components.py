import discord
from discord.ui import Modal, TextInput, View, Button
import config

class MotivoModal(Modal, title='Relatorio de Avaliacao'):
    motivo = TextInput(label='Motivo / Observacao do Admin', style=discord.TextStyle.paragraph, required=True)

    def __init__(self, acao, log_channel_id, cargo_id, original_msg_content, tipo, membro_alvo=None):
        super().__init__()
        self.acao = acao
        self.log_channel_id = log_channel_id
        self.cargo_id = cargo_id
        self.original_msg_content = original_msg_content
        self.tipo = tipo
        self.membro_alvo = membro_alvo

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Processando a avaliacao de {self.tipo}...", ephemeral=True)
        
        await interaction.message.edit(content=f"{self.original_msg_content}\n\n**[ AVALIADO POR {interaction.user.mention} - {self.acao} ]**", view=None)
        
        canal_log = interaction.guild.get_channel(self.log_channel_id)
        log_text = f"**Logs de {self.tipo}**\nStatus: {self.acao}\nAvaliador: {interaction.user.mention}\nMotivo: {self.motivo.value}\n\n**Mensagem Original:**\n{self.original_msg_content}\n\n-# made by santosdev11"
        await canal_log.send(log_text)

        if self.tipo == "AVAL" and self.acao == "✅ APROVADO":
            cargo_aval = interaction.guild.get_role(config.CARGO_AVAL_CONCEDIDO)
            erro_cargo = False
            
            if cargo_aval and self.membro_alvo:
                try:
                    await self.membro_alvo.add_roles(cargo_aval)
                except discord.Forbidden:
                    erro_cargo = True
                    await interaction.followup.send("[ ALERTA ] Aval aprovado e registrado nas Logs. Porem, o Discord bloqueou a entrega do cargo. O meu cargo no servidor deve estar ACIMA do cargo 'Aval Concedido' nas configuracoes.", ephemeral=True)
                except Exception as e:
                    erro_cargo = True
                    await interaction.followup.send(f"[ ERRO ] Falha desconhecida ao entregar o cargo: {e}", ephemeral=True)
            
            canal_liberado = interaction.guild.get_channel(config.CANAL_AVAL_LIBERADO)
            if canal_liberado:
                await canal_liberado.send(f"✅ **AVAL CONCEDIDO**\n\n**Responsavel:** {interaction.user.mention}\n**Solicitante:** {self.membro_alvo.mention if self.membro_alvo else 'Desconhecido'}\n\n**Informacoes originarias na LOG.**")

        if not erro_cargo if self.tipo == "AVAL" and self.acao == "✅ APROVADO" else True:
            await interaction.followup.send(f"Avaliacao concluida com sucesso.", ephemeral=True)

class BaseAvaliacaoView(View):
    def __init__(self, cargo_necessario, canal_log, tipo):
        super().__init__(timeout=None)
        self.cargo_necessario = cargo_necessario
        self.canal_log = canal_log
        self.tipo = tipo

    async def verificar_permissao(self, interaction: discord.Interaction):
        if not discord.utils.get(interaction.user.roles, id=self.cargo_necessario):
            await interaction.response.send_message("[ NEGADO ] Voce nao tem autorizacao para avaliar este documento.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aprovar", style=discord.ButtonStyle.success, custom_id="btn_aprovar", emoji="✅")
    async def aprovar(self, interaction: discord.Interaction, button: Button):
        if await self.verificar_permissao(interaction):
            membro = interaction.message.mentions[0] if interaction.message.mentions else None
            await interaction.response.send_modal(MotivoModal("✅ APROVADO", self.canal_log, self.cargo_necessario, interaction.message.content, self.tipo, membro))

    @discord.ui.button(label="Negar", style=discord.ButtonStyle.danger, custom_id="btn_negar", emoji="❌")
    async def negar(self, interaction: discord.Interaction, button: Button):
        if await self.verificar_permissao(interaction):
            membro = interaction.message.mentions[0] if interaction.message.mentions else None
            await interaction.response.send_modal(MotivoModal("❌ NEGADO", self.canal_log, self.cargo_necessario, interaction.message.content, self.tipo, membro))