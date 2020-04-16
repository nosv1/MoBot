import discord
from discord.ext import commands
import asyncio  
import selenium
from datetime import datetime
from bs4 import BeautifulSoup as bSoup
import requests
from requests_html import AsyncHTMLSession
from numberConversion import *
from pytz import timezone
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import random
import traceback
import mysql.connector
import re

import SecretStuff
import ClocksAndCountdowns
import MoBotTables
import DiscordSheets
import ReactionRole
import Collections
import RLScrims
import ticketManager
import Hangman
import GTACCHub
import Reservations
import MoBotTimeZones
import RLRanks
import RandomSupport
import AdminFunctions
import EventScheduler
import DKGetPicks
import SimpleCommands
import MoBotDatabase
import Mazes
import Help
import GTAWeather
import GeneralCommands

import TEPCOTT
import COTM
import AOR
import Noble2sLeague
import GRG
import Imperial
import ReapersMC

client = discord.Client()
moBotDB = None
moBotSupport = 467239192007671818

# channels
botSpam = 593911201658961942

# users
moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058
nosv1 = 475325629688971274

spaceChar = "⠀"

helpPages = {
  "Author" : "",
  "Number of Pages" : 0,
}

reactionMessages = {}
autoRoles = {}

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
  print("MoBotTest is online - " + str(datetime.now()))

  '''global autoRoles
  autoRoles = await ReactionRole.updateAutoRoles(autoRoles, await ReactionRole.openReactionRoleSpreadsheet())
  print("AutoRoles Received")'''

  global moBotDB
  try:
    moBotDB = MoBotDatabase.connectDatabase('MoBot')
    print ("Connected to MoBot Database")
  except mysql.connector.errors.DatabaseError:
    print("Could Not Connect to MoBot Database")

  '''mobotLog = client.get_guild(moBotSupport).get_channel(604099911251787776) # mobot log
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBotTest Restarted")
  await mobotLog.send(embed=embed)'''
# end on_ready

@client.event
async def on_raw_message_edit(payload):
  pd = payload.data
  message = await client.get_channel(int(pd["channel_id"])).fetch_message(int(pd["id"]))
  
  if (not message.author.bot):
    try:
      pd["content"]
      await on_message(message)
    except KeyError: # when content was not updated
      pass
# end on_raw_message_edit

