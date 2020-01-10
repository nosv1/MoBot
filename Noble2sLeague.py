import discord
import asyncio
from datetime import datetime, timedelta
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials
import math
import random
from pytz import timezone
import json

import SecretStuff
import Collections
import RLRanks


moBot = 449247895858970624
ssIDs = {
  "2s League [XB1/PC]" : "1qzDGDOzgaqR7Mmsda-tE1tYn71oU52Gt1okEHqScEnU",
  "Noble Leagues Off-Season" : "1M8wij5yJXNplkRdrhIj-sMqfHBC8KmKHlFqyOCMaARw",
  "Noble Leagues Qualifiers" : "1Ut8QSZ48uB-H1wpE3-NxpPwBKLybkK-uo6Jb5LOSIxY",
  "Noble Leagues MoBot" : "1w-cme_ZtMIU3nesgGajc-5Y3eJX22Htwl_UIefG3E1Q",
}

## roles
registeredRole = 569198468472766475

## common channels
REGISTER_ID = 519317465604554772

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  # 209584832030834688 donation $5, 2 months
  '''donationDate = datetime(2019,5,22)
  donationAmount = 5
  days = int(donationAmount / 2) * 30
  expires = donationDate + timedelta(days=days)
  if (not message.author.bot):
    n = int(random.random() * 100) < 50
    if ("bot" in message.content and n and now < expires):
      await message.channel.send("Heh, <@296428962152841238> = bot\n||Courtesy of <@209584832030834688> :sunglasses:||")'''

  tCommandLog = message.guild.get_channel(578955177478848523)

  rlrankChannels = [575097423823634443, 580198212401496115] # mmr post, mobot trouble shooting
  if (message.channel.id in rlrankChannels and message.author.id == 424398041043435520): # if in #mmr-post and rl rank tracker
    await getMMR(message, None, tCommandLog)

  if (str(moBot) in args[0]):
    if (args[1] == "info"):
      await getTeamInfo(message, args)
    elif (args[1] == "submit"):
      await submitResultConfirm(message, client)
    elif (args[1].lower() == "registerid" or args[1].lower() == "changeid"):
      await registerID(None, message, args)
    elif (args[1].lower() == "nrt"):
      await sendNRT(message, args)

  if (args[0] == "!t"):
    if (args[1] == "delete"):
      workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
      if (len(args) == 2):
        await tDeleteTeam(message, tCommandLog, workbook)
      else:
        authorPerms = message.channel.permissions_for(message.author)
        manageMessagePerms = authorPerms.manage_messages
        if (manageMessagePerms):
          await tDeleteTeam(message, tCommandLog, workbook)
    elif (args[1] == "teams"):
      await tTeams(message, None)
    elif (args[1] == "leave"):
      await tLeave(message, tCommandLog)
    elif (args[1] == "help"):
      await tHelp(message)
    elif (args[1] == "register"):
      await tRegister(message, tCommandLog, await openSpreadsheet(ssIDs["Noble Leagues MoBot"]))
    elif (args[1] == "create"):
      await tCreateTeam(message, tCommandLog, await openSpreadsheet(ssIDs["Noble Leagues MoBot"]))
    elif (args[1] == "prefix"):
      await tPrefix(message, tCommandLog, await openSpreadsheet(ssIDs["Noble Leagues MoBot"]))
    elif (args[1] == "active"):
      await tActive(message, tCommandLog)
    elif (args[1] == "edit"):
      await tEdit(message, tCommandLog)
    elif (args[1] == "prefixstyle"):
      await tPrefixStyle(message, tCommandLog)
    elif (args[1] == "add"):
      await tAdd(message, tCommandLog)
    elif (args[1] == "remove"):
      await tRemove(message, tCommandLog)
    elif (args[1] == "team"):
      await tTeam(message)
    elif (args[1] == "captain"):
      await tCaptain(message, tCommandLog)

  if (args[0] == "!minor" or args[0] == "!major"):
    if (args[1].lower() == "checkin"):
      await tournamentCheckin(message)
    elif (args[1].lower() == "retire"):
      await tournamentRetire(message)
    else:
      await tournamentSignup(message)

  if (message.author.name == "Mo" and message.content == "test"):
    #await testing(message)
    pass

  await updateDailyGrowth(message)
# end main

