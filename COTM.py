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

moTag = "<@405944496665133058>"
mardoniusTag = "<@445996484240998400>"
moBot = "449247895858970624"

CHECKMARK_EMOJI = "✅"
ARROWS_COUNTERCLOCKWISE_EMOJI  = "🔄"
THUMBSUP_EMOJI = "👍"
WAVE_EMOJI = "👋"
FIST_EMOJI = "✊"
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
    
  qualifyingChannel = message.guild.get_channel(607693838642970819)
  qualiScreenshotsChannel = message.guild.get_channel(607694176133447680)

  if (args[0][-19:-1] == moBot):
    if (args[1] == "quali" and authorPerms.administrator):
      await submitQualiTime(message, qualifyingChannel, None, None, client)
    if ("missingqualifiers" in args[1].lower()):
      await tagMissingQualifiers(message)
    '''  
    elif (args[1] == "quali" and args[2] == "start"):
      await message.delete()
      reply = "```Qualifying Starts: 7th January 12:00am UK - " + str(datetime.strptime("6 Jan 2019 18:00", "%d %b %Y %H:%M") - datetime.now()) + "```"
      reply += "```Race Day: 27th January - " + str(datetime.strptime("27 Jan 2019 11:30", "%d %b %Y %H:%M") - datetime.now()).split(",")[0] + "```"
      await message.channel.send(reply)
      
    elif (args[1] == "helpquote"):
      await helpQuote(message)
    elif (args[1] == "addquote"):
      await addQuote(message)
    elif (args[1] == "sayquote"):
      await message.delete()
      
      await sayQuote(message, 0)
    elif (args[1] == "votes" and args[2] == "clear"):
      await clearReactionVotes(message)
    elif (args[1] == "vote" and args[2] == "count"):
      await getVotes(message.channel)
    elif (args[1] == "voters" and args[2] == "missing"):
      await getNonVoters(message)
    elif (args[1] == "laps" and args[2] == "missing"):
      await getMissingLaps(message)
    elif (args[1] == "driver" and args[2] == "add" and "staff" in roles):
      await addDriver(message)
    elif (args[1] == "driver" and args[2] == "remove" and "staff" in roles):
      await removeDriver(message)
    elif (args[1] == "add" and args[2] == "streamer" and "staff" in roles):
      await addStreamer(message)
    elif (args[1] == "remove" and args[2] == "streamer" and "staff" in roles):
      await removeStreamer(message)
    elif (args[1] == "reserve" and args[2] == "help"):
      await reserveHelp(message)
    elif (args[1] == "reserve" and "staff" in roles):
      if (args[2] == "needed"):
        await reserveNeeded(message, args)
      elif (args[2] == "not" and args[3] == "needed"):
        await reserveNotNeeded(message, args)
        await updateStartOrders(message)
      elif ("for" in message.content):
        await reserveFound(message)
        await updateStartOrders(message)
      elif (args[2] == "available"):
        await reserveAvailable(message)
    elif (args[1] == "reserves"):
      await message.channel.trigger_typing()
      await message.channel.send("```" + await getReservesNeeded() + "```")
    elif ("mute" in args[1] and "<@" in args[2]):
      toMute = args[1] == "mute"
      for role in message.guild.roles:
        if (role.name == "Muted"):
          userId = message.content.split("mute ")[1].split(">")[0][-18:]
          user = message.guild.get_member(int(userId))
          if (toMute):
            await user.add_roles(role)
            await message.channel.send("```User has been muted.```")
          else:
            await user.remove_roles(role)
            await message.channel.send("```User has been unmuted.```")
          await message.delete()
    elif (args[1] == "new" and args[2] == "week" and message.author.name == "Mo"):
      await newWeek(message)
  else:
    rand = int(random.random() * 1000) % 500
    await sayQuote(message, rand)
    '''
  '''if (args[0] == moBot and args[1] == "move" and args[2] == "members"):
    members = message.guild.members
    roles = message.guild.roles
    everyone = ""
    for role in roles:
      if (role.name == "COTM"):
        everyone = role
    for member in members:
      await member.add_roles(everyone)'''
      
  '''if (args[0] == moBot and args[1] == "send" and args[2] == "mardonius" and args[3] == "message"):
    botIds = [155149108183695360, 431247481267814410, 159985870458322944, 449247895858970624]
    namesToNotPrint = [446031992879054858]
    members = message.guild.members
    moBotMessage = "To fellow member of the COTM Server and the GTAV Racing Community:\nSome of you may be unaware, but before the current COTM server you are in now, there was a different server. There was a switch made, and a transfer of ownership, due to a very unusual circumstance where the host seemed to start suffering from mental health problems. Unfortunately, this wasn't entirely false.\n\nThanks to Yodafox and others that helped him, Yodafox has been able to contact Mardonius's (Ed's) Mom to find out that \"very sadly it seems he has become quite unwell and has had to be hospitalized\" (Yodafox via Ed's Mom). At the time of this message, there has not been a diagnosis.\n\nIn attempt to show support, a Google Form has been made to submit a message to be sent to the family and Mardonius. The messages will be reviewed for appropriateness, then Yodafox will send the messages over to the family. If you have any questions, message Mo#9991.\n\nhttps://goo.gl/forms/xYDGnabNKuDASMPy2"
    for i in range(38, len(members)):
      member = members[i]
      if (member.id not in namesToNotPrint):
        print (i, member.id)
        print (member)
      if (member.id in botIds):
        continue
      await member.send(moBotMessage)'''