@client.event
async def on_message(message):
  logMessageToConsole(message, message.author, "reaction")

  try:
    if (not message.author.bot):
      print(message.content)
  except:
    pass

  message.content = message.content.translate({ord(c) : '"' for c in ['“', '”']})
  mc = message.content.translate({ord(c) : " " for c in ["\n", "\t", "\r"]}) # that was beautiful
  while ("  " in mc):
    mc = mc.replace("  ", " ")
  args = mc.split(" ")

  if (args[0] == "test" or str(moBotTest) in args[0]):
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
      
    if (len(args) > 1):
      if (args[1] == "test"):
        await COTM.handleFormSignup(await message.guild.get_channel(527355464216739866).fetch_message(700362940326477859))
        await message.channel.send("done", delete_after=3)
      elif (args[1] == "table"):
        await MoBotTables.main(args, message, client)
      elif (args[1] == "nrt"):
        await Noble2sLeague.sendNRT(message, args)
      elif (args[1] == "?"):
        await Help.main(args, message, client)
      elif (args[1] == "maze"):
        size = int(message.content.split("maze")[1].strip())
        maze = Mazes.mazeBuilder(size)
        await message.channel.send("```%s\n%s```" % (size, maze))
      elif ("command" in args or "commands" in args):
        await SimpleCommands.main(args, message, client)
      elif (args[1] == "dk"):
        try:
          await DKGetPicks.main(args, message, client)
        except:
          print(traceback.format_exc())
        #await message.channel.purge(limit=2)
      elif (args[1] == "countdown"):
        print("yes")
        await ClocksAndCountdowns.main(args, message, client)
      elif (args[1] == "help"):
        await Collections.displayCollection(message, False, "Help Menu", message.guild.id, client)
      elif (args[1] == "add" and args[2] == "reaction"):
        if (len(args) > 2):
          await ReactionRole.addReactionToMessage(await message.channel.fetch_message(int(args[-1])), args[3:-1])
      elif (args[1] == "embed"):
        await makeEmbed(message)
      elif (args[1] == "permission"):
        user = message.guild.get_member(int(args[2]))
        authorPerms = message.channel.permissions_for(user)
        await message.channel.send(str(authorPerms.administrator))
        await nosV1User.send("---")
      elif (args[1] == "say"):
        if (args[2] == "embed"):
          await moBotEmbed(message, args, False)
        else:
          await message.channel.send(message.content.split("say")[1].strip())
      elif (args[1] == "edit" and args[2] == "embed"):
        await moBotEmbed(message, args, True)
      elif ("collection" in args[1]):
        await Collections.main(args, message, client)
      elif (args[1] == "delete"):
        topMsgID = int(message.content.split("delete ")[1].split(" ")[0].strip())
        try:
          if ("delete" not in message.content.split(" ")[-2]):
            bottomMsgID = int(message.content.split(" ")[-1].strip())
          else:
            bottomMsgID = message.id
        except ValueError:
          bottomMsgID = message.id
        try:
          topMsg = await message.channel.fetch_message(topMsgID)
          bottomMsg = await message.channel.fetch_message(bottomMsgID)
          purged = await message.channel.purge(after=topMsg, before=bottomMsg)
          try:
            await topMsg.delete()
          except discord.errors.NotFound:
            pass
          try:
            await bottomMsg.delete()
          except discord.errors.NotFound:
            pass
          try:
            await message.delete()
          except discord.errors.NotFound:
            pass
          msg = await message.channel.send("Deleted " + str(len(purged) + 1) + " messages.")
          await asyncio.sleep(5)
          await msg.delete()
        except discord.errors.NotFound:
          await message.channel.send("Message Not Found -- Check the ID you gave -- For futher help, use `@MoBot#0697 help` -> General Use -> `@MoBot#0697 delete`")
        except AttributeError:
          topMsg = await message.channel.fetch_message(topMsgID)
          bottomMsg = await message.channel.fetch_message(bottomMsgID)
          history = message.channel.history(after=topMsg, before=bottomMsg)
          await topMsg.delete()
          async for msg in history:
            try:
              await msg.delete()
            except:
              pass
      elif (args[1] == "scrims"):
        await RLScrims.main(args, message, client)
      elif (args[1] == "wait"):
        msg1 = await message.channel.send("Waitin for reply... you have 10 seconds")

        def check(msg):
          return msg.author.id == 449247895858970624

        try:
          msg2 = await client.wait_for('message', timeout=10.0, check=check)
          await message.channel.send(msg2.content)
        except asyncio.TimeoutError:
          await message.channel.send("NOPE")
      elif (args[1] == "inttobraile"):
        await message.channel.send(intToBraile(int(message.content.split("inttobraile")[1].strip())))
      elif (args[1] == "brailetoint"):
        await message.channel.send(str(braileToInt(message.content.split("brailetoint")[1].strip())))
      elif (args[1] == "watch"):
        await ReactionRole.addReactionRoleMessage(message, args)
      elif (args[1] == "copy"):
        await message.channel.trigger_typing()

        try:
          destChannel = message.guild.get_channel(int(message.content.split("#")[1].split(">")[0].strip())) # checked error statement

          msgIDs = message.content.split("copy")[1].strip().split("<#")[0].strip().split(" ")
          for msgID in msgIDs:
            if (msgID == "embed"):
              continue
            msg = await message.channel.fetch_message(int(msgID))
            if (msg.content != ""):
              content = msg.content
            else:
              content = None
            if (args[2] == "embed"):
              try:
                await message.channel.send(embed=msg.embeds[0], content=content)
              except IndexError:
                await message.channel.send("**No Embed in Message**\n<" + msg.jump_url + ">.")
            else:
              content = msg.content
              for attachment in msg.attachments:
                content += "\n" + attachment.url
              content += " " + spaceChar
              await destChannel.send(content=content)
        except IndexError:
          await message.channel.send("**No [#destination-channel] Given**\n\n`@MoBot#0697 copy [embed] [Message_ID] [#destination-channel]` *(`[embed]` is only needed if there is an embed in the source message)*")
        
      elif (args[1] == "ticket"):
        await ticketManager.main(args, message, client)
      elif (args[1] == "autorole"):
        global autoRoles
        if (args[2] == "add"):
          autoRoles = await ReactionRole.addAutoRole(message, autoRoles)
          print(autoRoles)
        elif (args[2] == "clear"):
          autoRoles = await ReactionRole.clearAutoRole(message, autoRoles)
          print(autoRoles)
      elif (args[1] == "hangman"):
        await Hangman.newGame(message, client)
      elif (args[1] == "reservation"):
        await Reservations.main(args, message, client)
      elif (args[1] == "rss"):
        await rssTest(message)
      elif (args[1] == "avatar"):
        member = message.guild.get_member(int(args[2]))
        print(member.avatar_url)
      elif (args[1] == "tz"):
        await MoBotTimeZones.main(args, message, client)
      elif (args[1] == "rlrank"):
        await RLRanks.main(args, message, client)
      elif (args[1] == "admin"):
        await AdminFunctions.main(args, message, client)
      elif (args[1] == "remindme"):
        await EventScheduler.setReminder(message)
        
  if ("!" in args[0]):
    await GTACCHub.main(args, message, client)

  if (not message.author.bot):
    try:
      global moBotDB
      try:
        moBotDB.connection.commit()
      except AttributeError: # when no connection was made
        try:
          moBotDB = MoBotDatabase.connectDatabase('MoBot')
        except mysql.connector.errors.DatabaseError:
          pass # likely host cannot connect to database

      moBotDB.cursor.execute("""
        SELECT *
        FROM custom_commands 
        WHERE 
          custom_commands.trigger = '%s' AND 
          custom_commands.guild_id = '%s'
        """ % (message.content.replace("'", "''"), message.guild.id))
      for record in moBotDB.cursor:
        await SimpleCommands.sendCommand(message, record)
        break
    except:
      pass

