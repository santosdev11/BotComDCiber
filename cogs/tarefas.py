import discord
from discord.ext import commands, tasks
import config
import re
from datetime import datetime

class TarefasCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verificar_avals.start()

    def cog_unload(self):
        self.verificar_avals.cancel()

    # a cada 6 horas
    @tasks.loop(hours=6)
    async def verificar_avals(self):
        await self.bot.wait_until_ready()
        
        for guild in self.bot.guilds:
            cargo_afastado = guild.get_role(config.CARGO_AVAL_CONCEDIDO)
            canal_log_aval = guild.get_channel(config.CANAL_LOG_AVAL)
            
            if not cargo_afastado or not canal_log_aval:
                continue

            agora = datetime.now()
            ano_atual = agora.year
            
            for membro in cargo_afastado.members:
                
                async for msg in canal_log_aval.history(limit=2000):
                    if msg.author == self.bot.user and f"ID: {membro.id}" in msg.content and "APROVADO" in msg.content:
                        
                        # fim: DD/MM
                        match = re.search(r'Fim:\s*(\d{1,2})[/-](\d{1,2})', msg.content, re.IGNORECASE)
                        
                        if match:
                            dia = int(match.group(1))
                            mes = int(match.group(2))
                            
                            try:
                                data_fim = datetime(ano_atual, mes, dia, 23, 59, 59)
                                
                                if agora > data_fim:
                                    await membro.remove_roles(cargo_afastado, reason="Rotina automática: Aval expirado.")
                                    print(f"[ SISTEMA ] Aval de {membro.name} expirado. Cargo removido.")
                            except ValueError:
                                pass 
                        
                        break 

async def setup(bot):
    await bot.add_cog(TarefasCog(bot))
