import discord
import os
import requests
import random
from replit import db
from discord.ext import commands
from password_gen import generate_password
from keep_up import keep_up
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import voice  # Import the voice module

# Key words and sentence list for your bot's responses
key_words = ["dude", "serious", "bruh", "crodie"]

sentence_list = [
    "I'm not a bot, I'm a human.",
    "Bruh, your anger makes me want to recommend therapy...or an exorcist", 
    "I walk in this bitch like 2015 Adele", 
]

# Discord bot intents and client initialization
intents = discord.Intents.default()
intents.message_content = True  # Ensure the bot can receive message events

client = commands.Bot(command_prefix='$', intents=intents)
scheduler = AsyncIOScheduler()

# Function to get a random quote
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = response.json()
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

# Function to update sentence list in the database
def update_sentence_list(sentence):
    if "sentence_list" in db.keys():
        sentence_list = db["sentence_list"]
        sentence_list.append(sentence)
        db["sentence_list"] = sentence_list
    else:
        db["sentence_list"] = [sentence]

# Function to delete a sentence from the database
def delete_sentence(index):
    if "sentence_list" in db.keys():
        sentence_list = db["sentence_list"]
        if len(sentence_list) > index:
            del sentence_list[index]
            db["sentence_list"] = sentence_list

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    scheduler.start()

# Command to add a new sentence
@client.command(name='new')
async def new_sentence(ctx, *, sentence):
    update_sentence_list(sentence)
    await ctx.send("New sentence added.")

# Command to delete a sentence
@client.command(name='del')
async def del_sentence(ctx, index: int):
    delete_sentence(index)
    sentence_list = db["sentence_list"]
    await ctx.send(sentence_list)

# Command to send a quote
@client.command(name='quote')
async def send_quote(ctx):
    quote = get_quote()
    await ctx.send(quote)

# Interactive password generation
@client.command(name='password')
async def send_password(ctx, length: int = 12):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send('Include uppercase letters? (yes/no)')
    try:
        use_upper = (await client.wait_for('message', check=check, timeout=30)).content.lower() == 'yes'
    except TimeoutError:
        await ctx.send('You took too long to respond. Please try again.')
        return

    await ctx.send('Include lowercase letters? (yes/no)')
    try:
        use_lower = (await client.wait_for('message', check=check, timeout=30)).content.lower() == 'yes'
    except TimeoutError:
        await ctx.send('You took too long to respond. Please try again.')
        return

    await ctx.send('Include numbers? (yes/no)')
    try:
        use_numbers = (await client.wait_for('message', check=check, timeout=30)).content.lower() == 'yes'
    except TimeoutError:
        await ctx.send('You took too long to respond. Please try again.')
        return

    await ctx.send('Include symbols? (yes/no)')
    try:
        use_symbols = (await client.wait_for('message', check=check, timeout=30)).content.lower() == 'yes'
    except TimeoutError:
        await ctx.send('You took too long to respond. Please try again.')
        return

    try:
        password = generate_password(length, use_upper, use_lower, use_numbers, use_symbols)
        await ctx.author.send(f'Your generated password is: {password}')
        await ctx.send('Password has been sent to your private messages.')
    except ValueError as e:
        await ctx.send(str(e))

# Event triggered on receiving a message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if any(word in msg for word in key_words):
        await message.channel.send(random.choice(sentence_list))

    await client.process_commands(message)

# Scheduled job to send a quote at 12 PM every day
async def scheduled_quote():
    channel = client.get_channel()  # Replace with your channel ID
    if channel:
        quote = get_quote()
        await channel.send(quote)
    else:
        print("Channel not found!")

# Schedule the job
scheduler.add_job(scheduled_quote, 'cron', hour=12, minute=0)

# Ensure PASSKEY is set
token = os.getenv('PASSKEY')
if token is None:
    raise ValueError("No PASSKEY environment variable set")

# Register voice commands
voice.setup(client)

keep_up()
client.run(token)
