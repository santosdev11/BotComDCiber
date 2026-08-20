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
        self.ready_run = False
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        self.add_view(BaseAvaliacaoView(config.CARGO_CHEFIA_OP, "PATRULHA"))
        self.add_view(BaseAvaliacaoView(config.CARGO_PERM_AVAL, "AVAL"))
        self.add_view(BaseAvaliacaoView(config.CARGO_PERM_METAS, "META"))
        
        self.tree.on_error = self.on_app_command_error
        
        await self.tree.sync()
        print("[ INIT ] Módulos e comandos sincronizados.")

    async def on_ready(self):
        if self.ready_run: 
            return
        self.ready_run = True
        
        print(f"[ INIT ] Sistema operando via {self.user}.")

        for guild in self.guilds:
            print(f"[ INFO ] Verificando IDs no servidor: {guild.name}")
            
            canais = [config.CANAL_PATRULHA, config.CANAL_LOG_PATRULHA, config.CANAL_AVAL, 
                      config.CANAL_LOG_AVAL, config.CANAL_AVAL_LIBERADO, config.CANAL_METAS, config.CANAL_LOG_METAS]
            for canal_id in canais:
                if not guild.get_channel(canal_id):
                    print(f"[ ERRO ] Canal ID {canal_id} ausente.")
            
            cargos = [config.CARGO_ACESSO_BASICO, config.CARGO_CHEFIA_OP, config.CARGO_PERM_AVAL, 
                      config.CARGO_AVAL_CONCEDIDO, config.CARGO_PERM_METAS]
            for cargo_id in cargos:
                if not guild.get_role(cargo_id):
                    print(f"[ ERRO ] Cargo ID {cargo_id} ausente.")
            
            print("[ INFO ] Verificação de IDs concluída.")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingRole) or isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Acesso negado. Patente insuficiente.", ephemeral=True)
        else:
            await interaction.response.send_message("Falha na execução. Equipe de engenharia acionada.", ephemeral=True)
            print(f"[ FATAL ] {error}")

bot = ComDCiberBot()

if __name__ == '__main__':
    if TOKEN is None:
        print("[ FATAL ] Token ausente.")
    else:
        bot.run(TOKEN)
