# MoBot made by Mo#9991

'''
ISSUES: 
  get rid of 'priming temp storage' on_ready()
    UPDATE COLLECTIONS
  yeet MoBotServers.txt, get that shit in the database

FUTURE UPDATES:
  Upon updating MoBot Help
    check deleteMessages() in General Commands
'''

import discord
import asyncio
from datetime import datetime, timedelta
import random
from pytz import timezone
import traceback
import gspread
import mysql.connector

import SecretStuff

# importing server specific files
import GrottiF1
import COTM
import COTMPS4
import IG
import FortKnight
import GTACCHub
import CreatorChallenge
import XB1WEC
import Noble2sLeague
import NobleGaming
import NobleHub
import AOR
import TEPCOTT
import GRG
import Imperial
import ReapersMC

# importing external functions files
import GTAVRaces
import GTAVehicles
import GTAWeather
import XboxGamertags
import watchWords
#import tTeams // no longer supported
import MessageScheduler
import ticketManager
import DiscordSheets
import ClocksAndCountdowns
import RLScrims
import ReactionRole
import CollectionsOLD
import Collections
import Reservations
import MoBotTimeZones
import RLRanks
import AdminFunctions
import EventScheduler
import SimpleCommands
import MoBotDatabase
import GeneralCommands
import RandomSupport
import MoBotTables

import Hangman
import DKGetPicks

intents = discord.Intents.all()
client = discord.Client(intents = intents)

servers = {} # server files and ids are recieved in on_ready() after database connection  
moBotDB = None # connection is on_ready()

# guilds
cotm = 527156310366486529
moBotSupport = 467239192007671818
noble2sLeauge = 437936224402014208

# channels
botSpam = 593911201658961942

# users
moBot = 449247895858970624
mo = 405944496665133058
nosv1 = 475325629688971274
potterman = 209584832030834688

spaceChar = "⠀"

# question words -- who what when where why how will can are am 
yesNoQuestionResponses = [
  ["yes", [
    "Sure, why not?",
    "Do I need a dollar? ||hint - @MoBot#0697 donate :sunglasses:||", 
    ]
  ],
  ["no", [
    "Not a chance, lol", 
    ]
  ],
  ["maybe", [
    "Hell if I know...", 
    "Perhaps...", 
    ]
  ],
]

questionWords = {
  "will" : yesNoQuestionResponses,
  "can" : yesNoQuestionResponses,
  "are" : yesNoQuestionResponses,
  "am" : yesNoQuestionResponses,
  "is" : yesNoQuestionResponses,
  "do" : yesNoQuestionResponses,
  "would" : yesNoQuestionResponses,
}

 # updated upon connectivity of MoBot
reactionMessages = {}
autoRoles = {} 
isConnected = False

clock_check = datetime.utcnow()

class UserPerms:
  def __init__(self, administrator, manageMessages, manageRoles, manageChannels, changeNicknames, addReactions):
    self.administrator = administrator
    self.manageMessages = manageMessages
    self.manageRoles = manageRoles
    self.manageChannels = manageChannels
    self.changeNicknames = changeNicknames
    self.addReactions = addReactions
# end UserPerms

@client.event
async def on_ready():
  print("MoBot is online - " + str(datetime.now()))

  global autoRoles
  autoRoles = await ReactionRole.updateAutoRoles(autoRoles, await ReactionRole.openReactionRoleSpreadsheet())
  print("AutoRoles Received")
  
  global moBotDB
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  print("Connected to MoBot Database")
  getServers()
  
  # priming the temp storage
  msg = await client.get_user(nosv1).send(".")
  await msg.delete()
  
  mobotLog = client.get_guild(moBotSupport).get_channel(604099911251787776) # mobot log
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Restarted")
  await mobotLog.send(embed=embed)
  
  global isConnected
  isConnected = True
# end on_ready

