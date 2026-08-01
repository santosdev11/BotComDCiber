import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from datetime import datetime
import config
from components import BaseAvaliacaoView

class AvalModal(Modal, title='Solicitacao de Aval'):
    motivo = TextInput(label='Motivo do Aval', required=True)
    inicio_fim = TextInput(label='Inicio e Fim (Ex: 17/07 a 24/07)', required=True)
    observacoes = TextInput(label='Observacoes', style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        canal = interaction.guild.get_channel(config.CANAL_AVAL)
        msg = (
            f"📋 | **SOLICITAÇÃO DE AVAL**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 | **Responsável:** {interaction.user.mention}\n\n"
            f"📌 | **Motivo:** {self.motivo.value}\n\n"
            f"📝 | **Observações/Período:** {self.inicio_fim.value} | {self.observacoes.value}\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ | **Data:** {discord.utils.format_dt(datetime.now(), 'f')}\n\n"
            f"-# made by santosdev11"
        )
        await canal.send(msg, view=BaseAvaliacaoView(config.CARGO_PERM_AVAL, config.CANAL_LOG_AVAL, "AVAL"))
        await interaction.response.send_message("Solicitacao de aval enviada!", ephemeral=True)

class AvalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aval", description="Solicitar um aval")
    @app_commands.checks.has_role(config.CARGO_ACESSO_BASICO) 
    async def aval(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AvalModal())

async def setup(bot):
    await bot.add_cog(AvalCog(bot))