import discord, os, re, random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bench_regex_m = re.compile(
    r"\W(dad|brother|guy|man|boyfriend)\W"
)  # removed ^.*? from beginning and
bench_regex_f = re.compile(
    r"\W(mom|sister|girl|woman|girlfriend)\W"
)  # added \Ws at beginning and end
bench_regex_n = re.compile(r"\W(friend|boss|roommate|girlfriends|boyfriends)\W")
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
        print("Egg reaction!")
        await message.add_reaction("🥚")
    if random.random() < 0.005:
        await insult(message)


async def insult(message):
    words = word_regex.findall(message.content)
    longest = max(words, key=len)
    print("You're a word!")
    if longest[0].lower() in "aeiou":
        await message.reply(f"You're an {longest.lower()}!")
    else:
        await message.reply(f"You're a {longest.lower()}!")


@eggbot.command(aliases={"kg", "kgs"})
def kg(context, lb):
    try:
        kg = round(float(lb) / 2.2046226218, 2)
        await message.reply(f"{lb} pounds is equal to {kg} kilograms")
    except:
        await context.send(f"I'm sorry {context.author}. I can't do that {context.author}.")


@eggbot.command(aliases={"lb", "lbs"})
def lb(context, lb):
    try:
        kg = round(float(lb) / 2.2046226218, 2)
        await message.reply(f"{lb} pounds is equal to {kg} kilograms")
    except:
        await context.send(f"I'm sorry {context.author}. I can't do that {context.author}.")


class MyClient(discord.Client):
    async def on_message(self, message):
        # None of the bench responses have triggered in a while, I think the
        # regexes might be broken
        if bench_regex_m.match(message.content) and random.random() > 0.75:
            print("Bench response!")
            await message.reply("How much does he bench?")
        if bench_regex_f.match(message.content) and random.random() > 0.75:
            print("Bench response!")
            await message.reply("How much does she bench?")
        if bench_regex_n.match(message.content) and random.random() > 0.75:
            print("Bench response!")
            await message.reply("How much do they bench?")

        if message.content == "!facts":
            print("Egg facts!")
            await message.reply(random.choice(egg_facts))
        if message.content == "!wizard":
            print("Wizard!")
            await message.reply("```" + random.choice(wizards) + "```")


# client = MyClient()
eggbot.run(os.environ.get("DISCORD_API_KEY"))
