from discord.ext import commands


class Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def ping(self, ctx):
    #     await ctx.send('pong')

    # @commands.command()
    # async def what(self, ctx, what: int):
    #     await ctx.send(f'{what}???')

    # async def exit(self):
    #     await exit()

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if(message.author.bot):
    #         return

    #     if(message):
    #         await message.channel.send(message)

    #         print(message)


def setup(bot):
    bot.add_cog(Cog(bot))
