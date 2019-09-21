import discord
from datetime import datetime, timedelta
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import asyncio
import operator
import traceback

import SecretStuff

import RandomFunctions

# common member ids
moID = 405944496665133058
moBot = 449247895858970624

# common channels
COTM_STREAMS = 527161746473877504
QUALIFYING = 607693838642970819
QUALI_SCREENSHOTS = 607694176133447680
START_ORDERS = 622484589465829376
STANDINGS = 622467542497099786
DIVISION_UPDATES = 527319768911314944

# common emojis
CHECKMARK_EMOJI = "✅"
ARROWS_COUNTERCLOCKWISE_EMOJI  = "🔄"
THUMBSUP_EMOJI = "👍"
WAVE_EMOJI = "👋"
FIST_EMOJI = "✊"
CROWN = "👑"
WRENCH = "🔧"
GLOBE_WITH_LINES = "🌐"

spaceChar = "⠀"
logos = {
  "cotmFaded" : "https://i.gyazo.com/e720604af6507b3fc905083e8c92edf7.png",
  "d1" : "https://i.gyazo.com/6e47789b04f7dcd859893da2d2ee623d.png",
  "d2" : "https://i.gyazo.com/095a118003220990734330eb74ce14fe.png",
  "d3" : "https://i.gyazo.com/53ab40295fcdd9cbef5b443fd118a1a1.png",
  "d4" : "https://i.gyazo.com/1892dfb94a9d9d8fba6242991fb4d691.png",
  "d5" : "https://i.gyazo.com/5a56e3281bfb37b8467b1c125168b04f.png",
  "d6" : "https://i.gyazo.com/91d5cb3aa8688fe885a4e907fbf3bb78.png",
  "d7" : "https://i.gyazo.com/33e6ec2a82539f251a66aa8f2c6ee2fa.png",
}
divisionEmojis = {
  "1" : 527285368240734209,
  "2" : 527285430526148618,
  "3" : 527285478764969984,
  "4" : 527285532099870730,
  "5" : 527285566501552129,
  "6" : 527285612160614410,
  "7" : 527285647837364244,
}

async def main(args, message, client):
  try:
    authorPerms = message.channel.permissions_for(message.author)
  except:
    pass
    
  qualifyingChannel = message.guild.get_channel(QUALIFYING)
  qualiScreenshotsChannel = message.guild.get_channel(QUALI_SCREENSHOTS)

  if (args[0][-19:-1] == str(moBot)):
    if (args[1] == "quali" and authorPerms.administrator):
      await submitQualiTime(message, qualifyingChannel, None, None, client)
    if (message.author.id == moID):
      try:
        if (args[1] == "update"):
          if (args[2] == "standings"):
            await updateStandings(message.guild, await openSpreadsheet())
          elif (args[2] == "start" and args[3] == "orders"):
            await updateStartOrders(message.guild, await openSpreadsheet())
          elif (args[2] == "div" and args[3] == "list"):
            divList = await updateDriverRoles(message, await openSpreadsheet())
            await updateDivList(message, divList)
      except IndexError:
        pass
  # end main
# end main

async def mainReactionAdd(message, payload, client):
  member = message.guild.get_member(payload.user_id)
  memberPerms = message.channel.permissions_for(member)
  qualifyingChannel = message.guild.get_channel(QUALIFYING)
  qualiScreenshotsChannel = message.guild.get_channel(QUALI_SCREENSHOTS)

  if ("MoBot" not in member.name):
    if (payload.emoji.name == CHECKMARK_EMOJI):
      if (message.id == 614836845267910685): # message id for "Do you need to submit quali time"  
        await addUserToQualiScreenshots(message, member, qualiScreenshotsChannel, client)
        await message.remove_reaction(payload.emoji.name, member)
      elif (message.id == 620778190767390721): # message id for voting
        await openVotingChannel(message, member)
        await message.remove_reaction(payload.emoji.name, member)

    if ("are you ready to vote" in message.content):
      if (payload.emoji.name == CHECKMARK_EMOJI):
        await votingProcess(message, member, client)
      elif (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        await resetVotes(message)

    if (message.channel.id == qualiScreenshotsChannel.id):
      if (message.channel.permissions_for(member).administrator and payload.emoji.name == THUMBSUP_EMOJI):
        await waitForQualiTime(message, member, payload, qualifyingChannel, client)

    if (message.id == 620811567210037253): # message id for Reserves Embed
      if (payload.emoji.name == WAVE_EMOJI):
        await reserveNeeded(message, member)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveAvailable(message, member, payload, client)
        await message.channel.send(".", delete_after=0)

    if (message.id == 622137318513442816): # message id for streamer embed
      if (payload.emoji.name in ["Twitch", "Mixer", "Youtube"]):
        await addStreamer(message, member, payload, client)
      if (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        for reaction in message.reactions:
          async for user in reaction.users():
            if (reaction.emoji != ARROWS_COUNTERCLOCKWISE_EMOJI and user.id != int(moBot)):
              await removeStreamer(message, message.guild.get_member(user.id), reaction)
        await message.remove_reaction(payload.emoji.name, member)


    if (message.id == 622831151320662036): # message id for pit marshall signup embed
      if (payload.emoji.name == CROWN):
        await addHost(message, payload, member, client)
      elif (payload.emoji.name == WRENCH):
        await addPitMarshall(message, payload, member, client)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  member = message.guild.get_member(payload.user_id)
  if ("MoBot" not in member.name):
    if (message.id == 620811567210037253): # message id for Reserves Embed
      if (payload.emoji.name == WAVE_EMOJI):
        await reserveNotNeeded(message, member)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveNotAvailable(message, member)
        await message.channel.send(".", delete_after=0)

    if (message.id == 622137318513442816): # message id for streamer embed
      if (payload.emoji.name in ["Twitch", "Mixer", "Youtube"]):
        await removeStreamer(message, member, payload)

    if (message.id == 622831151320662036): # message id for pit marshall signup embed
      if (payload.emoji.name == CROWN):
        await removeHost(message, member)
      elif (payload.emoji.name == WRENCH):
        await removePitMarshall(message, member)
# end mainReactionRemove

async def mainMemberUpdate(before, after, client):
  def startedStreaming(before, after):
    try:
      return before.activity.type != discord.ActivityType.streaming and after.activity.type == discord.ActivityType.streaming
    except AttributeError: # when before.activity == None
      return after.activity.type == discord.ActivityType.streaming
  # end startedStreaming

  if (startedStreaming(before, after)):
    await memberStartedStreaming(after, client)
# end mainMemberUpdate

async def addPitMarshall(message, payload, member, client):
  
  def checkCheckmarkEmoji(payload):
    return payload.user_id == member.id and message.channel.id == payload.channel_id and payload.emoji.name == CHECKMARK_EMOJI
  # end checkCheckmarkEmoji

  embed = message.embeds[0].to_dict()

  try:
    div = int(member.display_name[2])
  except ValueError: # when user is not racing, but is pit marshalling
    div = 0

  divEmojisToAdd = []
  for i in range(1, len(embed["fields"])-2+1):
    if (i != div or div == 0):
      emoji = client.get_emoji(int(divisionEmojis[str(i)]))
      divEmojisToAdd.append(emoji)

  moBotMessage = await message.channel.send(member.mention + ", which division(s) are you available to pit-marshall?\n*Click all that apply, then click the " + CHECKMARK_EMOJI + ".\nDO NOT CLICK DIVISIONS WITH THE SAME START TIME*")
  for emoji in divEmojisToAdd:
    await moBotMessage.add_reaction(emoji)
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)

  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=checkCheckmarkEmoji)
    moBotMessage = await message.channel.fetch_message(payload.message_id)

    divs = []
    for reaction in moBotMessage.reactions:
      if (str(reaction.emoji) != CHECKMARK_EMOJI):
        async for user in reaction.users():
          if (user.id == member.id):
            divs.append(int(str(reaction.emoji).split(":")[1][-1]))
            
    
    for i in range(len(embed["fields"])):
      if (i+1 in divs):
        value = ""
        if (member.display_name in embed["fields"][i]["value"]):
          continue
        for line in embed["fields"][i]["value"].split("\n"):
          if ("Pit-Marshall" in line and "[" not in line):
            value += "Pit-Marshall - " + member.display_name + "\n"

            for role in message.guild.roles:
              if (role.name == "Pit-Marshalls"):
                await member.add_roles(role)
                break
          else:
            value += line + "\n"
        embed["fields"][i]["value"] = value
    await message.edit(embed=discord.Embed.from_dict(embed))
    await moBotMessage.delete()

  except asyncio.TimeoutError:
    await message.channel.send("**TIMED OUT**", delete_after=10.0)
    await moBotMessage.delete()
    await message.remove_reaction(payload.emoji.name, member)
