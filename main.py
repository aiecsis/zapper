import discord
from discord.ext import commands, tasks
from discord.ext.commands import MissingPermissions
from discord import app_commands, message, user, InteractionResponse, InteractionResponseType, channel, embeds
import sys
import json
from colorama import Fore
import typing
import asyncio
import random
import datetime
import requests
from itertools import cycle
import io
import string
import time
import os

'''
                    ____________________VARIABLES____________________
'''

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
openaikey = config['OPEN_AI_KEY']
token = config['token']
ownerid = int(config['owner'])
colorcode = int(config['color'])
DiscordCommandError = config['DiscordCommandError']

openai.api_key = openaikey

class ConditionalCommandTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        command = interaction.command
        ticket_commands = ["ticket_create", "ticket_close", "ticket_add", "ticket_remove", "ticket_disable"]
        if command and command.name in ticket_commands:
            guild_id = str(interaction.guild.id)
            if guild_id not in ticket_settings or "support_role_id" not in ticket_settings[guild_id]:
                await interaction.response.send_message("The ticket system is not enabled. Please ask an administrator to enable it.", ephemeral=True)
                return False
        return True
# 
def is_support_role():
    async def predicate(interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in ticket_settings:
            await interaction.response.send_message("Ticket system is not enabled for this server.", ephemeral=True)
            return False
        support_role_id = ticket_settings[guild_id].get("support_role_id")
        if not support_role_id:
            await interaction.response.send_message("Support role is not set up properly.", ephemeral=True)
            return False
        support_role = interaction.guild.get_role(support_role_id)
        if not support_role:
            await interaction.response.send_message("Support role not found. Please ask an administrator to enable the ticket system again.", ephemeral=True)
            return False
        return support_role in interaction.user.roles
    return app_commands.check(predicate)

# Define Load or Create files.
def load_or_create_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
        return {}

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Load or create JSON files.
ticket_counts = load_or_create_json('ticket_counts.json')
ticket_logs = load_or_create_json('ticket_logs.json')
ticket_settings = load_or_create_json('ticket_settings.json')
autowelcome = load_or_create_json('autowelcome.json')
autoroles = load_or_create_json('autoroles.json')

# Define "BOT".
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), case_insensitive=False, help_command=None, tree_cls=ConditionalCommandTree)

# Create a cycling status for the bot.
bot_status = cycle(
    ["/help", "/invite"])

# Define is_owner for owner only commands.
def is_owner():
    def predicate(interaction: discord.Interaction):
        if interaction.user.id == ownerid:
            return True
    return app_commands.check(predicate)

'''
                    ____________________BOT START UP____________________
'''
# Loop task for tthe cycling status.
@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(activity=discord.Game(f'{len(bot.guilds)} servers | {next(bot_status)}'))

# Bot startup
@bot.event
async def on_ready():
    change_status.start()
    try:
        s = await bot.tree.sync()
        print(f'Synced {len(s)} commands')
    except Exception as e:
        print(f'Error syncing commands: {e}')
    print('')
    print(f"{Fore.BLUE}- - - - - - {bot.user.name} is ready! - - - - - -")
    print('')
    user_id = "832268459006099467"
    user = await bot.fetch_user(user_id)
    embed = discord.Embed(description=f'''
    **Bot is online and ready to use!**
    ''', color=colorcode)
    await user.send(embed=embed)

'''
                    ____________________ HELP COMMAND ____________________
'''

