import discord
import asyncio
import youtube_dl
import os
import colorsys
import logging
import typing
import json
import aiohttp
import requests
import string
import translate
from translate import Translator
import discord, datetime, time
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import has_permissions 
from discord.utils import get,find
from time import localtime, strftime
import requests as rq
import random
from urllib.request import Request, urlopen
import discord, datetime, time

start_time = time.time()

m_offets = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1)
]

m_numbers = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:"]

with open("prefixes.json") as f:
    prefixes = json.load(f)
default_prefix = "d?"

def prefix(bot, message):
    id = message.server.id
    return prefixes.get(id, default_prefix)

bot = commands.Bot(command_prefix=prefix)

@bot.command(name="prefix", pass_context=True)
@commands.has_permissions(administrator=True)
async def _prefix(ctx, new_prefix):
    # Do any validations you want to do
    prefixes[ctx.message.server.id] = new_prefix
    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)


@_prefix.error
async def prefix_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, you do not have a administrator permission to use this command.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)	
	
bot.remove_command('help')

from discord import opus
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
             'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']


def load_opus_lib(opus_libs=OPUS_LIBS):
    if opus.is_loaded():
        return True

    for opus_lib in opus_libs:
            try:
                opus.load_opus(opus_lib)
                return
            except OSError:
                pass

    raise RuntimeError('Could not load an opus lib. Tried %s' %
                       (', '.join(opus_libs)))
load_opus_lib()

in_voice=[]


players = {}
songs = {}
playing = {}


async def all_false():
    for i in bot.servers:
        playing[i.id]=False


async def checking_voice(ctx):
    await asyncio.sleep(130)
    if playing[ctx.message.server.id]== False:
        try:
            pos = in_voice.index(ctx.message.server.id)
            del in_voice[pos]
            server = ctx.message.server
            voice_client = bot.voice_client_in(server)
            await voice_client.disconnect()
            await bot.say("{} left because there was no audio playing for a while".format(bot.user.name))
        except:
            pass


async def status_task():
    while True:
        await bot.change_presence(game=discord.Game(name='d?help', type=2))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(set(bot.get_all_members())))+' users', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name=str(len(bot.servers))+' servers', type=3))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='music'))
        await asyncio.sleep(5)
        await bot.change_presence(game=discord.Game(name='I need some upvotes to grow ;('))
        await asyncio.sleep(5)





@bot.event
async def on_ready():
   bot.loop.create_task(status_task())
   print(bot.user.name)
	
   print('Servers connected to:')
   for server in bot.servers:
        print(server.name)

	



    
    
@bot.command(pass_context=True)
async def ping(ctx):
    await bot.say(":ping_pong: ping!! xSSS")
    print ("user has pinged")
	
	
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def servers(ctx):
  servers = list(bot.servers)
  await bot.say(f"Connected on {str(len(servers))} servers:")
  await bot.say('\n'.join(server.name for server in servers))


@bot.command(pass_context=True)
async def info(ctx, user: discord.Member):
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0xe67e22)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.add_field(name="Created at", value=user.created_at)
    
    embed.add_field(name="nickname", value=user.nick)
    embed.add_field(name="Bot", value=user.bot)
    embed.set_thumbnail(url=user.avatar_url)
    await bot.say(embed=embed)

@bot.command(pass_context=True)  
@commands.has_permissions(kick_members=True)     
async def serverinfo(ctx):
    server = ctx.message.server
    roles = [x.name for x in server.role_hierarchy]
    role_length = len(roles)
    if role_length > 50: #Just in case there are too many roles...
        roles = roles[:50]
        roles.append('>>>> Displaying[50/%s] Roles'%len(roles))
    roles = ', '.join(roles);
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    online = len([m.status for m in server.members if m.status == discord.Status.online or m.status == discord.Status.idle])
    embed = discord.Embed(name="{} Server information".format(server.name), color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_thumbnail(url = server.icon_url)
    embed.add_field(name="Server name", value=server.name, inline=True)
    embed.add_field(name="Owner", value=server.owner.mention)
    embed.add_field(name="Server ID", value=server.id, inline=True)
    embed.add_field(name="Roles", value=len(server.roles), inline=True)
    embed.add_field(name="Members", value=len(server.members), inline=True)
    embed.add_field(name="Online", value=f"**{online}/{len(server.members)}**")
    embed.add_field(name="Created at", value=server.created_at.strftime("%d %b %Y %H:%M"))
    embed.add_field(name="Emojis", value=f"{len(server.emojis)}/100")
    embed.add_field(name="Server Region", value=str(server.region).title())
    embed.add_field(name="Total Channels", value=len(server.channels))
    embed.add_field(name="AFK Channel", value=str(server.afk_channel))
    embed.add_field(name="AFK Timeout", value=server.afk_timeout)
    embed.add_field(name="Verification Level", value=server.verification_level)
    embed.add_field(name="Roles {}".format(role_length), value = roles)
    await bot.send_message(ctx.message.channel, embed=embed)   
      


 
@bot.command(pass_context=True, no_pm=True)
async def avatar(ctx, member: discord.Member):
    """User Avatar"""
    await bot.reply("{}".format(member.avatar_url))

@bot.command()
async def stats():
	servers = list(bot.servers)
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
	embed = discord.Embed(title="📄Servers:", description=f"{str(len(servers))}", color=0xFFFF)
	embed.add_field(name="👤Users:", value=f"{str(len(set(bot.get_all_members())))}")
	embed.add_field(name="🕛Uptime:", value=f"{text}")
	embed.add_field(name="🚨Invite", value=f"[Link](https://discordapp.com/api/oauth2/authorize?client_id=501659280680681472&permissions=8&scope=bot)")
	embed.add_field(name="🚪Support server", value=f"[Click Here](https://discord.gg/FrgAWZA)")
	embed.add_field(name="💾Memory", value="Free: 10.50GB / Total: 20.80GB",inline=True)
	embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/501659280680681472/6587c3847aafd25f631eaa556a779368.webp?size=1024")
	await bot.say(embed=embed) 

@bot.command()
async def stats2():
	servers = list(bot.servers)
	current_time = time.time()
	difference = int(round(current_time - start_time))
	text = str(datetime.timedelta(seconds=difference))
        info = discord.Embed(color=0xDEADBF, title="**Info**")
        info.description = "Servers: **{}**\nMembers: **{}**\nUptime: **{}**\nMemory: **Free: 10.50GB / Total: 20.80GB**\n".format(
            str(len(servers)),
            str(len(set(bot.get_all_members()))),
            str(len(self.bot.commands)),
            text,
        )
        info.add_field(name="Links",
                       value="[GitHub](https://github.com/rekt4lifecs/NekoBotRewrite/) | "
                               "[Support Server](https://discord.gg/q98qeYN) | "
                               "[Patreon](https://www.patreon.com/NekoBot)")
        info.set_thumbnail(url="https://cdn.discordapp.com/avatars/501659280680681472/6587c3847aafd25f631eaa556a779368.webp?size=1024"))
        await bot.say(embed=info)
  

@bot.command(pass_context=True)
async def clear(ctx, number):
   if ctx.message.author.server_permissions.administrator:
    mgs = [] #Empty list to put all the messages in the log
    number = int(number) #Converting the amount of messages to delete to an integer
    async for x in bot.logs_from(ctx.message.channel, limit = number):
        mgs.append(x)
    await bot.delete_messages(mgs)


	
@bot.command(name="mute", pass_context=True)
@commands.has_permissions(kick_members=True, administrator=True)
async def _mute(ctx, user: discord.Member = None, *, arg = None):
	if user is None:
		await bot.say("please provide a member")
		return False
	if arg is None:
		await bot.say("please provide a reason to {}".format(user.name))
		return False
	if user.server_permissions.kick_members:
		return False
	reason = arg
	author = ctx.message.author
	role = discord.utils.get(ctx.message.server.roles, name="Muted")
	await bot.add_roles(user, role)
	embed = discord.Embed(title="Mute", description=" ", color=0xFFA500)
	embed.add_field(name="User: ", value="<@{}>".format(user.id), inline=False)
	embed.add_field(name="Moderator: ", value="{}".format(author.mention), inline=False)
	embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
	await bot.say(embed=embed)
	

@_mute.error
async def mute_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You don't have requirement permission to use this command `kick_members`.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)	

