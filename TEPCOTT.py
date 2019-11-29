import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import copy
import traceback
import sys

import SecretStuff
import MoBotDatabase
import RandomSupport

client = None

# users
moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

# qualifying
lapSubmissionChannel = 648538018117845002
lapSubmissionEmbed = 648538377263513635
lapSubmissionLog = 648538067573145643
'''lapSubmissionChannel = 648924604022390793
lapSubmissionEmbed = 648957018446626846
lapSubmissionLog = 648401621977399298'''

# pit marshalls
pitMarshallChannel = 649741834783817738
pitMarshallEmbed = 649743670161178654
pitMarshallRole = 649741250114617363

TEPCOTT_LIGHT_BLUE = int("0x568fd7", 16)

spaceChar = "⠀"
STOPWATCH_EMOJI = "⏱️"
LINK_EMOJI = "🔗"
TRASHCAN_EMOJI = "🗑️"
CHECKMARK_EMOJI = "✅"
X_EMOJI = "❌"
CROWN_EMOJI = "👑"
WRENCH_EMOJI = "🔧"

epsilonLogo = "https://i.imgur.com/8ioQdaW.png"

class Qualifier:
  def __init__(self, date, time, discordID, displayName, lapTime, lapTimeSec, proofLink, vehicle):
    self.date = str(date)
    self.time = str(time)
    self.discordID = discordID
    self.displayName = MoBotDatabase.replaceChars(displayName)
    self.lapTime = lapTime
    self.lapTimeSec = lapTimeSec
    self.proofLink = MoBotDatabase.replaceChars(proofLink)
    self.vehicle = MoBotDatabase.replaceChars(vehicle)
# end Qualifier

class Driver:
  def __init__(self, discordID, displayName, division, previousDivision, totalPoints):
    self.discordID = discordID
    self.displayName = MoBotDatabase.replaceChars(displayName)
    self.division = division
    self.previousDivision = previousDivision
    self.totalPoints = totalPoints
# end Driver

class PitMarshall:
  def __init__(self, discordID, displayName, host, pitMarshall):
    self.discordID = discordID
    self.displayName = displayName
    self.host = host
    self.pitMarshall = pitMarshall
# end PitMarshall

class Event:
  def __init__(self, numberOfDivs, driversPerDiv, qualiStartDate, qualiEndDate, qualiVehicles, roundDates): # roundDates is list of dates
    self.numberOfDivs = numberOfDivs
    self.driversPerDiv = driversPerDiv
    self.qualiStartDate = datetime.strptime(qualiStartDate, "%Y-%m-%d %H:%M")
    self.qualiEndDate = datetime.strptime(qualiEndDate, "%Y-%m-%d %H:%M")
    self.qualiVehicles = [vehicle for vehicle in qualiVehicles]
    self.roundDates = [datetime.strptime(dateStr, "%Y-%m-%d") for dateStr in roundDates]
# end Event

async def main(args, message, c):
  global client
  client = c

  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (message.author.id != moBot):
    if (message.channel.id == lapSubmissionChannel):
      await getLinkAndLapTimeFromMsg(message)
# end main

async def mainReactionAdd(message, payload, c):
  global client
  client = c

  member = message.guild.get_member(payload.user_id)

  if (payload.emoji.name == STOPWATCH_EMOJI):
    if (message.id == lapSubmissionEmbed):
      await handleLapSubmission(message, member)

  elif (payload.emoji.name == TRASHCAN_EMOJI):
    if (message.channel.id == lapSubmissionLog):
      await confirmDeleteLap(message)
      await message.remove_reaction(TRASHCAN_EMOJI, member)

  elif (payload.emoji.name == CHECKMARK_EMOJI):
    if (message.channel.id == lapSubmissionLog):
      await deleteLap(message, member)

  elif (payload.emoji.name == X_EMOJI):
    if (message.channel.id == lapSubmissionLog):
      await message.delete()
      await message.channel.send("**Canceled**", delete_after=3)

  elif (payload.emoji.name in [CROWN_EMOJI, WRENCH_EMOJI]):
    if (message.channel.id == pitMarshallChannel):
      await handlePitMarshall(message, member, payload)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

