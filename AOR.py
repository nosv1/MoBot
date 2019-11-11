import discord
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup as bSoup
import requests
import feedparser
import os
import random

import MoBotDatabase

spaceChar = "⠀"
OK_EMOJI = "🆗"
QUESTION_EMOJI = "❓"

moBot = 449247895858970624

moBotSupport = 467239192007671818
aor = 298938326306521098
pcF9 = 592086506068377624
f1GOAT = 291658352336044033

class Race:
  def __init__(
    self,
    name,
    date,
    season,
    region,
    platform,
    game,
    grand_prix,
    tier,
    assist_tier,
    quali_conditions,
    quali_position,
    quali_seconds,
    quali_tire,
    race_conditions,
    race_position,
    race_seconds,
    laps_down,
    penalty_seconds,
    points,
    dnf,
    fastest_lap,
    got_fastest_lap,
    pit_stops
  ):
    self.nam = name
    self.date = date
    self.season = season
    self.region = region
    self.platform = platform
    self.game = game
    self.grand_prix = grand_prix
    self.tier = tier
    self.assist_tier = assist_tier
    self.quali_conditions = quali_conditions
    self.quali_position = quali_position
    self.quali_seconds = quali_seconds
    self.quali_tire = quali_tire
    self.race_conditions = race_conditions
    self.race_position = race_position
    self.race_seconds = race_seconds
    self.laps_down = laps_down
    self.penalty_seconds = penalty_seconds
    self.points = points
    self.dnf = dnf
    self.fastest_lap = fastest_lap
    self.got_fastest_lap = got_fastest_lap
    self.pit_stops = pit_stops
# end Race

class DriverProfileOverview: # need to add teams raced for
  def __init__(self,
    names,
    leagues,
    firstRace,
    lastRace,
    avgQuailPos,
    avgRacePos,
  ):
    self.names = names
    self.leagues = leagues
    self.firstRace = firstRace
    self.lastRace = lastRace
    self.avgQuailPos = avgQuailPos
    self.avgRacePos = avgRacePos
# end DriverProfileOverview

class AutoUpdateStandingsMessage:
  def __init__(self, messageID, channelID, guildID, url):
    self.messageID = messageID
    self.channelID = channelID
    self.guildID = guildID
    self.url = url
# end AutoUpdateStandingsMessage

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (str(moBot) in args[0]):
    if (message.guild.id == officialServer):
      if (args[1].lower() == "aor"):
        if ("add game emojis" in message.content):
          await addGameEmojis(message)  
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  embed = message.embeds[0]

  if (str(payload.user_id) in embed.author.url):
    if ("AOR F1 Driver Profile" in embed.author.name):
      userID = int(embed.author.url.split("user_id=")[1].split("/")[0])
      if (payload.emoji.name == OK_EMOJI):
        await editDriverProfileOverviewEmbed(message, getDriverProfileOverview(await getDriverProfileNames(message, userID)))
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

# ---- AOR F1 DATABASE -----

#   --- AOR F1 DRIVER PROFILES ---

async def editDriverProfileOverviewEmbed(message, driverProfile):
  def raceValue(race):
    raceValue = "Date: %s\nGran Prix: %s\nFinish Position: %s\nTier: %s" % (
      race.date,
      race.grand_prix,
      race.race_position,
      ("AL" if (race.assist_tier == 1) else "F") + str(race.tier)
    )
    return raceValue
  # end raceValue

  try:
    embed = message.embeds[0]
    embed.description = ""
    embed.set_author(name=embed.author.name.replace(": Select Name(s)", ": Overview"), icon_url=embed.author.icon_url, url=embed.author.url)
  except IndexError: # when there was only one name in search for similar names
    moBotMember = message.guild.get_member(moBot)
    embed = discord.Embed(color=moBotMember.roles[-1].color)
    embed.set_author(name="AOR F1 Driver Profile: Overview", icon_url=moBotMember.avatar_url, url="https://google.com/user_id=%s/" % message.author.id)
    embed.set_thumbnail(url=message.guild.icon_url)

  embed.add_field(name="Name(s)", value="%s\n%s" % (", ".join(driverProfile.names), spaceChar))
  embed.add_field(name="Leagues(s)", value="%s\n%s" % (", ".join(driverProfile.leagues), spaceChar))
  embed.add_field(name="First Race", value="%s\n%s" % (raceValue(driverProfile.firstRace), spaceChar))
  embed.add_field(name="Most Recent Race", value="%s\n%s" % (raceValue(driverProfile.lastRace), spaceChar))
  embed.add_field(name="Avg. Quali. Pos.", value="%s\n%s" % (driverProfile.avgQuailPos, spaceChar))
  embed.add_field(name="Avg. Race Pos.", value="%s\n%s" % (driverProfile.avgRacePos, spaceChar))
  await message.clear_reactions()
  await message.edit(content=spaceChar, embed=embed)
  await message.add_reaction(QUESTION_EMOJI)
