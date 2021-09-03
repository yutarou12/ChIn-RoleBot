from typing import Optional

import discord
from discord.ext import commands


class InviteRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list(self, ctx):
        """サーバーに設定されている自動付与役職を一覧に出します"""
        data = self.db.all_invite_role(ctx.guild.id)
        if not data:
            return await ctx.reply('役職自動付与の招待リンクは設定されていません',
                                   allowed_mentions=discord.AllowedMentions.none())
        else:
            text = []
            for value in data:
                role = ctx.guild.get_role(value[0])
                ch = ctx.guild.get_channel(value[1])
                text.append(f'#{ch.name}: {role.name} | {value[2]}')
            return await ctx.reply('```\n{}\n```'.format('\n'.join(text)),
                                   allowed_mentions=discord.AllowedMentions.none())

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def role(self, ctx):
        """役職の自動付与に関するコマンドです"""
        if ctx.invoked_subcommand is None:
            return

    @role.command(usage='<役職> <招待リンク/コード>')
    @commands.has_permissions(administrator=True)
    async def add(self, ctx, role: Optional[discord.Role], link: discord.Invite = None):
        """既存の招待リンクと付与する役職を紐づけます"""
        if not role or not link:
            return await ctx.reply('役職または招待リンク/コードが指定されていません',
                                   allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.reply(f'招待リンク: `{link.code}` を `{role.name}` に紐づけました。\n'
                            f'この招待リンクを使って参加すると `{role.name}` をユーザーに付与します。\n{link.url}',
                            allowed_mentions=discord.AllowedMentions.none())

            self.db.add_invite_link(ctx.guild.id, ctx.channel.id, role.id, link.code)

    @role.command(usage='<役職> [チャンネル]')
    @commands.has_permissions(administrator=True)
    async def set(self, ctx, role: Optional[discord.Role], ch: discord.TextChannel = None):
        """招待リンクを作成し、付与する役職を設定します。"""
        if not role:
            return await ctx.reply('付与する役職を指定する必要があります',
                                   allowed_mentions=discord.AllowedMentions.none())

        if not ch:
            invite = await ctx.channel.create_invite()
            await ctx.reply('招待リンクを作成しました。\n'
                            f'この招待リンクを使って参加すると {role.name} をユーザーに付与します。\n{invite.url}',
                            allowed_mentions=discord.AllowedMentions.none())

            self.db.add_invite_link(ctx.guild.id, ctx.channel.id, role.id, invite.code)
        else:
            invite = await ch.create_invite()
            await ctx.reply(f'招待リンクを {ch.mention} に作成しました。\n'
                            f'この招待リンクを使って参加すると {role.name} をユーザーに付与します。\n{invite.url}',
                            allowed_mentions=discord.AllowedMentions.none())

            self.db.add_invite_link(ctx.guild.id, ch.id, role.id, invite.code)

    @role.command(usage='<チャンネル>')
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx, ch: discord.TextChannel = None):
        """設定されている役職をリセットします"""
        if not ch:
            return await ctx.reply('設定を削除するチャンネルを指定する必要があります',
                                   allowed_mentions=discord.AllowedMentions.none())

        guild_data = self.db.list_invite_link(ctx.guild.id)

        if ch.id in guild_data:
            self.db.del_invite_link(ctx.guild.id, ch.id)
            await ctx.reply('設定を削除しました',
                            allowed_mentions=discord.AllowedMentions.none())
        else:
            await ctx.reply('このチャンネルは設定されていません',
                            allowed_mentions=discord.AllowedMentions.none())

    @role.command(usage='<役職>')
    @commands.has_permissions(administrator=True)
    async def edit(self, ctx, role: discord.Role = None):
        """付与されている役職を変更します"""
        if not role:
            return await ctx.reply('付与する役職を指定してください',
                                   allowed_mentions=discord.AllowedMentions.none())

        guild_data = self.db.list_invite_link(ctx.guild.id)

        if ctx.channel.id not in guild_data:
            await ctx.reply('このチャンネルには設定されていません',
                            allowed_mentions=discord.AllowedMentions.none())
        else:
            before_role_id = self.db.get_invite_role(ctx.guild.id, ctx.channel.id)
            before_role = ctx.guild.get_role(before_role_id[0])
            if before_role:
                await ctx.reply(f'付与する役職を {before_role.name} から {role.name} に変更しました',
                                allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(InviteRole(bot))
