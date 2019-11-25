'''
Updating Div Number...
  Check your quali embeds! They're set to have 18 per div right now.
'''

import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import copy
import traceback

import SecretStuff
import MoBotDatabase
import RandomFunctions

# users
moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

# qualifying
'''lapSubmissionChannel = 648538018117845002
lapSubmissionEmbed = 648538377263513635
lapSubmissionLog = 648538067573145643'''
lapSubmissionChannel = 641465243897167882
lapSubmissionEmbed = 648364611761995788
lapSubmissionLog = 648401621977399298

TEPCOTT_LIGHT_BLUE = int("0x568fd7", 16)

spaceChar = "⠀"
STOPWATCH_EMOJI = "⏱️"
LINK_EMOJI = "🔗"
TRASHCAN_EMOJI = "🗑️"
CHECKMARK_EMOJI = "✅"
X_EMOJI = "❌"

epsilonLogo = "https://i.imgur.com/8ioQdaW.png"

qualiVehicles = [
  "Vehicle 1",
  "Vehicle 2",
  "Vehicle 3"
]

class Qualifier:
  def __init__(self, date, time, id, displayName, lapTime, lapTimeSec, proofLink, vehicle, deleted):
    self.date = str(date)
    self.time = str(time)
    self.id = id
    self.displayName = displayName
    self.lapTime = lapTime
    self.lapTimeSec = lapTimeSec
    self.proofLink = proofLink
    self.vehicle = vehicle
    self.deleted = int(deleted) # usually 0, only 1 if from deleteLap()
# end Qualifier

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (message.author.id != moBot):
    if (message.channel.id == lapSubmissionChannel):
      await getLinkAndLapTimeFromMsg(message)
# end main

async def mainReactionAdd(message, payload, client): 
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

# --- QUALIFYING ---

async def handleLapSubmission(message, member):
  await message.channel.trigger_typing()

  async def getVehicleFromReactions(message, member):
    for reaction in message.reactions:
      async for user in reaction.users():
        if (user.id == member.id):
          try:
            vehicle = qualiVehicles[RandomFunctions.numberEmojis.index(reaction.emoji)]
            return [vehicle]
          except ValueError: # when reaction is not a number
            pass
    await message.channel.send("**<@%s>, click a vehicle number, then click the %s.**" % (member.id, STOPWATCH_EMOJI), delete_after=10)
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
            "0"
          )

          inputLapSubmission(qualifier)
          lapSubmitted = True
          await message.channel.send("**Lap Submitted**", delete_after=3)
          await msg.delete()
          await logLapSubmission(message, qualifier)
      break

  if (lapSubmitted):
    while ("updating" in message.channel.name): # check if already updating
      await asyncio.sleep(5)

    await updateQualifyingChannel(message)

  reactionsToRemove = []
  for reaction in message.reactions:
    async for user in reaction.users():
      if (user.id == member.id):
        reactionsToRemove.append(reaction.emoji)
  for reaction in reactionsToRemove:
    await message.remove_reaction(reaction, member)
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
    proofLink = attachment.url
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
  n = datetime.utcnow()
  moBotDB = connectDatabase()
  try:
    for table in ["qualifying_log", "qualifying"]:
      if (qualifier.deleted is 1 and table == "qualifying_log"):
        continue

      moBotDB.cursor.execute("""
      INSERT INTO %s (
        date, 
        time, 
        discord_id, 
        display_name, 
        lap_time, 
        lap_time_sec, 
        proof_link, 
        vehicle
        %s
      )
      VALUES (
        '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' %s
      )
      """ % (
        table,
        "" if table == "qualifying" else ", deleted",
        n.strftime("%Y-%m-%d") if qualifier.deleted is 0 else qualifier.date,
        n.strftime("%H:%M:%S") if qualifier.deleted is 0 else qualifier.time, 
        qualifier.id,
        MoBotDatabase.replaceChars(qualifier.displayName),
        qualifier.lapTime,
        qualifier.lapTimeSec,
        MoBotDatabase.replaceChars(qualifier.proofLink),
        MoBotDatabase.replaceChars(qualifier.vehicle),
        "" if table == "qualifying" else ", '0'"
      ))
    moBotDB.connection.commit()
  except mysql.connector.errors.IntegrityError: # when duplicate id
    moBotDB.cursor.execute("""
      UPDATE qualifying
      SET 
        date = '%s',
        time = '%s',
        display_name = '%s',
        lap_time = '%s',
        lap_time_sec = '%s',
        proof_link = '%s',
        vehicle = '%s'
      WHERE
        discord_id = '%s'
    """ % (
      n.strftime("%Y-%m-%d"), # date
      n.strftime("%H:%M:%S"), # time
      MoBotDatabase.replaceChars(qualifier.displayName),
      qualifier.lapTime,
      qualifier.lapTimeSec,
      MoBotDatabase.replaceChars(qualifier.proofLink),
      MoBotDatabase.replaceChars(qualifier.vehicle),
      qualifier.id
    ))
    moBotDB.connection.commit()
  moBotDB.connection.close()
