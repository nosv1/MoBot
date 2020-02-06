import discord
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup as bSoup
import requests
import feedparser
import os
import random
import statistics

import MoBotDatabase

spaceChar = "⠀"
OK_EMOJI = "🆗"
QUESTION_EMOJI = "❓"

moBot = 449247895858970624

moBotSupport = 467239192007671818
aor = 298938326306521098
pcF9 = 592086506068377624
f1GOAT = 291658352336044033

class RaceInput:
  def __init__(
    self,
    driver_name,
    team,
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
    pit_stops,
    quali_percent_diff,
    race_percent_diff,
    fastest_lap_percent_diff,
    overtakes
  ):
    self.driver_name = driver_name
    self.date = date
    self.team = team
    self.season = int(season)
    self.region = region
    self.platform = platform
    self.game = game
    self.grand_prix = grand_prix
    self.tier = int(tier)
    self.assist_tier = int(assist_tier)
    self.quali_conditions = quali_conditions
    self.quali_position = quali_position
    self.quali_seconds = round(float(quali_seconds),3)
    self.quali_tire = quali_tire
    self.race_conditions = race_conditions
    self.race_position = race_position
    self.race_seconds = round(float(race_seconds),3)
    self.laps_down = laps_down
    self.penalty_seconds = penalty_seconds
    self.points = points
    self.dnf = dnf
    self.fastest_lap = round(float(fastest_lap),3)
    self.got_fastest_lap = got_fastest_lap
    self.pit_stops = pit_stops
    self.quali_percent_diff = quali_percent_diff
    self.race_percent_diff = race_percent_diff
    self.fastest_lap_percent_diff = fastest_lap_percent_diff
    self.overtakes = overtakes
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
  def __init__(self, messageID, channelID, guildID, url, league):
    self.messageID = messageID
    self.channelID = channelID
    self.guildID = guildID
    self.url = url
    self.league = league
# end AutoUpdateStandingsMessage

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (str(moBot) in args[0]):
    if (args[1].lower() == "aor"):
      if ("add game emojis" in message.content):
        await addGameEmojis(message)
    if (len(args) > 3):
      if ("standings" in args[1] and "new" in args[2]): # @MoBot standings new S18-UK-PC-F1
        await newStandings(message, client)
    
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  try:
    embed = message.embeds[0]

    if (str(payload.user_id) in embed.author.url):
      if ("AOR F1 Driver Profile" in embed.author.name):
        userID = int(embed.author.url.split("user_id=")[1].split("/")[0])
        if (payload.emoji.name == OK_EMOJI):
          await editDriverProfileOverviewEmbed(message, getDriverProfileOverview(await getDriverProfileNames(message, userID)))
          
  except IndexError: # when there is no embed...
    pass

# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove


#   --- AOR F1 RACE EVALUATION ---

def setPercentDifferences():
  raceInputs = getRaceInputs()
  moBotDB = connectDatabase()

  print("Getting Races")
  races = []
  for raceInput in raceInputs:
    race = [raceInput.season, raceInput.region, raceInput.platform, raceInput.grand_prix, raceInput.tier, raceInput.assist_tier]
    if (race not in races):
      races.append(race)

  print("Evaluating Races")
  for race in races:
    print(str(round((races.index(race) / len(races))*100,2)) + "%")
    race = getRace(raceInputs, *race)

    qualiEvaluation = []
    raceEvaluation = []
    fastestLapEvaluation = []
    overtakesEvaluation = []

    for raceInput in race:
      qualiEvaluation.append(evaluateQuali(raceInput, race))
      raceEvaluation.append(evaluateRace(raceInput, race))
      fastestLapEvaluation.append(evaluateFastestLap(raceInput, race))
      overtakesEvaluation.append(raceInput.quali_position - raceInput.race_position)
    
    for i in range(len(race)):
      raceInput = race[i]
      raceInput.quali_percent_diff = qualiEvaluation[i]*100
      raceInput.race_percent_diff = raceEvaluation[i]*100
      raceInput.fastest_lap_percent_diff = fastestLapEvaluation[i]*100
      raceInput.overtakes = overtakesEvaluation[i]
      moBotDB.cursor.execute("""
        UPDATE race_inputs
        SET 
          quali_percent_diff = '%s',
          race_percent_diff = '%s',
          fastest_lap_percent_diff = '%s',
          overtakes = '%s'
        WHERE 
          driver_name = '%s' AND
          season = '%s' AND
          region = '%s' AND
          platform = '%s' AND
          grand_prix = '%s' AND
          tier = '%s' AND
          assist_tier = '%s'
      """ % (
        raceInput.quali_percent_diff, 
        raceInput.race_percent_diff, 
        raceInput.fastest_lap_percent_diff, 
        raceInput.overtakes,
        raceInput.driver_name, raceInput.season, raceInput.region, raceInput.platform, raceInput.grand_prix, raceInput.tier, raceInput.assist_tier
      ))
  
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end setPercentDifferences

