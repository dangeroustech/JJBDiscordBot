import os
import sys
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDTEMP = os.getenv('DISCORD_GUILD')
guildID = 0

intents = discord.Intents.all()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    global guildID

    # find correct guild
    for guild in client.guilds:
        if guild.name == GUILDTEMP:
            guildID = guild.id
            break

    guild = client.get_guild(guildID)

    # exit if something is wrong with the guild discovery
    if guild == 0:
        print('Something\'s Wrong... Please to be Fixing...')
        sys.exit(999)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    for member in guild.members:
        print(f' - {member.name}')


@client.event
async def on_message(message):
    global guildID

    # make sure we don't trigger on our own messages
    if message.author == client.user:
        return

    # is a meme
    if message.content == '!sweat':
        response = 'Actually, since being a war hero in the Falklands, I can\'t sweat.'
        await message.channel.send(response)

    # controls role assignment for those who accept
    if message.channel.name == 'welcome-and-rules':
        # grant users the 'ThirstTrap' role
        if message.content == '!acceptrules':
            guild = client.get_guild(guildID)
            member = guild.get_member(message.author.id)
            await member.add_roles(guild.get_role(762318229514485801), reason=f'User {message.author} accepted rules')
            await message.delete()
        # handle users posting something else in this channel
        elif (message.author.name != 'Rocketman162' or
              message.author.name != 'biodrone' or
              message.author.name != 'Tombo_-'):
            await message.delete()


client.run(TOKEN)
