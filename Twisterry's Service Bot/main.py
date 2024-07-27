# Twisterry Service Bot (TWS)
# (C) 2020-2022 TwizZ

import discord, asyncpraw, os, asyncio, aiohttp, firebase_admin, json, secrets, psutil, time, random, ast # Import required libraries
import datetime as dt
from itertools import cycle # Import required libraries
from datetime import date, datetime
from discord.ext import tasks, commands
from discord import Interaction, option, Webhook
from discord.commands import Option, ApplicationContext
from dotenv import load_dotenv
from firebase_admin import db
from uuid import uuid4

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all()) # define bot variable
status = cycle(['Twisterry', 'Service', 'Rewritten!', 'v1.0b2', '!11elf', 'Moin!', ':-)', ':--)']) # Status Messages

# define Software Releasetype
releastype = "debug"

# bot token
load_dotenv()
token = os.getenv('token')

#Time for log
logtime = datetime.now().strftime("(%d.%m.%Y | %H:%M:%S)")

#Define Reddit instance
reddit = asyncpraw.Reddit(
                    client_id='t7B3_JergOYNkRVlk8H4cQ',
                    client_secret='FoieH8P88fp6kCSkLosNIkCqzqXOTA',
                    user_agent='Twisterry Service Bot (TWS) by /u/Twisterry'
)

# Firebase init
print('> Database init...')
cred_object = firebase_admin.credentials.Certificate('ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred_object, {
	'databaseURL':'https://tw-cloud-40bab-default-rtdb.europe-west1.firebasedatabase.app'
	})
ref = db.reference("/")
print('> Init done! starting bot...')

#Status Loop
@tasks.loop(seconds=5)
async def change_status():
    await bot.change_presence(
                            activity=discord.Activity(type=discord.ActivityType.playing, name=next(status)),
                            status=discord.Status.online
    )

# Generate Meme list
all_subs = []
async def gen_memes():
    ref = db.reference("/memelist")
    print('> checking for memes in database...')
    dbans = json.loads(ref.get())
    all_subs = []
    listdate = datetime.fromtimestamp(int(dbans["timestamp"]))
    curdate = datetime.fromtimestamp(int(time.time()))
    difference = curdate - listdate
    difmin = int(difference.seconds / 60)
    if difmin >= 1:
        print('> List too old! generating new one...')
        print('> Generating new memes...')
        subreddit = await reddit.subreddit("memes")
        top = subreddit.top(limit = 50)
        count = 0
        async for submission in top:
            count = count +1
            print(f'> Submission: {str(count)} of 100')
            all_subs.append(submission)
        print('> done!')
        data = {
            "list": str(all_subs),
            "timestamp": str(int(time.time())) 
            }
        ref.set(json.dumps(data))
        print(all_subs)
    else:
        print('> DB List OK!')
        lis = dbans["list"]
        res = lis.strip('][').split(', ')
        print(res)
        print(type(lis))
        print(type(res))
        all_subs = res
        print(type(all_subs))


# --EVENTS--

# do this when bot is ready
@bot.event
async def on_ready():
    await gen_memes()
    print('> |----------|')  
    print('> TW Service Bot')
    print(f'> Discord.py/Pycord Version: {discord.__version__}')
    print(f'> Systemzeit: {datetime.now().strftime("%d.%m.%Y / %H:%M")}')
    print('> Bot gestartet, eingeloggt als:')
    print('> '+bot.user.name)
    print('> '+str(bot.user.id))
    print('> (c)2022/Q2 TwizZ')
    print('> |----------|')
    change_status.start()
    bot.add_view(verifyview())
    bot.add_view(roleview())
    bot.add_view(unbanview())

# do this when user joins
@bot.event
async def on_member_join(member):
    logtime = datetime.now().strftime("(%d.%m.%Y | %H:%M:%S)")
    userid = member.id 
    print(f'> {logtime}: {member.name} joined')
    await member.add_roles(
        discord.utils.get(member.guild.roles, id=723644192479379506), # 'Einsteiger' Role
        discord.utils.get(member.guild.roles, id=938778087783559198), # Category 1 Role
        discord.utils.get(member.guild.roles, id=938778303983128617), # Category 2 Role
        discord.utils.get(member.guild.roles, id=938778367426174986)  # Category 3 Role
    )
    channel1 = bot.get_channel(830549724355362887)
    channel2 = bot.get_channel(862934794500702209)
    embed=discord.Embed(title=f"Willkommen {member.name}#{member.discriminator}!", description="Herzlich Willkommen auf Twisterry's / TwiZZ' World!", color=0x1a78d7)
    embed.set_footer(text="~ Die Server Leitung")
    embed.set_thumbnail(url=str(member.avatar.url))
    await channel1.send(embed=embed)