async def mainReactionAdd(message, payload, client):
  leagueTableMessageId = 533690254029357056
  fixturesMessageId = 533699441572708353
  nobleStandingsMessageId = 565576417664958464
  seedingTableMessageId = 601174317933264917
  teamsListMessageId = 580202716635201556
  
  if (payload.emoji.name == "🔄"): # if update button is clicked
    workbook2sLeague = await openSpreadsheet(ssIDs["2s League [XB1/PC]"]) 
    workbookNobleOffSeason = await openSpreadsheet(ssIDs["Noble Leagues Off-Season"])
    if (message.id == leagueTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getLeagueTable(message, leagueTableMessageId, workbook2sLeague)
    elif (message.id == fixturesMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getFixtures(message, fixturesMessageId, workbook2sLeague)
    elif (message.id == nobleStandingsMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getNobleScore(message, nobleStandingsMessageId, workbookNobleOffSeason)
    elif (message.id == seedingTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getSeeding(message, workbookNobleOffSeason)
    elif (message.id == teamsListMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await tTeams(message, payload)

  elif (message.id == 640568528453369856): # Registration Verification
    if (payload.emoji.name == "✅"):
      await registerID(payload, message, [])
  
  elif (message.id == 600812373212921866): # Stream Scheduler
    if (payload.emoji.name == "✅" or payload.emoji.name == "❌"):
      await streamScheduler(message, payload, client)
      await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
    elif (payload.emoji.name == "🗑"):
      member = message.guild.get_member(payload.user_id)
      if (message.channel.permissions_for(member).administrator):
        await clearStreamScheduler(message, client)
      await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
  elif (message.author.id == 424398041043435520 and str(payload.user_id) != moBot): #Quantum Tracker aka RL STat Tracker
    tCommandLog = message.guild.get_channel(578955177478848523) # team log
    await getMMR(message, payload, tCommandLog)
#end mainReactionAdd
      
async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  # remove id from spreadsheet
  workbook = await openSpreadsheet(ssIDs["Noble Leagues Off-Season"])
  registerIDSheet = workbook.worksheet("RegisterID")
  nameIDs = registerIDSheet.range("B3:C" + str(registerIDSheet.row_count))

  for i in range(0, len(nameIDs), 2):
    if (nameIDs[i+1].value[-19:-1] == str(member.id)):
      nameIDs[i+1].value = ""
      #for j in range(i+2, len(nameIDs), 2):
        #nameIDs[j-2].value = nameIDs[j].value
        #nameIDs[j-1].value = nameIDs[j+1].value  
      registerIDSheet.update_cells(nameIDs, value_input_option="USER_ENTERED")
      break
# end memberRemove

async def memberRoleAdd(member, role):
  if (role.id == 519297202795839488): # if role == verified
    activityLog = member.guild.get_channel(445265120549928962)
    await activityLog.send("<@209584832030834688>, " + member.mention + " has been added to `Verified`.")
# end memberRoleAdd

async def sendNRT(message, args):
  await message.channel.trigger_typing()

  platform = args[2].replace("pc", "steam")
  id = " ".join(args[3:]).strip()
  mmrs, url = RLRanks.getMMRs(platform, id)
  try:
    nrt = getNRT(mmrs)
  except: # any errors should mean the id doesn't exist
    await message.channel.send("Something went wrong... Is the ID correct?")
    return

  if (nrt is None):
    await message.channel.send("Not enough MMRs to calculate NRT.\n%s" % url)

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(name="Noble Rank Tracker", icon_url=message.guild.icon_url)

  description = "ID: `%s`\n" % id
  description += "Platform: `%s`\n\n" % platform
  description += "Season %s 2s: `%s`\n" % (nrt.last2.season, nrt.last2.mmr)
  description += "Season %s 3s: `%s`\n" % (nrt.last3.season, nrt.last3.mmr)
  description += "Season %s 2s (Peak): `%s`\n" % (nrt.peak2.season, nrt.peak2.mmr)
  description += "Season %s 3s (Peak): `%s`\n\n" % (nrt.peak3.season, nrt.peak3.mmr)
  description += "**NRT: `%s`**\n" % nrt.nrt
  description += "[__Tracker__](%s)" % url
  embed.description = description

  await message.channel.send(embed=embed)
# end sendNRT

def getNRT(mmrs): # mmrs are got from rlranks.getMMRs(platform, id)
  class NRT:
    def __init__(self):
      self.peak2 = MMR(0, 0, 0) # starting with current season, otherwise get past season
      self.peak3 = MMR(0, 0, 0)

      self.last2 = MMR(0, 0, 0) # starting from last season
      self.last3 = MMR(0, 0, 0)

      self.avg = 0
      self.nrt = 0
  # end NRT

  class MMR:
    def __init__(self, mmr, season, mode):
      self.mmr = mmr
      self.season = season
      self.mode = mode
  # end MMR
  
  nrt = NRT()
  seasons = list(mmrs.keys())

  '''
  nrt = 
  50% of peak 2s MMR current season OR 2s final MMR last season.
  25% of peak 3s MMR current season OR 3s final MMR last season.
  25% of highest final MMR from last season in 2s OR 3s
  '''

  # get first and second bit
  def getPeak(mode):
    if (mmrs[seasons[0]][mode]["peak"] != 0):
      return MMR(mmrs[seasons[0]][mode]["peak"], seasons[0], mode)
    else:
      for season in seasons[1:]:
        if (mmrs[season][mode]["current"] != 0):
          return MMR(mmrs[season][mode]["current"], season, mode)
  # end getPeakCurrent

  nrt.peak2 = getPeak(2)
  nrt.peak3 = getPeak(3)

  # get second bit
  def getLast(season, mode):  
    for season in seasons[seasons.index(season)+1:]:
      if (mmrs[season][mode]["current"] != 0):
        return MMR(mmrs[season][mode]["current"], season, mode)
  # end getLast

  nrt.last2 = getLast(nrt.peak2.season, 2)
  nrt.last3 = getLast(nrt.peak3.season, 3)

  try:
    twos = nrt.peak2.mmr if nrt.peak2.mmr > nrt.last2.mmr else nrt.last2.mmr
    threes = nrt.peak3.mmr if nrt.peak3.mmr > nrt.last3.mmr else nrt.last3.mmr
    last = nrt.last2.mmr if nrt.last2.mmr > nrt.last3.mmr else nrt.last3.mmr
  except AttributeError: # when mmrs don't exist
    return None

  if (min([nrt.peak2.mmr, nrt.peak3.mmr, nrt.last2.mmr, nrt.last3.mmr]) >= 1000):
    nrt.avg = .5 * twos + .25 * threes + .25 * last
    nrt.nrt = (nrt.avg-1000)/10
  else:
    nrt.nrt = 0
  return nrt
# end getNRT

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

async def setnick(message):
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  players = referencesSheet.range("G2:I" + str(referencesSheet.row_count))
  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))
  registerees = referencesSheet.range("C2:D" + str(referencesSheet.row_count))

  newNick = message.content.split("nick ")[1].strip()

  user = message.author
  await user.edit(nick=newNick)

  for i in range(0, len(players), 3):
    if (players[i].value == str(user.id)):
      prefix = prefixes[int(i/3)].value
      for k in range(0, len(registerees), 2):
        if (registerees[k].value == str(user.id)):
          await updatePrefix(user, registerees, k, prefix, True)
          break
      break

  msg = await message.channel.send("```Nickname Updated```")
  await asyncio.sleep(3)
  await message.delete()
  await msg.delete()
# end setnick

async def updateDailyGrowth(message):
  now = message.created_at + timedelta(hours=1)
  today = datetime(now.year, now.month, now.day)
  
  activityLog = message.guild.get_channel(445265120549928962)
  history = await activityLog.history(after=today).flatten()

  joined = 0
  left = 0
  for msg in history:
    try:
      if (msg.author.name == "Dyno"):
        embed = msg.embeds[0].to_dict()
        if (embed["author"]["name"] == "Member Joined"):
          joined += 1
        elif (embed["author"]["name"] == "Member Left"):
          left += 1
    except IndexError:
      continue
  
  growth = joined - left
  if (growth >= 0):
    growth = "+" + str(growth)
  else:
    growth = str(growth)
  
  channels = message.guild.channels
  for channel in channels:
    if ("Today's Growth: " in channel.name):
      newName = "Today's Growth: " + growth
      if (newName != channel.name):
        await channel.edit(name=newName)
      break
# end updateDailyGrowth

async def updatePlayerIDs():
  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  playerIds = referencesSheet.range("C2:C" + str(referencesSheet.row_count))

  for i in range(len(playerIds)):
    playerIds[i].value = ""
  referencesSheet.update_cells(playerIds, value_input_option="USER_ENTERED")
# end updatePlayerIDs

async def getMMR(message, payload, tCommandLog):
  if (payload is None and len(message.embeds) > 0):
    await message.channel.trigger_typing()
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    await message.channel.send("**Is this you?**\nIf the above player MMRs are your own, please click the ✅. Note this will lock your MMR for the entire season.\n\nTo cancel click the ❌.")
  elif (payload.emoji.name == "✅"):
    await message.channel.trigger_typing()
    embed = message.embeds[0].to_dict()
    solo = embed["fields"][0]["value"].split("-")[1].split("\n")[0]
    doubles = embed["fields"][1]["value"].split("-")[1].split("\n")[0]
    soloStandard = embed["fields"][2]["value"].split("-")[1].split("\n")[0]
    standard = embed["fields"][3]["value"].split("-")[1].split("\n")[0]
    userId = payload.user_id
    
    workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
    teamRange, leagueSheet, teamRangeCols = getLeagueSheet(workbook)
    registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)

    for i in range(0, len(teamRange), teamRangeCols):
      if (teamRange[i].value != ""):
        for j in range(i, i+teamRangeCols):
          if (getUserName(str(userId), registeredIDsRange) == teamRange[j].value):
            try:
              teamRange[j+1].value = str(max([int(solo), int(doubles), int(soloStandard), int(standard)]))
            except ValueError:
              await message.channel.send("**Could Not Submit MMRs**\nMake sure you are using the correct command - `rlrank`.")
              return None
            await message.channel.send(content="**MMRs Submitted**", delete_after=5)
            leagueSheet.update_cells(teamRange, value_input_option="USER_ENTERED")
            return None
      else:
        await message.channel.send("**MMRs Not Submitted**\nUser is not on a team. This is only for league players - join a team, then use this command.")
        break

  elif (payload.emoji.name == "❌"):
    await message.clear_reactions()
# end getMMR

async def updatePrefix(user, registerees, index, prefix, manualChange):
  if (not manualChange):
    prefixType = registerees[index+1].value
    prefixEdit = ""
    if (prefixType == "bar - team"):
      prefixEdit = prefix + " | "
    elif (prefixType == "bracket - team"):
      prefixEdit = "[" + prefix + "] "
    userNick = user.nick
    userName = user.name
    if (userNick != None):
      if ("| " in userNick):
        userNick = userNick.split("| ")[1]
      elif ("] " in userNick):
        userNick = userNick.split("] ")[1]
      await user.edit(nick=(prefixEdit + userNick))
    else:
      await user.edit(nick=(prefixEdit + userName))
# end updatePrefix

async def tHelp(message):
  await message.channel.trigger_typing()
  reply = "All !t Commands:"
  reply += "\n\t!t create team_name\n\t\tcreates a new team (one team per captain)"
  reply += "\n\t!t prefix new_prefix\n\t\t(captains only) updates their team's prefix"
  reply += "\n\t!t edit new_team_name\n\t\t(captains only) updates their team's name"
  reply += "\n\t!t delete\n\t\t(captains only) deletes their team"
  reply += "\n\t!t add @user (@user)\n\t\t(captains only) adds the given users to their team (max 3 on a team) Use '!t team team_name (or prefix)' to see who's on your team."
  reply += "\n\t!t remove @user (@user)\n\t\t(captains only) removes the given users from their team"
  reply += "\n\t!t leave\n\t\tremoves the user from their team"
  reply += "\n\t!t active team_name (or prefix)\n\t\tsets the user's prefix to their team's prefix or no prefix, if team_name is 'No Prefix' (without quotes)"
  reply += "\n\t!t prefixstyle 1 (or 2)\n\t\tupdates the user's prefixstyle to (1) 'prefix | user_name'  or (2) '[prefix] user_name'"
  reply += "\n\t!t teams\n\t\treturns a list of the teams"
  reply += "\n\t!t team team_name (or prefix)\n\t\treturns the details of a given team"
  reply += "\n\nCaptains are the people that create the team. If the captain leaves a team, the next person that was added will be the captain of that team."
  await message.channel.send("```" + reply + "```")
# end tHelp

async def tCaptain(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  captains = referencesSheet.range("G2:G" + str(referencesSheet.row_count))
  players = referencesSheet.range("H2:I" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))

  personToSwap = message.content.split("<@")[1].strip()[-19:-1]
  personToSwap = message.guild.get_member(int(personToSwap))

  currentCaptain = message.author

  captainExists = False
  playerExists = False
  for i in range(0, len(captains)):
    if (captains[i].value == str(currentCaptain.id)):
      captainExists = True
      for j in range(i * 2, i * 2 + 2):
        if (players[j].value == str(personToSwap.id)):
          playerExists = True
          players[j].value = str(currentCaptain.id)
          captains[i].value = str(personToSwap.id)

          referencesSheet.update_cells(captains, value_input_option="USER_ENTERED")
          referencesSheet.update_cells(players, value_input_option="USER_ENTERED")

          moBotMessages.append(await message.channel.send("```Captain has been updated.```"))
          await tCommandLog.send("<@" + str(currentCaptain.id) + "> has assigned <@" + str(personToSwap.id) + "> as captain on [" + teams[i].value + "].")
          break
      break

  if (not captainExists):
    moBotMessages.append(await message.channel.send("```You are not a captain of a team. Only captains can assign a new captain.```"))
  elif (not playerExists):
    moBotMessages.append(await message.channel.send("```The player you are trying to assign captain != on your team. Add him/her to your team, then try again.```"))

  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end help

async def tRemove(message, tCommandLog):  
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  captains = referencesSheet.range("G2:G" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))

  users = message.content.split("<@")
  for i in range(1, len(users)):
    try:
      userId = int(users[i].split(">")[0][-18:])
    except:
      userId = int(users[i].split(">")[0][-17:])
    user = message.guild.get_member(int(userId))
    users[i-1] = user
  del users[len(users)-1]

  captain = message.author
  captainExists = False
  for i in range(len(captains)):
    if (captains[i].value == str(captain.id)):
      captainExists = True
      team = referencesSheet.range(i+2, 7, i+2, 9)
      for user in users:
        onTeam = False
        for j in range(len(team)):
          if (team[j].value == str(user.id)):
            onTeam = True
            team[j].value = ""
            referencesSheet.update_cells(team, value_input_option="USER_ENTERED")
            if (user.nick != None):
              userNick = user.nick
              if (" | " in userNick):
                userNick = userNick.split(" | ")[1]
                await user.edit(nick=userNick)
              if ("] " in userNick):
                userNick = userNick.split("] ")[1]
              try:
                moBotMessages.append(await message.channel.send("```" + user.nick + " has been removed.```"))
              except TypeError:
                moBotMessages.append(await message.channel.send("```" + user.name + " has been removed.```"))
              await tCommandLog.send("<@" + str(captain.id) + "> has added <@" + str(user.id) + "> to his/her team - " + teams[i]) 

            else:
              moBotMessages.append(await message.channel.send("```" + user.name + " has been removed.```"))
        if (not onTeam):
          if (user.nick != None):
            moBotMessages.append(await message.channel.send("```" + user.nick + " is not on your team.```"))
          else:
            moBotMessages.append(await message.channel.send("```" + user.name + " is not on your team.```"))
  if (not captainExists):
    moBotMessages.append(await message.channel.send("```You cannot remove someone from a team that you did not create.```"))

  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tRemove

async def tLeave(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  players = referencesSheet.range("G2:I" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))

  user = message.author
  playerExists = False
  for i in range(len(players)):
    if (players[i].value == str(user.id)):
      teamName = teams[int(i/3)].value
      playerExists = True
      isCaptain = i % 3 == 0
      team = referencesSheet.range(int(i/3) + 2, 5, int(i/3) + 2, 9)
      if (isCaptain):
        if (team[3].value == "" and team[4].value == ""):
          for j in range(len(team)):
            team[j].value = ""
            await tDeleteTeam(message, None, tCommandLog)
            break
          break
        elif (team[3].value != ""):
          team[2].value = team[3].value
          team[3].value = ""
          captain = message.guild.get_member(int(team[2].value))
          if (captain.nick != None):
            moBotMessages.append(await message.channel.send("```" + captain.nick + " is now the captain.```"))
          else:
            moBotMessages.append(await message.channel.send("```" + captain.name + " is now the captain.```"))
        else:
          team[2].value = team[4].value
          team[4].value = ""

      players[i].value = ""
      if (user.nick != None):
        userNick = user.nick
        if (" | " in userNick):
          userNick = userNick.split(" | ")[1]
          await user.edit(nick=userNick)
        if ("] " in userNick):
          userNick = userNick.split("] ")[1]
      moBotMessages.append(await message.channel.send("```You have left your team.```"))
      await tCommandLog.send("<@" + str(user.id) + "> has left " + teamName + ".")
      referencesSheet.update_cells(players, value_input_option="USER_ENTERED")
      referencesSheet.update_cells(team, value_input_option="USER_ENTERED")
      break

  if (not playerExists):
    moBotMessages.append(await message.channel.send("```You cannot leave a team if you are not on one.```"))
  
  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tLeave

async def tTeams(message, payload):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")
  
  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))

  reply = "Teams: \n  "
  for i in range(len(teams)):
    if (teams[i].value != ""):
      reply += prefixes[i].value + " - " + teams[i].value + "\n  "

  if (payload == None):
    moBotMessages.append(await message.channel.send("```" + reply[:-3] + "```"))
  else:
    await message.edit(content="```" + reply[:-3] + "```")
    del moBotMessages[0]
    moBotMessages.append(await message.channel.send("```Teams List Updated```"))

  await asyncio.sleep(15)
  await deleteMoBotMessages(moBotMessages)
