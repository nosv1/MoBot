import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

import SecretStuff

moBot = "449247895858970624"

async def main(args, message, client):
  roles = []
  for role in message.guild.get_member(message.author.id).roles:
    roles.append(role.name.lower())
  for i in range(0, len(args)):
    args[i] = args[i].strip()

  if (args[0][-19:-1] == moBot):
    if (args[1] == "test"):
      pass
# end main

async def memberJoin(member):
  roles = member.guild.roles
  for role in roles:
    if ("peeker" in role.name.lower()):
      await member.add_roles(role)
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, cilent):
  prepareRaceMessageId = 587522662377455627 # for pit counter channel
  pitLogChannel = 570758112286343195

  user = message.guild.get_member(payload.user_id)
  if (user.name != "MoBot"):
    if (payload.emoji.name == "✅"): # if update button is clicked
      if (message.id == prepareRaceMessageId):
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await prepareRace(message)
    if (payload.emoji.name == "🏎"):
      await message.guild.get_channel(pitLogChannel).send("<@" + str(user.id) + "> has started the race.")
      await message.delete()
    if (payload.emoji.name == "🏁"):
      await message.guild.get_channel(pitLogChannel).send("---\n<@" + str(user.id) + "> has ended the race.")
      await message.channel.purge(after= await message.channel.fetch_message(prepareRaceMessageId))
    if (payload.emoji.name == "🔧"):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await driverPit(message, message.guild.get_channel(pitLogChannel))
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  user = message.guild.get_member(payload.user_id)
  if (user.name != "MoBot"):
    pass
# end mainReactionRemove

async def getRaceStartTime(pitLogChannel):
  history = pitLogChannel.history(limit=100)
  startRace = None # will be the message that says "@user has started the race."
  async for msg in history:
    if ("has started the race" in msg.content):
      startRace = msg
      break
  return startRace.created_at
# end getRaceStartTime

async def getLastPit(pitLogChannel, driverName):
  history = pitLogChannel.history(limit=100)
  lastPit = None # will be the message that says "driver has pit."
  async for msg in history:
    if (driverName + " - Pit" in msg.content):
      lastPit = msg
      break
  return lastPit.created_at

async def driverPit(message, pitLogChannel):
  parts = message.content[3:-3].split("--")
  driverName = parts[0].strip()
  numPits = int(parts[1]) + 1
  lastPitTime = 0

  pitLogMsg = await pitLogChannel.send(driverName + " has pit. Awaiting more details.")
  
  update = driverName + " -- " + str(numPits) + " -- " 
  if (len(parts) == 3):
    update += parts[2].strip()

  sinceRaceStart = pitLogMsg.created_at - await getRaceStartTime(pitLogChannel)
  
  if (numPits == 1):
    await pitLogMsg.edit(content="---\n" + driverName + " - Pit " + str(numPits) + "\n" + str(sinceRaceStart)[:-3] + " minutes since race start.")
    update += "✅"
  else:    
    lastPitTime = await getLastPit(pitLogChannel, driverName)
    betweenPits = pitLogMsg.created_at - lastPitTime
    betweenPitsMin = int(str(pitLogMsg.created_at - lastPitTime).split(":")[1][-2:])

    if (betweenPitsMin >= 19):
      await pitLogMsg.edit(content="---\n" + driverName + " - Pit " + str(numPits) + "\n" + str(betweenPits)[2:-3] + " minutes between pits.\n" + str(sinceRaceStart)[:-3] + " hours since race start.")
      update += "✅"
    else:
      await pitLogMsg.edit(content="---\n" + driverName + " - Pit " + str(numPits) + "\n" + str(betweenPits)[2:-3] + " minutes between pits.\n**This was an ILLEGAL pit. Not enough time passed between pits.**\n" + str(sinceRaceStart)[:-3] + " hours since race start.")
      update += "❌"

  await message.edit(content="```" + update + "```")
# end driverPit

async def prepareRace(message):
  await message.channel.purge(after=message)

  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Preparing Race```"))

  workbook = await openSpreadsheet()
  startingOrderSheet = workbook.worksheet("Starting Order")
  prototypeStartOrder = startingOrderSheet.range("C7:C24")
  gtStartOrder = startingOrderSheet.range("C27:C46")

  prototypeDNSs = startingOrderSheet.range(7, startingOrderSheet.col_count - 1, 24, startingOrderSheet.col_count - 1)
  gtDNSs = startingOrderSheet.range(27, startingOrderSheet.col_count - 1, 46, startingOrderSheet.col_count - 1)

  prototypeNames = []
  gtNames = []
  allNames = []

  for i in range(len(prototypeStartOrder)):
    if (prototypeStartOrder[i].value != "" and prototypeDNSs[i].value == "FALSE"):
      prototypeNames.append(prototypeStartOrder[i].value) 
      allNames.append(prototypeStartOrder[i].value)

  for i in range(len(gtStartOrder)):
    if (gtStartOrder[i].value != "" and gtDNSs[i].value == "FALSE"):
      gtNames.append(gtStartOrder[i].value) 
      allNames.append(gtStartOrder[i].value)

  allNames.sort()

  startRace = await message.channel.send("Click 🏎 when race starts.")
  await startRace.add_reaction("🏎")

  for name in allNames:
    if (name in prototypeNames):
      nameMsg = await message.channel.send("```[PROTO] " + name + " -- 0```")
      await nameMsg.add_reaction("🔧")
    else:
      nameMsg = await message.channel.send("```[GT] " + name + " -- 0```")
      await nameMsg.add_reaction("🔧")

  endRace = await message.channel.send("Click 🏁 when race ends.")
  await endRace.add_reaction("🏁")

  moBotMessages.append(await message.channel.send("```Race Prepared (WIP)```"))

  await asyncio.sleep(5)
  for i in moBotMessages:
    await i.delete()
#end prepareRace

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('XB1WEC_client_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1KCYmp_GuCR_PS16AKD3OpS7qFDu9NL4Un2YW0VUWiWI")
  return workbook
# end openSpreadsheet