def getRace(raceInputs, season, region, platform, grandPrix, tier, assistTier): # assist tier is 0 or 1  
  race = []
  for raceInput in raceInputs:
    if (
      raceInput.season == season and 
      raceInput.region == region and
      raceInput.platform == platform and
      raceInput.grand_prix == grandPrix and
      raceInput.tier == tier and
      raceInput.assist_tier == assistTier
    ):
      race.append(raceInput)

  return race
# end getRace

def evaluateQuali(raceInput, race):

  percentDifferences = []
  qualiTimes = []

  for aRaceInput in race:
    if (aRaceInput.quali_seconds > 0):
      qualiTimes.append(aRaceInput.quali_seconds)

  if (len(qualiTimes) < 5): # no times inputted
    return 0
  elif (raceInput.quali_seconds == 0): # no time set
    return -1

  for qualiTime in qualiTimes:
    if (qualiTime != raceInput.quali_seconds):
      percentDifferences.append(getPercentDifference(qualiTime, raceInput.quali_seconds))

  return sum(percentDifferences) / len(percentDifferences)
# end evaluateQuali

def evaluateRace(raceInput, race):

  percentDifferences = []
  raceTimes = []

  for aRaceInput in race:
    if (aRaceInput.race_seconds > 0):
      raceTimes.append(aRaceInput.race_seconds)

  if (len(raceTimes) < 5):
    return 0
  elif (raceInput.race_seconds == 0):
    return -1

  for raceTime in raceTimes:
    if (raceTime != raceInput.race_seconds):
      percentDifferences.append(getPercentDifference(raceTime, raceInput.race_seconds))

  return sum(percentDifferences) / len(percentDifferences)
# end evaluateRace

def evaluateFastestLap(raceInput, race):
  percentDifferences = []
  fastestLaps = []

  for aRaceInput in race:
    if (aRaceInput.fastest_lap > 0):
      fastestLaps.append(aRaceInput.fastest_lap)

  if (len(fastestLaps) < 5): # no times inputted
    return 0
  elif (raceInput.fastest_lap == 0): # no time set
    return -1

  for fastestLap in fastestLaps:
    if (fastestLap != raceInput.fastest_lap):
      percentDifferences.append(getPercentDifference(fastestLap, raceInput.fastest_lap))

  return sum(percentDifferences) / len(percentDifferences)
# end evaluateFastestLap


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
    races.append(RaceInput(*record))

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


#   --- AOR STANDINGS ---

async def newStandings(message, client):
  msg = await message.channel.send("**Getting League Spreadsheet Link**")

  msgID = msg.id
  channelID = msg.channel.id
  guildID = msg.guild.id
  league = message.content.split("new")[1].strip().split("-")
  season = league[0]
  region = league[1]
  platform = league[2]
  split = league[3]
  
  standingsSheetLinks = getStandingsSheetLinks()
  url = standingsSheetLinks[season][region][platform][split]
  await msg.edit(content="**Creating Standings Embed**\n*This could take a second...*")
  standingsEmbed = getStandings(url, league, client)
  moBotMember = message.guild.get_member(moBot)
  standingsEmbed.color = moBotMember.roles[-1].color
  await msg.edit(embed=standingsEmbed, content=spaceChar)

  moBotDB = MoBotDatabase.connectDatabase("AOR F1")
  moBotDB.cursor.execute("""
  INSERT INTO `AOR F1`.auto_update_standings 
    (`message_id`, `channel_id`, `guild_id`, `url`, `league`, `notes`)
  VALUES
    ('%s', '%s', '%s', '%s', '%s', '#%s, %s')
  """ % (msgID, channelID, guildID, url, "-".join(league), msg.channel.name, msg.guild.name))
  moBotDB.connection.commit()
  moBotDB.connection.close()
  await message.channel.send("**Automatic Standings Embed Saved**", delete_after=5)
# end newStandings

async def updateStandings(client):
  now = datetime.utcnow()

  autoUpdateStandings = getAutoUpdateStandings()

  guildsChannels = {}
  messages = []

  for standingsMessage in autoUpdateStandings:
    guildID = str(standingsMessage.guildID)
    channelID = str(standingsMessage.channelID)
    messageID = standingsMessage.messageID
    url = standingsMessage.url
    league = standingsMessage.league

    if (guildID not in guildsChannels):
      guildsChannels[guildID] = {}
    if (channelID not in guildsChannels[guildID]):
      guildsChannels[guildID][channelID] = client.get_guild(int(guildID)).get_channel(int(channelID))

    r = random.random()
    d = now.weekday()
    hourDays = [7, 0, 1] # sunday, monday, tuesday, when refresh should be once per hour
    # 54 not 60 because 90% of 60, and bot isn't up 100% of time
    if (
      (d in hourDays and r < 1/54) or 
      (d not in hourDays and r < 1/(54*24))
    ):
      try:
        messages.append([await guildsChannels[guildID][channelID].fetch_message(messageID), getStandings(url, league, client)])
      except IndexError: # error in getStandings -> getSpreadsheet -> columns = str(rows[i]).split("<td")
        pass
    
  for messageEmbed in messages:
    message = messageEmbed[0]
    embed = messageEmbed[1]

    moBotMember = message.guild.get_member(moBot)
    embed.color = moBotMember.roles[-1].color

    print("\nUpdating AOR Standings")
    await messageEmbed[0].edit(content=spaceChar, embed=messageEmbed[1])
