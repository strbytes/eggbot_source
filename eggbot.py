import os, random, sqlite3, hashlib
from argparse import ArgumentParser
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect("db.sqlite")
cursor = db.cursor()

intents = discord.Intents.default()
intents.message_content = True
eggbot = commands.Bot(command_prefix="!", intents=intents)


with open("eggfacts.txt") as f:
    egg_facts = [fact for fact in f.read().strip().split("\n")]
with open("wizards.txt") as f:
    wizards = [wizard for wizard in f.read().split("\n\n")]


### Event Listeners


@eggbot.event
async def on_ready():
    print(f"{timestamp()} Logged on as {eggbot.user}!")
    if args.sync:
        await eggbot.tree.sync()
        print("Commands synced")
        await eggbot.close()


@eggbot.event
async def on_message(message):
    if message.author == eggbot.user:
        return
    if "egg" in message.content.lower():
        await message.add_reaction("🥚")
        print(f"{timestamp()} Egg reaction!")
    if random.random() < 0.005:
        await do_insult(message)
        print(f"{timestamp()} You're a word!")
    await eggbot.process_commands(message)


### Command definitions


@eggbot.hybrid_command(aliases=["kgs"])
async def kg(ctx: Context, lb: int):
    try:
        kg = round(float(lb) / 2.2046226218, 2)
        await ctx.send(f"{lb} pounds is equal to {kg} kilograms")
    except:
        await ctx.send("Format is `!kg <lbs>`, where lbs is a valid number.")
    print(f"{timestamp()} lb -> kg")


@eggbot.hybrid_command(aliases=["lbs"])
async def lb(ctx: Context, kg: int):
    try:
        lb = round(float(kg) * 2.2046226218, 2)
        await ctx.send(f"{kg} kilograms is equal to {lb} pounds")
    except:
        await ctx.send("Format is `!lb <kgs>`, where kgs is a valid number.")
    print(f"{timestamp()} kg -> lb")


@eggbot.hybrid_command(aliases=["facts"])
async def fact(ctx: Context):
    await ctx.send(random.choice(egg_facts))
    print(f"{timestamp()} Egg facts!")


@eggbot.hybrid_command(aliases=["wizards"])
async def wizard(ctx: Context):
    await ctx.send(f"```Wizard!\n{random.choice(wizards)}```")
    print(f"{timestamp()} Wizard!")


@eggbot.hybrid_command()
async def insult(ctx: Context, user: discord.User):
    if response := ctx.message.reference:
        await do_insult(response.resolved)
        return

    last_message_from_user = [
        message async for message in ctx.channel.history() if message.author == user
    ][0]
    if last_message_from_user:
        await do_insult(last_message_from_user)
    else:
        await ctx.send(
            f"No recent messages from {user} found in this channel", ephemeral=True
        )


@eggbot.hybrid_command()
async def ban(ctx: Context, user: discord.User):
    to_ban = ctx.message.mentions
    if not to_ban:
        to_ban.append(user or ctx.message.author)

    for _user in to_ban:
        # don't save real id, just hash it
        id_hash = hashlib.sha1(str(_user.id).encode())
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
            f"{_user.display_name} has been banned! {_user.display_name} has been banned {bans} time(s)."
        )

    print(f"{timestamp()} Ban!")


### Utility functions


async def do_insult(message):
    words = message.content.split()
    user = message.author
    longest = max(words, key=len)
    if longest[0].lower() in "aeiou":
        await message.reply(f"You're an {longest.lower()}, @{user.display_name}!")
    else:
        await message.reply(f"You're a {longest.lower()}, @{user.display_name}!")
    print(f"{timestamp()} You're a word!")


def timestamp():
    return datetime.strftime(datetime.now(), "%m/%d/%Y %H:%M:%S")


### Execution


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Sync slash commands")
    parser.add_argument(
        "--create-table",
        action="store_true",
        help="Create the db table if it doesn't exist",
    )
    args = parser.parse_args()

    if args.create_table:
        cursor.execute(
            """
    CREATE TABLE IF NOT EXISTS banned (
        id integer PRIMARY KEY,
        bans integer NOT NULL
    );
            """
        )
        exit()

    token = os.environ.get("DISCORD_API_KEY")
    if token:
        eggbot.run(token)
    else:
        print("No API key found!")
