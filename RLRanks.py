import discord
import asyncio
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials 
import gspread
from requests_html import AsyncHTMLSession
import math
import sys
from bs4 import BeautifulSoup as bsoup
import requests
import re

import SecretStuff

moBot = "449247895858970624"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
  
  if (args[2] == "enable" or args[2] == "disable"):
    await enableServer(message, client)
  elif (args[2] == "register"):
    await message.channel.send("**Command disabled due to lack of hardware capability.**")
    #await registerID(message, client)

# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

def getMMRs(platform, id):

  urlID = id.lower().replace(" ", "%20")
  url = 'https://rocketleague.tracker.network/profile/' + platform + '/' + urlID

  html = str(bsoup(requests.get(url).text, "html.parser"))
  seasons = [x for x in range(13, 0, -1)] # current season first

  mmrs = {}
  ''' for example
  13: { // season
    2: mmr // twos
  }'''

  for season in seasons:

    urlID = id.lower().replace(" ", "%20")
    url = 'https://rocketleague.tracker.network/profile/' + platform + '/' + urlID

    html = str(bsoup(requests.get(url).text, "html.parser"))
    seasons = [x for x in range(13, 0, -1)] # current season first

    mmrs = {}
    ''' for example
    13: { // season
      2: mmr // twos
    }'''

    for season in seasons:
      
      mmrs[season] = {2 : 0, 3 : 0} # 2v2s : mmr, 3v3s : mmr

      splitOnTwos = "<td>\nRanked Doubles 2v2"
      splitOnThrees = "<td>\nRanked Standard 3v3"

      reg1 = r"(\n\d,\d\d\d)|(\n\d\d\d\d)|(\n\d\d\d)|(\n\d\d)|(\n\d)" 
      mmrsAboveThis = "<img"

      # get the text where the mmr is, not quite on its own yet
      try:
        seasonRanks = html.split("id=\"season-%s\"" % season)[1]
      except IndexError: # when season isn't available for the player
        continue

      def getMMR(splitOn):
        return re.sub(r"\n|,", "", "".join(x for x in re.findall(reg1, seasonRanks.split(splitOn)[1].split(mmrsAboveThis)[0].replace(" ", ""))[0]))

      try:
        mmrs[season][2] = int(getMMR(splitOnTwos))
      except IndexError: # if player has no mmr
        pass

      try:
        mmrs[season][3] = int(getMMR(splitOnThrees))
      except IndexError: # if player has no mmr
        pass

  return mmrs
# end getMMRs

async def updateUserRoles(guild, rankMMR, member, platform, profile, highest):
  print(member)
  if (member != None):
    if (highest == None):
      ranks, highest = await getRanks(platform, profile)
    print(highest)
    roles = guild.roles

    if ("rank" in rankMMR):
      rank = highest[0].split("Division")[0].strip()

      for role in roles:
        if (role.name == rank):
          print("ADDING", role.name, "TO", member)
          await member.add_roles(role)
          break
    elif ("mmr" in rankMMR):
      mmr = int(highest[1])

      for role in roles:
        roleName = role.name.split("-")
        if (len(roleName) == 2):
          print(roleName)
          if (not math.isnan(int(roleName[0])) and not math.isnan(int(roleName[1]))):
            mmrs = [int(roleName[0]), int(roleName[1])]
            if (mmr >= mmrs[0] and mmr <= mmrs[1]):
              print("ADDING", role.name, "TO", member)
              await member.add_roles(role)
              break
            elif (mmrs[1] > 2000 and mmr > 2000):
              print("ADDING", role.name, "TO", member)
              await member.add_roles(role)
              break
# end updateUserRoles

async def getGuildIDsDiscordIDs(client):
  workbook = await openSpreadsheet()
  idsSheet = workbook.worksheet("IDs")
  guildRange = idsSheet.range("A2:B" + str(idsSheet.row_count))
  idsRange = idsSheet.range("D2:F" + str(idsSheet.row_count))

  discordIDs = {}
  guildIDs = {}

  for i in range(0, len(guildRange), 2):
    if (guildRange[i].value != ""):
      guildIDs[int(guildRange[i].value)] = guildRange[i+1].value.lower()
    else:
      break
  
  for i in range(0, len(idsRange), 3):
    if (idsRange[i].value != ""):
      discordIDs[int(idsRange[i].value)] = [idsRange[i+1].value, idsRange[i+2].value]
    else:
      break

  return guildIDs, discordIDs