# end editDriverProfileOverviewEmbed

async def openDriverProfileEmbed(message):
  lookupName = message.content.split("profile")[1].strip().split(",")
  msg = await message.channel.send("**Searching for similar names...**")
  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(name="AOR F1 Driver Profile: Select Name(s)", icon_url=moBotMember.avatar_url, url="https://google.com/user_id=%s/" % message.author.id)
  embed.set_thumbnail(url=message.guild.icon_url)

  names = getSimilarDriverNames(lookupName)
  description = ""
  if (len(names) > 20):
    description = "**Search Name Too Vague**\nThere were too many results (%s > 20). Edit your original message, and search again." % len(names)
  elif (len(names) > 1):
    description = "**Select the name(s) you are looking for, then click the %s.**\n\n" % OK_EMOJI
    for name in names:
      emoji = chr(127462+names.index(name)) #starting at :reg_indc_A:
      description += "%s - %s\n" % (emoji, name)
      await msg.add_reaction(emoji)
    await msg.add_reaction(OK_EMOJI)
  elif (len(names) == 1):
    await editDriverProfileOverviewEmbed(msg, getDriverProfileOverview(names))
    return
  else:
    description = "**No Matching Names**\nEdit your original message, and try being less specific."
  embed.description = description

  await msg.edit(content=spaceChar, embed=embed)
# end openDriverProfileEmbed

def getDriverProfileOverview(names): # array of names
  moBotDB = MoBotDatabase.connectDatabase('AOR F1')
  moBotDB.connection.commit()

  # get leagues
  leagues = []
  for name in names:
    moBotDB.cursor.execute("""
      SELECT season, region, platform
      FROM race_inputs
      WHERE driver_name = '%s'
    """ % (MoBotDatabase.replaceChars(name)))
  for record in moBotDB.cursor:
    league = "S%s-%s-%s" % (record[0], record[1], record[2])
    if (league not in leagues):
      leagues.append(league)

  # get first and last race
  races = getDriverRaces(names)
  print(len(races))
  firstRace = races[0]
  lastRace = races[-1]

  # get avg quali position - i know it's bullshit, but for now
  qualiPositions = []
  racePositions = []
  for name in names:
    moBotDB.cursor.execute("""
      SELECT quali_position, race_position
      FROM race_inputs
      WHERE 
        driver_name = '%s'
    """ % (MoBotDatabase.replaceChars(name)))

    for record in moBotDB.cursor:
      qualiPosition = record[0]
      racePosition = record[1]
      if (qualiPosition > 0):
        qualiPositions.append(qualiPosition)
      if (racePosition > 0):
        racePositions.append(racePosition)
        
  avgQuailPos = round(sum(qualiPositions) / len(qualiPositions), 1)
  avgRacePos = round(sum(racePositions) / len(racePositions), 1)

  moBotDB.connection.close()
  return DriverProfileOverview(names, leagues, firstRace, lastRace, avgQuailPos, avgRacePos)
# end getDriverHistory

async def getDriverProfileNames(message, userID):
  embed = message.embeds[0]
  names = []
  reactions = message.reactions
  for reaction in reactions:
    async for user in reaction.users():
      if (user.id == userID):
        for line in embed.description.split("\n"):
          if (reaction.emoji in line and reaction.emoji not in OK_EMOJI):
            names.append(line.split(reaction.emoji + " - ")[1].split("\n")[0].strip())
            break
  return names
