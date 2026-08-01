import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Modal, TextInput
import config
from components import BaseAvaliacaoView

class MetaModal(Modal, title='Meta Semanal Concluida'):
    avaliado = TextInput(label='ID ou Nome do Membro Avaliado', required=True)
    patente = TextInput(label='Patente', required=True)
    observacoes = TextInput(label='Observacoes', style=discord.TextStyle.paragraph, required=True)
    fiscalizacao = TextInput(label='Fiscalizacao (Ex: Supervisao-Geral)', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        canal = interaction.guild.get_channel(config.CANAL_METAS)
        msg = (
            f"✅ | **META SEMANAL CONCLUÍDA**\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Relatório destinado ao registro de conclusão das metas.\n━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 | **Responsável pela Avaliação:** {interaction.user.mention}\n\n"
            f"👥 | **Membro Avaliado:** {self.avaliado.value}\n\n"
            f"🎖️ | **Patente:** {self.patente.value}\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 | **Observações:** {self.observacoes.value}\n━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ | **Fiscalização:** {self.fiscalizacao.value}\n\n"
            f"-# made by santosdev11"
        )
        await canal.send(msg, view=BaseAvaliacaoView(config.CARGO_PERM_METAS, config.CANAL_LOG_METAS, "META"))
        await interaction.response.send_message("Relatorio de meta enviado!", ephemeral=True)

class MetaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="meta", description="Registrar meta semanal concluida")
    @app_commands.checks.has_role(config.CARGO_ACESSO_BASICO) 
    async def meta(self, interaction: discord.Interaction):
        await interaction.response.send_modal(MetaModal())

async def setup(bot):
    await bot.add_cog(MetaCog(bot))