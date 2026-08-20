import discord
from discord.ext import commands
from discord import app_commands
import config
import re

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Lista os comandos disponíveis no sistema.")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="<:CYBER:1523690802021138563> Painel de Comandos - Defesa Cibernética",
            description="Comandos operacionais disponíveis no sistema:",
            color=discord.Color.dark_theme()
        )
        embed.add_field(name="`/painel`", value="Instala o painel interativo da STA no chat atual.\nAcesso: STA", inline=False)
        embed.add_field(name="`/patrulhamentos`", value="Consulta a quantidade e horas de patrulhas de um militar.\nAcesso: Livre", inline=False)
        embed.add_field(name="`/infoexilio`", value="Puxa o histórico de exílio de um membro.\nAcesso: Livre", inline=False)
        embed.add_field(name="`/infoblacklist`", value="Puxa o histórico de blacklist de um indivíduo.\nAcesso: Livre", inline=False)
        
        embed.set_footer(text=f"Solicitado por {interaction.user.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="patrulhamentos", description="Consulta patrulhamentos aprovados e soma horas de serviço.")
    @app_commands.describe(militar="Militar a ser consultado (Ex: @Meliante)")
    async def patrulhamentos(self, interaction: discord.Interaction, militar: discord.Member):
        await interaction.response.defer(ephemeral=False)
        
        canal_log = interaction.guild.get_channel(config.CANAL_LOG_PATRULHA)
        if not canal_log:
            await interaction.followup.send("Erro de configuração: canal de logs não localizado.")
            return
        
        contagem = 0
        total_segundos = 0
        
        async for msg in canal_log.history(limit=10000):
            if msg.author == self.bot.user and f"ID: {militar.id}" in msg.content and "✅ APROVADO" in msg.content:
                contagem += 1
                
                h_match = re.search(r'(?i)(\d+)\s*hora', msg.content)
                m_match = re.search(r'(?i)(\d+)\s*minuto', msg.content)
                s_match = re.search(r'(?i)(\d+)\s*segundo', msg.content)
                
                if h_match: total_segundos += int(h_match.group(1)) * 3600
                if m_match: total_segundos += int(m_match.group(1)) * 60
                if s_match: total_segundos += int(s_match.group(1))
                    
        h_totais = total_segundos // 3600
        m_totais = (total_segundos % 3600) // 60
        s_totais = total_segundos % 60
        
        texto_tempo = f"{h_totais} horas, {m_totais} minutos e {s_totais} segundos."
        if h_totais == 0:
            texto_tempo = f"{m_totais} minutos e {s_totais} segundos."
                    
        embed = discord.Embed(
            title="Relatório de Serviço",
            description=f"Constam **{contagem}** patrulhamentos aprovados no registro de {militar.mention}.\n\n**Tempo total de serviço:** {texto_tempo}",
            color=discord.Color.dark_theme()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="infoexilio", description="Busca o histórico de exílio de um membro no sistema.")
    async def infoexilio(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        if not canal:
            return await interaction.followup.send("Erro de configuração: canal de exílio não localizado.")

        async for msg in canal.history(limit=None):
            if str(usuario.id) in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                anexos = "\n".join([a.url for a in msg.attachments])
                if anexos: conteudo_limpo += f"\n\n**Anexos registrados:**\n{anexos}"
                await interaction.followup.send(f"**Registro localizado (Mais Recente):**\n\n{conteudo_limpo}")
                return
        await interaction.followup.send(f"Nenhum registro de exílio encontrado para {usuario.mention}.")

    @app_commands.command(name="infoblacklist", description="Busca o histórico de blacklist de um indivíduo no sistema.")
    async def infoblacklist(self, interaction: discord.Interaction, usuario: discord.User):
        await interaction.response.defer(ephemeral=False)
        canal = interaction.guild.get_channel(config.CANAL_BLACKLIST)
        if not canal:
            return await interaction.followup.send("Erro de configuração: canal de blacklist não localizado.")

        async for msg in canal.history(limit=None):
            if str(usuario.id) in msg.content:
                conteudo_limpo = msg.content.replace(f"-# UserID:{usuario.id}", "")
                anexos = "\n".join([a.url for a in msg.attachments])
                if anexos: conteudo_limpo += f"\n\n**Anexos registrados:**\n{anexos}"
                await interaction.followup.send(f"**Registro localizado (Mais Recente):**\n\n{conteudo_limpo}")
                return
        await interaction.followup.send(f"Nenhum registro de blacklist encontrado para {usuario.mention}.")

async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