# end getDriverProfileNames

#   --- END AOR F1 DRIVER PROFILES ---

#   --- AOR STANDINGS ---

async def updateStandings(client):
  now = datetime.utcnow()

  autoUpdateStandings = getAutoUpdateStandings()

  guildsChannels = {}
  messages = []

  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.connection.commit()
  for standingsMessage in autoUpdateStandings:
    guildID = str(standingsMessage.guildID)
    channelID = str(standingsMessage.channelID)
    messageID = standingsMessage.messageID
    url = standingsMessage.url

    if (guildID not in guildsChannels):
      guildsChannels[guildID] = {}
    if (channelID not in guildsChannels[guildID]):
      guildsChannels[guildID][channelID] = client.get_guild(int(guildID)).get_channel(int(channelID))

    r = random.random()
    d = now.weekday()
    hourDays = [7, 1, 2] # sunday, monday, tuesday, when refresh should be once per hour
    if ((d in hourDays and r < 1/60) or (d not in hourDays and r < 1/(60*24))):
      messages.append([await guildsChannels[guildID][channelID].fetch_message(messageID), getStandings(url, client, moBotDB)])
  moBotDB.connection.close()
    
  for messageEmbed in messages:
    message = messageEmbed[0]
    embed = messageEmbed[1]

    moBotMember = message.guild.get_member(moBot)
    embed.color = moBotMember.roles[-1].color
    embed.set_thumbnail(url=message.guild.icon_url)

    await messageEmbed[0].edit(content=spaceChar, embed=messageEmbed[1])
# end updateStandings

def getStandings(url, client, moBotDB):

  moBotDB.cursor.execute("""
  SELECT season, region, platform, split
  FROM standings_sheets_links
  WHERE url = '%s'
  """ % (url))
  
  season = ""
  region = ""
  platform = ""
  split = ""
  for record in moBotDB.cursor:
    season = record[0]
    region = record[1]
    platform = record[2]
    split = record[3]

  flags = getFlags()

  url = "%s?hl=en&widget=false&headers=false" % url
  standingsTable, roundFlag = getSpreadsheet(url)

  moBotMember = client.get_user(moBot)
  embed = discord.Embed()
  embed.set_author(name="%s-%s-%s-%s" % (season, region, platform, split), icon_url=moBotMember.avatar_url, url=url)

  value = ""
  for i in range(len(standingsTable)):
    try:
      position = standingsTable[i][0]
      try:
        flag = flags[standingsTable[i][1].split("flags/")[1].upper()]
      except KeyError:
        flag = ""
      name = standingsTable[i][2].replace("<br/>", "")
      points = standingsTable[i][-5]

      if (points != " - "):
        value += "\n%s. %s **%s** - %s" % (position, flag, name, points)

    except IndexError:
      pass
  value += "\n__[Results Spreadsheet](" + url.replace("_", "\\_") + ")__"
  embed.add_field(name="__Driver Standings - After %s__" % flags[roundFlag.upper()], value=value)
  embed.set_footer(text=datetime.strftime(datetime.utcnow(), "| Refreshed: %H:%M UTC |"))

  return embed
# end getStandings

#   --- END AOR STANDINGS ---

def getSpreadsheet(url):
  soup = bSoup(requests.get(url).text, "html.parser")
  rows = soup.findAll("tr")
  table = []
  completedRounds = 0
  for i in range(5, 25): # p1 to P20
    columns = str(rows[i]).split("<td")

    tempCompletedRounds = 0
    for column in columns[6:27]:
      if (column.split("\">")[1].split("</td>")[0] != ""):
        tempCompletedRounds += 1
    completedRounds = tempCompletedRounds if tempCompletedRounds > completedRounds else completedRounds

    j = len(columns) - 1
    while j > 31:
      del columns[j]
      j -= 1
    del columns[0:2]
    for j in range(len(columns)):
      columns[j] = columns[j].split("</td")[0].split(".png")[0].split("\">")[-1]
    table.append(columns)

  roundFlag = str(rows[3]).split("<td")[completedRounds + 1].split("flags/")[1].split(".png")[0]
  return table, roundFlag