@bot.tree.command(name='help', description="Show all the commands.")
async def help(interaction: discord.Interaction):
    pages = [
        {
            "title": "Zapper - Main Commands",
            "fields": [
                {"name": "/help", "value": "Show all commands", "inline": False},
                {"name": "/invite", "value": "Invite Zapper to your server", "inline": False},
                {"name": "/commandcount", "value": "Show the command count", "inline": False},
                {"name": "/suggest", "value": "Suggestions or comments for the bot", "inline": False},
                {"name": "/settings", "value": "Check the current server settings", "inline": False}
            ]
        },
        {
            "title": "Zapper - Information Commands",
            "fields": [
                {"name": "/avatar", "value": "Show your avatar", "inline": False},
                {"name": "/userinfo", "value": "Show your userinfo", "inline": False},
                {"name": "/serverinfo", "value": "Show your serverinfo", "inline": False},
                {"name": "/membercount", "value": "Show member count for the server", "inline": False},
            ]
        },
        {
            "title": "Zapper - Utility Commands",
            "fields": [
				{"name": "--- AUTO MESSAGES / ROLES ---", "value": "", "inline": False},
                {"name": "/welcome enable", "value": "Enable and set channel for welcome messages", "inline": False},
                {"name": "/welcome disable", "value": "Disable welcome messages", "inline": False},
                {"name": "/autorole enable", "value": "Enable and set auto role for new members", "inline": False},
                {"name": "/autorole disable", "value": "Disable the set auto role", "inline": False},
		        {"name": "--- TICKET SYSTEM ---", "value": "", "inline": False},
		        {"name": "/tickets enable", "value": "Enable Ticket System", "inline": False},
                {"name": "/ticket disable", "value": "Disable Ticket System", "inline": False},
                {"name": "/ticket create", "value": "Create a support ticket", "inline": False},
                {"name": "/ticket close", "value": "Close the current ticket", "inline": False},
                {"name": "/ticket add", "value": "Add a user to the current ticket", "inline": False},
                {"name": "/ticket remove", "value": "Remove a user from the current ticket", "inline": False},
            ]
        },
        {
            "title": "Zapper - Moderation Commands",
            "fields": [
                {"name": "/ban", "value": "Ban a member", "inline": False},
                {"name": "/unban", "value": "Unban a member", "inline": False},
                {"name": "/kick", "value": "Kick a member", "inline": False},
                {"name": "/mute", "value": "Mute a member", "inline": False},
                {"name": "/unmute", "value": "Unmute a member", "inline": False},
                {"name": "/purge", "value": "Purge a certain amount of messages", "inline": False},
                {"name": "/slowmode", "value": "Set a slowmode for a channel", "inline": False},
                {"name": "/slowmodeoff", "value": "Turn off slowmode for a channel", "inline": False},
            ]
        },
        {
            "title": "Zapper - Role and Channel Management",
            "fields": [
                {"name": "/createrole", "value": "Create a role with the entered name", "inline": False},
                {"name": "/deleterole", "value": "Delete a role with the entered name", "inline": False},
                {"name": "/addrole", "value": "Add a role to a member", "inline": False},
                {"name": "/removerole", "value": "Remove a role from a member", "inline": False},
                {"name": "/createchannel", "value": "Create a channel", "inline": False},
                {"name": "/deletechannel", "value": "Delete a channel", "inline": False},
            ]
        },
        {
            "title": "Zapper - Fun Commands",
            "fields": [
                {"name": "/dice", "value": "Roll a dice", "inline": False},
                {"name": "/coinflip", "value": "Flip a coin", "inline": False},
                {"name": "/roast", "value": "Roast someone", "inline": False},
                {"name": "/meme", "value": "Show a random meme", "inline": False},
                {"name": "/joke", "value": "Show a random joke", "inline": False},
                {"name": "/wanted", "value": "Make a 'Wanted' image of a member", "inline": False},
                {"name": "/trivia", "value": "Start a trivia question", "inline": False},
                {"name": "/hug", "value": "Hug a member", "inline": False},
                {"name": "/kiss", "value": "Kiss a member", "inline": False},
                {"name": "/kill", "value": "Kill a member", "inline": False},
                {"name": "/slap", "value": "Slap a member", "inline": False},
            ]
        },
        {
            "title": "Zapper - Interactive Commands",
            "fields": [
                {"name": "/ask", "value": "Ask Zapper any type of question", "inline": False},
                {"name": "/youtube", "value": "Search for a video on YouTube", "inline": False},
                {"name": "/poll", "value": "Make a poll with reactions", "inline": False},
                {"name": "/embed", "value": "Send an embedded text", "inline": False},
                {"name": "/choose", "value": "Send a choices embed with reactions", "inline": False},
            ]
        },
        {
            "title": "Zapper - Owner Commands",
            "fields": [
                {"name": "/sync", "value": "Sync the bot's commands to discord", "inline": False},
                {"name": "/restart", "value": "Restart the bot", "inline": False},
                {"name": "/ping", "value": "Shows the bot's ping", "inline": False},
                {"name": "/servers", "value": "Shows the servers the bot is in", "inline": False},
            ]
        }
    ]
    embeds = []
    for i, page in enumerate(pages):
        embed = discord.Embed(title=page["title"], color=colorcode)
        for field in page["fields"]:
            embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        embed.set_footer(text=f"Page {i+1}/{len(pages)}")
        embeds.append(embed)

    message = await interaction.response.send_message(embed=embeds[0])
    messagex = await interaction.original_response()
    await messagex.add_reaction('⏮')
    await messagex.add_reaction('◀')
    await messagex.add_reaction('▶')
    await messagex.add_reaction('⏭')

    def check(reaction, user):
        return user == interaction.user

    i = 0
    reaction = None

    while True:
        if str(reaction) == '⏮':
            i = 0
            await messagex.edit(embed=embeds[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await messagex.edit(embed=embeds[i])
        elif str(reaction) == '▶':
            if i < len(embeds) - 1:
                i += 1
                await messagex.edit(embed=embeds[i])
        elif str(reaction) == '⏭':
            i = len(embeds) - 1
            await messagex.edit(embed=embeds[i])

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            await messagex.remove_reaction(reaction, user)
        except:
            break

    await messagex.clear_reactions()

'''
                    ____________________ RESTART COMMAND ____________________
'''

@bot.tree.command(name="restart", description="Owner - Restart the bot.")
@is_owner()
async def restart(interaction: discord.Interaction):
    embed = discord.Embed(title="Successfully Restarded! :white_check_mark: ",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)
    os.system("clear")
    os.execv(sys.executable, ['python'] + sys.argv)


@restart.error
async def restart_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)    
    
'''
                    ____________________ SYNC COMMAND ____________________
'''

@bot.tree.command(name='sync', description='Owner -  Sync Commands.')
@is_owner()
async def sync(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    await bot.tree.sync()
    embed2 = discord.Embed(title='Commands Synced',
                           description='The bot has synced commands.',
                           color=colorcode)
    await interaction.edit_original_response(embed=embed2)


@sync.error
async def sync_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ AVATAR COMMAND ____________________
'''

@bot.tree.command(name="avatar", description="Shows your avatar.")
@app_commands.describe(user="The member to show the membed avatar.")
@app_commands.rename(user='user')
async def avatar(interaction: discord.Interaction,
                 user: discord.Member = None):
    if user is None:
        user = interaction.user
    embed = discord.Embed(title=f"{user.name}'s avatar", 
                          color=colorcode)
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)
    
'''
                    ____________________ USERINFO COMMAND ____________________
'''

@bot.tree.command(name="userinfo", description="Shows your userinfo.")
@app_commands.describe(user="The member to show the membed info.")
@app_commands.rename(user='user')
async def userinfo(interaction: discord.Interaction,
                   user: discord.Member = None):
    if user is None:
        user = interaction.user
    embed = discord.Embed(title=f"{user.name}'s userinfo", color=colorcode)
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="User ID", value=user.id, inline=True)
    embed.add_field(name="Joined Server",
                    value=user.joined_at.strftime("**%d/%m/%Y**"))
    embed.add_field(name="Joined Discord",
                    value=user.created_at.strftime("**%d/%m/%Y**"))
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

'''
                    ____________________ SERVER INFO COMMAND ____________________
'''

@bot.tree.command(name="serverinfo", description="Get information about the server.")
async def serverinfo(interaction: discord.Interaction):
    server = interaction.guild

    roles = " ".join([role.mention for role in server.roles if role.name != "@everyone"])
    emojis = " ".join([str(emoji) for emoji in server.emojis])
    channels = str(len(server.channels))

    rolecount = str(len(server.roles))
    emojicount = str(len(server.emojis))
    
    embeded = discord.Embed(description=f'''### {server.name}'s Server Info''',
                            color=colorcode)
    if server.icon:
        embeded.set_thumbnail(url=server.icon.url)
   
    embeded.add_field(
        name="Created on:",
        value=server.created_at.strftime('%d %B %Y at %H:%M UTC+3'),
        inline=True)
    embeded.add_field(name="Server ID:", value=server.id, inline=False)
    embeded.add_field(name="Server Owner:",
                      value=server.owner.mention if server.owner else "Not available",
                      inline=True)
    embeded.add_field(name="Member Count:",
                      value=server.member_count,
                      inline=True)
    embeded.add_field(name=f"Roles: {rolecount}", value=roles if roles else "No roles", inline=False)
    embeded.add_field(name=f"Emojis: {emojicount}", value=emojis if emojis else "No custom emojis", inline=False)
    embeded.add_field(name="Channel Count:", value=channels, inline=True)

    await interaction.response.send_message(embed=embeded)

'''
                    ____________________ MEMBERCOUNT COMMAND ____________________
'''

@bot.tree.command(name="membercount", description="Show the member count for the server.")
async def membercount(interaction: discord.Interaction):
    if interaction.guild:
        membercount = sum(not member.bot
                          for member in interaction.guild.members)
        botcount = sum(member.bot for member in interaction.guild.members)
        embed = discord.Embed(
            title=f"Member & Bot Count for {interaction.guild.name}",
            description=f'''
        There are currently `{membercount}` member/s in the server!

        There are `{botcount}` bot/s in the server.
        ''',
            color=colorcode)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
            "This command can only be used in a server.")