# end addPitMarshall

async def removePitMarshall(message, member):
  embed = message.embeds[0].to_dict()
  for i in range(len(embed["fields"])):
    value = ""
    for line in embed["fields"][i]["value"].split("\n"):
      if ("Pit-Marshall" in line and member.display_name in line):
        value += "Pit-Marshall - \n"
        for role in member.roles:
          if (role.name == "Pit-Marshalls"):
            await member.remove_roles(role)
            break
      else:
        value += line + "\n"
    embed["fields"][i]["value"] = value
  await message.edit(embed=discord.Embed.from_dict(embed))
# end removePitMarshall

async def addHost(message, payload, member, client):
  
  def checkCheckmarkEmoji(payload):
    return payload.user_id == member.id and message.channel.id == payload.channel_id and payload.emoji.name == CHECKMARK_EMOJI
  # end checkCheckmarkEmoji

  embed = message.embeds[0].to_dict()

  try:
    div = int(member.display_name[2])
  except ValueError: # when user is not racing, but is pit marshalling
    div = 0

  divHosts = {
    "0" : [1, 2, 3, 4, 5, 6],
    "1" : [2, 3, 5, 6],
    "2" : [3, 6],
    "3" : [1, 4, 7],
    "4" : [2, 3, 5, 6],
    "5" : [3, 6],
    "6" : [1, 4, 7],
    "7" : [2, 3, 5, 6]
  }
  divEmojisToAdd = []
  for i in range(1, len(embed["fields"])-2+1):
    if ((i in divHosts[str(div)] or div == 0) and i != div):
      emoji = client.get_emoji(int(divisionEmojis[str(i)]))
      divEmojisToAdd.append(emoji)

  moBotMessage = await message.channel.send(member.mention + ", which division(s) are you available to Host?\n*Click all that apply, then click the " + CHECKMARK_EMOJI + ".\nDO NOT CLICK DIVISIONS WITH THE SAME START TIME\nDO NOT CLICK MORE THAN ONE DIVISION*")
  for emoji in divEmojisToAdd:
    await moBotMessage.add_reaction(emoji)
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)

  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=checkCheckmarkEmoji)
    moBotMessage = await message.channel.fetch_message(payload.message_id)

    divs = []
    for reaction in moBotMessage.reactions:
      if (str(reaction.emoji) != CHECKMARK_EMOJI):
        async for user in reaction.users():
          if (user.id == member.id):
            divs.append(int(str(reaction.emoji).split(":")[1][-1]))
    
    for i in range(len(embed["fields"])):
      if (i+1 in divs):
        value = ""
        if (member.display_name in embed["fields"][i]["value"]):
          continue
        for line in embed["fields"][i]["value"].split("\n"):
          if ("Host" in line and "[" not in line):
            value += "Host  - " + member.display_name + "\n"

            for role in message.guild.roles:
              if (role.name == "Pit-Marshalls"):
                await member.add_roles(role)
                break
          else:
            value += line + "\n"
        embed["fields"][i]["value"] = value
    await message.edit(embed=discord.Embed.from_dict(embed))
    await moBotMessage.delete()

  except asyncio.TimeoutError:
    await message.channel.send("**TIMED OUT**", delete_after=10.0)
    await moBotMessage.delete()
    await message.remove_reaction(payload.emoji.name, member)
# end addHost

async def removeHost(message, member):
  embed = message.embeds[0].to_dict()
  for i in range(len(embed["fields"])):
    value = ""
    for line in embed["fields"][i]["value"].split("\n"):
      if ("Host" in line and member.display_name in line):
        value += "Host - \n"
        for role in member.roles:
          if (role.name == "Pit-Marshalls"):
            await member.remove_roles(role)
            break
      else:
        value += line + "\n"
    embed["fields"][i]["value"] = value
  await message.edit(embed=discord.Embed.from_dict(embed))
# end addHost

def updateMultistreams(multistreams):
  value = ""
  for j in range(len(multistreams)):
    link = "https://multistre.am/"
    if (multistreams[j] != []):
      print (multistreams[j])
      if (len(multistreams[j]) > 1):
        for name in multistreams[j]:
          link += name + "/"
      else:
        link += multistreams[j][0] + "/"
      value += "__[Division %s](%s)__ (%s)\n" % (j+1, link, len(multistreams[j]))  
  return value
# end updateMultistreams

async def addStreamer(message, member, payload, client):
  def checkMsg(msg):
    return msg.channel.id == message.channel.id and msg.author.id == payload.user_id
  # end checkMsg

  if ("twitch" in payload.emoji.name.lower()):
    try:
      moBotMessage =await message.channel.send(member.mention + ",what is your Twitch name?\n**NOT THE URL**")
      msg = await client.wait_for("message", timeout=300, check=checkMsg)
      twitchName = msg.content if ("ttv" not in msg.content and "twitch.tv" not in msg.content) else msg.content.split("/")[-1]
      await moBotMessage.delete()
      await msg.delete()

    except asyncio.TimeoutError:
      await message.channel.send(content="**TIMED OUT**", delete_after=60)
      await message.remove_reaction(payload.emoji.name, member)
      return None
  else:
    twitchName = None

  streamEmbed = message.embeds[0]
  streamEmbed = streamEmbed.to_dict()

  multistreams = [[], [] , [], [], [], [], []]

  for i in range(len(streamEmbed["fields"])):
    if (payload.emoji.name.lower() in streamEmbed["fields"][i]["name"].lower()):
      value = ""
      for line in streamEmbed["fields"][i]["value"].split("\n"):
        if (line == spaceChar):
          if (twitchName is not None):
            value += ("__[%s](https://twitch.tv/%s)__\n" % (member.display_name, twitchName))
          else:
            value += ("%s\n" % (member.display_name))
        else:
          value += line + "\n"
      value += spaceChar
      streamEmbed["fields"][i]["value"] = value
      
    if ("Twitch Streamers" in streamEmbed["fields"][i]["name"]):
      for line in streamEmbed["fields"][i]["value"].split("\n"):
        if ("twitch.tv/" in line):
          div = int(line.split("]")[0][-1])
          multistreams[div-1].append(line.split("/")[-1][:-3].strip())
    
    if ("Twitch Multistreams" in streamEmbed["fields"][i]["name"]):
      value = updateMultistreams(multistreams)
      streamEmbed["fields"][i]["value"] = value if (value != "") else spaceChar
  await message.edit(embed=discord.Embed.from_dict(streamEmbed))