# end updateStandings

def getStandings(url, league, client):
  
  if (type([]) is not type(league)): # given league may already be split
    league = league.split("-")
  season = league[0]
  region = league[1]
  platform = league[2]
  split = league[3]

  flags = getFlags()

  url = "%s?hl=en&widget=false&headers=false" % url
  try:
    standingsTable, roundFlag = getSpreadsheet(url)
  except IndexError:
    return

  guild = client.get_guild(aor)
  embed = discord.Embed()
  embed.set_author(name="%s-%s-%s-%s" % (season, region, platform, split), icon_url=guild.icon_url, url=url)

  lines = []
  maxNameWidth = 0
  maxPointsWdith = 0
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
        lines.append([position, flag, name, points])
        maxNameWidth = len(name) if len(name) > maxNameWidth else maxNameWidth
        maxPointsWdith = len(points) if len(points) > maxPointsWdith else maxPointsWdith
    except IndexError:
      pass

  embed.description = "**__Driver Standings - After %s__**" % flags[roundFlag.upper()]
  for line in lines:
    embed.description += "\n`%s.` %s `%s` `%s`" % (
      line[0].rjust(2, " "),
      line[1],
      line[2].ljust(maxNameWidth, " "),
      line[3].rjust(maxPointsWdith, " ")
    )
  
  embed.description += "\n[__Results Spreadsheet__](%s)"  % url.replace("_", "\\_")
  embed.set_footer(text=datetime.strftime(datetime.utcnow(), "| Refreshed: %b %d %H:%M UTC |"))
  return embed
# end getStandings

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
  SELECT message_id, channel_id, guild_id, url, league
  FROM auto_update_standings""")

  messages = []
  for record in moBotDB.cursor:
    messages.append(AutoUpdateStandingsMessage(*record))
  moBotDB.connection.close()
  return messages
# end getAutoUpdateStandings



def getRaceInputs():
  moBotDB = connectDatabase()

  raceInputs = []
  moBotDB.cursor.execute("""
    SELECT * 
    FROM race_inputs
  """)

  for record in moBotDB.cursor:
    raceInputs.append(RaceInput(*record))

  moBotDB.connection.close()
  return raceInputs
# end getRaceInputs

def connectDatabase():
  return MoBotDatabase.connectDatabase("AOR F1")
# end connectDatabase



def normalize(arr):
  minArr = min(arr)
  maxArr = max(arr)
  for i in range(len(arr)):
    arr[i] = (arr[i] - minArr) / (maxArr - minArr)
  return arr
# end normalize

def getPercentDifference(a, b):
  return (a - b) / b
# end getPercentDifference

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
'''
race = getRace(getRaceInputs(), 18, "EU", "PC", "RUSSIAN", 1, 0)
qualiEvaluation = []
raceEvaluation = []
fastestLapEvaluation = []
overtakesEvaluation = []
for raceInput in race:
  qualiEvaluation.append(evaluateQuali(raceInput, race))
  raceEvaluation.append(evaluateRace(raceInput, race))
  fastestLapEvaluation.append(evaluateFastestLap(raceInput, race))
  overtakesEvaluation.append(raceInput.quali_position - raceInput.race_position)
  print("%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
    raceInput.driver_name, 
    raceInput.quali_seconds, raceInput.race_seconds, raceInput.fastest_lap, raceInput.quali_position - raceInput.race_position,
    qualiEvaluation[-1], raceEvaluation[-1], fastestLapEvaluation[-1], overtakesEvaluation[-1]
  ))

'''
'''
qualiEvaluation = [0.15*(n-.5) for n in normalize(qualiEvaluation)]
raceEvaluation = [0.7*(n-.5) for n in normalize(raceEvaluation)]
fastestLapEvaluation = [0.05*(n-.5) for n in normalize(fastestLapEvaluation)]
overtakesEvaluation = [0.1*(n-.5) for n in normalize(overtakesEvaluation)]

print()
for i in range(len(race)):
  race[i].performance_rating = (qualiEvaluation[i] + raceEvaluation[i] + fastestLapEvaluation[i] + overtakesEvaluation[i]) / 4
  print ("%s: %s" % (race[i].driver_name, race[i].performance_rating))
'''
#setPercentDifferences()