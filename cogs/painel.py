import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, UserSelect, Button, Select, Modal, TextInput
import config
from datetime import datetime

class AdvModal(Modal, title="Aplicar Advertência"):
    motivo = TextInput(label="Motivo", style=discord.TextStyle.long, required=True)
    provas = TextInput(label="Comprovações (Links)", style=discord.TextStyle.short, required=True)

    def __init__(self, membro: discord.Member, nivel: str):
        super().__init__()
        self.membro = membro
        self.nivel = nivel

    async def on_submit(self, interaction: discord.Interaction):
        cargo = interaction.guild.get_role(config.CARGOS_ADV[self.nivel])
        if cargo:
            await self.membro.add_roles(cargo)
            
        canal_adv = interaction.guild.get_channel(config.CANAL_LOG_ADV)
        if canal_adv:
            msg = (
                "╭・<:CYBER:1523690802021138563>  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
                "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑨𝑫𝑽𝑬𝑹𝑻Ê𝑵𝑪𝑰𝑨*\n\n"
                f"**𝐌𝐈𝐋𝐈𝐓𝐀𝐑:** {self.membro.mention}\n"
                f"**𝐍𝐈𝐂𝐊:** {self.membro.display_name}\n\n"
                f"**𝐂𝐀𝐑𝐆𝐎:** {self.membro.top_role.name}\n\n"
                f"**𝐂𝐋𝐀𝐒𝐒𝐈𝐅𝐈𝐂𝐀ÇÃ𝐎:** {self.nivel}ª Advertência\n\n"
                f"**𝐌𝐎𝐓𝐈𝐕𝐎:** — {self.motivo.value}\n"
                f"**𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n• {self.provas.value}\n\n"
                f"**𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
                f"**𝐃𝐀𝐓𝐀:** {datetime.now().strftime('%d/%m/%Y')}\n\n"
                "**STATUS: ADVERTIDO**"
            )
            await canal_adv.send(msg)
        await interaction.response.send_message(f"Operação concluída. {self.nivel}ª Advertência aplicada em {self.membro.mention}.", ephemeral=True)

class ExilioModal(Modal, title="Aplicar Exílio (Ação Direta)"):
    motivo = TextInput(label="Motivo", style=discord.TextStyle.long, required=True)
    prazo = TextInput(label="Prazo", style=discord.TextStyle.short, required=True)
    provas = TextInput(label="Comprovações (Links)", style=discord.TextStyle.short, required=True)

    def __init__(self, membro: discord.Member):
        super().__init__()
        self.membro = membro

    async def on_submit(self, interaction: discord.Interaction):
        canal = interaction.guild.get_channel(config.CANAL_EXILIO)
        if not canal:
            return await interaction.response.send_message("Erro: Canal de exílio não configurado.", ephemeral=True)

        msg = (
            "╭・<:CYBER:1523690802021138563>  **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
            "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑬𝑿Í𝑳𝑰𝑶*\n\n"
            f"**𝐌𝐈𝐋𝐈𝐓𝐀𝐑:** {self.membro.mention}\n"
            f"**𝐍𝐈𝐂𝐊:** {self.membro.display_name}\n\n"
            f"**𝐂𝐀𝐑𝐆𝐎:** {self.membro.top_role.name}\n\n"
            f"**𝐏𝐑𝐀𝐙𝐎:** {self.prazo.value}\n\n"
            f"**𝐌𝐎𝐓𝐈𝐕𝐎:** — {self.motivo.value}\n"
            f"**𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n• {self.provas.value}\n\n"
            f"**𝐀𝐔𝐓𝐎𝐑𝐈𝐙𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
            f"**𝐃𝐀𝐓𝐀:** {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "**STATUS: EXILADO**\n"
            f"-# UserID:{self.membro.id}"
        )
        await canal.send(msg)
        
        try:
            await interaction.guild.kick(self.membro, reason=f"Exilado por {interaction.user.name}")
            await interaction.response.send_message("Operação concluída. O militar foi exilado e expulso do servidor.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Relatório salvo, mas houve falha ao expulsar: {e}", ephemeral=True)