@bot.command(name="unmute", pass_context=True)
@commands.has_permissions(kick_members=True, administrator=True)
async def _unmute(ctx, user: discord.Member = None, *, arg = None):
	if user is None:
		await bot.say("please provide a member")
		return False
	if arg is None:
		await bot.say("please provide a reason to {}".format(user.name))
		return False
	if user.server_permissions.kick_members:
		return False
	reason = arg
	author = ctx.message.author
	role = discord.utils.get(ctx.message.server.roles, name="Muted")
	await bot.remove_roles(user, role)
	embed = discord.Embed(title="Unmute", description=" ", color=0x00ff00)
	embed.add_field(name="User: ", value="<@{}>".format(user.id), inline=False)
	embed.add_field(name="Moderator: ", value="{}".format(author.mention), inline=False)
	embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
	await bot.say(embed=embed)
	

@_unmute.error
async def unmute_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You don't have requirement permission to use this command `kick_members`.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)		
		
		
	
@bot.command(pass_context=True)
async def botinfo(ctx):
	embed=discord.Embed(title="Bot name", description="Devil", color=0xFFFF00)
	embed.add_field(name="Creator", value="Imran")
	embed.add_field(name="Invite link", value="[Click Here!](https://discordapp.com/api/oauth2/authorize?client_id=501659280680681472&permissions=2146958839&scope=bot)")
	embed.add_field(name="Prefix", value="d?")
	await bot.say(embed=embed)
	
        
@bot.command(pass_context = True)
@commands.has_permissions(administrator=True) 
async def bans(ctx):
    x = await bot.get_bans(ctx.message.server)
    x = '\n'.join([y.name for y in x])
    embed = discord.Embed(title = "Ban list", description = x, color = 0xFFFFF)
    return await bot.say(embed = embed)
       
        
        

@bot.command(pass_context=True)
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))



@bot.command(name="kick", pass_context=True)
@commands.has_permissions(kick_members=True)
async def _kick(ctx, user: discord.Member = None, *, arg = None):
	if user is None:
		await bot.say("please provide a member")
		return False
	if arg is None:
		await bot.say("please provide a reason to {}".format(user.name))
		return False
	if user.server_permissions.kick_members:
		return False
	reason = arg
	author = ctx.message.author
	await bot.kick(user)
	embed = discord.Embed(title="Kick", description=" ", color=0x00ff00)
	embed.add_field(name="User: ", value="<@{}>".format(user.id), inline=False)
	embed.add_field(name="Moderator: ", value="{}".format(author.mention), inline=False)
	embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
	await bot.say(embed=embed)
	

@_kick.error
async def kick_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You don't have requirement permission to use this command `kick_members`.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)


        
@bot.command(name="ban", pass_context=True)
@commands.has_permissions(ban_members=True)
async def _ban(ctx, user: discord.Member = None, *, arg = None):
	if user is None:
		await bot.say("please provide a member")
		return False
	if arg is None:
		await bot.say("please provide a reason to {}".format(user.name))
		return False
	if user.server_permissions.ban_members:
		return False
	reason = arg
	author = ctx.message.author
	await bot.ban(user)
	embed = discord.Embed(title="Ban", description=" ", color=0xFF0000)
	embed.add_field(name="User: ", value="<@{}>".format(user.id), inline=False)
	embed.add_field(name="Moderator: ", value="{}".format(author.mention), inline=False)
	embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
	await bot.say(embed=embed)
	

@_ban.error
async def ban_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You don't have requirement permission to use this command `ban_members`.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)	
	
	
@bot.command(name="warn", pass_context=True)
@commands.has_permissions(kick_members=True)
async def _warn(ctx, user: discord.Member = None, *, arg = None):
	if user is None:
		await bot.say("please provide a member")
		return False
	if arg is None:
		await bot.say("please provide a reason to {}".format(user.name))
		return False
	if user.server_permissions.kick_members:
		return False
	reason = arg
	author = ctx.message.author
	server = ctx.message.server
	embed = discord.Embed(title="Warn", description=" ", color=0x00ff00)
	embed.add_field(name="User: ", value="<@{}>".format(user.id), inline=False)
	embed.add_field(name="Moderator: ", value="{}".format(author.mention), inline=False)
	embed.add_field(name="Reason: ", value="{}\n".format(arg), inline=False)
	await bot.say(embed=embed)
	await bot.send_message(user, "You have been warned for: {}".format(reason))
	await bot.send_message(user, "from: {} server".format(server))
	

@_warn.error
async def warn_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, You don't have requirement permission to use this command `kick_members`.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)	

	
	
	
	
	
	
	
	
@bot.command(pass_context=True)
@commands.has_permissions(kick_members=True, ban_members=True, administrator=True)
async def unban(con,user:int):
    try:
        who=await bot.get_user_info(user)
        await bot.unban(con.message.server,who)
        await bot.say("User has been unbanned")
    except:
        await bot.say("Something went wrong")
		

        

@bot.command(pass_context=True)
async def get_id(ctx):
    await bot.say("Channel id: {}".format(ctx.message.channel.id))       



    
@bot.command()
async def repeat(ctx, times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content) 
	
	
	
   
@bot.command()
async def invite():
  	"""Bot Invite"""
  	await bot.say("\U0001f44d")
  	await bot.whisper("Add me with this link {}".format(discord.utils.oauth_url(bot.user.id)))
	
	
	

@bot.event
async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.blue())
            await bot.send_message(ctx.message.channel, embed=em)    
		
		
		
    
@bot.command()
async def guildcount():
  	"""Bot Guild Count"""
  	await bot.say("**I'm in {} Guilds!**".format(len(bot.servers)))  
    
    
    
   
@bot.command(pass_context=True)
async def guildid(ctx):
	  """Guild ID"""
	  await bot.say("`{}`".format(ctx.message.server.id))   
	
	
    
@bot.command(pass_context=True, no_pm=True)
async def guildicon(ctx):
    """Guild Icon"""
    await bot.reply("{}".format(ctx.message.server.icon_url))
	
	
    
@bot.command(pass_context=True, hidden=True)
async def setgame(ctx, *, game):
    if ctx.message.author.id not in owner:
        return
    game = game.strip()
    if game != "":
        try:
            await bot.change_presence(game=discord.Game(name=game))
        except:
            await bot.say("Failed to change game")
        else:
            await bot.say("Successfuly changed game to {}".format(game))
    else:
        await bot.send_cmd_help(ctx)    
	
	
    
    
@bot.command(pass_context=True)
async def setname(ctx, *, name):
    if ctx.message.author.id not in owner:
        return
    name = name.strip()
    if name != "":
        try:
            await bot.edit_profile(username=name)
        except:
            await bot.say("Failed to change name")
        else:
            await bot.say("Successfuly changed name to {}".format(name))
    else:
        await bot.send_cmd_help(ctx)
        
        




@bot.event
async def on_member_join(member):
    print("Recognised that a member called " + member.name + " joined")
    await bot.send_message(member, newUserMessage)
    print("Sent message to " + member.name)

    # give member the steam role here
    ## to do this the bot must have 'Manage Roles' permission on server, and role to add must be lower than bot's top role
    role = discord.utils.get(member.server.roles, name="name-of-your-role")
    await bot.add_roles(member, role)
    print("Added role '" + role.name + "' to " + member.name)        
        
    
  
    

	
	

#@bot.command(pass_context=True)
#async def help(ctx):
    #server = ctx.message.server
    #embed = discord.Embed(title=None, description="**Help command for devil**", color=0xff00f6)
    #embed.add_field(name='Help Server',value='https://discord.gg/cQZBYFV', inline=True)
    #embed.add_field(name="♏Moderations Commands", value="__**Use it like**__ ``d?help_moderations`` __**- to get list of moderations**__")
    #embed.add_field(name="💮Fun Commands", value="__**Use it like**__ ``d?help_fun`` __**- to get list of fun commands**__")
    #embed.add_field(name="💠General Commands", value="__**Use it like**__ ``d?help_general`` __**- to get list of general commands**__")
    #embed.add_field(name="ⓂMusic Commands", value="__**Use it like**__ ``d?help_music`` __**- to get list of music commands**__")
    #embed.add_field(name="💸Economy Commands", value="__**Use it like**__ ``d?help_economy`` __**- to get list of economy commands**__")
    #embed.add_field(name='Note:', value="**More commands being added soon!**")
    #embed.set_thumbnail(url=server.icon_url)
    #embed.set_footer(text="Requested by: " + author.name)
    #await bot.say(embed=embed)
    