# end updateUserRoles

async def updateUserRolesLoop(client):
  lastSecond = 0
  while True:
    now = datetime.utcnow()
    second = now.second
    if (second == lastSecond):
      continue
    else:
      lastSecond = second

    sys.stdout.write("\rCurrent Time: " + str(now))
    sys.stdout.flush() # allows rewriting the line above in the console, basically it keeps replacing the text instead of having a bunch of lines

    if ((now.hour % 6 == 0 and now.minute == 0 and second == 0)):
      print("\nUPDATING ROLES", datetime.now())
      guildIDs, discordIDs = await getGuildIDsDiscordIDs(client)

      for guildID in guildIDs:
        guild = client.get_guild(guildID)
        rankMMR = guildIDs[guildID]

        for discordID in discordIDs:
          member = guild.get_member(discordID)
          platform = discordIDs[discordID][0]
          profile = discordIDs[discordID][1]
          
          await updateUserRoles(guild, rankMMR, member, platform, profile, None)
      print("ROLES UPDATED", datetime.now())
  
# end updateUserRolesLoop

async def getRanks(platform, profile):
  asession = AsyncHTMLSession()
  url = "https://rocketleague.tracker.network/profile/" + platform.strip() + "/" + profile
  r = await asession.get(url)
  await r.html.arender(retries=8)
  
  ranks = {}

  #parsing stuff below
  parse = r.html.text.split("(Top")
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

        if (mmr > highest[1]):
          highest = [rank, mmr]

  r.close()
  return ranks, highest
# end getRanks

async def registerID(message, client):
  await message.channel.trigger_typing()

  platform = message.content.lower().split("register")[1].strip().split(" ")[0].strip()
  profile = message.content.lower().split(platform)[1].strip().replace(" ", "%20")
  platform = platform.center(7, " ")
  platform = platform.replace(" xb1 ", " xbox ")
  platform = platform.replace(" xb ", " xbox ")
  platform = platform.replace(" ps4 ", " ps ")
  platform = platform.replace(" psn ", " ps ")
  platform = platform.replace(" pc ", " steam ")
  platform = platform.strip()
  
  await message.channel.send("**Verifying PLATFORM and ID... this may take a moment.**")
  await message.channel.trigger_typing()
  ranks, highest = await getRanks(platform, profile)

  if (highest[0] == ""):
    reply = "**PLATFORM AND ID COULD NOT BE VERIFIED**"
    reply += "\n\nPlease make sure your PLATFORM and ID are correct."
    reply += "\n  PC - `@MoBot#0697 rlrank register pc [Steam_ID]`"
    reply += "\n    *(Steam_ID: go to your profile, go to the URL, copy the number after `/profiles/`)*"
    reply += "\n  XBOX - `@MoBot#0697 rlrank regsiter xbox [Gamertag]`"
    reply += "\n  PS - `@MoBot#0697 rlrank regsiter ps [PSN]`"
    await message.channel.send(reply)
    return
  else:
    await message.channel.send("**PLATFORM AND ID VERIFIED**")

    workbook = await openSpreadsheet()
    idsSheet = workbook.worksheet("IDs")
    idsRange = idsSheet.range("D2:F" + str(idsSheet.row_count))

    def insertUser(idsRange, i, user, platform, profile):
      idsRange[i].value = str(user.id)
      idsRange[i+1].value = platform
      idsRange[i+2].value = profile
      idsSheet.update_cells(idsRange, value_input_option="USER_ENTERED")
      return idsRange

    user = message.author
    for i in range(len(idsRange)):
      if (idsRange[i].value == ""):
        idsRange = insertUser(idsRange, i, user, platform, profile)
        await message.channel.send("**USER REGISTERED**")
        break
      if (idsRange[i].value == str(user.id)):
        await message.channel.send("**USER ALREADY REGISTERED**")

        def check(payload):
          return (payload.emoji.name == "✅" or payload.emoji.name == "❌") and payload.user_id == message.author.id and payload.channel_id == message.channel.id

        reply = "Current PLATFORM and ID:"
        reply += "\n  " + idsRange[i+1].value
        reply += "\n  " + idsRange[i+2].value.replace("%20", " ")
        reply += "\n\nWould you like to update your PLATFORM and ID?"
        moBotMessage = await message.channel.send(reply)
        await moBotMessage.add_reaction("✅")
        await moBotMessage.add_reaction("❌")

        try:
          payload = await client.wait_for("raw_reaction_add", timeout=30.0, check=check)
          if (payload.emoji.name == "✅"):
            idsRange = insertUser(idsRange, i, user, platform, profile)
            await message.channel.send("**USER UPDATED**")
          elif (payload.emoji.name == "❌"):
            await message.channel.send("**CANCELING REGISTRATION**")
            return
        except asyncio.TimeoutError:
          await message.channel.send("**TIMED OUT**")
          return
        break

    guildRange = idsSheet.range("A2:B" + str(idsSheet.row_count))
    for i in range(len(guildRange)):
      if (guildRange[i].value == str(message.guild.id)):
        rankMMR = guildRange[i+1].value.lower()
        await message.channel.send("**ASSIGNING ROLE**")
        await updateUserRoles(message.guild, rankMMR, message.author, platform, profile, highest)
        await message.channel.send("**ROLE ASSIGNED**")
        break
      elif (guildRange[i].value == ""):
        await message.channel.send("**COULD NOT UPDATE ROLES**\n\nThis guild has not enabled automatic Rocket League role assignment.")
