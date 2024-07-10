from typing import Counter
import discord
from discord.ext import commands
import random
import os
import sys
import asyncio
import time
from discord.ui import Button, View
from discord import ButtonStyle
import typing
from colorama import Fore

OwnerID = [832268459006099467]

Prefix = open("prefix.txt","r").readline() 

token = 'token goes here!'

intents = discord.Intents.default()
#intents.members = True
#intents.message_content = True


bot = commands.Bot(command_prefix=f'{Prefix}', intents=intents, help_command=None)

@bot.event
async def on_ready():
    activity = discord.Game(name=f"{Prefix}help", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print('')
    print(f"{Fore.BLUE}- - - - - - ℤ𝕒𝕡𝕡𝕖𝕣 𝕚𝕤 𝕣𝕖𝕒𝕕𝕪! - - - - - -")
    print('')
    print('')
    print('')
    print('')
    print('.')


@bot.event
async def on_guild_join(guild: discord.Guild):
    print(f'Bot has been added to {guild.name}')

    textchannels = guild.text_channels
    channel = random.choice(textchannels)
    embed=discord.Embed(title="Hi, I'm Zapper bot!", description=f"Thank you for adding me! <3\nNote that I do not need any setup whatsoever.\n\nPrefix: `{Prefix}`\nHelp command: `{Prefix}help`\n\nCreated by: <@832268459006099467>", color=0x000000)
    embed.set_footer(text="The use of this bot is in agreement of the privacy policy.")
    button = Button(label="Privacy Policy", url="https://github.com/aiecsis/zapper/blob/main/README.md")
    view = View(timeout=30)
    view.add_item(button)
    await channel.send(embed=embed, view=view)



@bot.event
async def on_command_error(ctx, error):
    """Command error handler"""
    embed = discord.Embed(color=0x000000)
    if isinstance(error, commands.CommandNotFound):
        embed.title = "Command not Found"
        embed.description = "Recheck what you've typed."
        await ctx.send(embed=embed)



@bot.command(aliases=["r"])
async def restart(ctx):
    if ctx.author.id in OwnerID:
        embed=discord.Embed(title="Successfully Restarded! :white_check_mark: ", color=0x000000)
        await ctx.send(embed=embed)
        os.system("clear")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await ctx.send("You are not the owner of this bot, therefore you have no permission to use this command.")
        return



@bot.command()
async def prefixset(ctx, newprefix=None):
    if ctx.author.id in OwnerID:
        with open('prefix.txt', 'w') as prefixdelete:
            prefixdelete.seek(0)
            prefixdelete.truncate()
            prefixdelete.write(f"{newprefix}")  
            prefixdelete.close()
        await ctx.send(f"Successfully changed prefix to {newprefix}")
        os.system("clear")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await ctx.send("You are not the owner of this bot, therefore you have no permission to use this command.")
        return



@bot.command()
async def help(ctx):
    pages = 4
    cur_page = 1
    contents = [f'''
    **Fun Commands:**
    
    () = Required
    [] = Optional
    
    `{Prefix}help` -> Shows this page.
    `{Prefix}poll (question)` -> Make a poll with reactions.
    `{Prefix}embed` -> Send an embedded text.
    `{Prefix}choose (choice 1) | (choice 2)` -> Send a choices embed with reactions.
    `{Prefix}snipe` -> Snipe the last deleted message.
    `{Prefix}dice` -> Roll a dice.
    `{Prefix}coinflip` -> Flip a coin.
    `{Prefix}avatar` -> Shows your avatar.
    `{Prefix}userinfo` -> Shows your userinfo.
    `{Prefix}say (text)` -> Say something.
    
    ''',f'''
    **Moderating Commands:**

    `{Prefix}ban (@user) [reason]` -> Ban a member.
    `{Prefix}unban (user id)` -> Unban a member.
    `{Prefix}kick (@user) [reason]` -> Kick a member.
    `{Prefix}mute (@user) [reason]` -> Mute a member.
    `{Prefix}unmute (@user)` -> Unmute a member.
    `{Prefix}purge (amount)` -> Purge a certain amount of messages.
    `{Prefix}slowmode (seconds)` -> Set a slowmode for a channel.
    `{Prefix}slowmodeoff` -> Turn off slowmode for a channel.
    `{Prefix}createrole (name)` -> Create a roll with the entered name.
    `{Prefix}addrole (@user) (@role)` -> Add a roll to a member.
    `{Prefix}removerole (@user) (@role)` -> Remove a roll from a member.
    `{Prefix}warn (@user) [reason]` -> Warn a member.
    ''',f'''
    **Extra Commands:**
    
    `{Prefix}invite` -> Invite Zapper to your server!.
    `{Prefix}mc` -> Show member count for the server.
    `{Prefix}commandcount` -> Show the command count.

    ''',f'''
    **Zapper Settings:**

    `{Prefix}prefixset (new prefix)` -> Change the bot prefix.
    `{Prefix}restart` -> Restart the bot.
    `{Prefix}ping` -> Shows the bots ping.
    
    ''', 
                ]
    
    embed=discord.Embed(title="Zapper Help", description=(f"{contents[cur_page-1]}"), color=0x000000)
    embed.set_footer(text=f"Page {cur_page}/{pages}")
    message = await ctx.send(embed=embed)

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
        
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)

            if str(reaction.emoji) == "▶️" and cur_page != pages:
                cur_page += 1
                new_embed=discord.Embed(title="Zapper Help", description=(f"{contents[cur_page-1]}"), color=0x000000)
                new_embed.set_footer(text=f"Page {cur_page}/{pages}")
                await message.edit(embed=new_embed)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                cur_page -= 1
                new_embed=discord.Embed(title="Zapper Help", description=(f"{contents[cur_page-1]}"), color=0x00ffc8)
                new_embed.set_footer(text= f"Page {cur_page}/{pages}")
                await message.edit(embed=new_embed)
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)
                
        except asyncio.TimeoutError:
            await message.delete()
            break



