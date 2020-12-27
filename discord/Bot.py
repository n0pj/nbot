from discord.ext import commands
import traceback

extensions = [
    # 'cogs.cog',
    'cogs.GoogleCalendar'
]


class Bot(commands.Bot):

    def __init__(self, command_prefix='/'):
        super().__init__(command_prefix)

        for cog in extensions:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('-----')
        print(self.user.name)
        print(self.user.id)
        print('-----')
