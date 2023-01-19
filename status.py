from discord import Interaction, app_commands
from discord.ext import commands


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        print(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="ping",
        description="Get the bot latency",
    )
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(
            f"**Latency:** {self.bot.latency} Milliseconds",
        )


async def setup(bot):
    await bot.add_cog(Status(bot))
