import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
from datetime import datetime
import config
from components import BaseAvaliacaoView

class PatrulhaModal(Modal, title='Relatorio de Patrulhamento'):
    auxiliares = TextInput(label='Auxiliares (Deixe vazio se não houver)', required=False)
    local = TextInput(label='Local da Patrulha', required=True)
    observacao = TextInput(label='Observacao', style=discord.TextStyle.paragraph, required=True)
    tempo = TextInput(label='Tempo de Patrulhamento (Ex: 1 hora)', required=True)
    comprovacoes = TextInput(label='Links das Comprovacoes (Prints)', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        canal = interaction.guild.get_channel(config.CANAL_PATRULHA)
        msg = (
            f"🚔 | **RELATÓRIO DE PATRULHAMENTO**\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 | **Responsável:** {interaction.user.mention}\n"
            f"🧑‍💼 | **Auxiliares:** {self.auxiliares.value or 'Nenhum'}\n"
            f"📍 | **Local:** {self.local.value}\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 | **Observação:** {self.observacao.value}\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏰ | **Tempo:** {self.tempo.value}\n"
            f"⏰ | **Data:** {discord.utils.format_dt(datetime.now(), 'f')}\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📸 | **Comprovações:** {self.comprovacoes.value}\n\n"
            f"-# made by santosdev11"
        )
        await canal.send(msg, view=BaseAvaliacaoView(config.CARGO_CHEFIA_OP, config.CANAL_LOG_PATRULHA, "PATRULHA"))
        await interaction.response.send_message("Relatorio enviado com sucesso!", ephemeral=True)

class PatrulhaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="patrulha", description="Enviar um relatorio de patrulhamento")
    @app_commands.checks.has_role(config.CARGO_ACESSO_BASICO) 
    async def patrulha(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PatrulhaModal())

async def setup(bot):
    await bot.add_cog(PatrulhaCog(bot))