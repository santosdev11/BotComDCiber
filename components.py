import discord
from discord.ui import Modal, TextInput, View, Button
import config
import re

class MotivoModal(Modal, title='Relatório de Avaliação'):
    motivo = TextInput(label='Motivo / Observação', style=discord.TextStyle.paragraph, required=True)

    def __init__(self, acao, cargo_id, original_log_msg, tipo):
        super().__init__()
        self.acao = acao
        self.cargo_id = cargo_id
        self.original_log_msg = original_log_msg
        self.tipo = tipo

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Processando avaliação de {self.tipo}.", ephemeral=True)
        
        conteudo_log = self.original_log_msg.content
        linhas = conteudo_log.strip().split("\n")

        try:
            membro_id = int(linhas[1].split("ID: ")[1])
            ultima_linha = linhas[-1]
            canal_id = int(ultima_linha.split("CanalID:")[1].split(" ")[0])
            msg_id = int(ultima_linha.split("MsgID:")[1])
        except Exception:
            await interaction.followup.send("[ ERRO CRÍTICO ] Falha de integridade: IDs de rodapé corrompidos.", ephemeral=True)
            try:
                await self.original_log_msg.edit(content=f"{conteudo_log[:1900]}\n\n**[ ERRO ] RODAPÉ CORROMPIDO. RELATÓRIO INVALIDADO.**", view=None)
            except: pass
            return

        membro_alvo = interaction.guild.get_member(membro_id)
        canal_original = interaction.guild.get_channel(canal_id)
        
        try:
            mensagem_original = await canal_original.fetch_message(msg_id)
        except Exception:
            await interaction.followup.send("[ AVISO ] Mensagem de origem não localizada. Avaliação abortada.", ephemeral=True)
            try:
                await self.original_log_msg.edit(content=f"{conteudo_log[:1900]}\n\n**[ CANCELADO ] Mensagem de origem deletada pelo autor.**", view=None)
            except: pass
            return

        conteudo_sem_rodape = "\n".join(linhas[:-1])
        motivo_texto = self.motivo.value[:300] + "..." if len(self.motivo.value) > 300 else self.motivo.value
        
        bloco_avaliacao = f"\n\n━━━━━━━━━━━━━━━━━━━━━━━\n**[ AVALIADO POR {interaction.user.mention} - {self.acao} ]**\n**Motivo:** {motivo_texto}\n{ultima_linha}"
        
        espaco_livre = 2000 - len(bloco_avaliacao)
        
        if len(conteudo_sem_rodape) > espaco_livre:
            conteudo_sem_rodape = conteudo_sem_rodape[:espaco_livre - 50] + "\n...[TEXTO REDUZIDO PARA AVALIAÇÃO]"
            
        novo_conteudo_log = f"{conteudo_sem_rodape}{bloco_avaliacao}"
        
        try:
            await self.original_log_msg.edit(content=novo_conteudo_log, view=None)
        except Exception as e:
            await interaction.followup.send(f"[ ERRO CRÍTICO ] Falha na API ao editar log: {e}", ephemeral=True)
            return

        cor_acao = "APROVADO" if "APROVADO" in self.acao else "NEGADO"
        mencao_usuario = membro_alvo.mention if membro_alvo else f"<@{membro_id}> (Fora do Servidor)"
        
        resposta_publica = f"{mencao_usuario} Relatório de **{self.tipo}** processado.\n\n**Status:** {cor_acao}\n**Avaliador:** {interaction.user.mention}\n**Motivo:** {motivo_texto}"
        
        try:
            await mensagem_original.reply(resposta_publica)
            await mensagem_original.remove_reaction("⏳", interaction.client.user)
            await mensagem_original.add_reaction("✅" if "APROVADO" in self.acao else "❌")
        except:
            pass 

        erro_cargo = False
        if self.tipo == "AVAL" and "APROVADO" in self.acao:
            cargo_aval = interaction.guild.get_role(config.CARGO_AVAL_CONCEDIDO)
            
            if cargo_aval and membro_alvo:
                try:
                    await membro_alvo.add_roles(cargo_aval)
                except discord.Forbidden:
                    erro_cargo = True
                    await interaction.followup.send("[ ERRO ] Falha na atribuição de cargo por hierarquia de permissões.", ephemeral=True)
            
            canal_liberado = interaction.guild.get_channel(config.CANAL_AVAL_LIBERADO)
            if canal_liberado:
                
                inicio_match = re.search(r'(?i)(in[ií]cio:[^\n]+)', conteudo_sem_rodape)
                fim_match = re.search(r'(?i)(fim:[^\n]+)', conteudo_sem_rodape)
                
                obs_linhas = []
                if inicio_match:
                    obs_linhas.append(inicio_match.group(1).strip())
                if fim_match:
                    obs_linhas.append(fim_match.group(1).strip())
                    
                texto_observacao = "~ " + "\n~ ".join(obs_linhas) if obs_linhas else "~ Avaliado via sistema cibernético."

                msg_formatada = (
                    "[ AVAL CONCEDIDO ]\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Responsável pelo Aval:\n"
                    f"~ {interaction.user.mention}\n\n"
                    "Solicitante do Aval:\n"
                    f"~ {mencao_usuario}\n\n"
                    "Status do Aval:\n"
                    "~ Concedido\n\n"
                    "Motivo do Aval:\n"
                    f"~ {motivo_texto}\n\n"
                    "Observações:\n"
                    f"{texto_observacao}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Data e Horário: Discord Fornece.\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━"
                )
                try:
                    await canal_liberado.send(msg_formatada)
                except:
                    pass

        if not erro_cargo:
            await interaction.followup.send("Avaliação registrada.", ephemeral=True)

class BaseAvaliacaoView(View):
    def __init__(self, cargo_necessario, tipo):
        super().__init__(timeout=None)
        self.cargo_necessario = cargo_necessario
        self.tipo = tipo
        
        btn_aprovar = Button(label="Aprovar", style=discord.ButtonStyle.success, custom_id=f"btn_aprovar_{tipo}")
        btn_aprovar.callback = self.aprovar
        self.add_item(btn_aprovar)
        
        btn_negar = Button(label="Negar", style=discord.ButtonStyle.danger, custom_id=f"btn_negar_{tipo}")
        btn_negar.callback = self.negar
        self.add_item(btn_negar)

    async def verificar_permissao(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True

        if not discord.utils.get(interaction.user.roles, id=self.cargo_necessario):
            await interaction.response.send_message("Acesso negado. Patente insuficiente para avaliação.", ephemeral=True)
            return False
        
        return True
        
    async def aprovar(self, interaction: discord.Interaction):
        if await self.verificar_permissao(interaction):
            await interaction.response.send_modal(MotivoModal("✅ APROVADO", self.cargo_necessario, interaction.message, self.tipo))

    async def negar(self, interaction: discord.Interaction):
        if await self.verificar_permissao(interaction):
            await interaction.response.send_modal(MotivoModal("❌ NEGADO", self.cargo_necessario, interaction.message, self.tipo))