'''
                    ____________________ POLL COMMAND ____________________
'''

@bot.tree.command(name="poll", description="Make a poll with reactions.")
@app_commands.describe(question="Type a question for people to vote on:")
@app_commands.rename(question='question')
async def poll(interaction: discord.Interaction, 
               question: str):
    embed = discord.Embed(title=question, 
                          color=colorcode)
    embed.set_footer(text=f"Poll by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')

'''
                    ____________________ EMBED COMMAND ____________________
'''

@bot.tree.command(name="embed", description="Make an embed text message.")
@app_commands.describe(title="Title for the embed")
@app_commands.rename(title='title')
@app_commands.describe(description="Description for the embed.")
@app_commands.rename(description='description')
async def embed(interaction: discord.Interaction, 
                title: str,
                description: str):
    await interaction.response.send_message('Loading Embeded Message...')
    time.sleep(3)
    msg = await interaction.original_response()
    await msg.delete()
    channel1 = interaction.channel
    embed = discord.Embed(title=title,
                          description=description,
                          color=colorcode)
    await channel1.send(embed=embed)

'''
                    ____________________ CHOOSE COMMAND ____________________
'''

@bot.tree.command(name="choose",
                  description="Choose between multiple choices.")
@app_commands.describe(choice1="Type the first option:")
@app_commands.describe(choice2="Type the second option:")
@app_commands.rename(choice1='choice1')
@app_commands.rename(choice2='choice2')
async def choose(interaction: discord.Interaction, 
                 choice1: str, 
                 choice2: str):
    
    choices = [choice1, choice2]
    chosen_choice = random.choice(choices)
    if chosen_choice == choice1:
        embed = discord.Embed(title=f"I choose **{choice1}!**",
                              color=colorcode)
        await interaction.response.send_message(embed=embed)
    elif chosen_choice == choice2:
        embed = discord.Embed(title=f"I choose **{choice2}!**",
                              color=colorcode)
        await interaction.response.send_message(embed=embed)

'''
                    ____________________ DICE COMMAND ____________________
'''

@bot.tree.command(name="dice", description="Roll a dice.")
async def dice(interaction: discord.Interaction):
    dice_roll = random.randint(1, 6)
    embed = discord.Embed(title=f"You rolled a {dice_roll}!", 
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

'''
                    ____________________ COINFLIP COMMAND ____________________
'''

@bot.tree.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction):
    coin_flip = random.choice(["Heads", "Tails"])
    embed = discord.Embed(title=f"You flipped a {coin_flip}!", 
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

'''
                    ____________________ ROAST COMMAND ____________________
'''

def get_quote():
    url = 'https://evilinsult.com/generate_insult.php?lang=en&type=json'
    response = requests.get(url)
    quote_data = response.json()
    quote = f'{quote_data["insult"]}'
    return quote

@bot.tree.command(name="roast", description="Roast a member.")
@app_commands.describe(member="The member you want to roast.")
@app_commands.rename(member='member')
async def roast(interaction: discord.Interaction, member: discord.Member):
    quote = get_quote()
    embed = discord.Embed(description=f"{member.mention} {quote}",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

        
'''
                    ____________________ MEME COMMAND ____________________
'''

@bot.tree.command(name="meme", description="Get a random meme.")
async def meme(interaction: discord.Interaction):
    url = 'https://meme-api.com/gimme'
    response = requests.get(url)
    meme_data = response.json()
    meme_url = meme_data['url']
    meme_title = meme_data['title']
    embed = discord.Embed(title=f"{meme_title}", color=colorcode)
    embed.set_image(url=meme_url)
    await interaction.response.send_message(embed=embed)



'''
                    ____________________ JOKE COMMAND ____________________
'''

@bot.tree.command(name="joke", description="Get a random joke.")
async def joke(interaction: discord.Interaction):
    url = 'https://v2.jokeapi.dev/joke/Any?type=twopart'
    response = requests.get(url)
    joke_data = response.json()
    setup = joke_data['setup']
    delivery = joke_data['delivery']
    embed = discord.Embed(title=f"{setup}",
                          description=f"{delivery}",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)
        
'''
                    ____________________ WANTED COMMAND ____________________
''' 

@bot.tree.command(name='wanted',description="Make a wanted picture of a user.")
@app_commands.describe(user="Enter user to user for the image.")
@app_commands.rename(user='user')
async def wanted(interaction: discord.Interaction, user:discord.Member):
    if user.id == bot.user.id:
        await interaction.response.send_message("You can't use this command on me.")
        return
    await interaction.response.defer(thinking=True)
    time.sleep(3)
    url = user.avatar.url
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((177,177)).convert('RGBA')
    bg = Image.open(r"wanted.png")
    bg.paste(img,(120,212),img)
    bg.save('picture.png')
    await interaction.followup.send(file = discord.File("picture.png"))
        
'''
                    ____________________ TRIVIA COMMAND ____________________
''' 
    
@bot.tree.command(name="trivia", description="Start a trivia question!")
async def trivia(interaction: discord.Interaction):
    await interaction.response.defer()

    response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
    if response.status_code != 200:
        await interaction.followup.send("Sorry, I couldn't fetch a trivia question at the moment.")
        return

    data = response.json()['results'][0]

    question = html.unescape(data['question'])
    correct_answer = html.unescape(data['correct_answer'])
    incorrect_answers = [html.unescape(answer) for answer in data['incorrect_answers']]

    all_answers = incorrect_answers + [correct_answer]
    random.shuffle(all_answers)

    embed = discord.Embed(title="Trivia Time!", description=question, color=discord.Color.blue())
    for i, answer in enumerate(all_answers):
        embed.add_field(name=f"Option {i+1}", value=answer, inline=False)

    view = TriviaView(interaction.user, correct_answer, all_answers)
    message = await interaction.followup.send(embed=embed, view=view)
    view.message = message

class TriviaView(discord.ui.View):
    def __init__(self, author, correct_answer, all_answers):
        super().__init__(timeout=30)
        self.author = author
        self.correct_answer = correct_answer
        self.all_answers = all_answers
        self.message = None

    @discord.ui.button(label="1", style=discord.ButtonStyle.primary)
    async def button_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 0)

    @discord.ui.button(label="2", style=discord.ButtonStyle.primary)
    async def button_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 1)

    @discord.ui.button(label="3", style=discord.ButtonStyle.primary)
    async def button_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 2)

    @discord.ui.button(label="4", style=discord.ButtonStyle.primary)
    async def button_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.check_answer(interaction, 3)

    def disable_all_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    async def check_answer(self, interaction: discord.Interaction, index: int):
        if interaction.user != self.author:
            await interaction.response.send_message("This isn't your trivia game!", ephemeral=True)
            return

        self.disable_all_buttons()
        await interaction.response.edit_message(view=self)

        user_answer = self.all_answers[index]
        if user_answer == self.correct_answer:
            await interaction.followup.send(f"Correct! The answer is indeed: {self.correct_answer}")
        else:
            await interaction.followup.send(f"Sorry, that's incorrect. The correct answer was: {self.correct_answer}")

        self.stop()

    async def on_timeout(self):
        self.disable_all_buttons()
        if self.message:
            await self.message.edit(view=self)
            await self.message.reply(f"Time's up! The correct answer was: {self.correct_answer}")

