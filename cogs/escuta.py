import discord
from discord.ext import commands
import config
from components import BaseAvaliacaoView

class EscutaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        is_mod = message.author.guild_permissions.manage_messages or message.author.guild_permissions.administrator

        tipo = None
        canal_log_id = None
        cargo_id = None
        
        conteudo_upper = message.content.upper()

        if message.channel.id == config.CANAL_PATRULHA:
            if "RELATÓRIO DE PATRULHAMENTO" not in conteudo_upper and "RELATORIO DE PATRULHAMENTO" not in conteudo_upper:
                if not is_mod:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão de **Relatório de Patrulhamento**.", delete_after=10)
                return 
                
            tipo = "PATRULHA"
            canal_log_id = config.CANAL_LOG_PATRULHA
            cargo_id = config.CARGO_CHEFIA_OP
            
        elif message.channel.id == config.CANAL_AVAL:
            if "SOLICITAÇÃO DE AVAL" not in conteudo_upper and "SOLICITACAO DE AVAL" not in conteudo_upper:
                if not is_mod:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão de **Solicitação de Aval**.", delete_after=10)
                return
                
            tipo = "AVAL"
            canal_log_id = config.CANAL_LOG_AVAL
            cargo_id = config.CARGO_PERM_AVAL
            
        elif message.channel.id == config.CANAL_METAS:
            if "META SEMANAL CONCLUÍDA" not in conteudo_upper and "META SEMANAL CONCLUIDA" not in conteudo_upper:
                if not is_mod:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão de **Meta Semanal**.", delete_after=10)
                return
                
            tipo = "META"
            canal_log_id = config.CANAL_LOG_METAS
            cargo_id = config.CARGO_PERM_METAS

        if tipo:
            canal_log = self.bot.get_channel(canal_log_id)
            if canal_log:
                texto_log = (
                    f"**Nova Solicitação de {tipo}**\n"
                    f"**Autor:** {message.author.mention} | ID: {message.author.id}\n"
                    f"**Canal Original:** <#{message.channel.id}> | ID: {message.channel.id}\n"
                    f"**Mensagem Original:** {message.id}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{message.content}"
                )
                
                await canal_log.send(texto_log, view=BaseAvaliacaoView(cargo_id, tipo))
                await message.add_reaction("⏳")

async def setup(bot):
    await bot.add_cog(EscutaCog(bot))