# end on_message

@client.event
async def on_raw_reaction_add(payload):
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id

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

  try:
    embedAuthor = str(message.embeds[0].author.name)
  except IndexError:
    embedAuthor = "None"
    
  try:
    pName = payload.emoji.name if (payload.emoji.id == None) else "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
    msg = reactionMessages[pName][message.id]
    roles = message.guild.roles
    for role in roles:
      for roleID in msg["RoleID"][0]:
        if (role.id == int(roleID)):
          if (msg["RoleID"][1] == "add"):
            await member.add_roles(role)
          else:
            await member.remove_roles(role)
  except KeyError:
    pass
  except discord.errors.Forbidden:
    msg = await message.channel.send("Cannot add role, <@449247895858970624> does not have permission...")
    await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
    await asyncio.sleep(5)
    await msg.delete()

  if (not member.bot):        
    logMessageToConsole(message, member, "reaction")

    if (message.id == 620740642443886611): # message id for Reserves Embed
      if (payload.emoji.name == "👋"):
        await COTM.reserveNeeded(message, member)
      elif (payload.emoji.name == "✊"):
        await COTM.reserveAvailable(message, member)
      elif (payload.emoji.name == "❌"):
        await COTM.clearReserves(message)

    if (len(message.embeds) > 0):
      if (message.id == 600723441888264211):
        if (payload.emoji.name == "✅" or payload.emoji.name == "❌"):
          await streamScheduler(message, payload, client)
          await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
        elif (payload.emoji.name == "🗑"):
          await clearStreamScheduler(message, client)
          await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
      if ("Noble Rank Tracker" in embedAuthor):
        await Noble2sLeague.saveNRT(message, member)
      if ("Score Submission" in embedAuthor):
        await Noble2sLeague.mainReactionAdd(message, payload, client)
      if ("MoBot Tables" in embedAuthor):
        await MoBotTables.mainReactionAdd(message, payload, client)
      if ("TEPCOTT - Season 4" in embedAuthor):
        await TEPCOTT.mainReactionAdd(message, payload, client)
      if ("GTA V Weather Forecast" in embedAuthor):
        await GTAWeather.handleFutureCast(message, member)
      if ("MoBot Commands" in embedAuthor):
        await Help.mainReactionAdd(message, payload, client)
      if ("Clock Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "clock")
      if ("Countdown Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
      if ("AOR" in embedAuthor):
        await AOR.mainReactionAdd(message, payload, client)
      '''if ("Countdown Editor" in message.embeds[0].author.name):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
      if (("MoBotCollection" in message.embeds[0].author.url or "MoBotReservation" in message.embeds[0].author.url) and message.author.id == moBotTest):
        await Collections.mainReactionAdd(message, payload, message.embeds[0], client)
        if ("MoBotReservation" in message.embeds[0].author.url):
          await Reservations.mainReactionAdd(message, payload, client)
      if ("EventScheduler" in message.embeds[0].author.url):
        pass'''
    else:
      #if (message.guild.id == 527156310366486529 or "are you ready to vote" in message.content.lower() or "do you need to vote" in message.content.lower()): # cotm
        #await COTM.mainReactionAdd(message, payload, client)
      if ("open a ticket" in message.content.lower()):
        if (payload.emoji.name == "✅"):
          await ticketManager.openTicket(message, member, True, client)
      if message.id == 700023016549253171:
        await ReapersMC.mainReactionAdd(message, payload, client)


@client.event
async def on_raw_reaction_remove(payload):
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id

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

  try:
    embedAuthor = str(message.embeds[0].author.name)
  except IndexError:
    embedAuthor = "None"

  try:
    pName = payload.emoji.name if (payload.emoji.id == None) else "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
    msg = reactionMessages[pName][message.id]
    roles = message.guild.roles
    for role in roles:
      for roleID in msg["RoleID"][0]:
        if (role.id == int(roleID)):
          if (msg["RoleID"][1] == "add"):
            await member.remove_roles(role)
          else:
            await member.add_roles(role)
  except KeyError:
    pass
  except discord.errors.Forbidden:
    pass

  if (not member.bot):    
    logMessageToConsole(message, member, "reaction")

    if (message.id == 620740642443886611): # message id for Reserves Embed
      if (payload.emoji.name == "👋"):
        await COTM.reserveNotNeeded(message, member)
      elif (payload.emoji.name == "✊"):
        await COTM.reserveNotAvailable(message, member)

    if (len(message.embeds) > 0):
      if ("MoBot Commands" in embedAuthor):
        await Help.mainReactionAdd(message, payload, client)
      '''if (("MoBotCollection" in message.embeds[0].author.url or "MoBotReservation" in message.embeds[0].author.url) and message.author.id == moBotTest):
        await Collections.mainReactionRemove(message, payload, message.embeds[0], client)'''
      pass
# end on_raw_reaction_remove

@client.event
async def on_member_join(member):
  if (str(member.guild.id) in autoRoles):
    await ReactionRole.addAutoRoleToUser(member, autoRoles[str(member.guild.id)]["RoleIDs"])
# end on_member_join

@client.event
async def on_member_update(before, after):
  pass
# end on_member_update

def logMessageToConsole(message, user, logType):
  try:
    logMessage = str(datetime.now().strftime("%H:%M:%S.%f")) + " : G - " + str(message.guild) + " : C - " + str(message.channel)

    if (logType == "message"): 
      logMessage += " : MS - "
      if (str(message.author.id) != moBot and message.author.bot):
        return
    elif (logType == "reactionAdd"):
      logMessage += " : RA - "
    elif (logType == "reactionRemoved"):
      logMessage += " : RR - "

    logMessage += str(user.display_name)
    if (len(message.guild.members) < 1000):
      print(logMessage)
  except AttributeError: # None type as message is in DM
    pass
# end logMessage

async def getTimeZoneDifference(message):
  currentTime = datetime.now()

  timeZones = MoBotTimeZones.timeZones
  userTimeZones = message.content.split("tz")[1].strip().split(" ")
  for i in range(len(userTimeZones)):
    userTimeZones[i] = userTimeZones[i].lower()

  times = []
  for tz in timeZones:
    tz = timezone(tz)
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(tz)
    if (convertedTime.tzname().lower() in userTimeZones):
      times.append(convertedTime.replace(tzinfo=None))

  if (len(times) == 2):
    delta = (times[0] - times[1]).total_seconds()
    if (delta < 0):
      # [0] ahead of [1]
      t = userTimeZones[0]
      userTimeZones[0] == userTimeZones[1]
      userTimeZones[1] == t
      delta = (times[1] - times[0]).total_seconds()

      t = times[0]
      times[0] = times[1]
      times[1] = t

    hours = int(delta / 3600)
    minutes = int((delta - (hours * 3600)) / 60)

    reply = userTimeZones[0].upper() + " + " + str(hours) + ":" + str(minutes).rjust(2, "0") + " = " + userTimeZones[1].upper() + "\n\n"
    reply += "**Current Times**\n"
    reply += userTimeZones[0].upper() + ": " + times[0].strftime("%H:%M - %b %d") + "\n"
    reply += userTimeZones[1].upper() + ": " + times[1].strftime("%H:%M - %b %d")

    await message.channel.send(reply)

  else:
    msg = await message.channel.send("At least one of the two time zones provided is not recognized in *MoBot's Time Zone List*.\n\nWould you like to view the current list?")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(payload):
      return (payload.emoji.name == "✅" or payload.emoji.name == "❌") and payload.user_id == message.author.id

    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=check)

    if (payload.emoji.name == "✅"):
      timeZones = MoBotTimeZones.timeZones
      reply = "**MoBot's Time Zone List:**"
      for tz in timeZones:
        convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz)) 
        name = "**" + convertedTime.tzname() + "**" if tz == "UTC" else convertedTime.tzname()
        reply += "\n  " + name + " - " + tz
      reply += "\n\nExample: `@MoBot#0697 tz UTC MSK`"
      reply += "\n*If you would like to add a time zone to this list, join the `@MoBot#0697 server` and stick it in <#547247266361114655>.*"
      await message.channel.send(reply)
