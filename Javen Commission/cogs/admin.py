import contextlib
import inspect
import logging
import pprint
import re
import textwrap
import traceback
from io import StringIO
import os 
import psutil
import time 
import sys, threading
from datetime import datetime, timedelta

import discord
from discord.ext import commands 

cogs = [
    "cogs.admin",
    "cogs.requests",
]

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.env = {}
        self.ln = 0
        self.stdout = StringIO()


    @commands.command()
    @commands.is_owner()
    async def threads(self, ctx):
        def get_t(thread):
            frame = sys._current_frames().get(thread.ident, None)
            if frame:
                return frame.f_code.co_filename, frame.f_code.co_name, frame.f_code.co_firstlineno
        threads = ""
        for thread in threading.enumerate():
            threads += f"**{get_t(thread)}**\n\n"
        embed = discord.Embed(color=0x4196f7)
        embed.title = f"Threads"
        embed.description = threads
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send(F"{self.bot.check} Restarting now! This may take 10+ seconds..")
        await self.bot.change_presence(status=discord.Status.dnd)
        os.execv(sys.executable, ['python3.6'] + sys.argv)

    @commands.command(aliases=['r'])
    @commands.is_owner()
    async def reload(self, ctx):
        cogs_list = ""
        for cog in cogs:
            try:
                self.bot.reload_extension(cog)
                cogs_list += f"{self.bot.check} **{cog}**\n"
            except Exception as e:
                exc = ''.join(traceback.format_exception(type(e), e, e.__traceback__, chain=False))
                cogs_list += f"{self.bot.x} **{cog}** ```py\n{exc}```\n"
        await ctx.send(cogs_list)

    @commands.command()
    async def say(self, ctx, channel: discord.TextChannel = None, *, msg = None):
        if not channel:
            channel = ctx.channel
        await channel.send(msg)

    def _format(self, inp, out):  # (str, Any) -> (str, discord.Embed)
        self._ = out

        res = ""

        # Erase temp input we made
        if inp.startswith("_ = "):
            inp = inp[4:]

        # Get all non-empty lines
        lines = [line for line in inp.split("\n") if line.strip()]
        if len(lines) != 1:
            lines += [""]

        # Create the input dialog
        for i, line in enumerate(lines):
            if i == 0:
                # Start dialog
                start = f"In [{self.ln}]: "

            else:
                # Indent the 3 dots correctly;
                # Normally, it's something like
                # In [X]:
                #    ...:
                #
                # But if it's
                # In [XX]:
                #    ...:
                #
                # You can see it doesn't look right.
                # This code simply indents the dots
                # far enough to align them.
                # we first `str()` the line number
                # then we get the length
                # and use `str.rjust()`
                # to indent it.
                start = "...: ".rjust(len(str(self.ln)) + 7)

            if i == len(lines) - 2:
                if line.startswith("return"):
                    line = line[6:].strip()

            # Combine everything
            res += (start + line + "\n")

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = StringIO()

        if text:
            res += (text + "\n")

        if out is None:
            # No output, return the input statement
            return (res, None)

        res += f"Out[{self.ln}]: "

        if isinstance(out, discord.Embed):
            # We made an embed? Send that as embed
            res += "<Embed>"
            res = (res, out)

        else:
            if (isinstance(out, str) and out.startswith("Traceback (most recent call last):\n")):
                # Leave out the traceback message
                out = "\n" + "\n".join(out.split("\n")[1:])

            if isinstance(out, str):
                pretty = out
            else:
                pretty = pprint.pformat(out, compact=True, width=60)

            if pretty != str(out):
                # We're using the pretty version, start on the next line
                res += "\n"

            if pretty.count("\n") > 20:
                # Text too long, shorten
                li = pretty.split("\n")

                pretty = ("\n".join(li[:3])  # First 3 lines
                          + "\n ...\n"  # Ellipsis to indicate removed lines
                          + "\n".join(li[-3:]))  # last 3 lines

            # Add the output
            res += pretty
            res = (res, None)

        return res  # Return (text, embed)

    async def _eval(self, ctx, code):  # (discord.Context, str) -> None

        self.ln += 1

        if code.startswith("exit"):
            self.ln = 0
            self.env = {}
            return await ctx.send("```Reset history!```")

        env = {
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "server": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "inspect": inspect,
            "discord": discord,
            "contextlib": contextlib,
            "datetime": datetime, 
            "timedelta": timedelta
        }

        self.env.update(env)

        # Ignore this code, it works
        _code = """
async def func():  # (None,) -> Any
    try:
        with contextlib.redirect_stdout(self.stdout):
{0}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update(locals())
""".format(textwrap.indent(code, '            '))

        try:
            exec(_code, self.env)  # noqa: B102,S102
            func = self.env['func']
            res = await func()

        except Exception:
            res = traceback.format_exc()

        out, embed = self._format(code, res) # pylint: disable=unused-variable
        await ctx.send(f"```py\n{out}```")

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        """ Run eval in a REPL-like format. """
        code = code.strip("`")
        if re.match('py(thon)?\n', code):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(  # Check if it's an expression
                r"^(return|import|for|while|def|class|"
                r"from|exit|[a-zA-Z0-9]+\s*=)", code, re.M) and len(
                    code.split("\n")) == 1:
            code = "_ = " + code

        await self._eval(ctx, code)

    @commands.command(
        name="ping",
        brief="Pong!"
    )
    async def ping(self, ctx):
        """
Pong!
        """
        server = ctx.guild
        t1 = time.perf_counter()
        message = await ctx.send(":ping_pong:")
        t2 = time.perf_counter()
        rest = round((t2 - t1) * 1000)
        latency = round(self.bot.latency * 1000, 2)
        t3 = time.perf_counter() 
        await self.bot.db.settings.find_one({"guild_id": server.id})
        t4 = time.perf_counter() 
        database_latency = round((t4 - t3) * 1000)
        await message.edit(content=f"Pong! :ping_pong:\n**Response Latency:** {rest}ms\n**Websock Latency:** {latency}ms\n**Database Latency:** {database_latency}ms")

def setup(bot):
    bot.add_cog(Owner(bot))