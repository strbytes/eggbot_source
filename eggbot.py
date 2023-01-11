import discord, os, re, random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

word_regex = re.compile(r"\w+")
insult_trigger = re.compile(r"\!insult$")

with open("eggfacts.txt") as f:
    egg_facts = [fact for fact in f.read().strip().split("\n")]
with open("wizards.txt") as f:
    wizards = [wizard for wizard in f.read().split("\n\n")]

eggbot = commands.Bot(command_prefix="!")


@eggbot.event
async def on_ready():
    print(f"Logged on as {eggbot.user}!")


@eggbot.event
async def on_message(message):
    if message.author == eggbot.user:
        return
    if "egg" in message.content.lower():
        await message.add_reaction("🥚")
        print("Egg reaction!")
    if random.random() < 0.005:
        await insult(message)
        print("You're a word!")
    await eggbot.process_commands(message)


async def insult(message):
    words = word_regex.findall(message.content)
    longest = max(words, key=len)
    if longest[0].lower() in "aeiou":
        await message.reply(f"You're an {longest.lower()}!")
    else:
        await message.reply(f"You're a {longest.lower()}!")


@eggbot.command(aliases=["kgs"])
async def kg(ctx, lb):
    try:
        kg = round(float(lb) / 2.2046226218, 2)
        await ctx.send(f"{lb} pounds is equal to {kg} kilograms")
    except:
        await ctx.send(f"I'm sorry {ctx.author}. I can't do that {ctx.author}.")
    print("lb -> kg")


@eggbot.command(aliases=["lbs"])
async def lb(ctx, kg):
    try:
        lb = round(float(kg) * 2.2046226218, 2)
        await ctx.send(f"{kg} kilograms is equal to {lb} pounds")
    except:
        await ctx.send(f"I'm sorry {ctx.author}. I can't do that {ctx.author}.")
    print("kg -> lb")


@eggbot.command(aliases=["facts"])
async def fact(ctx):
    await ctx.send(random.choice(egg_facts))
    print("Egg facts!")


@eggbot.command(aliases=["wizards"])
async def wizard(ctx):
    await ctx.send(f"```{random.choice(wizards)}```")
    print("Wizard!")


# client = MyClient()
eggbot.run(os.environ.get("DISCORD_API_KEY"))