# end registerID

async def checkForRoles(message, rankMMR):
  await message.channel.send("**Checking for Rocket League Ranks/MMRs as Roles**")
  await message.channel.trigger_typing()
  
  ranks = {
    "Grand Champion" : "c705dd",
    "Champion" : "c705dd",
    "Diamond" : "0210a5",
    "Platinum" : "08d3e2",
    "Gold" : "dda004",
    "Silver" : "cccccc",
    "Bronze" : "a0522d",
    "Unranked" : "000000",
  }

  mmrs = {
    "1" : {
      "0-299" : "000000",
      "300-599" : "000000",
      "600-899" : "000000",
      "900-1199" : "000000",
      "1200-1499" : "000000",
      "1500-1799" : "000000",
      "1800-2099" : "000000",
    },
    "2" : {
      "0-99" : "000000",
      "100-199" : "000000",
      "200-299" : "000000",
      "300-399" : "000000",
      "400-499" : "000000",
      "500-599" : "000000",
      "600-699" : "000000",
      "700-799" : "000000",
      "800-899" : "000000",
      "900-999" : "000000",
      "1000-1099" : "000000",
      "1100-1199" : "000000",
      "1200-1299" : "000000",
      "1300-1399" : "000000",
      "1400-1499" : "000000",
      "1500-1599" : "000000",
      "1600-1699" : "000000",
      "1700-1799" : "000000",
      "1800-1899" : "000000",
      "1900-1999" : "000000",
    }
  }

  roles = message.guild.roles

  def lookForRole(roles, tRole):
    roleExists = False
    for role in roles:
      if (role.name == tRole):
        roleExists = True
    return roleExists

  async def createRole(tRole, rank, ranks, mmrs, mmrDetail, rankMMR, message):
    roleColor = "0x" + (ranks[rank] if ("rank" in rankMMR) else mmrs[mmrDetail][tRole])
    await message.guild.create_role(name=tRole, color=discord.Color(int(roleColor, 16)))
    await message.channel.send("**" + tRole +" Role Created**")

  if ("rank" in rankMMR):
    for rank in ranks:
      for i in ["III", "II", "I"]:
        if (rank != "Grand Champion" and rank != "Unranked"):
          tRole = rank + " " + str(i) 
          roleExists = lookForRole(roles, tRole)
          if (not roleExists):
            await createRole(tRole, rank, ranks, None, None, rankMMR, message)
        else:
          tRole = rank
          roleExists = lookForRole(roles, tRole)
          if (not roleExists):
            await createRole(tRole, rank, ranks, None, None, rankMMR, message)
          break
          
  else:
    mmrDetail = rankMMR[-1]
    for mmr in mmrs[mmrDetail]:
      roleExists = lookForRole(roles, mmr)
      tRole = mmr
      if (not roleExists):
        await createRole(mmr, None, ranks, mmrs, mmrDetail, rankMMR, message)