#@bot.command(pass_context=True)
#async def help_fun(ctx):
	#author = ctx.message.author
	#embed = discord.Embed(title=None, description="***__Fun Commands..__***", color=0xFFFF)
	#embed.add_field(name = "kiss", value="Use it like ``d?kiss @user``",inline = False)
	#embed.add_field(name = "hug", value="Use it like ``d?hug @user``",inline = False)
	#embed.add_field(name = "slap", value="Use it like ``d?slap @user``",inline = False)
	#embed.add_field(name = "thuglife", value="Use it like ``d?thuglife``",inline = False)
	#embed.add_field(name = "burned", value="Use it like ``d?burned``",inline = False)
	#embed.add_field(name = "rolldice", value="Use it like ``d?rolldice`` [fun command]",inline = False)
	#embed.add_field(name = "filpcoin", value="Use it like ``d?flipcoin`` [50 50 chance]",inline = False)
	#embed.add_field(name = "meme", value="Use it like ``d?meme``",inline = False)
	#embed.add_field(name = "Movie", value="Use it like ``d?movie <any movie name>``",inline = False)
	#embed.add_field(name = "Guess", value="Use it like ``d?guess [1-10]``",inline = False)
	#embed.add_field(name = "Virgin", value="Use it like ``d?virgin @user``",inline = False)
	#embed.add_field(name = "Gender", value="Use it like ``d?gender @user``",inline = False)
	#embed.add_field(name = "Damn", value="Use it like ``d?damn``",inline = False)
	#embed.add_field(name = "happybirthday", value="Use it like ``d?happybirthday @user``",inline = False)
	#embed.add_field(name = "Randomshow", value="Use it like ``d?randomshow``",inline = False)
	#embed.add_field(name = "Tweet", value="Use it like ``d?tweet @user <text>``",inline = False)
	#embed.add_field(name = "Dog", value="Use it like ``d?dog``",inline = False)
	#embed.add_field(name = "cat", value="Use it like ``d?cat``",inline = False)
	#embed.add_field(name = "Fox", value="Use it like ``d?fox``",inline = False)
	#embed.add_field(name = "Eightball", value="Use it like ``d?eigthball <your text>``",inline = False)

	#embed.add_field(name = 'Note:', value="**More commands being added soon!**",inline = False)

	#embed.set_footer(text="Requested by: " + author.name)
	#await bot.say(embed=embed)
	#embed = discord.Embed(title=f"User: {ctx.message.author.name} have used fun command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
	#await bot.send_message(channel, embed=embed)


#@bot.command(pass_context=True)
#async def help_general(ctx):
   #author = ctx.message.author
   #embed = discord.Embed(title=None, description="***__General Commands..__***", color=0xFFFF)
   #embed.add_field(name = 'd?happybirthday @user ',value ='To wish someone happy birthday',inline = False)
   #embed.add_field(name = 'd?joined @user ', value='Says when a member joined.', inline = False)		
   #embed.add_field(name = 'd?repeat', value='Use it like ``d?repeat 5``', inline = False)
   #embed.add_field(name = 'd?online', value='Use it like ``d?online``  Members Online.', inline = False)
   #embed.add_field(name = 'd?offline', value='Use it like ``d?offline``  Members Offline.', inline = False)
   #embed.add_field(name = 'd?membercount', value='Use it like ``d?membercount`` to see how many members are in the server.', inline = False)
   #embed.add_field(name = 'd?invite',value ='Use it to invite our bot to your server',inline = False)
   #embed.add_field(name = 'd?avatar', value='Use it like ``d?avatar @user`` show user avatar', inline = False)  
   #embed.add_field(name = 'd?info',value ='Use it like ``d?info @user`` to get some basic info of tagged user',inline = False)
   #embed.add_field(name = 'd?meme',value ='Use it like ``d?meme`` to get a random meme',inline = False)
   #embed.add_field(name = 'd?movie',value ='Use it like ``d?movie <any movie name>`` to get some basic info of movie',inline = False)
   #embed.add_field(name = 'd?joke',value ='Use it like ``d?joke`` to get a random joke',inline = False)
   #embed.add_field(name = 'd?botinfo',value ='Use it like ``d?botinfo`` to get some basic info of bot',inline = False)
   #embed.add_field(name = 'Note:', value="***More commands being added soon!***")
   #embed.set_footer(text="Requested by: " + author.name)
   #await bot.say(embed=embed)
   #embed = discord.Embed(title=f"User: {ctx.message.author.name} have used moderations command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
   #await bot.send_message(channel, embed=embed)

	
	
	
	
#@bot.command(pass_context=True)
#async def help_moderations(ctx):
   #author = ctx.message.author
   #embed = discord.Embed(title=None, description="***__Moderation Commands..__***", color=0xFFFF)	 
   #embed.add_field(name = 'd?kick(Kick members Permission Required)',value ='Use it like ``d?kick @user`` to kick any user',inline = False)
   #embed.add_field(name = 'd?mute(Mute members Permission Required)',value ='Use it like ``d?mute @user <time>`` to mute any user',inline = False)
   #embed.add_field(name = 'd?unmute(Mute members Permission Required)',value ='Use it like ``d?unmute @user`` to unmute anyone',inline = False)
   #embed.add_field(name = 'd?ban(Ban members Permission Required)',value ='Use it like ``d?ban @user`` to ban any user',inline = False)
   #embed.add_field(name = 'd?unban(Ban members Permission Required)', value="Use it liked ``?unban user.id`` | for example d!unban 277983178914922497",inline = False)
   #embed.add_field(name = 'd?setupwelcomer(Admin Permission required)',value ='Simply use it to make a channel named welcome so that bot will send welcome and leaves logs in that channel.',inline = False)
   #embed.add_field(name = 'd?setuplog(Admin Permission required)',value ='Simply use it to make a channel named logs so that bot will send logs in that channel.',inline = False)
   #embed.add_field(name = 'd?Dm(Admin Permission required)', value="Use it like ``d?dm @user <text>`` to send dm any one",inline = False)
   #embed.add_field(name = 'd?say(Admin permission required)',value ='Use it like ``d?say <text>``',inline = False)
   #embed.add_field(name = 'd?announce(Admin permission required)', value="Use it like ``d?announce #channel <text>``",inline = False)
   #embed.add_field(name = 'd?prefix(Admin permission required)', value="Use it like ``d?prefix ?``",inline = False)
   #embed.add_field(name = 'd?serverinfo(Kick members Permission Required) ',value ='Use it like ``d?serverinfo`` to get server info',inline = False)

   #embed.add_field(name = 'Note:', value="***More commands being added soon!***")
   #embed.set_footer(text="Requested by: " + author.name)
   #await bot.say(embed=embed)
   #embed = discord.Embed(title=f"User: {ctx.message.author.name} have used moderations command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
   #await bot.send_message(channel, embed=embed)
	
	
#@bot.command(pass_context=True)
#async def help_economy(ctx):
    #author = ctx.message.author
    #embed = discord.Embed(title=None, description="***__Economy Commands..__***", color=0xFFFF)
    #embed.add_field(name = "Daily", value="Use it like ``d?daily``",inline = False)
    #embed.add_field(name = "Leaderboard", value="Use it like ``d?lb``",inline = False)
    #embed.add_field(name = "Balance", value="Use it like ``d?bal``",inline = False)
    #embed.add_field(name = "Work", value="Use it like ``d?work``",inline = False)
    #embed.add_field(name = "Coinflip", value="Use it like ``d?coinflip heads/tails <your amount>``",inline = False)
    #embed.add_field(name = "Dice", value="Use it like ``d?dice <your No between 1-6> <your  amount>``",inline = False)
    #embed.add_field(name = 'Note:', value="***More commands being added soon!***")
    #embed.set_footer(text="Requested by: " + author.name)
    #await bot.say(embed=embed)
    #embed = discord.Embed(title=f"User: {ctx.message.author.name} have used moderations command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
    #await bot.send_message(channel, embed=embed)

