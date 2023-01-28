import logging

from discord import Interaction, app_commands
from discord.ext import commands


logger = logging.getLogger(__name__)


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # doing something when the cog gets loaded
    async def cog_load(self):
        logger.info(f"{self.__class__.__name__} loaded!")

    # doing something when the cog gets unloaded
    async def cog_unload(self):
        logger.info(f"{self.__class__.__name__} unloaded!")

    @app_commands.command(
        name="ping",
        description="Get the bot latency",
    )
    async def ping(self, interaction: Interaction):
        await interaction.response.send_message(
            f"**Latency:** {round(self.bot.latency, 3)} ms",
        )


async def setup(bot):
    await bot.add_cog(Status(bot))
