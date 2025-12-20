import discord
from discord.ext import commands
from datetime import datetime
import os
import traceback

# =======================
# CONFIG
# =======================
OWNER_ID = 1373716141297504428

FOOTER_ICON = "https://cdn.discordapp.com/attachments/1398867717871767582/1451976357784453150/Death_Note_icon__3.jpg"
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
# FOOTER GENERATOR
# =======================
def generar_footer_panel(fecha: datetime):
    return f"Sent by lexcarlxs#0 | {fecha.strftime('%d/%m/%Y %H:%M')}"

def generar_footer_hora():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

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
    key = discord.ui.TextInput(label="Script Key")

    async def on_submit(self, interaction: discord.Interaction):
        uid = interaction.user.id
        footer = generar_footer_hora()

        if uid in whitelist and whitelist[uid]["blacklisted"]:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not whitelisted",
                    description="You are blacklisted.",
                    color=COLOR_ERROR
                ).set_footer(text=footer),
                ephemeral=True
            )
            return

        if uid in whitelist:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Already whitelisted",
                    description="You already redeemed a key.",
                    color=COLOR_ERROR
                ).set_footer(text=footer),
                ephemeral=True
            )
            return

        if self.key.value == WHITELIST_KEY:
            whitelist[uid] = {
                "key": self.key.value,
                "redeemed_at": datetime.now(),
                "blacklisted": False
            }
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Successfully Redeemed!",
                    description="You are now whitelisted.",
                    color=COLOR_SUCCESS
                ).set_footer(text=footer),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Invalid key",
                description="User key doesn't exist.",
                color=COLOR_ERROR
            ).set_footer(text=footer),
            ephemeral=True
        )

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
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Not whitelisted",
                description="Redeem a key to continue.",
                color=COLOR_ERROR
            ).set_footer(text=generar_footer_hora()),
            ephemeral=True
        )

    @discord.ui.button(label="📜 Get Script", style=discord.ButtonStyle.blurple)
    async def get_script(self, interaction, button):
        uid = interaction.user.id
        if uid not in whitelist or whitelist[uid]["blacklisted"]:
            await self.not_whitelisted(interaction)
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Your Script",
                description=(
                    "```lua\n"
                    'script_key = "Nova81y2uv1iqbbanHub9ns"\n'
                    'loadstring(game:HttpGet("https://api.novahub.workers.dev/files/v3/loaders/novahub.lua"))()\n'
                    "```"
                ),
                color=COLOR_PRINCIPAL
            ).set_footer(text=generar_footer_hora()),
            ephemeral=True
        )

# =======================
# MODAL PANEL
# =======================
class PanelModal(discord.ui.Modal, title="Create Control Panel"):
    panel_title = discord.ui.TextInput(label="Project Name")

    async def on_submit(self, interaction: discord.Interaction):
        fecha_creacion = datetime.now()
        project_name = self.panel_title.value

        embed = discord.Embed(
            title=f"{project_name} Control Panel",
            description=(
                f"This control panel is for the project: **{project_name}**\n"
                "Redeem your key to access the script, stats and more."
            ),
            color=COLOR_PRINCIPAL
        )
        embed.set_footer(
            text=generar_footer_panel(fecha_creacion),
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
@bot.tree.command(name="panel", description="Create a control panel")
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