# --- PIT MARSHALLS ---

async def handlePitMarshall(message, member, payload):
  await message.channel.trigger_typing()
  moBotMessage = await waitForUpdate(message)

  async def checkForDiv(msg, member):
    reactions = msg.reactions
    for reaction in reactions:
      async for user in reaction.users():
        if (user.id == member.id):
          try:
            div = RandomSupport.emojiNumbertoNumber(reaction.emoji)
            return div if div <= getEventDetails().numberOfDivs else False
          except ValueError: # when a number is not clicked
            pass
    return False
  # end checkForDiv

  def insertPitMarshall(member, div, payload):
    moBotDB = connectDatabase()
    try:
      moBotDB.cursor.execute("""
        INSERT INTO pit_marshalls(
          discord_id, display_name, host, pit_marshall
        ) VALUES (
          '%s', '%s', '%s', '%s'
        )
      """ % (
        member.id, 
        member.display_name, 
        div if (payload.emoji.name == CROWN_EMOJI) else None,
        div if (payload.emoji.name == WRENCH_EMOJI) else None,
      ))
      moBotDB.connection.commit()
      moBotDB.connection.close()
      return True
    except mysql.connector.IntegrityError:
      moBotDB.connection.close()
      return False
  # end insertPitMarshall

  def removePitMarshall(member, div, payload): # find current person, then remove if same
    moBotDB = connectDatabase()
    moBotDB.cursor.execute("""
      SELECT discord_id, display_name
      FROM pit_marshalls
      WHERE 
        host = %s AND
        pit_marshall = %s
    """ % (
      div if payload.emoji.name == CROWN_EMOJI else 0,
      div if payload.emoji.name == WRENCH_EMOJI else 0
    ))

    delete = True
    for record in moBotDB.cursor:
      if (int(record[0]) == member.id):
        break

    if (delete):
      moBotDB.cursor.execute("""
        DELETE FROM pit_marshalls
        WHERE 
          host = %s AND
          pit_marshall = %s 
      """ % (
        div if payload.emoji.name == CROWN_EMOJI else 0,
        div if payload.emoji.name == WRENCH_EMOJI else 0
      ))
      moBotDB.connection.commit()
      moBotDB.connection.close()
      return False
    else:
      moBotDB.connection.close()
      return True
  # end removePitMarshall

  div = await checkForDiv(message, member)
  if (div):
    if (insertPitMarshall(member, div, payload)):
      await message.edit(embed=buildPitMarshallEmbed())
      await moBotMessage.edit(content="**<@%s> is now a %s for Division %s.**" % (
        member.id, 
        "Host" if payload.emoji.name == CROWN_EMOJI else "Pit-Marshall",
        div
      ), delete_after=10)
      await member.add_roles(RandomSupport.getRole(message.guild, pitMarshallRole))
      
    else:
      if (removePitMarshall(member, div, payload)):
        await moBotMessage.edit(content="**<@%s>, there is already a %s for Division %s.**" % (
        member.id,
        "Host" if payload.emoji.name == CROWN_EMOJI else "Pit-Marshall",
        div
        ), delete_after=10)
      else:
        await message.edit(embed=buildPitMarshallEmbed())
        await moBotMessage.edit(content="**<@%s> is no longer a %s for Division %s.**" % (
        member.id,
        "Host" if payload.emoji.name == CROWN_EMOJI else "Pit-Marshall",
        div
        ), delete_after=10)
        await member.remove_roles(RandomSupport.getRole(message.guild, pitMarshallRole))
  else:
    await moBotMessage.edit(content="**<@%s>, click a division number, and then click the %s or the %s.**" % (member.id, CROWN_EMOJI, WRENCH_EMOJI), delete_after=10)
    await message.remove_reaction(payload.emoji.name, member)

  for reaction in message.reactions:
    async for user in reaction.users():
      if (user.id == member.id):
        await message.remove_reaction(reaction.emoji, member)
  await message.channel.edit(name=message.channel.name.replace("updating", ""))