# do this when user lefts
@bot.event
async def on_member_remove(member):
    logtime = datetime.now().strftime("(%d.%m.%Y | %H:%M:%S)")
    print(f'> {logtime}: {member.name} left')
    channel = bot.get_channel(830549724355362887)
    embed=discord.Embed(title=f"Auf wiedershen {member.name}#{member.discriminator}!", description="Schade, dass du uns verlassen hast :(", color=0xff0000)
    embed.set_footer(text="~ Die Server Leitung")
    await channel.send(embed=embed)

# do this when message was sent
@bot.event
async def on_message(message):
    if message.channel.id == 938047810979369010 and not message.content == "<@&963536268355043339>":
        time.sleep(3)
        print(f'> {logtime}: New message in #3rd-party-news!')
        await bot.get_channel(938047810979369010).send('<@&963536268355043339>')

# --COMMANDS--

# simple send command (sends message in specific channel)
@bot.slash_command(description="Sendet eine Nachricht in einen Kanal")
@discord.default_permissions(send_messages=True)
@option(
    "channel",
    discord.TextChannel,
    # you can specify allowed channel types by passing a list of them like this
    description="Waehle einen Kanal aus.",
)
@option("text", description="Nachricht")
async def send(ctx, channel: discord.TextChannel, *, text: str):
    await channel.send(text)
    await ctx.response("Okay", ephemeral=True)

# warn any user
@bot.slash_command(description="Verwarnt einen Benutzer")
@discord.default_permissions(kick_members=True)
@option(
    "user",
    discord.Member,
    description="Wähle einen User aus."
)
async def warn(ctx, user: discord.Member, *, reason):
   member = ctx.author
   channel = bot.get_channel(806220474279002144)
   await channel.send(f'{user.mention} wurde von {member.mention} verwarnt!\n**Grund:** *{reason}*')
   await ctx.response('OK!', ephemeral=True)

# clear messages in specific channel
@bot.slash_command(description="löscht eine Anzahl an Nachrichten in einem Kanal")
@discord.default_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=amount):
              messages.append(message)
    await channel.delete_messages(messages)
    await ctx.respond('{} Nachrichten gelöscht!'.format(amount), ephemeral=True)

# Gives information about any user
@bot.slash_command(description="Gibt Informationen über einen Benutezr aus.")
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

# Opens the Bug report form
@bot.slash_command(description="Öffnet das Formular um einen Bug im Bot zu melden.")
async def bugreport(ctx):
    await ctx.send_modal(Bugreport())

# Unban Form
@bot.slash_command(description="Öffnet das Entbannungsformular (Minecraft Server)")
async def entbannung(ctx):
    await ctx.send_modal(Unbanform())

# Meme command
@bot.slash_command(description="sendet ein meme aus r/memes")
async def meme(ctx):
    subreddit = await reddit.subreddit('memes')
    #print(len(all_subs))
    random_sub = random.choice(all_subs)
    all_subs.remove(random_sub)
    posttime = random_sub.created_utc
    embed = discord.Embed(title=random_sub.title)
    embed.set_image(url=random_sub.url)
    embed.set_footer(text=f'gepostet von {random_sub.author} in r/{random_sub.subreddit} am {datetime.utcfromtimestamp(posttime).strftime("%d.%m.%Y um %H:%M:%S")}')
    await ctx.respond(embed=embed)
    if len(all_subs) <= 20:
        await gen_memes()

# Ping command
@bot.slash_command(description="Gibt die Latenz zum Bot zurück")
async def ping(ctx):
    await ctx.respond(f'Latenz: `{str(bot.latency)}ms`', ephemeral=True)

# -- 'Admin' COMMANDS --
admin = discord.SlashCommandGroup("admin", "Commands nur für den Owner & Admins", default_member_permissions=discord.Permissions(administrator=True))

# Send Verify Button message
@admin.command()
async def sndverbtn(ctx):
    ch = bot.get_channel(862934794500702209)
    await ch.send('**Bitte klicke auf "verifizieren", um vollen Zugriff auf den Server zu erhalten.**', view=verifyview())

