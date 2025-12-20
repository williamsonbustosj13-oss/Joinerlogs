import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import os
import traceback

# =======================
# CONFIG
# =======================
OWNER_ID = 1373716141297504428

FOOTER_ICON = "https://cdn.discordapp.com/avatars/1373716141297504428/e682f46e142edbc99ff265eca11df3ed.webp?size=4096"
COLOR_PRINCIPAL = 0x96720a
COLOR_ERROR = 0x930909
COLOR_SUCCESS = 0x00ff00

WHITELIST_KEY = "Nova81y2uv1iqbbanHub9ns"
ROLE_BUYER_ID = 1402166260757696603

# =======================
# BASE DE DATOS SIMPLE
# =======================
whitelist = {}  # user_id : {key, redeemed_at, blacklisted}

# =======================
# FOOTERS
# =======================
def generar_footer_panel():
    hora = datetime.now().strftime("%H:%M")
    return f"Sent by lexcarlxs#0 | Hoy a {hora}"

def generar_footer_hora():
    hora = datetime.now().strftime("%H:%M")
    return f"Hoy a {hora}"

# =======================
# BOT
# =======================
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="https://luarmor.net/"
        )
    )
    await bot.tree.sync()
    print(f"Bot listo como {bot.user}")

@bot.event
async def on_error(event, *args, **kwargs):
    traceback.print_exc()

# =======================
# MODAL REDEEM
# =======================
class RedeemModal(discord.ui.Modal, title="Enter script key below"):
    key = discord.ui.TextInput(
        label="Script Key",
        placeholder="Vwk8u17bbqlqlp0j1qbw4"
    )

    async def on_submit(self, interaction: discord.Interaction):
        uid = interaction.user.id
        footer = generar_footer_hora()

        if uid in whitelist and whitelist[uid]["blacklisted"]:
            embed = discord.Embed(
                title="Not whitelisted",
                description="You are blacklisted.",
                color=COLOR_ERROR
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if uid in whitelist:
            embed = discord.Embed(
                title="Already whitelisted",
                description="You already redeemed a key.",
                color=COLOR_ERROR
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.key.value == WHITELIST_KEY:
            whitelist[uid] = {
                "key": self.key.value,
                "redeemed_at": datetime.now(),
                "blacklisted": False
            }
            embed = discord.Embed(
                title="Successfully Redeemed!",
                description="You are now whitelisted.",
                color=COLOR_SUCCESS
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="Invalid key",
            description="User key doesn't exist.",
            color=COLOR_ERROR
        )
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# =======================
# BOTONES
# =======================
class ControlButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔑 Redeem Key", style=discord.ButtonStyle.green)
    async def redeem(self, interaction, button):
        await interaction.response.send_modal(RedeemModal())

    async def not_whitelisted(self, interaction):
        embed = discord.Embed(
            title="Not whitelisted",
            description="Redeem a key to continue.",
            color=COLOR_ERROR
        )
        embed.set_footer(text=generar_footer_hora())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📜 Get Script", style=discord.ButtonStyle.blurple)
    async def get_script(self, interaction, button):
        uid = interaction.user.id
        if uid not in whitelist or whitelist[uid]["blacklisted"]:
            await self.not_whitelisted(interaction)
            return

        embed = discord.Embed(
            title="Your Script",
            description=(
                "```lua\n"
                'script_key = "Nova81y2uv1iqbbanHub9ns"\n'
                'loadstring(game:HttpGet("https://api.novahub.workers.dev/files/v3/loaders/novahub.lua"))()\n'
                "```"
            ),
            color=COLOR_PRINCIPAL
        )
        embed.set_footer(text=generar_footer_hora())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="📊 Get Stats", style=discord.ButtonStyle.grey)
    async def get_stats(self, interaction, button):
        uid = interaction.user.id
        if uid not in whitelist:
            await self.not_whitelisted(interaction)
            return

        data = whitelist[uid]
        embed = discord.Embed(title="Your Stats", color=COLOR_PRINCIPAL)
        embed.add_field(name="Key", value=data["key"], inline=False)
        embed.add_field(
            name="Redeemed at",
            value=data["redeemed_at"].strftime("%d/%m/%Y %H:%M"),
            inline=False
        )
        embed.add_field(name="Status", value="🟢 Whitelisted", inline=False)
        embed.set_footer(text=generar_footer_hora())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="👤 Get Role", style=discord.ButtonStyle.blurple)
    async def get_role(self, interaction, button):
        uid = interaction.user.id
        if uid not in whitelist:
            await self.not_whitelisted(interaction)
            return

        role = interaction.guild.get_role(ROLE_BUYER_ID)
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ Added {role.mention}",
                ephemeral=True
            )

# =======================
# MODAL PANEL
# =======================
class PanelModal(discord.ui.Modal, title="Create Control Panel"):
    panel_title = discord.ui.TextInput(
        label="Panel Title",
        placeholder="Autojoiner",
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.panel_title.value,
            description=(
                f"This control panel is for the project: **{self.panel_title.value}**\n"
                "Redeem your key to access the script, stats and more."
            ),
            color=COLOR_PRINCIPAL
        )
        embed.set_footer(
            text=generar_footer_panel(),
            icon_url=FOOTER_ICON
        )

        await interaction.channel.send(embed=embed, view=ControlButtons())
        await interaction.response.send_message(
            "✅ Panel created successfully",
            ephemeral=True
        )

# =======================
# COMANDO /panel
# =======================
@bot.tree.command(name="panel", description="Create control panel")
async def panel(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "No puedes usar este comando.",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(PanelModal())

# =======================
# RUN
# =======================
bot.run(os.getenv("DISCORD_TOKEN"))