'''
                    ____________________ TICKET SYSTEM COMMANDS ____________________
'''

class TicketSystem(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name='ticket', description='Manage ticket system')
        self.bot = bot

    @app_commands.command(name="enable", description="Enable ticket system.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction):
        guild = interaction.guild
        existing_role = discord.utils.get(guild.roles, name="Ticket Support - Zapper")

        if existing_role:
            support_role = existing_role
            await interaction.response.send_message(f"Ticket system is already enabled. Using existing support role: {support_role.mention}", ephemeral=True)
        else:
            support_role = await guild.create_role(name="Ticket Support - Zapper", color=discord.Color.blue())
            await interaction.response.send_message(f"Ticket system has been successfully enabled. Support role created: {support_role.mention}", ephemeral=True)

        guild_id = str(guild.id)
        ticket_settings[guild_id] = {
            "support_role_id": support_role.id
        }
        save_json('ticket_settings.json', ticket_settings)

    @app_commands.command(name="create", description="Create a new support ticket")
    async def create(self, interaction: discord.Interaction, issue: str):
        guild = interaction.guild
        member = interaction.user
        guild_id = str(guild.id)
        if guild_id not in ticket_settings:
            await interaction.response.send_message("Ticket system is not enabled. Please ask an administrator to set it up.", ephemeral=True)
            return
        support_role_id = ticket_settings[guild_id].get("support_role_id")
        if not support_role_id:
            await interaction.response.send_message("Ticket system is not properly configured. Please ask an administrator to enable it again.", ephemeral=True)
            return
        support_role = guild.get_role(support_role_id)
        if not support_role:
            await interaction.response.send_message("Support role not found. Please ask an administrator to enable the ticket system again.", ephemeral=True)
            return
        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")
        if guild_id not in ticket_counts:
            ticket_counts[guild_id] = 0
        ticket_counts[guild_id] += 1
        ticket_number = ticket_counts[guild_id]
        save_json('ticket_counts.json', ticket_counts)
        channel_name = f"ticket-{ticket_number:04d}"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        channel = await category.create_text_channel(channel_name, overwrites=overwrites)
        embed = discord.Embed(description=f'''
## Ticket Information:
*Created:* {member.mention}
*Issued at: * {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
*Issue:* {issue}

**Plase send any details you would like to add, Support will be in touch with you soon!**
''', color=colorcode)
        await channel.send(embed=embed, content=f"{member.mention} {support_role.mention}")
        await interaction.response.send_message(f"Ticket has been created! Please check {channel.mention}", ephemeral=True)

    @app_commands.command(name="add", description="Add a user to the current ticket")
    @app_commands.checks.has_role("Ticket Support - Zapper")
    @app_commands.describe(user="The user to add to the ticket")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        if not isinstance(interaction.channel, discord.TextChannel) or not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)
            return
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"{user.mention} has been added to the ticket.")

    @app_commands.command(name="close", description="Close the current ticket")
    @app_commands.checks.has_role("Ticket Support - Zapper")
    async def close(self, interaction: discord.Interaction):
        if not isinstance(interaction.channel, discord.TextChannel) or not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)
            return
        await interaction.response.send_message("Ticket will be closed in 5 seconds.")
        await asyncio.sleep(5)
        channel_name = interaction.channel.name
        await interaction.channel.delete()
        try:
            await interaction.user.send(f"Ticket {channel_name} has been closed by ticket support administration. If you need to create a new ticket, please use the `/ticket create` command.")
        except discord.errors.Forbidden:
            pass

    @app_commands.command(name="remove", description="Remove a user from the current ticket")
    @app_commands.checks.has_role("Ticket Support - Zapper")
    @app_commands.describe(user="The user to remove from the ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith("ticket-"):
            await interaction.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to remove users from tickets.", ephemeral=True)
            return

        if user not in interaction.channel.members:
            await interaction.response.send_message(f"{user.mention} is not in this ticket.", ephemeral=True)
            return

        try:
            await interaction.channel.set_permissions(user, overwrite=None)

            embed = discord.Embed(
                title="User Removed from Ticket",
                description=f"{user.mention} has been removed from the ticket.",
                color=colorcode
            )
            await interaction.response.send_message(embed=embed)

            log_embed = discord.Embed(
                title="User Removed from Ticket",
                description=f"{interaction.user.mention} removed {user.mention} from {interaction.channel.mention}",
                color=colorcode
            )
            log_channel_id = ticket_settings.get(str(interaction.guild.id), {}).get("log_channel_id")
            if log_channel_id:
                log_channel = interaction.guild.get_channel(int(log_channel_id))
                if log_channel:
                    await log_channel.send(embed=log_embed)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove users from this channel.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="disable", description="Disable ticket system.")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        guild_id = str(interaction.guild.id)

        try:
            with open('ticket_settings.json', 'r') as f:
                ticket_settings = json.load(f)

            if guild_id in ticket_settings:
                del ticket_settings[guild_id]

                with open('ticket_settings.json', 'w') as f:
                    json.dump(ticket_settings, f, indent=4)

                category = discord.utils.get(interaction.guild.categories, name="Tickets")
                if category:
                    for channel in category.channels:
                        await channel.delete()
                    await category.delete()

                support_role = discord.utils.get(interaction.guild.roles, name="Ticket Support - Zapper")
                if support_role:
                    await support_role.delete()

                embed = discord.Embed(
                    title="Ticket System Removed",
                    description="The ticket system has been successfully removed from this server.",
                    color=colorcode
                )
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Ticket System Not Found",
                    description="There is no ticket system enabled for this server.",
                    color=colorcode
                )
                await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f'[ERROR] {e}')
            embed = discord.Embed(
                title="Error",
                description="An error occurred while trying to remove the ticket system.",
                color=colorcode
            )
            await interaction.followup.send(embed=embed)

    @enable.error
    @create.error
    @add.error
    @close.error
    @remove.error
    @disable.error
    async def ticket_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
        elif isinstance(error, app_commands.errors.MissingRole):
            await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        elif isinstance(error, app_commands.errors.MemberNotFound):
            await interaction.response.send_message("The specified user was not found.", ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)
bot.tree.add_command(TicketSystem(bot))

'''
                    ____________________ REACTION COMMANDS ____________________
'''