# Send Roll select message
@admin.command()
async def sndrolsel(ctx):
    ch = bot.get_channel(880765047050231858)
    embed=discord.Embed(title="Rollen Übersicht", description="Übersicht über alle zugänglichen Rollen (Kategorie Rollen ausgenommen)", color=0x359dcf)
    embed.add_field(name=discord.utils.get(ctx.guild.roles, id=938782986160197642).mention, value="Verwaltung aller Rollen (Nur für Bots!)", inline=False)
    embed.add_field(name="<@&723643996643262484>", value="Besitzer / Co-besitzer des Servers", inline=False)
    embed.add_field(name="<@&799061825521057822>", value="Administratoren des Servers", inline=False)
    embed.add_field(name="<@&799062210756083753>", value="Moderatoren des Servers", inline=False)
    embed.add_field(name="<@&723646091672944721>", value="Bots", inline=False)
    embed.add_field(name="<@&734068510501896234>", value="Software Entwickler", inline=False)
    embed.add_field(name="<@&790627932136800308>", value="Langzeit Mitglieder", inline=False)
    embed.add_field(name="<@&856172382573166623>", value="Server Booster", inline=False)
    embed.add_field(name="<@&734422323796639854>", value="Beantworten Support Tickets & Entbannungsanträge", inline=False)
    embed.add_field(name="<@&723644192479379506>", value="Standard Mitglied des Servers", inline=False)
    embed.add_field(name="<@&829006483931791391>", value="Zeitbasiert für unangemessenes Verhalten innerhalb des Servers", inline=False)
    embed.add_field(name="<@&785947329161068616>", value="Verifizierter Benutzer", inline=False)
    await ch.send(embed=embed, view=roleview())

# Send Rules in Rule Channel
@admin.command()
async def sndrul(ctx):
    embed=discord.Embed(title="Regeln", description="Regelwerk der Twisterry's World", color=0x359dcf)
    embed.set_author(name="⋉TwizZ⋊#5536", icon_url="https://cdn.discordapp.com/avatars/606485611221876746/9d92f810fb87345b5b56b41d23f6c677.png?size=1024")
    embed.add_field(name="(1) Namensgebung", value="Nicknames/Usernames dürfen keine beleidigenden, verletzende , verbotene oder geschützte Inhalte enthalten.", inline=False)
    embed.add_field(name="(1.1) Avatar", value="Avatare dürfen keine pornographischen, rassistischen, verbotene oder beleidigende Inhalte aufweisen.", inline=False)
    embed.add_field(name="(2) Umgangston", value="Der Umgang mit anderen Usern sollte stets freundlich erfolgen. Verbale Angriffe gegen andere User sind Verboten.", inline=False)
    embed.add_field(name="(2.1) Gespräche aufnehmen", value="Das Mitschneiden oder Mithören ist auf dem gesamten Server ausnahmslos untersagt.", inline=False)
    embed.add_field(name="(3) Kicken/Bannen", value="Ein Kick oder ein Bann ist zu keinem Zeitpunkt unangebracht. Wenn der Verdacht eines Unrechtmäßigen Kicks/Banns im Raume steht, sollte bei einem Admin oder Mod oder [hier](https://twonline.ml/beschwerde) beschwerde Eingelegt werden.", inline=False)
    embed.add_field(name="(3.1) Direktionsrecht", value="Den Anweisungen einer befugten Person ist zu folgen.", inline=False)
    embed.add_field(name="(3.2) Server-Rechte", value="Rechte in form von Rollen werden nicht Wahrlos vergeben, sie gelten immer einem bestimmten Grund. Bei Bedarf an Rechten wende dich an einen Admin oder klicke [hier](https://twonline.ml/rechte).", inline=True)
    embed.add_field(name="(4) Werbung", value="Jegliche Art von Werbung ist auf diesem Server Untersagt. Dazu zählen Auch Live Übertragungen mit eingeblendeten Werbebildern in Sprachkanälen.", inline=False)
    embed.add_field(name="(4.1) Datenschutz", value="Es ist strikt Untersagt eigene Private Informationen in öffentlichen Kanälen auszutauschen oder ggf. pers. Daten anderer Personen Weiterzugeben.", inline=False)
    embed.add_field(name="(5) Meldepflicht", value="Die Regeln müssen von allen Benutzern beachtet werden. Sollte ein Regelverstoß eines Benutzers erkannt werden, so ist dieser umgehend zu melden. Weitere Infos [hier](https://twonline.ml/melden)", inline=True)
    embed.add_field(name="Bei einem Verstoß der oben genannten Regeln ist mit einem Timeout, kick oder Bann zu rechnen.", value="‎", inline=False)
    embed.add_field(name="‎", value="Dieses Regelwerk tritt ab dem <t:1652997600:f> in Kraft", inline=False)
    embed.set_footer(text="Geschrieben von: ⋉TwizZ⋊#0001 (Administrator)")
    await bot.get_channel(746321406811177020).send(embed=embed)