# end main

async def mainReactionAdd(message, payload, client):
  member = message.guild.get_member(payload.user_id)
  memberPerms = message.channel.permissions_for(member)
  qualifyingChannel = message.guild.get_channel(607693838642970819)
  qualiScreenshotsChannel = message.guild.get_channel(607694176133447680)

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
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveAvailable(message, member, payload, client)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  member = message.guild.get_member(payload.user_id)
  if ("MoBot" not in member.name):
    if (message.id == 620811567210037253): # message id for Reserves Embed
      if (payload.emoji.name == WAVE_EMOJI):
        await reserveNotNeeded(message, member)
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveNotAvailable(message, member)
# end mainReactionRemove

async def tagMissingQualifiers(message):
  driversRange, driverSheet = await getDriversRange(await openSpreadsheet())
  missingQualifiers = await getMissingQualifiers(driversRange, message.guild)
  reply = ""
  for member in missingQualifiers:
    reply += member.mention
  print (reply)
# end tagMissingQualifiers

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
  embed["fields"][0]["value"] = reservesNeeded + "\n" + member.mention + "\n" + spaceChar
  await message.edit(embed=discord.Embed.from_dict(embed))
# end reserveNeeded

async def reserveNotNeeded(message, member):
  embed = message.embeds[0].to_dict()
  reservesNeeded = embed["fields"][0]["value"][:-1].strip().split("\n")
  newReservesNeeded = ""
  for reserve in reservesNeeded:
    if (str(member.id) not in reserve):
      newReservesNeeded += reserve + "\n"
  newReservesNeeded += spaceChar
  embed["fields"][0]["value"] = newReservesNeeded
  await message.edit(embed=discord.Embed.from_dict(embed))
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
  # end getReserveDivs

  reserveDiv = await getReserveDiv(member)
  divEmojisToAdd = []
  if (reserveDiv == -1):
    await message.remove_reaction(payload.emoji.name, member)
    return -1
  else:
    if (reserveDiv == 1):
      divEmojisToAdd.append(client.get_emoji(int(divisionEmojis[str(reserveDiv+1)])))
    else:
      for i in range(reserveDiv-1, reserveDiv+2, 2):
        emoji = client.get_emoji(int(divisionEmojis[str(i)]))
        divEmojisToAdd.append(emoji)

  moBotMessage = await message.channel.send(member.mention + ", which division(s) are you available to reserve for? *Click all that apply, then click the " + CHECKMARK_EMOJI + ".*")
  for emoji in divEmojisToAdd:
    await moBotMessage.add_reaction(emoji)
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)

  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=checkCheckmarkEmoji)
    moBotMessage = await message.channel.fetch_message(payload.message_id)
    embed = message.embeds[0].to_dict()
    reservesNeeded = embed["fields"][1]["value"][:-1].strip()

    for reaction in moBotMessage.reactions:
      if (str(reaction.emoji) != CHECKMARK_EMOJI):
        async for user in reaction.users():
          if (user.id == member.id):
            reservesNeeded += "\n" + str(reaction.emoji) + " - " + member.mention
    embed["fields"][1]["value"] = reservesNeeded + "\n" + spaceChar
    await message.edit(embed=discord.Embed.from_dict(embed))
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
    if (str(member.id) not in reserve):
      newReservesNeeded += reserve + "\n"
  newReservesNeeded += spaceChar
  embed["fields"][1]["value"] = newReservesNeeded
  await message.edit(embed=discord.Embed.from_dict(embed))

  for role in member.roles:
    if ("Reserve" in role.name):
      await member.remove_roles(role)
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
  totalVotersEmojiNumbers = await RandomFunctions.numberToEmojiNumbers(totalVoters)
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
    currentVotersEmbed["fields"][2]["value"] += "\n" + member.mention + " - <#" + str(votingChannel.id) + ">"
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
    if (userID == int(moBot)):
      await message.channel.send("**Driver Not Found**\nEdit your message to follow this command: `@MoBot#0697 quali @User x.xx.xxx`")
      return

    user = message.guild.get_member(userID)
    lapTime = message.content.split(str(user.id))[1].strip().split(" ")[1].strip().replace(":", ".")
  else:
    user = message.author
    lapTime = lapTime.replace(":", ".")
    await message.channel.send(user.mention + ", your lap has been submitted.")

  workbook = await openSpreadsheet()
  driversRange, driversSheet = await getDriversRange(workbook)
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
  await updateDivList(message, divList)
