import math
import discord
from discord.ext import commands


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        """Botの招待リンクを表示します"""
        return await ctx.reply('https://discord.com/api/oauth2/authorize?client_id=883187744984162305&permissions=268528689&scope=bot',
                               allowed_mentions=discord.AllowedMentions.none())

    @commands.command()
    async def ping(self, ctx):
        """Botの応答速度を測ります"""
        await ctx.reply(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms',
                        allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(Bot(bot))
