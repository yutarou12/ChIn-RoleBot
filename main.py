import json
import os
import discord
from discord import app_commands, Interaction
from discord.app_commands import AppCommandError
from discord.ext import commands, tasks
from dotenv import load_dotenv
from libs import Database
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'), permissions=discord.Permissions(1342565620))
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]
MY_GUILD = discord.Object(id=int(os.getenv('OFFICIAL_GUILD')))


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        OWNER = bot.application.owner

        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original
        elif isinstance(error, app_commands.MissingPermissions):
            return
        elif isinstance(error, discord.Forbidden):
            return await interaction.response.send_message('Botの権限を確認してください。', ephemeral=True)
        elif isinstance(error, commands.BadUnionArgument):
            return
        elif isinstance(error, discord.errors.NotFound):
            return

        tracebacks = getattr(error, 'traceback', error)
        tracebacks = ''.join(traceback.TracebackException.from_exception(tracebacks).format())
        tracebacks = discord.utils.escape_markdown(tracebacks)
        embed_traceback = discord.Embed(description=f'```{tracebacks}```')
        if interaction.guild:
            embed_traceback.set_footer(text=f'{interaction.channel.name} \nG:{interaction.guild_id} C:{interaction.channel_id}',
                                       icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        else:
            embed_traceback.set_footer(text=f"{interaction.user}'s DM_CHANNEL C:{interaction.channel_id}")
        await OWNER.send(embed=embed_traceback)

        embed_error = discord.Embed(title='エラーが発生しました。', color=0xff0000)
        msg = 'エラーが発生しました。\n コマンドが正しく入力されているにも関わらずエラーが出る際には、公式サーバーまでお問い合わせください。' \
              '\n  [公式サーバー](https://discord.gg/k5Feum44gE)\n'
        embed_error.add_field(name='メッセージ', value=msg, inline=False)
        try:
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
        except discord.Forbidden:
            pass

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)

        try:
            await bot.load_extension('jishaku')
        except discord.ext.commands.ExtensionAlreadyLoaded:
            await bot.reload_extension('jishaku')
        for ext in extensions_list:
            try:
                await bot.load_extension(f'cogs.{ext}')
            except discord.ext.commands.ExtensionAlreadyLoaded:
                await bot.reload_extension(f'cogs.{ext}')

    async def get_context(self, message, *args, **kwargs):
        return await super().get_context(message, *args, **kwargs)


intents = discord.Intents.all()
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
bot = MyBot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    allowed_mentions=discord.AllowedMentions(replied_user=False, everyone=False),
    intents=intents,
    help_command=None
)


@tasks.loop(minutes=5)
async def pre_loop():
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=discord.Game(name=f'/help {len(bot.guilds)} Servers')
    )


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    if not pre_loop.is_running():
        pre_loop.start()

    await bot.tree.sync()


@bot.listen('on_ready')
async def push_guild_invite():
    for guild in bot.guilds:
        data = {}
        for invite in (await guild.invites()):
            data[f'{invite.code}'] = f'{invite.uses}'
        file = open(f'./data/{guild.id}.json', 'w')
        json.dump(data, file, indent=4)


if __name__ == '__main__':
    bot.config = config
    bot.db = Database.Database()

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
