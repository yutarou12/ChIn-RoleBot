import math
import discord
from discord import app_commands
from discord.ext import commands


class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='invite')
    async def invite(self, interaction):
        """Botの招待リンクを表示します"""
        return await interaction.response.send_message(
            'https://discord.com/api/oauth2/authorize?client_id=883187744984162305&permissions=268435457&scope=applications.commands%20bot',
            ephemeral=True)

    @app_commands.command(name='ping')
    async def ping(self, interaction):
        """Botの応答速度を測ります"""
        return await interaction.response.send_message(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms',
                                                       ephemeral=True)

    @app_commands.command(name='help')
    async def _help(self, interaction):
        """Botのヘルプを表示します"""
        embed = discord.Embed()
        embed.add_field(name='/role add', value='既存の招待リンクと付与するロールを紐づけます', inline=False)
        embed.add_field(name='/role edit', value='付与されるロールを変更します', inline=False)
        embed.add_field(name='/role remove', value='設定されているロールをリセットします', inline=False)
        embed.add_field(name='/role set', value='招待リンクを作成し、付与するロールを設定します', inline=False)
        embed.add_field(name='/list', value='サーバーに設定されている自動付与役職を一覧に出します', inline=False)

        return await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Bot(bot))