# end addStreamer

async def removeStreamer(message, member, payload):
  streamEmbed = message.embeds[0]
  streamEmbed = streamEmbed.to_dict()

  multistreams = [[], [] , [], [], [], [], []]

  for i in range(len(streamEmbed["fields"])):
    if (payload.emoji.name.lower() in streamEmbed["fields"][i]["name"].lower()):
      value = ""
      for line in streamEmbed["fields"][i]["value"].split("\n"):
        if (member.display_name not in line):
          value += line + "\n"
      streamEmbed["fields"][i]["value"] = value
      
    if ("Twitch Streamers" in streamEmbed["fields"][i]["name"]):
      for line in streamEmbed["fields"][i]["value"].split("\n"):
        if ("twitch.tv/" in line):
          div = int(line.split("]")[0][-1])
          multistreams[div-1].append(line.split("/")[-1][:-3].strip())
    
    if ("Twitch Multistreams" in streamEmbed["fields"][i]["name"]):
      value = updateMultistreams(multistreams)
      streamEmbed["fields"][i]["value"] = value if (value != "") else spaceChar
  await message.edit(embed=discord.Embed.from_dict(streamEmbed))
# end removeStreamer

async def memberStartedStreaming(member, client):
  try:
    message = await member.guild.get_channel(COTM_STREAMS).fetch_message(622137318513442816)
    streamEmbed = message.embeds[0]
    streamEmbed = streamEmbed.to_dict()

    twitchStreamers = streamEmbed["fields"][0]["value"]
    #multiStreams = streamEmbed["fields"][3]["value"]
  except:
    await client.get_member(moID).send(str(traceback.format_exc()))
# end startedStreaming

async def clearReserves(message):
  embed = message.embeds[0].to_dict()
  embed["fields"][0]["value"] = spaceChar
  embed["fields"][0]["value"] = spaceChar

  for reaction in message.reactions:
    async for user in reaction.users():
      if (reaction.emoji == FIST_EMOJI):
        member = message.guild.get_member(user.id)
        roles = member.roles
        for role in roles:
          if ("Reserve" in role.name):
            await member.remove_roles(role)

  await message.clear_reactions()
  await message.add_reaction(WAVE_EMOJI)
  await message.add_reaction(FIST_EMOJI)
# end clearReserves

async def reserveNeeded(message, member):
  embed = message.embeds[0].to_dict()
  reservesNeeded = embed["fields"][0]["value"][:-1].strip()
  embed["fields"][0]["value"] = reservesNeeded + "\n" + member.display_name + "\n" + spaceChar
  await message.edit(embed=discord.Embed.from_dict(embed))

  workbook = await openSpreadsheet()
  await setReservesNeeded(embed["fields"][0]["value"], workbook)
  await updateStartOrders(message.guild, workbook)
# end reserveNeeded

async def reserveNotNeeded(message, member):
  embed = message.embeds[0].to_dict()
  reservesNeeded = embed["fields"][0]["value"][:-1].strip().split("\n")
  newReservesNeeded = ""
  for reserve in reservesNeeded:
    if (member.display_name not in reserve):
      newReservesNeeded += reserve + "\n"
  newReservesNeeded += spaceChar
  embed["fields"][0]["value"] = newReservesNeeded
  await message.edit(embed=discord.Embed.from_dict(embed))

  workbook = await openSpreadsheet()
  await setReservesNeeded(member, embed["fields"][0]["value"], workbook)
  await updateStartOrders(message.guild, workbook)
# end reserveNotNeeded

async def reserveAvailable(message, member, payload, client):
  await message.channel.trigger_typing()
  
  def checkCheckmarkEmoji(payload):
    return payload.user_id == member.id and message.channel.id == payload.channel_id and payload.emoji.name == CHECKMARK_EMOJI
  # end checkCheckmarkEmoji

  async def getReserveDiv(member):
    workbook = await openSpreadsheet()
    driversSheet = workbook.worksheet("Drivers")
    driversRange = driversSheet.range("B3:F" + str(driversSheet.row_count))
    for i in range(len(driversRange)):
      if (driversRange[i].value == str(member.id)):
        return int(driversRange[i+4].value)
    return -1
  # end getReserveDiv

  reserveDiv = await getReserveDiv(member)
  divEmojisToAdd = []
  if (reserveDiv == -1):
    await message.remove_reaction(payload.emoji.name, member)
    return -1
  else:
    if (reserveDiv == 1): # d1 driver
      divEmojisToAdd.append(client.get_emoji(int(divisionEmojis[str(reserveDiv+1)])))
    elif (reserveDiv == 0): # full time reserve
      for role in member.roles:
        if ("Reserve Division" in role.name):
          divEmojisToAdd.append(client.get_emoji(int(divisionEmojis[str(role.name.split("Division")[1].strip())])))
    else:
      for i in range(reserveDiv-1, reserveDiv+2, 2):
        emoji = client.get_emoji(int(divisionEmojis[str(i)]))
        divEmojisToAdd.append(emoji)

  moBotMessage = await message.channel.send(member.mention + ", which division(s) are you available to reserve for?\n*Click all that apply, then click the " + CHECKMARK_EMOJI + ".*")
  for emoji in divEmojisToAdd:
    await moBotMessage.add_reaction(emoji)
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)

  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=checkCheckmarkEmoji)
    moBotMessage = await message.channel.fetch_message(payload.message_id)
    embed = message.embeds[0].to_dict()
    reservesNeeded = embed["fields"][1]["value"][:-1].strip()

    reserveAdded = False
    for reaction in moBotMessage.reactions:
      if (str(reaction.emoji) != CHECKMARK_EMOJI):
        async for user in reaction.users():
          if (user.id == member.id):
            reserveAdded = True
            reservesNeeded += "\n" + str(reaction.emoji) + " - " + member.display_name
    if (reserveAdded):
      embed["fields"][1]["value"] = reservesNeeded + "\n" + spaceChar
      await message.edit(embed=discord.Embed.from_dict(embed))

      workbook = await openSpreadsheet()
      await setReservesAvailable(embed["fields"][1]["value"], workbook)
      await moBotMessage.edit(content="**Updating Reserve List**")
      await moBotMessage.clear_reactions()
      await updateStartOrders(message.guild, workbook)
    else:
      await message.remove_reaction(payload.emoji.name, member)
    await moBotMessage.delete()

  except asyncio.TimeoutError:
    await message.channel.send("**TIMED OUT**", delete_after=10.0)
    await moBotMessage.delete()
    await message.remove_reaction(payload.emoji.name, member)
# end reserveAvailable

async def reserveNotAvailable(message, member):
  embed = message.embeds[0].to_dict()
  reservesNeeded = embed["fields"][1]["value"][:-1].strip().split("\n")
  newReservesNeeded = ""
  for reserve in reservesNeeded:
    if (member.display_name not in reserve):
      newReservesNeeded += reserve + "\n"
  newReservesNeeded += spaceChar
  embed["fields"][1]["value"] = newReservesNeeded
  await message.edit(embed=discord.Embed.from_dict(embed))
  
  for role in member.roles:
    if ("Reserve Division" in role.name and "[R]" not in member.display_name):
      await member.remove_roles(role)
      await message.guild.get_channel(DIVISION_UPDATES).send(member.mention + " has been removed from " + role.name)

  workbook = await openSpreadsheet()
  await setReservesAvailable(embed["fields"][1]["value"], workbook)
  await updateStartOrders(message.guild, workbook)
