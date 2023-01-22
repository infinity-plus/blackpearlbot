import discord
import sqlite3
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS triggers (trigger text, response text)''')
    conn.commit()
    conn.close()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Retrieve the response for the triggered word
    c.execute(f"SELECT response FROM triggers WHERE trigger='{message.content.strip().lower()}'")
    result = c.fetchone()
    if result:
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
    result = c.fetchone()
    if result:
        await interaction.response.send_message(
            f"Trigger word ``{trigger}`` already exists, please use a different word.")
    else:
        # Insert the trigger word and response into the triggers table
        c.execute(f"INSERT INTO triggers (trigger, response) VALUES ('{trigger}', '{response}')")
        conn.commit()
        await interaction.response.send_message(f"Filter added: {trigger} -> {response}")
    conn.close()


@bot.tree.command()
async def filter_delete(interaction: discord.Interaction, trigger: str):
    """Delete a filter by its trigger word."""
    # Connect to the SQLite database
    conn = sqlite3.connect('triggers.db')
    c = conn.cursor()
    # Check if the trigger word exists in the triggers table
    c.execute(f"SELECT * FROM triggers WHERE trigger='{trigger}'")
    result = c.fetchone()
    if result:
        c.execute(f"DELETE FROM triggers WHERE trigger='{trigger}'")
        conn.commit()
        await interaction.response.send_message(f"Filter deleted successfully!")
    else:
        await interaction.response.send_message(f"Trigger word ``{trigger}`` does not exist.")
    conn.close()


@bot.tree.command()
async def filter_wipe(interaction: discord.Interaction):
    """Wipe the filter database."""
    confirm_message = await interaction.channel.send(
        "Are you sure you want to delete all filters?\nThis action cannot be undone."
        "\nType `yes` to confirm or `no` to cancel.")

    def check(m):
        return m.content.lower() in (
            'yes', 'no') and m.channel == interaction.channel and m.author == interaction.user

    try:
        confirm_response = await bot.wait_for('message', check=check, timeout=60.0)
        if confirm_response.content.lower() == 'yes':
            conn = sqlite3.connect('triggers.db')
            c = conn.cursor()
            # Delete all rows from the triggers table
            c.execute("DELETE FROM triggers")
            conn.commit()
            await interaction.channel.send("Filter database has been successfully wiped!")
        else:
            await interaction.channel.send("Filter wipe canceled.")
    except asyncio.TimeoutError:
        # If the user does not confirm within 60 seconds, send a message and return
        await confirm_message.edit(content="Filter wipe cancelled, time limit exceeded.")
        return
      
      
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
    filters = []
    # Loop through the result set and append the trigger word and response to a list
    for trigger, response in result:
        filters.append(f"{trigger} -> {response}")
    # Join all items in the list into a single string
    filters_string = "\n".join(filters)
    await interaction.response.send_message(f"All filters:\n{filters_string}")
    conn.close()

bot.run(TOKEN)