# end handlePitMarshall

def buildPitMarshallEmbed():
  pitMarshalls = getPitMarshalls()
  event = getEventDetails()

  embed = buildBasicEmbed()
  embed.description = ""
  for i in range(event.numberOfDivs):
    div = i + 1
    embed.description += "\n\n**Division %s**" % div

    embed.description += "\nHost: "
    host = [pitMarshall for pitMarshall in pitMarshalls if pitMarshall.host == div]
    if (host):
      embed.description += "`%s`" % host[0].displayName

    embed.description += "\nPit-Marshall: "
    pitMarshall = [pitMarshall for pitMarshall in pitMarshalls if pitMarshall.pitMarshall == div]
    if (pitMarshall):
      embed.description += "`%s`" % pitMarshall[0].displayName

  embed.description += "\n\n**Start Times**\nTBD..."
  # still need start times

  embed.description += "\n\n**Instructions**"
  embed.description += "\n1. Click the division number"
  embed.description += "\n2. Click the %s or the %s" % (CROWN_EMOJI, WRENCH_EMOJI)
  embed.description += "\n%sa. %s for Host" % (spaceChar, CROWN_EMOJI)
  embed.description += "\n%sb. %s for Pit-Marshall" % (spaceChar, WRENCH_EMOJI)
  embed.description += "\n*It is the same process for adding and removing yourself.*"
  embed.description += "\n***Hosts __SHOULD NOT__ have a race before the race they are hosting.***"

  return embed
# end buildPitMarshallEmbeds

def clearPitMarshalls():
  pass
# end clearPitMarshalls