# end reserveNotAvailable

async def resetVotes(message):
  await message.clear_reactions()
  await message.channel.purge(after=message)
  await message.add_reaction(CHECKMARK_EMOJI)
  await message.add_reaction(ARROWS_COUNTERCLOCKWISE_EMOJI)
# end resetVotes

async def votingProcess(message, member, client):
  await message.clear_reactions()
  await message.add_reaction(ARROWS_COUNTERCLOCKWISE_EMOJI)
  numberEmojis = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
  undoEmoji = "↩"

  votingChannel = message.channel

  # get vote options
  voteOptionsMsg = await getCurrentVotersVoteOptionsMsg(message)
  voteOptionsEmbed = voteOptionsMsg.embeds[0].to_dict()
  voteOptions = voteOptionsEmbed["fields"][1]["value"].split("\n")
  del voteOptions[-1]

  voteOptionsDict = {}
  for i in range(len(voteOptions)):
    voteOptions[i] = voteOptions[i].split("]")[0].split("[")[1]
    voteOptionsDict[voteOptions[i]] = 0

  def checkSpent(payload):
    return (payload.emoji.name in numberEmojis or payload.emoji.name == undoEmoji) and payload.channel_id == votingChannel.id and payload.user_id == member.id

  reply = ""
  reply += "**Voting Options:**"
  for option in voteOptions:
    reply += "\n  - " + option + ": 0"
  reply += "\n\nVotes Remaining: " + str(len(voteOptions))

  voteOptionsMsg = await votingChannel.send(reply)

  async def getVoteSpent(payload):
    for i in range(len(numberEmojis)):
      if (payload.emoji.name == numberEmojis[i]):
        return i
  # end getVoteSpent

  async def updateVoteOptions(option, votesRemaining):
    reply = "**Vote Options:**"
    for option in voteOptions:
      reply += "\n - " + option + ": " + str(voteOptionsDict[option])
    reply += "\n\nVotes Remaining: " + str(votesRemaining)
    await voteOptionsMsg.edit(content=reply)
  # end updateVoteOptions
  
  votesRemaining = len(voteOptions)
  i = 0
  moBotMessage = await votingChannel.send("**Loading options...**")
  await asyncio.sleep(3)
  while (i < len(voteOptions) and votesRemaining > 0):
    option = voteOptions[i]
    await moBotMessage.edit(content="**How many votes would you like to spend on `" + option + "`?**")
    
    for j in range(votesRemaining + 1):
      await moBotMessage.add_reaction(numberEmojis[j])

    try:
      payload = await client.wait_for("raw_reaction_add", timeout=120.0, check=checkSpent)
      await moBotMessage.clear_reactions()
      if (payload.emoji.name in numberEmojis):
        votesSpent = await getVoteSpent(payload)
        votesRemaining -= votesSpent
        voteOptionsDict[option] += votesSpent
        await updateVoteOptions(option, votesRemaining)
        i += 1
    except asyncio.TimeoutError:
      await moBotMessage.clear_reactions()
      await message.channel.send("**TIMED OUT**\n\n**Click the 🔄 at the top to restart the voting process.**")
      return

    if (votesRemaining > 0 and i == len(voteOptions)):
      await moBotMessage.edit(content="**Please use all of your votes.**")
      await asyncio.sleep(2)
      i = 0

  moBotMessage = await message.channel.send("**All votes have been used, would you like to submit?**\nIf not, click the 🔄 at the top to restart the voting process.")
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)
  def check(payload):
    return payload.message_id == moBotMessage.id and payload.user_id == member.id
  try:
    payload = await client.wait_for("raw_reaction_add", timeout=120.0, check=check)
    await moBotMessage.clear_reactions()
  except asyncio.TimeoutError:
    await moBotMessage.clear_reactions()
    await message.channel.send("**TIMED OUT**\n\n**Click the 🔄 at the top to restart the voting process.**")
    return

  await message.channel.send("**Submitting Your Votes**")
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet()
  votingSheet = workbook.worksheet("Voting")
  voterRange = votingSheet.range("D3:H" + str(votingSheet.row_count))
  totalVoters = 0
  log = {member.display_name : [], "Total Votes" : []}
  for i in range(0, len(voterRange), 5):
    totalVoters += 1
    if (voterRange[i].value == ""):
      voterRange[i].value = str(member.id)
      for j in range(0, len(voteOptions)):
        voterRange[j+i+1].value = str(voteOptionsDict[voteOptions[j]])
        log[member.display_name].append([voteOptions[j], voterRange[j+i+1].value])
      break
  votingSheet.update_cells(voterRange, value_input_option="USER_ENTERED")
  log["Total Votes"] = votingSheet.range("E2:H2")

  await message.channel.send("**Thank you for voting.**")
  await asyncio.sleep(3)
  await closeVotingChannel(message, member, totalVoters, log)
# end votingProcess

async def closeVotingChannel(message, member, totalVoters, log):
  await message.channel.delete()
  totalVotersEmojiNumbers = RandomFunctions.numberToEmojiNumbers(totalVoters)
  currentVotersMsg = await getCurrentVotersVoteOptionsMsg(message)
  currentVotersEmbed = currentVotersMsg.embeds[0].to_dict()
  currentVoters = (currentVotersEmbed["fields"][2]["value"] + "\n").split("\n")
  value = ""
  for voter in currentVoters:
    if (str(member.id) not in voter and "@" in voter):
      value += "\n" + voter
  if (value.split(spaceChar)[0].strip() == ""):
    value = "None" 
  value += "\n" + spaceChar
  currentVotersEmbed["fields"][2]["value"] = value
  currentVotersEmbed["fields"][3]["value"] = totalVotersEmojiNumbers
  await currentVotersMsg.edit(embed=discord.Embed.from_dict(currentVotersEmbed))

  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
  embed.add_field(name=member.display_name + ":", value="", inline=False)
  embed.add_field(name="Total Votes:", value="", inline=False)
  embed.add_field(name="Total Voters:", value=totalVotersEmojiNumbers)
  embed = embed.to_dict()
  for i in range(len(log["Total Votes"])):
    embed["fields"][0]["value"] += "\n" + spaceChar + log[member.display_name][i][0] + " - " + log[member.display_name][i][1]
    embed["fields"][1]["value"] += "\n" + spaceChar + log[member.display_name][i][0] + " - " + log["Total Votes"][i].value
  embed["fields"][0]["value"] += "\n" + spaceChar
  embed["fields"][1]["value"] += "\n" + spaceChar
  await message.guild.get_channel(530284914071961619).send(embed=discord.Embed.from_dict(embed))
# end closeVotingChannel

async def getCurrentVotersVoteOptionsMsg(message):
  channel = message.guild.get_channel(608472349712580608)
  currentVotersMsg = await channel.fetch_message(620778154197385256)
  return currentVotersMsg
# end getCurrentVotersVoteOptionsMsg