# end getTimeZoneDifference
    
async def updateTimeZoneList(currentTime):
  moBotSupportGuild = client.get_guild(moBotSupport)
  timeZonesChannel = moBotSupportGuild.get_channel(607323514042712074)
  timeZonesListMessage = await timeZonesChannel.fetch_message(607324012774817942) # 607323599925149706 (mobot)

  timeZones = ["America/Los_Angeles", "America/Denver", "America/Chicago", "America/New_York", "Canada/Atlantic", "UTC", "Europe/London", "Europe/Monaco", "Europe/Moscow"]

  timeZoneList = ""
  for tz in timeZones:
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))  
    time = convertedTime.strftime("%H:%M " + convertedTime.tzname() + " (%z) " + tz)
    if (tz == "UTC"):
      time = "**" + time + "**"
    timeZoneList += time + "\n"
  
  await timeZonesListMessage.edit(content=timeZoneList)

async def clearStreamScheduler(message, client):
  embed = message.embeds[0]
  embed = embed.to_dict()
  value = embed["fields"][0]["value"]
  lines = value.split("\n")
  newValue = ""

  for line in lines:
    tLine = line + "\n"
    if ("- " in line and ":" in line):
      tLine = "- " + line.split("- ")[1].split(":")[0] + ":" + "\n"

    newValue += tLine
  
  embed["fields"][0]["value"] = newValue

  embed = discord.Embed.from_dict(embed)
  await message.edit(embed=embed)
  await Collections.replaceCollectionEmbed(message, message.id, message.id, client)