# CPU Load command
@admin.command()
async def usage(ctx):
    await ctx.respond(f'CPU Auslastung: `{str(psutil.cpu_percent())}%`', ephemeral=True)

# --VIEWS (Buttons & Co.)--

class verifyview(discord.ui.View): # Create a class called View that subclasses discord.ui.View
    # verify button
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="verifizieren",  custom_id="verbtn", row=0, style=discord.ButtonStyle.success, emoji="✔") 
    async def button_callback(self, button, interaction):
        if discord.utils.find(lambda r: r.id == 785947329161068616, interaction.user.guild.roles) not in interaction.user.roles:
            logtime = datetime.now().strftime("(%d.%m.%Y | %H:%M:%S)")
            print(f'> {logtime}: {interaction.user.name} verified')
            role = discord.utils.get(interaction.user.guild.roles, id=785947329161068616)
            await interaction.user.add_roles(role)
            embed=discord.Embed(title=f"Willkommen auf Twisterry's World, {interaction.user.name}#{interaction.user.discriminator}!", description="Deine verifizierung war Erfolgreich!", color=0x359dcf)
            embed.add_field(name="Das Team wünscht dir Viel Spaß", value="hier auf Twisterry's / TwiZZ' World!", inline=True)
            embed.add_field(name="Hier erhältst du Rollen: ", value="gehe in <#880765047050231858> und wähle eine Rollen aus.", inline=True)
            embed.set_footer(text="~ Die Server Leitung")
            dmch = await interaction.user.create_dm()
            await bot.get_channel(dmch.id).send(embed=embed)
            await interaction.response.send_message("Du bist nun verifiziert!", ephemeral=True)
        else:
            await interaction.response.send_message("Du bist bereits verifiziert!", ephemeral=True)
    # Help Button
    @discord.ui.button(label="Hilfe",  custom_id="helpbtn", row=0, style=discord.ButtonStyle.red, emoji="🛠")
    async def help_callback(self, button, interaction):
         await interaction.response.send_modal(Helpform())

class unbanview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    # Accept button
    @discord.ui.button(label="Akzeptieren",  custom_id="accbtn", style=discord.ButtonStyle.success, emoji="✔") 
    async def button_callback(self, button, interaction):
        ref = db.reference("/unbanrequests/" + str(interaction.message.id))
        databseentry = json.loads(ref.get())
        if databseentry['status'] == "denied" or databseentry['status'] == "accepted":
            await interaction.response.send_message("❌ Antrag wurde bereits Akzeptiert bzw. abgelehnt!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Antrag **{databseentry['id']}** erfolgreich Akzeptiert!")
            user = bot.get_user(int(databseentry['user']))
            embed=discord.Embed(title="Entbannungsantrag", description="TW Unban Service", color=0x008000)
            embed.add_field(name="Dein Entbannungsantrag wurde akzeptiert!", value=f"ID: `{databseentry['id']}`", inline=False)
            await user.send(embed=embed)
            if(databseentry['status'] == "undefined"):
                ref.set(json.dumps({"status": "accepted"}))
    # Deny button
    @discord.ui.button(label="Ablehnen",  custom_id="deny", row=0, style=discord.ButtonStyle.red, emoji="❌")
    async def deny_callback(self, button, interaction):
        ref = db.reference("/unbanrequests/" + str(interaction.message.id))
        databseentry = json.loads(ref.get())
        if databseentry['status'] == "denied" or databseentry['status'] == "accepted":
            await interaction.response.send_message("❌ Antrag wurde bereits Akzeptiert bzw. abgelehnt!", ephemeral=True)
        else:
            await interaction.response.send_message(f"Antrag **{databseentry['id']}** erfolgreich abgelehnt")
            user = bot.get_user(int(databseentry['user']))
            embed=discord.Embed(title="Entbannungsantrag", description="TW Unban Service", color=discord.Colour.red())
            embed.add_field(name="Dein Entbannungsantrag wurde abgelehnt!", value=f"ID: `{databseentry['id']}`", inline=False)
            await user.send(embed=embed)
            if(databseentry['status'] == "undefined"):
                ref.set(json.dumps({"status": "denied"}))