async def openVotingChannel(message, member):
  await message.channel.trigger_typing()
  async def getVotingCategory(message):
    categories = message.guild.by_category()
  
    for category in categories:
      try:
        if ("voting" in category[0].name.lower()):
          return category[0]
      except AttributeError:
        pass
  # end getVotingCategory

  # get current voters
  currentVotersMsg = await getCurrentVotersVoteOptionsMsg(message)
  currentVotersEmbed = currentVotersMsg.embeds[0].to_dict()
  currentVoters = currentVotersEmbed["fields"][2]["value"]

  # get past voters
  workbook = await openSpreadsheet()
  votingSheet = workbook.worksheet("Voting")
  pastVotersRange = votingSheet.range("D3:D" + str(votingSheet.row_count))
  isPastVoter = findDriver(pastVotersRange, str(member.id)) >= 0

  # create voting channel
  if (str(member.id) not in currentVoters and not isPastVoter):
    votingChannel = await message.guild.create_text_channel(name="voting " + member.display_name)

    # udpate current voters
    currentVotersEmbed["fields"][2]["value"] = "" if ("None" in currentVoters) else currentVoters.split(spaceChar)[0].strip() 
    currentVotersEmbed["fields"][2]["value"] += "\n" + member.display_name + " - <#" + str(votingChannel.id) + ">"
    currentVotersEmbed["fields"][2]["value"] += "\n" + spaceChar
    await currentVotersMsg.edit(embed=discord.Embed.from_dict(currentVotersEmbed))

    # set permissions
    await votingChannel.edit(category=await getVotingCategory(message), sync_permissions=True)
    await votingChannel.set_permissions(member, read_messages=True, send_messages=False, add_reactions=False)
    for role in message.guild.roles:
      if (role.name == "@everyone"):
        await votingChannel.set_permissions(role, read_messages=False)
        break

    # get vote options
    voteOptionsMsg = await getCurrentVotersVoteOptionsMsg(message)
    voteOptionsEmbed = voteOptionsMsg.embeds[0].to_dict()
    voteOptions = voteOptionsEmbed["fields"][1]["value"].split("\n")
    del voteOptions[-1]

    await votingChannel.send("This season there's been a change to how the voting works. As you can see there are " + str(len(voteOptions)) + " options to vote from. You have " + str(len(voteOptions)) + " votes to 'spend'. You can use them all on one option, or spread them out.")

    moBotMessage = await votingChannel.send("**" + member.mention + ", are you ready to vote?**")
    await moBotMessage.add_reaction(CHECKMARK_EMOJI)

  else:
    msg = await message.channel.send("**Cannot open a voting channel.**\n**" + member.mention + ", you either already have a voting channel open, or you have already voted.**")
    await asyncio.sleep(10)
    await msg.delete()
# end openVotingChannel

async def waitForQualiTime(message, member, payload, qualifyingChannel, client):
  def check(msg):
    return msg.author.id == member.id and message.channel.id == msg.channel.id

  reactions = message.reactions
  for reaction in reactions:
    if (reaction.emoji == payload.emoji.name):
      if (reaction.count == 1):
        moBotMessage = await message.channel.send(member.mention + ", please type the time from the screenshot that you added the reaction to.")
        msg = await client.wait_for("message", timeout=60.0, check=check)
        await submitQualiTime(message, qualifyingChannel, msg.content, payload, client)
        await moBotMessage.delete()
      break
# end waitForQualiTime

async def getMissingQualifiers(driversRange, guild):
  members = guild.members
  driverIDs = []
  missingDrivers = []
  for i in range(len(driversRange)):
    if (driversRange[i].value != ""):
      try:
        driverIDs.append(int(driversRange[i].value))
      except ValueError:
        pass
    else:
      break
  for member in members:
    isCOTM = False
    for role in member.roles:
      if (role.name == "COTM"):
        isCOTM = True
    if (isCOTM):
      if (member.id not in driverIDs):
        missingDrivers.append(member)
  return missingDrivers
# end getMissingQualifiers

