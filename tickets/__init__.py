from .cog import Tickets
from .database import SESSION


async def setup(bot):
    await SESSION.create_all()
    await bot.add_cog(Tickets(bot))
