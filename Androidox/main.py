# Androidox Bot
# (C) 2024 TwizZ/Twisterry & Der Vater

from email import header
import discord
import sys
import confuse
import json
import asyncio
from discord.ext import commands, tasks, pages
from datetime import datetime
import datetime as dt
from discord import Interaction, option, Webhook
from rcon.source import rcon
import requests
from progress.spinner import Spinner
import time
from pytz import timezone
import progressbar
import urllib
import zipfile, os
import statistics
from discord.commands import Option
import threading
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor
import atexit
import psutil
from discord.ext.pages import Paginator, Page

bot = commands.Bot(intents = discord.Intents.all()) # define Bot variable
config = confuse.Configuration('Androidox')
config.set_file('config.yaml', base_for_paths=True)

# Config Variables
guildid = config['guildid'].get(int)
loglevel = config['loglevel'].get(int)
botid = config['botid'].get(int)
bottoken = config['bottoken'].get(str)
clientver = config['clientver'].get(str)
acceptrole = config['roles']['acceptrole'].get(int)
closerole = config['roles']['closerole'].get(int)
welcomech = config['channels']['welcomech'].get(int)
logch = config['channels']['logch'].get(int)
mcch = config['channels']['mcch'].get(int)
rulech = config['channels']['rulech'].get(int)
statch = config['channels']['statch'].get(int)
imprvch = config['channels']['imprvch'].get(int)
statmsg = config['msgid']['statmsg'].get(int)
mcip = config['minecraft']['serverip'].get(str)
rconport = config['minecraft']['rconport'].get(int)
rconpass = config['minecraft']['rconpass'].get(str)
rulemsg = config['messages']['rulemsg'].get(str)

# --FUNCTIONS & CLASSES--   

def log(msg: str):
    time = datetime.now(timezone('Europe/Amsterdam')).strftime("> [%d.%m. - %H:%M] | ")
    print(time + msg)

def saverating(stars: int, userid: int):
    r = open('data/ratings.json')
    rlist = json.load(r)
    for a in range(len(rlist["ratings"])):
        if int(userid) == rlist["ratings"][a]["userid"]:
            rlist["ratings"][a]["stars"] = int(stars)
            rlist["ratings"][a]["time"] = int(time.time())
            rlist["ratings"][a]["improv"] = "K. A."
            with open('data/ratings.json', 'w') as json_file:
                json.dump(rlist,
                        json_file,
                        indent=4,
                       separators=(',', ': '))
            return "OK"
            break
        else:
            pass
        rlist["ratings"].append({
            "userid": int(userid),
            "stars": int(stars),
            "improv": "K. A.",
            "time": int(time.time())
        })
        #print(rlist)
        r.close()
        with open('data/ratings.json', 'w') as json_file:
            json.dump(rlist, json_file, indent=4, separators=(',', ': '))
        return "OK"

def saveimprov(improv: str, userid: int):
    rlist = json.load(open('data/ratings.json'))
    for a in range(len(rlist["ratings"])):
        if int(userid) == rlist["ratings"][a]["userid"]:
            rlist["ratings"][a]["improv"] = str(improv)
            rlist["ratings"][a]["time"] = int(time.time())
            with open('data/ratings.json', 'w') as json_file:
                json.dump(rlist,
                            json_file,
                            indent=4,
                            separators=(',', ': '))
            return "OK"
            break
        else:
            pass
    rlist["ratings"][i]["gratings"].append({
        "userid": int(userid),
        "impro": str(impro),
        "time": int(time.time())
    })
    print(rlist)
    with open('data/ratings.json', 'w') as json_file:
        json.dump(rlist, json_file, indent=4, separators=(',', ': '))

# --START--

print('\033[31m', end='')
print(f"""
> ------------------------------------------------------------
>                     _           _     _           
>     /\             | |         (_)   | |          
>    /  \   _ __   __| |_ __ ___  _  __| | _____  __
>   / /\ \ | '_ \ / _` | '__/ _ \| |/ _` |/ _ \ \/ /
>  / ____ \| | | | (_| | | | (_) | | (_| | (_) >  < 
> /_/    \_\_| |_|\__,_|_|  \___/|_|\__,_|\___/_/\_\ v{clientver}
>                                           (C) TwizZ
> ------------------------------------------------------------                                              
""")
print('> Log:')
# --- OLD AUTH ---

