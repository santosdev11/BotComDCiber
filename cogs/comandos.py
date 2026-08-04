import discord
from discord.ext import commands
from discord import app_commands
import config
from datetime import datetime
from discord.app_commands import Choice

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def verificar_diretoria(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            return True
            
        cargo_diretoria = interaction.guild.get_role(config.CARGO_DIRETORIA)
        
        if not cargo_diretoria:
            await interaction.response.send_message("Erro interno: Cargo de Diretoria não configurado.", ephemeral=True)
            return False
            
        if interaction.user.top_role.position >= cargo_diretoria.position:
            return True
            
        await interaction.response.send_message("Acesso negado. Patente insuficiente para esta ação.", ephemeral=True)
        return False

    # ---------------------------------------------------------
    # COMANDO: HELP  
    # ---------------------------------------------------------
    @app_commands.command(name="help", description="Lista os comandos disponíveis no sistema.")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<:CYBER:1523690802021138563> Painel de Comandos - Defesa Cibernética",
            description="Comandos operacionais disponíveis no sistema:",
            color=discord.Color.dark_theme()
        )
        
        embed.add_field(name="`/patrulhamentos`", value="Consulta a quantidade de patrulhas aprovadas de um militar.\nAcesso: Livre", inline=False)
        embed.add_field(name="`/exilar`", value="Gera relatório, exila e expulsa/bane o alvo do servidor.\nAcesso: Diretoria+", inline=False)
        embed.add_field(name="`/blacklist`", value="Gera relatório, aplica blacklist e expulsa/bane o alvo.\nAcesso: Diretoria+", inline=False)
        embed.add_field(name="`/infoexilio`", value="Puxa o histórico de exílio de um membro.\nAcesso: Livre", inline=False)
        embed.add_field(name="`/infoblacklist`", value="Puxa o histórico de blacklist de um indivíduo.\nAcesso: Livre", inline=False)
        
        embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------------------------------------------------------
    # COMANDO: PATRULHAMENTOS  
    # ---------------------------------------------------------
    @app_commands.command(name="patrulhamentos", description="Consulta quantos patrulhamentos aprovados um militar possui.")
    @app_commands.describe(militar="Militar a ser consultado (Ex: @Meliante)")
    async def patrulhamentos(self, interaction: discord.Interaction, militar: discord.Member):
        await interaction.response.defer(ephemeral=False)
        
        canal_log = interaction.guild.get_channel(config.CANAL_LOG_PATRULHA)
        if not canal_log:
            await interaction.followup.send("Erro de configuração: canal de logs não localizado.")
            return
        
        contagem = 0
        async for msg in canal_log.history(limit=10000):
            if msg.author == self.bot.user:
                if f"ID: {militar.id}" in msg.content and "✅ APROVADO" in msg.content:
                    contagem += 1
                    
        embed = discord.Embed(
            title="Relatório de Serviço",
            description=f"Constam **{contagem}** patrulhamentos aprovados no registro de {militar.mention}.",
            color=discord.Color.dark_theme()
        )
        embed.set_footer(text="Consulta realizada via banco de logs")
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
        acao_discord="Ação a ser executada na conta",
        comprovacao_texto="Link da prova (Opcional se enviar arquivo)",
        comprovacao_arquivo="Anexo de Print/Vídeo (Opcional se enviar link)"
    )
    @app_commands.choices(acao_discord=[
        Choice(name="Expulsar (Kick)", value="kick"),
        Choice(name="Banir (Ban)", value="ban")
    ])
    async def exilar(self, interaction: discord.Interaction, usuario: discord.User, nick: str, cargo: str, prazo: str, motivo: str, acao_discord: str, comprovacao_texto: str = None, comprovacao_arquivo: discord.Attachment = None):
        if not await self.verificar_diretoria(interaction): return
        
        if not comprovacao_texto and not comprovacao_arquivo:
            await interaction.response.send_message("Ação cancelada: É obrigatório fornecer ao menos uma prova (link ou anexo).", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        if not canal:
            await interaction.followup.send("Erro interno: Canal de Exílio não definido.")
            return

        arquivos = []
        if comprovacao_arquivo:
            if comprovacao_arquivo.size > 8388608:
                await interaction.followup.send("Arquivo rejeitado: tamanho superior a 8MB. Utilize um link externo no campo de texto.")
                return
            arquivos.append(await comprovacao_arquivo.to_file())

        texto_prova = comprovacao_texto if comprovacao_texto else "Provas anexadas neste registro."
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        mensagem = (
            "╭・<:CYBER:1523690802021138563>  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
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
                await interaction.guild.ban(usuario, reason=f"Exílio autorizado por {interaction.user.name} - Prazo: {prazo}")
                acao_texto = "banido"
            else:
                if membro_presente:
                    await interaction.guild.kick(usuario, reason=f"Exílio autorizado por {interaction.user.name} - Prazo: {prazo}")
                    acao_texto = "expulso"
                else:
                    await interaction.followup.send(f"Registro processado. {usuario.mention} já não se encontra no servidor, remoção ignorada.")
                    return
                
            await interaction.followup.send(f"Operação concluída. {usuario.mention} foi exilado e {acao_texto} do servidor.")
        except discord.Forbidden:
            await interaction.followup.send("O relatório foi registrado, mas o sistema bloqueou a ação no usuário por hierarquia de cargos. Remova-o manualmente.")
        except Exception as e:
            await interaction.followup.send(f"Relatório salvo. Ocorreu uma falha na API ao interagir com o usuário: {e}")


    # ---------------------------------------------------------
    # COMANDO: APLICAR BLACKLIST  
    # ---------------------------------------------------------
    @app_commands.command(name="blacklist", description="Aplica blacklist a um usuário e registra no sistema.")
    @app_commands.describe(
        usuario="Usuário punido (Menção ou ID)",
        nick="Nick/Nome do usuário",
        prazo="Prazo textual que vai no relatório (Ex: 30 dias, Permanente)",
        motivo="Motivo detalhado da blacklist",
        acao_discord="Ação a ser executada na conta",
        comprovacao_texto="Link da prova (Opcional se enviar arquivo)",
        comprovacao_arquivo="Anexo de Print/Vídeo (Opcional se enviar link)"
    )
    @app_commands.choices(acao_discord=[
        Choice(name="Banir (Ban)", value="ban"),
        Choice(name="Expulsar (Kick)", value="kick")
    ])
    async def blacklist(self, interaction: discord.Interaction, usuario: discord.User, nick: str, prazo: str, motivo: str, acao_discord: str, comprovacao_texto: str = None, comprovacao_arquivo: discord.Attachment = None):
        if not await self.verificar_diretoria(interaction): return
        
        if not comprovacao_texto and not comprovacao_arquivo:
            await interaction.response.send_message("Ação cancelada: É obrigatório fornecer ao menos uma prova (link ou anexo).", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        canal = interaction.guild.get_channel(config.CANAL_BLACKLIST)
        if not canal:
            await interaction.followup.send("Erro interno: Canal de Blacklist não definido.")
            return

        arquivos = []
        if comprovacao_arquivo:
            if comprovacao_arquivo.size > 8388608:
                await interaction.followup.send("Arquivo rejeitado: tamanho superior a 8MB. Utilize um link externo no campo de texto.")
                return
            arquivos.append(await comprovacao_arquivo.to_file())

        texto_prova = comprovacao_texto if comprovacao_texto else "Provas anexadas neste registro."
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        mensagem = (
            "╭・<:CYBER:1523690802021138563>  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
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
                await interaction.guild.ban(usuario, reason=f"Blacklist autorizada por {interaction.user.name} - Prazo: {prazo}")
                acao_texto = "banido"
            else:
                if membro_presente:
                    await interaction.guild.kick(usuario, reason=f"Blacklist autorizada por {interaction.user.name} - Prazo: {prazo}")
                    acao_texto = "expulso"
                else:
                    await interaction.followup.send(f"Registro processado. {usuario.mention} já não se encontra no servidor, remoção ignorada.")
                    return
                
            await interaction.followup.send(f"Operação concluída. {usuario.mention} sofreu blacklist e foi {acao_texto} do servidor.")
        except discord.Forbidden:
            await interaction.followup.send("O relatório foi registrado, mas o sistema bloqueou a ação no usuário por hierarquia de cargos. Remova-o manualmente.")
        except Exception as e:
            await interaction.followup.send(f"Relatório salvo. Ocorreu uma falha na API ao interagir com o usuário: {e}")


    # ---------------------------------------------------------
    # COMANDO: INFO EXÍLIO  
    # ---------------------------------------------------------
    @app_commands.command(name="infoexilio", description="Busca o histórico de exílio de um membro no sistema.")
    @app_commands.describe(usuario="Membro a ser consultado (Menção ou ID)")
    async def infoexilio(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        
        async for msg in canal.history(limit=None):
            if str(usuario.id) in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                
                anexos_urls = "\n".join([anexo.url for anexo in msg.attachments])
                if anexos_urls:
                    conteudo_limpo += f"\n\n**Anexos registrados:**\n{anexos_urls}"
                
                aviso_legado = ""
                if msg.author != self.bot.user:
                    aviso_legado = f"\n\n- Registro legado inserido manualmente por {msg.author.mention}."
                
                await interaction.followup.send(f"**Registro localizado:**\n\n{conteudo_limpo}{aviso_legado}")
                return
        
        await interaction.followup.send(f"Nenhum registro de exílio encontrado para {usuario.mention}.")


    # ---------------------------------------------------------
    # COMANDO: INFO BLACKLIST  
    # ---------------------------------------------------------
    @app_commands.command(name="infoblacklist", description="Busca o histórico de blacklist de um indivíduo no sistema.")
    @app_commands.describe(usuario="Indivíduo a ser consultado (Menção ou ID)")
    async def infoblacklist(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_BLACKLIST)
        
        async for msg in canal.history(limit=None):
            if str(usuario.id) in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                
                anexos_urls = "\n".join([anexo.url for anexo in msg.attachments])
                if anexos_urls:
                    conteudo_limpo += f"\n\n**Anexos registrados:**\n{anexos_urls}"
                
                aviso_legado = ""
                if msg.author != self.bot.user:
                    aviso_legado = f"\n\n- Registro legado inserido manualmente por {msg.author.mention}."
                
                await interaction.followup.send(f"**Registro localizado:**\n\n{conteudo_limpo}{aviso_legado}")
                return
        
        await interaction.followup.send(f"Nenhum registro de blacklist encontrado para {usuario.mention}.")

async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
