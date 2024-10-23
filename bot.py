import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Charger les variables d'environnement du fichier .env
load_dotenv()

# Récupérer le token Discord depuis les variables d'environnement
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True  # Nécessaire pour suivre les changements d'état vocal

bot = commands.Bot(command_prefix="!", intents=intents)

# Définissez les salons de base et leurs limites de personnes
CREATE_CHANNELS = {
    "duo": 2,
    "trio": 3,
    "Créer un Quatuor": 4,
    "Créer un Groupe de 6": 6,
}

# Mapping des types de salons à leurs catégories
CATEGORY_MAPPING = {
    "duo": "Catégorie Duo",
    "trio": "𝒯𝑅𝐼𝒜𝒟𝐸 - 3 pers",
    "Créer un Quatuor": "Catégorie Quatuor",
    "Créer un Groupe de 6": "Catégorie Groupe de 6",
}

# Event quand un membre rejoint un canal vocal
@bot.event
async def on_voice_state_update(member, before, after):
    # Vérifie si l'utilisateur vient de rejoindre un nouveau canal vocal
    if after.channel is not None:
        channel_name = after.channel.name
        
        # Vérifie si le canal rejoint fait partie des canaux "Créer"
        if channel_name in CREATE_CHANNELS:
            guild = member.guild
            limit = CREATE_CHANNELS[channel_name]

            new_channel_name = f"{channel_name} de {member.name}"
            category_name = CATEGORY_MAPPING[channel_name]
            category = discord.utils.get(guild.categories, name=category_name)

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                member: discord.PermissionOverwrite(view_channel=True, connect=True)
            }

            new_channel = await guild.create_voice_channel(
                name=new_channel_name, 
                overwrites=overwrites, 
                user_limit=limit, 
                category=category
            )

            await member.move_to(new_channel)

            # Optionnel : Supprimer le canal automatiquement après que tout le monde l'ait quitté
            def check_empty_channel():
                return len(new_channel.members) == 0

            await bot.wait_for('voice_state_update', timeout=60.0, check=lambda m, b, a: check_empty_channel())
            if check_empty_channel():
                await new_channel.delete()

# Lancer le bot avec le token
bot.run(DISCORD_TOKEN)