# ---- REMOVED UPDATE PART ----

# --LOOPS--

@tasks.loop(minutes=5)
async def autoreloadstatistics():
    cha = bot.get_channel(statch) # Fetch stat channel
    mes = await cha.fetch_message(statmsg) # Fetch stat message
    await mes.edit(content=f":arrows_clockwise: Daten werden automatisch neugeladen... Bitte warten!", view=reloadstatv())
    r = open('data/ratings.json') #requests.get(f'{apiurl}/bot/rate/get', params={'guildid': guildid}, headers={"Authentication": authkey})  fetch ratings
    data = json.load(r) # Parse Ratings
    starlist = []
    for i in range(len(data["ratings"])):
        starlist.append(int(data["ratings"][i]["stars"]))
        user1 = bot.get_user(int(data["ratings"][i]["userid"]))
        star = int(data["ratings"][i]["stars"])
    stars = statistics.mean(starlist) # fetch 
    embed=discord.Embed(title="Bewertungen", description=f"**Ø = {str(round(stars, 1))} {'Stern' if stars == 1 else 'Sterne'}**", color=0xff0000)
    embed.set_author(name="Androidox", icon_url="https://cdn.discordapp.com/avatars/816223701124382740/c9dc033ac24b88a0a710233ef22deed4.png?size=256")
    for i in range(len(data["ratings"])):
        starlist.append(int(data["ratings"][i]["stars"]))
        user1 = bot.get_user(int(data["ratings"][i]["userid"]))
        star = int(data["ratings"][i]["stars"])
        improv = str(data["ratings"][i]["improv"])
        solved = 0
        if star < 5:
            embed.add_field(name=f'{user1.name} - <t:{str(data["ratings"][i]["time"])}>', value=f'{str(star)} {"Stern" if star == 1 else "Sterne"}', inline=False)
            embed.add_field(name=f'Feedback von {user1.name} {"✅" if solved == 1 else "❌"}', value=f'{improv}', inline=True)
        else:
            embed.add_field(name=f'{user1.name} - <t:{str(data["ratings"][i]["time"])}>', value=f'{str(star)} {"Stern" if star == 1 else "Sterne"}', inline=False)
    nexttitme = getattr(autoreloadstatistics,'next_iteration')
    await mes.edit(content=f":arrows_clockwise: letztes Update: <t:{int(time.time())}>\n:envelope_with_arrow: nächstes Update: <t:{int(nexttitme.timestamp())}>", embed=embed, view=reloadstatv())
    r.close()

# --EVENTS--

@bot.event
async def on_ready(): # print message when bot is ready
    bot.add_view(acceptview())
    bot.add_view(rateview())
    bot.add_view(reloadstatv())
    #bot.add_view(rulespage())
    autoreloadstatistics.start()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="mit Bier!"), status=discord.Status.dnd) # change bot status
    log("Bot gestartet!")
    log(f'Discord.py/Pycord Version: {discord.__version__}')
    log(f'Systemzeit: {datetime.now().strftime("%d.%m.%Y / %H:%M")}')

@bot.event
async def on_member_join(member):
    userid = member.id 
    avurl = None
    if member.avatar.url != None:
        avurl = member.avatar.url
    else:
        avurl = "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg"
    channel1 =  bot.get_channel(int(welcomech)) # Welcome Channel
    embed =     discord.Embed(title=f"Hey {member.display_name}!", description="Da Du ja neu in der Anstalt bist, bist du erstmal ein Jedermann. Lies dir gerne mal die <#805410870028009482> durch.\n\nbis dann mein Gutster", color=discord.Color.green())
    embed.set_footer(text="~ Die Server Leitung")
    embed.set_thumbnail(url=str(member.avatar.url))
    await channel1.send(embed=embed)
    log(f'{member.display_name} ist dem Server beigetreten')
    if int(loglevel) == 1:
        channel = bot.get_channel(int(logch))
        await channel.send(f'> {member.display_name} ist dem Server beigetreten')


