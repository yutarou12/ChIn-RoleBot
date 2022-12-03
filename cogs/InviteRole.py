from typing import Optional

import discord
from discord import app_commands
from discord.app_commands import Choice, Group
from discord.ext import commands


class InviteRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db

    @app_commands.guild_only()
    class MyGroup(app_commands.Group):
        pass

    role_group = MyGroup(name='role', description='役職の自動付与に関するコマンドです')

    @app_commands.command(name='list')
    @app_commands.checks.has_permissions(administrator=True)
    async def list(self, interaction: discord.Interaction):
        """サーバーに設定されている自動付与役職を一覧に出します"""
        data = self.db.all_invite_role(interaction.guild.id)
        if not data:
            return await interaction.response.send_message('役職自動付与の招待リンクは設定されていません', ephemeral=True)
        else:
            text = []
            for value in data:
                role = interaction.guild.get_role(value[0])
                ch = interaction.guild.get_channel(value[1])
                text.append(f'#{ch.name if ch else "None"}: {role.name if role else "None"} | {value[2]}')
            return await interaction.response.send_message('```\n{}\n```'.format('\n'.join(text)), ephemeral=True)

    @role_group.command(name='add')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.rename(role='ロール', link='招待リンク')
    async def role_add(self, interaction, role: discord.Role, link: str):
        """既存の招待リンクと付与するロールを紐づけます

        Parameters
        -----------
        :param role: 招待リンクに紐づけるロール
        :param link: 紐づける招待リンク/コード
        """

        if not role or not link:
            return await interaction.response.send_message('役職または招待リンク/コードが指定されていません',
                                                           ephemeral=True)

        invite = discord.utils.resolve_invite(link)

        guild_invite = await interaction.guild.invites()

        if invite.code not in [i.code for i in guild_invite]:
            return await interaction.response.send_message('招待リンク/コードが見つかりませんでした',
                                                           ephemeral=True)

        def search_invite() -> discord.Invite:
            for i in guild_invite:
                if i.code == invite.code:
                    return i

        guild_data = self.db.list_invite_link(interaction.guild.id)
        if search_invite().channel.id in guild_data:
            return await interaction.response.send_message('既にこの招待リンクのチャンネルは設定されています', ephemeral=True)

        await interaction.response.send_message(f'招待リンク: `https://discord.gg/{invite.code}` を `{role.name}` に紐づけました。\n'
                                                f'この招待リンクを使って参加すると `{role.name}` をユーザーに付与します。'
                                                f'\nhttps://discord.gg/{invite.code}',
                                                ephemeral=True)
        self.db.add_invite_link(interaction.guild.id, search_invite().channel.id, role.id, invite.code)

    @role_group.command(name='set')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.rename(role='ロール', ch='チャンネル')
    async def role_set(self, interaction, role: discord.Role, ch: Optional[discord.abc.GuildChannel]):
        """招待リンクを作成し、付与するロールを設定します。

        Parameters
        -----------
        :param role: 招待リンクに紐づけるロール
        :param ch: 招待リンクを作成するチャンネル
        """
        channel = ch if ch else interaction.channel

        if not role:
            return await interaction.response.send_message('付与する役職を指定してください', ephemeral=True)

        guild_data = self.db.list_invite_link(interaction.guild.id)
        if channel.id in guild_data:
            return await interaction.response.send_message('既にこのチャンネルには設定されています', ephemeral=True)

        invite = await channel.create_invite()
        await interaction.response.send_message(f'招待リンクを {channel.mention} に作成しました。\n'
                                                f'この招待リンクを使って参加すると {role.name} をユーザーに付与します。\n{invite.url}',
                                                ephemeral=True)

        self.db.add_invite_link(interaction.guild.id, channel.id, role.id, invite.code)

    @role_group.command(name='remove')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.rename(ch='チャンネル')
    async def role_remove(self, interaction, ch: discord.abc.GuildChannel):
        """設定されているロールをリセットします。

        Parameters
        -----------
        :param ch: 設定を削除するチャンネル
        """

        if not ch:
            return await interaction.response.send_message('設定を削除するチャンネルを指定してください。', ephemeral=True)

        guild_data = self.db.list_invite_link(interaction.guild.id)

        if ch.id in guild_data:
            self.db.del_invite_link(interaction.guild.id, ch.id)
            return await interaction.response.send_message('設定を削除しました', ephemeral=True)
        else:
            return await interaction.response.send_message(f'{ch.mention} では設定されていません', ephemeral=True)

    @role_group.command(name='edit')
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.rename(role='ロール', ch='チャンネル')
    async def role_edit(self, interaction, role: discord.Role, ch: Optional[discord.abc.GuildChannel]):
        """付与される役職を変更します。

        Parameters
        -----------
        :param role: 変更先のロール
        :param ch: 設定を削除するチャンネル
        """

        if not role:
            return await interaction.response.send_message('付与される役職を指定してください', ephemeral=True)

        guild_data = self.db.list_invite_link(interaction.guild.id)
        channel = ch if ch else interaction.channel

        if channel.id in guild_data:
            before_role_id = self.db.get_invite_role(interaction.guild.id, channel.id)
            before_role = interaction.guild.get_role(before_role_id[0])
            if before_role:
                return await interaction.response.send_message(f'付与する役職を {before_role.name} から {role.name} に変更しました',
                                                               ephemeral=True)
        else:
            return await interaction.response.send_message(f'{channel.mention} では設定されていません', ephemeral=True)


async def setup(bot):
    await bot.add_cog(InviteRole(bot))
