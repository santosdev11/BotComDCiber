import discord
from discord.ext import commands
from discord import app_commands
import config

class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