# end tTeams

async def tTeam(message):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  searchFor = message.content.split("team ")[1].strip()

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))
  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))

  teamExists = False
  for i in range(len(prefixes)):
    if (prefixes[i].value.lower() == searchFor.lower() or teams[i].value.lower() == searchFor.lower()):
      teamExists = True
      team = referencesSheet.range(i+2, 5, i+2, 9)
      reply = "Team: " + team[1].value
      reply += "\nPrefix: " + team[0].value
      reply += "\nPlayers: \n  "
      for j in range(2, len(team)):
        if (team[j].value != ""):
          user = message.guild.get_member(int(team[j].value))
          if (user != None):
            if (user.nick != None):
              reply += user.nick + "\n  "
            else:
              reply += user.name + "\n  "
      reply = reply[:-3]
      moBotMessages.append(await message.channel.send("```" + reply + "```"))
  if (not teamExists):
    moBotMessages.append(await message.channel.send("```The team you searched for was not found. Feel free to use the prefix or the team name.```"))

  await asyncio.sleep(10)
  await deleteMoBotMessages(moBotMessages)
# end tTeam

async def tAdd(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  captains = referencesSheet.range("G2:G" + str(referencesSheet.row_count))
  players = referencesSheet.range("G2:I" + str(referencesSheet.row_count))
  registerees = referencesSheet.range("C2:D" + str(referencesSheet.row_count))
  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))

  users = message.content.split("<@")
  for i in range(1, len(users)):
    try:
      userId = int(users[i].split(">")[0][-18:])
    except:
      userId = int(users[i].split(">")[0][-17:])
    user = message.guild.get_member(int(userId))
    users[i-1] = user
  del users[len(users)-1]

  captain = message.author
  captainExists = False
  for i in range(len(captains)):
    if (captains[i].value == str(captain.id)):
      captainExists = True
      alreadyOnTeam = False
      for user in users:
        for j in range(len(players)):
          if (players[j].value == str(user.id)):
            alreadyOnTeam = True
            if (user.nick != None):
              moBotMessages.append(await message.channel.send("```" + user.nick + " is already on a team.```"))
            break
        if (not alreadyOnTeam):
          team = referencesSheet.range(i+2, 7, i+2, 9)
          memberAdded = False
          for j in range(len(team)):
            if (team[j].value == ""):
              memberAdded = True
              team[j].value = str(user.id)
              registereeExists = False
              for k in range(0, len(registerees), 2):
                if (registerees[k].value == str(user.id)):
                  registereeExists = True
                  await updatePrefix(user, registerees, k, prefixes[i].value, False)
                  break
              if (not registereeExists):
                registerIDChannel = message.guild.get_channel(519317465604554772)
                await registerIDChannel.send("<@" + str(user.id) + ">, you have been added to a team but you have not registered an ID. Please use `@MoBot#0697 registerID input_name` to register. Replace `input_name` with a name of your choice.")
              if (user.nick != None):
                moBotMessages.append(await message.channel.send("```" + user.nick + " has been added.```"))
              else:
                moBotMessages.append(await message.channel.send("```" + user.name + " has been added.```"))
              await tCommandLog.send("<@" + str(captain.id) + "> has added <@" + str(user.id) + "> to his/her team - " + teams[i].value) 
              referencesSheet.update_cells(team, value_input_option="USER_ENTERED")
              break
          if (not memberAdded):
            if (user.nick != None):
              moBotMessages.append(await message.channel.send("```Cannot add " + user.nick + ". Team is full.```"))
            else:
              moBotMessages.append(await message.channel.send("```Cannot add " + user.name + ". Team is full.```"))


  if (not captainExists):
    moBotMessages.append(await message.channel.send("```You cannot add users to a team if you did not create one.```"))
  
  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tAdd