'''---- HUGS -----'''
@bot.tree.command(name='hug',description="Hug a user.")
@app_commands.describe(user="The member you want to hug.")
@app_commands.rename(user='user')
async def hug(interaction: discord.Interaction, user:discord.User):
    embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"{interaction.user.mention} huged {user.mention} <3"
    )
    embed.set_image(url=(random.choice(hugs)))
    await interaction.response.send_message(embed=embed)

'''---- KILSS -----'''
@bot.tree.command(name='kill',description="Kill a user.")
@app_commands.describe(user="The member you want to kill.")
@app_commands.rename(user='user')
async def kill(interaction: discord.Interaction, user:discord.User):
    embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"{interaction.user.mention} killed {user.mention} <3"
    )
    embed.set_image(url=(random.choice(kills)))
    await interaction.response.send_message(embed=embed)

'''---- KISSES -----'''
@bot.tree.command(name='kiss',description="Kiss a user.")
@app_commands.describe(user="The member you want to kiss.")
@app_commands.rename(user='user')
async def kiss(interaction: discord.Interaction, user:discord.User):
    embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"{interaction.user.mention} kissed {user.mention} <3"
    )
    embed.set_image(url=(random.choice(kisses)))
    await interaction.response.send_message(embed=embed)
    
'''---- SLAPS -----'''
@bot.tree.command(name='slap',description="Slap a user.")
@app_commands.describe(user="The member you want to slap.")
@app_commands.rename(user='user')
async def slap(interaction: discord.Interaction, user:discord.User):

    embed = discord.Embed(
        colour=discord.Colour.blue(),
        description=f"{interaction.user.mention} slapped {user.mention} <3"
    )
    embed.set_image(url=(random.choice(slaps)))
    await interaction.response.send_message(embed=embed)
    
'''
                    ____________________ AI RESPONSE COMMAND ____________________
'''

question_count = 0

last_response = {}

@bot.tree.command(name='ask', description='Ask Zapper ANY question.')
@app_commands.describe(question="What do you want to ask to AI.")
@app_commands.rename(question='question')
async def ask(interaction: discord.Interaction, question:str):
    global question_count
    question_count += 1
 
    #await interaction.response.send_message(f"`Question`:\n{question}")
    await interaction.response.send_message('Please wait while I think...')
    original_response = await interaction.original_response()

    thread = threading.Thread(target=handle_question, args=(interaction, interaction.user.id, question, interaction.channel.id, original_response))
    thread.start()

@bot.tree.command(name='count')
async def count(interaction: discord.Interaction):
    await interaction.response.send_message(f"{question_count}")

def handle_question(interaction, user_id, question, channel_id, original_response):
    global last_response
    try:
        if user_id in last_response:
            if time.time() - last_response[user_id]['timestamp'] < 10:
                response = last_response[user_id]['response']
                send_response(interaction, response, question, channel_id, original_response)
                return
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": question }]
        )

#        time.sleep(10)
        actual_response = response.choices[0].message.content
        last_response[user_id] = {'response': actual_response, 'timestamp': time.time()}
        send_response(interaction, actual_response, question, channel_id, original_response)
    except Exception as e:
        print(f"Error handling question from user {user_id}: {e}")
def send_response(interaction, response, question, channel_id, original_response):
    #bot.loop.create_task(bot.get_channel(channel_id).send(f"`Answer`:\n{response}"))
    bot.loop.create_task(interaction.edit_original_response(content=f'''
`Question`: {question}
`Answer`: {response}
'''))

'''
                    ____________________ YOUTUBE SEARCH COMMAND ____________________
'''

@bot.tree.command(name='youtube', description='Search for a YouTube video.')
@app_commands.describe(search="Query to search for the video.")
@app_commands.rename(search='search')
async def youtube(interaction: discord.Interaction, search:str):
    query_string = urllib.parse.urlencode({'search_query': search})
    html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
    search_content= html_content.read().decode()
    search_results = re.findall(r'\/watch\?v=\w+', search_content)
    #print(search_results)
    await interaction.response.send_message(f'Here is the search result: https://www.youtube.com' + search_results[0])

'''
                    ____________________ ON MEMBER JOIN AND GUILD REMOVE EVENTS  ____________________
'''
 
def create_circular_image(img, size=(150, 150)):
    img = img.resize(size, Image.LANCZOS).convert("RGBA")

    bigsize = (img.size[0] * 3, img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)

    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + bigsize, fill=255)

    mask = mask.resize(img.size, Image.LANCZOS)

    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)

    return output
            
@bot.event
async def on_member_join(member):
    global autowelcome
    try:
        if str(member.guild.id) in autowelcome:
            channel_id = autowelcome[str(member.guild.id)]
            
            img_width, img_height = 800, 300
            img = Image.new('RGB', (img_width, img_height), color = (0, 0, 0))
            d = ImageDraw.Draw(img)
            main_font = ImageFont.truetype("STIXGeneralBolIta.otf", 40)
            sub_font = ImageFont.truetype("STIXGeneralBolIta.otf", 30)

            # Get and process profile image
            profile_image = Image.open(requests.get(member.avatar.url, stream=True).raw)
            profile_image = create_circular_image(profile_image, (150, 150))

            # Prepare the welcome text
            top_text = f"{member.name} just joined the server."
            bottom_text = f"Member #{member.guild.member_count}"

            # Get the size of the main text
            bbox = d.textbbox((0, 0), top_text, font=main_font)
            main_text_width = bbox[2] - bbox[0]
            main_text_height = bbox[3] - bbox[1]

            # Get the size of the sub text
            bbox = d.textbbox((0, 0), bottom_text, font=sub_font)
            sub_text_width = bbox[2] - bbox[0]
            sub_text_height = bbox[3] - bbox[1]

            # Calculate position for main text (center, 50 pixels from bottom)
            main_x = (img_width - main_text_width) / 2
            main_y = img_height - main_text_height - sub_text_height - 60  # 60 pixels from the bottom

            # Calculate position for sub text (center, just below main text)
            sub_x = (img_width - sub_text_width) / 2
            sub_y = main_y + main_text_height + 20  # 10 pixels gap between texts

            # Draw the texts
            d.text((main_x, main_y), top_text, font=main_font, fill=(255,255,225))
            d.text((sub_x, sub_y), bottom_text, font=sub_font, fill=(225,225,225))  # Light grey color

            # Paste the profile image (adjust position as needed)
            profile_size = 150
            x_position = (img_width - profile_size) // 2
            y_position = 25  # 20 pixels from the top
            img.paste(profile_image, (x_position, y_position), profile_image)

            with io.BytesIO() as image_binary:
                img.save(image_binary, 'PNG')
                image_binary.seek(0)

                # Send welcome message with image
                embed = discord.Embed(color=colorcode)
                embed.set_image(url='attachment://welcome.png')
                await bot.get_channel(int(channel_id)).send(f'{member.mention}', embed=embed, file=discord.File(image_binary, 'welcome.png'))

        if str(member.guild.id) in autoroles:
            role_id = autoroles[str(member.guild.id)]
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)
                print(f"Added role {role.name} to {member.name} in {member.guild.name}")
            else:
                print(f"[ERROR] Role with ID {role_id} not found in guild {member.guild.id}")
        else:
            print(f"No auto-role set for guild {member.guild.id}")
    except Exception as e:
        print(f'[ERROR] {e}')

