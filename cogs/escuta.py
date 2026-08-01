import discord
from discord.ext import commands
import config
from components import BaseAvaliacaoView

class EscutaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def processar_mensagem(self, message: discord.Message, tipo, canal_log_id, cargo_id):
        canal_log = self.bot.get_channel(canal_log_id)
        if canal_log:
            texto_seguro = message.content[:1700] + "\n...[TEXTO CORTADO POR LIMITE DE CARACTERES]" if len(message.content) > 1700 else message.content

            texto_log = (
                f"**Nova Solicitação de {tipo}**\n"
                f"**Autor:** {message.author.mention} | ID: {message.author.id}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{texto_seguro}\n"
                f"-# CanalID:{message.channel.id} MsgID:{message.id}"
            )
            
            arquivos = []
            if message.attachments:
                for anexo in message.attachments:
                    if len(arquivos) < 10:
                        arquivos.append(await anexo.to_file())
            
            await canal_log.send(content=texto_log, files=arquivos, view=BaseAvaliacaoView(cargo_id, tipo))
            await message.add_reaction("⏳")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[ SISTEMA ] Iniciando varredura de mensagens perdidas...")
        
        configuracoes = [
            (config.CANAL_PATRULHA, "PATRULHA", config.CANAL_LOG_PATRULHA, config.CARGO_CHEFIA_OP, ["RELATÓRIO DE PATRULHAMENTO", "RELATORIO DE PATRULHAMENTO"]),
            (config.CANAL_AVAL, "AVAL", config.CANAL_LOG_AVAL, config.CARGO_PERM_AVAL, ["SOLICITAÇÃO DE AVAL", "SOLICITACAO DE AVAL"]),
            (config.CANAL_METAS, "META", config.CANAL_LOG_METAS, config.CARGO_PERM_METAS, ["META SEMANAL CONCLUÍDA", "META SEMANAL CONCLUIDA"])
        ]

        for canal_id, tipo, log_id, cargo_id, palavras_chave in configuracoes:
            canal = self.bot.get_channel(canal_id)
            if canal:
                async for msg in canal.history(limit=10):
                    if msg.author.bot:
                        continue
                    
                    ja_processada = False
                    for reaction in msg.reactions:
                        if str(reaction.emoji) in ["⏳", "✅", "❌","➖"]:
                            ja_processada = True
                            break
                    
                    if not ja_processada:
                        conteudo_upper = msg.content.upper()
                        if any(palavra in conteudo_upper for palavra in palavras_chave):
                            print(f"[ RECUPERACAO ] Mensagem de {msg.author.name} recuperada em {tipo}.")
                            await self.processar_mensagem(msg, tipo, log_id, cargo_id)

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
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão.", delete_after=10)
                return 
            tipo = "PATRULHA"
            canal_log_id = config.CANAL_LOG_PATRULHA
            cargo_id = config.CARGO_CHEFIA_OP
            
        elif message.channel.id == config.CANAL_AVAL:
            if "SOLICITAÇÃO DE AVAL" not in conteudo_upper and "SOLICITACAO DE AVAL" not in conteudo_upper:
                if not is_mod:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão.", delete_after=10)
                return
            tipo = "AVAL"
            canal_log_id = config.CANAL_LOG_AVAL
            cargo_id = config.CARGO_PERM_AVAL
            
        elif message.channel.id == config.CANAL_METAS:
            if "META SEMANAL CONCLUÍDA" not in conteudo_upper and "META SEMANAL CONCLUIDA" not in conteudo_upper:
                if not is_mod:
                    await message.delete()
                    await message.channel.send(f"⚠️ {message.author.mention}, sua mensagem foi apagada pois não segue o formato padrão.", delete_after=10)
                return
            tipo = "META"
            canal_log_id = config.CANAL_LOG_METAS
            cargo_id = config.CARGO_PERM_METAS

        if tipo:
            await self.processar_mensagem(message, tipo, canal_log_id, cargo_id)

async def setup(bot):
    await bot.add_cog(EscutaCog(bot))