async def tPrefixStyle(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  prefixStyle = message.content.split("prefixstyle")[1].strip()

  prefixStyles = {
    "1" : "bar", 
    "2" : "bracket"
    }

  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))
  registerees = referencesSheet.range("C2:D" + str(referencesSheet.row_count))
  players = referencesSheet.range("G2:I" + str(referencesSheet.row_count))

  user = message.author
  registereeExists = False
  badStyle = False
  for i in range(0, len(registerees), 2):
    if (registerees[i].value == str(user.id)):
      registereeExists = True
      currentPrefixStyle = registerees[i+1].value.split(" -")[0]
      try:
        registerees[i+1].value = registerees[i+1].value.replace(currentPrefixStyle, prefixStyles[prefixStyle])
        referencesSheet.update_cells(registerees, value_input_option="USER_ENTERED")
        await tCommandLog.send("<@" + str(user.id) + "> has updated his/her prefix style to " + prefixStyles[prefixStyle])
        moBotMessages.append(await message.channel.send("```Prefix style upated.```"))
      except KeyError:
        moBotMessages.append(await message.channel.send("```Prefix style does not exist.\n!t prefixstyle 1 for NG | Noble Gaming\n!t prefixstyle 2 for [NG] Noble Gaming```"))
        badStyle = True
      break

  if (registereeExists):
    if (not badStyle):
      playerExists = False
      for i in range(len(players)):
        if (players[i].value == str(user.id)):
          playerExists = True
          prefix = prefixes[int(i/3)].value
          for j in range(0, len(registerees), 2):
            if (registerees[j].value == str(user.id)):
              await updatePrefix(user, registerees, j, prefix, False)
              moBotMessages.append(await message.channel.send("```Prefix updated.```"))
              break
          break

    if (not playerExists):
      moBotMessages.append(await message.channel.send("```You are not currently on a team. Current prefix has not been udpated.```"))

  else:
    moBotMessages.append(await message.channel.send("```To change prefix type, you must register an ID first. To register, use @MoBot#0697 registerID input_name```"))

  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tPrefixStyle

async def tActive(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  teamName = message.content.split("active ")[1].strip()

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  prefixes = referencesSheet.range("E2:E" + str(referencesSheet.row_count))
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))
  registerees = referencesSheet.range("C2:D" + str(referencesSheet.row_count))

  user = message.author
  if (teamName.lower() == "no prefix"):
    if (user.nick != None):
      userNick = user.nick
      if (" | " in userNick):
        userNick = userNick.split(" | ")[1]
        await user.edit(nick=userNick)
      if ("] " in userNick):
        userNick = userNick.split("] ")[1]
        await user.edit(nick=userNick)

    await tCommandLog.send("<@" + str(user.id) + ">" + " has deactivated their prefix.")
    moBotMessages.append(await message.channel.send("```Prefix removed.```"))

    for i in range(0, len(registerees), 2):
      if (registerees[i].value == str(user.id)):
        registerees[i+1].value = registerees[i+1].value.replace("team", "none")
        break

  else:
    teamExists = False
    for i in range(len(teams)):
      if (teams[i].value.lower() == teamName.lower() or prefixes[i].value.lower() == teamName.lower()):
        teamExists = True
        prefix = prefixes[i].value

        players = referencesSheet.range(i+2, 7, i+2, 9)  
        playerExists = False
        for j in range(len(players)):
          if (players[j].value == str(user.id)):
            playerExists = True

            for k in range(0, len(registerees), 2):
              if (registerees[k].value == str(user.id)):
                registerees[k+1].value = registerees[k+1].value.replace("none", "team")
                await updatePrefix(user, registerees, k, prefix, False)
                await tCommandLog.send("<@" + str(user.id) + "> has activated " + teams[i].value + "'s prefix.")
                moBotMessages.append(await message.channel.send("```Team activated.```"))
                break
            break

        if (not playerExists):
          moBotMessages.append(await message.channel.send("```Cannot activate this team. You are not a member.```"))
        break

    if (not teamExists):
      moBotMessages.append(await message.channel.send("```Team does not exist.```"))

  referencesSheet.update_cells(registerees, value_input_option="USER_ENTERED")

  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tActive

async def tPrefix(message, tCommandLog, workbook):
  await message.channel.trigger_typing()
  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)
  teamRange, leagueSheet, teamRangeCols = getLeagueSheet(workbook)
  headersRange = leagueSheet.range("A1:K1")

  prefix = message.content.split("prefix")[-1].strip()

  for i in range(len(headersRange)):
    if (headersRange[i].value == "Captain"):
      for j in range(0, len(teamRange), teamRangeCols):
        if (teamRange[j].value != ""):
          if (getRegisteredID(teamRange[j+i].value, registeredIDsRange) == message.author.id): # if captain
            teamRange[j+1].value = prefix
            await updatePrefixes(message, prefix, teamRange, teamRangeCols, j, leagueSheet, registeredIDsRange)
            await message.channel.send("**Prefix Updated**")
            leagueSheet.update_cells(teamRange, value_input_option="USER_ENTERED")
            break
        else:
          await message.channel.send("**Could Not Update Prefix**\nYou are not a captain of a team, to register a team, use the command `!t register @Captain @Player @Sub_1 @Sub_2` - @Sub_2 is optional.")
          break
      break
# end tPrefix

async def tEdit(message, tCommandLog):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Qualifiers"])
  referencesSheet = workbook.worksheet("Noble Teams")

  teamName = ""
  for part in message.content.split("edit ")[1].strip().split(" "):
    teamName += part + " "
  teamName = teamName[:-1]
  
  teams = referencesSheet.range("F2:F" + str(referencesSheet.row_count))
  captains = referencesSheet.range("G2:G" + str(referencesSheet.row_count))
  
  teamExists = False
  for i in range(len(teams)):
    if (teams[i].value.lower() == teamName.lower()):
      teamExists = True
      moBotMessages.append(await message.channel.send("```Team name already exists.```"))
      break

  if (not teamExists):
    user = message.author
    captainExists = False
    for i in range(len(captains)):
      if (captains[i].value == str(user.id)):
        captainExists = True
        teams[i].value = teamName
        await tCommandLog.send("<@" + str(user.id) + "> has edited his/her team's name.\nNew Team Name: " + teamName)
        moBotMessages.append(await message.channel.send("```Team has been edited.```"))
        referencesSheet.update_cells(teams, value_input_option="USER_ENTERED")
    if (not captainExists):
      moBotMessages.append(await message.channel.send("```Cannot edit a team that you did not create.```"))

  await asyncio.sleep(5)
  await deleteMoBotMessages(moBotMessages)
# end tEdit