@bot.event
async def on_guild_remove(guild):
    files_to_update = ['autowelcome.json', 'autoroles.json']
    for file in files_to_update:
        try:
            data = load_or_create_json(file)
            guild_id_str = str(guild.id)
            if guild_id_str in data:
                del data[guild_id_str]
                save_json(file, data)
                print(f"Removed guild {guild.id} from {file}")
            else:
                print(f"Guild {guild.id} not found in {file}")
        except Exception as e:
            print(f'[ERROR] Failed to update {file}: {e}')

    for file in files_to_update:
        try:
            data = load_or_create_json(file)
            print(f"Contents of {file} after update: {data}")
        except Exception as e:
            print(f'[ERROR] Failed to read {file}: {e}')

'''
                    ____________________ WElCOME AND AUTO ROLE COMMAND ____________________
'''

class Welcome(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name='welcome', description='Manage welcome message settings.')

    @app_commands.command(name='enable', description='Set channel for welcome messages.')
    @app_commands.describe(channel="Channel to send welcome messages.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(thinking=True)
        with open('autowelcome.json', 'r', encoding='utf-8') as f:
            autowelcome = json.load(f)

        autowelcome[str(interaction.guild.id)] = str(channel.id)
        with open('autowelcome.json', 'w', encoding='utf-8') as f:
            json.dump(autowelcome, f, indent=4, ensure_ascii=False)

        embed = discord.Embed(
            title='Welcome Channel Set!',
            description=f'{channel.mention} has been set for welcome messages',
            color=colorcode)
        await interaction.followup.send(embed=embed)

        embed2 = discord.Embed(
            title='This channel has been set for welcome messages.',
            description='If you would like to change the channel, please use the command again and input the right channel.',
            color=colorcode)
        await channel.send(embed=embed2)

    @app_commands.command(name='disable', description='Disable the welcome message setting for this server.')
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        try:
            with open('autowelcome.json', 'r', encoding='utf-8') as f:
                autowelcome = json.load(f)
            guild_id = str(interaction.guild.id)
            if guild_id in autowelcome:
                del autowelcome[guild_id]
                with open('autowelcome.json', 'w', encoding='utf-8') as f:
                    json.dump(autowelcome, f, indent=4, ensure_ascii=False)
                embed = discord.Embed(title='Welcome message channel has been removed for this server. :white_check_mark:', color=colorcode)
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title='No welcome message channel was set for this server. :x:', color=colorcode)
                await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f'[ERROR] {e}')
            embed = discord.Embed(title='An error occurred while trying to remove the welcome message. :x:', color=colorcode)
            await interaction.followup.send(embed=embed)

class Autorole(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name='autorole', description='Manage auto role settings for new members.')

    @app_commands.command(name='enable', description='Enable and set the auto role for new members.')
    @app_commands.describe(role="Role to be given to new members.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.defer(thinking=True)
        with open('autoroles.json', 'r', encoding='utf-8') as f:
            autoroles = json.load(f)

        autoroles[str(interaction.guild.id)] = str(role.id)
        with open('autoroles.json', 'w', encoding='utf-8') as f:
            json.dump(autoroles, f, indent=4, ensure_ascii=False)

        embed = discord.Embed(
            title='Auto Role Enabled!',
            description=f'{role.mention} has been set as the auto role.\nIf you would like to change the role, please use this command again and input the desired role.',
            color=colorcode)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name='disable', description='Disable the auto-role setting for this server.')
    @app_commands.checks.has_permissions(administrator=True)
    async def disable(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        try:
            with open('autoroles.json', 'r', encoding='utf-8') as f:
                autoroles = json.load(f)

            guild_id = str(interaction.guild.id)
            if guild_id in autoroles:
                del autoroles[guild_id]

                with open('autoroles.json', 'w', encoding='utf-8') as f:
                    json.dump(autoroles, f, indent=4, ensure_ascii=False)
                embed = discord.Embed(title='Auto-role has been disabled for this server. :white_check_mark:', color=colorcode)
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title='No auto-role was set for this server. :x:', color=colorcode)
                await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f'[ERROR] {e}')
            embed = discord.Embed(title='An error occurred while trying to disable the auto-role. :x:', color=colorcode)
            await interaction.followup.send(embed=embed)

bot.tree.add_command(Welcome(bot))
bot.tree.add_command(Autorole(bot))

# Error handlers
@Welcome.enable.error
async def enable_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to enable auto-welcome messages.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while enabling auto-welcome messages.", ephemeral=True)

@Welcome.disable.error
async def disable_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to disable auto-welcome messages.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while disabling auto-welcome messages.", ephemeral=True)

@Autorole.enable.error
async def enable_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to enable auto-role.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while enabling auto-role.", ephemeral=True)

@Autorole.disable.error
async def disable_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to disable auto-role.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while disabling auto-role.", ephemeral=True)

'''
                    ____________________ SERVER SETTINGS COMMAND ____________________
'''
    
