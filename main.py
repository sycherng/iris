from discord.ext.commands import Bot
import discord
import asyncio
import secrets
import weather

bot = Bot(command_prefix = secrets.command_prefix)

@bot.event
async def on_ready():
    print('Connected.')
 
@bot.event
async def on_message(message):
    # ignores messages from bot itself
    if message.author.id != secrets.bot_id:
        await weather.respond(bot, message)

if __name__ == '__main__':
    bot.run(secrets.bot_token)
