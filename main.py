import nextcord, json, os
from nextcord.ext import commands

config = json.load(open("config.json", "r"))
check = ["TOKEN", "ADMINS"]
for ele in check:
    if ele not in config: exit(f"[ERROR] Invalid config.json file, missing '{ele}'.")

intents = nextcord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.command()
async def load(ctx, extensions):
    if ctx.author.id in config["ADMINS"]:
        try:
            bot.load_extension(f'cogs.{extensions}')
            await ctx.send(f"Loaded cog {extensions}")
        except Exception as e: await ctx.send("An error occured while trying that. Check your DMs for more info."); await ctx.author.send(e)

@bot.command()
async def unload(ctx, extensions):
    if ctx.author.id in config["ADMINS"]:
        try:
            bot.unload_extension(f'cogs.{extensions}')
            await ctx.send(f"Unloaded cog {extensions}")
        except Exception as e: await ctx.send("An error occured while trying that. Check your DMs for more info."); await ctx.author.send(e)

@bot.command()
async def reload(ctx, extensions):
    if ctx.author.id in config["ADMINS"]:
        try:
            bot.unload_extension(f'cogs.{extensions}')
            bot.load_extension(f'cogs.{extensions}')
            await ctx.send(f"Reloaded cog {extensions}")
        except Exception as e: await ctx.send("An error occured while trying that. Check your DMs for more info."); await ctx.author.send(e)

if __name__ == "__main__":
    print("--------------------")
    for file in os.listdir("cogs"):
        if (
            file.endswith(".py")
            and not file.startswith("_")
            and not file.startswith("classes")
        ):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(config["TOKEN"])