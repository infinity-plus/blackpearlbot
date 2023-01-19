import json

from discord import Embed, Interaction, Member, app_commands, utils
from discord.ext import commands


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="taskdone",
        description="Adds +1 to your amount of completed tasks.",
    )
    async def taskdone(self, interaction: Interaction):
        author_id = str(interaction.user.id)
        for guild in self.bot.guilds:
            junior_devs = utils.get(
                guild.roles,
                name="Junior Developers",
            )
            senior_devs = utils.get(
                guild.roles,
                name="Senior Developers",
            )
            lead_devs = utils.get(
                guild.roles,
                name="Lead Developers",
            )
            project_managers = utils.get(
                guild.roles,
                name="Project Managers",
            )

            if not isinstance(interaction.user, Member):
                return

            if (
                junior_devs in interaction.user.roles
                or senior_devs in interaction.user.roles
                or lead_devs in interaction.user.roles
                or project_managers in interaction.user.roles
            ):
                with open("database.json", "r") as f:
                    data = json.load(f)

                if author_id in data.keys():
                    data[author_id] += 1

                    with open("database.json", "w") as f:
                        json.dump(data, f, indent=2)

                elif author_id not in data.keys():
                    data[author_id] = 1

                    with open("database.json", "w") as f:
                        json.dump(data, f, indent=2)

                await interaction.response.send_message(
                    "**Task amount updated!** :white_check_mark:"
                )
            else:
                await interaction.response.send_message(
                    "**You do not have permission to run this command!** :x:"
                )

    @app_commands.command(
        name="viewtasks",
        description="Adds +1 to your amount of completed tasks.",
    )
    async def viewtasks(self, interaction: Interaction):
        if not isinstance(interaction.user, Member):
            return
        for guild in self.bot.guilds:
            junior_devs = utils.get(
                guild.roles,
                name="Junior Developers",
            )
            senior_devs = utils.get(
                guild.roles,
                name="Senior Developers",
            )
            lead_devs = utils.get(
                guild.roles,
                name="Lead Developers",
            )
            project_managers = utils.get(
                guild.roles,
                name="Project Managers",
            )

            # Open the database file in read mode
            with open("database.json", "r") as database:
                # Load the contents of the file into a dictionary
                data = json.load(database)

            if (
                junior_devs in interaction.user.roles
                or senior_devs in interaction.user.roles
                or lead_devs in interaction.user.roles
                or project_managers in interaction.user.roles
            ):
                message_text = "".join(
                    f"<@{user_id}>**: {value}**\n"
                    for user_id, value in sorted(
                        data.items(), key=lambda x: x[1], reverse=True
                    )
                )
                # Create the embed
                task_embed = Embed(
                    title="Tasks Completed This Week",
                    description=message_text,
                    color=0x2F3136,
                )

                # Send the embed
                await interaction.response.send_message(embed=task_embed)

            else:
                # The message author does not have one of the roles
                # Don't perform the code actions
                await interaction.response.send_message(
                    "**You do not have permission to run this command!** :x:"
                )


async def setup(bot):
    await bot.add_cog(Tasks(bot))