@bot.event
async def on_member_remove(member):
    channel =   bot.get_channel(int(welcomech))
    embed =     discord.Embed(title=f"Auf wiedersehen {member.display_name}!", description="wir werden dich vermissen :(", color=discord.Color.red())
    embed.set_footer(text="~ Die Server Leitung")
    if member.avatar.url != None:
        embed.set_thumbnail(url=str(member.avatar.url))
    else:
        pass
    await channel.send(embed=embed)
    log(f'> {member.display_name} left')
    if int(loglevel) == 1:
        channel = bot.get_channel(int(logch))
        await channel.send(f'> {member.display_name} hat den Server verlassen!') 

# --COMMANDS--
    
@bot.slash_command(guild_ids=[int(guildid)], description="Gibt Informationen über einen User auf dem Server aus.")
async def userinfo(ctx, user: discord.Member):
    member = user or ctx.author
    e = discord.Embed()
    e.set_author(name=user.name, icon_url=str(member.default_avatar.url))
    e.set_thumbnail(url=str(member.avatar.url))
    e.add_field(name="User ID", value=user.id, inline=False)
    e.add_field(name="Server beitritt", value=discord.utils.format_dt(member.joined_at, "F"), inline=True)
    e.add_field(name="Account erstellt", value=discord.utils.format_dt(user.created_at, "F"), inline=True)
    e.add_field(name="höchste Rolle", value=member.top_role, inline=True)
    colour = user.color
    if colour.value:
        e.colour = member.colour
    if isinstance(user, discord.User):
        e.set_footer(text="Dieser User ist nicht auf dem Server!")
    await ctx.respond(embed=e, ephemeral=True)

@bot.slash_command(description="Gibt die Latenz zum Bot zurück")
async def ping(ctx):
    await ctx.respond(f'Latenz: `{str(bot.latency)}ms`', ephemeral=True)

# --MINECRAFT COMMANDS--
minecraft = discord.SlashCommandGroup("minecraft", "Commands, die sich auf den MC Server beziehen", default_member_permissions=discord.Permissions(kick_members=True))

@minecraft.command(guild_ids=[int(guildid)], description="Fügt einen User zur Liste der berechtigten Spieler hinzu.")
async def adduser(ctx, user: discord.User, mcname: discord.Option(str)):
    list = json.load(open('userlist.json'))

    for i in range(len(list["users"])):
        userid = list['users'][i]['id']
        if int(user.id) == int(userid):
            await ctx.respond('Spieler ist bereits auf der Liste!', ephemeral=True)
            break
    else:
        list['users'].append(
            {
                "id": str(user.id),
                "name": mcname
            }
        )
        with open('userlist.json', 'w') as json_file:
            json.dump(list, json_file, indent=4, separators=(',',': '))
        await ctx.respond('Spieler hinzugefügt!', ephemeral=True)

# --ADMIN COMMANDS--
admin = discord.SlashCommandGroup("admin", "Commands nur für Server Admins (Verwaltung)", default_member_permissions=discord.Permissions(administrator=True))

@admin.command(guild_ids=[int(guildid)], description="Sendet den Akzeptieren button in einen Eingestellten Kanal.")
async def sndaccbtn(ctx):
    ch = bot.get_channel(int(rulech))
    await ch.send(rulemsg, view=acceptview())

@admin.command(name="purge", guild_ids=[int(guildid)], description="löscht eine Anzahl an Nachrichten aus dem aktuellen Kanal.")
async def cmd_purge(ctx, anzahl: Option(int, description="Anzahl der zu löschenden Nachrichten.", min_value=2, max_value=1000)):
    channel = ctx.channel
    messages = []
    try:
        async for message in channel.history(limit=anzahl):
                messages.append(message)
        await channel.delete_messages(messages)
        await ctx.respond('{} Nachrichten gelöscht!'.format(str(anzahl)), ephemeral=True)
    except Exception as e:
        await ctx.respond(f'Fehler: {e}', ephemeral=True)

