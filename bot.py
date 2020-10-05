import os
import sys
import discord
import random
import argparse
from dotenv import load_dotenv

debug = False

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDTEMP = os.getenv('DISCORD_GUILD')
guildID = 0

intents = discord.Intents.all()
client = discord.Client(intents=intents)


# runs when client is initially ready
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

    if not debug:
        await send_reboot_message()
        await post_commands()


# runs when client receives a message
@client.event
async def on_message(message):
    global guildID

    # make sure we don't trigger on our own messages
    if message.author == client.user:
        return

    # is a meme
    if '!sweat' in message.content:
        response = 'Actually, since being a war hero in the Falklands, I can\'t sweat.'
        await message.channel.send(response)

    # context sensitive command - royalist
    if '!royalist' in message.content:
        quote_list = ['I have no recollection of ever meeting this lady, none whatsoever.', 'I was with the children and I\'d taken Beatrice to a Pizza Express in Woking', 'Today is reality. Yesterday is history.', 'I look at Canada like a second home.', 'Actually, since being a war hero in the Falklands, I can\'t sweat.', 'Love and Light', 'UNROLL THE TADPOLE OSFrog UNCLOG THE FROG OSFrog UNLOAD THE TOAD OSFrog UNINHIBIT THE RIBBIT OSFrog', 'Spread love everywhere you go. Let no one ever come to you without leaving happier.', 'The optimist thinks this is the best of all possible worlds. The pessimist fears it is true.', 'One day, in retrospect, the years of struggle will strike you as the most beautiful.']
        response = random.choice(quote_list)
        await message.channel.send(response)

    # context sensitive command - scheudle
    if '!schedule' in message.content:
        response = 'Check out our stream schedule here: https://www.twitch.tv/jennytree95/schedule'
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


# post current commands to the welcome channel
async def post_commands():
    global guildID

    guild = client.get_guild(guildID)

    for channel in guild.channels:
        if channel.name == 'welcome-and-rules':
            await delete_old_commands(channel)

            commands = parse_commands()

            ls = "My commands are:\n"
            for key in commands:
                ls = ls + key + "\n" + "  - " + commands[key] + "\n"

            await channel.send(ls.replace("him", "me").replace("his", "my"))
            break


# parse the currently available commands
def parse_commands():
    commands = {}

    with open('README.md') as f:
        for line in f:
            if line[0] == '-':
                commands.update({f'{line.lstrip("- ").rstrip()}': f'{f.readline().lstrip("- ").rstrip()}'})

    return commands


# delete the last commands message
async def delete_old_commands(channel):

    async for message in channel.history(limit=2, oldest_first=False):
        if message.author == client.user:
            await message.delete()


# ping the bot-test channel with a reboot message
async def send_reboot_message():
    global guildID

    guild = client.get_guild(guildID)

    for channel in guild.channels:
        if channel.name == 'bot-test':
            await channel.send('Bleep Bloop, I\'ve Rebuilt.\nGod Save The One Formerly Named Markle')
            break

def main(argv):
    global debug

    parser = argparse.ArgumentParser(prog='python bot.py',
                                     description='Be a swagalicious royalist discord bot')
    parser.add_argument('-d', '--debug', required=False, help='Set Debug Mode for Local Dev', action='store_true')
    args = parser.parse_args()

    if args.debug:
        debug = True

    client.run(TOKEN)

if __name__ == '__main__':
    main(sys.argv)