async def tDeleteTeam(message, tCommandLog, workbook):
  await message.channel.trigger_typing()
  moBotMessages = [message]

  workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
  teamRange, leagueSheet, teamRangeCols = getLeagueSheet(workbook)
  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)
  headersRange = leagueSheet.range("A1:K1")

  if ("<@" in message.content):
    captainID = message.content.split("delete")[-1].replace("!", "").split("@")[1][:-1].strip()
  else:
    captainID = message.author.id

  for i in range(len(headersRange)):
    if (headersRange[i].value == "Captain"):
      for j in range(0, len(teamRange), teamRangeCols):
        if (teamRange[j].value != ""):
          tempCaptainID = getRegisteredID(teamRange[j+i].value, registeredIDsRange)
          if (tempCaptainID == int(captainID)): # if captain
            await updatePrefixes(message, "", teamRange, teamRangeCols, j, leagueSheet, registeredIDsRange)
            teamName = teamRange[j].value
            for k in range(j+teamRangeCols, len(teamRange), teamRangeCols):
              if (teamRange[k-teamRangeCols].value != ""):
                for l in range(k, k+teamRangeCols):
                  teamRange[l-teamRangeCols].value = teamRange[l].value
              else:
                await message.channel.send("**Team Deleted**")
                await tCommandLog.send("%s deleted a team - %s." % (message.author.mention, teamName))
                leagueSheet.update_cells(teamRange, value_input_option="USER_ENTERED")
                break
            break
        else:
          await message.channel.send("**Could Not Delete Team**\nYou are either not a captain for the team you're trying to delete, or, if you're an admin, then the provided user is not a captain. ")
          break
      break
# end tDeleteTeam

async def tCreateTeam(message, tCommandLog, workbook):
  await message.channel.trigger_typing()
  teamRange, leagueSheet, teamRangeCols = getLeagueSheet(workbook)

  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)
  teamName = message.content.split("create")[1].strip()

  i = 0
  teamExists = True
  while (teamExists):
    if (teamRange[i].value.lower() == teamName.lower() and teamExists): # team exists?
      await message.channel.send("**Cannot Create Team**\nTeam name already exists.")
      return None
    elif (teamRange[i+3].value == getUserName(message.author.id, registeredIDsRange)): # author is captain?
      prefix = getPrefixFromTeamName(teamName)
      teamRange[i+0].value = teamName
      teamRange[i+1].value = prefix
      await updatePrefixes(message, prefix, teamRange, teamRangeCols, i, leagueSheet, registeredIDsRange)
      await message.channel.send("**Team Name and Prefix Updated**\nTo change the team's prefix, use the command `!t prefix [new_prefix]`")
      leagueSheet.update_cells(teamRange, value_input_option="USER_ENTERED")
      break

    if (teamRange[i].value == ""): # reached end, no team found
      teamExists = False
      await message.channel.send("**Cannot Create/Edit Team**\nThe team does not exist, or you are not a captain.")

    i += teamRangeCols
  # end while
#end tCreateTeam

async def updatePrefixes(message, prefix, teamRange, teamRangeCols, index, leagueSheet, registeredIDsRange):
  headers = leagueSheet.range("A2:K2")
  for i in range(0, teamRangeCols):
    if (headers[i].value == "ID"):
      if (teamRange[index+i].value != ""):
        user = message.guild.get_member(getRegisteredID(teamRange[index+i].value, registeredIDsRange))
        if (prefix != ""):
          await user.edit(nick="%s | %s" % (prefix, user.display_name.split(" | ")[-1]))
        else:
          await user.edit(nick="%s" % (user.display_name.split(" | ")[-1]))
# end updatePrefixes
    
def getPrefixFromTeamName(teamName):
  prefix = ""
  if (" " in teamName):
    for word in teamName.split(" "):
      prefix += word[0]
  else:
    prefix = teamName
  return prefix
# end getPrefixFromTeamName

async def tRegister(message, tCommandLog, workbook):
  await message.channel.trigger_typing()

  teamRange, leagueSheet, teamRangeCols = getLeagueSheet(workbook)
  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)

  users = message.content.replace("!", "").split("<@")
  for i in range(1, len(users)):
    userId = int(users[i].split(">")[0])
    users[i] = message.guild.get_member(int(userId))
    if (not checkIfRegistered(users[i], registeredIDsRange)):
      await message.channel.send("Not Registered - " + users[i].mention)
      users[i] = False
  del users[0]

  if (len(users) < 3 or len(users) > 4):
    await message.channel.send("**Cannot Complete Registration**\nA team must have at least 2 players and a sub - a 2nd sub is optional. Use the command `!t register @Captain @Player @Sub_1 (@Sub_2)` - the @Sub_2 is optional.")

  elif (False in users):
    await message.channel.send("**Cannot Complete Registration**\nEach player on the team must be registered with @MoBot#0697. A user can register by using the command `@MoBot#0697 registerID [username]` - replace [username]")

  else:
    for i in range(0, len(teamRange), teamRangeCols):
      if (teamRange[i].value != ""):
        for user in users:
          for j in range(i, i+teamRangeCols):
            if (getUserName(user.id, registeredIDsRange) == teamRange[j].value):
              await message.channel.send("**Cannot Complete Registration**\n%s is already on a team.\nTeam Name: %s\nCaptain: %s" % (user.mention, teamRange[i], message.guild.get_member(getRegisteredID(teamRange[j].value, registeredIDsRange)).mention))
              return None
      else:
        tbdNumber = i // teamRangeCols + 1
        teamRange[i+0].value = "TBD %s" % (tbdNumber)
        teamRange[i+1].value = "TBD %s" % (tbdNumber)
        teamRange[i+2].value = "BAR"
        teamRange[i+3].value = getUserName(message.author.id, registeredIDsRange)
        playerCount = 0
        for user in users:
          if (user.id != message.author.id):
            teamRange[i+5+(playerCount*2)].value = getUserName(user.id, registeredIDsRange)
            playerCount += 1

        for user in users:
          for role in message.guild.roles:
            if (role.id == 575935641892945920): # League Players Role
              await user.add_roles(role)
              await tCommandLog.send("<@" + str(message.author.id) + "> registered <@" + str(user.id) + ">")
              break
          await user.edit(nick="TBD %s | %s" % (tbdNumber, user.display_name.split(" | ")[-1].strip()))
        await message.channel.send("**Registration Complete**\nTo set your team name, use the command `!t create [Team_Name]`")
        leagueSheet.update_cells(teamRange, value_input_option="USER_ENTERED")
        break
# end tRegister

def getLeagueSheet(workbook):
  leagueSheet = workbook.worksheet("League")
  teamRange = leagueSheet.range("A3:K" + str(leagueSheet.row_count))
  teamRangeCols = 11
  return teamRange, leagueSheet, teamRangeCols
# end getLeagueSheet

async def testing(message):
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet(ssIDs["Noble Leagues Off-Season"])
  registerIDSheet = workbook.worksheet("RegisterID")

  activityLog = message.guild.get_channel(445265120549928962)
  history = await activityLog.history(limit=100000).flatten()
  dates = []
  for message in history:
      try:
        if (message.author.name == "Dyno"):
          embed = message.embeds[0].to_dict()
          if (embed["author"]["name"] == "Member Left"):
            dates.append(str(message.created_at))
            print(message.created_at)
      except IndexError:
        continue

  print(len(dates))
  r = registerIDSheet.range("R1:R" + str(len(dates)))
  for i in range(len(r)):
    r[i].value = dates[i]
  registerIDSheet.update_cells(r, value_input_option="USER_ENTERED")
# end testing

