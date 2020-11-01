import discord 
from discord.ext import commands 
# import motor.motor_asyncio as _motor 
import traceback 
import os 
import sys  

# pylint: disable=anomalous-backslash-in-string
print("""
   _____                _        _ _____           _   
  / ____|              | |      | |  __ \         | |  
 | |     _ __ _   _ ___| |_ __ _| | |__) |   _ ___| |_ 
 | |    | '__| | | / __| __/ _` | |  _  / | | / __| __|
 | |____| |  | |_| \__ \ || (_| | | | \ \ |_| \__ \ |_ 
  \_____|_|   \__, |___/\__\__,_|_|_|  \_\__,_|___/\__|
               __/ |                                   
              |___/                                                          
""")

# try:
#     client = _motor.AsyncIOMotorClient("mongodb+srv://ModmailBot:Alterra12345@cluster0-ivikc.mongodb.net/test?retryWrites=true&w=majority") 
#     print("The Modmail database has been loaded.") 
# except Exception as e:
#     print(f"I have failed to load the main database, here is the error:\n{e}") 

# async def get_prefix(bot, message):
#     if not message.guild:
#         return 
#     server = message.guild 
#     # get the settings collection and this returns a dict
#     settings = await bot.db.settings.find_one({"guild_id": server.id}) 
#     mail_logs = await bot.db.mail_logs.find_one({"guild_id": server.id})

#     # set the prefixes to where you can mention the bot 
#     base = ["<@botid>", "<@!botid>"]

#     if not settings:
#         inserted_data = {
#             "guild_id": server.id,
#             "prefix": "!",
#             "support-channel": None,
#             "logs-channel": None
#         }
#         await bot.db.settings.insert_one(inserted_data)
#         base.append("!")
#     elif not mail_logs:
#         inserted_data = {
#             "guild_id": server.id,
#             "logs": []
#         }
#         await bot.db.mail_logs.insert_one(inserted_data)
#         base.append("!")
#     else:
#         base.append(settings['prefix']) 
#     return base 

extensions = ["cogs.admin", "cogs.requests"] 

class JavenBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(">>>"), case_insensitive=True) 

        self.x = ":x:"
        self.check = ":white_check_mark:"

        self.embed = 0xdb4637

        for extension in extensions:
            try:
                self.load_extension(extension)
                print(f"Loaded {extension} successfully.")
            except:
                print(f"Failed to load extension {extension}.", file=sys.stderr)
                traceback.print_exc() 

    async def on_ready(self):
        print("CrystalRust Reports is now online.") 

bot = JavenBot() 
bot.load_extension('jishaku')

bot.run("NzA3MDc3ODg1NDQ1NDA2NzUw.Xsv-OA.7PCE4gdDNEEDgvQ1A60LMbRddWE")