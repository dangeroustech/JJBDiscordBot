# TODO: Add an approved_user func to thin down some repeated functionality

import os
import sys
import discord
import random
import argparse
import json
import requests
from dotenv import load_dotenv

debug = False

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILDTEMP = os.getenv('DISCORD_GUILD')
client_id = os.getenv('client_id') #needs to be a github secret
client_secret = os.getenv('client_secret') #needs to be a github secret
grant_type = 'client_credentials'
twitch_userID = "jennytree95" #probably needs a better place to live?
API_ENDPOINT = "https://api.twitch.tv/helix/streams?user_login=" + twitch_userID
guildID = 0
oauth_token = ""
oauth_timer = 0

intents = discord.Intents.all()
client = discord.Client(intents=intents)


def main(argv):
    global debug

    parser = argparse.ArgumentParser(prog='python bot.py',
                                     description='Be a swagalicious royalist discord bot')
    parser.add_argument('-d', '--debug', required=False, help='Set Debug Mode for Local Dev', action='store_true')
    args = parser.parse_args()

    if args.debug:
        debug = True

    client.run(TOKEN)


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
        quote_list = []
        response = random.choice(get_royalist())
        await message.channel.send(response)

    # add a command to the royalist list (only if approved user)
    if '!addroyalist' in message.content:
        if (
                message.author.name == 'Rocketman162' or
                message.author.name == 'biodrone' or
                message.author.name == 'Tombo_-'
        ):
            add_royalist(message.content)
            await message.channel.send(f'Added Quote: {str(message.content).lstrip("!addroyalist ")}')
        else:
            # maybe send a DM here too
            await message.delete()

    # get the royalist list (only if approved user)
    if '!getroyalist' in message.content:
        if (
                message.author.name == 'Rocketman162' or
                message.author.name == 'biodrone' or
                message.author.name == 'Tombo_-'
        ):
            await message.channel.send(''.join(list_royalist()))
        else:
            # maybe send a DM here too
            print(message.author.name)
            await message.delete()

    # delete a royalist command (only if approved user)
    if '!delroyalist' in message.content:
        if (
                message.author.name == 'Rocketman162' or
                message.author.name == 'biodrone' or
                message.author.name == 'Tombo_-'
        ):
            response = del_royalist(message.content.lstrip('!delroyalist '))
            if response == "ERROR":
                await message.channel.send("There Aren't That Many Quotes... Learn to Math Please.")
            else:
                await message.channel.send("Removed Quote: {}".format(response))
        else:
            # maybe send a DM here too
            print(message.author.name)
            await message.delete()

    # context sensitive command - scheudle
    if '!schedule' in message.content:
        response = 'Check out our stream schedule here: https://www.twitch.tv/jennytree95/schedule'
        await message.channel.send(response)

    # context sensitive command - stream status
    if '!stream' in message.content:
        oauth_token = (get_oauth(client_id, client_secret, grant_type))
        response = (twitch_getstatus(oauth_token, client_id))
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
        elif (
                message.author.name != 'Rocketman162' or
                message.author.name != 'biodrone' or
                message.author.name != 'Tombo_-'
        ):
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


def add_royalist(quote):
    # add a royalist quote
    with open('royalist', 'a') as f:
        f.write('\n{}'.format(str(quote).lstrip('!addroyalist ')))


def get_royalist():
    # get all royalist quotes
    quotes = []

    with open('royalist') as f:
        for line in f:
            quotes.append(line)

    return quotes


def list_royalist():
    # get all royalist quotes
    quotes = []

    with open('royalist') as f:
        num = 1
        for line in f:
            quotes.append(str(num) + " - " + line)
            num += 1

    return quotes


def del_royalist(index):
    # delete a royalist quote
    # WARN: This writes a newline to the end of the file if the last quote is deleted

    with open('royalist') as f:
        lines = f.readlines()

    try:
        removal = lines[int(index) - 1]
        del lines[int(index) - 1]
        os.remove('royalist')

        with open('royalist', 'w+') as w:
            for line in lines:
                w.write(line)

        return removal
    except IndexError as e:
        return "ERROR"


def get_oauth(client_id, client_secret, grant_type):
    oauth_request = requests.post(
        "https://id.twitch.tv/oauth2/token?client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=" + grant_type)
    if oauth_request.status_code == 200:
        json_response = json.loads(oauth_request.text)
        #print(json_response)
        global oauth_timer
        oauth_timer = (json_response['expires_in'])
        new_oauth_token = str((json_response['access_token']))
    return new_oauth_token


def twitch_getstatus(oauth_token, client_id):
    # set data
    data = {
        'Authorization': 'Bearer ' + oauth_token,
        'Client-Id': client_id
    }
    # api call here
    status_response = requests.get(url=API_ENDPOINT, headers=data)
    # data output
    if status_response.status_code == 200:
        json_response = json.loads(status_response.text)
        #print(json_response)
        twitch_data = str((json_response['data']))
        if twitch_data == "[]":
            return (twitch_userID + " is currently OFFLINE")
        else:
            twitch_game_id = str((json_response['data'][0]['game_id']))
            #twitch_game_name = str(twitch_getgamename(twitch_game_id)) #can't get this to work right now...
            return ("**" + twitch_userID + "** is currently LIVE :movie_camera:\nGo watch here: https://twitch.tv/" + twitch_userID)


def twitch_getgamename(twitch_game_id):
    data = {
        'Authorization': 'Bearer ' + oauth_token,
        'Client-Id': client_id
    }
    getgamename_response = requests.get(url="https://api.twitch.tv/helix/games?id=" + twitch_game_id, headers=data)
    if getgamename_response.status_code == 200:
        json_response = json.loads(getgamename_response.text)
        #print(json_response)
        game_name = (json_response['data'][0]['name'])
        return game_name


if __name__ == '__main__':
    main(sys.argv)