@bot.tree.command(name='settings', description='Check the current auto-welcome, auto-role, and ticket system settings.')
@app_commands.checks.has_permissions(administrator=True)
async def settings(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    guild_id = str(interaction.guild.id)

    # Auto-welcome settings
    try:
        with open('autowelcome.json', 'r', encoding='utf-8') as f:
            autowelcome = json.load(f)
        welcome_channel_id = autowelcome.get(guild_id)
        welcome_channel = interaction.guild.get_channel(int(welcome_channel_id)) if welcome_channel_id else None
    except Exception as e:
        print(f"Error reading autowelcome.json: {e}")
        welcome_channel = None

    # Auto-role settings
    try:
        with open('autoroles.json', 'r', encoding='utf-8') as f:
            autoroles = json.load(f)
        role_id = autoroles.get(guild_id)
        auto_role = interaction.guild.get_role(int(role_id)) if role_id else None
    except Exception as e:
        print(f"Error reading autoroles.json: {e}")
        auto_role = None

    # Ticket system settings
    try:
        with open('ticket_settings.json', 'r', encoding='utf-8') as f:
            ticket_settings = json.load(f)
        guild_ticket_settings = ticket_settings.get(guild_id, {})
        ticket_support_role_id = guild_ticket_settings.get('support_role_id')
        ticket_support_role = interaction.guild.get_role(int(ticket_support_role_id)) if ticket_support_role_id else None
        ticket_count = guild_ticket_settings.get('ticket_count', 0)
    except Exception as e:
        print(f"Error reading ticket_settings.json: {e}")
        guild_ticket_settings = {}
        ticket_support_role = None
        ticket_count = 0

    embed = discord.Embed(title=f"Settings for {interaction.guild.name}", color=colorcode)

    if welcome_channel:
        embed.add_field(name="Auto-Welcome Channel", value=welcome_channel.mention, inline=False)
    else:
        embed.add_field(name="Auto-Welcome Channel", value="Disabled", inline=False)

    if auto_role:
        embed.add_field(name="Auto-Role", value=auto_role.mention, inline=False)
    else:
        embed.add_field(name="Auto-Role", value="Disabled", inline=False)

    if guild_ticket_settings:
        embed.add_field(name="Ticket System", value="Enabled", inline=False)
        if ticket_support_role:
            embed.add_field(name="Ticket Support Role", value=ticket_support_role.mention, inline=False)
        else:
            embed.add_field(name="Ticket Support Role", value="Not set", inline=False)
        embed.add_field(name="Total Tickets Created", value=str(ticket_count), inline=False)
    else:
        embed.add_field(name="Ticket System", value="Disabled", inline=False)

    await interaction.followup.send(embed=embed)

@settings.error
async def settings_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need administrator permissions to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

'''
                    ____________________ BAN COMMAND ____________________
'''

@bot.tree.command(name="ban", description="Ban a member.")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(member="The member you want to ban.")
@app_commands.describe(reason="The reason for the ban.")
@app_commands.rename(member='member')
@app_commands.rename(reason='reason')
async def ban(interaction: discord.Interaction, member: discord.Member,
              reason: str):
    await member.ban(reason=reason)
    embed = discord.Embed(title=f"Successfully banned {member.name}!",
                          descriptionf=f"{member.id}",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@ban.error
async def ban_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ UNBAN COMMAND ____________________
'''

@bot.tree.command(name="unban", description="Unban a member.")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(userid="The member you want to unban.")
@app_commands.describe(reason="The reason for the unban.")
@app_commands.rename(userid='user-id')
@app_commands.rename(reason='reason')
async def unban(interaction: discord.Interaction, userid: discord.User,
                reason: str):
    await interaction.guild.unban(userid, reason=reason)
    embed = discord.Embed(title=f"Successfully unbanned {userid.name}!",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@unban.error
async def unban_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ KICK COMMAND ____________________
'''

@bot.tree.command(name="kick", description="Kick a member.")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(member="The member you want to kick.")
@app_commands.describe(reason="The reason for the kick.")
@app_commands.rename(member='member')
@app_commands.rename(reason='reason')
async def kick(interaction: discord.Interaction, member: discord.Member,
               reason: str):
    await member.kick(reason=reason)
    embed = discord.Embed(title=f"Successfully kicked {member.name}!",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@kick.error
async def kick_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ MUTE COMMAND ____________________
'''

@bot.tree.command(name="mute", description="Mute a member.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(member="The member you want to mute.")
@app_commands.describe(reason="The reason for the mute.")
@app_commands.rename(member='member')
@app_commands.rename(reason='reason')
async def mute(interaction: discord.Interaction, member: discord.Member,
               reason: str):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)
    await member.add_roles(muted_role, reason=reason)
    embed = discord.Embed(title=f"Successfully muted {member.name}!",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@mute.error
async def mute_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ UNMUTE COMMAND ____________________
'''

@bot.tree.command(name="unmute", description="Unmute a member.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(member="The member you want to unmute.")
@app_commands.describe(reason="The reason for the unmute.")
@app_commands.rename(member='member')
@app_commands.rename(reason='reason')
async def unmute(interaction: discord.Interaction, member: discord.Member,
                 reason: str):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role, reason=reason)
        embed = discord.Embed(title=f"Successfully unmuted {member.name}!",
                              color=colorcode)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title=f"{member.name} is not muted.",
                              color=colorcode)
        await interaction.response.send_message(embed=embed)

@unmute.error
async def unmute_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)

'''
                    ____________________ PURGE COMMAND ____________________
'''

@bot.tree.command(name="purge", description="Purge a certain amount of messages.")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(amount="The amount of messages you want to purge.")
@app_commands.rename(amount='amount')
async def purge(interaction: discord.Interaction, amount: int):
    if amount > 100:
        embed = discord.Embed(title="You can only purge up to 100 messages.",
                              color=colorcode)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(
        f'Purging `{amount}` messages in 3 seconds...')
        time.sleep(3)
        msg = await interaction.original_response()
        await msg.delete()
        channel1 = interaction.channel
        await interaction.channel.purge(limit=amount)
        embed = discord.Embed(title=f"Successfully purged `{amount}` messages!",
                          color=colorcode)
        await channel1.send(embed=embed)

@purge.error
async def purge_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ SLOWMODE COMMAND ____________________
'''

@bot.tree.command(name="slowmode", description="Set the slowmode for a channel.")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(
    seconds="The amount of seconds you want to set the slowmode to.")
@app_commands.rename(seconds='seconds')
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    embed = discord.Embed(
        title=f"Successfully set the slowmode to `{seconds}` seconds!",
        color=colorcode)
    await adapter.create_interaction_response(embed=embed)

@slowmode.error
async def slowmode_error(interaction: discord.Interaction,
                         error: app_commands.AppCommandError):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ SLOWMODE OFF COMMAND ____________________
'''

@bot.tree.command(name="slowmodeoff", description="Turn the slowmode off for a channel.")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmodeoff(interaction: discord.Interaction):
    await interaction.channel.edit(slowmode_delay=0)
    embed = discord.Embed(title=f"Successfully turned off the slowmode!",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@slowmodeoff.error
async def slowmodeoff_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ CREATE ROLE COMMAND ____________________
'''

@bot.tree.command(name="createrole", description="Create a role.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(name="The name of the role.")
@app_commands.rename(name='name')
async def createrole(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    await guild.create_role(name=name)
    embed = discord.Embed(title=f"Successfully created role `{name}`!",
                          color=colorcode)
    await interaction.response.send_message(embed=embed)

@createrole.error
async def createrole_error(error: app_commands.AppCommandError):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)
    
'''
                    ____________________ DELETE ROLE COMMAND ____________________
'''

@bot.tree.command(name="deleterole", description="Delete a role.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(role="The role you want to delete.")
@app_commands.rename(role='role')
async def deleterole(interaction: discord.Interaction, role: discord.Role):
    await role.delete()
    embed = discord.Embed(title=f"Successfully deleted role `{role.name}`!", color=colorcode)
    await interaction.response.send_message(embed=embed)

@deleterole.error
async def deleterole_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ ADD ROLE COMMAND ____________________
'''

@bot.tree.command(name="addrole", description="Add a role to a member.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(member="The member you want to add the role to.")
@app_commands.describe(role="The role you want to add to the member.")
@app_commands.rename(member='member')
@app_commands.rename(role='role')
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    embed = discord.Embed(title=f"Successfully added role ` {role.name} ` to {member.name}!", color=colorcode)
    await interaction.response.send_message(embed=embed)

@addrole.error
async def addrole_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ REMOVE ROLE COMMAND ____________________
'''

@bot.tree.command(name="removerole", description="Remove a role from a member.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(member="The member you want to remove the role from.")
@app_commands.describe(role="The role you want to remove from the member.")
@app_commands.rename(member='member')
@app_commands.rename(role='role')
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    embed = discord.Embed(title=f"Successfully removed role `{role.name}` from {member.name}", color=colorcode)
    await interaction.response.send_message(embed=embed)

@removerole.error
async def removerole_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ CREATE CHANNEL COMMAND ____________________
'''

@bot.tree.command(name="createchannel", description="Create a channel.")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(name="Name of the channel.")
@app_commands.rename(name='name')
async def createchannel(interaction: discord.Interaction, name: str):
    guild = interaction.guild
    await guild.create_text_channel(name)
    embed = discord.Embed(title=f"Successfully created channel `{name}` :white_check_mark: ", color=colorcode)
    await interaction.response.send_message(embed=embed)

@createchannel.error
async def createchannel_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)

'''
                    ____________________ DELETE CHANNEL COMMAND ____________________
'''

@bot.tree.command(name="deletechannel", description="Delete a channel.")
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.describe(channel="Channel you want to delete.")
@app_commands.rename(channel='channel')
async def deletechannel(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.delete()
    embed = discord.Embed(title=f"Successfully deleted channel `{channel}` :white_check_mark: ", color=colorcode)
    await interaction.response.send_message(embed=embed)

@deletechannel.error
async def deletechannel_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)
        
'''
                    ____________________ INVITE COMMAND ____________________
'''

@bot.tree.command(name="invite", description="Invite bot to your own server.")
async def invite(interaction: discord.Interaction):
    embed = discord.Embed( description='''
**Invite me to your server!** [**Click Here!**](https://discord.com/oauth2/authorize?client_id=1255749237300269079&permissions=8&integration_type=0&scope=applications.commands+bot)
        
**Join our server for fun and support!** [**Click Here!**](https://discord.gg/7uq96Bdadk)
''', color=colorcode)
    await interaction.response.send_message(embed=embed)

'''
                    ____________________ SERVERS COMMAND ____________________
'''

@bot.tree.command(name='servers', description='Owner - Shows the servers the bot is in.')
@is_owner()
async def servers(interaction: discord.Interaction):
    embed = discord.Embed(title="List of servers:", color=colorcode)
    servernumber = 0
    for guild in bot.guilds:
        servernumber += 1
        embed.add_field(name=f'Server #{servernumber}' , value=f'Server Name: `{guild.name}` - Server ID: `{guild.id}`', inline=False)
    await interaction.response.send_message(embed=embed)

@servers.error
async def servers_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}', ephemeral=True)
    
'''
                    ____________________ COMMAND COUNT COMMAND ____________________
'''

@bot.tree.command(name="commandcount", description="Show the command count for the bot.")
async def commandcount(interaction: discord.Interaction):
    embed = discord.Embed( title="Command Count", description=f"There are currently {len(bot.tree.get_commands())}", color=colorcode)
    await interaction.response.send_message(embed=embed)

'''
                    ____________________ SUGGEST COMMAND ____________________
'''

@bot.tree.command(name="suggest", description="Suggest new commands.")
@app_commands.checks.cooldown(1, 300.0, key=lambda i: (i.guild_id, i.user.id))
async def suggest(interaction: discord.Interaction, suggestion: str):
    user = await bot.fetch_user(832268459006099467)
    embed1 = discord.Embed(
        title="Suggestion Sent!",
        description="Your suggestion has been sent to the owner.",
        color=colorcode)
    await interaction.response.send_message(embed=embed1, ephemeral=True)
    embed2 = discord.Embed(description=f'''
    New sugestion from {interaction.user.mention}

    Suggestion: {suggestion}''',
                           color=colorcode)
    await user.send(embed=embed2)

@suggest.error
async def suggest_error(interaction: discord.Interaction,
                        error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
        await interaction.response.send_message(
            f"Please wait until `{timeRemaining}` to execute this command again.",
            ephemeral=True)

'''
                    ____________________ SUSPENDED: STATUS COMMAND ____________________
'''

# @bot.tree.command(name="status", description="Set the bots status.")
# @is_owner()
# @app_commands.describe(status="Choose a presence for the bot.")
# @app_commands.describe(text="Type a status for the bot. Type none to remove.")
# @app_commands.rename(status='status')
# @app_commands.rename(text='text')
# async def status(interaction: discord.Interaction,
#                  status: typing.Literal['Online', 'Do Not Disturb', 'Idle',
#                                         'Invisible'], text: str):
    
#     if status == 'Online':
#         activity = discord.Game(name=f"{text}", type=3)
#         await bot.change_presence(status=discord.Status.online,
#                                   activity=activity)
#         embed = discord.Embed(
#             title=
#             f"Successfully set status to `Online - {text}` :white_check_mark: ",
#             color=0x000000)
#         await interaction.response.send_message(embed=embed)

#     elif status == 'Do Not Disturb':
#         activity = discord.Game(name=f"{text}", type=3)
#         await bot.change_presence(status=discord.Status.dnd, activity=activity)
#         embed = discord.Embed(
#             title=
#             f"Successfully set status to `Do Not Disturb - {text}` :white_check_mark: ",
#             color=0x000000)
#         await interaction.response.send_message(embed=embed)

#     elif status == 'Idle':
#         activity = discord.Game(name=f"{text}", type=3)
#         await bot.change_presence(status=discord.Status.idle,
#                                   activity=activity)
#         embed = discord.Embed(
#             title=
#             f"Successfully set status to `Idle - {text}` :white_check_mark: ",
#             color=0x000000)
#         await interaction.response.send_message(embed=embed)

#     elif status == 'Invisible':
#         await bot.change_presence(status=discord.Status.invisible)
#         embed = discord.Embed(
#             title=f"Successfully set status to `Invisible` :white_check_mark: ",
#             color=0x000000)
#         await interaction.response.send_message(embed=embed)

# @status.error
# async def status_error(interaction: discord.Interaction, error):
#     await interaction.response.send_message(f'{DiscordCommandError}',
#                                             ephemeral=True)

'''
                    ____________________ PING COMMAND ____________________
'''

@bot.tree.command(name='ping', description='Owner - Show the bots latency')
@is_owner()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f'Pong! `{round(bot.latency * 1000)}ms`')

@ping.error
async def ping_error(interaction: discord.Interaction, error):
    await interaction.response.send_message(f'{DiscordCommandError}',
                                            ephemeral=True)
    
'''
                    ____________________ BOT END ____________________
'''

bot.run(token)