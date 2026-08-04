import discord
from discord.ext import commands
from discord import app_commands
import config
from datetime import datetime
from discord.app_commands import Choice

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # apenas cargos iguais e superiores à Diretoria
    async def verificar_diretoria(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
            
        cargo_diretoria = interaction.guild.get_role(config.CARGO_DIRETORIA)
        
        if not cargo_diretoria:
            await interaction.response.send_message("⚠️ [ ERRO ] Cargo de Diretoria não encontrado nas configurações.", ephemeral=True)
            return False
            
        if interaction.user.top_role.position >= cargo_diretoria.position:
            return True
            
        await interaction.response.send_message("⚠️ [ NEGADO ] Você não possui hierarquia (Diretoria ou superior) para usar este comando.", ephemeral=True)
        return False

    # ---------------------------------------------------------
    # COMANDO: PATRULHAMENTOS   
    # ---------------------------------------------------------
    @app_commands.command(name="patrulhamentos", description="Consulta quantos patrulhamentos aprovados um militar possui.")
    @app_commands.describe(militar="Militar que você deseja consultar (Ex: @Meliante)")
    async def patrulhamentos(self, interaction: discord.Interaction, militar: discord.Member):
        await interaction.response.defer(ephemeral=False)
        
        canal_log = interaction.guild.get_channel(config.CANAL_LOG_PATRULHA)
        if not canal_log:
            await interaction.followup.send("⚠️ [ ERRO ] Canal de logs de patrulha não encontrado nas configurações.")
            return
        
        contagem = 0
        async for msg in canal_log.history(limit=2000):
            if msg.author == self.bot.user:
                if f"ID: {militar.id}" in msg.content and "✅ APROVADO" in msg.content:
                    contagem += 1
                    
        embed = discord.Embed(
            title="📊 Relatório de Serviço",
            description=f"O militar {militar.mention} possui **{contagem}** patrulhamento(s) aprovado(s) registrados no sistema.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Consulta via banco de dados do Discord")
        await interaction.followup.send(embed=embed)


    # ---------------------------------------------------------
    # COMANDO: APLICAR EXÍLIO   
    # ---------------------------------------------------------
    @app_commands.command(name="exilar", description="Exila um militar e registra no sistema.")
    @app_commands.describe(
        usuario="Militar a ser exilado (Menção ou ID)",
        nick="Nick/Nome de registro do militar",
        cargo="Cargo que ele ocupava",
        prazo="Prazo textual que vai no relatório (Ex: 7 dias, Permanente)",
        motivo="Motivo detalhado da punição",
        acao_discord="O que o bot deve fazer com a conta dele no servidor?",
        comprovacao_texto="Link da prova (Opcional se enviar o arquivo abaixo)",
        comprovacao_arquivo="Anexe Print/Vídeo (Opcional se enviar o link acima)"
    )
    @app_commands.choices(acao_discord=[
        Choice(name="Expulsar (Kick) - Ideal para prazos curtos", value="kick"),
        Choice(name="Banir - Ideal para prazos permanentes", value="ban")
    ])
    async def exilar(self, interaction: discord.Interaction, usuario: discord.User, nick: str, cargo: str, prazo: str, motivo: str, acao_discord: str, comprovacao_texto: str = None, comprovacao_arquivo: discord.Attachment = None):
        if not await self.verificar_diretoria(interaction): return
        
        # exige pelo menos 1 prova
        if not comprovacao_texto and not comprovacao_arquivo:
            await interaction.response.send_message("⚠️ [ ERRO ] Você deve fornecer uma prova! Preencha o link no campo de texto OU anexe um arquivo.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        if not canal:
            await interaction.followup.send("⚠️ Erro: Chat de Exílio não encontrado nas configurações.")
            return

        # limite de ram
        arquivos = []
        if comprovacao_arquivo:
            if comprovacao_arquivo.size > 8388608: # limite de 8mb
                await interaction.followup.send("⚠️ [ ALERTA DE RAM ] O arquivo anexado é muito pesado (maior que 8MB). Por favor, use um link do YouTube/Imgur no campo 'comprovacao_texto' para não travar o sistema.")
                return
            arquivos.append(await comprovacao_arquivo.to_file())

        texto_prova = comprovacao_texto if comprovacao_texto else "Provas anexadas abaixo."
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        mensagem = (
            "╭・:CYBER:  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
            "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑬𝑿Í𝑳𝑰𝑶*\n\n"
            f"**𝐌𝐈𝐋𝐈𝐓𝐀𝐑:** {usuario.mention}\n"
            f"**𝐍𝐈𝐂𝐊:** {nick}\n\n"
            f"**𝐂𝐀𝐑𝐆𝐎:** {cargo}\n\n"
            f"**𝐏𝐑𝐀𝐙𝐎:** {prazo}\n\n"
            f"**𝐌𝐎𝐓𝐈𝐕𝐎:** — {motivo}\n"
            f"**𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n• {texto_prova}\n\n"
            f"**𝐀𝐔𝐓𝐎𝐑𝐈𝐙𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
            f"**𝐃𝐀𝐓𝐀:** {data_atual}\n\n"
            "**STATUS: EXILADO**\n"
            f"-# UserID:{usuario.id}"
        )

        await canal.send(content=mensagem, files=arquivos)
        
        try:
            membro_presente = interaction.guild.get_member(usuario.id)
            if acao_discord == "ban":
                await interaction.guild.ban(usuario, reason=f"Exilado por {interaction.user.name} - Prazo: {prazo}")
                acao_texto = "banido"
            else:
                if membro_presente:
                    await interaction.guild.kick(usuario, reason=f"Exilado por {interaction.user.name} - Prazo: {prazo}")
                    acao_texto = "expulso"
                else:
                    await interaction.followup.send(f"✅ Relatório criado! Aviso: {usuario.mention} **já tinha saído do servidor**, portanto não foi expulso pelo bot (mas o registro foi salvo).")
                    return
                
            await interaction.followup.send(f"✅ Registro criado! {usuario.mention} foi exilado e **{acao_texto}** do servidor com sucesso.")
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ O relatório foi salvo no chat, mas o Discord **bloqueou a ação** automática. Remova-o manualmente!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Relatório salvo, mas ocorreu um erro com o Discord: {e}")


    # ---------------------------------------------------------
    # COMANDO: APLICAR BLACKLIST    
    # ---------------------------------------------------------
    @app_commands.command(name="blacklist", description="Aplica blacklist a um usuário e registra no sistema.")
    @app_commands.describe(
        usuario="Usuário punido (Menção ou ID)",
        nick="Nick/Nome do usuário",
        prazo="Prazo textual que vai no relatório (Ex: 30 dias, Permanente)",
        motivo="Motivo detalhado da blacklist",
        acao_discord="O que o bot deve fazer com a conta dele no servidor?",
        comprovacao_texto="Link da prova (Opcional se enviar o arquivo abaixo)",
        comprovacao_arquivo="Anexe Print/Vídeo (Opcional se enviar o link acima)"
    )
    @app_commands.choices(acao_discord=[
        Choice(name="Banir do Servidor", value="ban"),
        Choice(name="Expulsar (Kick) do Servidor", value="kick")
    ])
    async def blacklist(self, interaction: discord.Interaction, usuario: discord.User, nick: str, prazo: str, motivo: str, acao_discord: str, comprovacao_texto: str = None, comprovacao_arquivo: discord.Attachment = None):
        if not await self.verificar_diretoria(interaction): return
        
        # exige pelo menos 1 prova
        if not comprovacao_texto and not comprovacao_arquivo:
            await interaction.response.send_message("⚠️ [ ERRO ] Você deve fornecer uma prova! Preencha o link no campo de texto OU anexe um arquivo.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        canal = interaction.guild.get_channel(config.CANAL_BLACKLIST)
        if not canal:
            await interaction.followup.send("⚠️ Erro: Chat de Blacklist não encontrado nas configurações.")
            return

        # limite de ram
        arquivos = []
        if comprovacao_arquivo:
            if comprovacao_arquivo.size > 8388608: # limite de 8mb
                await interaction.followup.send("⚠️ [ ALERTA DE RAM ] O arquivo anexado é muito pesado (maior que 8MB). Por favor, use um link do YouTube/Imgur no campo 'comprovacao_texto' para não travar o sistema.")
                return
            arquivos.append(await comprovacao_arquivo.to_file())

        texto_prova = comprovacao_texto if comprovacao_texto else "Provas anexadas abaixo."
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        mensagem = (
            "╭・:CYBER:  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
            "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑩𝑳𝑨𝑪𝑲𝑳𝑰𝑺𝑻*\n\n"
            f"**𝐔𝐒𝐔Á𝐑𝐈𝐎:** {usuario.mention}\n"
            f"**𝐍𝐈𝐂𝐊:** {nick}\n\n"
            f"**𝐏𝐑𝐀𝐙𝐎:** {prazo}\n\n"
            f"**𝐌𝐎𝐓𝐈𝐕𝐎:** — {motivo}\n"
            f"**𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n• {texto_prova}\n\n"
            f"**𝐀𝐔𝐓𝐎𝐑𝐈𝐙𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
            f"**𝐃𝐀𝐓𝐀:** {data_atual}\n\n"
            "**STATUS: BLACKLIST**\n"
            f"-# UserID:{usuario.id}"
        )

        await canal.send(content=mensagem, files=arquivos)
        
        try:
            membro_presente = interaction.guild.get_member(usuario.id)
            if acao_discord == "ban":
                await interaction.guild.ban(usuario, reason=f"Blacklist por {interaction.user.name} - Prazo: {prazo}")
                acao_texto = "banido"
            else:
                if membro_presente:
                    await interaction.guild.kick(usuario, reason=f"Blacklist por {interaction.user.name} - Prazo: {prazo}")
                    acao_texto = "expulso"
                else:
                    await interaction.followup.send(f"✅ Relatório criado! Aviso: {usuario.mention} **já tinha saído do servidor**, portanto não foi expulso pelo bot (mas o registro foi salvo).")
                    return
                
            await interaction.followup.send(f"✅ Registro criado! {usuario.mention} tomou Blacklist e foi **{acao_texto}** do servidor com sucesso.")
        except discord.Forbidden:
            await interaction.followup.send(f"⚠️ O relatório foi salvo, mas o Discord **bloqueou a ação** automática. Remova-o manualmente!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Relatório salvo, mas ocorreu um erro com o Discord: {e}")


    # ---------------------------------------------------------
    # COMANDO: INFO EXÍLIO   
    # ---------------------------------------------------------
    @app_commands.command(name="infoexilio", description="Puxa a ficha de exílio de um membro do banco de dados cibernético.")
    @app_commands.describe(usuario="Membro a ser consultado (Menção ou ID)")
    async def infoexilio(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        
        async for msg in canal.history(limit=2000):
            if msg.author == self.bot.user and f"UserID:{usuario.id}" in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                await interaction.followup.send(f"📄 **Registro Encontrado no Sistema:**\n\n{conteudo_limpo}")
                return
        
        await interaction.followup.send(f"❌ A ficha do usuário {usuario.mention} está limpa. Nenhum exílio encontrado.")


    # ---------------------------------------------------------
    # COMANDO: INFO BLACKLIST
    # ---------------------------------------------------------
    @app_commands.command(name="infoblacklist", description="Puxa a ficha de blacklist de um indivíduo do banco de dados cibernético.")
    @app_commands.describe(usuario="Indivíduo a ser consultado (Menção ou ID)")
    async def infoblacklist(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_BLACKLIST)
        
        async for msg in canal.history(limit=2000):
            if msg.author == self.bot.user and f"UserID:{usuario.id}" in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                await interaction.followup.send(f"📄 **Registro Encontrado no Sistema:**\n\n{conteudo_limpo}")
                return
        
        await interaction.followup.send(f"❌ A ficha de {usuario.mention} está limpa. Nenhuma blacklist encontrada.")

async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
