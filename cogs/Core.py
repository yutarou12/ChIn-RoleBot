import json
import traceback

from discord import AllowedMentions, Embed, Forbidden
from discord.ext import commands


class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    async def push_link_json(self, guild) -> None:
        data = {}
        for invite in (await guild.invites()):
            data[f'{invite.code}'] = f'{invite.uses}'
        file = open(f'./data/{guild.id}.json', 'w')
        json.dump(data, file, indent=4)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.push_link_json(invite.guild)

    @commands.Cog.listener()
    async def on_invite_remove(self, invite):
        await self.push_link_json(invite.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild_data = self.db.list_invite_link(member.guild.id)
        if not guild_data:
            return

        data = {}
        for invite in (await member.guild.invites()):
            data[f'{invite.code}'] = f'{invite.uses}'

        with open(f'./data/{member.guild.id}.json', 'r', encoding='UTF-8') as config:
            g_data = json.load(config)

        code = list(dict(data.items() - g_data.items()).items())[0]
        link_role = self.db.fetch_invite_role(member.guild.id, code)

        if not link_role:
            return

        role = member.guild.get_role(link_role[0])
        if role:
            try:
                await member.add_roles(role)
            except Forbidden:
                return
        await self.push_link_json(member.guild)


async def setup(bot):
    await bot.add_cog(Core(bot))
