import discord 
from discord.ext import commands 
import re

ID_MATCHER = re.compile("<@!?([0-9]+)>")

class DiscordUser(commands.UserConverter):
  async def convert(self, ctx, argument):
    user = None
    match = ID_MATCHER.match(argument)
    if match is not None:
      argument = match.group(1)
    try:
      user = await commands.UserConverter().convert(ctx, argument)
    except:
      user = await ctx.bot.fetch_user(argument)
      if not user:
        user = None
    if user is None:
        return await ctx.send(f"{ctx.bot.x} I could not find that user.")