@admin.command(name="last", guild_ids=[int(guildid)], description="Gibt die aktuelle CPU auslastung des Servers zurück.")
async def usage(ctx):
    await ctx.respond(f'CPU Auslastung: `{str(psutil.cpu_percent())}%`', ephemeral=True)

# --MODERATOR COMMANDS--
moderator = discord.SlashCommandGroup("moderator", "Commands nur für Server Moderatoren (Supportteam)", default_member_permissions=discord.Permissions(moderate_members=True))

@moderator.command(name="kick", guild_ids=[int(guildid)], description="Kickt einen Benutzer")
async def cmd_kick(ctx, user: Option(discord.Member, description="Zu kickender Benutzer"), reason: Option(str, description="Grund für den Kick", Required=False)):
    try:
        await user.kick(reason = reason)
        await ctx.respond(f"{user.mention} Erfolgreich gekickt!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Fehler: `{e}`", ephemeral=True)

@moderator.command(name="ban", guild_ids=[int(guildid)], description="Bannt einen Benutzer")
async def cmd_ban(ctx, user: Option(discord.Member, description="Zu bannender Benutzer"), reason: Option(str, description="Grund für den Bann", Required=False)):
    try:
        await user.ban(reason = reason)
        await ctx.respond(f"{user.mention} Erfolgreich gebannt!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Fehler: `{e}`", ephemeral=True)

@moderator.command(name="unban", guild_ids=[int(guildid)], description="Entbannt einen Benutzer")
async def cmd_unban(ctx, user: Option(discord.Member, description="Zu entbannender Benutzer"), reason: Option(str, description="Grund für die Entbannung", Required=False)):
    try:
        await ctx.guild.unban(user, reason = reason)
        await ctx.respond(f"{user.mention} Erfolgreich entbannt!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Fehler: `{e}`", ephemeral=True)

@moderator.command(name="deafen", guild_ids=[int(guildid)], description="Deaft einen Benutzer")
async def cmd_deaf(ctx, user: Option(discord.Member, description="Benutzer")):
    try:
        await user.edit(deafen=True)
        await ctx.respond(f"{user.mention} Erfolgreich gedeaft!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Fehler: `{e}`", ephemeral=True)

@moderator.command(name="undeafen", guild_ids=[int(guildid)], description="Undeaft einen Benutzer")
async def cmd_undeaf(ctx, user: Option(discord.Member, description="Benutzer")):
    try:
        await user.edit(deafen=False)
        await ctx.respond(f"{user.mention} Erfolgreich ungedeaft!", ephemeral=True)
    except Exception as e:
        await ctx.respond(f"Fehler: `{e}`", ephemeral=True)

# --VIEWS--

class reloadstatv(discord.ui.View):
    # Reload stats
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Daten Neuladen", custom_id="reloadvv", row=0, style=discord.ButtonStyle.red, emoji="📨")
    async def reloadvvbtn_callback(self, button, interaction):
        r = open('data/ratings.json')
        data = json.load(r) # Parse Ratings
        cha = bot.get_channel(statch) # Fetch stat channel
        mes = await cha.fetch_message(statmsg) # Fetch stat message
        starlist = []
        for i in range(len(data["ratings"])):
            starlist.append(int(data["ratings"][i]["stars"]))
            user1 = bot.get_user(int(data["ratings"][i]["userid"]))
            star = int(data["ratings"][i]["stars"])
        stars = statistics.mean(starlist) # fetch 
        embed=discord.Embed(title="Bewertungen", description=f"**Ø = {str(round(stars, 1))} {'Stern' if stars == 1 else 'Sterne'}**", color=0xff0000)
        embed.set_author(name="Androidox", icon_url="https://cdn.discordapp.com/avatars/816223701124382740/c9dc033ac24b88a0a710233ef22deed4.png?size=256")
        for i in range(len(data["ratings"])):
            starlist.append(int(data["ratings"][i]["stars"]))
            user1 = bot.get_user(int(data["ratings"][i]["userid"]))
            star = int(data["ratings"][i]["stars"])
            improv = str(data["ratings"][i]["improv"])
            solved = 0
            if star < 5:
                embed.add_field(name=f'{user1.name} - <t:{str(data["ratings"][i]["time"])}>', value=f'{str(star)} {"Stern" if star == 1 else "Sterne"}', inline=False)
                embed.add_field(name=f'Feedback von {user1.name} {"✅" if solved == 1 else "❌"}', value=f'{improv}', inline=True)
            else:
                embed.add_field(name=f'{user1.name} - <t:{str(data["ratings"][i]["time"])}>', value=f'{str(star)} {"Stern" if star == 1 else "Sterne"}', inline=False)
        
        nexttitme = getattr(autoreloadstatistics,'next_iteration')
        await mes.edit(content=f":arrows_clockwise: letztes Update: <t:{int(time.time())}>\n:envelope_with_arrow: nächstes Update: <t:{int(nexttitme.timestamp())}>", embed=embed, view=reloadstatv())
        await interaction.response.send_message(":ballot_box_with_check: erfolgreich Neugeladen!", ephemeral=True)
        r.close()

