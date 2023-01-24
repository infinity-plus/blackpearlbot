import discord
import sqlite3
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Create the triggers table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS triggers (trigger text, response text)''')
    conn.commit()
    conn.close()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Retrieve the response for the triggered word
    c.execute(f"SELECT response FROM triggers WHERE trigger='{message.content.strip().lower()}'")
    if result := c.fetchone():
        await message.channel.send(result[0])
    conn.close()


@bot.tree.command()
async def filter_add(interaction: discord.Interaction, trigger: str, response: str):
    """Create a new filter with the trigger word and a response."""
    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Check if the trigger word already exists in the triggers table
    c.execute(f"SELECT * FROM triggers WHERE trigger='{trigger}'")
    if c.fetchone():
        await interaction.response.send_message(
            f"Trigger word ``{trigger}`` already exists, please use a different word.")
    else:
        # Insert the trigger word and response into the triggers table
        c.execute(f"INSERT INTO triggers (trigger, response) VALUES ('{trigger}', '{response}')")
        conn.commit()
        await interaction.response.send_message(f"Filter added: ``{trigger}`` -> {response}")
    conn.close()


@bot.tree.command()
async def filter_delete(interaction: discord.Interaction, trigger: str):
    """Delete a filter by its trigger word."""
    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Check if the trigger word exists in the triggers table
    c.execute(f"SELECT * FROM triggers WHERE trigger='{trigger}'")
    if c.fetchone():
        c.execute(f"DELETE FROM triggers WHERE trigger='{trigger}'")
        conn.commit()
        await interaction.response.send_message("Filter deleted successfully!")
    else:
        await interaction.response.send_message(f"Trigger word ``{trigger}`` does not exist.")
    conn.close()


class Buttons(discord.ui.View):
    def __init__(self, author):
        self.author = author
        super().__init__()

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.View):
        if interaction.user == self.author:
            await interaction.response.send_message('Filter database has been successfully wiped!')
            self.value = 'Yes'
            conn = sqlite3.connect('triggers.db')
            c = conn.cursor()
            c.execute("DELETE FROM triggers")
            conn.commit()
            self.stop()
        else:
            await interaction.response.send_message(
                f'{interaction.user.mention} You are not authorized to perform this action.')

    @discord.ui.button(label='No', style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.View):
        if interaction.user == self.author:
            await interaction.response.send_message('Filter wipe has been canceled.')
            self.value = 'No'
            self.stop()
        else:
            await interaction.response.send_message(
                f'{interaction.user.mention} You are not authorized to perform this action.')


@bot.tree.command()
async def filter_wipe(interaction):
    """Wipe the filter database."""
    # Send a message asking the user to confirm the action
    view = Buttons(interaction.user)
    embed = discord.Embed(title='Are you sure you want to delete all filters?',
                          description=':warning: This action cannot be undone.',
                          color=discord.Color.from_rgb(54, 57, 63))
    await interaction.channel.send(embed=embed, view=view)


@bot.tree.command()
async def filter_list(interaction: discord.Interaction):
    """List all existing filter triggers and responses."""
    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Select all rows from the triggers table
    c.execute("SELECT * FROM triggers")
    result = c.fetchall()
    if len(result) == 0:
        await interaction.response.send_message("There are no filters in the database.")
        conn.close()
        return
    filters = [f"``{trigger}``-> {response}" for trigger, response in result]
    # Join all items in the list into a single string
    filters_string = "\n".join(filters)
    embed = discord.Embed(title='List of all filters:',
                          description=f'\n{filters_string}',
                          color=discord.Color.from_rgb(54, 57, 63))
    await interaction.channel.send(embed=embed)
    conn.close()


bot.run(TOKEN)