class AdvSelect(Select):
    def __init__(self, membro: discord.Member):
        self.membro = membro
        options = [
            discord.SelectOption(label="1ª Advertência", value="1"),
            discord.SelectOption(label="2ª Advertência", value="2"),
            discord.SelectOption(label="3ª Advertência", value="3")
        ]
        super().__init__(placeholder="Selecione o nível da advertência...", options=options, custom_id="adv_select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(AdvModal(self.membro, self.values[0]))

class AdvView(View):
    def __init__(self, membro: discord.Member):
        super().__init__(timeout=60)
        self.add_item(AdvSelect(membro))

class PainelOperacionalView(View):
    def __init__(self, membro: discord.Member, is_criador: bool, can_exile: bool):
        super().__init__(timeout=180)
        self.membro = membro
        self.is_criador = is_criador
        
        btn_promover = Button(label="Promover", style=discord.ButtonStyle.success)
        btn_promover.callback = self.promover
        self.add_item(btn_promover)
        
        btn_rebaixar = Button(label="Rebaixar", style=discord.ButtonStyle.danger)
        btn_rebaixar.callback = self.rebaixar
        self.add_item(btn_rebaixar)
        
        btn_adv = Button(label="Advertir", style=discord.ButtonStyle.primary)
        btn_adv.callback = self.advertir
        self.add_item(btn_adv)
        
        if can_exile:
            btn_exilar = Button(label="Exilar", style=discord.ButtonStyle.secondary)
            btn_exilar.callback = self.exilar
            self.add_item(btn_exilar)

    def get_track_index(self):
        for i, role_id in enumerate(config.TRILHA_CARGOS):
            if discord.utils.get(self.membro.roles, id=role_id):
                return i, role_id
        return -1, None

    async def promover(self, interaction: discord.Interaction):
        idx, current_role = self.get_track_index()
        if idx == -1:
            if not self.is_criador: return await interaction.response.send_message("Usuário fora da hierarquia linear (AP-CO). Ação bloqueada.", ephemeral=True)
            novo = interaction.guild.get_role(config.TRILHA_CARGOS[0])
            await self.membro.add_roles(novo)
        elif idx < len(config.TRILHA_CARGOS) - 1:
            antigo = interaction.guild.get_role(current_role)
            novo = interaction.guild.get_role(config.TRILHA_CARGOS[idx+1])
            await self.membro.remove_roles(antigo)
            await self.membro.add_roles(novo)
        else:
            if not self.is_criador: return await interaction.response.send_message("Limite hierárquico alcançado. Operação bloqueada.", ephemeral=True)
            return await interaction.response.send_message("Membro já é CO. Uso manual obrigatório para patentes superiores.", ephemeral=True)
            
        await interaction.response.send_message(f"Promoção executada com sucesso na conta de {self.membro.mention}.", ephemeral=True)

    async def rebaixar(self, interaction: discord.Interaction):
        idx, current_role = self.get_track_index()
        if idx <= 0:
            return await interaction.response.send_message("Rebaixamento bloqueado. O usuário já é um Aprendiz ou não está na trilha AP-CO.", ephemeral=True)
        
        antigo = interaction.guild.get_role(current_role)
        novo = interaction.guild.get_role(config.TRILHA_CARGOS[idx-1])
        await self.membro.remove_roles(antigo)
        await self.membro.add_roles(novo)
        await interaction.response.send_message(f"Rebaixamento executado com sucesso na conta de {self.membro.mention}.", ephemeral=True)

    async def advertir(self, interaction: discord.Interaction):
        await interaction.response.send_message("Selecione a classificação:", view=AdvView(self.membro), ephemeral=True)

    async def exilar(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ExilioModal(self.membro))


class MainPainelSelect(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Selecione um militar para abrir a ficha...", max_values=1, custom_id="main_painel_select")

    async def callback(self, interaction: discord.Interaction):
        user_roles = [r.id for r in interaction.user.roles]
        
        if not any(r in config.CARGOS_STA for r in user_roles) and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Acesso negado. Você não tem o cargo necessário.", ephemeral=True)

        is_criador = config.STA_CRIADOR in user_roles or interaction.user.guild_permissions.administrator
        can_exile = any(r in config.STA_EXILIO for r in user_roles) or interaction.user.guild_permissions.administrator
        
        membro = self.values[0]
        if not isinstance(membro, discord.Member):
            return await interaction.response.send_message("Erro: O alvo precisa estar no servidor.", ephemeral=True)

        embed = discord.Embed(
            title=f"Terminal Operacional: {membro.display_name}",
            description="Selecione uma ação abaixo para este militar. Ações punitivas requerem logs formais.",
            color=discord.Color.dark_theme()
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        cargos = ", ".join([r.mention for r in membro.roles if r.name != "@everyone"])
        embed.add_field(name="Patentes Atuais", value=cargos if cargos else "Nenhuma")

        await interaction.response.send_message(embed=embed, view=PainelOperacionalView(membro, is_criador, can_exile), ephemeral=True)

class MainPainelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MainPainelSelect())

class PainelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="painel", description="Instala o painel persistente da STA no canal.")
    async def painel(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("Apenas administradores podem instalar o painel.", ephemeral=True)
            
        embed = discord.Embed(
            title="<:CYBER:1523690802021138563> Sistema de Gerenciamento - STA",
            description="Utilize o menu abaixo para localizar um militar e gerenciar sua ficha criminal e hierárquica.",
            color=discord.Color.dark_theme()
        )
        embed.set_footer(text="Ações realizadas neste terminal são monitoradas.")
        await interaction.channel.send(embed=embed, view=MainPainelView())
        await interaction.response.send_message("Painel instalado com sucesso.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PainelCog(bot))
