import discord 
from discord.ext.commands import command, Cog, group, has_guild_permissions 
from datetime import datetime, timedelta
import asyncio

class Requests(Cog):
    def __init__(self,bot):
        self.bot = bot 

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            not message.guild 
            or message.author.bot 
        ):
            return 
        
        server = message.guild 
        channel = message.channel 
        author = message.author

        if channel.id != 714946897470685244:
            return
        
        logs_channel = server.get_channel(714947202375483471)
        await message.delete()

        def check(m):
            return m.author == self.bot.user

        reletave_messages = await logs_channel.history().filter(check).flatten()
        embeded_messages = [msg for msg in reletave_messages if len(msg.embeds) >= 1]

        for msg in embeded_messages:
            if str(author.id) in msg.embeds[0].description and msg.embeds[0].author.name == "Pending Report":
                try:
                    await author.send(f"You already have an open ticket. Please send an admin all relevant information.")
                except:
                    await channel.send(f"{author.mention}, you already have an open ticket. Please send an admin all relevant information.", delete_after=10)
                return
        embed = discord.Embed(color=0xffcf4a, timestamp=datetime.utcnow())
        embed.set_author(name="Pending Report", icon_url=author.avatar_url)
        embed.description = f"""
A new report was submitted by {author.mention} with an ID of {author.id}.
        """
        embed.add_field(name="Report Content", value=message.content)
        logged_report = await logs_channel.send(content=f"{server.get_role(697169208349294594).mention} {server.get_role(704088287832309780).mention}", embed=embed)
        await logged_report.add_reaction("✅")
        await logged_report.add_reaction("⛔")

        try:
            await author.send(f"Thank you for submitting a support request, you will receive a notification once one of our admins processes your ticket.")
        except:
            return

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        server = self.bot.get_guild(payload.guild_id)
        channel = server.get_channel(payload.channel_id)

        if channel.id != 714947202375483471:
            return 
        
        message = await channel.fetch_message(payload.message_id)

        admin = payload.member

        if len(message.embeds) == 0 or admin == self.bot.user:
            return 

        embed = message.embeds[0]

        moderator_role = server.get_role(704088287832309780)

        if embed.author.name == "Accepted Report" or embed.author.name == "Denied Report":
            return
        
        if payload.emoji.name == "✅":
            if moderator_role in admin.roles:
                return
            splitted, user_id = embed.description.split("ID of") #pylint: disable=unused-variable
            user_id = user_id.replace(".", "")
            user = server.get_member(int(user_id))

            try:
                await user.send(f"""
Your support request was accepted by {admin.mention} (ID: {admin.id}) and it is currently being looked into. If you have further information that needs to be shared feel free to message this Admin and provide any additional info.
                """)
            except:
                await admin.send(f":no_entry: I could not send {user.mention} (ID: {user.id}) an accepted message.")
                pass 

            embed.description += f"\nThis report has been accepted by {admin.mention}!"

            new_embed = discord.Embed(color=0x4affa8, timestamp=datetime.utcnow())
            new_embed.set_author(name="Accepted Report", icon_url=user.avatar_url)
            new_embed.description = embed.description
            new_embed.add_field(name="Report Content", value=embed.fields[0].value)
            await message.edit(embed=new_embed)
        elif payload.emoji.name == "⛔":
            splitted, user_id = embed.description.split("ID of") #pylint: disable=unused-variable
            user_id = user_id.replace(".", "")
            user = server.get_member(int(user_id))

            try:
                await user.send("Your support request was denied! You failed to provide information we requested, please refer to the premade template. You can always open up a new support request.")
            except:
                await admin.send(f":no_entry: I could not send {user.mention} (ID: {user.id}) a denial message.")

            embed.description += f"\nThis report has been denied by {admin.mention}!"
            new_embed = discord.Embed(color=self.bot.embed, timestamp=datetime.utcnow())
            new_embed.set_author(name="Denied Report", icon_url=user.avatar_url)
            new_embed.description = embed.description 
            new_embed.add_field(name="Report Content", value=embed.fields[0].value)
            await message.edit(embed=new_embed)

def setup(bot):
    bot.add_cog(Requests(bot))