# end getSpreadsheet

def getStandingsSheetLinks():
  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
  SELECT url, season, region, platform, split
  FROM standings_sheets_links
  """)
  moBotDB.connection.close()

  spreadsheetLinks = {}
  for record in moBotDB.cursor:
    url = record[0]
    season = record[1]
    region = record[2]
    platform = record[3]
    split = record[4]

    if (season not in spreadsheetLinks):
      spreadsheetLinks[season] = {}
    if (region not in spreadsheetLinks[season]):
      spreadsheetLinks[season][region] = {}    
    if (platform not in spreadsheetLinks[season][region]):
      spreadsheetLinks[season][region][platform] = {}
    if (split not in spreadsheetLinks[season][region][platform]):
      spreadsheetLinks[season][region][platform][split] = {}

    spreadsheetLinks[season][region][platform][split] = url
  return spreadsheetLinks
# end getStandingsSheetLinks

def getAutoUpdateStandings():
  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
  SELECT message_id, channel_id, guild_id, url
  FROM auto_update_standings""")

  messages = []
  for record in moBotDB.cursor:
    messages.append(AutoUpdateStandingsMessage(*record))
  moBotDB.connection.close()
  return messages
# end getAutoUpdateStandings

def getFlags():
  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
  SELECT flags.key, flags.flag
  FROM flags
  """)
  moBotDB.connection.close()

  flags = {}
  for record in moBotDB.cursor:
    flags[record[0]] = record[1]
  return flags
# end getFlag

def getDriverRaces(names):
  sqlNames = ""
  for name in names:
    sqlNames+= "\ndriver_name = '%s' OR\n" % (MoBotDatabase.replaceChars(name))
  sqlNames = sqlNames[:-3]

  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT *
    FROM race_inputs
    WHERE %s
    ORDER BY date ASC
  """ % sqlNames)

  races = []
  for record in moBotDB.cursor:
    races.append(Race(*record))

  moBotDB.connection.close()
  return races
# end getDriverRaces

def getSimilarDriverNames(names):
  whereClause = ""
  for name in names:
    whereClause += ("LOWER(driver_name) LIKE '%s' OR\n"
      % ("%" + MoBotDatabase.replaceChars(name.strip().lower()) + "%"))
  whereClause = whereClause[:-3]

  moBotDB = MoBotDatabase.connectDatabase('AOR F1')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT DISTINCT(driver_name)
    FROM race_inputs
    WHERE %s
    ORDER BY driver_name
    """ % (whereClause))

  names = []
  for record in moBotDB.cursor:
    names.append(record[0])
  moBotDB.connection.close()

  return names
# end getSimilarDriverNames

# ----- END AOR F1 DATABASE -----

async def addGameEmojis(message):
  directory = os.fsencode("C:/Users/Owner/Desktop/AOR Emojis/Games")
  for file in os.listdir(directory):
    filename = os.fsdecode(file)
    image = open(os.fsdecode(directory) + "/" + filename, "rb")
    f = image.read()
    b = bytearray(f)
    emoji = await message.guild.create_custom_emoji(name=filename.split(".")[0], image=b)
    emojiImage = "<:" + emoji.name + ":" + str(emoji.id) + ">"
    await message.channel.send(emoji.name + " -> " + emojiImage)

async def udpateRSSChannel(client):
  channel = client.get_guild(467239192007671818).get_channel(547274914319826944)
  
  embed = discord.Embed()
  url = "https://apexonlineracing.com/community/forums/aor-pc-f9-league-season-18.1535/index.rss"
  feed = feedparser.parse(url)
  '''for c in str(feed.entries):
    try:
      print(c, end="")
    except:
      pass
  return'''
  for entry in feed.entries:
    fieldName = entry.title
    fieldValue = entry.summary[:1024]
    embed.add_field(name=fieldName, value=fieldValue, inline=False)
    await channel.send(embed=embed)
    break
# end udpateRSSChannel
