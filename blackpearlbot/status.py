import logging
from datetime import datetime

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

    @app_commands.command(
        name="uptime",
        description="Get the bot uptime",
    )
    async def uptime(self, interaction: Interaction):
        delta_uptime = datetime.utcnow() - self.bot.launch_time  # type: ignore
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        response = f"{days}d, {hours}h, {minutes}m, {seconds}s"
        await interaction.response.send_message(
            f"**Uptime:** {response}",
        )

    @app_commands.command(
        name="sync",
        description="Sync the commands",
    )
    async def sync(self, interaction: Interaction):
        synced = await self.bot.tree.sync()
        await interaction.response.send_message(
            f"Synced {len(synced)} command(s)",
        )


async def setup(bot):
    await bot.add_cog(Status(bot))
