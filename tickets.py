import sqlite3

import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")


# Creates the basic form structure
@bot.tree.command()
async def form_create(
    interaction: discord.Interaction,
    title: str,
    question1: str,
    placeholder1: str,
    question2: str,
    placeholder2: str,
):
    """Create a new form with the given title and questions."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='forms';"
            )
            table = c.fetchone()
            if table is None:
                c.execute(
                    "CREATE TABLE forms ("
                    "id INTEGER PRIMARY KEY, title TEXT, question1 TEXT,"
                    " placeholder1 TEXT, question2 TEXT, placeholder2 TEXT)"
                )

            c.execute("SELECT * FROM forms WHERE title = ?", (title,))
            if existing_form := c.fetchone():
                await interaction.response.send_message(
                    f"**A form with the title `{title}` already exists!**"
                    f"\n**Please create a form with a different title.**"
                )
            else:
                c.execute(
                    "INSERT INTO forms (title, question1, placeholder1, question2, placeholder2)"
                    "VALUES (?,?,?,?,?)",
                    (title, question1, placeholder1, question2, placeholder2),
                )
                conn.commit()
                conn.close()

                await interaction.response.send_message(
                    f"**Form `{title}` has been created successfully!**"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Selects a form and displays it, form is non-interactive
# (you can't fill it out by calling this command)
@bot.tree.command()
async def form_view(interaction: discord.Interaction, title: str):
    """View an existing form with the given title."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()

            c.execute("SELECT * FROM forms WHERE title = ?", (title,))
            if form := c.fetchone():
                form_title, question1, placeholder1, question2, placeholder2 = (
                    form[1],
                    form[2],
                    form[3],
                    form[4],
                    form[5],
                )
                embed = discord.Embed(
                    title=form_title,
                    color=discord.Color.blue(),
                )
                embed.add_field(
                    name=question1,
                    value=placeholder1,
                    inline=False,
                )
                embed.add_field(
                    name=question2,
                    value=placeholder2,
                    inline=False,
                )
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"**Form `{title}` was not found!** :x:"
                )
            conn.close()
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Shows a list of all created forms in the database
@bot.tree.command()
async def form_list(interaction: discord.Interaction):
    """List all forms from the database and send them to the channel."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='forms'"
            )
            if c.fetchone():
                c.execute("SELECT title FROM forms")
                forms = c.fetchall()
                form_titles = "\n".join(form[0] for form in forms)
                await interaction.response.send_message(
                    f"**List of all forms:**\n`{form_titles}`"
                )
            else:
                await interaction.response.send_message(
                    "**No forms found!** :x:",
                )
            conn.close()
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Selects an individual form and deletes it from the database
@bot.tree.command()
async def form_delete(interaction: discord.Interaction, title: str):
    """Delete an existing form with the given title.
    This action cannot be undone."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()
            c.execute("SELECT * FROM forms WHERE title = ?", (title,))
            if form := c.fetchone():
                c.execute("DELETE FROM forms WHERE title=?", (title,))
                conn.commit()
                conn.close()
                await interaction.response.send_message(
                    f"**Form `{title}` has been deleted successfully!**"
                )
            else:
                await interaction.response.send_message(
                    f"**Form `{title}` was not found!** :x:"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Allows you to edit an existent form by typing out its title
# (it checks whether or not a form with that title exists)
# Work in progress: Making it so calling this command actually shows
# you the data you've previously entered in the form,
# instead of making you re-do everything
# Work in progress: Making it so it immediately warns you if
# the form title you entered is non-existent,
# instead of warning you only after you've finished the edit
@bot.tree.command()
async def form_edit(
    interaction: discord.Interaction,
    title: str,
    question1: str,
    placeholder1: str,
    question2: str,
    placeholder2: str,
):
    """Edit an existing form with the given title."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()

            c.execute("SELECT * FROM forms WHERE title = ?", (title,))
            if form := c.fetchone():
                c.execute(
                    "UPDATE forms SET question1 = ?, placeholder1 = ?, question2 = ?, placeholder2 = ? WHERE title = ?",
                    (question1, placeholder1, question2, placeholder2, title),
                )
                conn.commit()
                conn.close()

                await interaction.response.send_message(
                    f"**Form `{title}` has been edited successfully!**"
                )
            else:
                await interaction.response.send_message(
                    f"**Form `{title}` does not exist!**"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Creates a panel, checks if the given form exists
@bot.tree.command()
async def panel_create(
    interaction: discord.Interaction,
    title: str,
    description: str,
    button_text: str,
    form: str,
):
    """Create a new panel with the given title, description, and button text,
    linked to the specified form."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute(
                """CREATE TABLE IF NOT EXISTS panels
                               (id INTEGER PRIMARY KEY,
                               title TEXT,
                               description TEXT,
                               button_text TEXT,
                               form TEXT)"""
            )
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()
            c.execute("SELECT * FROM forms WHERE title = ?", (form,))
            if existing_form := c.fetchone():
                conn = sqlite3.connect("database.db")
                c = conn.cursor()
                c.execute("SELECT * FROM panels WHERE title = ?", (title,))
                if existing_panel := c.fetchone():
                    await interaction.response.send_message(
                        f"**A panel with the title `{title}` already exists!**"
                        f"\n**Please create a panel with a different title.**"
                    )
                else:
                    c.execute(
                        "INSERT INTO panels (title, description, button_text, form) VALUES (?, ?, ?, ?)",
                        (title, description, button_text, form),
                    )

                    conn.commit()
                    conn.close()

                    await interaction.response.send_message(
                        f"**Panel `{title}` has been created successfully!**"
                    )
            else:
                await interaction.response.send_message(
                    f"**The form `{form}` does not exist!**"
                    f"\n**Please create a form with the"
                    f" specified title before creating a panel.**"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Links 2 existing panels together and gives them a new joined title,
# while merging their desc, button text and form
# It doesn't delete the panels after linking them,
# they still exist individually in the db
@bot.tree.command()
async def panel_link(
    interaction: discord.Interaction,
    new_panel_title: str,
    panel1_title: str,
    panel2_title: str,
):
    """Link two existing panels together to create a new panel
    with the given title."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute(
                "SELECT description, button_text, form FROM panels WHERE title = ?",
                (panel1_title,),
            )
            panel1 = c.fetchone()

            c.execute(
                "SELECT description, button_text, form FROM panels WHERE title = ?",
                (panel2_title,),
            )
            panel2 = c.fetchone()

            if panel1 and panel2:
                # Combine the data from the two panels
                new_panel_description = panel1[0] + panel2[0]
                new_panel_button_text = panel1[1] + panel2[1]
                new_panel_form = panel1[2] + panel2[2]

                c.execute(
                    "SELECT title FROM panels WHERE title = ?",
                    (new_panel_title,),
                )
                if existing_panel := c.fetchone():
                    await interaction.response.send_message(
                        f"**A panel with the title `{new_panel_title}` already exists!**"
                    )
                else:
                    c.execute(
                        "INSERT INTO panels (title, description, button_text, form) VALUES (?,?,?,?)",
                        (
                            new_panel_title,
                            new_panel_description,
                            new_panel_button_text,
                            new_panel_form,
                        ),
                    )
                    conn.commit()
                    conn.close()
                    await interaction.response.send_message(
                        f"**New panel `{new_panel_title}` has been created successfully!**"
                    )
            else:
                await interaction.response.send_message(
                    "**One or both of the panels were not found!** :x:"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Selects and deletes a individual panel from db
@bot.tree.command()
async def panel_delete(interaction: discord.Interaction, title: str):
    """Delete the panel with the specified title.
    This action cannot be undone."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT * FROM panels WHERE title=?", (title,))
            if panel := c.fetchone():
                c.execute("DELETE FROM panels WHERE title=?", (title,))
                conn.commit()
                conn.close()
                await interaction.response.send_message(
                    f"**Panel `{title}` deleted successfully!**"
                )
            else:
                await interaction.response.send_message(
                    f"**Panel `{title}` was not found!** :x:"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Retrieves a panel from the db, non-interactive for now
# Work in progress: Making a functional button that will allow the user
# to access the form and fill it out, and then
# create a new ticket channel with the options to close the ticket,
# limit ticket amount (basically all the harder stuff)
@bot.tree.command()
async def panel_retrieve(interaction: discord.Interaction, title: str):
    """Retrieve the specified panel from the database
    and send it to the channel."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute("SELECT * FROM panels WHERE title=?", (title,))
            if panel := c.fetchone():
                title, description, button_text, form = (
                    panel[1],
                    panel[2],
                    panel[3],
                    panel[4],
                )
                embed = discord.Embed(
                    title="Ticket Information", color=discord.Color.blue()
                )
                embed.add_field(name=title, value=description, inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    f"**Panel `{title}` was not found!** :x:"
                )
            conn.close()
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Lists all available panels in the db by their title
@bot.tree.command()
async def panel_list(interaction: discord.Interaction):
    """List all panel titles from the database
    and send them to the channel."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='panels'"
            )
            if c.fetchone():
                c.execute("SELECT title FROM panels")
                panels = c.fetchall()
                panel_titles = "\n".join(panel[0] for panel in panels)
                await interaction.response.send_message(
                    f"**List of all panels:**\n`{panel_titles}`"
                )
            else:
                await interaction.response.send_message("**No panels found!** :x:")
                conn.close()
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Allows you to edit a panel (same limitations as form_edit, work in progress)
@bot.tree.command()
async def panel_edit(
    interaction: discord.Interaction,
    title: str,
    description: str,
    button_text: str,
    form: str,
):
    """Edit an existing panel with the given title."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            c.execute("SELECT * FROM panels WHERE title = ?", (title,))
            if panel := c.fetchone():
                c.execute(
                    "UPDATE panels SET description = ?, button_text = ?, form = ? WHERE title = ?",
                    (description, button_text, form, title),
                )
                conn.commit()
                conn.close()

                await interaction.response.send_message(
                    f"**Panel `{title}` has been edited successfully!**"
                )
            else:
                await interaction.response.send_message(
                    f"**Panel `{title}` does not exist!**"
                )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Wipes the entire panel db
# Work in progress: Making a confirmation system so terrence
# doesn't end up deleting everything on accident
@bot.tree.command()
async def panel_wipe(interaction: discord.Interaction):
    """Wipe the entire panel database. This action cannot be undone."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("database.db")
            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()

            for table in tables:
                c.execute(f"DROP TABLE IF EXISTS {table[0]}")

            conn.commit()
            conn.close()

            await interaction.response.send_message(
                "**The database has been successfully wiped!**\
                :white_check_mark:"
            )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )


# Wipes the entire form db
# Work in progress (same as panel_wipe)
@bot.tree.command()
async def form_wipe(interaction: discord.Interaction):
    """Wipe the entire form database. This action cannot be undone."""
    for guild in bot.guilds:
        project_managers = discord.utils.get(
            guild.roles,
            name="Project Managers",
        )
        if not isinstance(interaction.user, discord.Member):
            return
        if project_managers in interaction.user.roles:
            conn = sqlite3.connect("forms.db")
            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()

            for table in tables:
                c.execute(f"DROP TABLE IF EXISTS {table[0]}")

            conn.commit()
            conn.close()

            await interaction.response.send_message(
                "**The forms database has been successfully wiped!**"
                ":white_check_mark:"
            )
        else:
            await interaction.response.send_message(
                "**You do not have permission to run this command!** :x:"
            )