async def submitQualiTime(message, qualifyingChannel, lapTime, reactionPayload, client):  
  await message.channel.trigger_typing()
  
  if (lapTime is None):
    try:
      userID = int(message.content.split("@")[-1].strip().split(">")[0])
    except ValueError:
      userID = int(message.content.split("@")[-1].strip().split(">")[0][1:])
    if (userID == moBot):
      await message.channel.send("**Driver Not Found**\nEdit your message to follow this command: `@MoBot#0697 quali @User x.xx.xxx`")
      return

    user = message.guild.get_member(userID)
    lapTime = message.content.split(str(user.id))[1].strip().split(" ")[1].strip().replace(":", ".")
  else:
    user = message.author
    lapTime = lapTime.replace(":", ".")
    await message.channel.send(user.mention + ", your lap has been submitted.")

  workbook = await openSpreadsheet()
  driversRange, driversSheet = getDriversRange(workbook)
  qualifyingSheet = workbook.worksheet("Qualifying")
  qualifyingRange = qualifyingSheet.range("G3:I" + str(qualifyingSheet.row_count))

  driverIndex = findDriver(driversRange, str(user.id))
  moBotMessage = None
  if (driverIndex == -1):
    def checkMsg(msg):
      if (msg.channel.id == message.channel.id):
        if (reactionPayload is None):
          return msg.author.id == message.author.id
        else:
          return msg.author.id == reactionPayload.user_id
      else:
        return False
    def checkMsgEdit(payload):
      if (payload.channel_id == message.channel.id):
        if (reactionPayload is None):
          return msg.author.id == message.author.id
        else:
          return payload.user_id == reactionPayload.user_id
      else:
        return False
    def checkEmoji(payload):
      if (payload.channel_id == message.channel.id and (payload.emoji.name == CHECKMARK_EMOJI or payload.emoji.name == "❌")):
        if (reactionPayload is None):
          return payload.user_id == message.author.id
        else:
          return payload.user_id == reactionPayload.user_id
      else:
        return False

    moBotMessage = await message.channel.send("This user has not had a time inputted yet. What is their gamertag in the screenshot?")
    looped = False
    while True:
      try:
        if (not looped):
          msg = await client.wait_for("message", timeout=30.0, check=checkMsg)
        else:
          payload = await client.wait_for("raw_message_edit", timeout=30.0, check=checkMsgEdit)
          msg = await message.channel.fetch_message(payload.message_id)
        await moBotMessage.delete()
      except asyncio.TimeoutError:
        msg = await message.channel.send("**TIMED OUT**")
        await asyncio.sleep(3)
        await moBotMessage.delete()
        await msg.delete()
        return

      userGT = msg.content.strip()
      reply = "Is this gamertag correct?\n`" + userGT + "`"
      if (not looped):
        moBotMessage = await message.channel.send(reply)
      else:
        await moBotMessage.edit(content=reply)
      await moBotMessage.add_reaction(CHECKMARK_EMOJI)
      await moBotMessage.add_reaction("❌")

      try:
        payload = await client.wait_for("raw_reaction_add", timeout=30.0, check=checkEmoji)
      except asyncio.TimeoutError:
        msg = await message.channel.send("**TIMED OUT**")
        await asyncio.sleep(3)
        await moBotMessage.delete()
        await msg.delete()
        return

      if (payload.emoji.name == CHECKMARK_EMOJI):
        await moBotMessage.delete()
        break
      else:
        looped = True
        await moBotMessage.edit(content="Edit your message above with the correct gamertag.")
        await moBotMessage.clear_reactions()
    
    for i in range(len(driversRange)):
      if (driversRange[i].value == ""):
        driversRange[i].value = str(user.id)
        driversRange[i+1].value = userGT
        break

    driversSheet.update_cells(driversRange, value_input_option="USER_ENTERED")
    await user.edit(nick=userGT)

  else:
    userGT = driversRange[driverIndex+1].value

  moBotMessage = await message.channel.send("**Submitting Lap Time**")
  driverIndex = findDriver(qualifyingRange, userGT)
  if (driverIndex == -1):
    for i in range(len(qualifyingRange)):
      if (qualifyingRange[i].value == ""):
        driverIndex = i
        break
  lapTime = int(lapTime[0]) * 60 + float(lapTime[2:])
  qualifyingRange[driverIndex].value = userGT
  qualifyingRange[driverIndex+1].value = datetime.utcnow().strftime("%m/%d/%Y %H:%M")
  qualifyingRange[driverIndex+2].value = lapTime

  qualiTable = []
  for i in range(0, len(qualifyingRange), 3):
    if (qualifyingRange[i].value != ""):
      qualiTable.append([qualifyingRange[i].value, datetime.strptime(qualifyingRange[i+1].value, "%m/%d/%Y %H:%M"), float(qualifyingRange[i+2].value)])
    else:
      break
  
  qualiTable = sorted(qualiTable, key=operator.itemgetter(2, 1)) # sorts in ascending order both times

  qualiScreenShotReactionMsg = await qualifyingChannel.fetch_message(614836845267910685)
  history = await qualifyingChannel.history(after=qualiScreenShotReactionMsg).flatten()
  for hMsg in history:
    try:
      embedURL = hMsg.embeds[0].author.url
      try:
        if ("COTMQualifying" in embedURL):
          topMsg = await qualifyingChannel.fetch_message(int(embedURL.split("top=")[1].split("/")[0]))
          bottomMsg = await qualifyingChannel.fetch_message(int(embedURL.split("bottom=")[1].split("/")[0]))
          await qualifyingChannel.purge(after=topMsg, before=bottomMsg)
          await topMsg.delete()
          await bottomMsg.delete()
      except TypeError:
        pass
    except IndexError:
      pass
  
  qualiStandingEmbeds = []
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5\nQualifying Standings", icon_url=logos["cotmFaded"], url="https://www.google.com/COTMQualifying")
  embed = embed.to_dict()
  qualiStandingEmbeds.append(embed)

  def floatTimeToStringTime(t):
    m = str(int(t/60))
    s = str(round(t - int(t/60)*60, 3))
    ili = s.split(".")[1].ljust(3, "0")
    s = s.split(".")[0].rjust(2, "0")
    return m + ":" + s + "." + ili
  
  def stringTimetoFloatTime(t):
    seconds = int(t.split(":")[0]) * 60 + int(t.split(":")[1])
    return seconds

  def lapTimeDifferenceToString(t):
    t = round(t, 3)
    return "-" + str(t).split(".")[0] + "." + str(t).split(".")[1].ljust(3, "0")

  fastestOverall = []
  fastestInDiv = []
  driverAhead = []
  userEntry = [] # [name, date, laptime, id]
  position = 0
  for i in range(len(qualiTable)):
    division = int(i / 15) + 1
    name = qualiTable[i][0]
    lTime = qualiTable[i][2]
    driverIndex = findDriver(driversRange, name)
    userID = driversRange[driverIndex - 1].value

    if (i == 0):
      fastestOverall = qualiTable[i]
    if (qualiTable[i][0] == userGT):
      qualiTable[i].append(userID)
      userEntry = qualiTable[i]
      position = i + 1
      driverDiv = division
      fastestInDiv = qualiTable[(division - 1) * 15]
      if (i != 0):
        driverAhead = qualiTable[i-1]
      else:
        driverAhead = fastestOverall

    qualifyingRange[i*3+0].value = name 
    qualifyingRange[i*3+1].value = qualiTable[i][1].strftime("%m/%d/%Y %H:%M")
    qualifyingRange[i*3+2].value = lTime

    if (i % 15 == 0):
      embed = discord.Embed(color=int("0xd1d1d1", 16))
      embed.add_field(name="Division " + str(division), value="", inline=False)
      embed = embed.to_dict()
      qualiStandingEmbeds.append(embed)

    qualiStandingEmbeds[len(qualiStandingEmbeds)-1]["fields"][0]["value"] += "\n" + str(i+1) + ". " + name + " - " + floatTimeToStringTime(lTime)
    
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  missingDrivers = await getMissingQualifiers(driversRange, message.guild)
  for i in range(len(missingDrivers)):
    missingDrivers[i] = missingDrivers[i].display_name
  missingDrivers.sort(key=lambda x: x[0])
  value = ""
  for member in missingDrivers:
    value += "\n" + member
  embed.add_field(name="Missing Qualifiers", value=value, inline=False)
  embed.set_footer(text="Missing Qualifiers: " + str(len(missingDrivers)))
  embed = embed.to_dict()
  qualiStandingEmbeds.append(embed)

  qualifyingSheet.update_cells(qualifyingRange, value_input_option="USER_ENTERED")
  
  await moBotMessage.edit(content="**Updating Driver Roles**")
  divList = await updateDriverRoles(message, workbook)

  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
  value = ""
  value += "**Driver:** <@" + str(userEntry[3]) + ">"
  value += "\n**Time:** " + floatTimeToStringTime(lapTime)
  value += "\n**Division:** " + str(int((position - 1) / 15) + 1)
  value += "\n**Position:** " + str(position)
  value += "\n\n**Fastest Overall:**\n" + spaceChar + floatTimeToStringTime(fastestOverall[2]) + " (" + lapTimeDifferenceToString(lapTime - fastestOverall[2]) + ") by <@" + driversRange[findDriver(driversRange, fastestOverall[0])-1].value + ">"
  value += "\n**Fastest In Division:**\n" + spaceChar + floatTimeToStringTime(fastestInDiv[2]) + " (" + lapTimeDifferenceToString(lapTime - fastestInDiv[2]) + ") by <@" + driversRange[findDriver(driversRange, fastestInDiv[0])-1].value + ">"
  value += "\n**Driver Ahead:**\n" + spaceChar + floatTimeToStringTime(driverAhead[2]) + " (" + lapTimeDifferenceToString(lapTime - driverAhead[2]) + ") by <@" + driversRange[findDriver(driversRange, driverAhead[0])-1].value + ">"
  embed.add_field(name="__New Qualifying Time__", value=value, inline=False)
  await moBotMessage.delete()
  await message.channel.send(embed=embed)
  moBotMessage = await message.channel.send("**Updating Qualifying Standings**")

  topMsgID = None
  for embed in qualiStandingEmbeds:
    embed = discord.Embed.from_dict(embed)
    msg = await qualifyingChannel.send(embed=embed)
    topMsgID = msg.id if (topMsgID is None) else topMsgID
  bottomMsgID = msg.id
  topMsg = await qualifyingChannel.fetch_message(topMsgID)
  topMsgEmbed = topMsg.embeds[0].to_dict()
  topMsgEmbed["author"]["url"] += "/top=" + str(topMsgID)
  topMsgEmbed["author"]["url"] += "/bottom=" + str(bottomMsgID)
  await topMsg.edit(embed=discord.Embed.from_dict(topMsgEmbed))
  await moBotMessage.edit(content="**Updating Division List**")
  await updateDivList(message, divList)
  await moBotMessage.edit(content="**Updating Start Orders**")
  await updateStartOrders(message.guild, workbook)
  await moBotMessage.edit(content="**Updating Standings**")
  await updateStandings(message.guild, workbook)
  await moBotMessage.delete()
# end submitQualiTime