class acceptview(discord.ui.View):
    # accept button
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Regeln akzeptieren",  custom_id="accbtn", row=0, style=discord.ButtonStyle.success, emoji="✔") 
    async def button_callback(self, button, interaction):
        if discord.utils.find(lambda r: r.id == int(acceptrole), interaction.user.guild.roles) not in interaction.user.roles:
            role = discord.utils.get(interaction.user.guild.roles, id=int(acceptrole))
            await interaction.user.add_roles(role)
            embed=discord.Embed(title=f"Willkommen in der Gaminganstalt!, {interaction.user.name}#{interaction.user.discriminator}!", color=0x359dcf)
            embed.set_footer(text="~ Die Server Leitung")
            dmch = await interaction.user.create_dm()
            await bot.get_channel(dmch.id).send(embed=embed)
            await interaction.response.send_message("Du hast die Regeln erfolgreich akzeptiert!", ephemeral=True)
        else:
            await interaction.response.send_message("Du hast die Regeln bereits akzeptiert!", ephemeral=True)

class rateview(discord.ui.View):
    # Rate View
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="1 Stern", custom_id="1_star", row=0, style=discord.ButtonStyle.red, emoji="⭐")
    async def onebutton_callback(self, button, interaction):
        saverating(1, interaction.user.id)
        await interaction.response.send_modal(improvmodal(title="Was können Wir verbessern?"))

    @discord.ui.button(label="2 Sterne", custom_id="2_stars", row=0, style=discord.ButtonStyle.red, emoji="⭐")
    async def twobutton_callback(self, button, interaction):
        saverating(2, interaction.user.id)
        await interaction.response.send_modal(improvmodal(title="Was können Wir verbessern?"))
    
    @discord.ui.button(label="3 Sterne", custom_id="3_stars", row=0, style=discord.ButtonStyle.primary, emoji="⭐")
    async def threebutton_callback(self, button, interaction):
        saverating(3, interaction.user.id)
        await interaction.response.send_modal(improvmodal(title="Was können Wir verbessern?"))
    
    @discord.ui.button(label="4 Sterne", custom_id="4_stars", row=0, style=discord.ButtonStyle.primary, emoji="⭐")
    async def fourbutton_callback(self, button, interaction):
        saverating(4, interaction.user.id)
        await interaction.response.send_modal(improvmodal(title="Was können Wir verbessern?"))
    
    @discord.ui.button(label="5 Sterne", custom_id="5_stars", row=0, style=discord.ButtonStyle.green, emoji="⭐")
    async def fivebutton_callback(self, button, interaction):
        saverating(5, interaction.user.id)
        await interaction.response.send_message("OK 5 Sterne", ephemeral=True)

class improvmodal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Was können wir verbessern?", min_length=4, max_length=1000, style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        saveimprov(improv=self.children[0].value, userid=interaction.user.id)
        await interaction.response.send_message("Vielen Dank für dein Feedback!", ephemeral=True)

bot.add_application_command(minecraft)
bot.add_application_command(admin)
bot.add_application_command(moderator)
bot.run(bottoken)