async def registerID(payload, message, args):
  moBotMessages = [message] if payload == None else []
  await message.channel.trigger_typing()
  workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
  registerIDSheet = workbook.worksheet("RegisterID")
  nameIDs = registerIDSheet.range("A2:B" + str(registerIDSheet.row_count))

  if (payload == None):
    userId = message.author.id # in format @MoBot registerid name
    if (message.content.count("<@") > 1):
      registerName = message.author.display_name
    else:
      registerName = ""
      for i in range(2, len(args)):
        registerName += args[i].strip() + " "
      registerName = registerName[:-1]
  else:
    userId = payload.user_id
    registerName = message.guild.get_member(userId).display_name

  idNotPresent = True
  nameNotPresent = True
  idLocation = -1

  # checking for previous entries
  for i in range(0, len(nameIDs), 2):
    try:
      if (str(userId) == nameIDs[i+1].value):
        idNotPresent = False
        idLocation = i+1
        if (args[1].lower() == "registerid"):
          nameNotPresent = False
          if (payload == None):
            moBotMessages.append(await message.channel.send("**Cannot Register ID**\nYour ID is already registered; if you would like to change your name, use `@MoBot#0697 changeID new_name`"))
          break

      if (registerName.lower() == nameIDs[i].value.lower()):
        nameNotPresent = False
        if (payload == None):
          moBotMessages.append(await message.channel.send("**Cannot Register ID**\n%s name is already taken." % (registerName)))
        else:
          moBotMessages.append(await message.channel.send("**Cannot Register ID**\n%s name is already taken. To register your ID, go to <#%s>, and then use `@MoBot#0697 registerID name`."))
        break
    except IndexError: # hits the end of the names and tries to parse a blank value
      pass

  # adding new registeree
  if (idNotPresent and nameNotPresent):
    for i in range(0, len(nameIDs), 2):
      if (nameIDs[i].value == ""):
        nameIDs[i].value = registerName.strip()
        nameIDs[i+1].value = str(userId)
        break
    moBotMessages.append(await message.channel.send("**ID Registered as %s**\nIf you want to change your ID use `@MoBot#0697 changeID new_name`." % (registerName)))
    await message.guild.get_channel(569196829137305631).send("<@" + str(userId) + "> has registered their ID with " + registerName.strip() + ".")

  # changing name
  if (not(idNotPresent) and nameNotPresent):
    if (payload is None):
      nameIDs[idLocation - 1].value = registerName
      moBotMessages.append(await message.channel.send("**ID Updated**"))
      await message.guild.get_channel(569196829137305631).send("<@" + str(userId) + "> has changed their ID to " + registerName + ".")
  
  registerIDSheet.update_cells(nameIDs, value_input_option="USER_ENTERED")

  if (payload is not None):
    await asyncio.sleep(3)
    await deleteMoBotMessages(moBotMessages)
# end register

def getRegisteredIDRange(workbook):
  registeredIDsSheet = workbook.worksheet("RegisterID")
  registeredIDsRange = registeredIDsSheet.range("A2:B" + str(registeredIDsSheet.row_count))
  return registeredIDsRange, registeredIDsSheet
# end getRegisteredIDRange

def checkIfRegistered(member, registeredIDsRange):
  for i in range(len(registeredIDsRange)):
    if (str(member.id) in registeredIDsRange[i].value):
      return True
  return False
# end checkIfRegistered

def getRegisteredID(name, registeredIDsRange):
  for i in range(len(registeredIDsRange)):
    if (name == registeredIDsRange[i].value):
      return int(registeredIDsRange[i+1].value)
# end getRegisteredID

def getUserName(memberID, registeredIDsRange):
  for i in range(len(registeredIDsRange)):
    if (str(memberID) in registeredIDsRange[i].value):
      return registeredIDsRange[i-1].value
# end getUserName

async def tournamentCheckin(message):
  await message.channel.trigger_typing()
  workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
  signupSheet = workbook.worksheet("Minor") if ("!minor" in message.content) else workbook.worksheet("Major")

  signupRange = signupSheet.range("B2:D" + str(signupSheet.row_count))
  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)

  for i in range(0, len(signupRange), 3):
    for j in range(i, i+2):
      if (signupRange[j].value == getUserName(message.author.id, registeredIDsRange)):
        signupRange[i+2].value = "=TRUE"
        await message.channel.send("**Checked In**")
        registerLog = message.guild.get_channel(569196829137305631)
        await registerLog.send("%s and %s have checked in for the %s tournament." % (message.guild.get_member(getRegisteredID(signupRange[i].value, registeredIDsRange)).mention, message.guild.get_member(getRegisteredID(signupRange[i+1].value, registeredIDsRange)).mention, message.content.split(" ")[0].split("!")[1].strip()))
        signupSheet.update_cells(signupRange, value_input_option="USER_ENTERED")
        return 0
  await message.channel.send("**Member Not On Team**\n" + message.author.mention + " is not on a team for this tournament.")
# end tournamentCheckin

async def tournamentSignup(message):
  await message.channel.trigger_typing()
  workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
  registeredIDsSheet = workbook.worksheet("RegisterID")
  signupSheet = workbook.worksheet("Minor") if ("!minor" in message.content) else workbook.worksheet("Major")

  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)
  signupRange = signupSheet.range("B2:D" + str(signupSheet.row_count))

  mc = message.content.replace("!", "")
  userIDs = [int(mc.split(">")[0].split("@")[1]), int(mc.split(">")[-2].split("@")[1])]
  continueSignup = True
  if (userIDs[0] == userIDs[1]):
    await message.channel.send("**Canceling Signup Process**\n" + message.author.mention + ", when signing up a team, include both members of the team.")
    continueSignup = False

  if (continueSignup):
    for userID in userIDs:
      member = message.guild.get_member(userID)
      if (not checkIfRegistered(member, registeredIDsRange)):
        await message.channel.send("**Canceling Signup Process**\n" + member.mention + " is not a registered member. Use the command `@MoBot#0697 registerID username` to register.")
        continueSignup = False

  if (continueSignup):
    for i in range(len(signupRange)):
      userNames = [getUserName(str(userIDs[0]), registeredIDsRange), getUserName(str(userIDs[1]), registeredIDsRange)]
      if (signupRange[i].value == ""):
        signupRange[i].value = userNames[0]
        signupRange[i+1].value = userNames[1]
        signupSheet.update_cells(signupRange, value_input_option="USER_ENTERED")
        for role in message.guild.roles:
          if (role.id == registeredRole):
            for userID in userIDs:
              member = message.guild.get_member(userID)
              await member.add_roles(role)
            break
        await message.channel.send("**Signup Complete**")
        registerLog = message.guild.get_channel(569196829137305631)
        await registerLog.send("%s has signed up %s and %s for the %s tournament." % (message.author.mention, message.guild.get_member(userIDs[0]).mention, message.guild.get_member(userIDs[1]).mention, message.content.split(" ")[0].split("!")[1].strip()))
        break
      if (signupRange[i].value in userNames): 
        member = message.guild.get_member(int(getRegisteredID(signupRange[i].value), registeredIDsRange))
        await message.channel.send("**Canceling Signup Process**\n" + member.mention + " has already signed up. If this is a mistake, contact an Organiser.")
        break
# end tournamentSignup

async def tournamentRetire(message):
  await message.channel.trigger_typing()
  workbook = await openSpreadsheet(ssIDs["Noble Leagues MoBot"])
  signupSheet = workbook.worksheet("Minor") if ("!minor" in message.content) else workbook.worksheet("Major")

  registeredIDsRange, registeredIDsSheet = getRegisteredIDRange(workbook)
  signupRange = signupSheet.range("B2:D" + str(signupSheet.row_count))

  for i in range(0, len(signupRange), 3):
    if (signupRange[i].value != ""):
      for j in range(i, i+2):
        if (getUserName(message.author.id, registeredIDsRange) == signupRange[j].value):
          registerLog = message.guild.get_channel(569196829137305631)
          users = [
            message.guild.get_member(getRegisteredID(signupRange[i].value, registeredIDsRange)),
            message.guild.get_member(getRegisteredID(signupRange[i+1].value, registeredIDsRange))
          ]
          await registerLog.send("%s and %s have retired from the %s." % (users[0].mention, users[1].mention, message.content.split(" ")[0].replace("!", "").strip()))
          for role in message.guild.roles:
            if (role.id == registeredRole):
              for user in users:
                await user.remove_roles(role)
              break
          for k in range(i+3, len(signupRange)):
            if (signupRange[k-3].value != ""):
              signupRange[k-3].value = signupRange[k].value
            else:
              await message.channel.send("**Retired**")
              signupSheet.update_cells(signupRange, value_input_option="USER_ENTERED")
              return None
    else:
      await message.channel.send("**Could Not Retire**\nYou are not on a team for this tournament.")
      break
# end tournamentRetire

