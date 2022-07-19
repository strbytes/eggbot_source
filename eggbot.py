import discord, re, random

bench_regex_m = re.compile(r'\W(dad|brother|guy|man|boyfriend)\W') # removed ^.*? from beginning and
bench_regex_f = re.compile(r'\W(mom|sister|girl|woman|girlfriend)\W') # added \Ws at beginning and end
bench_regex_n = re.compile(r'\W(friend|boss|roommate|girlfriends|boyfriends)\W')
word_regex = re.compile(r'\w+')
insult_trigger = re.compile(r'\!insult$')

with open('eggfacts.txt') as f:
    egg_facts = [fact for fact in f.read().strip().split('\n')]
with open('wizards.txt') as f:
    wizards = [wizard for wizard in f.read().split('\n\n')]

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author == client.user:
            return
        if 'egg' in message.content.lower():
            print('Egg reaction!')
            await message.add_reaction('🥚')
        # None of the bench responses have triggered in a while, I think the
        # regexes might be broken
        if bench_regex_m.match(message.content) and random.random() > .75:
            print('Bench response!')
            await message.reply('How much does he bench?')
        if bench_regex_f.match(message.content) and random.random() > .75:
            print('Bench response!')
            await message.reply('How much does she bench?')
        if bench_regex_n.match(message.content) and random.random() > .75:
            print('Bench response!')
            await message.reply('How much do they bench?')
        if message.content == '!facts':
            print('Egg facts!')
            await message.reply(random.choice(egg_facts))
        if message.content == '!wizard':
            print('Wizard!')
            await message.reply('```' + random.choice(wizards) + '```')
        # pick out the longest word from a message on a .01 chance and then say "you're a [word]"
        if random.random() < .005 or insult_trigger.findall(message.content):
            words = word_regex.findall(message.content)
            longest = ''
            for word in words:
                if len(word) > len(longest):
                    longest = word
            print("You're a word!")
            if longest[0].lower() in 'aeiou':
                await message.reply(f"You're an {longest.lower()}!")
            else:
                await message.reply(f"You're a {longest.lower()}!")
        if message.content[:4] == '!kg':
            lb = message.content[5:]
            kg = round(float(lb) / 2.2046226218, 2)
            await message.reply(f'{int(lb)} pounds is equal to {kg} kilograms')
        if message.content[:4] == '!lb':
            kg = message.content[5:]
            lb = round(float(kg) * 2.2046226218, 2)
            await message.reply(f'{kg} kilograms is equal to {lb} pounds')


client = MyClient()
client.run('Token goes here')