def getPitMarshalls():
  pitMarshalls = []
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
    SELECT *
    FROM pit_marshalls
  """)
  for record in moBotDB.cursor:
    pitMarshalls.append(PitMarshall(*record))
  moBotDB.connection.close()
  return pitMarshalls
# end getPitMarshalls

# --- END PIT MARSHALLS ---

# --- START ORDERS ---

def buildStartOrderEmbeds():
  def getWidths(startOrder):
    maxNameWidth = 4
    maxPointsWidth = 1
    for d in startOrder:
      ld = len(d[0])
      lp = len(str(d[2]))
      maxNameWidth = ld if (ld > maxNameWidth) else maxNameWidth
      maxPointsWidth = lp if (lp > maxPointsWidth) else maxPointsWidth
    return maxNameWidth, maxPointsWidth
  # end getWidths

  startOrders = getStartOrders()

  embed = buildBasicEmbed()
  embed.description = ""
  embeds = [copy.deepcopy(embed) for i in startOrders]
  for embed in embeds:
    div = embeds.index(embed) + 1
    nameWidth, pointsWidth = getWidths(startOrders[div-1])

    embed.description += "**Division %s**\n`Pos` `%s` `D` `%s`" % (
      div, "Name".ljust(nameWidth), 
      "P".center(pointsWidth)
    )
    for driver in startOrders[div-1]:
      pos = startOrders[div-1].index(driver) + 1
      name = driver[0]
      previousDivision = driver[1]
      totalPoints = driver[2]

      embed.description += "`%s.` `%s` `%s` `%s`\n" % (
        str(pos).rjust(2),
        name.ljust(nameWidth),
        previousDivision,
        str(totalPoints).rjust(pointsWidth)
      )

    embed.description += "*D - Previous Division\nP - Total Points*"
  return embeds
# end buildStartOrderEmbeds

def getStartOrders():
  event = getEventDetails()
  startOrders = [[] for i in range(event.numberOfDivs)]

  moBotDB = connectDatabase()  
  for i in range(event.numberOfDivs):
    div = i + 1
    moBotDB.cursor.execute("""
      SELECT display_name, previous_division, total_points
      FROM division_%s
    """ % div)
    for record in moBotDB.cursor:
      startOrders[i].append([r for r in record])
  moBotDB.connection.close()

  for i in range(1, event.numberOfDivs):
    stayedInDiv = [d for d in startOrders[i] if d[1] == i + 1]
    demoted = [d for d in startOrders[i] if d[1] > i + 1]
    promoted = [d for d in startOrders[i] if d[1] < i + 1]
    startOrders[i] = stayedInDiv + demoted + promoted
  return startOrders
# end getStartOrders

# --- END START ORDERS ---

# --- QUALIFYING ---

''' 
check to make sure lap and link are in message
check to make sure user clicked a vehicle 
handle lap submission
input lap
update drivers and divs
log lap
get qualifiers
build embeds
update qualifying channel

confirm delete lap
check for reason
delete lap
update qualifying channel
'''

async def handleLapSubmission(message, member):
  await message.channel.trigger_typing()
  moBotMessage = await waitForUpdate(message)
  event = getEventDetails()

  async def getVehicleFromReactions(message, member):
    for reaction in message.reactions:
      async for user in reaction.users():
        if (user.id == member.id):
          try:
            vehicle = event.qualiVehicles[RandomSupport.emojiNumbertoNumber(reaction.emoji)-1] 
            return [vehicle]
          except ValueError: # when reaction is not a number
            pass
    await moBotMessage.edit(content="**<@%s>, click a vehicle number, then click the %s.**" % (member.id, STOPWATCH_EMOJI), delete_after=10)
    return []
  # end getVehicleFromReactions

  history = await message.channel.history(after=message, oldest_first=False).flatten()
  lapSubmitted = False
  for msg in history:
    if (msg.author.id == member.id):
      linkLapTimeCheck = await getLinkAndLapTimeFromMsg(msg) # returns array of good results or False if bad
      if (linkLapTimeCheck):
        vehicleCheck = await getVehicleFromReactions(message, member)
        proofLink = linkLapTimeCheck[0]
        lapTime = linkLapTimeCheck[1]
        if (vehicleCheck):
          vehicle = vehicleCheck[0]
          sent = msg.created_at
          qualifier = Qualifier(
            sent.strftime("%Y-%m-%d"),
            sent.strftime("%H:%M:%S"),
            member.id,
            member.display_name,
            lapTime,
            getLapTimeSecFromLapTime(lapTime),
            proofLink,
            vehicle,
          )

          lapSubmitted = True # not submitting until a couple lines below...
          await msg.delete()
      break

  if (lapSubmitted):
    inputLapSubmission(qualifier)
    await logLapSubmission(message, qualifier)
    await moBotMessage.edit(content="**Lap Submitted**", delete_after=3)

    await updateQualifyingChannel(message)

  reactionsToRemove = []
  for reaction in message.reactions:
    async for user in reaction.users():
      if (user.id == member.id):
        reactionsToRemove.append(reaction.emoji)
  for reaction in reactionsToRemove:
    await message.remove_reaction(reaction, member)

  await message.channel.edit(name=message.channel.name.replace("updating", ""))
# end handleLapSubmission

async def getLinkAndLapTimeFromMsg(msg):
  def getLapTimeFromMsg(msg):
    lapTime = msg.content[:9].strip()
    lapTime = lapTime[-8:-7] + ":" + lapTime[-6:-4] + "." + lapTime[-3:]
    return lapTime
  # end getLapTimeFromMsg

  def checkIfLegitLap(lapTime):
    try:
      lapTimeSec = getLapTimeSecFromLapTime(lapTime)
      return True
    except:
      return False
  # end checkIfLegitLap

  if (msg.attachments):
    proofLink = await RandomSupport.saveImageReturnURL(msg.attachments[0], client)
    lapTime = getLapTimeFromMsg(msg)
  elif ("http" in msg.content):
    proofLink = "http" + msg.content.split("http")[1].split(">")[0]
    lapTime = getLapTimeFromMsg(msg)
  else:
    m = await msg.channel.send("**No Screenshot or Video**\nTo submit a lap, proof must be included. Either link the proof or attach it in your message.\n*Deleting message in 30 seconds...*")
    await deleteMsgs(30, [m, msg])
    return False

  if (checkIfLegitLap(lapTime)):
    return [proofLink, lapTime]
  else:
    m = await msg.channel.send("**Not a Valid Lap**\n<@%s>, a lap time could not be parsed from your message. In the same message, please type your lap time (MM:SS.000) then include your proof (attachment or link of video/screnshot).\nEx. `1:23.456 https://i.imgur.com/8ioQdaW.png`\n*Deleting message in 30 seconds...*" % msg.author.id)
    await deleteMsgs(30, [m, msg])
    return False
# end getLinkAndLapTimeFromMsg

def inputLapSubmission(qualifier):
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
  INSERT INTO qualifying_log (
    date, 
    time, 
    discord_id, 
    display_name, 
    lap_time, 
    lap_time_sec, 
    proof_link, 
    vehicle
  ) VALUES (
    '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'
  )
  """ % (
    qualifier.date,
    qualifier.time, 
    qualifier.discordID,
    qualifier.displayName,
    qualifier.lapTime,
    qualifier.lapTimeSec,
    qualifier.proofLink,
    qualifier.vehicle,
  ))
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end inputLapSubmission