# end clearStreamScheduler

async def streamScheduler(message, payload, client):
  emojis = {
    "days" : {
      "⚪" : "Monday",
      "⚫" : "Tuesday",
      "🔴" : "Thursday",
      "🔵" : "Saturday",
    }, 
    "hours" : {
      "5⃣" : "5pm:",
      "6⃣" : "6pm:",
      "7⃣" : "7pm:",
    },
    "confirm" : "✅",
    "leave" : "❌",
  }

  member = message.guild.get_member(payload.user_id)
  day = []
  hour = []
  for reaction in message.reactions:
    if (reaction.emoji in emojis["days"] or reaction.emoji in emojis["hours"]):
      async for user in reaction.users():
        if (user.id == member.id):
          try:
            day = [reaction.emoji, emojis["days"][reaction.emoji]]
            await message.remove_reaction(reaction.emoji, user)
          except KeyError:
            hour = [reaction.emoji, emojis["hours"][reaction.emoji]]
            await message.remove_reaction(reaction.emoji, user)
          break
    if (day != [] and hour != []):
      break

  if (day == [] or hour == []):
    return
  else:
    embed = message.embeds[0]
    embed = embed.to_dict()
    value = embed["fields"][0]["value"]
    lines = value.split("\n")
    newValue = ""

    tDay = ""
    tHour = ""
    tLine = ""

    for line in lines:
      tLine = line + "\n"
      if ("** - " in line):
        tDay = line.split("**")[1]
      elif ("- " in line and ":" in line):
        tHour = line.split("- ")[1].split(":")[0] + ":"

        if (tDay == day[1] and tHour == hour[1]):
          if (payload.emoji.name == emojis["confirm"]):
            tLine = line.split("\n")[0] + " " + member.mention + "\n"
          else:
            if (str(member.id) in line):
              tLine = tLine.replace(" " + member.mention + "", "")

      newValue += tLine
    
    embed["fields"][0]["value"] = newValue

  embed = discord.Embed.from_dict(embed)
  await message.edit(embed=embed)
  await Collections.replaceCollectionEmbed(message, message.id, message.id, client)