@bot.command(aliases=['mc'])
async def membercount(ctx):
    guild = bot.guilds[0]
    mcEmbed = discord.Embed(description=f"This Server Has `{int(guild.member_count)}` Member/s!", color=0x000000)
    await ctx.send(embed = mcEmbed)



@bot.command()
async def suggest(ctx, *, suggestion=None):
    user_id = "832268459006099467"
    user = await bot.fetch_user(user_id)
    
    if suggestion == None:
        await ctx.send(f"Please enter a suggestion! Example: {Prefix}suggest (Suggestion)")
        return

    elif user:
        Embed = discord.Embed(title="New Suggestion!", description=f'''
        Suggested by {ctx.message.author.mention}
        
        Suggestion: {suggestion}
        
        ''', color=0x000000)
        await ctx.message.delete()
        sent = await ctx.send("Your suggestion has been sent to the developer!")
        await user.send(embed=Embed)
        time.sleep(5)
        await sent.delete()



@bot.command()
async def poll(ctx, question=None):
    if question == None:
        await ctx.send(f"Please enter a question! Example: `.poll (question)`")
        
    else:
        Embed = discord.Embed(title=f"{question}", color=0x000000)
        message = await ctx.send(embed = Embed)
        await message.add_reaction('❎')
        await message.add_reaction('✅')
        time.sleep(3)
        await ctx.message.delete()



@bot.command()
async def createrole(ctx, name=None):
    if name == None:
        await ctx.send(f"Please enter a name!")
    else:
        await ctx.guild.create_role(name=name)
        Embed = discord.Embed(description=f"**Successfully created role `{name}`!**", color=0x000000)
        await ctx.send(embed = Embed)



