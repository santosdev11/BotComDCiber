import discord
from discord.ui import Modal, TextInput, View, Button
import config

class MotivoModal(Modal, title='Relatorio de Avaliacao'):
    motivo = TextInput(label='Motivo / Observacao', style=discord.TextStyle.paragraph, required=True)

    def __init__(self, acao, cargo_id, original_log_msg, tipo):
        super().__init__()
        self.acao = acao
        self.cargo_id = cargo_id
        self.original_log_msg = original_log_msg
        self.tipo = tipo

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Processando a avaliacao de {self.tipo}...", ephemeral=True)
        
        conteudo_log = self.original_log_msg.content
        linhas = conteudo_log.split("\n")
        
        try:
            membro_id = int(linhas[1].split("ID: ")[1])
            canal_id = int(linhas[2].split("ID: ")[1])
            msg_id = int(linhas[3].split("**Mensagem Original:** ")[1])
            
            membro_alvo = interaction.guild.get_member(membro_id)
            canal_original = interaction.guild.get_channel(canal_id)
            mensagem_original = await canal_original.fetch_message(msg_id)
        except Exception as e:
            await interaction.followup.send(f"[ ERRO ] Nao foi possivel encontrar os dados da mensagem original. Ela pode ter sido deletada. Erro: {e}", ephemeral=True)
            return

        novo_conteudo_log = f"{conteudo_log}\n\n━━━━━━━━━━━━━━━━━━━━━━━\n**[ AVALIADO POR {interaction.user.mention} - {self.acao} ]**\n**Motivo:** {self.motivo.value}\n\n-# made by santosdev11"
        await self.original_log_msg.edit(content=novo_conteudo_log, view=None)

        cor_acao = "🟢 APROVADO" if "APROVADO" in self.acao else "🔴 NEGADO"
        resposta_publica = f"{membro_alvo.mention} O seu relatorio de **{self.tipo}** foi avaliado!\n\n**Status:** {cor_acao}\n**Avaliador:** {interaction.user.mention}\n**Motivo:** {self.motivo.value}\n\n-# made by santosdev11"
        
        try:
            await mensagem_original.reply(resposta_publica)
            await mensagem_original.remove_reaction("⏳", interaction.client.user)
            await mensagem_original.add_reaction("✅" if "APROVADO" in self.acao else "❌")
        except:
            pass # Ignora se o bot n tiver permissao de reagir

        erro_cargo = False
        if self.tipo == "AVAL" and "APROVADO" in self.acao:
            cargo_aval = interaction.guild.get_role(config.CARGO_AVAL_CONCEDIDO)
            
            if cargo_aval and membro_alvo:
                try:
                    await membro_alvo.add_roles(cargo_aval)
                except discord.Forbidden:
                    erro_cargo = True
                    await interaction.followup.send("[ ALERTA ] Discord bloqueou a entrega do cargo (Hierarquia de cargos baixa).", ephemeral=True)
            
            canal_liberado = interaction.guild.get_channel(config.CANAL_AVAL_LIBERADO)
            if canal_liberado:
                await canal_liberado.send(f"✅ **AVAL CONCEDIDO**\n\n**Responsavel:** {interaction.user.mention}\n**Solicitante:** {membro_alvo.mention if membro_alvo else 'Desconhecido'}\n\n**Informacoes originarias na LOG.**")

        if not erro_cargo:
            await interaction.followup.send(f"Avaliacao concluida com sucesso.", ephemeral=True)

class BaseAvaliacaoView(View):
    def __init__(self, cargo_necessario, tipo):
        super().__init__(timeout=None)
        self.cargo_necessario = cargo_necessario
        self.tipo = tipo
        
        btn_aprovar = Button(label="Aprovar", style=discord.ButtonStyle.success, custom_id=f"btn_aprovar_{tipo}", emoji="✅")
        btn_aprovar.callback = self.aprovar
        self.add_item(btn_aprovar)
        
        btn_negar = Button(label="Negar", style=discord.ButtonStyle.danger, custom_id=f"btn_negar_{tipo}", emoji="❌")
        btn_negar.callback = self.negar
        self.add_item(btn_negar)

    async def verificar_permissao(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True

        if not discord.utils.get(interaction.user.roles, id=self.cargo_necessario):
            await interaction.response.send_message("[ NEGADO ] Voce nao tem autorizacao para avaliar.", ephemeral=True)
            return False
        
        return True
        
    async def aprovar(self, interaction: discord.Interaction):
        if await self.verificar_permissao(interaction):
            await interaction.response.send_modal(MotivoModal("✅ APROVADO", self.cargo_necessario, interaction.message, self.tipo))

    async def negar(self, interaction: discord.Interaction):
        if await self.verificar_permissao(interaction):
            await interaction.response.send_modal(MotivoModal("❌ NEGADO", self.cargo_necessario, interaction.message, self.tipo))