# end checkForRoles

async def enableServer(message, client):
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet()
  idsSheet = workbook.worksheet("IDs")
  guildRange = idsSheet.range("A2:B" + str(idsSheet.row_count))

  guildIDStr = str(message.guild.id)
  rankMMR = message.content.split(" ")[-1]
  if ("enable" in message.content and "mmr" not in rankMMR.lower() and "rank" not in rankMMR.lower()):
    await message.channel.send("Do you want the users to be sorted by MMR1, MMR2, or RANK? (MMR1 splits the MMRs into 7 different roles, MMR2 splits them into 20)\n*Users will be assigned appropiate roles upon registering with <@" + str(moBot) + ">.*")
    def checkMsg(msg):
      return msg.author.id == message.author.id and msg.channel.id == message.channel.id

    try:
      msg = await client.wait_for("message", timeout=30.0, check=checkMsg)
      if ("mmr" not in msg.content.lower() or "rank" not in msg.content.lower()):
        rankMMR = msg.content.lower()
      else:
        await message.channel.send("**Response not recognized, canceling.**")
        return
    except asyncio.TimeoutError:
      await message.channel.send("**TIMED OUT**")
      return

  for i in range(len(guildRange)):
    if ("enable" in message.content):
      if (guildRange[i].value == ""):
        guildRange[i].value = guildIDStr
        guildRange[i+1].value = rankMMR
        idsSheet.update_cells(guildRange, value_input_option="USER_ENTERED")
        await message.channel.send("**GUILD ENABLED**")
        await checkForRoles(message, rankMMR.lower())
        break
      elif (guildRange[i].value == guildIDStr):
        await message.channel.send("**GUILD ALREADY ENABLED**")
        def check(payload):
          return (payload.emoji.name == "✅" or payload.emoji.name == "❌") and payload.user_id == message.author.id and payload.channel_id == message.channel.id

        reply = "Current Roles:"
        reply += "\n  " + guildRange[i+1].value
        reply += "\n\nWould you like to update the Roles?"
        moBotMessage = await message.channel.send(reply)
        await moBotMessage.add_reaction("✅")
        await moBotMessage.add_reaction("❌")

        try:
          payload = await client.wait_for("raw_reaction_add", timeout=30.0, check=check)
          if (payload.emoji.name == "✅"):
            guildRange[i].value = guildIDStr
            guildRange[i+1].value = rankMMR
            idsSheet.update_cells(guildRange, value_input_option="USER_ENTERED")
            await checkForRoles(message, rankMMR.lower())
            await message.channel.send("**ROLES UPDATED**")
        except asyncio.TimeoutError:
          await message.channel.send("**TIMED OUT**")
          return
        break
    elif ("disable" in message.content):
      if (guildRange[i].value == ""):
        await message.channel.send("**GUILD IS NOT ENABLED**")
        break
      if (guildRange[i].value == guildIDStr):
        for j in range(i, len(guildRange), 2):
          for k in range(0, 2):
            guildRange[j+k].value = guildRange[j+2].value
          if (guildRange[j+2].value == ""):
            break
        idsSheet.update_cells(guildRange, value_input_option="USER_ENTERED")
        await message.channel.send("**GUILD DISABLED**")
        break
# end enableServer

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1880Rf5ZMDxWnJO7zkKZGAfQWwruiMZmbvaD_tIPz4pg")
  return workbook
# end openSpreadsheet