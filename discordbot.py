import json
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from libs import Database
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'), permissions=discord.Permissions(1342565620))
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]


intents = discord.Intents.all()
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
bot = commands.Bot(
    command_prefix=config['prefix'],
    intents=intents
)

bot.db = Database.Database()


@tasks.loop(minutes=5)
async def pre_loop():
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=discord.Game(name=f'{config["prefix"]}help | {len(bot.guilds)} Servers')
    )


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    if not pre_loop.is_running():
        pre_loop.start()


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
    other_extension = ['jishaku']
    for o_extension in other_extension:
        try:
            bot.load_extension(o_extension)
        except commands.ExtensionAlreadyLoaded:
            bot.reload_extension(o_extension)
    for extension in extensions_list:
        try:
            bot.load_extension(f'cogs.{extension}')
        except commands.ExtensionAlreadyLoaded:
            bot.reload_extension(f'cogs.{extension}')

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