async def addUserToQualiScreenshots(message, member, qualiScreenshotsChannel, client):
  await qualiScreenshotsChannel.set_permissions(member, read_messages=True, send_messages=True)
  moBotMessage = await qualiScreenshotsChannel.send(member.mention + ", you have 60 seconds to submit your screenshot.")

  def check(msg):
    return msg.author.id == member.id and msg.channel.id == qualiScreenshotsChannel.id
  
  try:
    msg = await client.wait_for("message", timeout=60.0, check=check)
    await moBotMessage.delete()
    if (len(msg.attachments) > 0 or "http" in msg.content):
      moBotMessage = await msg.channel.send(member.mention + ", if there is more than one driver in the screenshot, please type which drivers need inputting, otherwise, thank you for submitting.")
      try:
        msg = await client.wait_for("message", timeout=120.0, check=check)
      except asyncio.TimeoutError:
        pass
      await qualiScreenshotsChannel.set_permissions(member, read_messages=True, send_messages=False)
      await moBotMessage.delete()
      return
    else:
      await qualiScreenshotsChannel.send("**Please only send an attachment of your screenshot or a link to it.**\nIf this was an error, contact Mo#9991.", delete_after=10.0)
      await msg.delete()
  except asyncio.TimeoutError:
    await moBotMessage.delete()
    await message.channel.send(member.mention + ", you took too long. If you still need to submit a screenshot, click the ✅ at the top of the channel.", delete_after=120.0)
  
  await qualiScreenshotsChannel.set_permissions(member, overwrite=None)
# end addUserToQualiScreenshots

async def updateDivList(message, divList):
  divListChannel = message.guild.get_channel(527226061100941312)

  divListEmbeds = {
    "sortedByGamertag" : [],
    "sortedByDivision" : [],
  }

  for key in divListEmbeds:
    embed = discord.Embed(color=int("0xd1d1d1", 16))
    if (key == "sortedByGamertag"):
      divList.sort(key=lambda x:x[2])
      embed.set_author(name="Children of the Mountain - Season 5\nSorted By Gamertag", icon_url=logos["cotmFaded"], url="https://www.google.com/DivisionList")
      embed = embed.to_dict()
      divListEmbeds["sortedByGamertag"].append(embed)

    else:
      divList.sort(key=lambda x:x[0])
      embed.set_author(name="Children of the Mountain - Season 5\nSorted By Division", icon_url=logos["cotmFaded"], url="https://www.google.com/DivisionList")
      embed = embed.to_dict()
      divListEmbeds["sortedByDivision"].append(embed)

    nameRange = [None, None]
    oldDiv = 0
    for i in range(len(divList)):
      nameRange[1] = divList[i][1]

      if (key == "sortedByDivision"):
        div = int(divList[i][1].display_name[2])
        if (div != oldDiv):
          oldDiv = div
          embed = discord.Embed(color=int("0xd1d1d1", 16))
          embed.add_field(name="Division " + str(div), value="", inline=False)
          embed = embed.to_dict()
          divListEmbeds[key].append(embed)

      elif (key == "sortedByGamertag"):
        if (i % 15 == 0):
          nameRange[0] = divList[i][1]
          embed = discord.Embed(color=int("0xd1d1d1", 16))
          embed.add_field(name="", value="", inline=False)
          embed = embed.to_dict()
          divListEmbeds[key].append(embed)


      if (key == "sortedByGamertag"):
        divListEmbeds[key][len(divListEmbeds[key])-1]["fields"][0]["name"] = nameRange[0].display_name + " - " + nameRange[1].display_name
      divListEmbeds[key][len(divListEmbeds[key])-1]["fields"][0]["value"] += divList[i][1].display_name + "\n"
  
  await divListChannel.purge()
  for embed in divListEmbeds["sortedByGamertag"]:
    await divListChannel.send(embed=discord.Embed.from_dict(embed))
  for embed in divListEmbeds["sortedByDivision"]:
    await divListChannel.send(embed=discord.Embed.from_dict(embed))
# end updateDivList

async def updateDriverRoles(message, workbook):
  await message.channel.trigger_typing()
  divUpdateChannel = message.guild.get_channel(DIVISION_UPDATES)
  driversSheet = workbook.worksheet("Drivers")
  driversRange = driversSheet.range("B3:D" + str(driversSheet.row_count))

  divRoles = []
  for role in message.guild.roles:
    if ("division" in role.name.lower() and "reserve" not in role.name.lower()):
      divRoles.append([int(role.name[-1]), role])
  divRoles.sort(key=lambda x:x[0])

  divList = []
  for member in message.guild.members:
    driverIndex = findDriver(driversRange, member.id)
    if (driverIndex >= 0):
      try:
        div = str(int(driversRange[driverIndex+2].value))
        gamertag = driversRange[driverIndex+1].value
        role = divRoles[int(div)-1][1]

        newNick = "[D" + div + "] " + gamertag
        divList.append([int(div), member, gamertag.lower()])
        if (newNick != member.display_name):
          await member.edit(nick=newNick)

        hasRole = False
        for mRole in member.roles:
          if (mRole.name == role.name):
            hasRole = True
          elif ("division" in mRole.name.lower() and "reserve" not in mRole.name.lower()):
            await member.remove_roles(mRole)
            await divUpdateChannel.send("" + member.mention + " has been removed from " + mRole.name + ".")

        if (not hasRole):
          await member.add_roles(role)
          await divUpdateChannel.send("" + member.mention + " has been added to " + role.name + ".")  
      except ValueError:
        pass
  return divList
# end updateDriverRoles

async def updateStartOrders(guild, workbook):
  startOrdersChannel = guild.get_channel(START_ORDERS)

  startOrders = getStartOrders(workbook)
  startOrderEmbeds = []
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
  embed.add_field(name="Start Orders", value="Pos. Driver - Reserve - Points - Last Week's Division", inline=False)
  embed = embed.to_dict()
  startOrderEmbeds.append(embed)

  for division in startOrders:
    embed = discord.Embed(color=int("0xd1d1d1", 16))
    embed.add_field(name="Division " + str(division), value="", inline=False)
    embed = embed.to_dict()
    for i in range(len(startOrders[division])):
      driver = startOrders[division][i]
      driverMember = guild.get_member(driver.driverID)
      if (driver.reserveID != None):
        driverName = "~~" + driverMember.display_name + "~~"
        reserveMember = guild.get_member(driver.reserveID)
        for role in guild.roles:
          if (role.name == "Reserve Division " + str(division)):
            hasRole = False
            for role2 in reserveMember.roles:
              if (role2 == role):
                hasRole = True
                break
            if (not hasRole):
              await reserveMember.add_roles(role)
              await guild.get_channel(DIVISION_UPDATES).send(reserveMember.mention + " is now reserving for " + driverMember.mention + ".")
            break
        embed["fields"][0]["value"] += ("%d. %s - %s - %d - D%s\n" % (i+1, driverName, reserveMember.display_name, driver.totalPoints, driver.lastWeeksDiv))
      else:
        driverName = driverMember.display_name
        embed["fields"][0]["value"] += ("%d. %s - %d - D%s\n" % (i+1, driverName, driver.totalPoints, driver.lastWeeksDiv))
    startOrderEmbeds.append(embed)

  await startOrdersChannel.purge()
  for embed in startOrderEmbeds:
    try:
      await startOrdersChannel.send(embed=discord.Embed.from_dict(embed))
    except discord.errors.HTTPException: # when a division has no drivers
      pass
# end updateStartOrders