@bot.command()   
async def addrole(ctx, member: discord.Member=None, role: discord.Role=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.addrole (@user) (@role)`")
    
    elif role == None:
        await ctx.send(f"Please mention a role! Example: `.addrole (@user) (@role)`")

    elif role in member.roles:
        await ctx.send(f"That member already has that role!")

    elif ctx.author.guild_permissions.administrator == True:
        await member.add_roles(role)
        Embed = discord.Embed(description=f"**Successfully added role** `{role}` **to** `{member}`**!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def removerole(ctx, member: discord.Member=None, role: discord.Role=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.removerole (@user) (@role)`")
    
    elif role == None:
        await ctx.send(f"Please mention a role! Example: `.removerole (@user) (@role)`")

    elif role not in member.roles:
        await ctx.send(f"That member doesn't have that role!")

    elif ctx.author.guild_permissions.administrator == True:
        await member.remove_roles(role)
        Embed = discord.Embed(description=f"**Successfully removed role** `{role}` **from** `{member}`**!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")
            
@bot.command()
async def warn(ctx, member: discord.Member=None, *, reason=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.warn (@user) [reason]`")
    
    elif reason == None:
        await ctx.send(f"Please enter a reason! Example: `.warn (@user) [reason]`")

    elif ctx.author.guild_permissions.administrator == True:
        Embed = discord.Embed(description=f"**Successfully warned `{member}`**!**", color=0x000000)
        await member.send(f"You have been warned in **{ctx.guild.name}** for: **{reason}**") 
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def warnings(ctx, member: discord.Member=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.warnings (@user)`")
    
    elif ctx.author.guild_permissions.administrator == True:
        Embed = discord.Embed(description=f"**{member}** has **0** warnings!", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def clearwarnings(ctx, member: discord.Member=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.clearwarnings (@user)`")
    
    elif ctx.author.guild_permissions.administrator == True:
        Embed = discord.Embed(description=f"**Successfully cleared all warnings for `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")


@bot.command()
async def snipe(ctx):
    channel = ctx.channel 
    try:
        snipeEmbed = discord.Embed(title=f"Last deleted message in #{channel.name}", description = snipe_message_content[channel.id])
        snipeEmbed.set_footer(text=f"Deleted by {snipe_message_author[channel.id]}")
        await ctx.send(embed = snipeEmbed)
    except:
        await ctx.send(f"There are no deleted messages in #{channel.name}")


@bot.command()
async def choose(ctx, choice1=None, choice2=None):
    if choice1 == None:
        await ctx.send(f"Please enter a choice! Example: `.choose (choice 1) | (choice 2)`")
    elif choice2 == None:
        await ctx.send(f"Please enter a choice! Example: `.choose (choice 1) | (choice 2)`")
    else:
        choices = [choice1, choice2]
        Embed = discord.Embed(description=f"I choose `{random.choice(choices)}`!", color=0x000000)    
        await ctx.send(embed = Embed)


@bot.command()   
async def invite(ctx):  
    Embed = discord.Embed(description=f'''
    ・**Invite me to your server!** [Click Here!](https://discord.com/oauth2/authorize?client_id=1255749237300269079&permissions=8&integration_type=0&scope=bot)
    ・**Join our server!** [Zapped!](https://discord.gg/gXHRsBqRqk)
    ''', color=0x000000)
    await ctx.send(embed = Embed)

@bot.command()
async def commandcount(ctx):
    Embed = discord.Embed(description=f"**I have `{len(bot.commands)}` commands!**", color=0x000000)
    await ctx.send(embed = Embed)


@bot.command()
async def embed(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    await ctx.send('Waiting for a title')
    title = await bot.wait_for('message', check=check)

    await ctx.send('Waiting for a description')
    desc = await bot.wait_for('message', check=check)

    await ctx.channel.purge(limit=int(5))
    embed = discord.Embed(title=title.content, description=desc.content, color=0x000000)
    await ctx.send(embed=embed)



@bot.command()
async def slowmode(ctx, seconds: int=None):
    if seconds == None:
        await ctx.send(f"Please enter a number! Example: `.slowmode (seconds)`")
        
    if ctx.author.guild_permissions.administrator == True:
        await ctx.channel.edit(slowmode_delay=seconds)
        Embed = discord.Embed(description=f"**Successfully set the slowmode to `{seconds}` seconds!**", color=0x000000)
        await ctx.send(embed = Embed)
    else:
        await ctx.send(f"You don't have permission to use this command!")
        
@bot.command()
async def slowmodeoff(ctx):
    if ctx.author.guild_permissions.administrator == True:
        await ctx.channel.edit(slowmode_delay=0)
        Embed = discord.Embed(description=f"**Successfully turned off the slowmode!**", color=0x000000)
        await ctx.send(embed = Embed)
        
    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def purge(ctx, amount=None):
    if amount == None:
        amount = 50
        await ctx.channel.purge(limit=int(amount))
        Embed = discord.Embed(description=f"**Successfully purged last `{amount}` messages!**", color=0x000000)
        sent = await ctx.send(embed = Embed)
        time.sleep(5)
        await sent.delete()
        
    else:
        await ctx.channel.purge(limit=int(amount))
        Embed = discord.Embed(description=f"**Successfully purged last `{amount}` messages!**", color=0x000000)
        sent = await ctx.send(embed = Embed)
        time.sleep(5)
        await sent.delete()

@bot.command()
async def kick(ctx, member: discord.Member=None, *, reason=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.kick (@user) [reason]`")
    elif reason == None:
        reason = None
    elif ctx.author.guild_permissions.administrator == True:
        await member.kick(reason=reason)
        Embed = discord.Embed(description=f"**Successfully kicked `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def ban(ctx, member: discord.Member=None, *, reason=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.ban (@user) [reason]`")
    
    elif reason == None:
        await ctx.send(f"Please enter a reason! Example: `.ban (@user) [reason]`")

    elif ctx.author.guild_permissions.administrator == True:
        await member.ban(reason=reason)
        Embed = discord.Embed(description=f"**Successfully banned `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def unban(ctx, member: discord.Member=None, *, reason=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.unban (@user) [reason]`")
    
    elif reason == None:
        await ctx.send(f"Please enter a reason! Example: `.unban (@user) [reason]`")

    elif ctx.author.guild_permissions.administrator == True:
        await member.unban(reason=reason)
        Embed = discord.Embed(description=f"**Successfully unbanned `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def mute(ctx, member: discord.Member=None, *, reason=None):
    perms = discord.Permissions(send_messages=False, read_messages=True)
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role is None:
        role = await ctx.guild.create_role(name="Muted", permissions=perms)
        return
        
    elif member == None:
        await ctx.send(f"Please mention a member! Example: `.mute (@user) [reason]`")
    
    elif reason == None:
        await ctx.send(f"Please enter a reason! Example: `.mute (@user) [reason]`")

    elif ctx.author.guild_permissions.manage_roles == True:
        await member.add_roles(role)
        Embed = discord.Embed(description=f"**Successfully muted `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def unmute(ctx, member: discord.Member=None, *, reason=None):
    if member == None:
        await ctx.send(f"Please mention a member! Example: `.unmute (@user) [reason]`")
    
    elif reason == None:
        await ctx.send(f"Please enter a reason! Example: `.unmute (@user) [reason]`")

    elif ctx.author.guild_permissions.administrator == True:
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)
        Embed = discord.Embed(description=f"**Successfully unmuted `{member}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def lock(ctx):
    if ctx.author.guild_permissions.administrator == True:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        Embed = discord.Embed(description=f"**Successfully locked `{ctx.channel.name}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")


@bot.command()
async def unlock(ctx):
    if ctx.author.guild_permissions.administrator == True:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        Embed = discord.Embed(description=f"**Successfully unlocked `{ctx.channel.name}`!**", color=0x000000)
        await ctx.send(embed = Embed)

    else:
        await ctx.send(f"You don't have permission to use this command!")

@bot.command()
async def dice(ctx):
    Embed = discord.Embed(description=f"**You rolled a `{random.randint(1, 6)}`!**")
    await ctx.send(embed = Embed)

@bot.command()   
async def coin(ctx):
    Embed = discord.Embed(description=f"**You flipped a `{random.choice(['Heads', 'Tails'])}`!**")
    await ctx.send(embed = Embed)

@bot.command()
async def ping(ctx):
    if ctx.author.id in OwnerID:
        Embed = discord.Embed(description=f"**Pong! `{round(bot.latency * 1000)}`ms**", color=0x000000)
        await ctx.send(embed = Embed)

@bot.command()
async def say(ctx, *, message=None):
    if message == None:
        await ctx.send(f"Please enter a message! Example: `.say (message)`")
    else:
        await ctx.message.delete()
        await ctx.send(message)

bot.run(token)
