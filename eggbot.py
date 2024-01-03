import os, random, sqlite3, hashlib
from argparse import ArgumentParser
from contextlib import closing, contextmanager
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
eggbot = commands.Bot(command_prefix="!", intents=intents)


with open("eggfacts.txt") as file:
    egg_facts = [fact for fact in file.read().strip().split("\n")]
with open("wizards.txt") as file:
    wizards = [wizard for wizard in file.read().split("\n\n")]


@contextmanager
def use_db():
    with closing(sqlite3.connect("db.sqlite")) as db:
        with closing(db.cursor()) as cursor:
            yield cursor
        db.commit()


### Event Listeners


@eggbot.event
async def on_ready():
    print(f"{timestamp()} Logged on as {eggbot.user}!")
    if args.sync:
        await eggbot.tree.sync()
        print("Commands synced")
        await eggbot.close()


@eggbot.event
async def on_message(message: discord.Message):
    if message.author == eggbot.user:
        return
    if "egg" in message.content.lower():
        await message.add_reaction("🥚")
        print(f"{timestamp()} Egg reaction!")
    if random.random() < 0.005:
        insult = await make_insult(message)
        await message.reply(insult)
        print(f"{timestamp()} Random insult!")
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


@eggbot.hybrid_command()
async def c(ctx: Context, f: int):
    try:
        c = round((float(f) - 32) / (9 / 5), 2)
        await ctx.send(f"{f} degrees fahrenheit is equal to {c} degrees celsius")
    except:
        await ctx.send(
            "Format is `!c <degrees fahrenheit>`, where degrees fahrenheit is a valid number."
        )
    print(f"{timestamp()} f -> c")


@eggbot.hybrid_command()
async def f(ctx: Context, c: int):
    try:
        f = round(float(c) * (9 / 5) + 32, 2)
        await ctx.send(f"{c} degrees celsius is equal to {f} degrees fahrenheit")
    except:
        await ctx.send(
            "Format is `!f <degrees celsius>`, where <degrees celsius> is a valid number."
        )
    print(f"{timestamp()} c -> f")


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
    # If this command is called as a response to a message, use that message as the input
    if reference := ctx.message.reference:
        if isinstance(reference.resolved, discord.Message):
            insult = await make_insult(reference.resolved)
            await ctx.send(insult, reference=reference)
        else:
            await ctx.send("Command failed: invalid message reference", ephemeral=True)
    # Otherwise, get the last message from the user in the argument
    elif user:
        last_message_from_user = [
            message async for message in ctx.channel.history() if message.author == user
        ][0]
        if last_message_from_user:
            insult = await make_insult(last_message_from_user)
            await ctx.send(insult, reference=last_message_from_user)
        else:
            await ctx.send(
                f"No recent messages from {user} found in this channel", ephemeral=True
            )
    print(f"{timestamp()} Deliberate insult!")


@eggbot.hybrid_command()
async def ban(ctx: Context, user: discord.User):
    with use_db() as cursor:
        # don't save real id, just hash it
        id_hash = hashlib.sha1(str(user.id).encode()).hexdigest()
        # concatenate the output
        id = str(int(id_hash, 16))[:10]

        cursor.execute("SELECT bans FROM banned WHERE id = ?;", [str(id)])
        bans = ban_data[0] + 1 if (ban_data := cursor.fetchone()) else 1
        cursor.execute(
            """INSERT OR REPLACE INTO banned (id, bans) VALUES (?, ?);""",
            [str(id), str(bans)],
        )

        await ctx.send(
            f"{user.display_name} has been banned! {user.display_name} has been banned {bans} time(s)."
        )

    print(f"{timestamp()} Ban!")


### Utility functions


async def make_insult(message: discord.Message):
    words = message.content.split()
    user = message.author
    longest = max(words, key=len)
    if longest[0].lower() in "aeiou":
        return f"You're an {longest.lower()} {user.mention}!"
    else:
        return f"You're a {longest.lower()} {user.mention}!"


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
        with use_db() as cursor:
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