async def logLapSubmission(message, qualifier):
  logChannel = message.guild.get_channel(lapSubmissionLog)
  embed = buildBasicEmbed()
  embed.description = "**New Lap Submission**\n"
  embed.description += "Driver: <@%s>\n" % qualifier.discordID
  embed.description += "Lap Time: `%s`\n" % qualifier.lapTime
  embed.description += "Vehicle: `%s`\n" % qualifier.vehicle
  embed.description += "Proof: [%s](%s)\n" % (
    qualifier.proofLink, 
    qualifier.proofLink
  )
  embed.description += "Submitted: `%s %s UTC`\n" % (
    qualifier.date, 
    qualifier.time
  )
  embed.description += "<#%s>\n" % message.channel.id

  msg = await logChannel.send(embed=embed)
  await msg.add_reaction(TRASHCAN_EMOJI)
# end logLapSubmission

def getQualifiers():
  qualifiers = []
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
    SELECT *
    FROM qualifying_standings
  """)
  for record in moBotDB.cursor:
    qualifiers.append(Qualifier(*record))
  moBotDB.connection.close()
  return qualifiers
# end getQualifiers

def buildQualiEmbeds(qualifiers):
  event = getEventDetails()

  maxNameWidth = 4
  for qualifier in qualifiers:
    l = len(qualifier.displayName)
    maxNameWidth = l if (l > maxNameWidth) else maxNameWidth

  numQualifiers = len(qualifiers)
  numEmbeds = (numQualifiers // event.driversPerDiv) + 1 if (numQualifiers % event.driversPerDiv is not 0) else 0
  
  embed = buildBasicEmbed()
  embed.description = "`Pos` `%s` `Lap Time` `Car`" % (
    "Name".ljust(maxNameWidth," ")
  )
  embeds = []
  for i in range(numEmbeds):
    embeds.append(copy.deepcopy(embed))

  for qualifier in qualifiers:
    position = qualifiers.index(qualifier) + 1
    embedNumber = (position - 1) // event.driversPerDiv
    embed = embeds[embedNumber]
    embed.description += "\n`%s.` `%s` `%s` `%s` [%s](%s)" % (
      str(position).rjust(2, " "),
      qualifier.displayName.ljust(maxNameWidth, " "),
      qualifier.lapTime,
      str(event.qualiVehicles.index(qualifier.vehicle) + 1).center(3, " "),
      LINK_EMOJI,
      qualifier.proofLink
    )
    embeds[embedNumber] = embed
  return embeds
# end buildQualiEmbeds

async def updateQualifyingChannel(message):
  channel = message.guild.get_channel(lapSubmissionChannel)
  message = await channel.fetch_message(lapSubmissionEmbed)
  await message.channel.send("Waiting for update to finish...")

  qualifiers = getQualifiers()
  embeds = buildQualiEmbeds(qualifiers)

  history = await message.channel.history(after=message, oldest_first=False).flatten()
  for msg in history: # remove old standings
    if (msg.author.id == message.author.id):
      await msg.delete()

  for i in range(len(embeds)): # send new standings
    if (i is 0):
      await message.channel.send(embed=embeds[i])
    else:
      embed = embeds[i].to_dict()
      del embed["author"]
      embed = discord.Embed().from_dict(embed)
      embed.description = "\n".join(embed.description.split("\n")[1:])
      await message.channel.send(embed=embed)

  setDriverDivsFromQualifiers()
# end updateQualifyingChannel

async def confirmDeleteLap(message):
  await message.channel.trigger_typing()
  qualifier = getQualifierFromEmbed(message.embeds[0])

  embed = buildBasicEmbed()
  embed.description = "**Are you sure you want to delete this lap time?**\n"
  embed.description += "Driver: <@%s>\n" % qualifier.discordID
  embed.description += "Lap Time: `%s`\n" % qualifier.lapTime
  embed.description += "Proof: [%s](%s)\n" % (
    LINK_EMOJI,
    qualifier.proofLink
  )
  embed.description += "Submitted: `%s %s UTC`\n" % (
    qualifier.date,
    qualifier.time
  )
  embed.description += "Type your reasoning, and then click the %s to delete the lap.\n" % CHECKMARK_EMOJI
  embed.description += "Click the %s to cancel.\n" % X_EMOJI
  embed.set_footer(text="| %s |" % message.id)

  msg = await message.channel.send(embed=embed)
  await msg.add_reaction(CHECKMARK_EMOJI)
  await msg.add_reaction(X_EMOJI)
# end confirmDeleteLap

async def deleteLap(message, member):
  history = await message.channel.history(after=message, oldest_first=False).flatten()

  reason = ""
  for msg in history:
    if (msg.author.id == member.id):
      reason = msg.content
      await msg.delete()
      break

  if (not reason):
    await message.channel.send("**Reason Not Found**\nPlease include a reason for deleting a lap time, and then click the %s." % CHECKMARK_EMOJI, delete_after=10)
    await message.remove_reaction(CHECKMARK_EMOJI, member)
    return

  qualifier = getQualifierFromEmbed(message.embeds[0])
  driver = message.guild.get_member(int(qualifier.discordID))

  moBotDB = connectDatabase()
  
  await message.clear_reactions()
  await message.channel.send("**Lap Deleted**")
  try:
    await driver.send("**TEPCOTT QUALIFYING LAP DELETED**\nLap Time: `%s`\nReason: `%s`" % (qualifier.lapTime, reason))
    await message.channel.send("**Driver Notified**")
  except discord.errors.Forbidden:
    await message.channel.send("**Driver Not Notified**\nDriver does not allow DMs from bots. Message the driver manually.")

  moBotDB.cursor.execute("""
    UPDATE qualifying_log
    SET
      deleted = '1'
    WHERE
      discord_id = '%s' AND
      date = '%s' AND
      time = '%s'
  """ % (
    qualifier.discordID,
    qualifier.date,
    qualifier.time
  ))
  moBotDB.connection.commit()
  moBotDB.connection.close()

  embed = message.embeds[0].to_dict()
  msg = await message.channel.fetch_message(int(embed["footer"]["text"].split("|")[1]))
  embed = msg.embeds[0].to_dict()
  embed["description"] += "\n\n**LAP DELETED:** `%s`" % reason
  embed["description"] = embed["description"].replace("New Lap Submission", "~~New Lap Submission~~")
  await msg.edit(embed=discord.Embed().from_dict(embed))
  for reaction in msg.reactions:
    if (reaction.emoji == TRASHCAN_EMOJI):
      async for user in reaction.users():
        await msg.remove_reaction(reaction.emoji, user)
      break
  await message.edit(embed=discord.Embed().from_dict(embed))

  await updateQualifyingChannel(message)
# end deleteLap

def getLapTimeSecFromLapTime(lapTime):
  minutes = int(lapTime.split(":")[0])
  seconds = float(lapTime.split(":")[1])
  return minutes * 60 + seconds
# end getLapTimeSecFromLapTime

def getQualifierFromEmbed(embed):
  discordID = embed.description.split("Driver: <@")[1].split(">")[0].replace("!", "")
  lapTime = embed.description.split("Lap Time: `")[1].split("`")[0]
  dateTime = embed.description.split("Submitted: `")[1].split(" ")
  date = dateTime[0]
  time = dateTime[1]

  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
  SELECT *
  FROM qualifying_log
  WHERE 
    discord_id = '%s' AND
    lap_time = '%s' AND
    date = '%s' AND
    time = '%s'
  """ % (discordID, lapTime, date, time))

  qualifier = None
  for record in moBotDB.cursor:
    qualifier = Qualifier(*record[:-1])
    break

  moBotDB.connection.close()
  return qualifier