# end inputLapSubmission

async def logLapSubmission(message, qualifier):
  logChannel = message.guild.get_channel(lapSubmissionLog)
  embed = discord.Embed(color=TEPCOTT_LIGHT_BLUE)
  embed.set_author(name="TEPCOTT - Season 4", icon_url=epsilonLogo)
  embed.description = """
    **New Lap Submission**

    Driver: <@%s>
    Lap Time: `%s`
    Proof: [%s](%s)
    Submitted: `%s %s UTC`
    <#%s>
  """ % (qualifier.id, qualifier.lapTime, LINK_EMOJI, qualifier.proofLink, qualifier.date, qualifier.time, message.channel.id)

  msg = await logChannel.send(embed=embed)
  await msg.add_reaction(TRASHCAN_EMOJI)
# end logLapSubmission

def getQualifiers():
  qualifiers = []
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
    SELECT *
    FROM qualifying
    ORDER BY lap_time_sec, date, time
  """)
  for record in moBotDB.cursor:
    r = record + ("0",)
    qualifiers.append(Qualifier(*r))
  moBotDB.connection.close()
  return qualifiers
# end buildQualiEmbeds

def buildQualiEmbeds(qualifiers):
  maxNameWidth = 4
  for qualifier in qualifiers:
    l = len(qualifier.displayName)
    maxNameWidth = l if (l > maxNameWidth) else maxNameWidth

  numQualifiers = len(qualifiers)
  driversPerEmbed = 18
  numEmbeds = (numQualifiers // driversPerEmbed) + 1 if (numQualifiers % driversPerEmbed is not 0) else 0
  
  embed = discord.Embed(color=TEPCOTT_LIGHT_BLUE)
  embed.set_author(name="TEPCOTT - Season 4", icon_url=epsilonLogo)
  embed.description = "`%s` `%s` `Lap Time` `Car`" % (
    "".rjust(1+len(str(numQualifiers))," "),
    "Name".ljust(maxNameWidth," ")
  )
  embeds = []
  for i in range(numEmbeds):
    embeds.append(copy.deepcopy(embed))

  for qualifier in qualifiers:
    position = qualifiers.index(qualifier) + 1
    embedNumber = (position - 1) // driversPerEmbed
    embed = embeds[embedNumber]
    embed.description += "\n`%s.` `%s` `%s` `%s` [%s](%s)" % (
      str(position).rjust(len(str(numQualifiers)), " "),
      qualifier.displayName.ljust(maxNameWidth, " "),
      qualifier.lapTime,
      str(qualiVehicles.index(qualifier.vehicle) + 1).center(3, " "),
      LINK_EMOJI,
      qualifier.proofLink
    )
    embeds[embedNumber] = embed
  return embeds
# end buildQualiEmbeds

async def updateQualifyingChannel(message):
  qualifiers = getQualifiers()
  embeds = buildQualiEmbeds(qualifiers)

  channel = message.guild.get_channel(lapSubmissionChannel)
  message = await channel.fetch_message(lapSubmissionEmbed)
  
  await message.channel.edit(name=message.channel.name + " updating")

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

  await message.channel.edit(name=message.channel.name.replace("updating", ""))
# end updateQualifyingChannel

async def confirmDeleteLap(message):
  await message.channel.trigger_typing()
  qualifier = getQualifierFromEmbed(message.embeds[0])

  embed = discord.Embed(color=TEPCOTT_LIGHT_BLUE)
  embed.set_author(name="TEPCOTT - Season 4", icon_url=epsilonLogo)
  embed.description = """
    **Are you sure you want to delete this lap time?**

    Driver: <@%s>
    Lap Time: `%s`
    Proof: [%s](%s)
    Submitted: `%s %s UTC`
  """ % (
    qualifier.id,
    qualifier.lapTime,
    LINK_EMOJI,
    qualifier.proofLink,
    qualifier.date,
    qualifier.time
  )
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
      break

  if (not reason):
    await message.channel.send("**Reason Not Found**\nPlease include a reason for deleting a lap time, and then click the %s." % CHECKMARK_EMOJI)
    await message.remove_reaction(CHECKMARK_EMOJI, member)
    return

  qualifer = getQualifierFromEmbed(message.embeds[0])
  driver = message.guild.get_member(int(qualifer.id))

  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
    DELETE FROM qualifying
    WHERE
      discord_id = '%s'
  """ % (
    qualifer.id
  ))
  
  await message.clear_reactions()
  await message.channel.send("**Lap Deleted**")
  try:
    await driver.send("**TEPCOTT QUALIFYING LAP DELETED**\nLap Time: `%s`\nReason: `%s`" % (qualifer.lapTime, reason))
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
    qualifer.id,
    qualifer.date,
    qualifer.time
  ))
  moBotDB.connection.commit()

  moBotDB.cursor.execute("""
    SELECT *
    FROM qualifying_log
    WHERE
      discord_id = '%s' AND
      deleted <> 1
    ORDER BY date DESC, time DESC
  """ % (
    qualifer.id
  ))
  qualifer = None
  for record in moBotDB.cursor:
    r = record[:-1] + ("1",) # only setting to 1 to not log an old time
    qualifer = Qualifier(*r)
    break

  if (qualifer is not None):
    inputLapSubmission(qualifer)
  moBotDB.connection.close()

  embed = message.embeds[0].to_dict()
  msg = await message.channel.fetch_message(int(embed["footer"]["text"].split("|")[1]))
  embed["description"] += "\n\n**LAP DELETED:** `%s`" % reason
  embed["description"] = embed["description"].replace("New Lap Submission", "~~New Lap Submission~~")
  await message.edit(embed=discord.Embed().from_dict(embed))
  for reaction in msg.reactions:
    if (reaction.emoji == TRASHCAN_EMOJI):
      async for user in reaction.users():
        await msg.remove_reaction(reaction.emoji, user)
      break

  await updateQualifyingChannel(message)
# end deleteLap

def getLapTimeSecFromLapTime(lapTime):
  minutes = int(lapTime.split(":")[0])
  seconds = float(lapTime.split(":")[1])
  return minutes * 60 + seconds
# end getLapTimeSecFromLapTime

def getQualifierFromEmbed(embed):
  driverID = embed.description.split("Driver: <@")[1].split(">")[0].replace("!", "")
  lapTime = embed.description.split("Lap Time: `")[1].split("`")[0]
  moBotDB = connectDatabase()
  moBotDB.cursor.execute("""
  SELECT *
  FROM qualifying_log
  WHERE 
    discord_id = '%s' AND
    lap_time = '%s'
  """ % (driverID, lapTime))

  qualifer = None
  for record in moBotDB.cursor:
    r = record[:-1] + ("0",)
    qualifer = Qualifier(*r)
    break

  moBotDB.connection.close()
  return qualifer
# end getQualifierFromEmbed

# --- END QUALIFYING ---

async def deleteMsgs(sleep, messagesToDelete):
  await asyncio.sleep(sleep)
  for msg in messagesToDelete:
    await msg.delete()
# end deleteMsgs

def connectDatabase():
  return MoBotDatabase.connectDatabase("TEPCOTT S4")
# end connectDatabase