async def updateStandings(guild, workbook):
  standingsChannel = guild.get_channel(STANDINGS)

  standings = getStandings(workbook)
  standingsEmbeds = []
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
  embed.add_field(name="Standings", value="Pos. Driver - Points", inline=False)
  embed = embed.to_dict()
  standingsEmbeds.append(embed)

  for i in range(len(standings)):
    if (i % 15 == 0):
      embed = discord.Embed(color=int("0xd1d1d1", 16))
      embed.add_field(name=("Pos. %d - %d" % (i+1, i+15)), value="", inline=False)
      embed = embed.to_dict()
      standingsEmbeds.append(embed)

    driverMember = guild.get_member(standings[i].driverID)
    standingsEmbeds[len(standingsEmbeds)-1]["fields"][0]["value"] += ("%d. %s - %d" % (standings[i].position, driverMember.display_name, standings[i].points)) + "\n"

  await standingsChannel.purge()
  for embed in standingsEmbeds:
    await standingsChannel.send(embed=discord.Embed.from_dict(embed))
# end updateStandings

def getStandings(workbook):
  class Driver:
    def __init__(self, position, driverID, points):
      self.position = position
      self.driverID = driverID
      self.points= points
  # end Driver

  standingsSheet = workbook.worksheet("Standings")
  standingsRange = standingsSheet.range("B3:E" + str(standingsSheet.row_count))
  driversRange, driverSheet = getDriversRange(workbook)

  standings = []
  for i in range(0, len(standingsRange), 4):
    if (standingsRange[i].value == ""):
      break  
    position = int(standingsRange[i].value)
    driverID = int(driversRange[findDriver(driversRange, standingsRange[i+2].value)-1].value)
    points = int(standingsRange[i+3].value.split(".")[0])
    standings.append(Driver(position, driverID, points))
  return standings
# end getStandings

def getReserves(workbook):
  class Reserve:
    def __init__(self, division, driverID, reserveID):
      self.division = division
      self.driverID = driverID
      self.reserveID = reserveID
  # end Reserve

  reservesSheet = workbook.worksheet("Reserves")
  reservesNeeded = reservesSheet.range("B4:C" + str(reservesSheet.row_count))
  reservesAvailable = reservesSheet.range("D4:E" + str(reservesSheet.row_count))
  driversRange, driverSheet = getDriversRange(workbook)
  reserves = {}
  reservesAdded = {
    "1" : [],
    "2" : [],
    "3" : [],
    "4" : [],
    "5" : [],
    "6" : [],
    "7" : []
  }
  for i in range(0, len(reservesNeeded), 2):
    if (reservesNeeded[i].value != ""):
      driverID = int(driversRange[findDriver(driversRange, reservesNeeded[i+1].value)-1].value)
      division = int(reservesNeeded[i].value)
      for j in range(0, len(reservesAvailable), 2):
        if (reservesAvailable[j].value == ""):
          break
        elif (int(reservesAvailable[j].value) == division):
          reserveID = int(driversRange[findDriver(driversRange, reservesAvailable[j+1].value)-1].value)
          if (reserveID not in reservesAdded[str(division)]):
            reservesAdded[str(division)].append(reserveID)
            reserves[driverID] = Reserve(division, driverID, reserveID)
            break
  return reserves    
# end getReserve

async def setReservesNeeded(member, reservesNeededValue, workbook):
  reservesSheet = workbook.worksheet("Reserves")
  reservesNeededRange = reservesSheet.range("B4:C" + str(reservesSheet.row_count))
  reserves = getReserves(workbook)
  reservesNeeded = []
  for line in reservesNeededValue.split("\n"):
    if (spaceChar in line):
      break
    reservesNeeded.append(line.split("]")[0][-1])
    reservesNeeded.append(line.split("]")[1].strip())

  for i in range(len(reservesNeededRange)):
    try:
      reservesNeededRange[i].value = reservesNeeded[i]
    except IndexError: # when reserve is not needed
      reservesNeededRange[i].value = ""
      reservesNeededRange[i+1].value = ""
      if (member.id in reserves):
        reserveMember = member.guild.get_member(reserves[member.id].reserveID)
        driverMember = member.guild.get_member(reserves[member.id].driverID)
        await member.guild.get_channel(DIVISION_UPDATES).send(reserveMember.mention + " is no longer reserving for " + driverMember.mention + ".")
        for role in reserveMember.roles:
          if (role.name == "Reserve Division " + str(reserves[member.id].division) and "[R]" not in reserveMember.display_name):
            await reserveMember.remove_roles(role)
            break
      break
  reservesSheet.update_cells(reservesNeededRange, value_input_option="USER_ENTERED")
# end setReservesNeeded

async def setReservesAvailable(reservesAvailableValue, workbook):
  reservesSheet = workbook.worksheet("Reserves")
  reservesAvailableRange = reservesSheet.range("D4:E" + str(reservesSheet.row_count))
  reservesAvailable = []
  for line in reservesAvailableValue.split("\n"):
    if (spaceChar in line):
      break
    reservesAvailable.append(line.split(":")[1][-1])
    reservesAvailable.append(line.split("]")[1].strip())

  for i in range(len(reservesAvailableRange)):
    try:
      reservesAvailableRange[i].value = reservesAvailable[i]
    except IndexError: # when reserve is not available
      reservesAvailableRange[i].value = ""
  reservesSheet.update_cells(reservesAvailableRange, value_input_option="USER_ENTERED")
# end setReservesAvailable

def getStartOrders(workbook):
  class Driver:
    def __init__(self, driverID, totalPoints, lastWeeksDiv, reserveID):
      self.driverID = driverID
      self.totalPoints = totalPoints
      self.lastWeeksDiv = lastWeeksDiv
      self.reserveID = reserveID
  # end Driver

  reserves = getReserves(workbook)

  divisionRostersSheet = workbook.worksheet("Division Rosters")
  driversRange, driversSheet = getDriversRange(workbook)

  weekNumber = int(divisionRostersSheet.range("B1:B1")[0].value)
  divisionRostersRanges = {}
  startOrders = {}
  for i in range(0, 7):
    division = str(i+1)
    topRow = ((int(division) - 1) * 31) + 5
    bottomRow = topRow + 28
    divisionRostersRanges[division] = divisionRostersSheet.range("B%1d:F%1d" % (topRow, bottomRow))
  
  for division in divisionRostersRanges:
    startOrder = []
    for i in range(0, len(divisionRostersRanges[division]), 5):
      divisionRoster = divisionRostersRanges[division]
      if (divisionRoster[i].value != ""):
        driverID = int(driversRange[findDriver(driversRange, divisionRoster[i+2].value)-1].value)
        totalPoints = int(divisionRoster[i+3].value.split(".")[0])
        lastWeeksDiv = divisionRoster[i+1].value
        if (driverID in reserves):
          reserveID = reserves[driverID].reserveID
        else:
          reserveID = None
        startOrder.append(Driver(driverID, totalPoints, lastWeeksDiv, reserveID))
      else:
        break
    startOrders[division] = startOrder
  return startOrders
# end getStartOrders

def getDriversRange(workbook):
  driversSheet = workbook.worksheet("Drivers")
  driversRange = driversSheet.range("B3:C" + str(driversSheet.row_count))
  return driversRange, driversSheet
# end getDriversRange

def findDriver(table, driver):
  driverFound = -1
  for i in range(len(table)):
    if (table[i].value == str(driver)):
      driverFound = i
      break
  return driverFound
# end findDriver
  
async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  season5Key = "14L5u8GmPh4udQk85KCOlCTSen78mB8SxgPecdGMUk1E"
  workbook = clientSS.open_by_key(season5Key)
  return workbook
# end openSpreadsheet