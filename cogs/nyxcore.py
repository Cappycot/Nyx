import asyncio

from discord import Game, Status
from discord.ext import commands
from discord.ext.commands.view import StringView

import nyx.nyxcommands as nyxcommands
from nyx.nyxutils import respond

green = ["g", "green", "online"]
yellow = ["idle", "y", "yellow"]
red = ["busy", "r", "red"]
gray = ["gray", "grey", "off", "offline"]


class Core:
    def __init__(self, nyx):
        self.nyx = nyx

    @commands.command(name="privilege", aliases=["rank"], pass_context=True)
    async def check_privilege(self, ctx):
        """Displays your privilege rank."""
        if await self.nyx.is_owner(ctx.message.author):
            privilege = "Owner"
        else:
            privilege = str(
                self.nyx.get_user_data(ctx.message.author).get_privilege())
        if ctx.message.guild is None:
            await ctx.send("Privilege: " + privilege)
        else:
            await ctx.send("".join(
                [ctx.message.author.mention, ", your privilege level is ",
                 privilege, "."]))

    @commands.command()
    @commands.is_owner()
    async def exec(self, ctx, code):
        """Remote executes code."""
        py_start = code.lower().startswith("```py")
        python_start = py_start and code.lower().startswith("```python")
        view = StringView(ctx.message.content)
        view.skip_string(ctx.prefix)
        view.skip_ws()
        view.skip_string(ctx.invoked_with)
        view.skip_ws()
        code = view.read_rest()
        if python_start:
            code = code[9:]
        elif py_start:
            code = code[5:]
        elif code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        output = await self.nyx.loadstring(code, ctx)
        if not output:
            output = "empty"
        output = "```" + output + "```"
        await respond(ctx, output)

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def echo(self, ctx, *words):
        """I copy what you say."""
        stuff = " ".join(words)
        if not stuff:
            await ctx.send("What?")
            return
        if ctx.guild is not None and ctx.message.channel.permissions_for(
                ctx.message.guild.get_member(
                    self.nyx.user.id)).manage_messages:
            await ctx.message.delete()
        print(stuff)
        await ctx.send(stuff)

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def shutdown(self, ctx):
        """Dun kill me pls..."""
        await ctx.send("Light cannot be without dark!!!")
        await asyncio.sleep(1)
        await self.nyx.logout()

    @commands.command()
    @nyxcommands.has_privilege(privilege=-1)
    async def status(self, ctx, color, *words):
        if any(color == a for a in green):
            color = Status.online
        elif any(color == a for a in yellow):
            color = Status.idle
        elif any(color == a for a in red):
            color = Status.dnd
        elif any(color == a for a in gray):
            color = Status.offline
        else:
            color = None
        if len(words) > 0:
            mention = ctx.bot.user.mention
            if ctx.guild is not None:
                mention = ctx.guild.get_member(ctx.bot.user.id).mention
            words = " ".join(words).replace(mention, "@" + ctx.bot.user.name)
            activity = Game(name=words)
            words = '"{}"'.format(words)
        else:
            activity = None
            words = "nothing"
        await self.nyx.change_presence(game=activity, status=color)
        await respond(ctx, 'I changed my status to {}...'.format(words))

def setup(nyx):
    nyx.add_cog(Core(nyx))