@client.event
async def on_raw_message_edit(payload):
  pd = payload.data
  message = await client.get_channel(int(pd["channel_id"])).fetch_message(int(pd["id"]))
  
  if (not message.author.bot and isConnected):
    try:
      pd["content"]
      await on_message(message)
    except KeyError: # when content was not updated
      pass
# end on_raw_message_edit

@client.event
async def on_message(message):
  if (not isConnected): # don't check messages unless on_ready() is done
    return

  try:
    message.content = message.content.translate({ord(c) : '"' for c in ['“', '”']})
    mc = message.content.translate({ord(c) : " " for c in ["\n", "\t", "\r"]}) # that was beautiful
    while ("  " in mc):
      mc = mc.replace("  ", " ")
    args = mc.split(" ")
    
    logActionToConsole(message, message.author, "message")

    if (moBot != message.author.id):
      if ((message.author.id == potterman or message.author.id == mo) and "beep" in args): # if potterman says beep...
        await message.channel.send("boop")

      try:
        authorPerms = message.channel.permissions_for(message.author)
        isBotSpam = message.channel.id == botSpam
        isMo = message.author.id == mo
        isNos = message.author.id == nosv1
        authorPerms = UserPerms(
          isNos or isMo or authorPerms.administrator,
          isNos or isMo or authorPerms.manage_messages or isBotSpam,
          isNos or isMo or authorPerms.manage_roles or isBotSpam,
          isNos or isMo or authorPerms.manage_channels or isBotSpam,
          isNos or isMo or authorPerms.change_nickname or isBotSpam,
          isNos or isMo or authorPerms.add_reactions or isBotSpam,
        )
      except AttributeError: # user has no perms
        authorPerms = None

      if (str(moBot) in args[0]):
        if (len(args) == 1):
          await message.channel.send(":eyes: Use `@MoBot#0697 help` for help...")

        # --- SPECALIZED COMMANDS ---
        elif ("table" in args[1] and authorPerms.manageMessages):
          await MoBotTables.main(args, message, client)
        elif ("ticket" in args[1]):
          await ticketManager.main(args, message, client)
        elif ("schedule message" in mc):
            await MessageScheduler.main(args, message, client)
        elif (args[1] in ["countdown", "clock"] and authorPerms.manageMessages):
          await ClocksAndCountdowns.main(args, message, client)
        elif ("scrims" in args[1]):
          await RLScrims.main(args, message, client)
        elif ("watch" in args[1] and authorPerms.manageRoles):
          await ReactionRole.addReactionRoleMessage(message, args)
        elif ("autorole" in args[1] and authorPerms.manageRoles):
          global autoRoles
          if (args[2] == "add"):
            autoRoles = await ReactionRole.addAutoRole(message, autoRoles)
          elif (args[2] == "clear"):
            autoRoles = await ReactionRole.clearAutoRole(message, autoRoles)
        elif ("collection" in args[1]):
          await Collections.main(args, message, client)
        elif ("reservation" in args[1]):
          await Reservations.main(args, message, client)
        elif ("tz" in args[1]):
          await MoBotTimeZones.main(args, message, client)
        elif ("rlrank" in args[1]):
          await RLRanks.main(args, message, client)
        elif ("remindme" in args[1]):
          await EventScheduler.setReminder(message)
        elif ("commands" in args[1]):
          await SimpleCommands.main(args, message, client)
        elif (len(args) >= 3 and "command" in args[2]):
          if (authorPerms.manageMessages):
            await SimpleCommands.main(args, message, client)
          else:
            await message.channel.send("**Not Enough Permissions**\nMust have Manage Message permisisons to create/edit/delete MoBot Custom Commands.")

        # --- GENERAL USE COMMANDS --- 
        elif ("say" in args[1] and authorPerms.manageMessages):
          if ("embed" in args[2]):
            await GeneralCommands.sayEmbed(message, args, False)
          else:
            try:
              await message.delete()
            except discord.errors.Forbidden:
              pass
            await message.channel.send(message.content[26:])
        elif ("edit" in args[1] and authorPerms.manageMessages):
          if ("embed" in args[2]):
            await GeneralCommands.sayEmbed(message, args, True)
          else:
            await GeneralCommands.editMessage(message, args)
        elif ("channel" in args[1] and authorPerms.manageChannels):
          channel = message.guild.get_channel(int(args[2]))
          await channel.edit(name=message.content.split(str(channel.id))[1].strip())
          try:
            await message.delete()
          except discord.errors.Forbidden:
            pass
        elif ("monick" in args[1] and isMo):
          await message.guild.get_member(moBot).edit(nick=message.content.split(args[1])[1].strip())
        elif ("add" in args[1]):
          if ("reaction" in args[2] and authorPerms.addReactions):
            if (len(args) > 2):
              try:
                await message.delete()
              except discord.errors.Forbidden:
                pass
              await ReactionRole.addReactionToMessage(await message.channel.fetch_message(int(args[-1])), args[3:-1])
        elif ("nick" in args[1] and authorPerms.changeNicknames):
          if (message.guild.id == noble2sLeauge):
            await Noble2sLeague.setnick(message)
          else:
            await message.author.edit(nick=message.content.split("nick")[1].strip())
            try:
              await message.delete()
            except discord.errors.Forbidden:
              pass
        elif ("clear" in args[1] and authorPerms.manageMessages):
          await GeneralCommands.clearMessages(message, args)
        elif ("delete" in args[1]):
          if "category" in args[2] and authorPerms.manageChannels:
            await GeneralCommands.deleteCategory(message, args)
          elif authorPerms.manageMessages:
            await GeneralCommands.deleteMessages(message)
        # remove/add role to user
        elif ("role" in args[1] and authorPerms.manageRoles):
          await GeneralCommands.addRemoveRole(message, args)
        elif (args[1] == "copy" and authorPerms.manageMessages):
          await GeneralCommands.copyMessage(message, args)
        elif ("replace" in args[1] and authorPerms.manageMessages):
          await GeneralCommands.replaceMessage(message, args)


        ## random commands
        elif ("choice" in args[1] or "choose" in args[1]):
          try:
            choices = message.content.split(f"{args[0]} {args[1]}")[1].split(",")
            await message.channel.send(random.choice(choices))
          except:
            print(f"CAUGHT EXCEPTION\n{traceback.format_exc()}")
            await message.channel.send("There was an error... Possibly a format error... `@MoBot#0697 choice choice1, choice2, choice3, ...`")
        elif ("corona" in args[1]): 
          await message.channel.send(RandomSupport.cornavirus())
        elif ("gtacar" in args[1] or "gta car" in message.content):
          await GTAVehicles.handleUserVehicleInput(message, client)
        elif ("gtatier" in args[1] or "gta tier" in message.content):
          await GTAVehicles.displayTier(message, args[1:])
        elif ("gtaweather" in args[1] or "gta weather" in message.content):
          await GTAWeather.sendWeatherForecast(message)
        elif ("gtarace" in args[1] and "random" in args[2]):
          await GTAVRaces.generateRandomRace(message, args, None)
        elif (args[1] == "admin" and isMo):
          await AdminFunctions.main(args, message, client) 
        elif (args[1] == "dk" and isMo):
          await DKGetPicks.main(args, message, client)
        elif (args[1] == "avatar"):
          member = message.guild.get_member(int(args[2]))
          await message.channel.send(str(member.avatar_url_as))
        elif args[1] == "guildicon":
          await message.channel.send(message.guild.icon_url)
        elif (args[1] == "hangman"):
          await Hangman.main(args, message, client)
        elif (message.content.split("> ")[1].strip() == "2 + 2"):
          msg = await message.channel.send("2 + 2 = 5")
          await asyncio.sleep(3)
          await msg.edit(content="2.4 + 2.4 = 4.8 = 5")
        elif (args[1] == "ping"):
          pong = await message.channel.send("pong")
          ping = message.created_at
          await asyncio.sleep(3)
          await message.channel.send("Well, was it slow?")
          await asyncio.sleep(1)
          await message.channel.send("ping was sent at " + str(ping) + "\n" + "pong was sent at " + str(pong.created_at))
        elif (args[1].lower() in questionWords):
          await moBotQuestions(message, args)
        elif (args[1] == "markdown"):
          if (args[2] == "emoji"):
            await message.channel.send("```" + message.content.split("emoji")[1].strip().replace(" ", "\"\n\"") + "```")
          else:
            await message.channel.send("```" + message.content.split("markdown")[1].strip() + "```")
            
        elif (args[1] == "ids"):
          reply = "**How to get IDs:**\n"
          reply += "Settings -> Appearance -> Developer Mode -> On\n\n"
          reply += "With Developer Mode you will be able to right click various 'things', or hold if you are on mobile. Upon right clicking you will see an option to 'Copy ID'. These IDs are used in many of MoBot's commands.\n\n"

          reply += "**Using IDs in Messages:**\n"
          reply += "@User = <@user_ID>\n"
          reply += "#channel = <#channel_ID>\n"
          reply += "@Role = <@&role_ID>"

          await message.channel.send(reply)
        elif (args[1] == "invite"):
          await message.channel.send("Invite <@449247895858970624> to your server\nhttps://discordapp.com/oauth2/authorize?client_id=449247895858970624&scope=bot&permissions=469920856")
        elif (args[1] == "help"):
          await Collections.displayCollection(message, False, "Help Menu", moBotSupport, False, client)
          #await prepareHelp(message, 1, 0)
        elif ((args[1] == "servers" or args[1] == "guilds") and isMo):
          guilds = client.guilds
          guildCount = len(guilds)
          memberCount = 0
          for i, guild in enumerate(guilds):
            members = guild.members
            try:
              joinDate = guild.get_member(449247895858970624).joined_at
              guilds[i] = [guild.name, len(members), joinDate]
            except:
              guilds[i] = ["unknown", "unknown", datetime.utcnow()]
            memberCount += len(members)

          reply = ""
          guilds.sort(key=lambda x:x[2])
          for i in range(len(guilds)):
            reply += "**" + guilds[i][0] + "** - " + str(guilds[i][1]) + " - " + guilds[i][2].strftime("%b %d %Y") + "\n"

          replies = [""]
          for line in reply.split("\n"):
            if (len(replies[-1] + line) > 2000):
              replies.append(line + "\n")
            else:
              replies[-1] += line + "\n"
          for reply in replies:
            await message.channel.send(reply)
          await message.channel.send("%s%s" % (
            "Guild Count: " + str(guildCount) + "\n",
            "Member Count: " + str(memberCount) + "\n"
          ))
        elif (args[1] == "embed"):
          if (args[2] == "help"):
            # its not that complex
            await message.channel.send("*<@" + str(message.author.id) + ">, trust me, it's less complex than it looks... :D*\nFirst, here's an example of an Embed with all the editable attributes MoBot offers.")
            await asyncio.sleep(1)

            # example embed
            moBotUser = client.get_user(int(moBot))
            embed = discord.Embed(colour=0xd1d1d1)
            embed.set_thumbnail(url=moBotUser.avatar_url_as)
            embed.set_author(name="Author Line", icon_url=moBotUser.avatar_url_as)
            embed.add_field(name="Field Name 1", value='Field Value 1\n' + spaceChar, inline=False)
            embed.add_field(name="Field Name 2", value='Field Value 2', inline=False)
            embed.set_image(url=message.author.avatar_url_as)
            embed.set_footer(text="Footer")
            await message.channel.send(embed=embed)

            await asyncio.sleep(2)

            reply1 = "**Detailed Embed Help**\nMoBot has the functionality to let a user send an embed. Fortunately, embeds have a lot of potential in what you can display with them, however, unfortunately, there is a lot of 'checking' MoBot has to do to understand what the user wants.\n\n__Embed Attributes__\n  - #Color (the colored line on the left)\n  - $$Author Icon$$\n  - !!Author Line!!\n  - %%Thumbnail%%\n  - @@Field Name@@\n  - Field Value\n  - &&Embed Picture&&\n  - ##Footer##\n\n__How to Send an Embed as <@449247895858970624>__\nWhat you see below must be followed exactly, each new element of the embed, must be separated by hitting the return key. *You should be able to copy and paste if you're on mobile - it's its own message.*"

            reply2 = "```@MoBot#0697 say embed #d1d1d1\n!!Author Line!!\n@@Field Name 1@@\nField Value 1\n\n@@Field Name 2@@\nField Value 2\n\n##Footer##\n$$author_picture_address$$\n%%thumbnail_picture_address%%\n&&big_picture_address&&```"

            reply3 = "***Note 1:** You are able to send an embed even if you don't have one of these attributes, for example if you didn't include @@Footer@@ it would just send everything else.*\n***Note 2:** In the edit embed 593862550861512704 command you are able to insert pictures without an address by inserting them into your message. More details below.*\n\n__How to Edit an Embed as <@449247895858970624>__\nThe edit embed 593862550861512704 command can only change one attribute at a time; however, if you are going to edit any of the field names/values they must all be re-typed in one message.\n\nExample: Insert/edit thumbnail picture\n```@MoBot#0697 edit embed 593862550861512704\n%%thumbnail_picture_address%%```\n***Note:** If you are inserting/editing pictures, you don't need the picture address; you are able to send the picture with the message, but just put %%%% instead.*\n\nExample: Editing the color\n```@MoBot#0697 edit embed 593862550861512704 #0000ff```\nExample: Editing the author line\n```@MoBot#0697 edit embed 593862550861512704 !!New_Author_Text!!```\n\n***Final Notes:** Unfortunately, embeds don't enable for tags anywhere except for the Field Value spots. For example, you can't have the clickable links like <@449247895858970624> or <#" + str(message.channel.id) + "> in places except for the Field Values.*"

            reply4 = "<@" + str(message.author.id) + ">, for future format referencing, use `@MoBot#0697 embed format`. It'll post the example embed, and the example `@MoBot#0697 say embed` command."

            await message.channel.send(reply1)
            await message.channel.send(reply2)
            await message.channel.send(reply3)
            await message.channel.send(reply4)
          if (args[2] == "format"):
            content = "Remember, you don't need every attribute of the embed, but make sure everything after the #color is on a new line as seen below. Feel free to copy and paste, then remove anything you don't want/need.```@MoBot#0697 say embed #ff0000\n!!Author Line!!\n@@Field Name 1@@\nField Value 1\n\n@@Field Name 2@@\nField Value 2\n\n##Footer##\n$$author_picture_address$$\n%%thumbnail_picture_address%%\n&&big_picture_address&&```"

            moBotUser = client.get_user(int(moBot))
            embed = discord.Embed(colour=0xd1d1d1)
            embed.set_thumbnail(url=moBotUser.avatar_url_as)
            embed.set_author(name="Author Line", icon_url=moBotUser.avatar_url_as)
            embed.add_field(name="Field Name 1", value='Field Value 1\n' + spaceChar, inline=False)
            embed.add_field(name="Field Name 2", value='Field Value 2', inline=False)
            embed.set_image(url=message.author.avatar_url_as)
            embed.set_footer(text="Footer")
            await message.channel.send(embed=embed, content=content)
        elif (args[1] == "bug"):
          if (len(args) > 2):
            await bugReport(message)
          else:
            await message.channel.send("If there was an issue with a MoBot function, please use `@MoBot#0697 bug [issue]` to submit a bug report.\nFeel free to include a screenshot, as well as what your input was, what happened, and what you thought should have happened.\n\n<@" + str(mo) + "> may reach out to you if he needs more information.")
        elif (args[1] == "send" and authorPerms.administrator):
          if (args[2] == "collection"):
            await CollectionsOLD.sendCollection(message, args, True, client)
          elif(args[2] == "fail"):
            await CollectionsOLD.sendCollection(message, args, True, client)
        elif (args[1] == "test" and isMo):
          await test(message, client)

        ## MoBot promo commands
        elif (args[1].lower() == "donate"):
          await message.channel.send("If you pay, it becomes ***real***...\n\n**PayPal** - <https://paypal.me/MoShots>\n**Venmo** - <https://venmo.com/MoBot_>\n**CashApp** - NickSmithv0")
        elif (args[1].lower() == "server"):
          await message.channel.send("Join my server... It's where you can see features that are in development and such, if you're into that... https://discord.gg/mqxMeTj")

      # end @MoBot ...

      if authorPerms:
        await GeneralCommands.pingRole(message, authorPerms)

      try:
      ## calling server specific file 
        if (str(message.guild.id) in servers):
          await eval(servers[str(message.guild.id)] + ".main(args, message, client)")

        if ((message.guild.id == cotm or message.guild.id == moBotSupport) and "<@%s>" % str(moBot) in message.content):
          try:
            #await message.channel.send("```" + message.content + "```")
            await ReactionRole.addReactionToMessage(message, "🇲")
            await ReactionRole.addReactionToMessage(message, "🇴")
            await ReactionRole.addReactionToMessage(message, "🇧")
            await ReactionRole.addReactionToMessage(message, "🅾")
            await ReactionRole.addReactionToMessage(message, "🇹")
          except discord.errors.NotFound:
            pass

      except AttributeError: # some reason message.guild is none
        pass

      # global clock_check
      # if (datetime.utcnow() - clock_check).seconds > 60:
      #   clock_check = datetime.utcnow()
      #   try:
      #     if (clock_check - await ClocksAndCountdowns.clockCheck(client)).seconds > 300:
      #       await RandomSupport.sendMessageToMo("Check MoBotLoop", client, mo)
      #   except AttributeError:
      #     pass

    # end not MoBot message

    if (not message.author.bot):
      global moBotDB
      try:
        moBotDB.connection.commit()
      except AttributeError: # when no connection was made
        moBotDB = MoBotDatabase.connectDatabase('MoBot')
        
      try:
        sql = """
          SELECT *
          FROM custom_commands 
          WHERE 
            custom_commands.trigger = '%s' AND 
            custom_commands.guild_id = '%s'
          """ % (MoBotDatabase.replaceChars(message.content), message.guild.id)
        moBotDB.connection.commit()
        moBotDB.cursor.execute(sql)
        for record in moBotDB.cursor:
          await SimpleCommands.sendCommand(message, record)
          break
      except AttributeError: # when messaage is a private message... idk 
        pass

    

  except:
    await RandomSupport.sendErrorToMo("MoBot", client, mo)
