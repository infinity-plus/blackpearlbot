import discord
from discord.ext import commands
import asyncio
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time


# ---------- USER CONFIGURABLE SECTION -----------------
token = ''  # Stores the bot's token. Used to pass the bot's token into bot.run in order to run the bot.
bot = commands.Bot(command_prefix='', intents=discord.Intents.all())  # Changing the bot's intents will break functionality! Only touch this if you know what you're doing!
bot.Prefix = '!'  # Defines the bot's command prefix.
# ---------- END OF USER CONFIGURABLE SECTION ----------


@bot.event
async def on_message(message):  # Runs the code whenever a message is sent in the server.
    args = str(message.content).lower().split(' ')  # Converts the message.content into an str, lowers the case of all the characters, splits the data into separate keys wherever there's a space, and stores the keys in an array.
    authorID = str(message.author.id)
    for guild in bot.guilds:
        # Get the role objects for the roles on the current guild
        juniorDevs = discord.utils.get(guild.roles, name='Junior Developers')
        seniorDevs = discord.utils.get(guild.roles, name='Senior Developers')
        leadDevs = discord.utils.get(guild.roles, name='Lead Developers')
        projectManagers = discord.utils.get(guild.roles, name="Project Managers")

        if args[0] == bot.Prefix + 'taskdone':
            # Check if the message author has one of the roles
            if juniorDevs in message.author.roles or seniorDevs in message.author.roles or leadDevs in message.author.roles or projectManagers in message.author.roles:
                # The message author has one of the roles
                # Perform the code actions

                # Open the database file in read mode
                with open('database.json', 'r') as f:
                    # Load the contents of the file into a dictionary
                    data = json.load(f)

                if authorID in data.keys():
                    # Increment the value of the message author's key by 1
                    data[authorID] += 1

                    # Open the file in write mode
                    with open('database.json', 'w') as f:
                        # Write the updated dictionary to the file
                        json.dump(data, f, indent=2)

                elif authorID[0] not in data.keys():
                    data[authorID] = 1

                    # Open the file in write mode
                    with open('database.json', 'w') as f:
                        # Write the updated dictionary to the file
                        json.dump(data, f, indent=2)

                await message.channel.send('**Task amount updated!** :white_check_mark:')
            elif juniorDevs not in message.author.roles or seniorDevs not in message.author.roles or leadDevs not in message.author.roles or projectManagers not in message.author.roles:
                # The message author does not have one of the roles
                # Don't perform the code actions
                await message.channel.send('**You do not have permission to run this command!** :x:')

    if args[0] == bot.Prefix + 'viewtasks':
        # Get the role object for the role on the current guild
        juniorDevs = discord.utils.get(guild.roles, name='Junior Developers')
        seniorDevs = discord.utils.get(guild.roles, name='Senior Developers')
        leadDevs = discord.utils.get(guild.roles, name='Lead Developers')
        projectManagers = discord.utils.get(guild.roles, name='Project Managers')

        for guild in bot.guilds:
            # Open the database file in read mode
            with open('database.json', 'r') as database:
                # Load the contents of the file into a dictionary
                data = json.load(database)

            if juniorDevs in message.author.roles or seniorDevs in message.author.roles or leadDevs in message.author.roles or projectManagers in message.author.roles:
                # Initialize the message
                message_text = ""
                # Build the message using string formatting
                for user_id, value in sorted(data.items(), key=lambda x: x[1], reverse=True):
                    message_text += f"<@{user_id}>**: {value}**\n"

                # Create the embed
                task_embed = discord.Embed(title='Tasks Completed This Week', description=message_text, color=0x2f3136)

                # Send the embed
                await message.channel.send(content=None, embed=task_embed)

            elif juniorDevs not in message.author.roles or seniorDevs not in message.author.roles or leadDevs not in message.author.roles or projectManagers not in message.author.roles:
                # The message author does not have one of the roles
                # Don't perform the code actions
                await message.channel.send('**You do not have permission to run this command!** :x:')

    if args[0] == bot.Prefix + 'help':
        help_embed = discord.Embed(title='Commands', description='**!help - Displays this help message.\n\n!taskdone - Adds +1 to your amount of completed tasks.\n\n!viewtasks - Displays a list of every developer and their number of completed tasks.**', color=0x2f3136)
        await message.channel.send(content=None, embed=help_embed)

    if args[0] == 'bruh':
        await message.channel.send('<:bruh_stone:1059119664543825950>')

    if args[0] == bot.Prefix + 'ping':
        await message.channel.send(f'**Latency:** {bot.latency} Milliseconds')

    if args[0] == "I'm horny" or "Im horny":
        await message.channel.send('https://tenor.com/view/vorzek-vorzneck-oglg-og-lol-gang-gif-24901093')

def reset_values():
    # Open the database file in read mode
    with open('database.json', 'r') as f:
        # Load the contents of the file into a dictionary
        data = json.load(f)

    # Iterate through the keys in the dictionary
    for key in data.keys():
        # Set the value of each key to 0
        data[key] = 0

    # Open the file in write mode
    with open('database.json', 'w') as f:
        # Write the updated dictionary to the file
        json.dump(data, f, indent=2)

# Create a scheduler
scheduler = BackgroundScheduler()

# Schedule the reset_values function to run every Monday at 00:00
scheduler.add_job(reset_values, 'cron', day_of_week='1', hour=0, minute=0)

# Start the scheduler
scheduler.start()


bot.run(token)  # Passes in the token from the token variable and runs the bot.
