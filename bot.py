import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    for member in guild.members:
        print(f' - {member.name}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # is a meme
    if message.content == '!sweat':
        response = 'Actually, since being a war hero in the Falklands, I can\'t sweat.'
        await message.channel.send(response)

    # controls role assignment for those who accept
    if message.channel.name == 'mods-discussion' and message.content == '!acceptrules':

        for guild in client.guilds:
            if guild.name == GUILD:
                break

        member = guild.get_member(message.author.id)

        await member.add_roles(guild.get_role(762318229514485801), reason=f'User {message.author} accepted rules')

client.run(TOKEN)
