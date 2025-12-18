import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta

# =======================
# CONFIG
# =======================
TOKEN = "MTQ0ODkzODQ3MTM4NDE1NDE5Mw.GvS8TF.l5hpJnxA27gJIIar-IgLGekA6EXWcPnN8RKeII"
OWNER_ID = 1373716141297504428  # PON TU ID

FOOTER_ICON = "https://cdn.discordapp.com/attachments/1398867717871767582/1451039506017812542/4c6637bb61fb4d70.jpg?ex=6944b959&is=694367d9&hm=50471d27d5cc21b439d5ddac727ec2285f194b01957ef729fee3e1bafbef8fae"
COLOR_PRINCIPAL = 0x96720a
COLOR_ERROR = 0x930909
COLOR_SUCCESS = 0x00ff00

WHITELIST_KEY = "NoVaHub2025OntOpvjjsnmm38Nbshjq"
ROLE_BUYER_ID = 1443132513676427264

# =======================
# BASE DE DATOS SIMPLE
# =======================
whitelist = {}  # user_id : {"key": str, "redeemed_at": datetime, "blacklisted": bool}

# =======================
# FOOTERS
# =======================
def generar_footer_panel():
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M")
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)

    if ahora.date() == hoy:
        texto = f"Hoy a {hora}"
    elif ahora.date() == ayer:
        texto = f"Ayer a {hora}"
    else:
        texto = f"{fecha} a {hora}"

    return f"Sent by lexcarlxs#0 | {texto}"

def generar_footer_hora():
    ahora = datetime.now()
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M")
    hoy = ahora.date()
    ayer = hoy - timedelta(days=1)

    if ahora.date() == hoy:
        texto = f"Hoy a {hora}"
    elif ahora.date() == ayer:
        texto = f"Ayer a {hora}"
    else:
        texto = f"{fecha} a {hora}"

    return texto

# =======================
# BOT
# =======================
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="https://luarmor.net/"
    ))
    await bot.tree.sync()
    print(f"Bot listo como {bot.user}")