async def signupOLD(message):
  await message.channel.trigger_typing()
  moBotMessages = []
  workbook = await openSpreadsheet(ssIDs["Noble Leagues Off-Season"])
  seedingSheet = workbook.worksheet("Seeding")
  registerIDSheet = workbook.worksheet("RegisterID")
  calculationsSheet = workbook.worksheet("Calculations")
  weekHeaders = calculationsSheet.range(2, 3, 2, calculationsSheet.col_count)
  seedingTable = seedingSheet.range(2, 2, 2, seedingSheet.col_count)

  # get current week
  currentWeek = 0
  currentWeekTable = "" # future range of table
  for i in range(0, len(weekHeaders), 3):
    dateParts = weekHeaders[i].value.split("- ")[1].split("/")
    weekEnd = datetime(int("20" + dateParts[2]), int(dateParts[1]), int(dateParts[0]))
    now = datetime.now()
    now = datetime(now.year, now.month, now.day)

    if (now <= weekEnd):
      currentWeek = int(weekHeaders[i].value.split(" -")[0][-2:])
      for j in range(0, len(seedingTable), 4):
        if (int(seedingTable[j].value.split("Week ")[1][:2]) == currentWeek):
          currentWeekTable = seedingSheet.range(5, j+2, seedingSheet.row_count, j+2) # j+2 cause starting at column 2 
          break
      break

  # check if 2 users are present
  users = message.content.split(">")
  if (len(users) == 4):
    try:
      user1 = message.guild.get_member(int(users[1][-18:]))
    except:
      user1 = message.guild.get_member(int(users[1][-17:]))
    try:
      user2 = message.guild.get_member(int(users[2][-18:]))
    except:
      user2 = message.guild.get_member(int(users[2][-17:]))

    # go find users in RegisterID tab
    registerIDTable = registerIDSheet.range("B3:C" + str(registerIDSheet.row_count))
    user1Name = ""
    user2Name = ""
    usersFound = False
    for i in range(len(registerIDTable)):
      if (registerIDTable[i].value == "<@" + str(user1.id) + ">"):
        user1Name = registerIDTable[i-1].value
      if (registerIDTable[i].value == "<@" + str(user2.id) + ">"):
        user2Name = registerIDTable[i-1].value
      if (user1Name != "" and user2Name != ""):
        usersFound = True
        break

    if (not usersFound):
      if (user1Name == ""):
        moBotMessages.append(await message.channel.send("<@" + str(user1.id) + "> has not been registered. To register, use @MoBot#0697 registerID input_name"))
      if (user2Name == ""):
        moBotMessages.append(await message.channel.send("<@" + str(user2.id) + "> has not been registered. To register, use @MoBot#0697 registerID input_name"))
    else:
      # add users to table
      for i in range(len(currentWeekTable)):
        if (currentWeekTable[i].value == user1Name or currentWeekTable[i].value == user2Name):
          moBotMessages.append(await message.channel.send("```Cannot complete signup; at least one of the two users has already signed up.```"))
          break
        if (currentWeekTable[i].value == ""):
          currentWeekTable[i].value = user1Name
          currentWeekTable[i+1].value = user2Name

          roles = message.guild.roles
          for role in roles:
            if (569198468472766475 == role.id): # Registered Role
              await user1.add_roles(role)
              await user2.add_roles(role)

          seedingSheet.update_cells(currentWeekTable, value_input_option="USER_ENTERED")
          moBotMessages.append(await message.channel.send("```Signup Completed```"))
          await message.guild.get_channel(569196829137305631).send("<@" + str(message.author.id) + "> has signed up " + user1Name + " and " + user2Name + ".")
          break
  else:
    moBotMessages.append(await message.channel.send("```Signups must include 2 users at a time. @MoBot#0697 signup @user @user```"))
  
  '''await message.delete()
  await asyncio.sleep(7)
  for msg in moBotMessages:
    await msg.delete()'''
# end signup

async def getSeeding(message, workbook):
  table1 = await message.channel.fetch_message(601172821535621120)
  table2 = await message.channel.fetch_message(601174317933264917)

  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Updating Table```"))
  seedingSheet = workbook.worksheet("Seeding")
  r = seedingSheet.range(2, 2, seedingSheet.row_count, seedingSheet.col_count)

  numCols = seedingSheet.col_count - 1

  # get current week
  currentWeek = r[0]
  colCount = 2
  for i in range(numCols * 3, numCols * 4, 4):
    if (r[i].value != ""):
      currentWeek = r[int(i - (numCols * 3))].value
      colCount += 1 * 4
    else:
      break
  colCount += -4

  header = currentWeek + " Seeding"
  currentWeekTable = seedingSheet.range(5, colCount, seedingSheet.row_count, colCount + 3)

  # get player width
  playerWidth = 6
  for i in range(0, len(currentWeekTable), 4):
    if (len(currentWeekTable[i].value) > playerWidth):
      playerWidth = len(currentWeekTable[i].value)

  totalWidth = playerWidth + 4 + 3 + 4 # playerWidth + seed + team number + col lines
  horizontalBoarder = ""
  for i in range(totalWidth):
    horizontalBoarder += "-"

  table = ["", ""]
  table[0] += "\n" + horizontalBoarder + "\n"
  table[0] += "|" + header.center(len(horizontalBoarder) - 2, " ") + "|\n"
  table[0] += horizontalBoarder + "\n"
  table[0] += "|" + "#".center(3, " ") + "|" + "Player".center(playerWidth, " ") + "|" + "Seed".center(4, " ") + "|\n"
  table[0] += horizontalBoarder + "\n"
  index = 0
  for i in range(0, len(currentWeekTable), 8):
    if (currentWeekTable[i].value != ""):
      table[index] += "|" + str(int(i/8) + 1).center(3, " ") + "|" + currentWeekTable[i].value.center(playerWidth, " ") + "|" + currentWeekTable[i+3].value.center(4, " ") + "|\n"
      table[index] += "|" + "".center(3, " ") + "|" + currentWeekTable[i+4].value.center(playerWidth, " ") + "|" + "".center(4, " ") + "|\n"
      table[index] += horizontalBoarder + "\n"
      if (len(table[0]) > 1600 and index != 1):
        index = 1
        table[1] += "\n" + horizontalBoarder + "\n"
  await table1.edit(content="```" + table[0] + "```")
  if (len(table[1]) < 1916):
    await table2.edit(content="```" + table[1] + "*All teams with the same seed will be randomly assigned a seed for the bracket```")
    moBotMessages.append(await message.channel.send("```Table Updated```"))
  else:
    moBotMessages.append(await message.channel.send("```Table is too large; cannot update.```"))

  await asyncio.sleep(5)
  for msg in moBotMessages:
    await msg.delete()
# end getSeeding

async def getNobleScore(message, nobleStandingsMessageId, workbook):
  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Updating Table```"))
  standingsSheet = workbook.worksheet("Standings")
  r = standingsSheet.range("B2:D" + str(standingsSheet.row_count-1))

  # get name width
  numCols = 3
  nameWidth = 0
  scoreWdith = 0
  for i in range(7, len(r), numCols):
    if (len(r[i].value) > nameWidth):
      nameWidth = len(r[i].value)
    if (len(r[i+1].value) > scoreWdith):
      scoreWdith = len(r[i+0].value)

  horizontalBoarder = ""
  '''for i in range(len(r[0].value) + numCols + 1 - 2):
    horizontalBoarder += "-"'''
  for i in range(4 + nameWidth + scoreWdith + (numCols + 1)):
    horizontalBoarder += "-"


  #nameWidth = len(horizontalBoarder) - (numCols + 1) - 6 - (scoreWdith + 2)

  tableHeader = "\n" + horizontalBoarder + "\n"
  tableHeader += "|" + str(r[0].value.split(" - ")[0]).center(len(horizontalBoarder) - 2, " ") + "|\n"
  tableHeader += "|" + str(r[0].value.split(" - ")[1]).center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"
  tableHeader += "|" + r[3].value.center(4, " ") + "|" + r[4].value.center(nameWidth, " ") + "|" + r[5].value.center(scoreWdith, " ") + "|\n" + horizontalBoarder + "\n"# secondary header

  table1 = ""
  table2 = horizontalBoarder + "\n"

  for i in range(6, len(r), 3):
    if (r[i+2].value != ""):
      if (len(table1) < 1650):
        table1 += "|" + r[i].value.center(4, " ") + "|" + r[i+1].value.center(nameWidth) + "|" + r[i+2].value.center(scoreWdith, " ") + "|\n"
      else:
        table2 += "|" + r[i].value.center(4, " ") + "|" + r[i+1].value.center(nameWidth) + "|" + r[i+2].value.center(scoreWdith, " ") + "|\n"
  table1 += horizontalBoarder
  table2 += horizontalBoarder

  msg1 = await message.channel.fetch_message(565576409414631426)
  await msg1.edit(content="```Noble Standings:" + tableHeader + table1 + "```")
  await message.edit(content="```\n" + table2 + "```")

  moBotMessages.append(await message.channel.send("```Table Updated```"))
  asyncio.sleep(3)
  for msg in moBotMessages:
    await msg.delete()
# end getNobleScore

