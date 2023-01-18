import discord
import discord.ext
from discord.ext import commands
import asyncio
import json
from apscheduler.schedulers.background import BackgroundScheduler
import time

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} command(s)')


#@bot.tree.command(name='help', description='Displays a list of all available commands.')
#async def help(interaction: discord.Interaction):
#    help_embed = discord.Embed(title='Commands',
#                               description='``!help``\n**Displays this help message.**\n\n``!taskdone``\n **Adds +1 to your amount of completed tasks.**\n\n``!viewtasks``\n**Displays a list of every developer and their number of completed tasks.**',
#                               color=0x2f3136)
#    await interaction.response.send_message(embed=help_embed)


@bot.tree.command(name='ping', description="Displays the bot's latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f'**Latency:** {bot.latency} Milliseconds')

@bot.tree.command(name='clayton', description= 'Face reveal of Terrence.')
async def clayton(interaction: discord.Interaction):
    await interaction.response.send_message(
        'https://i.pinimg.com/originals/f3/25/40/f32540c61fd8c8f585bbb99161632934.jpg'
    )

@bot.tree.command(name='taskdone', description ='Adds +1 to your amount of completed tasks.')
async def taskdone(interaction: discord.Interaction):
    authorID = str(interaction.user.id)
    for guild in bot.guilds:
        juniorDevs = discord.utils.get(guild.roles, name='Junior Developers')
        seniorDevs = discord.utils.get(guild.roles, name='Senior Developers')
        leadDevs = discord.utils.get(guild.roles, name='Lead Developers')
        projectManagers = discord.utils.get(guild.roles, name="Project Managers")

        if juniorDevs in interaction.user.roles or seniorDevs in interaction.user.roles or leadDevs in interaction.user.roles or projectManagers in interaction.user.roles:
            with open('database.json', 'r') as f:
                data = json.load(f)

            if authorID in data.keys():
                data[authorID] += 1

                with open('database.json', 'w') as f:
                    json.dump(data, f, indent=2)

            elif authorID not in data.keys():
                data[authorID] = 1

                with open('database.json', 'w') as f:
                    json.dump(data, f, indent=2)

            await interaction.response.send_message('**Task amount updated!** :white_check_mark:')
        else:
            await interaction.response.send_message('**You do not have permission to run this command!** :x:')

@bot.tree.command(name='viewtasks', description = 'Displays a list of every developer and their number of completed tasks.')
async def viewtasks(interaction: discord.Interaction):
    for guild in bot.guilds:
        juniorDevs = discord.utils.get(guild.roles, name='Junior Developers')
        seniorDevs = discord.utils.get(guild.roles, name='Senior Developers')
        leadDevs = discord.utils.get(guild.roles, name='Lead Developers')
        projectManagers = discord.utils.get(guild.roles, name="Project Managers")

        # Open the database file in read mode
        with open('database.json', 'r') as database:
            # Load the contents of the file into a dictionary
            data = json.load(database)

        if juniorDevs in interaction.user.roles or seniorDevs in interaction.user.roles or leadDevs in interaction.user.roles or projectManagers in interaction.user.roles:
            message_text = "".join(
                f"<@{user_id}>**: {value}**\n"
                for user_id, value in sorted(
                    data.items(), key=lambda x: x[1], reverse=True
                )
            )
            # Create the embed
            task_embed = discord.Embed(title='Tasks Completed This Week', description=message_text, color=0x2f3136)

            # Send the embed
            await interaction.response.send_message(embed=task_embed)

        else:
            # The message author does not have one of the roles
            #Don't perform the code actions
            await interaction.response.send_message('**You do not have permission to run this command!** :x:')


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


scheduler = BackgroundScheduler()

# Schedule the reset_values function to run every Monday at 00:00
scheduler.add_job(reset_values, 'cron', day_of_week='1', hour=0, minute=0)

scheduler.start()


# non-slash command part of code
@bot.event
async def on_message(message):
    args = str(message.content).lower().split(' ')
    if args[0] == 'bruh':
        await message.channel.send('<:bruh_stone:1059119664543825950>')

    elif args[0] == "i'm" and " ".join(args[1:]) == "horny":
        await message.channel.send('https://tenor.com/view/vorzek-vorzneck-oglg-og-lol-gang-gif-24901093')

    elif args[0] == "im" and " ".join(args[1:]) == "horny":
        await message.channel.send('https://tenor.com/view/vorzek-vorzneck-oglg-og-lol-gang-gif-24901093')
        
    elif args[0] == 'moo':
        await message.channel.send('https://tenor.com/view/holy-cow-holy-cow-gif-25938150')


bot.run('')
