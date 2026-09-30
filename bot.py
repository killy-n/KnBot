import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('.env.local')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

welcome_channel_id = None
role_pilote_id = None
role_atc_id = None

@bot.event
async def on_ready():
    print(f'{bot.user} est connecte!')
    print(f'ID du bot: {bot.user.id}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    global welcome_channel_id
    if welcome_channel_id:
        channel = bot.get_channel(welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="Bienvenue!",
                description=f"Bienvenue {member.mention} sur le serveur!",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.add_field(name="Membre", value=member.name, inline=True)
            embed.set_footer(text="Nous sommes ravis de t'avoir parmi nous!")
            await channel.send(embed=embed)

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command(name='bonjour')
async def bonjour(ctx):
    await ctx.send(f'Bonjour {ctx.author.mention}!')

@bot.command(name='aide')
async def aide(ctx):
    help_text = """
**Commandes disponibles:**
- `!ping` - Teste la connexion
- `!bonjour` - Dit bonjour
- `!aide` - Affiche cette aide
- `!setwelcome <channel_id>` - Definit le salon de bienvenue
- `!setroles <pilote_id> <atc_id>` - Definit les IDs des roles
- `!rolepanel` - Envoie le panel de selection de roles
    """
    await ctx.send(help_text)

@bot.command(name='setwelcome')
async def setwelcome(ctx, channel_id: int):
    global welcome_channel_id
    welcome_channel_id = channel_id
    await ctx.send(f'Salon de bienvenue defini sur: {channel_id}')

@bot.command(name='setroles')
async def setroles(ctx, pilote_id: int, atc_id: int):
    global role_pilote_id, role_atc_id
    role_pilote_id = pilote_id
    role_atc_id = atc_id
    await ctx.send(f'Roles definis: Pilote={pilote_id}, ATC={atc_id}')

class RoleButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="PILOTE", style=discord.ButtonStyle.green, custom_id="pilote_role", emoji="✈️")
    async def pilote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global role_pilote_id
        if role_pilote_id:
            role = interaction.guild.get_role(role_pilote_id)
            if role:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message("Role Pilote retire!", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("Role Pilote ajoute!", ephemeral=True)
            else:
                await interaction.response.send_message("Role introuvable!", ephemeral=True)
        else:
            await interaction.response.send_message("Role non configure!", ephemeral=True)

    @discord.ui.button(label="ATC", style=discord.ButtonStyle.primary, custom_id="atc_role", emoji="🎧")
    async def atc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global role_atc_id
        if role_atc_id:
            role = interaction.guild.get_role(role_atc_id)
            if role:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message("Role ATC retire!", ephemeral=True)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("Role ATC ajoute!", ephemeral=True)
            else:
                await interaction.response.send_message("Role introuvable!", ephemeral=True)
        else:
            await interaction.response.send_message("Role non configure!", ephemeral=True)

@bot.command(name='rolepanel')
async def rolepanel(ctx):
    embed = discord.Embed(
        title="Selection de Role",
        description="Ces roles sont purement decoratifs et permettent d'identifier qui est ATC sur IVAO, VATSIM ou autre, ou qui est Pilote.",
        color=discord.Color.blue()
    )
    embed.add_field(name="✈️・𝑷𝑰𝑳𝑶𝑻𝑬", value="Pour les pilotes sur IVAO, VATSIM ou autre", inline=False)
    embed.add_field(name="🎧・𝑨𝑻𝑪", value="Pour les controleurs aeriens sur IVAO, VATSIM ou autre", inline=False)
    embed.set_footer(text="Cliquez sur les boutons pour obtenir ou retirer les roles")
    
    view = RoleButton()
    await ctx.send(embed=embed, view=view)

bot.run(os.getenv('DISCORD_TOKEN'))