# end getQualifierFromEmbed

def setDriverDivsFromQualifiers(): # use quali table to update driver divs...
  qualifiers = getQualifiers()
  drivers = getDrivers()
  event = getEventDetails()

  moBotDB = connectDatabase()
  for qualifier in qualifiers:
    div = qualifiers.index(qualifier) // event.driversPerDiv + 1
    div = event.numberOfDivs + 1 if div > event.numberOfDivs else div
    for driver in drivers:
      if (qualifier.discordID == driver.discordID):
        sql = """
          \nUPDATE drivers
          SET 
            division = '%s'
          WHERE discord_id = '%s'; 
        """ % (
          div, 
          driver.discordID
        )
        break
    else:
      sql = """
        \nINSERT INTO drivers (
          display_name,
          division,
          total_points
        ) VALUES (
          '%s', '%s', '%s',
        ); """ % (
          qualifier.discordID,
          qualifier.displayName,
          div
        )
    moBotDB.cursor.execute(sql)
  
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end setDriverDivsFromQualifiers

# --- END QUALIFYING ---

async def waitForUpdate(message): 
  moBotMessage = await message.channel.send("**Waiting for update to finish...**")
  while ("updating" in message.channel.name):
    await asyncio.sleep(5)
  await message.channel.edit(name=message.channel.name + " updating")
  return moBotMessage