@bot.command(pass_context = True)
async def help(ctx):
    server = ctx.message.server
    author = ctx.message.author
    embed = discord.Embed(title=None, description="**Help command for devil**", color=0xff00f6)		
    embed.add_field(name="Moderations Commands:", value="``kick`` ``ban`` ``mute`` ``unmute`` ``warn`` ``clear`` ``say`` ``dm`` ``unban`` ``setupwelcomer`` ``setuplog`` ``announce`` ``embed`` ``stats``",inline = False)
    embed.add_field(name="Action Commands:", value="``poke`` ``kiss`` ``slap`` ``hug`` ``bite`` ``pat`` ``bloodsuck`` ``cuddle`` ``thuglife`` ``burned`` ``savage`` ``facedesk`` ``highfive``",inline = False)		      
    embed.add_field(name="General Commands:", value="``ping`` ``info`` ``serverinfo`` ``membercount`` ``guildicon`` ``guildcount`` ``invite`` ``avatar`` ``online`` ``offline`` ``botinfo`` ``joined``",inline = False) 		
    embed.add_field(name="Music Commands:", value="``play`` ``skip`` ``stop`` ``song`` ``resume`` ``pause`` ``queue`` ``volume`` ``mutemusic`` ``unmutemusic``",inline = False) 		
    embed.add_field(name="Fun Commands:", value=" ``virgin`` ``randommovie`` ``meme`` ``randomanime`` ``bottleflip`` ``joke`` ``movie`` ``tweet`` ``happybirthday`` ``gender`` ``minesweeper`` ``guess`` ``fact`` ``truthordare``",inline = False)	
    embed.add_field(name="Image Commands:", value="``meme`` ``dog`` ``fox`` ``cat`` ``img`` ``randomshow`` ``neko`` ``buddy`` ``duck`` ``bird`` ``randompic`` ``animepic``",inline = False)	
    embed.add_field(name="Misc Commands:", value="``tweet`` ``trans`` ``eightball``",inline = False)
    embed.add_field(name="Game Commands:", value="``flipcoin`` ``rolldice`` ``guess``",inline = False)
    embed.add_field(name="Economy Commands:", value="``daily`` ``dice`` ``coinflip`` ``bal`` ``work`` ``lb``",inline = False)
    embed.add_field(name='Need more help?', value="Join our support server at https://discord.gg/Eagbjbj")  
    embed.set_thumbnail(url=server.icon_url)
    embed.set_footer(text="Requested by: " + author.name)
    await bot.say(embed=embed)		

@bot.command(pass_context=True)
async def duck(ctx):
        """
        Function: Send random duck picture
        Command: `>duck`
        Usage Example: `>duck`
        """

        emb = discord.Embed(title=None)
        r = rq.Session().get('https://random-d.uk/api/v1/random')
        if r.status_code == 200:
            emb.set_image(url=r.json()['url'])
            await bot.say(embed=emb)
        if r.status_code != 200:
            emb = discord.Embed(title="Error {}".format(r.status_code))
            emb.set_image(url='https://http.cat/{}'.format(r.status_code))
            await bot.say(embed=emb)


@bot.command(pass_context=True)
async def bird(ctx):
        """Shows a random birb"""
        url = "http://random.birb.pw/tweet.json/"
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        data = json.loads(urlopen(request).read().decode())
        emb=discord.Embed(description=":bird:", colour=ctx.message.author.colour)
        emb.set_image(url="http://random.birb.pw/img/" + data["file"])
        try:
            await bot.say(embed=emb)
        except:
            await bot.say("The birb didn't make it, sorry :no_entry:")		

@bot.command(pass_context=True)
async def trans(ctx, *args):
    """Ex: '>trans en->de example' OR '>trans de Beispiel'"""
    if "bugs" in args[0]:
        await client.say("Wraith... bugs is not a language.")
        return

    if len(args[0]) == 2:
        arr = [args[0], "en"]
    else: arr = '{}'.format(args[0]).split('->')
    t = Translator(from_lang=arr[0],to_lang=arr[1])
    await bot.say('```' + t.translate(" ".join(args[1:])) + '```')
	
@bot.command(pass_context=True, hidden=True, enabled=True)
async def neko(ctx, nsfw:str="false"):
        """
        Function: Send random neko picture, adding nsfw will send nsfw ones
        Command: `d?neko`
        Usage Example: `d?neko` or `d?neko nsfw`
        """
        if nsfw.lower() == 'nsfw':
            nsfw = 'true'
        else:
            nsfw = 'false'
        img = rq.get(
            'https://nekos.moe/api/v1/random/image?count=1&nsfw={}'.format(nsfw)).json()
        url = 'https://http.cat/200'
        emb = discord.Embed(title='Neko')
        emb.set_image(
            url='https://nekos.moe/image/{}'.format(img['images'][0]['id']))
        await bot.say(embed=emb)	


	
