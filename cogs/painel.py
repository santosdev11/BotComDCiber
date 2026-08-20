import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, UserSelect, Button, Select, Modal, TextInput
import config
from datetime import datetime
import re

# div e prefixos
DIVISOES = [
    1521956217545560064, # Candidatos
    1521956187451429067, # Praças
    1521956151124824225, # Graduados
    1521956081650110675, # Oficiais
    1521950209800671423  # Alto Comando
]

MAP_CARGOS = {
    config.TRILHA_CARGOS[0]: (1521956217545560064, "{ 𝓐𝓟 }"),
    config.TRILHA_CARGOS[1]: (1521956187451429067, "{ 𝓣𝓜 }"),
    config.TRILHA_CARGOS[2]: (1521956151124824225, "{ 𝓞𝓡 }"),
    config.TRILHA_CARGOS[3]: (1521956081650110675, "{ 𝓔𝓒 }"),
    config.TRILHA_CARGOS[4]: (1521956081650110675, "{ 𝓐𝓔 }"),
    config.TRILHA_CARGOS[5]: (1521950209800671423, "{ 𝓒𝓘 }"),
    config.TRILHA_CARGOS[6]: (1521950209800671423, "{ 𝓒𝓞 }")
}

async def atualizar_dados_militar(guild: discord.Guild, membro: discord.Member, novo_cargo_id: int):
    if novo_cargo_id not in MAP_CARGOS:
        return False

    divisao_id, prefixo = MAP_CARGOS[novo_cargo_id]

    roles_to_add = []
    roles_to_remove = []

    # patente
    nova_patente = guild.get_role(novo_cargo_id)
    if nova_patente and nova_patente not in membro.roles:
        roles_to_add.append(nova_patente)

    for cargo_id in config.TRILHA_CARGOS:
        if cargo_id != novo_cargo_id:
            cargo_antigo = guild.get_role(cargo_id)
            if cargo_antigo and cargo_antigo in membro.roles:
                roles_to_remove.append(cargo_antigo)

    # div
    nova_divisao = guild.get_role(divisao_id)
    if nova_divisao and nova_divisao not in membro.roles:
        roles_to_add.append(nova_divisao)

    for d_id in DIVISOES:
        if d_id != divisao_id:
            antiga_divisao = guild.get_role(d_id)
            if antiga_divisao and antiga_divisao in membro.roles:
                roles_to_remove.append(antiga_divisao)

    # nickname
    nome_atual = membro.display_name
    nome_base = re.sub(r'^[\{\[\(].*?[\}\]\)]\s*', '', nome_atual).strip()
    if not nome_base: 
        nome_base = "Militar"

    novo_nick = f"{prefixo} {nome_base}"[:32]

    try:
        if roles_to_remove: await membro.remove_roles(*roles_to_remove)
        if roles_to_add: await membro.add_roles(*roles_to_add)
        if membro.display_name != novo_nick:
            await membro.edit(nick=novo_nick)
        return True
    except discord.Forbidden:
        return False


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
            try:
                await self.membro.add_roles(cargo)
            except discord.Forbidden:
                return await interaction.response.send_message("❌ O bot não tem permissão para dar cargos. Suba o cargo dele nas configurações do servidor.", ephemeral=True)
            
        canal_adv = interaction.guild.get_channel(config.CANAL_LOG_ADV)
        if canal_adv:
            msg = (
                "╭・<:CYBER:1523690802021138563> **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
                "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑨𝑫𝑽𝑬𝑹𝑻Ê𝑵𝑪𝑰𝑨*\n"
                "> \n"
                f"> **𝐌𝐈𝐋𝐈𝐓𝐀𝐑:** {self.membro.mention}\n"
                f"> **𝐍𝐈𝐂𝐊:** {self.membro.display_name}\n"
                "> \n"
                f"> **𝐂𝐀𝐑𝐆𝐎:** {self.membro.top_role.name}\n"
                "> \n"
                f"> **𝐂𝐋𝐀𝐒𝐒𝐈𝐅𝐈𝐂𝐀ÇÃ𝐎:** {self.nivel}ª Advertência\n"
                "> \n"
                f"> **𝐌𝐎𝐓𝐈𝐕𝐎:** — {self.motivo.value}\n"
                "> **𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n"
                f"> • {self.provas.value}\n"
                "> \n"
                f"> **𝐑𝐄𝐆𝐈𝐒𝐓𝐑𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
                f"> **𝐃𝐀𝐓𝐀:** {datetime.now().strftime('%d/%m/%Y')}\n\n"
                "`STATUS:` **ADVERTIDO**"
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
            "╭・<:CYBER:1523690802021138563> **𝐂𝐎𝐌𝐀𝐍𝐃𝐎 𝐃𝐄 𝐃𝐄𝐅𝐄𝐒𝐀 𝐂𝐈𝐁𝐄𝐑𝐍É𝐓𝐈𝐂𝐀**\n"
            "*𝑹𝑬𝑳𝑨𝑻Ó𝑹𝑰𝑶 𝑫𝑬 𝑬𝑿Í𝑳𝑰𝑶*\n"
            "> \n"
            f"> **𝐌𝐈𝐋𝐈𝐓𝐀𝐑:** {self.membro.mention}\n"
            f"> **𝐍𝐈𝐂𝐊:** {self.membro.display_name}\n"
            "> \n"
            f"> **𝐂𝐀𝐑𝐆𝐎:** {self.membro.top_role.name}\n"
            "> \n"
            f"> **𝐏𝐑𝐀𝐙𝐎:** {self.prazo.value}\n"
            "> \n"
            f"> **𝐌𝐎𝐓𝐈𝐕𝐎:** — {self.motivo.value}\n"
            "> **𝐂𝐎𝐌𝐏𝐑𝐎𝐕𝐀ÇÕ𝐄𝐒:**\n"
            f"> • {self.provas.value}\n"
            "> \n"
            f"> **𝐀𝐔𝐓𝐎𝐑𝐈𝐙𝐀𝐃𝐎 𝐏𝐎𝐑:** {interaction.user.mention}\n"
            f"> **𝐃𝐀𝐓𝐀:** {datetime.now().strftime('%d/%m/%Y')}\n\n"
            "`STATUS:` **EXILADO**\n"
            f"-# UserID:{self.membro.id}"
        )
        await canal.send(msg)
        
        try:
            await interaction.guild.kick(self.membro, reason=f"Exilado por {interaction.user.name}")
            await interaction.response.send_message("Operação concluída. O militar foi exilado e expulso do servidor.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Relatório salvo, mas houve falha ao expulsar. O bot tem permissão?: {e}", ephemeral=True)


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
        for i in range(len(config.TRILHA_CARGOS) - 1, -1, -1):
            role_id = config.TRILHA_CARGOS[i]
            if discord.utils.get(self.membro.roles, id=role_id):
                return i, role_id
        return -1, None

    async def promover(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        idx, current_role = self.get_track_index()
        
        if idx == -1:
            if not self.is_criador: 
                return await interaction.followup.send("Usuário fora da hierarquia linear (AP-CO). Ação bloqueada.")
            novo_id = config.TRILHA_CARGOS[0]
        elif idx < len(config.TRILHA_CARGOS) - 1:
            novo_id = config.TRILHA_CARGOS[idx+1]
        else:
            if not self.is_criador: 
                return await interaction.followup.send("Limite hierárquico alcançado. Operação bloqueada.")
            return await interaction.followup.send("Membro já é CO. Uso manual obrigatório para patentes superiores.")
            
        sucesso = await atualizar_dados_militar(interaction.guild, self.membro, novo_id)
        if not sucesso:
            return await interaction.followup.send("❌ Erro de Hierarquia: O bot não tem permissão para alterar cargos deste membro.")
            
        await interaction.followup.send(f"✅ Promoção executada na conta de {self.membro.mention}. Ficha limpa e sincronizada.")

    async def rebaixar(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        idx, current_role = self.get_track_index()
        
        if idx <= 0:
            return await interaction.followup.send("Rebaixamento bloqueado. O usuário já é um Aprendiz ou não está na trilha AP-CO.")
        
        novo_id = config.TRILHA_CARGOS[idx-1]
        
        sucesso = await atualizar_dados_militar(interaction.guild, self.membro, novo_id)
        if not sucesso:
            return await interaction.followup.send("❌ Erro de Hierarquia: O bot não tem permissão para alterar cargos deste membro.")
            
        await interaction.followup.send(f"✅ Rebaixamento executado na conta de {self.membro.mention}. Ficha limpa e sincronizada.")

    async def advertir(self, interaction: discord.Interaction):
        await interaction.response.send_message("Selecione a classificação:", view=AdvView(self.membro), ephemeral=True)

    async def exilar(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ExilioModal(self.membro))


class MainPainelSelect(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Selecione um militar para abrir a ficha...", max_values=1, custom_id="main_painel_select")

    async def callback(self, interaction: discord.Interaction):
        user_roles = [r.id for r in interaction.user.roles]
        
        # apenas STA podem acessar
        if not any(r in config.CARGOS_STA for r in user_roles):
            return await interaction.response.send_message("❌ Acesso negado. Apenas membros designados da STA podem operar este terminal.", ephemeral=True)

        is_criador = config.STA_CRIADOR in user_roles
        can_exile = any(r in config.STA_EXILIO for r in user_roles)
        
        membro = self.values[0]
        if not isinstance(membro, discord.Member):
            return await interaction.response.send_message("Erro: O alvo precisa estar no servidor.", ephemeral=True)

        roles_limpos = []
        for r in reversed(membro.roles):
            if r.name == "@everyone": continue
            if "---" in r.name or r.name.startswith(('<', '>', '│', '┃', '┌', '└')): continue
            roles_limpos.append(r.mention)

        cargos_texto = "\n".join(f"• {r}" for r in roles_limpos) if roles_limpos else "Nenhuma patente registrada."

        embed = discord.Embed(
            title=f"Terminal Operacional: {membro.display_name}",
            description="Selecione uma ação abaixo para este militar. Ações punitivas requerem logs formais.",
            color=discord.Color.dark_theme()
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="Patentes Atuais", value=cargos_texto, inline=False)

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
        user_roles = [r.id for r in interaction.user.roles]
        
        # apenas STA pode dar /painel
        if not any(r in config.CARGOS_STA for r in user_roles):
            return await interaction.response.send_message("❌ Acesso negado. Apenas membros da STA podem instalar o painel.", ephemeral=True)
            
        embed = discord.Embed(
            title="<:CYBER:1523690802021138563> Sistema de Gerenciamento - STA",
            description="Utilize o menu abaixo para localizar um militar e gerenciar sua ficha criminal e hierárquica.",
            color=discord.Color.dark_theme()
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1526286439967621203/1540052218869317692/8ae3ccc5-07a7-4c8a-82e6-3edefda96f79.png?ex=6a888ce5&is=6a873b65&hm=3d4ccf09bafcbb03754b4d0ab22afdaf865b51434a4b2ede459f38aadb54bbee&")
        embed.set_footer(text="Ações realizadas neste terminal são monitoradas.")
        
        await interaction.channel.send(embed=embed, view=MainPainelView())
        await interaction.response.send_message("Painel instalado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PainelCog(bot))
