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

        print(list(dict(data.items() - g_data.items()).items()))

        code, count = list(dict(data.items() - g_data.items()).items())[0]
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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            # CommandNotFound
            if isinstance(error, commands.CommandNotFound):
                return

            # CommandMissingPermission
            elif isinstance(error, commands.MissingPermissions):
                try:
                    return await ctx.reply('このコマンドを実行する権限がありません', allowed_mentions=AllowedMentions.none())
                except Exception:
                    raise error

            # NotOwner
            elif isinstance(error, commands.NotOwner):
                return await ctx.reply("このコマンドは開発者専用コマンドです", allowed_mentions=AllowedMentions.none())

            # BotMissingPermissions
            elif isinstance(error, commands.BotMissingPermissions):
                return await ctx.reply('BOTの権限を確認して下さい', allowed_mentions=AllowedMentions.none())

            elif isinstance(error, commands.RoleNotFound):
                return await ctx.reply('役職が見つかりませんでした', allowed_mentions=AllowedMentions.none())
            elif isinstance(error, commands.ChannelNotFound):
                return await ctx.reply('チャンネルが見つかりませんでした', allowed_mentions=AllowedMentions.none())
            elif isinstance(error, commands.BadInviteArgument):
                return await ctx.reply('招待リンクが無効か、有効期限が切れています。', allowed_mentions=AllowedMentions.none())
            elif isinstance(error, commands.BadUnionArgument):
                return
            else:
                raise error
        except Exception:
            owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
            orig_error = getattr(error, "original", error)
            error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
            error_log_msg = Embed(description=f'```py\n{error_msg}\n```')
            error_log_msg.set_footer(text=f'サーバー: {ctx.guild.name} | 送信者: {ctx.author}')
            await owner.send(embed=error_log_msg)


def setup(bot):
    bot.add_cog(Core(bot))