# end streamScheduler

async def help(message):

  helpPages = {
    "Author" : "MoBot's Command Help Menu",
    "Page 1" : {
      "Header" : "Instructions",
      "Fields" : [
        "Use the ◀/▶ to maneuver through the editor.",
        "Use the ➕/➖ to 'zoom in' and 'zoom out' of a specific page.",
        "Click the ❌ when you're finished."
      ]
    },
    "Page 2" : {
      "Header" : "Command Type",
      "Fields" : [
        "MoBot General Server Commands",
        "MoBot Specific Use Commands",
        "MoBot Random Commands",
        "MoBot Promo Commands",
        "This Server's Commands",
      ]
    },
  }

  helpPages["Number of Pages"] = len(helpPages) - 2

  helpEmbed = discord.Embed(colour=0x36393f)
  helpEmbed.set_author(name=helpPages["Author"])

  field = ""
  for line in helpPages["Page 1"]["Fields"]:
    field += line + "\n"

  helpEmbed.add_field(name=helpPages["Page 1"]["Header"], value=field, inline=False)
  helpEmbed.set_footer(text="Page 1/" + str(helpPages["Number of Pages"]))

  helpMsg = await message.channel.send(embed=helpEmbed)
  await helpMsg.add_reaction("◀")
  await helpMsg.add_reaction("▶")
  await helpMsg.add_reaction("➕")
  await helpMsg.add_reaction("➖")
  await helpMsg.add_reaction("❌")

  # figure out what kind of commands they wanna see

  
  # if server specific, call server help command
# end help

async def makeEmbed(message):
  '''Creates an embed messasge with specified inputs'''

  moBotUser = message.guild.get_member(int(moBot))
  embed = discord.Embed(colour=discord.Embed().Empty)
  embed.set_thumbnail(url=moBotUser.avatar_url)
  embed.set_author(name="**Tes**\n*test*" + spaceChar, url="https://google.com/MoBotReservation/collection=605980661492350976/id=605980829818159128/left=605980830430658581/right=605980830430658581/emojis=👑,🔧/sub_specifiers=host,pit_marshall", icon_url="https://images.discordapp.net/avatars/449247895858970624/6e2a9f666b1190d5bf59be5c3bb20327.png?size=512")
  embed.add_field(name="Field Name\ntest", value='Field Value', inline=True)
  embed.description = "**Big test** <@" + str(moBot) + ">"

  embed.set_image(url=message.author.avatar_url)
  embed.set_image(url="https://giant.gfycat.com/MeekOrneryArgentineruddyduck.gif")
  embed.set_footer(text="Footer\n**__Footer__**")
  print(embed.to_dict())

  await message.channel.send(embed=embed)

