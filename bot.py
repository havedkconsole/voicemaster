import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

#DISCORD_TOKEN=
#GUILD_ID=
#TRIGGER_CHANNEL_ID=
#TEMP_CATEGORY_ID=

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
TRIGGER_CHANNEL_ID = int(os.getenv("TRIGGER_CHANNEL_ID"))
TEMP_CATEGORY_ID = int(os.getenv("TEMP_CATEGORY_ID"))

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == TRIGGER_CHANNEL_ID:
        guild = member.guild
        category = guild.get_channel(TEMP_CATEGORY_ID)

        # создаём канал
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            member: discord.PermissionOverwrite(manage_channels=True, connect=True, move_members=True),
        }

        temp_channel = await guild.create_voice_channel(
            name=f"{member.name}'s Room",
            overwrites=overwrites,
            category=category
        )

        # перемещаем юзера
        await member.move_to(temp_channel)

        print(f"Создан канал: {temp_channel.name} для {member.name}")

        # опционально: удаляем канал, когда пустой
        def check_empty_channel(*_):
            if len(temp_channel.members) == 0:
                asyncio.create_task(temp_channel.delete())
                print(f"Канал {temp_channel.name} удалён")

        bot.loop.create_task(wait_for_empty(temp_channel, check_empty_channel))

import asyncio
async def wait_for_empty(channel, callback, check_interval=10):
    while True:
        await asyncio.sleep(check_interval)
        if len(channel.members) == 0:
            await callback()
            break

bot.run(TOKEN)
