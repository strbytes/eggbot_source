import os, re, random, sqlite3, hashlib
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect("db.sqlite")
cursor = db.cursor()

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
        await ctx.send("Format is `!kg <lbs>`, where lbs is a valid number.")
    print("lb -> kg")


@eggbot.command(aliases=["lbs"])
async def lb(ctx, kg):
    try:
        lb = round(float(kg) * 2.2046226218, 2)
        await ctx.send(f"{kg} kilograms is equal to {lb} pounds")
    except:
        await ctx.send("Format is `!lb <kgs>`, where kgs is a valid number.")
    print("kg -> lb")


@eggbot.command(aliases=["facts"])
async def fact(ctx):
    await ctx.send(random.choice(egg_facts))
    print("Egg facts!")


@eggbot.command(aliases=["wizards"])
async def wizard(ctx):
    await ctx.send(f"```{random.choice(wizards)}```")
    print("Wizard!")


@eggbot.command()
async def ban(ctx, *args):
    to_ban = ctx.message.mentions

    for user in to_ban:
        # don't save real id, just hash it
        id_hash = hashlib.sha1(str(user.id).encode())
        # python's default hash called to produce a shorter number
        id = hash(id_hash.hexdigest())

        cursor.execute("SELECT bans FROM banned WHERE id = ?", [str(id)])
        bans = ban_data[0] + 1 if (ban_data := cursor.fetchone()) else 1
        cursor.execute(
            """INSERT OR REPLACE INTO banned (id, bans) VALUES (?, ?);""",
            [str(id), str(bans)],
        )

        db.commit()
        await ctx.send(
            f"{user.nick} has been banned! {user.nick} has been banned {bans} time(s)."
        )

    print("Ban!")


if __name__ == "__main__":
    cursor.execute(
        """
CREATE TABLE IF NOT EXISTS banned (
    id integer PRIMARY KEY,
    bans integer NOT NULL
);
        """
    )

    eggbot.run(os.environ.get("DISCORD_API_KEY"))