async def submitResult(message):
  matchResultsChannel = message.guild.get_channel(538429198608498729) # match results
  
  results = message.content.split("submit")[1] + "\n"
  for i in message.attachments:
    results += i.url + "\n" 
  await matchResultsChannel.send(results)

  msg = await message.channel.send("**Submitted**")
  await asyncio.sleep(3)
  await msg.delete()
  await message.delete()
# end submitResult

async def submitResultCancel(message):
  msg = await message.channel.send("**Canceled**")
  await asyncio.sleep(3)
  await msg.delete()
  await message.delete()
# end submitResultCancel

async def submitResultConfirm(message, client):
  msg = await message.channel.send("Are you sure you would like to submit?")
  await msg.add_reaction("✅")
  await msg.add_reaction("❌")

  def checkEmoji(payload):
    return ((payload.emoji.name == "✅" or payload.emoji.name == "❌") and payload.message_id == msg.id and payload.user_id != int(moBot))

  payload = await client.wait_for('raw_reaction_add', check=checkEmoji)
  if (payload.emoji.name == "✅"):
    await submitResult(message)
  else:
    await submitResultCancel(message)
  await msg.delete()
# end submitResult

async def getLeagueTable(message, leagueTableMessageId, workbook):
  leagueTableMessageId = 533691725042941979
  r = workbook.worksheet("Table").range("B2:D13")
  
  # get team name width
  numCols = 3
  teamNameWidth = 0
  for i in range(7, len(r), numCols):
    if (len(r[i].value) > teamNameWidth):
      teamNameWidth = len(r[i].value)
      
  horizontalBoarder = ""
  for i in range(0, 4 + teamNameWidth + 6 + (numCols + 1)):
    horizontalBoarder += "-"
  
  table = "\n" + horizontalBoarder + "\n"
  table += "|" + r[0].value.center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"# main header
  table += "|" + r[3].value.center(4, " ") + "|" + r[4].value.center(teamNameWidth, " ") + "|" + r[5].value.center(6, " ") + "|\n" + horizontalBoarder + "\n"# secondary header
  
  for i in range(6, len(r), 3):
    table += "|" + r[i].value.center(4, " ") + "|" + r[i+1].value.center(teamNameWidth, " ") + "|" + r[i+2].value.center(6, " ") + "|\n"
  table += horizontalBoarder
  msg = await message.channel.fetch_message(leagueTableMessageId)
  await msg.edit(content=("```League Table (Updated: " + currentTime + "):" + table + "\nPosition 9 - Play-Offs\nPosition 10 - Relegation```"))
# end getLeagueTable

async def getFixtures(message, fixturesMessageId, workbook):
  fixturesMessageId = 533699713078263819
  weekNum = int(workbook.worksheet("Calculations").acell("P26").value)
  
  if (weekNum < 6):
    if (weekNum == 0):
      weekNum = 1
    r = workbook.worksheet("W" + str(weekNum)).range("B2:G8")
    numCols = 6
    
    # get team widths
    teamWidths = [0, 0]
    
    for i in range (12, len(r), numCols):
      if (len(r[i].value) > teamWidths[0]):
        teamWidths[0] = len(r[i].value)
      if (len(r[i+2].value) > teamWidths[1]):
        teamWidths[1] = len(r[i+2].value)
        
      if (i == 12 or r[i+3].value == ""):
        continue
        
      if (len(r[i+3].value) > teamWidths[0]):
        teamWidths[0] = len(r[i+3].value)
      if (len(r[i+5].value) > teamWidths[1]):
        teamWidths[1] = len(r[i+5].value)
    
    
    horizontalBoarder = ""
    for i in range(0, sum(teamWidths) + 5):
      horizontalBoarder += "-"
      
    table = "\n" + horizontalBoarder + "\n"
    table += "|" + r[0].value.center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n" # main header
    table += "|" + r[6].value.center(teamWidths[0] + 3 + teamWidths[1], " ") + "|\n" + horizontalBoarder + "\n" # secondary header 1
    
    for i in range(12, len(r), numCols):
      table += "|" + r[i].value.center(teamWidths[0], " ") + " v " + r[i+2].value.center(teamWidths[1], " ") + "|\n"
    table += horizontalBoarder
    
    if (weekNum != 1):
      table += "\n|" + r[9].value.center(teamWidths[0] + 3 + teamWidths[1], " ") + "|\n" + horizontalBoarder + "\n" # secondary header 2
      for i in range(12, len(r), numCols):
        table += "|" + r[i+3].value.center(teamWidths[0], " ") + " v " + r[i+5].value.center(teamWidths[1], " ") + "|\n"
      table += horizontalBoarder
    else:
      table += "\nNo Game 2 in the first week!"
    msg = await message.channel.fetch_message(fixturesMessageId)
    await msg.edit(content=("```Fixtures (Updated: " + currentTime + "):" + table + "```"))
# end getFixtures

async def getTeamInfo(message, args):
  teamName = ""
  for i in range(2, len(args)):
    teamName += args[i] + " "
  teamName = teamName[:-1] # remove trailing space
  
  workbook = await openSpreadsheet(ssIDs["2s League [XB1/PC]"])
  teamInfoSheet = workbook.worksheet("Team Info")
  oldValue = teamInfoSheet.acell("C2").value
  
  # update team name
  teamInfoSheet.update_acell("C2", teamName)
  # get team info
  range1 = teamInfoSheet.range("B4:F15")
  range2 = teamInfoSheet.range("H5:J8")
  teamInfoSheet.update_acell("C2", oldValue)
  
  # get Opponent Width
  opponentWidth = 8
  numCols = 5
  for i in range(0, len(range1), numCols):
    if (len(range1[i+2].value) > opponentWidth):
      opponentWidth = len(range1[i+2].value)
  totalWidth = 4 + opponentWidth + 6 + 5 + (numCols + 1) - 1
  
  horizontalBoarder = ""
  for i in range(totalWidth):
    horizontalBoarder += "-"
      
  table = "Team Info (" + teamName + "):"
  # row 1
  table += "\n" + horizontalBoarder + "\n"
  table += "|" + range1[1].value.center(4 + opponentWidth + 1, " ") # record
  table += "|" + range1[3].value.center(6 + 5 + 1, " ") + "|" # position
  
  # row 2
  table += "\n" + horizontalBoarder + "\n"
  for i in range(5, 10):
    if (i - numCols == 1):
      continue
    if (i - numCols == 2):
      table += "|" + range1[i].value.center(opponentWidth, " ")
    else:
      table += "|" + range1[i].value.center(len(range1[i].value), " ")
  table += "|"
  
  # the rest
  table += "\n" + horizontalBoarder + "\n"
  for i in range(10, len(range1), 5):
    table += "|" + range1[i].value.center(4, " ") # week
    if (range1[i+2].value != "F/W"):      
      table += "|" + range1[i+2].value.center(opponentWidth, " ") # opponent
      table += "|" + range1[i+3].value.center(6, " ") # result
      table += "|" + range1[i+4].value.center(5, " ") # score
    else:
      table += "|" + "F/W".center(opponentWidth + 6 + 5 + 2, " ")
    table += "|\n"
    if (i % 10 != 0):
      table += horizontalBoarder + "\n"
  await message.channel.send("```" + table + "```")
  
  table = ""
  playerWidth = 6
  positionWidth = 10
  mmrWidth = 3
  for i in range(3, len(range2), 3):
    if (len(range2[i].value) > playerWidth):
      playerWidth = len(range2[i].value)
    if (len(range2[i+2].value) > mmrWidth):
      mmrWidth = len(range2[i+2].value)
  
  horizontalBoarder = ""
  for i in range(playerWidth + positionWidth + mmrWidth + 4):
    horizontalBoarder += "-"
  
  table += "\n" + horizontalBoarder + "\n"
  for i in range(0, len(range2), 3):
    table += "|" + range2[i].value.center(playerWidth, " ")
    table += "|" + range2[i+1].value.center(positionWidth, " ")
    table += "|" + range2[i+2].value.center(mmrWidth, " ")
    table += "|\n"
    if (i == 0):
      table += horizontalBoarder + "\n"
  table += horizontalBoarder + "\n"
  await message.channel.send("```" + table + "```")
# end getTeamInfo

async def deleteMoBotMessages(moBotMessages):
  for msg in moBotMessages:
    await msg.delete()

async def openSpreadsheet(ssKey):
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('Noble Leagues Off-Season_client_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key(ssKey)    
  return workbook
# end openSpreadsheet