async def moBotEmbed(message, args, isEdit):
  mc = message.content
  empty = discord.Embed().Empty
  color = empty
  authorIcon = empty
  authorLine = None
  authorURL = None
  thumbnail = empty
  fields = []
  embedPicture = None
  footer = None
  embed = None
  isCollection = False
  isReservation = False
  if (isEdit):
    try:
      msg = None
      try:
        msg = await message.channel.fetch_message(int(args[3]))
      except discord.errors.NotFound:
        for channel in message.guild.channels:
          try:
            msg = await channel.fetch_message(int(args[3]))
            break
          except discord.errors.NotFound:
            pass
          except AttributeError:
            pass
      if (msg is None):
        await message.channel.send("**Message ID Not Found**")
        return
      mc = mc.replace(args[3] + " ", "")
      embed = msg.embeds[0]
      color = embed.color
      embed = embed.to_dict()

      try:
        authorIcon = embed["author"]["icon_url"]
      except KeyError:
        pass

      try:
        authorURL = embed["author"]["url"]
        isCollection = "MoBotCollection" in authorURL
        isReservation = "MoBotReservation" in authorURL
      except KeyError:
        pass

      try:
        descripton = embed["description"]
      except KeyError:
        pass

      try:
        authorLine = embed["author"]["name"]
      except KeyError:
        pass

      try:
        thumbnail = embed["thumbnail"]["url"]
      except KeyError:
        pass

      try:
        eFields = embed["fields"]
        for i in range(len(eFields)):
          fields.append([eFields[i]["name"], eFields[i]["value"]])
      except KeyError:
        pass

      try:
        embedPicture = embed["image"]["url"]
      except KeyError:
        pass

      try:
        footer = embed["footer"]["text"]
      except KeyError:
        pass

      embed = discord.Embed().from_dict(embed)
    except:
      await message.channel.send("Looks like something wasn't quite right... Either the MessageID you typed isn't correct, or the MessageID of the message doesn't have an embed already. You also need to be in the same channel as the embed. Use `@MoBot#0697 embed help` for further guidence.")
      return

  # get color
  try:
    color = int("0x" + mc.split("embed #")[1].split("\n")[0].strip(), 16)
  except IndexError:
    pass
  if (isEdit):
    embed.color = color
  else:
    embed = discord.Embed(color=color)

  # get author stuff
  try:
    authorIcon = mc.split("$$")[1].split("\n")[0].strip()
    authorIcon = authorIcon if (authorIcon != "") else empty

    try:
      authorIcon = message.attachments[0].url
    except IndexError:
      pass

  except IndexError:
    pass

  try:
    authorLine = mc.split("!!")[1].split("\n")[0].strip().replace("\\n", "\n")
  except IndexError:
    pass

  if (authorIcon != empty and authorLine == None):
    if (isCollection):
      embed.set_author(name=spaceChar, icon_url=authorIcon, url=authorURL)
    else:
      embed.set_author(name=spaceChar, icon_url=authorIcon)
  elif (authorLine != None):
    if (isCollection or isReservation):
      embed.set_author(name=authorLine, icon_url=authorIcon, url=authorURL)
    else:
      embed.set_author(name=authorLine, icon_url=authorIcon)
    
  try:
    description = mc.split("^^")[1].split("\n")[0].strip()
    embed.description = description.replace("\\n", "\n")
  except IndexError:
    pass

  # get footer
  try:
    footer = mc.split("##")[1].split("\n")[0].strip()
    embed.set_footer(text=footer)
  except IndexError:
    pass

  # get thumbnail
  try:
    thumbnail = mc.split("%%")[1].split("\n")[0].strip()

    if (thumbnail == ""):
      try:
        thumbnail = message.attachments[0].url
      except IndexError:
        thumbnail = None

    if (thumbnail == None):
      embed = embed.to_dict()
      try:
        embed.pop("thumbnail")
      except KeyError:
        pass
      embed = discord.Embed().from_dict(embed)
    else:
      embed.set_thumbnail(url=thumbnail)
  except IndexError:
    pass

  # get embed picture
  try:
    embedPicture = mc.split("&&")[1].split("\n")[0].strip()

    if (embedPicture == ""):
      try:
        embedPicture = message.attachments[0].url
      except IndexError:
        embedPicture = None

    if (embedPicture == None):
      embed = embed.to_dict()
      try:
        embed.pop("image")
      except KeyError:
        pass
      embed = discord.Embed().from_dict(embed)
    else:
      embed.set_image(url=embedPicture)
  except IndexError:
    pass

  newFields = []
  # get fields
  lines = mc.split("\n")
  symbols = ["!!", "^^", "@@", "##", "$$", "%%", "&&"]
  i = 1
  while (i < len(lines)):
    if (lines[i].strip() == ""):
      lines[i] = spaceChar

    fieldName = ""
    fieldValue = ""
    symbolInLine = False
    for symbol in symbols:
      symbolInLine = symbol in lines[i]
      if (symbolInLine):
        break

    if ("@@" in lines[i]):
      fieldName = lines[i].split("@@")[1].split("\n")[0].strip()

    elif (not symbolInLine):
      fieldName = spaceChar if (fieldName == "") else fieldName
      fieldValue = lines[i] + "\n"
    
    if (fieldName != ""):
      i += 1
      j = i
      while (j < len(lines)):
        if (lines[j].strip() == ""):
          lines[j] = spaceChar

        symbolInLine = False
        for symbol in symbols:
          symbolInLine = symbol in lines[j]
          if (symbolInLine):
            break

        if ("@@" in lines[j]):
          i = j
          break

        elif (not symbolInLine):
          fieldValue += lines[j] + "\n"
          i = j + 1
          j = i

        else:
          i = j + 1
          break
    else:
      i += 1

    if (fieldName != "" and fieldValue != ""):
      newFields.append([fieldName, fieldValue])
    elif (fieldName != "" and fieldValue == ""):
      newFields.append([fieldName, spaceChar])
  # end while

  fields = newFields if (newFields != []) else fields
  if (len(newFields) != 0):
    embed.clear_fields()
    for field in fields:
      embed.add_field(name=field[0].replace("\\n", "\n"), value=field[1].replace("\\n", "\n"), inline=False)

  try:
    if (isEdit):
      await msg.edit(embed=embed)
      await message.channel.send("**Message Edited**", delete_after=5.0)
      if (isCollection or isReservation):
        await Collections.replaceCollectionEmbed(message, msg.id, msg.id, client)
    else:
      msg = await message.channel.send(embed=embed)
  except discord.errors.HTTPException:
    await message.channel.send("Looks like something didn't go quite right... Discord has a limit on how long a message can be, 2000 characters  ... but there is also a limit on how big a field value can be, 1024 characters. If you have a large field value, perhaps adding another field header, and splitting the field value might work.")