# end waitForUpdate

def buildBasicEmbed():
  embed = discord.Embed(color=TEPCOTT_LIGHT_BLUE)
  embed.set_author(name="TEPCOTT - Season 4", icon_url=epsilonLogo)
  return embed
# end buildBasicEmbed

def getEventDetails():
  moBotDB = connectDatabase()

  moBotDB.cursor.execute("SHOW COLUMNS FROM event_details")
  roundDateIndexes = []
  qualiVehicleIndexes = []

  index = 0
  for record in moBotDB.cursor:
    if ("round_date" in record[0]):
      roundDateIndexes.append(index)
    if ("quali_vehicle" in record[0]):
      qualiVehicleIndexes.append(index)
    index += 1

  moBotDB.cursor.execute("SELECT * FROM event_details")
  t = ()
  for record in moBotDB.cursor:
    for i in range(len(record)):
      if (i not in roundDateIndexes and i not in qualiVehicleIndexes):
        t += (record[i],)

      elif (i == roundDateIndexes[0]):
        t += ([date for date in record[min(roundDateIndexes):max(roundDateIndexes)+1]],)

      elif (i == qualiVehicleIndexes[0]):
        t += ([vehicle for vehicle in record[min(qualiVehicleIndexes):max(qualiVehicleIndexes)+1]],)
  moBotDB.connection.close()
  return Event(*t)
# end getEventDetails

def getDrivers():
  drivers = []
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
    SELECT *
    FROM drivers
  """)
  for record in moBotDB.cursor:
    drivers.append(Driver(*record))
  moBotDB.connection.close()
  return drivers
# end getDrivers

async def deleteMsgs(sleep, messagesToDelete):
  await asyncio.sleep(sleep)
  for msg in messagesToDelete:
    await msg.delete()
# end deleteMsgs

def connectDatabase():
  return MoBotDatabase.connectDatabase("TEPCOTT S4")
# end connectDatabase