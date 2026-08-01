import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import config
from components import BaseAvaliacaoView

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ComDCiberBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        self.add_view(BaseAvaliacaoView(config.CARGO_CHEFIA_OP, config.CANAL_LOG_PATRULHA, "PATRULHA"))
        self.add_view(BaseAvaliacaoView(config.CARGO_PERM_AVAL, config.CANAL_LOG_AVAL, "AVAL"))
        self.add_view(BaseAvaliacaoView(config.CARGO_PERM_METAS, config.CANAL_LOG_METAS, "META"))
        
        self.tree.on_error = self.on_app_command_error
        
        await self.tree.sync()
        print("Modulos e Slash Commands sincronizados.")

    async def on_ready(self):
        print(f"Sistema Operacional: {self.user} online.")

        #### ------------
        for guild in self.guilds:
            print(f"--- Escaneando IDs no servidor: {guild.name} ---")
            
            canais = [config.CANAL_PATRULHA, config.CANAL_LOG_PATRULHA, config.CANAL_AVAL, 
                      config.CANAL_LOG_AVAL, config.CANAL_AVAL_LIBERADO, config.CANAL_METAS, config.CANAL_LOG_METAS]
            for canal_id in canais:
                if not guild.get_channel(canal_id):
                    print(f"[ERRO] Canal ID {canal_id} nao foi encontrado. Verifique o config.py.")
            
            cargos = [config.CARGO_ACESSO_BASICO, config.CARGO_CHEFIA_OP, config.CARGO_PERM_AVAL, 
                      config.CARGO_AVAL_CONCEDIDO, config.CARGO_PERM_METAS]
            for cargo_id in cargos:
                if not guild.get_role(cargo_id):
                    print(f"[ERRO] Cargo ID {cargo_id} nao foi encontrado. Verifique o config.py.")
            
            print("--- Escaneamento finalizado ---")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("[ NEGADO ] Voce nao possui hierarquia para usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"[ ERRO DO SISTEMA ] Informe o desenvolvedor: {error}", ephemeral=True)
            print(f"Erro critico: {error}")

bot = ComDCiberBot()

if __name__ == '__main__':
    if TOKEN is None:
        print("Erro: Token nao encontrado no .env")
    else:
        bot.run(TOKEN)