# end moBotEmbed

async def getRLStats(message, args):
  now = datetime.now()
  await message.channel.trigger_typing()

  platform = args[2]
  profile = message.content.split(platform)[1].strip().replace(" ", "%20")

  asession = AsyncHTMLSession()
  url = "https://rocketleague.tracker.network/profile/" + platform.replace("pc", "steam") + "/" + profile
  r = await asession.get(url)
  await message.channel.send("Web page recieved... rendering")
  await r.html.arender(timeout=16)
  await message.channel.send("Web page rendered...")

  ranks = {}

  #parsing stuff below
  parse = r.html.text.split("(Top")
  reply = ""
  highest = ["", 0]
  for i in range(1, len(parse)-2):
    if ("Ranked" in parse[i] and "-" not in parse[i]):
      if ("Grand Champion Division" in parse[i] or "Unranked Division" in parse[i] or "I Division I" in parse[i]):
        gameMode = parse[i].split("v")[0].split("\n")[-1][:-1].strip()
        rank = parse[i].split(gameMode)[1].split("\n")[0][5:].strip()
        mmr = int(parse[i].split("\n")[-2].strip().replace(",", ""))
        ranks[gameMode] = {
          "Rank" : "",
          "MMR" : 0
        }
        ranks[gameMode]["Rank"] = rank
        ranks[gameMode]["MMR"] = mmr
        reply += "Game Mode: " + gameMode + "\n" + "Rank: " + rank + "\n" + "MMR: " + str(mmr) + "\n\n"

        if (mmr > highest[1]):
          highest = [rank, mmr]

  reply += "Highest: " + highest[0] + ", " + str(highest[1])

  then = datetime.now()
  reply += "\n\nEllapsed Time: " + str(then - now)
  if (highest[0] == ""):
    await message.channel.send("URL: <" + url + ">```Something ain't right feller...```")
  else:
    await message.channel.send("URL: <" + url + ">```" + reply + "```")

  r.close()
# end getRLStats

async def rssTest(message):

  url = "https://noblecommunity.altervista.org/news/feed/"

  d = feedparser.parse(url)
  print(d)
# end rssTest

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open("power/kills")
  return workbook
  workbook = clientSS.open_by_key("14YQLkU7C8IuyLJXVZ9IIJZuYhnp5ezsZkeeyI-NUkQQ")
  workbook = clientSS.open_by_url("https://docs.google.com/spreadsheets/d/14YQLkU7C8IuyLJXVZ9IIJZuYhnp5ezsZkeeyI-NUkQQ/pubhtml?hl=en&widget=false&headers=false")
  return workbook
# end openSpreadsheet

print("Connecting...")
client.run(SecretStuff.getToken("MoBotTestDiscordToken.txt"))