# end submitQualiTime

async def addUserToQualiScreenshots(message, user, qualiScreenshotsChannel, client):
  await qualiScreenshotsChannel.set_permissions(user, read_messages=True, send_messages=True)
  moBotMessage = await qualiScreenshotsChannel.send("<@" + str(user.id) + ">, you have 60 seconds to submit your screenshot.")

  def check(msg):
    return msg.author.id == user.id and msg.channel.id == qualiScreenshotsChannel.id
  
  try:
    msg = await client.wait_for("message", timeout=60.0, check=check)
    await moBotMessage.delete()
    if (len(msg.attachments) > 0 or "http" in msg.content):
      moBotMessage = await msg.channel.send("<@" + str(user.id) + ">, if there is more than one driver in the screenshot, please type which drivers need inputting, otherwise, thank you for submitting.")
      try:
        msg = await client.wait_for("message", timeout=120.0, check=check)
      except asyncio.TimeoutError:
        pass
      await qualiScreenshotsChannel.set_permissions(user, read_messages=True, send_messages=False)
      await moBotMessage.delete()
      return
    else:
      await qualiScreenshotsChannel.send("**Please only send an attachment of your screenshot or a link to it.**\nIf this was an error, contact Mo#9991.", delete_after=10.0)
      await msg.delete()
  except asyncio.TimeoutError:
    await moBotMessage.delete()
    await message.channel.send("<@" + str(user.id) + ">, you took too long. If you still need to submit a screenshot, click the ✅ at the top of the channel.", delete_after=120.0)
  
  await qualiScreenshotsChannel.set_permissions(user, overwrite=None)
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
      divList.sort(key=lambda x:x[1])
      embed.set_author(name="Children of the Mountain - Season 5\nSorted By Gamertag", icon_url=logos["cotmFaded"], url="https://www.google.com/DivisionList")
      embed = embed.to_dict()
      divListEmbeds["sortedByGamertag"].append(embed)

    else:
      divList.sort(key=lambda x:x[0])
      embed.set_author(name="Children of the Mountain - Season 5\nSorted By Division", icon_url=logos["cotmFaded"], url="https://www.google.com/DivisionList")
      embed = embed.to_dict()
      divListEmbeds["sortedByDivision"].append(embed)

    nameRange = ["", ""]
    for i in range(len(divList)):
      nameRange[1] = divList[i][1]
      if (i % 15 == 0):
        nameRange[0] = divList[i][1]
        div = int(i/15) + 1

        embed = discord.Embed(color=int("0xd1d1d1", 16))
        if (key == "sortedByGamertag"):
          embed.add_field(name="", value="", inline=False)
        else:
          embed.add_field(name="Division " + str(div), value="", inline=False)
        embed = embed.to_dict()
        divListEmbeds[key].append(embed)
      if (key == "sortedByGamertag"):
        divListEmbeds[key][len(divListEmbeds[key])-1]["fields"][0]["name"] = nameRange[0] + " - " + nameRange[1]
      divListEmbeds[key][len(divListEmbeds[key])-1]["fields"][0]["value"] += "[D" + str(divList[i][0]) + "] " + divList[i][1] + "\n"
  
  await divListChannel.purge()
  for embed in divListEmbeds["sortedByGamertag"]:
    await divListChannel.send(embed=discord.Embed.from_dict(embed))
  for embed in divListEmbeds["sortedByDivision"]:
    await divListChannel.send(embed=discord.Embed.from_dict(embed))
# end updateDivList

async def updateDriverRoles(message, workbook):
  await message.channel.trigger_typing()
  divUpdateChannel = message.guild.get_channel(527319768911314944)
  standingsSheet = workbook.worksheet("Standings")
  drivers = standingsSheet.range("C3:D" + str(standingsSheet.row_count))

  divRoles = []
  for role in message.guild.roles:
    if ("division" in role.name.lower() and "reserve" not in role.name.lower()):
      divRoles.append([int(role.name[-1]), role])
  divRoles.sort(key=lambda x:x[0])

  divList = []
  for member in message.guild.members:
    driverIndex = findDriver(drivers, member.id)
    if (driverIndex >= 0):
      try:
        div = str(int(drivers[driverIndex-1].value[-1]))
        gamertag = drivers[driverIndex].value
        role = divRoles[int(div)-1][1]

        newNick = "[D" + div + "] " + gamertag
        divList.append([int(div), gamertag])
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
        print (str(traceback.format_exc()))
  return divList
# end updateDriverRoles

async def getDriversRange(workbook):
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