# =======================
# MODAL DE REDEEM
# =======================
class RedeemModal(discord.ui.Modal, title="Redeem a key"):
    key = discord.ui.TextInput(
        label="Enter script key below:",
        placeholder="VZeGvaxErVhZfVBLUqGqYHuVxTmfOhDm",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        footer = generar_footer_hora()

        # Verificar blacklist
        if user_id in whitelist and whitelist[user_id].get("blacklisted", False):
            embed = discord.Embed(
                title="Not whitelisted",
                description="You are blacklisted and cannot redeem any key.",
                color=COLOR_ERROR
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Ya whitelisted
        if user_id in whitelist:
            embed = discord.Embed(
                title="Already whitelisted",
                description="You already redeemed a key.",
                color=COLOR_ERROR
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Key correcta
        if self.key.value == WHITELIST_KEY:
            whitelist[user_id] = {
                "key": self.key.value,
                "redeemed_at": datetime.now(),
                "blacklisted": False
            }
            embed = discord.Embed(
                title="Successfully Redeemed!",
                description="Your key has been redeemed successfully.\nYou are now **whitelisted**.",
                color=COLOR_SUCCESS
            )
            embed.set_footer(text=footer)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Key inválida
        embed = discord.Embed(
            title="An error ocurred",
            description="User key doesn't exist",
            color=COLOR_ERROR
        )
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# =======================
# VIEW CON BOTONES
# =======================
class ControlButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # ---- REDEEM ----
    @discord.ui.button(label="🔑 Redeem Key", style=discord.ButtonStyle.green)
    async def redeem(self, interaction, button):
        await interaction.response.send_modal(RedeemModal())

    # ---- NOT WHITELISTED ----
    async def send_not_whitelisted(self, interaction: discord.Interaction):
        footer = generar_footer_hora()
        embed = discord.Embed(
            title="Not whitelisted!",
            description="You need to be whitelisted to get this.\n"
                        "If you have a script key, click on the Redeem button below to redeem it",
            color=COLOR_ERROR
        )
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---- GET SCRIPT ----
    @discord.ui.button(label="📜 Get Script", style=discord.ButtonStyle.blurple)
    async def get_script(self, interaction, button):
        user_id = interaction.user.id
        if user_id not in whitelist or whitelist[user_id].get("blacklisted", False):
            await self.send_not_whitelisted(interaction)
            return
        user_key = whitelist[user_id]["key"]
        footer = generar_footer_hora()
        embed = discord.Embed(
            title="Your Script",
            description=(
                "```lua\n"
                f'getgenv().Key = "{user_key}"\n'
                'loadstring(game:HttpGet("https://api.luarmor-net-sqyr-finder.workers.dev/"))()\n'
                "```"
            ),
            color=COLOR_PRINCIPAL
        )
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---- GET STATS ----
    @discord.ui.button(label="📊 Get Stats", style=discord.ButtonStyle.grey)
    async def get_stats(self, interaction, button):
        user_id = interaction.user.id
        if user_id not in whitelist or whitelist[user_id].get("blacklisted", False):
            await self.send_not_whitelisted(interaction)
            return
        data = whitelist[user_id]
        redeemed = data["redeemed_at"].strftime("%d/%m/%Y %H:%M")
        footer = generar_footer_hora()
        embed = discord.Embed(
            title="Your Key Stats",
            color=COLOR_PRINCIPAL
        )
        embed.add_field(name="Key", value=f"`{data['key']}`", inline=False)
        embed.add_field(name="Redeemed at", value=redeemed, inline=False)
        embed.add_field(name="Status", value="🟢 Whitelisted", inline=False)
        embed.set_footer(text=footer)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---- GET ROLE ----
    @discord.ui.button(label="👤 Get Role", style=discord.ButtonStyle.blurple)
    async def get_role(self, interaction, button):
        user_id = interaction.user.id
        if user_id not in whitelist or whitelist[user_id].get("blacklisted", False):
            await self.send_not_whitelisted(interaction)
            return
        role = interaction.guild.get_role(ROLE_BUYER_ID)
        if role:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅️Added {role.mention} role to your roles",
                    ephemeral=True
                )
            except:
                await interaction.response.send_message(
                    "❌ Could not add role, check my permissions.",
                    ephemeral=True
                )

    # ---- RESET HWID ----
    @discord.ui.button(label="⚙️ Reset HWID", style=discord.ButtonStyle.grey)
    async def reset_hwid(self, interaction, button):
        user_id = interaction.user.id
        if user_id not in whitelist or whitelist[user_id].get("blacklisted", False):
            await self.send_not_whitelisted(interaction)
            return
        await interaction.response.send_message(
            "✅️HWID ``reseted``",
            ephemeral=True
        )

# =======================
# COMANDO /panel
# =======================
@bot.tree.command(name="panel", description="Send the Autojoiner Control Panel")
async def panel(interaction: discord.Interaction):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("No puedes usar este comando.", ephemeral=True)
        return
    await interaction.response.send_message("listo bro🥺", ephemeral=True)
    embed = discord.Embed(
        title="Auto Joiner Nova Control Panel",
        description=(
            "This control panel is for the project: **Auto Joiner Nova**\n"
            "Redeem your key to access the script, stats and more."
        ),
        color=COLOR_PRINCIPAL
    )
    embed.set_footer(text=generar_footer_panel(), icon_url=FOOTER_ICON)
    await interaction.channel.send(embed=embed, view=ControlButtons())

# =======================
# COMANDO /whitelist
# =======================
@bot.tree.command(name="whitelist", description="Whitelist a user manually")
@app_commands.describe(user="User to whitelist")
async def whitelist_user(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("No puedes usar este comando.", ephemeral=True)
        return

    # Mensaje efímero
    await interaction.response.send_message("listo bro🥺", ephemeral=True)

    # Agregar a whitelist
    whitelist[user.id] = {
        "key": WHITELIST_KEY,
        "redeemed_at": datetime.now(),
        "blacklisted": False
    }

    # Mensaje normal en el canal
    await interaction.channel.send(f"You have been whitelisted {user.mention} check your DMs")

    # Mandar DM con la key
    try:
        await user.send(f"You have been whitelisted {user.mention}.\nYour key is: `{WHITELIST_KEY}`")
    except:
        pass

# =======================
# COMANDO /blacklist
# =======================
@bot.tree.command(name="blacklist", description="Blacklist a user")
@app_commands.describe(user="User to blacklist")
async def blacklist_user(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message("No puedes usar este comando.", ephemeral=True)
        return

    # Mensaje efímero
    await interaction.response.send_message("listo bro🥺", ephemeral=True)

    # Marcar como blacklisted
    if user.id in whitelist:
        whitelist[user.id]["blacklisted"] = True

    # Mensaje normal en el canal
    await interaction.channel.send(f"{user.mention} Your Whitelist is expired or added to blacklist")

# =======================
bot.run(TOKEN)