# end on_message

@client.event
async def on_member_join(member):
  if (not isConnected):
    return

  if (str(member.guild.id) in autoRoles):
    await ReactionRole.addAutoRoleToUser(member, autoRoles[str(member.guild.id)]["RoleIDs"])

  if (str(member.guild.id) in servers):
    await eval(servers[str(member.guild.id)] + ".memberJoin(member)")
# end on_member_join

@client.event
async def on_member_remove(member):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    await eval(servers[str(member.guild.id)] + ".memberRemove(member, client)")
# end on_member_remove

@client.event
async def on_raw_reaction_add(payload):
  if (not isConnected):
    return
  
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id
  try:

    try:
      guild = client.get_guild(guildID)
      channel = guild.get_channel(channelID)
      msg = await channel.fetch_message(messageID)
      member = msg.guild.get_member(payload.user_id)
    except AttributeError:
      try:
        msg = await client.get_channel(channelID).fetch_message(messageID)
        member = client.get_user(payload.user_id)
      except AttributeError:  
        member = client.get_user(payload.user_id)
        msg = await member.send(".")
        await msg.delete()
        msg = await msg.channel.fetch_message(messageID)  
    except discord.errors.NotFound:
      return

    message = msg

    # needed embed stuff
    try:
      embedAuthor = str(message.embeds[0].author.name)
    except IndexError:
      embedAuthor = "None"

    try:
      embedFooter = str(message.embeds[0].footer.text)
    except IndexError:
      embedFooter = "None"

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"
    # end embed stuff

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"


    if (not member.bot):
      await ReactionRole.reactionRole(message, payload, member, "click")

      logActionToConsole(message, member, "reactionAdd")
      if (len(message.embeds) > 0):

        if ("RLScrims" in embedAuthor):
          await RLScrims.mainReactionAdd(message, payload, client, member)

        elif (("MoBotCollection" in embedAuthorURL or "MoBotReservation" in embedAuthorURL) and message.author.id == int(moBot)):
          if (message.author.id == int(moBot)):
            await Collections.mainReactionAdd(message, payload, message.embeds[0], client)
            if ("MoBotReservation" in message.embeds[0].author.url):
              await Reservations.mainReactionAdd(message, payload, client)

        elif ("MoBot Hangman" in embedAuthor):
          await Hangman.mainReactionAdd(message, payload, client)
              
        elif ("MoBot Tables" in embedAuthor):
          await MoBotTables.mainReactionAdd(message, payload, client)

        elif ("Countdown Editor" in embedAuthor):
          await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
        elif ("MoBot Clock Editor" in embedAuthor):
          await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "clock")

        elif ("MoBot Custom Commands" in embedAuthor):
          await SimpleCommands.mainReactionAdd(message, payload, client)

        elif ("GTA V Weather Forecast" in embedAuthor):
          await GTAWeather.mainReactionAdd(message, payload, client)

        elif "GTA V Vehicle Search" in embedAuthor:
          await GTAVehicles.mainReactionAdd(message, payload, client)

        elif ("•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
          if (payload.emoji.name == "⬅"):
            await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
          elif (payload.emoji.name == "➡"):
            await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)

      elif ("open a ticket" in message.content.lower()):
        if (payload.emoji.name == "✅"):
          await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
          await ticketManager.openTicket(message, member, True, client)
      elif ("Add Table" in message.content):
        await DiscordSheets.mainReactionAdd(message, payload, client)
      elif ("Message Scheduler" in message.content):
        await MessageScheduler.mainReactionAdd(message, payload, client)
      elif (len(message.embeds) > 0 and "Countdown Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
      elif (len(message.embeds) > 0 and "Clock Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "clock")
      elif (len(message.embeds) > 0 and "•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
        if (payload.emoji.name == "⬅"):
          await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
        elif (payload.emoji.name == "➡"):
          await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)

      if (str(message.guild.id) in servers):
        await eval(servers[str(message.guild.id)] + ".mainReactionAdd(message, payload, client)")
  except discord.errors.Forbidden:
    pass
# end on_reaction_add

@client.event
async def on_raw_reaction_remove(payload):
  if (not isConnected):
    return
  
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id
  try:

    try:
      guild = client.get_guild(guildID)
      channel = guild.get_channel(channelID)
      msg = await channel.fetch_message(messageID)
      member = msg.guild.get_member(payload.user_id)
    except AttributeError:
      try:
        msg = await client.get_channel(channelID).fetch_message(messageID)
        member = client.get_user(payload.user_id)
      except AttributeError:  
        member = client.get_user(payload.user_id)
        msg = await member.send(".")
        await msg.delete()
        msg = await msg.channel.fetch_message(messageID)  

    message = msg

    # needed embed stuff
    try:
      embedAuthor = str(message.embeds[0].author.name)
    except IndexError:
      embedAuthor = "None"

    try:
      embedFooter = str(message.embeds[0].footer.text)
    except IndexError:
      embedFooter = "None"

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"
    # end embed stuff


    if (not member.bot or member.id == 476974462022189056):
      await ReactionRole.reactionRole(message, payload, member, "unclick")
      
      logActionToConsole(message, member, "reactionRemove")
      if (len(message.embeds) > 0):

        if "GTA V Vehicle Search" in embedAuthor:
          await GTAVehicles.mainReactionRemove(message, payload, client)

      if (len(message.embeds) > 0 and "•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
        if (payload.emoji.name == "⬅"):
          await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
        elif (payload.emoji.name == "➡"):
          await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)  
      elif (len(message.embeds) > 0 and ("MoBotCollection" in embedAuthorURL or "MoBotReservation" in embedAuthorURL)):
        if (message.author.id == int(moBot)):
          await Collections.mainReactionRemove(message, payload, message.embeds[0], client)

      # calling server specific file but mainReactionRemove function instead of main
      elif (str(message.guild.id) in servers):
        await eval(servers[str(message.guild.id)] + ".mainReactionRemove(message, payload, client)")
  except discord.errors.NotFound:
    pass
# end on_reaction_remove

@client.event
async def on_member_update(before, after):
  if (not isConnected):
    return
  
  bRoles = before.roles
  aRoles = after.roles

  if (len(aRoles) > len(bRoles)):
    for role in aRoles:
      if (role not in bRoles):
        await on_member_role_add(after, role)
        break
  elif (len(bRoles) > len(aRoles)):
    for role in bRoles:
      if (role not in aRoles):
        await on_member_role_remove(after, role)
        break
  try:
    await eval(servers[str(before.guild.id)] + ".mainMemberUpdate(before, after, client)")
  except KeyError:
    pass
  except AttributeError:
    pass
# end on_member_update

# called in on_member_update
async def on_member_role_add(member, role):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    try:
      await eval(servers[str(member.guild.id)] + ".memberRoleAdd(member, role)")
    except AttributeError:
      pass
# end on_role_update

# called in on_member_update
async def on_member_role_remove(member, role):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    try:
      await eval(servers[str(member.guild.id)] + ".memberRoleRemove(member, role)")
    except AttributeError:
      pass
# end on_role_update

def logActionToConsole(message, user, logType):
  try:
    logMessage = str(datetime.now().strftime("%H:%M:%S.%f")) + " : G - " + str(message.guild) + " : C - " + str(message.channel)

    if (logType == "message"): 
      logMessage += " : MS - "
      if (str(message.author.id) != moBot and message.author.bot):
        return
    elif (logType == "reactionAdd"):
      logMessage += " : RA - "
    elif (logType == "reactionRemove"):
      logMessage += " : RR - "

    logMessage += str(user.display_name)
    if (len(message.guild.members) < 1000):
      print(logMessage)
  except AttributeError: # None type as message is in DM
    pass
# end logMessage

async def moBotQuestions(message, args):
  r = int(random.random() * 100)
  reply = questionWords[args[1].lower()][r % len(questionWords[args[1].lower()])][1]
  reply = reply[r % len(reply)]
  await message.channel.send(reply)
# end moBotQuestions

async def bugReport(message):
  moBotSupportServer = client.get_guild(moBotSupport)
  bugReportChannel = moBotSupportServer.get_channel(593895342030716928)

  bug = str(message.guild.id) + "-" + str(message.channel.id) + "-" + str(message.author.id) + "\n\n**Bug Report:**\n"
  try:
    bug += message.content + "\n"
  except IndexError:
    pass

  bug += "\n**Attatchments:**\n"
  for i in message.attachments:
    bug += i.url + "\n" 
  await bugReportChannel.send(bug)
  await message.channel.send("Thank you for reporting a bug!\nJoin `@MoBot#0697 server` to stay updated on updates and patches.")

def getServers():
  global servers
  moBotDB.cursor.execute("""
    SELECT id, file_name
    FROM servers
  """)
  
  for record in moBotDB.cursor:
    servers[record[0]] = record[1]
# end getServers

async def test(message, client):
  msg = await message.channel.fetch_message(600812373212921866)
  print(msg.embeds[0].color)
# end test

print("Connecting...")
client.run(SecretStuff.getToken("MoBotDiscordToken.txt"))