@bot.command(pass_context=True)
async def facedesk(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["https://gifimage.net/wp-content/uploads/2018/11/face-desk-gif-1.gif", "https://media.giphy.com/media/1cXN3ppw2lC0M/giphy.gif", "https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPArtgSjP1eqJCWy7SnEQyZ8A", "http://i.imgur.com/tnBGkwT.gif", "https://media1.tenor.com/images/3eeb3943b8ecab2617d26f4b36f7f9a3/tenor.gif"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url=random.choice(gifs))
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)
	
	
@bot.command(pass_context=True)
async def highfive(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>highfive <mention a user>```")
    else:
        randomurl = ["http://rs584.pbsrc.com/albums/ss289/vampgirl17/Danny%20Phantom/hifive.gif", "https://thumbs.gfycat.com/ActualWarmheartedDungbeetle-small.gif", "https://media1.tenor.com/images/aed08ae3d802b0de9791057e2dadf7a6/tenor.gif", "https://i.pinimg.com/originals/d2/b2/7c/d2b27cdf7a0d320e18efbe21dfca9a50.gif", "https://media1.tenor.com/images/9730876547cb3939388cf79b8a641da9/tenor.gif"]
        embed = discord.Embed(title=f"{user.name} highfives {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)
	
@bot.command(pass_context=True)
async def pat(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>pat <mention a user>```")
    else:
        randomurl = ["https://thumbs.gfycat.com/ImpurePleasantArthropods-small.gif", "https://i.imgur.com/4ssddEQ.gif", "https://thumbs.gfycat.com/ShockingFaroffJavalina-size_restricted.gif", "http://i.imgur.com/laEy6LU.gif", "https://i.imgur.com/NNOz81F.gif"]
        embed = discord.Embed(title=f"{user.name} You just got a patted from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)		
	
	
@bot.command(pass_context=True)
async def bite(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>bite <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/fhkRUj3BWmMnu/giphy.gif", "https://gifimage.net/wp-content/uploads/2017/09/anime-bite-gif-7.gif", "https://toxicmuffin.files.wordpress.com/2013/04/tumblr_mkzqyghtsm1r0rp7xo1_400.gif", "https://78.media.tumblr.com/tumblr_m5vv15KoxB1qklrzno2_500.gif", "https://media1.tenor.com/images/06f88667b86a701b1613bbf5fb9205e9/tenor.gif"]
        embed = discord.Embed(title=f"{user.name} you have been bitten by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	
@bot.command(pass_context=True)
async def poke(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>poke <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/WvVzZ9mCyMjsc/giphy.gif", "https://gifimage.net/wp-content/uploads/2017/09/anime-poke-gif-11.gif", "https://media1.tenor.com/images/1a64ac660387543c5b779ba1d7da2c9e/tenor.gif", "https://i.gifer.com/bun.gif", "https://thumbs.gfycat.com/KeyImaginativeBushsqueaker-size_restricted.gif"]
        embed = discord.Embed(title=f"{user.name} you have been poked by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	
@bot.command(pass_context=True)
async def bloodsuck(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>bloodsuck <mention a user>```")
    else:
        randomurl = ["https://78.media.tumblr.com/tumblr_m5vv15KoxB1qklrzno2_500.gif", "https://i1.wp.com/24.media.tumblr.com/tumblr_mcj6b5gsSr1riv2oqo1_500.gif", "https://i.imgur.com/UbaeYIq.gif", "https://i.imgur.com/CtwmzpG.gif", "https://images.gr-assets.com/hostedimages/1438121044ra/15667005.gif"]
        embed = discord.Embed(title=f"{user.name} is sucking the blood of {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	

	
@bot.command(pass_context=True)
async def cuddle(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>cuddle <mention a user>```")
    else:
        randomurl = ["https://media.giphy.com/media/143v0Z4767T15e/giphy.gif", "https://i.imgur.com/nrdYNtL.gif", "https://media1.tenor.com/images/8f8ba3baeecdf28f3e0fa7d4ce1a8586/tenor.gif", "https://66.media.tumblr.com/18fdf4adcb5ad89f5469a91e860f80ba/tumblr_oltayyHynP1sy5k7wo1_400.gif", "https://i.imgur.com/wOmoeF8.gif"]
        embed = discord.Embed(title=f"{user.name} you have been cuddled by {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
	

	
	
	
	
	
	
@bot.command(pass_context=True)
async def online(con):
    amt = 0
    for i in con.message.server.members:
        if i.status != discord.Status.offline:
            amt += 1
    await bot.send_message(con.message.channel, "**Currently `{}` Members Online In `{}`**".format(amt,con.message.server.name))



@bot.command(pass_context=True)
async def offline(con):
    amt = 0
    for i in con.message.server.members:
        if i.status == discord.Status.offline:
            amt += 1
    await bot.send_message(con.message.channel, "**Currently `{}` Members Offline In `{}`**".format(amt,con.message.server.name))





	
@bot.event
async def on_member_join(member):
    channel = get(member.server.channels, name="welcome")
    await bot.send_file(channel, '_Sans-Simple-Red.gif')
    embed = discord.Embed(title='New Member Join', description="Welcome,{} to the {}! Be sure to have fun!:tada::confetti_ball:".format(member.mention, member.server.name), colour=0x7ED6DE)
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name='__Join position__', value='{}'.format(str(member.server.member_count)), inline=True)
    embed.add_field(name="Joined", value=member.joined_at)
    embed.set_thumbnail(url=member.avatar_url)
    await bot.send_message(channel, embed=embed)
    
	
@bot.event
async def on_member_remove(member):
    channel = get(member.server.channels, name="welcome")
    embed = discord.Embed(title='Member Left', description="goodbye😞,{}".format(member.mention), colour=0xff00f6)
    embed.set_author(name=member.name, icon_url=member.avatar_url)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.set_thumbnail(url=member.avatar_url)
    await bot.send_message(channel, embed=embed)







	
	

	
	
	
@bot.event
async def on_message_delete(message):
    if not message.author.bot:
      channelname = 'logs'
      logchannel=None
      for channel in message.server.channels:
        if channel.name == channelname:
          user = message.author
      for channel in message.author.server.channels:
        if channel.name == 'logs':
          logchannel = channel
          r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
          embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
          embed.set_author(name='Message deleted')
          embed.add_field(name = 'User: **{0}**'.format(user.name),value ='UserID: **{}**'.format(user.id),inline = False)
          embed.add_field(name = 'Message:',value ='{}'.format(message.content),inline = False)
          embed.add_field(name = 'Channel:',value ='{}'.format(message.channel.name),inline = False)
          await bot.send_message(logchannel,  embed=embed)
	

@bot.command(pass_context = True)
@commands.has_permissions(administrator=True)
async def setup(ctx):
    author = ctx.message.author
    server = ctx.message.server
    mod_perms = discord.Permissions(manage_messages=True, kick_members=True, manage_nicknames =True, mute_members=True)
    admin_perms = discord.Permissions(ADMINISTRATOR=True)

    
    await bot.create_role(author.server, name="Owner", permissions=admin_perms)
    await bot.create_role(author.server, name="Admin", permissions=admin_perms)
    await bot.create_role(author.server, name="Senior Moderator", permissions=mod_perms)
    await bot.create_role(author.server, name="G.O.H")
    await bot.create_role(author.server, name="Moderator", permissions=mod_perms)
    await bot.create_role(author.server, name="Muted")

    await bot.create_role(author.server, name="Friend of Owner")
    await bot.create_role(author.server, name="Verified")
        
    await bot.create_channel(server, '🎉welcome🎉',everyone)
    await bot.create_channel(server, '🎯rules🎯',everyone)
    await bot.create_channel(server, '🎥featured-content🎥',everyone)
    await bot.create_channel(server, '📢announcements📢',everyone)
    await bot.create_channel(server, '📢vote_polls📢',everyone)
    await bot.create_channel(server, 'private_chat',private)
    await bot.create_channel(server, '🎮general_chat🎮',user)
    await bot.create_channel(server, '🎮general_media🎮',user)
    await bot.create_channel(server, '👍bots_zone👍',user)
    await bot.create_channel(server, '🎥youtube_links🎥',user)
    await bot.create_channel(server, '🎥giveaway_links🎥',user)
    await bot.create_channel(server, '🎥other_links🎥',user)
    await bot.create_channel(server, '🔥Music Zone🔥', type=discord.ChannelType.voice)
    await bot.create_channel(server, '🔥music_command🔥s',user)
    await bot.create_channel(server, '🔥Chill Zone🔥', type=discord.ChannelType.voice)
    print(f"{ctx.message.author.name} from {ctx.message.server} used d?setup command")

    
def user_is_me(ctx):
	return ctx.message.author.id == "455500545587675156"
	
	

						 
						 
@bot.command(name="say", pass_context=True)
@commands.has_permissions(administrator=True)
async def _say(ctx, *, msg = None):
    await bot.delete_message(ctx.message)

    if not msg: await bot.say("Please specify a message to send")
    else: await bot.say(msg)
    return
    
    embed = discord.Embed(title=f"User: {ctx.message.author.name} have used say command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
    await bot.send_message(channel, embed=embed)

    
@_say.error
async def say_error(error, ctx):
	if isinstance(error, discord.ext.commands.errors.CheckFailure):
		text = "Sorry {}, you do not have a administrator permission to use this command.".format(ctx.message.author.mention)
		await bot.send_message(ctx.message.channel, text)					 

@bot.command(pass_context=True, no_pm=True)
async def membercount(ctx):
	members = set(ctx.message.server.members)
	bots = filter(lambda m: m.bot, members)
	bots = set(bots)
	users = members - bots
	await bot.send_message(ctx.message.channel, embed=discord.Embed(title="Membercount", description="{} there is {} users and {} bots with a total of {} members in this server.".format(ctx.message.author.mention, len(users), len(bots), len(ctx.message.server.members)), colour=0X008CFF))
	embed = discord.Embed(title=f"User: {ctx.message.author.name} have used membercount command", description=f"ID: {ctx.message.author.id}", color=0xff9393)
	await bot.send_message(channel, embed=embed)		
		
		

@bot.command(pass_context=True)
async def slap(ctx, user: discord.Member = None):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["http://rs20.pbsrc.com/albums/b217/strangething/flurry-of-blows.gif?w=280&h=210&fit=crop", "https://media.giphy.com/media/LB1kIoSRFTC2Q/giphy.gif", "https://i.imgur.com/4MQkDKm.gif"]
    if user == None:
        await bot.say(f"{ctx.message.author.mention} ```Proper usage is\n\n>slap <mention a user>```")
    else:
        embed = discord.Embed(title=f"{ctx.message.author.name} Just slapped the shit out of {user.name}!", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(gifs))
        await bot.say(embed=embed)	
		
		
		
@bot.command(pass_context=True)
async def kiss(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    randomurl = ["https://media3.giphy.com/media/G3va31oEEnIkM/giphy.gif", "https://i.imgur.com/eisk88U.gif", "https://media1.tenor.com/images/e4fcb11bc3f6585ecc70276cc325aa1c/tenor.gif?itemid=7386341", "http://25.media.tumblr.com/6a0377e5cab1c8695f8f115b756187a8/tumblr_msbc5kC6uD1s9g6xgo1_500.gif"]
    if user.id == ctx.message.author.id:
        await bot.say("Goodluck kissing yourself {}".format(ctx.message.author.mention))
    else:
        embed = discord.Embed(title=f"{user.name} You just got a kiss from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)



@bot.command(pass_context=True)
async def hug(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    if user.id == ctx.message.author.id:
        await bot.say("{} Wanted to hug himself/herself , good luck on that you will look like an idiot trying to do it".format(user.mention))
    else:
        randomurl = ["http://gifimage.net/wp-content/uploads/2017/09/anime-hug-gif-5.gif", "https://media1.tenor.com/images/595f89fa0ea06a5e3d7ddd00e920a5bb/tenor.gif?itemid=7919037", "https://media.giphy.com/media/NvkwNVuHdLRSw/giphy.gif"]
        embed = discord.Embed(title=f"{user.name} You just got a hug from {ctx.message.author.name}", color = discord.Color((r << 16) + (g << 8) + b))
        embed.set_image(url=random.choice(randomurl))
        await bot.say(embed=embed)	
		
		
@bot.command(pass_context=True)
async def joke(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    joke = ["What do you call a frozen dog?\nA pupsicle", "What do you call a dog magician?\nA labracadabrador", "What do you call a large dog that meditates?\nAware wolf", "How did the little scottish dog feel when he saw a monster\nTerrier-fied!", "Why did the computer show up at work late?\nBecause it had a hard drive", "Autocorrect has become my worst enime", "What do you call an IPhone that isn't kidding around\nDead Siri-ous", "The guy who invented auto-correct for smartphones passed away today\nRestaurant in peace", "You know you're texting too much when you say LOL in real life, instead of laughing", "I have a question = I have 18 Questions\nI'll look into it = I've already forgotten about it", "Knock Knock!\nWho's there?\Owls say\nOwls say who?\nYes they do.", "Knock Knock!\nWho's there?\nWill\nWill who?\nWill you just open the door already?", "Knock Knock!\nWho's there?\nAlpaca\nAlpaca who?\nAlpaca the suitcase, you load up the car.", "Yo momma's teeth is so yellow, when she smiled at traffic, it slowed down.", "Yo momma's so fat, she brought a spoon to the super bowl.", "Yo momma's so fat, when she went to the beach, all the whales started singing 'We are family'", "Yo momma's so stupid, she put lipstick on her forehead to make up her mind.", "Yo momma's so fat, even Dora can't explore her.", "Yo momma's so old, her breast milk is actually powder", "Yo momma's so fat, she has to wear six different watches: one for each time zone", "Yo momma's so dumb, she went to the dentist to get a bluetooth", "Yo momma's so fat, the aliens call her 'the mothership'", "Yo momma's so ugly, she made an onion cry.", "Yo momma's so fat, the only letters she knows in the alphabet are K.F.C", "Yo momma's so ugly, she threw a boomerang and it refused to come back", "Yo momma's so fat, Donald trump used her as a wall", "Sends a cringey joke\nTypes LOL\nFace in real life : Serious AF", "I just got fired from my job at the keyboard factory. They told me I wasn't putting enough shifts.", "Thanks to autocorrect, 1 in 5 children will be getting a visit from Satan this Christmas.", "Have you ever heard about the new restaurant called karma?\nThere's no menu, You get what you deserve.", "Did you hear about the claustrophobic astronaut?\nHe just needed a little space", "Why don't scientists trust atoms?\nBecase they make up everything", "How did you drown a hipster?\nThrow him in the mainstream", "How does moses make tea?\nHe brews", "A man tells his doctor\n'DOC, HELP ME. I'm addicted to twitter!'\nThe doctor replies\n'Sorry i don't follow you...'", "I told my wife she was drawing her eyebrows too high. She looked surprised.", "I threw a boomeranga a few years ago. I now live in constant fear"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.add_field(name=f"Here is a random joke that {ctx.message.author.name} requested", value=random.choice(joke))
    await bot.say(embed=embed)		
		
@bot.command(pass_context=True)
async def burned(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url="https://i.imgur.com/wY4xbak.gif")
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)



@bot.command(pass_context=True)
async def savage(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["https://media.giphy.com/media/s7eezS6vxhACk/giphy.gif", "https://m.popkey.co/5bd499/gK00J_s-200x150.gif",
            "https://i.imgur.com/XILk4Xv.gif"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url=random.choice(gifs))
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)

	
@bot.command(pass_context=True)
async def thuglife(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    gifs = ["https://media.giphy.com/media/kU1qORlDWErOU/giphy.gif", "https://media.giphy.com/media/EFf8O7znQ6zRK/giphy.gif",
            "https://i.imgur.com/XILk4Xv.gif", "http://www.goodbooksandgoodwine.com/wp-content/uploads/2011/11/make-it-rain-guys.gif"]
    embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url=random.choice(gifs))
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)	
		
@bot.command(pass_context = True)
async def meme(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(title='Random Meme', description='from reddit', color = discord.Color((r << 16) + (g << 8) + b))
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.reddit.com/r/me_irl/random") as r:
            data = await r.json()
            embed.set_image(url=data[0]["data"]["children"][0]["data"]["url"])
            embed.set_footer(text=f'Requested by: {ctx.message.author.display_name}', icon_url=f'{ctx.message.author.avatar_url}')
            embed.timestamp = datetime.datetime.utcnow()
            await bot.say(embed=embed)
						 

@bot.command(pass_context = True)
async def dm(ctx, user: discord.Member, *, msg: str):
   if user is None or msg is None:
       await bot.say('Invalid args. Use this command like: ``d?dm @user message``')
   if ctx.message.author.server_permissions.kick_members == False:
       await bot.say('**You do not have permission to use this command**')
       return
   else:
       await bot.send_message(user, msg)
       await bot.delete_message(ctx.message)          
       await bot.say("Success! Your DM has made it! :white_check_mark: ")		
		
		
@bot.command(pass_context = True)
async def flipcoin(ctx):
    choices = ['Heads', 'Tails', 'Coin self-destructed']
    color = discord.Color(value=0x00ff00)
    embed=discord.Embed(color=color, title='Flipped a coin!')
    embed.description = random.choice(choices)
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=embed)	
		
@bot.command(pass_context = True)
async def rolldice(ctx):
    choices = ['1', '2', '3', '4', '5', '6']
    color = discord.Color(value=0x00ff00)
    em = discord.Embed(color=color, title='Rolled! (1 6-sided die)', description=random.choice(choices))
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=em)	

@bot.command(pass_context=True)
async def movie(ctx, *, name:str=None):
        r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
        await bot.send_typing(ctx.message.channel)
        if name is None:
                embed=discord.Embed(description = "Please specify a movie, *eg. d?movie Inception*", color = discord.Color((r << 16) + (g << 8) + b))
                x = await bot.say(embed=embed)
                await asyncio.sleep(5)
                return await bot.delete_message(x)
        key = "4210fd67"
        url = "http://www.omdbapi.com/?t={}&apikey={}".format(name, key)
        response = requests.get(url)
        x = json.loads(response.text)
        embed=discord.Embed(title = "**{}**".format(name).upper(), description = "Here is your movie {}".format(ctx.message.author.name), color = discord.Color((r << 16) + (g << 8) + b))
        if x["Poster"] != "N/A":
            embed.set_thumbnail(url = x["Poster"])
            embed.add_field(name = "__Title__", value = x["Title"])
            embed.add_field(name = "__Released__", value = x["Released"])
            embed.add_field(name = "__Runtime__", value = x["Runtime"])
            embed.add_field(name = "__Genre__", value = x["Genre"])
            embed.add_field(name = "__Director__", value = x["Director"])
            embed.add_field(name = "__Writer__", value = x["Writer"])
            embed.add_field(name = "__Actors__", value = x["Actors"])
            embed.add_field(name = "__Plot__", value = x["Plot"])
            embed.add_field(name = "__Language__", value = x["Language"])
            embed.add_field(name = "__Imdb Rating__", value = x["imdbRating"]+"/10")
            embed.add_field(name = "__Type__", value = x["Type"])
            embed.set_footer(text = "Information from the OMDB API")
            await bot.say(embed=embed)

@bot.command(pass_context = True)
async def announce(ctx, channel: discord.Channel=None, *, msg: str=None):
    member = ctx.message.author
    if channel is None or msg is None:
        await bot.say('Invalid args. Use this command like ``d?announce #channel text here``')
        return
    else:
        if member.server_permissions.administrator == False:
            await bot.say('**You do not have permission to use this command**')
            return
        else:
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed=discord.Embed(title="Announcement", description="{}".format(msg), color = discord.Color((r << 16) + (g << 8) + b))
            await bot.send_message(channel, embed=embed)
            await bot.delete_message(ctx.message)




		
		

	
		
@bot.event
async def on_message_edit(before, after):
    if before.content == after.content:
      return
    if before.author == bot.user:
      return
    else:
      user = before.author
      member = after.author
      for channel in user.server.channels:
        if channel.name == 'logs':
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
            embed.set_author(name='Message edited')
            embed.add_field(name = 'User: **{0}**'.format(user.name),value ='UserID: **{}**'.format(user.id),inline = False)
            embed.add_field(name = 'Before:',value ='{}'.format(before.content),inline = False)
            embed.add_field(name = 'After:',value ='{}'.format(after.content),inline = False)
            embed.add_field(name = 'Channel:',value ='{}'.format(before.channel.name),inline = False)
            await bot.send_message(channel, embed=embed)		
		
@bot.command(pass_context = True)
async def setupwelcomer(ctx):
    if ctx.message.author.bot:
      return
    if ctx.message.author.server_permissions.administrator == False:
      await bot.say('**You do not have permission to use this command**')
      return
    else:
      server = ctx.message.server
      everyone_perms = discord.PermissionOverwrite(send_messages=False, read_messages=True)
      everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
      await bot.create_channel(server, 'welcome',everyone)
      await bot.say(':white_check_mark:**Success setup**')
	
	
		
@bot.command(pass_context = True)
async def setuplog(ctx):
    if ctx.message.author.bot:
      return
    if ctx.message.author.server_permissions.administrator == False:
      await bot.say('**You do not have permission to use this command**')
      return
    else:
      author = ctx.message.author
      server = ctx.message.server
      everyone_perms = discord.PermissionOverwrite(send_messages=False, read_messages=True)
      everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
      await bot.create_channel(server, 'logs',everyone)	
      await bot.say(':white_check_mark:**Success setup**')

@bot.command(pass_context=True)
async def gender(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    random.seed(user.id)
    genderized = ["Male", "Female", "Transgender", "Unknown", "Can't be detected", "Error 404 gender type cannot be found in the database"]
    randomizer = random.choice(genderized)
    if user == ctx.message.author:
        embed = discord.Embed(title="You should know your own gender", color = discord.Color((r << 16) + (g << 8) + b))
        await bot.say(embed=embed)
    else:
        embed = discord.Embed(color=0xfff47d)
        embed.add_field(name=f"{user.name}'s gender check results", value=f"{randomizer}")
        await bot.say(embed=embed)   


@bot.command(pass_context=True)
async def virgin(ctx, user: discord.Member):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    random.seed(user.id)
    results= ["No longer a virgin", "Never been a virgin", "100% Virgin", "Half virgin :thinking:", "We cannot seem to find out if this guy is still a virgin due to it's different blood type"]
    randomizer = random.choice(results)
    if user == ctx.message.author:
        embed = discord.Embed(title="Go ask yourself if you are still a virgin", color = discord.Color((r << 16) + (g << 8) + b))
        await bot.say(embed=embed)
    else:
        embed = discord.Embed(color=0x7dfff2)
        embed.add_field(name=f"{user.name}'s virginity check results", value=f"{randomizer}")
        await bot.say(embed=embed)


@bot.command(pass_context=True)
async def damn(ctx):
    r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
    embed = discord.Embed(title="DAMNNNNNNNN!!", color = discord.Color((r << 16) + (g << 8) + b))
    embed.set_image(url="http://i.imgur.com/OKMogWM.gif")
    await bot.say(embed=embed)
    await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def guess(ctx, number):
    try:
        arg = random.randint(1, 10)
    except ValueError:
        await bot.say("Invalid number")
    else:
        await bot.say('The correct answer is ' + str(arg))


@bot.command(pass_context = True)
async def happybirthday(ctx, *, msg = None):
    if not msg: await client.say("Please specify a user to wish")
    if '@here' in msg or '@everyone' in msg:
      return
    await bot.say('Happy birthday ' + msg + ' \nhttps://asset.holidaycardsapp.com/assets/card/b_day399-22d0564f899cecd0375ba593a891e1b9.png')
    return


@bot.command(pass_context=True)
async def cat(ctx):
        """
        Function: Send random cat picture
        Command: `d?cat`
        Usage Example: `d?cat`
        """
        r = rq.Session().get('http://aws.random.cat/meow')
        if r.status_code == 200:
            emb = discord.Embed(title='Cat')
            emb.set_image(url=r.json()['file'])
            await bot.say(embed=emb)

        if r.status_code != 200:
            emb = discord.Embed(title='Error {}'.format(r.status_code))
            emb.set_image(url='https://http.cat/{}'.format(r.status_code))
            await bot.say(embed=emb)


		
		
@bot.command(pass_context=True)
async def randomshow(ctx):
    url = 'https://tv-v2.api-fetch.website/random/show'
    r = rq.get(url).text
    r_json = json.loads(r)
    name = r_json['title']
    year = r_json['year']
    img = r_json['images']['poster']
    await bot.say("**Name**: {}\n**Year**: {}\n**Poster**: {}".format(name, year, img))	
	
		

@bot.command(pass_context=True)
async def img(ctx):
    """FAILED IMAGE GENERATOR BY KEYWORDS s.img dog"""
    img_api = '142cd7a6-ce58-4647-a81d-8b82f9668b75'

    query = ctx.message.content[5:]
    url = 'http://version1.api.memegenerator.net//Generators_Search?q={}&apiKey={}'.format(
        query, img_api)
    rq_link = rq.get(url).text
    rq_json = json.loads(rq_link)
    await bot.say(rq_json['result'][0]['imageUrl'])
	
@bot.command(pass_context=True)
async def tweet(ctx, usernamename:str, *, txt:str):
    url = f"https://nekobot.xyz/api/imagegen?type=tweet&username={usernamename}&text={txt}"
    async with aiohttp.ClientSession() as cs:
        async with cs.get(url) as r:
            res = await r.json()
            r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
            embed = discord.Embed(color = discord.Color((r << 16) + (g << 8) + b))
            embed.set_image(url=res['message'])
            embed.title = "{} twitted: {}".format(usernamename, txt)
            await bot.say(embed=embed)	



		
@bot.command(pass_context=True, aliases=['imranLoL'])
async def dog(ctx):
        """(d) random dog picture"""
        print("★DOG★")
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random.dog/woof.json') as r:
                    res = await r.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await bot.say(embed=em.set_image(url=res))	
	
	
	
	
@bot.command(pass_context=True)
async def fox(ctx):
        """
        Function: Send random fox picture
        Command: `d?fox`
        Usage Example: `d?fox`
        """

        emb = discord.Embed(title=None)
        r = rq.Session().get('https://randomfox.ca/floof/')
        if r.status_code == 200:
            emb.set_image(url=r.json()['image'])
            await bot.say(embed=emb)
        if r.status_code != 200:
            emb = discord.Embed(title="Error {}".format(r.status_code))
            emb.set_image(url='https://http.cat/{}'.format(r.status_code))
            await bot.say(embed=emb)	


@bot.command(pass_context = True)
async def eightball(ctx):
        '''Answer a question with a response'''

        responses = [
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Yes',
            'Signs point to yes',
            'Reply hazy try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Do not count on it',
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
        ]

        random_number = random.randint(0, 19)
        if random_number >= 0 and random_number <= 9:
            embed = discord.Embed(color=0x60E87B)
        elif random_number >= 10 and random_number <= 14:
            embed = discord.Embed(color=0xECE357)
        else:
            embed = discord.Embed(color=0xD55050)

        header = 'Magic/Eight ball says...'
        text = responses[random_number]

        embed.add_field(name=header, value=text, inline=True)
        await bot.say(embed=embed)	
	

	
@bot.command(pass_context = True)
async def truthordare(ctx):
    choices = [':regional_indicator_t: :regional_indicator_t: :regional_indicator_u: :regional_indicator_t: :regional_indicator_h: ', ':regional_indicator_d: :regional_indicator_a: :regional_indicator_r: :regional_indicator_e:']
    color = discord.Color(value=0x00ff00)
    embed=discord.Embed(color=color, title='TRUTH OR DARE')
    embed.description = random.choice(choices)
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=embed)
	
	
@bot.event	
async def on_server_role_create(role): 
    server = role.server
    user = "Unknown"
    channel = get(server.channels, name="logs")
    emb=discord.Embed(description="The role **{}** has been created by **{}**".format(role.name, user), colour=0x5fe468, timestamp=datetime.utcnow())
    emb.set_author(name=server, icon_url=server.icon_url)
    await bot.send_message(channel, embed=emb)
	
@bot.event	
async def on_server_role_delete(role):
    server = role.server
    channel = get(server.channels, name="logs")
    emb=discord.Embed(description="The role **{}** has been deleted".format(role.name), colour=0xf84b50, timestamp=datetime.utcnow())
    emb.set_author(name=server, icon_url=server.icon_url)
    await bot.send_message(channel, embed=emb)
  
@bot.event	
async def on_server_role_update(before, after):
    server = before.server	
    channel = get(server.channels, name="logs")
    if before.name != after.name:
        emb=discord.Embed(description="The role **{}** has been renamed".format(before.name), colour=0xe6842b, timestamp=datetime.utcnow())
        emb.set_author(name=server, icon_url=server.icon_url)
        emb.add_field(name="Before", value=before)
        emb.add_field(name="After", value=after)
    elif before.permissions != after.permissions:
        permissionadd = list(map(lambda x: "+ " + x[0].replace("_", " ").title(), filter(lambda x: x[0] in map(lambda x: x[0], filter(lambda x: x[1] == True, after.permissions)), filter(lambda x: x[1] == False, before.permissions))))
        permissionremove = list(map(lambda x: "- " + x[0].replace("_", " ").title(), filter(lambda x: x[0] in map(lambda x: x[0], filter(lambda x: x[1] == False, after.permissions)), filter(lambda x: x[1] == True, before.permissions))))
        emb=discord.Embed(description="The role **{}** has had permission changes made by **{}**\n```diff\n{}\n{}```".format(before.name, user, "\n".join(permissionadd), "\n".join(permissionremove)), colour=0xe6842b, timestamp=datetime.utcnow())
        emb.set_author(name=server, icon_url=server.icon_url)
    else: 
        return
    await bot.send_message(channel, embed=emb)
	
@bot.command(pass_context=True)
async def minesweeper(ctx, size: int = 5):
    size = max(min(size, 8), 2)
    bombs = [[random.randint(0, size - 1), random.randint(0, size - 1)] for x in range(int(size - 1))]
    is_on_board = lambda x, y: 0 <= x < size and 0 <= y < size
    has_bomb = lambda x, y: [i for i in bombs if i[0] == x and i[1] == y]
    message = "**Click to play**:\n"
    for y in range(size):
        for x in range(size):
            tile = "||{}||".format(chr(11036))
            if has_bomb(x, y):
                tile = "||{}||".format(chr(128163))
            else:
                count = 0
                for xmod, ymod in m_offets:
                    if is_on_board(x + xmod, y + ymod) and has_bomb(x + xmod, y + ymod):
                        count += 1
                if count != 0:
                    tile = "||{}||".format(m_numbers[count - 1])
            message += tile
        message += "\n"
    await bot.say(message)	



@bot.command(pass_context=True)
async def fact(ctx, *, text: str):
    if len(text) > 165:
        return await bot.send("Text too long...")
    async with aiohttp.ClientSession() as cs:
        async with cs.get("https://nekobot.xyz/api/imagegen?type=fact"
                          "&text=%s" % text) as r:
            data = await r.json()
	
    await bot.send_typing(ctx.message.channel)
    em = discord.Embed(color=0xDEADBF)
    await bot.say(embed=em.set_image(url=data["message"]))


@bot.command(pass_context = True)
async def bottleflip (ctx):
    choices = ['🍾Your bottle landed', '🍾Your bottle didnt land', '🍾Your bottle broke']
    color = discord.Color(value=0x00ff00)
    embed=discord.Embed(color=color, title='Flipped a Bottel!')
    embed.description = random.choice(choices)
    await bot.send_typing(ctx.message.channel)
    await bot.say(embed=embed)


@bot.command(pass_context=True)
async def randomanime(ctx):
  """
  Function: Send random anime
  Command: `d?randomanime`
  Usage Example: `d?randomanime`
  """

  rData = rq.Session().get('https://tv-v2.api-fetch.website/random/anime')
  r = rData.json()
  if rData.status_code == 200:
      title = r['title']
      mal_id = r['mal_id']
      genres = r['genres']
      url2 = 'https://api.jikan.moe/anime/{}/stats/'.format(mal_id)
      r2 = rq.Session().get(url2).text
      r2j = json.loads(r2)
      summary = r2j['synopsis']
      emb = discord.Embed(title=None, description="**Here is your randomanime**", color=0xe74c3c)
      emb.add_field(name = "__Title__", value ="{}".format(title), inline=False)
      emb.add_field(name = "__Genres__", value ="{}".format(genres), inline=False)
      emb.add_field(name = "__Synopsis__", value ="{}".format(summary), inline=False)
      await bot.say(embed=emb)		

  if rData.status_code != 200:
      emb = discord.Embed(title='Error {}'.format(rData.status_code))
      emb.set_image(url='https://http.cat/{}'.format(rData.status_code))
      await bot.say(embed=emb)
	
	
@bot.command(pass_context=True)
async def randommovie(ctx):
   """
   Function: Send a random movie
   Command: `d?randommovie`
   Usage Example: `d?randommovie`
   """

   movie = rq.Session().get('https://tv-v2.api-fetch.website/random/movie')
   if movie.status_code == 200:
      rest = movie.text
      rq_json = json.loads(rest)
      title = rq_json['title']
      summary = rq_json['synopsis']
      runtime = rq_json['runtime']
      genres = rq_json['genres']
      img = rq_json['images']['poster']
      gen = " ".join(genres[1:])
      emb = discord.Embed(title=None, description="**Here is your randommovie**", color=0xe74c3c)
      emb.add_field(name = "__Title__", value ="{}".format(title), inline=False)
      emb.add_field(name = "__Genres__", value ="{}".format(genres), inline=False)
      emb.add_field(name = "__Runtime__", value ="{} Minutes".format(runtime), inline=False)
      emb.add_field(name = "__Synopsis__", value ="{}".format(summary), inline=False)
      await bot.say(embed=emb)	
	
   if movie.status_code != 200:
      emb = discord.Embed(title='Error {}'.format(movie.status_code))
      emb.set_image(url='https://http.cat/{}'.format(movie.status_code))
      await bot.say(embed=emb)	
	
@bot.command(pass_context=True)
async def randompic(ctx):
        """
        Function: Sends you a random picture
        Command: `d?randompic`
        Usage Example: `d?randompic`
        """
        image_id = random.randint(1, 1084)
        emb = discord.Embed(title=None)
        emb.set_image(
            url='https://picsum.photos/200/300/?image={}'.format(image_id))
        await bot.say(embed=emb)	
	
	
@bot.command(pass_context=True)
async def animepic(ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://nekobot.xyz/api/v2/image/animepic") as r:
                date = await r.json()
        image = date["message"]
        #color = await helpers.get_dominant_color(self.bot, image, image.rpartition("/")[2], 10000)
        em = discord.Embed(color=0xDEADBF)
        await bot.say(embed=em.set_image(url=image))


@bot.command(pass_context=True, no_pm=True, aliases=["savatar"])
async def serveravatar(ctx):
        """Look at the current server avatar"""
        server = ctx.message.server
        colour = ''.join([random.choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)
        s=discord.Embed(colour=discord.Colour(value=colour))
        s.set_author(name="{}'s Icon".format(server.name), icon_url=server.icon_url, url=server.icon_url_as(format="png", size=1024))
        s.set_image(url=server.icon_url_as(format="png", size=1024))
        await bot.say(embed=s)






		
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def embed(ctx, *args):
    if ctx.message.author.bot:
      return
    else:
      argstr = " ".join(args)
      r, g, b = tuple(int(x * 255) for x in colorsys.hsv_to_rgb(random.random(), 1, 1))
      text = argstr
      color = discord.Color((r << 16) + (g << 8) + b)
      await bot.send_message(ctx.message.channel, embed=Embed(color = color, description=text))
      await bot.delete_message(ctx.message)
  




    
bot.run(os.environ['BOT_TOKEN'])
