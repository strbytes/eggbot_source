import os, random, sqlite3, hashlib
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

db = sqlite3.connect("db.sqlite")
cursor = db.cursor()

intents = discord.Intents.default()
intents.message_content = True
eggbot = commands.Bot(command_prefix="!", intents=intents)


def timestamp():
    return datetime.strftime(datetime.now(), "%m/%d/%Y %H:%M:%S")


with open("eggfacts.txt") as f:
    egg_facts = [fact for fact in f.read().strip().split("\n")]
with open("wizards.txt") as f:
    wizards = [wizard for wizard in f.read().split("\n\n")]


@eggbot.event
async def on_ready():
    print(f"{timestamp()} Logged on as {eggbot.user}!")


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


async def do_insult(message):
    words = message.content.split()
    user = message.author
    longest = max(words, key=len)
    if longest[0].lower() in "aeiou":
        await message.reply(f"You're an {longest.lower()}, @{user.display_name}!")
    else:
        await message.reply(f"You're a {longest.lower()}, @{user.display_name}!")
    print(f"{timestamp()} You're a word!")


@eggbot.command()
@commands.is_owner()
async def sync(ctx):
    await eggbot.tree.sync()
    print(f"{timestamp()} Slash commands synced")


@eggbot.tree.command(name="kg", description="Convert pounds to kilograms")
async def lb_to_kg(interaction: discord.interactions.Interaction, lb: int):
    # try:
    kg = round(float(lb) / 2.2046226218, 2)
    await interaction.response.send_message(f"{lb} pounds is equal to {kg} kilograms")
    # except:
    #     await interaction.response.send_message(
    #         "Format is `!kg <lbs>`, where lbs is a valid number."
    #     )
    print(f"{timestamp()} lb -> kg")


@eggbot.tree.command(name="lb", description="Convert kilograms to pounds")
async def kg_to_lb(interaction: discord.interactions.Interaction, kg: int):
    # try:
    lb = round(float(kg) * 2.2046226218, 2)
    await interaction.response.send_message(f"{kg} kilograms is equal to {lb} pounds")
    # except:
    #     await interaction.response.send_message(
    #         "Format is `!lb <kgs>`, where kgs is a valid number."
    #     )
    print(f"{timestamp()} kg -> lb")


# @eggbot.tree.command(name="fact", description="Provide one (1) Egg Fact")
# async def fact(interaction: discord.interactions.Interaction):
#     # TODO - fuzzy find a fact based on a string?
#     await interaction.response.send_message(random.choice(egg_facts))
#     print(f"{timestamp()} Egg facts!")


@eggbot.command()
async def fact(ctx):
    # TODO - fuzzy find a fact based on a string?
    await ctx.send(random.choice(egg_facts))
    print(f"{timestamp()} Egg facts!")


@eggbot.command()
async def insult(ctx):
    if response := ctx.message.reference:
        await do_insult(response.resolved)


# @eggbot.tree.command(name="wizard", description="Provides one (1) Wizard")
# async def wizard(interaction: discord.interactions.Interaction):
#     await interaction.response.send_message(f"```Wizard!\n{random.choice(wizards)}```")
#     print(f"{timestamp()} Wizard!")


@eggbot.command()
async def wizard(ctx):
    await ctx.send(f"```Wizard!\n{random.choice(wizards)}```")
    print(f"{timestamp()} Wizard!")


@eggbot.command()
async def ban(ctx, *args):
    to_ban = ctx.message.mentions
    if not to_ban:
        to_ban.append(ctx.message.author)

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
            f"{user.display_name} has been banned! {user.display_name} has been banned {bans} time(s)."
        )

    print(f"{timestamp()} Ban!")


if __name__ == "__main__":
    #     cursor.execute(
    #         """
    # CREATE TABLE IF NOT EXISTS banned (
    #     id integer PRIMARY KEY,
    #     bans integer NOT NULL
    # );
    #         """
    #     )

    token = os.environ.get("DISCORD_API_KEY")
    if not token:
        raise Exception("No API token found!")
    eggbot.run(token)