class roleview(discord.ui.View):
    # role select menu
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.select(
        placeholder = "Bitte wähle eine oder mehrere Rollen aus!",
        min_values=1,
        max_values=1,
        custom_id = "roleselector",
        options=[
            discord.SelectOption(
                label="Giveaway Ping",
                description="Mit dieser Rolle wirst du bei neuen Giveaways Benarichtigt."
            ),
            discord.SelectOption(
                label="News Ping",
                description="Mit dieser Rolle wirst du bei neuen News Benarichtigt."
            )
        ]
    )
    async def select_callback(self, select, interaction):
        if select.values[0] == "Giveaway Ping":
            roleid = 905518311368962058
        elif select.values[0] == "News Ping":
            roleid = 905520173547651143
        #await interaction.response.send_message(f'Du hast {select.values[0]}({roleid}) gewählt.')

        member = interaction.user
        if discord.utils.find(lambda r: r.id == roleid, member.guild.roles) not in member.roles:
            await member.add_roles(discord.utils.get(member.guild.roles, id=roleid))
            await interaction.response.send_message('Erfolgreich!', ephemeral=True)
        else:
            await member.remove_roles(discord.utils.get(member.guild.roles, id=roleid))
            await interaction.response.send_message('Erfolgreich **entfernt**!', ephemeral=True)

class Bugreport(discord.ui.Modal):
    # Bugreport Form
     def __init__(self) -> None:
        super().__init__(title="Bug Report")

        self.add_item(discord.ui.InputText(label="Kurze Fehlerbeschreibung"))
        self.add_item(discord.ui.InputText(label="Lange Fehlerbeschreibung", style=discord.InputTextStyle.long))

     async def callback(self, interaction: discord.Interaction):
         await interaction.response.send_message("Der Report wurde versendet!", ephemeral=True)
         await bot.get_user(606485611221876746).send(f"Neuer Bugreport von {interaction.user.mention}!\n**Kurze Beschreibung:** *{self.children[0].value}*\n**Lange Beschreibung:** *{self.children[1].value}*")

class Helpform(discord.ui.Modal):
    # Help Form
     def __init__(self) -> None:
        super().__init__(title="Hilfe Formular")

        self.add_item(discord.ui.InputText(label="Anfrage", style=discord.InputTextStyle.long))

     async def callback(self, interaction: discord.Interaction):
         await interaction.response.send_message("Deine Anfrage wurde versendet! Das Team wird sich schnellst möglich um dich kümmern!", ephemeral=True)
         await bot.get_user(606485611221876746).send(f"{interaction.user.mention} benötigt hilfe!\nNachricht: `{self.children[0].value}`")

class Unbanform(discord.ui.Modal):
    # Unban Form
     def __init__(self) -> None:
        super().__init__(title="MC-Entbannungs Formular")

        self.add_item(discord.ui.InputText(label="Grund des Bannes", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Minecraft Name", style=discord.InputTextStyle.short))
        self.add_item(discord.ui.InputText(label="Weitere Details", style=discord.InputTextStyle.long, required=False))

     async def callback(self, interaction: discord.Interaction):
         try:
             if self.children[2].value == None or self.children[2].value == "":
                 more = "Keine Angabe."
             else:
                 more = self.children[2].value
             ch = bot.get_channel(827683585544290324)
             unbanid = uuid4()
             webhook = await ch.create_webhook(name="Test")
             embed=discord.Embed(title="Entbannungs Antrag", description="unban application", color=0x0080ff)
             embed.add_field(name="Grund des Bannes", value=self.children[0].value, inline=True)
             embed.add_field(name="Minecraft Name", value=self.children[1].value, inline=True)
             embed.add_field(name="Discord Name", value=interaction.user.mention, inline=True)
             embed.add_field(name="Weitere Details", value=more, inline=False)
             embed.set_footer(text="Request ID: " + str(unbanid))
             msg = await webhook.send(embed=embed, view=unbanview(), username="Entbannungs Antrag", wait=True) # Executing webhook.
             await webhook.delete()
             
             data = {
                    "id": str(unbanid), 
                    "user": str(interaction.user.id), 
                    "reason": self.children[0].value, 
                    "mcname": self.children[1].value, 
                    "info": more,
                    "msgid": str(msg.id),
                    "status": "undefined"
                }
             ref = db.reference('/unbanrequests/' + str(msg.id))
             ref.set(json.dumps(data))
         except Exception as e:
            await interaction.response.send_message(f"Error: `{e}`", ephemeral=True)
         await interaction.response.send_message("Deine Anfrage wurde versendet! Das Team wird sich schnellst möglich um den Antrag kümmern!", ephemeral=True)

#add 'admin' group
bot.add_application_command(admin)

bot.run(token)