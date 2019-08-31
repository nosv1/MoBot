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

async def main(args, message, client):
  try:
    authorPerms = message.channel.permissions_for(message.author)
  except:
    pass
    
  qualifyingChannel = message.guild.get_channel(607693838642970819)
  qualiScreenshotsChannel = message.guild.get_channel(607694176133447680)

  if (args[0][-19:-1] == moBot):
    if (args[1] == "quali" and authorPerms.administrator):
      await submitQualiTime(message, qualifyingChannel, None, client)
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
  qualifyingChannel = message.guild.get_channel(607693838642970819)
  qualiScreenshotsChannel = message.guild.get_channel(607694176133447680)

  if (member.name != "MoBot"):
    if (message.id == 614836845267910685): # message id for "Do you need to submit quali time"
      if (payload.emoji.name == "✅"):
        await addUserToQualiScreenshots(message, member, qualiScreenshotsChannel, client)
        await message.remove_reaction(payload.emoji.name, member)
    elif (message.id == 609588876272730112): # message id for message "Do you need to vote?"
      if (payload.emoji.name == "✅"):
        await openVotingChannel(message, member)
        await message.remove_reaction(payload.emoji.name, member)
    elif ("are you ready to vote" in message.content):
      if (payload.emoji.name == "✅"):
        await votingProcess(message, member, client)
      elif (payload.emoji.name == "🔄"):
        await resetVotes(message)
    elif (message.channel.id == qualiScreenshotsChannel.id):
      if (message.channel.permissions_for(member).administrator and payload.emoji.name == "👍"):
        await waitForQualiTime(message, member, payload, qualifyingChannel, client)

    '''if (message.channel.id == 528303438132543499): # voting channel
      votingMessagesIds = [528307697133682698, 528307713403256852, 528307733456355331, 528307794936463374]
      if (message.id in votingMessagesIds):
        await voting(message, payload, votingMessagesIds)
    elif (payload.emoji.name == "🔄"): # if update button is clicked 
      if (message.id == 527321745968070689): # qualifying standings channel
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updateQualiStandings(message)
      if (message.id == 527685885790126111): # qualifying channel
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updateQualiStartTimes(message)
      if (message.id == 535553787948171284): # div list channel
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updateDivList(message)
      if (message.id == 536878535827259432): # start order channel
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updateStartOrders(message)
      if (message.id == 527563354877984810): # cotm-streams channel
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updateDivStreamers(message)
      if ("pit-log" in channelName):
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        div = int(channelName[1])
        await updateNamesPitLog(message, div)
    elif ("pit-log" in channelName):
      if (payload.emoji.name == "1⃣" or payload.emoji.name == "2⃣"):
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
        await updatePitCount(message, payload)'''
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  channelName = message.channel.name
# end mainReactionRemove

async def resetVotes(message):
  await message.clear_reactions()
  await message.channel.purge(after=message)
  await message.add_reaction("✅")
  await message.add_reaction("🔄")
# end resetVotes

async def votingProcess(message, member, client):
  await message.clear_reactions()
  await message.add_reaction("🔄")
  numberEmojis = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
  undoEmoji = "↩"

  votingChannel = message.channel

  # get vote options
  voteOptionsMsg = await getCurrentVotersVoteOptionsMsg(message)
  voteOptionsEmbed = voteOptionsMsg.embeds[0].to_dict()
  voteOptions = voteOptionsEmbed["fields"][0]["value"].split("\n")
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
  await moBotMessage.add_reaction("✅")
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
  currentVoters = (currentVotersEmbed["fields"][1]["value"] + "\n").split("\n")
  value = ""
  for voter in currentVoters:
    if (str(member.id) not in voter and "@" in voter):
      value += "\n" + voter
  if (value.split(spaceChar)[0].strip() == ""):
    value = "None" 
  value += "\n" + spaceChar
  currentVotersEmbed["fields"][1]["value"] = value
  currentVotersEmbed["fields"][2]["value"] = totalVotersEmojiNumbers + "\n" + spaceChar
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
  currentVotersMsg = await channel.fetch_message(609588935747960864)
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
  currentVoters = currentVotersEmbed["fields"][1]["value"]

  # get past voters
  workbook = await openSpreadsheet()
  votingSheet = workbook.worksheet("Voting")
  pastVotersRange = votingSheet.range("D3:D" + str(votingSheet.row_count))
  isPastVoter = findDriver(pastVotersRange, str(member.id)) >= 0

  # create voting channel
  if (str(member.id) not in currentVoters and not isPastVoter):
    votingChannel = await message.guild.create_text_channel(name="voting " + member.display_name)

    # udpate current voters
    currentVotersEmbed["fields"][1]["value"] = "" if ("None" in currentVoters) else currentVoters.split(spaceChar)[0].strip() 
    currentVotersEmbed["fields"][1]["value"] += "\n<@" + str(member.id) + "> - <#" + str(votingChannel.id) + ">"
    currentVotersEmbed["fields"][1]["value"] += "\n" + spaceChar
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
    voteOptions = voteOptionsEmbed["fields"][0]["value"].split("\n")
    del voteOptions[-1]

    await votingChannel.send("This season there's been a change to how the voting works. As you can see there are " + str(len(voteOptions)) + " options to vote from. You have " + str(len(voteOptions)) + " votes to 'spend'. You can use them all on one option, or spread them out.")

    moBotMessage = await votingChannel.send("**<@" + str(member.id) + ">, are you ready to vote?**")
    await moBotMessage.add_reaction("✅")

  else:
    msg = await message.channel.send("**Cannot open a voting channel.**\n**<@" + str(member.id) + ">, you either already have a voting channel open, or you have already voted.**")
    await asyncio.sleep(10)
    await msg.delete()
# end openVotingChannel

async def waitForQualiTime(message, member, payload, qualifyingChannel,client):
  def check(msg):
    return msg.author.id == member.id and message.channel.id == msg.channel.id

  reactions = message.reactions
  for reaction in reactions:
    if (reaction.emoji == payload.emoji.name):
      if (reaction.count == 1):
        moBotMessage = await message.channel.send(member.mention + ", please type the time from the screenshot that you added the reaction to.")
        msg = await client.wait_for("message", timeout=60.0, check=check)
        await submitQualiTime(message, qualifyingChannel, msg.content, client)
        await moBotMessage.delete()
      break
# end waitForQualiTime

async def submitQualiTime(message, qualifyingChannel, lapTime, client):  
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
  driversSheet = workbook.worksheet("Drivers")
  driversRange = driversSheet.range("B3:C" + str(driversSheet.row_count))
  qualifyingSheet = workbook.worksheet("Qualifying")
  qualifyingRange = qualifyingSheet.range("G3:I" + str(qualifyingSheet.row_count))

  driverIndex = findDriver(driversRange, str(user.id))
  moBotMessage = None
  if (driverIndex == -1):
    def checkMsg(msg):
      return msg.author.id == message.author.id and msg.channel.id == message.channel.id
    def checkMsgEdit(payload):
      return payload.author_id == message.author.id and payload.channel_id == message.channel.id
    def checkEmoji(payload):
      return payload.user_id == message.author.id and payload.channel_id == message.channel.id and (payload.emoji.name == "✅" or payload.emoji.name == "❌")

    moBotMessage = await message.channel.send("This user has not had a time inputted yet. What is their gamertag in the screenshot?")
    looped = False
    while True:
      try:
        if (not looped):
          msg = await client.wait_for("message", timeout=30.0, check=checkMsg)
        else:
          payload = await client.wait_for("raw_message_edit", timeout=30.0, check=checkMsg)
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
      await moBotMessage.add_reaction("✅")
      await moBotMessage.add_reaction("❌")

      try:
        payload = await client.wait_for("raw_reaction_add", timeout=30.0, check=checkEmoji)
      except asyncio.TimeoutError:
        msg = await message.channel.send("**TIMED OUT**")
        await asyncio.sleep(3)
        await moBotMessage.delete()
        await msg.delete()
        return

      if (payload.emoji.name == "✅"):
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

  qualifyingSheet.update_cells(qualifyingRange, value_input_option="USER_ENTERED")
  
  await moBotMessage.edit(content="**Updating Driver Roles**")
  divList = await updateDriverRoles(message, workbook)

  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
  value = ""
  value += "**Driver:** <@" + str(userEntry[3]) + ">"
  value += "\n**Time:** " + floatTimeToStringTime(lapTime)
  value += "\n**Division:** " + str(int(position / 15) + 1)
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
    topMsgID = msg.id if (topMsgID == None) else topMsgID
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
  drivers = standingsSheet.range("C3:E" + str(standingsSheet.row_count))

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
        gamertag = drivers[driverIndex+1].value
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
            await divUpdateChannel.send("<@" + str(member.id) + "> has been removed from " + mRole.name + ".")

        if (not hasRole):
          await member.add_roles(role)
          await divUpdateChannel.send("<@" + str(member.id) + "> has been added to " + role.name + ".")  
      except ValueError:
        print (str(traceback.format_exc()))
  return divList
# end updateDriverRoles

############# OLD FUNCITONS #############
async def removeDriver(message):
  # remove from standings sheet
  workbook = await openSpreadsheet()
  standingsSheet = workbook.worksheet("Standings")
  udsrSheet = workbook.worksheet("Universal Driver Skill Rating")
  
  gt = ""
  for i in message.content.split("remove")[1][1:].split(" "):
    gt += i + " "
  gt = gt[:-1]
  
  upperDivs = standingsSheet.range("B7:C96")
  bottomDiv = standingsSheet.range("L7:L34")
  
  driverFoundU = findDriver(upperDivs, gt)
  driverFoundB = findDriver(bottomDiv, gt)  
  
  currentDiv = ""
  if (driverFoundU > -1):
    upperDivs[driverFoundU].value = ""
    currentDiv = upperDivs[driverFoundU-1].value[-1]
  elif (driverFoundB > -1):
    bottomDiv[driverFoundB].value = ""
    currentDiv = standingsSheet.range("K5:L5")[0].value[-1]
  else:
    await message.channel.send("```Driver was not found.```")
    
  if (driverFoundU > -1 or driverFoundB > -1):
    standingsSheet.update_cells(upperDivs, value_input_option="USER_ENTERED")
    standingsSheet.update_cells(bottomDiv, value_input_option="USER_ENTERED")
    
  # update roles -- find user in server, based on gamertag, assuming they haven't left the server
  members = message.guild.members
  user = None
  for member in members:
    # [D#] gt
    try:
      if (member.nick[5:] == gt):
        user = member
        break
    except TypeError:
      continue
  
  try:
    divUpdateChannel = message.guild.get_channel(527319768911314944)
    for role in message.guild.roles:
      if ("Peeker" == role.name):
        await user.add_roles(role)
      elif ("Division " + str(currentDiv) == role.name):
        await user.remove_roles(role)
        await divUpdateChannel.send("<@" + str(user.id) + "> has been removed from Division " + str(currentDiv) + ".")
      elif ("COTM" == role.name):
        await user.remove_roles(role)
        await user.edit(nick=user.nick.split("] ")[1])
  except TypeError:
    await message.channel.send("```User not found.```")
  
  
  # promote drivers on spreadsheet
  '''drivers = udsrSheet.range("R6:R129")
  rpis = udsrSheet.range("AA6:AA129")
  canPromote = False
  i = int(currentDiv) * 15 * 2 + 1 # 15 num divs, 2 columns, + 1 to get the name, not the div
  while (i < len(upperDivs)):
    promotee = upperDivs[i].value
    for j in range(len(drivers)):
      if (drivers[j].value == promotee):
        if (rpis[j].value != ""):
          canPromote = True
          break
    if (canPromote):
      break
      
    i += 2'''
  await updateStartOrders(message)
  await updateDivList(message)

async def addDriver(message):
  # add driver to spreadsheet
  workbook = await openSpreadsheet()
  standingsSheet = workbook.worksheet("Standings")
  
  bottomDiv = standingsSheet.range("L7:L34")
  
  gt = ""
  for i in message.content.split(">")[2][1:].split(" "):
    gt += i + " "
  gt = gt[:-1]
  
  for i in range(len(bottomDiv)):
    if (bottomDiv[i].value == ""):
      bottomDiv[i].value = gt
      break
  standingsSheet.update_cells(bottomDiv, value_input_option="USER_ENTERED")
  
  # assign roles
  numDivs = standingsSheet.range("K5:M5")[0].value[-1]
  user = message.content.split(">")[1][-18:]
  user = message.guild.get_member(int(user))
  
  divUpdateChannel = message.guild.get_channel(527319768911314944)
  for role in message.guild.roles:
    if (("Division " + str(numDivs)) == role.name):
      await user.add_roles(role)
      await divUpdateChannel.send("<@" + str(user.id) + "> has been added to Division " + str(numDivs) + ".")
    elif ("COTM" == role.name):
      await user.add_roles(role)
    elif ("Peeker" == role.name):
      await user.remove_roles(role)
  
  # update name in server
  await user.edit(nick="[D" + str(numDivs) + "] " + gt)
  
  await updateStartOrders(message)
  await updateDivList(message)
# end addDriver

async def updatePitCount(message, payload):
  if (payload.emoji.name == "1⃣"):
    try:
      numPits = int(message.content.split(" -")[0][-1]) + 1
      reply = message.content.split(" -")[0][:-1] + str(numPits) + " -- " + message.content.split("-- ")[1]
    except ValueError:
      numPits = int(message.content[-4]) + 1
      reply = message.content[:-4] + str(numPits) + "```"
    await message.edit(content=reply)
  elif (payload.emoji.name == "2⃣"):
    numPits = int(message.content[-4]) + 1
    reply = message.content[:-4] + str(numPits) + "```"
    await message.edit(content=reply)
# end updatePitCount

async def updateNamesPitLog(message, div): # div is an int already  
  # clear everything in channel
  junk = message.channel.history(after=message)
  async for msg in junk:
    await msg.delete()
  
  # get start orders from discord channel...
  startOrdersChannel = message.guild.get_channel(533173141611085824)
  startOrderMessages = startOrdersChannel.history(after=await startOrdersChannel.fetch_message(536878535827259432))
  startOrders = []
  async for startOrderMessage in startOrderMessages:
    try:
      startOrders.append(startOrderMessage.content.split(":")[1].split("-`")[0])
      i = len(startOrders)-1
      startOrders[i] = startOrders[i][startOrders[i].index("-\n| ")+2:] # gets rid of headers
      startOrders[i] = startOrders[i][:startOrders[i].index("|\n-")] # gets rid of bottom line
      
      startOrders[i] = startOrders[i].split("|\n")
      for j in range(0, len(startOrders[i])):
        temp = []
        temp.append(startOrders[i][j].split("|")[2].strip()) # driver
        temp.append(startOrders[i][j].split("|")[3].strip()) # reserve
        if (temp[1] != "" and temp[1] != "Race Penalty" and temp[1] != "Grid Penalty"):
          t = temp[0]
          temp[0] = temp[1]
          temp[1] = t
        temp.append(temp[0].lower())
        # to correclty sort the names in the bottom div, we fake the sort data to be 'z' instead of blank
        if (temp[-1] != ""):
          startOrders[i][j] = temp
        else:
          startOrders[i][j] = ["","","zzzzz"]
    except IndexError:
      break
      
  for i in range(0, len(startOrders)):
    startOrders[i].sort(key=lambda x:x[2])
  
  # make this smarter
  for j in range(0, len(startOrders[div-1]), 2):
    i = div - 1
    
    # add first name
    reply = ""
    if (startOrders[i][j][2] != "zzzzz"):
      if (startOrders[i][j][1] == ""):
        reply += startOrders[i][j][0] + " 0"
      else:
        reply += startOrders[i][j][1] + " (R) 0"
        
    # add second name
    try:
      if (startOrders[i][j+1][2] != "zzzzz"):
        if (startOrders[i][j+1][1] == ""):
          reply += " -- " +  startOrders[i][j+1][0] + " 0"
        else:
          reply += " -- " +  startOrders[i][j+1][1] + " (R) 0"
    except IndexError:
      pass
    
    if (reply != ""):
      msg = await message.channel.send("```" + reply + "```")
      await msg.add_reaction("1⃣")
      if ("--" in reply):
        await msg.add_reaction("➖")
        await msg.add_reaction("2⃣")
# end updateNamesPitLog

async def reserveHelp(message):
  reply = ""
  reply += "Reserve Commands:\n"
  reply += "\n"
  reply += "  Reserve Needed:\n"
  reply += "    @MoBot#0697 reserve needed gamertag\n"
  reply += "      @MoBot#0697 reserve needed Mo v0\n"
  reply += "\n"
  reply += "  Reserve For Driver:\n"
  reply += "    @MoBot#0697 reserve reserve_gamertag for gamertag\n"
  reply += "      @MoBot#0697 reserve IStarki11er29I for Mo v0\n"
  reply += "\n"
  reply += "  Reserve Available:\n"
  reply += "    @MoBot#0697 reserve available reserve_gamertag\n"
  reply += "      @MoBot#0697 reserve available Mo v0\n"
  reply += "\n"
  reply += "  Reserve Not Needed:\n"
  reply += "    @MoBot#0697 reserve not needed gamertag\n"
  reply += "      @MoBot#0697 reserve not needed Mo v0\n"
  reply += "\n"
  reply += "  Get Reserves for Current Week:\n"
  reply += "    @MoBot#0697 reserves\n"
  reply = reply[:-1] # remove trailing new line

  await message.channel.send("```" + reply + "```")
# end reserveHelp

async def getReservesNeeded():
  workbook = await openSpreadsheet()
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  
  reserveList = weeklyInformationSheet.range("B2:D23")
  reserves = []
  
  driverWidth = 10
  reserveDriverWidth = 7
  for i in range(6, len(reserveList), 3):
    if (not(reserveList[i+1].value == "" and reserveList[i+2].value == "")):
      reserves.append([reserveList[i].value, reserveList[i+1].value, reserveList[i+2].value])
      if (len(reserves[len(reserves)-1][1]) > driverWidth):
        driverWidth = len(reserves[len(reserves)-1][1])
      if (len(reserves[len(reserves)-1][2]) > reserveDriverWidth):
        reserveDriverWidth = len(reserves[len(reserves)-1][2])
        
  horizontalBoarder = ""
  for i in range(0, 3 + driverWidth + reserveDriverWidth + 4):
    horizontalBoarder += "-"
    
  reserveTable = "\n" + horizontalBoarder + "\n"
  reserveTable += "|" + reserveList[0].value.center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"
  reserveTable += "|" + reserveList[3].value.center(3, " ") + "|" + reserveList[4].value.center(driverWidth, " ") + "|" + reserveList[5].value.center(reserveDriverWidth, " ") + "|\n" + horizontalBoarder + "\n"
  
  for row in reserves:
    if (row[0] != ""):
      reserveTable += "|" + row[0][-1].center(3, " ") + "|"
    else:
      reserveTable += "|" + "".center(3, " ") + "|"
    reserveTable += row[1].center(driverWidth, " ") + "|" + row[2].center(reserveDriverWidth, " ") + "|\n"
  reserveTable += horizontalBoarder
  
  return reserveTable
# end getReservesNeeded

async def reserveAvailable(message):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  
  reserve = message.content.split("available ")[1]
  reserves = weeklyInformationSheet.range("D4:D23")
  
  driverFoundR = findDriver(reserves, reserve)
  if (driverFoundR > -1):
    await message.channel.send("```" + reserve + " is already available to reserve.```")
  else:
    for i in range(len(reserves) - 1, 0 - 1, -1):
      if (reserves[i].value == ""):
        reserves[i].value = reserve
        break
    await message.channel.send("```" + reserve + " is now available to reserve.```")
    weeklyInformationSheet.update_cells(reserves, value_input_option="USER_ENTERED")
    await message.channel.send("```" + await getReservesNeeded() + "```")
# end reserveAvailable

async def reserveFound(message):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  standingsSheet = workbook.worksheet("Standings")
  
  reserve = message.content.split("reserve ")[1].split(" for")[0]
  driver = message.content.split("for ")[1]
  
  reserves = weeklyInformationSheet.range("D4:D23")
  drivers = weeklyInformationSheet.range("C4:C23")
  
  driverFoundR = findDriver(reserves, reserve)
  driverFoundD = findDriver(drivers, driver)
  
  reserveUpdated = False
  if (driverFoundD > -1):
    if (driverFoundR > -1):
      if (drivers[driverFoundR].value == ""):
        reserves[driverFoundR].value = ""
        reserves[driverFoundD].value = reserve
        reserveUpdated = True
      else:
        await message.channel.send("```" + reserve + " is already reserving for someone. Update reserve manually.```")
    else:
      reserves[driverFoundD].value = reserve
      reserveUpdated = True
  else:
    driverFoundD = findDriver(standingsSheet.range("H7:H124"), driver)
    if (driverFoundD > -1):
      for i in range(len(drivers)):
        if (drivers[i].value == "" and reserves[i].value == ""):
          drivers[i].value = driver
          reserves[i].value = reserve
          reserveUpdated = True
          break
    else:
      await message.channel.send("```" + driver + " was not found. If you are sure the gamertag typed was correct, tag IStarki11er29I and/or Mo.```")
      
  if (reserveUpdated):
    divs = standingsSheet.range("G7:G124")
    driverFoundD = findDriver(standingsSheet.range("H7:H124"), driver)
    
    members = message.guild.members
    user = None
    for member in members:
      if (member.nick != None):
        if (reserve in member.nick):
          user = member
    for role in message.guild.roles:
      if ("reserve" in role.name.lower() and role.name[-1] == divs[driverFoundD].value[-1]):
        await user.add_roles(role)
        await message.guild.get_channel(527319768911314944).send("<@" + str(user.id) + "> has been added to " + role.name + ".")
    
    await message.channel.send("```" + reserve + " is now reserving for " + driver + " in Division " + divs[driverFoundD].value[-1] + ".```")
  
    weeklyInformationSheet.update_cells(reserves, value_input_option="USER_ENTERED")
    weeklyInformationSheet.update_cells(drivers, value_input_option="USER_ENTERED")
    
    await message.channel.send("```" + await getReservesNeeded() + "```")

async def reserveNotNeeded(message, args):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  
  driver = await compileDriverFromArgs(args, 4, len(args))
  
  reservesNeeded = weeklyInformationSheet.range("C4:D23")
  driverFoundR = findDriver(reservesNeeded, driver)
  
  if (driverFoundR > -1):
    reserve = reservesNeeded[driverFoundR + 1].value
    reservesNeeded[driverFoundR].value = ""
    reservesNeeded[driverFoundR + 1].value = ""
    
    weeklyInformationSheet.update_cells(reservesNeeded, value_input_option="USER_ENTERED")
    await message.channel.send("```" + driver + " has been removed from the 'Reserves Needed' list.```")
    if (reserve != ""):
      div = 0 
      i = 0
      members = message.guild.members
      while (i < len(members)):
        try:
          if (div == 0):
            if (driver.lower() in members[i].nick.lower()):
              div = members[i].nick[2]
              i = 0
          elif (reserve.lower() in members[i].nick.lower()):
            for role in message.guild.roles:
              if ("reserve" in role.name.lower() and role.name[-1] == div):
                await members[i].remove_roles(role)
                await message.guild.get_channel(527319768911314944).send("<@" + str(members[i].id) + "> has been removed from " + role.name + ".")
            break
        except AttributeError:
          i += 1
          continue
        i += 1
    
      await message.channel.send("```" + reserve + " is no longer a reserve.```")
    
    await message.channel.send("```" + await getReservesNeeded() + "```")

async def reserveNeeded(message, args):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  standingsSheet = workbook.worksheet("Standings")
  
  driver = await compileDriverFromArgs(args, 3, len(args))          
  driverFoundS = findDriver(standingsSheet.range("H7:H124"), driver)
  
  if (driverFoundS > -1): # driver was in standings
    reservesNeeded = weeklyInformationSheet.range("C4:C23")
    driverFoundR = findDriver(reservesNeeded, driver)
    if (driverFoundR == -1):
      for i in range(0, len(reservesNeeded)):
        if (reservesNeeded[i].value == "" or reservesNeeded[i].value == driver):
          reservesNeeded[i].value = driver
          break
      weeklyInformationSheet.update_cells(reservesNeeded, value_input_option="USER_ENTERED")
      divs = standingsSheet.range("G7:G124")
      await message.channel.send("```" + driver + ", who is in Division " + divs[driverFoundS].value + ", has been added to the 'Reserves Needed' list.```")
      await message.channel.send("```" + await getReservesNeeded() + "```")
      await updateStartOrders(message)
    else:
      await message.channel.send("```" + driver + " has already been added to the 'Reserves Needed' list.```")
  else:
    await message.channel.send("```" + driver + " was not found. If you are sure the gamertag typed was correct, tag IStarki11er29I and/or Mo.```")
# end reserveNeeded

async def updateDivStreamers(message):
  workbook = await openSpreadsheet()
  weeklyInfoSheet = workbook.worksheet("Weekly Information")
  pitMarshallsRange = weeklyInfoSheet.range("F17:H23")

  cotmStreamsChannel = message.guild.get_channel(527161746473877504)
  mainListMessage = await cotmStreamsChannel.fetch_message(527563354877984810)
  divStreamersMessage = await cotmStreamsChannel.fetch_message(543450388955791361)
  multiStreamsMessage = await cotmStreamsChannel.fetch_message(551817591526653955)
  
  members = message.guild.members
  users = {}
  # get div of user
  for member in members:
    if (member.nick != None):
      if ("[" in member.nick):
        users[member.nick[5:]] = [member.nick[2], member]
  
  divStreamers = [[], [], [], [], [], [], []] # div 1-7
  reserves = [[], [], [], [], [], [], []]
  pitMarshalls = [[], [], [], [], [], [], []]
  
  streamers = mainListMessage.content.split("\n")
  for streamer in streamers:
    try:
      temp = streamer.split(" - ")
      if (len(temp) > 1):
        gt = temp[1]
        div = users[gt][0]
        divStreamers[int(div)-1].append([users[gt][1].nick, temp[-1]])
        
        for role in users[gt][1].roles:
          if ("reserve" in role.name.lower()):
            reserveDiv = role.name[-1]
            reserves[int(reserveDiv)-1].append([users[gt][1].nick, temp[-1]])
            
        for i in range(0, len(pitMarshallsRange), 3):
          div = pitMarshallsRange[i].value
          if (gt == pitMarshallsRange[i+1].value):
            pitMarshalls[int(div)-1].append([users[gt][1].nick, temp[-1]])
          elif (gt == pitMarshallsRange[i+2].value):
            pitMarshalls[int(div)-1].append([users[gt][1].nick, temp[-1]])
            
    except KeyError: # mistake in gamertag in main streamer list...
      continue
      
  divMultiStreams = ["", "", "", "", "", "", ""]
  reply1 = ""
  for i in range(len(divStreamers)):
    if (len(divStreamers[i]) != 0):
      reply1 += "\n**Division " + str(i+1) + "**:\n"
      divMultiStreams[i] = "https://multistre.am/"
      for streamer in divStreamers[i]:
        reply1 += "  - " + streamer[0] + " - " + streamer[1] + "\n"
        try:
          divMultiStreams[i] += streamer[1].split(".tv/")[1].split(">")[0] + "/"
        except IndexError: # mixer links and youtube links
          continue
      # add reserve to multistream
      for streamer in reserves[i]:
        reply1 += "  - [R]" + streamer[0] + " - " + streamer[1] + "\n"
        try:
          divMultiStreams[i] += streamer[1].split(".tv/")[1].split(">")[0] + "/"
        except IndexError: # mixer and youtube links 
          continue
      # add pit marshall to multistream
      for streamer in pitMarshalls[i]:
        reply1 += "  - [PM]" + streamer[0] + " - " + streamer[1] + "\n"
        try:
          divMultiStreams[i] += streamer[1].split(".tv/")[1].split(">")[0] + "/"
        except IndexError: # mixer and youtube links 
          continue
        
  reply2 = ""
  reply2 += "\n__**Known Multistreams**__\n"
  for i in range(len(divMultiStreams)):
    if (divMultiStreams[i] != ""):
      reply2 += "  Division " + str(i + 1) + " - <" + divMultiStreams[i] + ">\n"
      
  await divStreamersMessage.edit(content="__**This Week's Streamers**__\n" + reply1)
  await multiStreamsMessage.edit(content=reply2 + "\n*Feel free to set up a custom multistream using <https://multistre.am/>*")
# end updateDivStreamers

async def removeStreamer(message):
  streamer = message.content.split("streamer ")[1]
  if (" " == streamer[-1]):
    streamer = streamer[:-1]

  streamerMessage = await message.channel.fetch_message(527563354877984810)
  streamerList = streamerMessage.content.split("\n")
  for i in range(len(streamerList)):
    streamerList[i] = streamerList[i].split(" - ")
    
  for i in range(len(streamerList)): 
    try:
      if (streamerList[i][1] == streamer):
        del streamerList[i]
    except IndexError:
      continue
        
  reply = "**Streamers:**\n"
  for i in range(1, len(streamerList)):
    reply += "  - " + streamerList[i][1] + " - " + streamerList[i][2] + "\n"
    
  await streamerMessage.edit(content=reply)
  await message.delete()
# end removeStreamer

async def addStreamer(message):
  cotmStreamsChannel = message.guild.get_channel(527161746473877504)
  mainListMessage = await cotmStreamsChannel.fetch_message(527563354877984810)
  
  streamLink = message.content.split(" ")[-1]
  gamertag = message.content.split("streamer ")[1].split(" " + streamLink)[0]
  
  newEntry = "  - " + gamertag + " - "
  if ("<" not in streamLink):
    newEntry += "<" + streamLink + ">"
  else:
    newEntry += streamLink
    
  members = message.guild.members
  
  # make sure gamertag is in the server
  user = None
  for member in members:
    if (member.nick != None):
      if ("[" in member.nick):
        gt = member.nick[5:]
        if (gt == gamertag):
          user = member
      elif (member.nick == gamertag):
        user = member
    else:
      if (member.name == gamertag):
        user = member
        
  # get Streamer role
  '''for role in message.guild.roles:
    if (role.name == "Streamer"):
      if (user != None):
        await user.add_roles(role)
        break'''
    
  newList = mainListMessage.content + "\n" + newEntry
  await mainListMessage.edit(content=newList)
  await message.channel.send("```Streamer added.```")
# end addStreamer

# includes updating reserve list
async def updateStartOrders(message):
  moBotMessages = []
  startOrderChannel = message.guild.get_channel(533173141611085824)
  updateMsg = await startOrderChannel.fetch_message(536878535827259432)
  history = startOrderChannel.history(after=updateMsg)
  async for msg in history:
    await msg.delete()
  moBotMessages.append(await message.channel.send("```Updating Start Orders...```"))
  
  workbook = await openSpreadsheet()
  weeklyInfoSheet = workbook.worksheet("Weekly Information")
  divRosterSheet = workbook.worksheet("Division Rosters")
  
  reserveList = weeklyInfoSheet.range("B2:D23")
  startOrders = []
  reserves = []
  
  for i in range(0, 6):
    topCell = str(10 + (18 * i))
    bottomCell = str(24 + (18 * i))
    startOrders.append(divRosterSheet.range("H" + topCell + ":H" + bottomCell))
    reserves.append(divRosterSheet.range("N" + topCell + ":N" + bottomCell))
    
  # get bottom div
  startOrders.append(divRosterSheet.range("H118:H145"))
  reserves.append(divRosterSheet.range("N118:N145"))
  
  # get div count
  divCount = 0
  for i in range(len(startOrders)):
    if (startOrders[i][0].value != ""):
      divCount += 1
      
  # construct reserve list table
  # get dirver width 
  driverWidth = 10
  for i in range(len(startOrders)):
    for j in range(len(startOrders[i])):
      if (len(startOrders[i][j].value) > driverWidth):
        driverWidth = len(startOrders[i][j].value)
  # get reserve driver width
  reserveDriverWidth = 7
  for i in range(len(reserves)):
    for j in range(len(reserves[i])):
      if (len(reserves[i][j].value) > reserveDriverWidth):
        reserveDriverWidth = len(reserves[i][j].value)
        
  horizontalBoarder = ""
  for i in range(0, 3 + driverWidth + reserveDriverWidth + 4):
    horizontalBoarder += "-"
  
  reserveTable = await getReservesNeeded()
 
  divCount = 0
  for i in range(len(startOrders)):
    if (startOrders[i][0].value != ""):
      divCount += 1
    else:
      continue
    startOrderTable = "Division " + str(divCount) + ":\n" + horizontalBoarder + "\n"
    startOrderTable += "|Pos|" + "Driver".center(driverWidth, " ") + "|" + "Reserve".center(reserveDriverWidth, " ") + "|\n" + horizontalBoarder + "\n"
    for j in range(len(startOrders[i])):
      startOrderTable += "|" + str(j+1).center(3, " ")
      startOrderTable += "|" + startOrders[i][j].value.center(driverWidth, " ")
      startOrderTable += "|" + reserves[i][j].value.center(reserveDriverWidth, " ") + "|\n"
    startOrderTable += horizontalBoarder
    startOrders[i] = startOrderTable
      
  for startOrder in startOrders:
    try:
      await startOrderChannel.send ("```" + startOrder + "```")
    except TypeError:
      continue
  await startOrderChannel.send("```" + reserveTable + "```")
  moBotMessages.append(await message.channel.send("```Updated Start Orders```"))
  time.sleep(3)
  for i in moBotMessages:
    await i.delete()
# end getStartOrders

async def getMissingLaps(message):
  await message.delete()
  missingDrivers = []
  members = message.guild.members
  workbook = await openSpreadsheet()
  qualifying = workbook.worksheet("Qualifying")
  drivers = qualifying.range("C3:C120")
  driverNames = []
  for i in range(0, len(drivers)):
    if (drivers[i].value != ""):
      driverNames.append(drivers[i].value)
      
  staffCount = 0
  outsiderCount = 0

  for member in members:    
    roles = []
    for role in member.roles:
      roles.append(role.name.lower())
      
    memberName = member.nick
    if (memberName == None):
      memberName = member.name
    if (not (member.bot) and memberName not in driverNames):
       if ("staff" not in roles and "peeker" not in roles):
          missingDrivers.append(member)
       if ("peeker" in roles):
        outsiderCount += 1
       elif ("staff" in roles):
        staffCount += 1
      
      
  reply = ""
  for member in missingDrivers:
    reply += "<@" + str(member.id) + "> "
  await message.channel.send(reply)
  await message.channel.send("Laps Missing: " + str(len(missingDrivers)) + "\nLaps Inputted: " + str(len(driverNames)) + "\nStaff Excluded: " + str(staffCount) + "\nPeeker Excluded: " + str(outsiderCount))
# end getMissingLaps
  
async def getNonVoters(message):
  await message.delete()
  nonVoters = []
  members = message.guild.members
  workbook = await openSpreadsheet()
  trackVoting = workbook.worksheet("Track Voting")
  voters = trackVoting.range("D5:D122")
  voterIds = []
  for i in range(0, len(voters)):
    if (voters[i].value != ""):
      voterIds.append(voters[i].value)
    
  for member in members:
    roles = member.roles
    isPeeker = False
    for role in roles:
      if (role.name == "Peeker"):
        isPeeker = True
        break
    if (not (member.bot) and str(member.id) not in voterIds and not isPeeker):
      nonVoters.append(member)
  reply = ""
  for member in nonVoters:
    reply += "<@" + str(member.id) + "> "
  await message.channel.send(reply[:-1])
# end getNonVoters

async def getVotes(channel):
  workbook = await openSpreadsheet()
  trackVotingSheet = workbook.worksheet("Track Voting")
  voteCounts = trackVotingSheet.range("E3:H4")
  perfectVotes = trackVotingSheet.range("E1:H1")
  reply = "Current Vote Counts:\n"
  for i in range(0, 4):
    reply += "  - " + voteCounts[i].value + " - " + voteCounts[i+4].value + "\n"
  reply += "\nPerfect Votes:\n"
  for i in range(0, 4):
    reply += "  - " + voteCounts[i].value + " - " + perfectVotes[i].value + "\n"
  await channel.send("```" + reply + "```")
# end getVotes

async def clearReactionVotes(message):
  votingChannel = 528303438132543499
  voteMessageIds = [528307697133682698, 528307713403256852, 528307733456355331, 528307794936463374]
  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Clearing Vote Reactions```"))
  for msgId in voteMessageIds:
    msg = await message.guild.get_channel(votingChannel).fetch_message(msgId)
    reactions = msg.reactions
    for reaction in reactions:
      users = reaction.users()
      moBotID = 449247895858970624
      async for user in users:
        if (user.id != moBotID):
          await msg.remove_reaction(reaction.emoji, msg.guild.get_member(user.id))
  moBotMessages.append(await message.channel.send("```Vote Reactions Cleared```"))
  if (message.id not in voteMessageIds):    
    await message.delete()
  time.sleep(2)
  for i in moBotMessages:
    await i.delete()
# end clearReactionVotes

async def updateQualiStartTimes(message):
  msg = await message.channel.fetch_message(527685885790126111)
  reply = "```Qualifying Starts: 7th January 12:00am UK - " + str(datetime.strptime("6 Jan 2019 18:00", "%d %b %Y %H:%M") - datetime.now()) + "```"
  reply += "```Race Day: 27th January - " + str(datetime.strptime("27 Jan 2019 11:30", "%d %b %Y %H:%M") - datetime.now()).split(",")[0] + "```"
  await msg.edit(content=reply)
# end updateQualiStartTimes

async def helpQuote(message):
  await message.channel.send('```To add a quote, type @MoBot#0697 addquote "quote to add" - author\nTo have MoBot share a quote, type @MoBot#0697 sayquote; otherwise, one will be shared with a 1% chance everytime a message is sent in this chat.```')
# end helpQuote

async def sayQuote(message, rand):
  cotmQuotes = open("CotmQuotes.txt", "r")
  quotes = cotmQuotes.readlines()
  cotmChat = 527156400908926978
  if (rand == 0 and message.channel.id == cotmChat): # rand must be 0, trigger message must be in cotm guild but not in bot help
    rand = int(random.random() * 1000) % len(quotes)
    await message.channel.send(quotes[rand][:-1]) # cotm chat channel
# end sayQuote

async def addQuote(message):
  quote = ""
  by = ""
  quote = '"' + (message.content).split('"')[1] + '"'
  by = (message.content).split('"')[2].split("-")[1].strip()
  if (quote != "" and by != ""):
    cotmQuotes = open("CotmQuotes.txt", "a")
    cotmQuotes.write(quote + " - " + by + "\n")
    cotmQuotes.close()
    await message.channel.send("```Quote added.\nTo trigger a quote to be shared, type @MoBot#0697 sayquote; otherwise, one will be shared with a 1% chance everytime a message is sent in this chat.```")
  else:
    await message.channel.send('```To add a quote, type @MoBot#0697 addquote "quote to add" - author')
# end addQuote

async def newWeek(message):
  workbook = await openSpreadsheet()
  snapshotTemplateSheet = workbook.worksheet("Snapshot Template")
  referencesSheet = workbook.worksheet("References")
  standingsSheet = workbook.worksheet("Standings")
  rostersSheet = workbook.worksheet("Division Rosters")
  weeklyInformationSheet = workbook.worksheet("Weekly Information")
  trackVotingSheet = workbook.worksheet("Track Voting")
  promosDemosSheet = workbook.worksheet("Promos/Demos")
  divisionRostersSheet = workbook.worksheet("Division Rosters")
  driverSkillRatingSheet = workbook.worksheet("Universal Driver Skill Rating")
  
  # create new snapshot sheet
  weekNum = referencesSheet.acell("B21").value
  numSheets = len(workbook.worksheets())
  newSnapshotSheet = workbook.duplicate_sheet(snapshotTemplateSheet.id,insert_sheet_index=(numSheets-1),new_sheet_name="Week " + str(weekNum) + " Snapshot")
  
  # copy standings sheet values
  standings = standingsSheet.range("B5:M124")
  newSnapshotStandings = newSnapshotSheet.range("B2:M121")
  for i in range(len(newSnapshotStandings)):
    newSnapshotStandings[i].value = standings[i].value
  newSnapshotSheet.update_cells(newSnapshotStandings, value_input_option="USER_ENTERED")
  
  # copy division rosters
  rosters = rostersSheet.range("B8:S145")
  newSnapshotRosters = newSnapshotSheet.range("O2:AF139")
  for i in range(len(newSnapshotRosters)):
    newSnapshotRosters[i].value = rosters[i].value
  newSnapshotSheet.update_cells(newSnapshotRosters, value_input_option="USER_ENTERED")
  
  # copy weekly information
  weeklyInformation = weeklyInformationSheet.range("B2:N23")
  newSnapshotWeeklyInformation = newSnapshotSheet.range("AH2:AT23")
  for i in range(len(newSnapshotWeeklyInformation)):
    newSnapshotWeeklyInformation[i].value = weeklyInformation[i].value
  newSnapshotSheet.update_cells(newSnapshotWeeklyInformation, value_input_option="USER_ENTERED")
  
  # copy track voting
  trackVoting = trackVotingSheet.range("B1:H122")
  newSnapshotTrackVoting = newSnapshotSheet.range("AV1:BB122")
  for i in range(len(newSnapshotTrackVoting)):
    newSnapshotTrackVoting[i].value = trackVoting[i].value
  newSnapshotSheet.update_cells(newSnapshotTrackVoting, value_input_option="USER_ENTERED")
  
  # update week number
  currentWeekCell = referencesSheet.acell("B21").value
  currentWeekCell = int(currentWeekCell) + 1
  referencesSheet.update_acell("B21", currentWeekCell)
  
  # clear weekly information
  reservesTable = weeklyInformationSheet.range("C4:D23")
  reservesTable = await clearContents(reservesTable)
  weeklyInformationSheet.update_cells(reservesTable, value_input_option="USER_ENTERED")
  pitMarshallsTable = weeklyInformationSheet.range("G17:H23")
  pitMarshallsTable = await clearContents(pitMarshallsTable)
  weeklyInformationSheet.update_cells(pitMarshallsTable, value_input_option="USER_ENTERED")
  vehicleSelectionTable = weeklyInformationSheet.range("K4:K10")
  vehicleSelectionTable = await clearContents(vehicleSelectionTable)
  weeklyInformationSheet.update_cells(vehicleSelectionTable, value_input_option="USER_ENTERED")
  trackLinkCell = weeklyInformationSheet.acell("H12").value
  trackLinkCell = '=HYPERLINK("Link", "Track Link - TBD")'
  weeklyInformationSheet.update_acell("H12", trackLinkCell)
  
  # clear track voting
  trackVotingTable = trackVotingSheet.range("C5:H122")
  trackVotingTable = await clearContents(trackVotingTable)
  trackVotingSheet.update_cells(trackVotingTable, value_input_option="USER_ENTERED")
  
  # clear division rosters
  topRow = 10
  bottomRow = 24
  for i in range(7):
    raceTime = divisionRostersSheet.range(topRow, 10, bottomRow, 10)
    fastestLap = divisionRostersSheet.range(topRow, 13, bottomRow, 13)
    raceTime = await clearContents(raceTime)
    fastestLap = await clearContents(fastestLap)
    divisionRostersSheet.update_cells(raceTime, value_input_option="USER_ENTERED")
    divisionRostersSheet.update_cells(fastestLap, value_input_option="USER_ENTERED")
    topRow += 18
    if (i < 6):
      bottomRow += 18
    else:
      bottomRow += 31
      
  # clear standings sheet
  divList = standingsSheet.range("C7:C96")
  bottomDiv = standingsSheet.range("L7:L34")
  divList = await clearContents(divList)
  bottomDiv = await clearContents(bottomDiv)
  standingsSheet.update_cells(divList, value_input_option="USER_ENTERED")
  standingsSheet.update_cells(bottomDiv, value_input_option="USER_ENTERED")
  
  # update standings sheet
  promosDemos = [["", promosDemosSheet.range("C4:C13"), promosDemosSheet.range("D4:D13")],
                [promosDemosSheet.range("F4:F13"), promosDemosSheet.range("G4:G13"), promosDemosSheet.range("H4:H13")],
                [promosDemosSheet.range("J4:J13"), promosDemosSheet.range("K4:K13"), promosDemosSheet.range("L4:L13")],
                [promosDemosSheet.range("B17:B26"), promosDemosSheet.range("C17:C26"), promosDemosSheet.range("D17:D26")],
                [promosDemosSheet.range("F17:F26"), promosDemosSheet.range("G17:G26"), promosDemosSheet.range("H17:H26")],
                [promosDemosSheet.range("J17:J26"), promosDemosSheet.range("K17:K26"), promosDemosSheet.range("L17:L26")],
                [promosDemosSheet.range("N4:N31"), promosDemosSheet.range("O4:O31"), ""]]
                
  divs = []
  
  for i in range(len(promosDemos)):
    if (promosDemos[i][1][0].value != ""):
      divs.append([])
  
  for i in range(len(divs)):
    # if d1
    if (i == 0):
      # stayd in div
      for j in range(len(promosDemos[i][1])):
        if (promosDemos[i][1][j].value != ""):
          divs[i].append(promosDemos[i][1][j].value)
      # promos
      for j in range(len(promosDemos[i+1][0])):
          if (promosDemos[i+1][0][j].value != ""):
            divs[i].append(promosDemos[i+1][0][j].value)
          
    # if middle div
    if (i != 0 and i < len(divs)-2):
      # stayd in div
      for j in range(len(promosDemos[i][1])):
        if (promosDemos[i][1][j].value != ""):
          divs[i].append(promosDemos[i][1][j].value)
      # demos
      for j in range(len(promosDemos[i-1][2])):
        if (promosDemos[i-1][2][j].value != ""):
          divs[i].append(promosDemos[i-1][2][j].value)
      # promos
      for j in range(len(promosDemos[i+1][0])):
        if (promosDemos[i+1][0][j].value != ""):
          divs[i].append(promosDemos[i+1][0][j].value)
    
    # if 2nd to last div
    if (i == len(divs)-2):
      # stayd in div
      for j in range(len(promosDemos[i][1])):
        if (promosDemos[i][1][j].value != ""):
          divs[i].append(promosDemos[i][1][j].value)
      # demos
      for j in range(len(promosDemos[i-1][2])):
        if (promosDemos[i-1][2][j].value != ""):
          divs[i].append(promosDemos[i-1][2][j].value)
      # promos
      for j in range(len(promosDemos[-1][0])):
        if (promosDemos[-1][0][j].value != ""):
          divs[i].append(promosDemos[-1][0][j].value)
    
    # if last div
    if (i == len(divs)-1):
      # stayd in div
      for j in range(len(promosDemos[-1][1])):
        if (promosDemos[-1][1][j].value != ""):
          divs[i].append(promosDemos[-1][1][j].value)
      # demos
      for j in range(len(promosDemos[i-1][2])):
        if (promosDemos[i-1][2][j].value != ""):
          divs[i].append(promosDemos[i-1][2][j].value)

  # main div list
  divs.append([])
  for i in range(len(divs)-2):
    for j in range(len(divs[i])):
      divs[-1].append(divs[i][j])
      
  # set up for update
  divList = standingsSheet.range("C7:C96")
  bottomDiv = standingsSheet.range("L7:L34")
  for i in range(len(divs[-1])):
    divList[i].value = divs[-1][i]
  for i in range(len(divs[-2])):
    bottomDiv[i].value = divs[-2][i]
    
  # update standings sheet    
  standingsSheet.update_cells(divList, value_input_option="USER_ENTERED")
  standingsSheet.update_cells(bottomDiv, value_input_option="USER_ENTERED")
  
  # update Universal Driver Skill Rating
  timeTable1 = driverSkillRatingSheet.range("AD6:AH12")
  timeTable2 = driverSkillRatingSheet.range("AD17:AH23")
  
  for i in range(0, len(timeTable1), 5):
    timeTable1[i].value = timeTable2[i].value
    timeTable1[i+2].value = timeTable2[i+2].value
    timeTable1[i+3].value = timeTable2[i+3].value
    timeTable1[i+4].value = timeTable2[i+4].value
    timeTable2[i].value = ""
    timeTable2[i+3].value = ""
    timeTable2[i+4].value = ""
  
  driverSkillRatingSheet.update_cells(timeTable1, value_input_option="USER_ENTERED")
  driverSkillRatingSheet.update_cells(timeTable2, value_input_option="USER_ENTERED")
    
  # remove reserve role from all members
  divUpdateChannel = message.guild.get_channel(527319768911314944)
  for member in message.guild.members:
    for role in member.roles:
      if ("Reserve" in role.name):
        await member.remove_roles(role)
        await divUpdateChannel.send("<@" + str(member.id) + "> has been removed from " + role.name + ".")
        
  # update driver roles in server
  await updateDriverRoles(message)
  # update div list in server
  await updateDivList(message)
  # update start orders in server
  await updateStartOrders(message)
# end newWeek

async def updateDivListOLD(message):
  workbook = await openSpreadsheet()
  standingsSheet = workbook.worksheet("Standings")
  driverHistorySheet = workbook.worksheet("Driver History")
  divListChannel = message.guild.get_channel(527226061100941312)
  
  moBotMessages = []
  updateMsg = await divListChannel.fetch_message(535553787948171284)
  history = divListChannel.history(after=updateMsg)
  async for msg in history:
    await msg.delete()
  moBotMessages.append(await message.channel.send("```Updating Division List...```"))
  
  # get d1-6 from standings sheet
  topDivs = standingsSheet.range("C7:C96")
  # get d7 (bottom div) from standings sheet
  bottomDiv = standingsSheet.range("L7:L34")
  # get drivers from driver history (alphabetical order)
  driverList = driverHistorySheet.range("C4:D153")
  
  replys = [[], []]
  
  # generate reply (sorted by div)
  sortedByDiv = [[], [], [], [], [], [], []]
  currentDiv = 0
  for i in range(0, len(topDivs)):
    currentDiv = int((i + 15) / 15)
    sortedByDiv[currentDiv - 1].append(topDivs[i].value)
    
  for i in range(0, len(bottomDiv)):
    sortedByDiv[6].append(bottomDiv[i].value)
    
  
  emptyDivs = 0
  for i in range(len(sortedByDiv)):
    reply = ""
    if (sortedByDiv[i][0] != ""):
      reply = "Division " + str(i - emptyDivs + 1) + ":\n"
      for j in range(len(sortedByDiv[i])):
        if (sortedByDiv[i][j] != ""):
          reply += "  " + sortedByDiv[i][j] + "\n"
      
      replys[1].append("```" + reply + "```")
    else:
      emptyDivs += 1
  
  replys[0].append("```Division List (Sorted by Gamertag):```")
  reply = "```"
  for i in range(0, len(driverList), 2):
    if (i % 15 == 0 and i != 0):
      if (reply != "```"):
        replys[0].append(reply[:-1] + "```")
      reply = "```"
    if (driverList[i].value != ""):
      reply += driverList[i+1].value + " - " + driverList[i].value + "\n"
  if (reply != "```"):
    replys[0].append(reply + "```")
  replys[0][len(replys[0])-1] = replys[0][len(replys[0])-1] + "\n\n```Division List (Sorted by Division):```"
  
  for i in range(len(replys)):
    for j in range(len(replys[i])):
      await divListChannel.send(replys[i][j])
  
  moBotMessages.append(await message.channel.send("```Division List Updated```"))
  time.sleep(3)
  for i in moBotMessages:
    await i.delete()
# end updateDivList

async def clearContents(cells):
  for i in range(len(cells)):
    cells[i].value = ""
  return cells
# end clearContents

async def updateQualiStandings(message):
  moBotMessages = []
  qualiChannel = message.guild.get_channel(527226287828369410)
  lastUpdatedMsg = await qualiChannel.fetch_message(527321745968070689)
  history = qualiChannel.history(after=await qualiChannel.fetch_message(527321745968070689))
  async for msg in history:
    await msg.delete()
  moBotMessages.append(await message.channel.send("```Updating Quali Standings...```"))
  
  workbook = await openSpreadsheet()
  qualiSheet = workbook.worksheet("Qualifying")
  qualiTable = qualiSheet.range("S3:U" + str(qualiSheet.row_count))
  
  driverWidth = 6
  for i in range(0, len(qualiTable), 3):
    if (len(qualiTable[i+1].value) > driverWidth):
      driverWidth = len(qualiTable[i+1].value)
      
  horizontalBoarder = ""
  for i in range(15 + driverWidth):
    horizontalBoarder += "-"
    
  replys = []
  
  header = horizontalBoarder + "\n"
  header += "|" + "Pos".center(3, ' ') + "|" + "Driver".center(driverWidth, ' ') + "|" + "Lap Time".center(8, ' ') + "|\n"
  header += horizontalBoarder + "\n"
  
  for i in range(0, 7):
    replys.append("")
    replys[i] = "```Division " + str(i+1) + ":\n" + header
  
  divNum = 1
  for i in range(0, len(qualiTable), 3):
    divNum = int(int(i/3) / 15) + 1
    if (len(qualiTable[i].value) > 0):
      replys[divNum-1] += "|" + qualiTable[i].value.center(3, ' ') + "|"
      replys[divNum-1] += qualiTable[i+1].value.center(driverWidth, ' ')
      replys[divNum-1] += "|" + qualiTable[i+2].value.center(8, ' ') + "|\n"
  for i in range(0, len(replys)):
    if (replys[i][-3] != "-"):
      replys[i] += horizontalBoarder + "```"
    else:
      replys[i] += "```"
      
  lastUpdated = "```To Update, Click Refresh Icon\n  Last Updated: " + (datetime.today() + timedelta(hours=6)).strftime("%a %H:%M:%S.%f")[:-3] + " UK" + "```"
  await lastUpdatedMsg.edit(content=lastUpdated)
  
  for i in range(0, len(replys)):
    await qualiChannel.send(replys[i])
  
  moBotMessages.append(await message.channel.send("```Quali Standings Updated```"))
  time.sleep(3)
  for i in moBotMessages:
    await i.delete()
# end updateQualiStandings

async def voting(message, payload, messageIds):
  one = "1⃣"
  two = "2⃣"
  three = "3⃣"
  four = "4⃣"
  check = "✅"
  inputUser  = payload.user_id
  user = message.guild.get_member(inputUser)
  votingLog = message.guild.get_channel(530284914071961619)
  messages = []
  moBotMessages = []
  if (payload.emoji.name == check):
    moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, checking your votes..."))
    for i in messageIds:
      msg = await message.channel.fetch_message(i)
      messages.append(msg)
      
    if (payload.emoji.name == check):
      await message.remove_reaction(payload.emoji, user)
      multiVotesForOneTracakMessage = False
      multiVotesForMultiTracakMessage = False
      voteValueCounts = [0, 0, 0, 0]
      voteValues = []
      for msg in messages:
        msgReactions = msg.reactions
        multiVotesForTracakCount = 0
        index = 0
        for reaction in msgReactions:
          if (reaction.emoji != check):
            users = reaction.users()
            async for user in users:
              if (user.id == inputUser):
                if (reaction.emoji == one):
                  voteValues.append(1)
                elif (reaction.emoji == two):
                  voteValues.append(2)
                elif (reaction.emoji == three):
                  voteValues.append(3)
                elif (reaction.emoji == four):
                  voteValues.append(4)
                await msg.remove_reaction(reaction.emoji, user)
                voteValueCounts[index] += 1 
                multiVotesForTracakCount += 1
              if (multiVotesForTracakCount >= 2):
                if (not multiVotesForOneTracakMessage):
                  moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you cannot have multiple values for the same option."))
                  
                  await votingLog.send("<@" + str(inputUser) + "> tried to vote with multiple values for the same option. -- " + str(voteValues))
                  multiVotesForOneTracakMessage = True
          index += 1
        if (max(voteValueCounts) > 1):
          if (not multiVotesForMultiTracakMessage):
            moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you cannot have the same value for multiple options."))
            
            await votingLog.send("<@" + str(inputUser) + "> tried to vote with the same value for multiple options. -- " + str(voteValues))
            multiVotesForMultiTracakMessage = True
        
      if (multiVotesForOneTracakMessage or multiVotesForMultiTracakMessage):
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, your votes have been cleared; try again."))
      elif (sum(voteValueCounts) < 4):
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you must vote for each option. Your votes have been cleared; try again."))
        
        await votingLog.send("<@" + str(inputUser) + "> tried to vote without voting for each option. -- " + str(voteValues))
      else:
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, submitting your votes..."))
        driver = message.guild.get_member(inputUser).nick
        if (driver == None):
          driver = message.guild.get_member(inputUser).name
        driverId = inputUser
        
        isPeeker = True
        for role in message.guild.get_member(driverId).roles:
          if ("Division" in role.name):
            isPeeker = False
          
        if (not isPeeker):
          workbook = await openSpreadsheet()
          trackVotingSheet = workbook.worksheet("Track Voting")
          alreadyVoted, count = await submitVote(trackVotingSheet, voteValues, driver, driverId)
          if (alreadyVoted):
            moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you have already voted. If you would like to edit your vote (for good reason), tag IStarki11er29I#2992."))
            
            await votingLog.send("<@" + str(inputUser) + "> tried to vote again after already voting. -- " + str(voteValues))
          else:
            voteCount = await message.channel.fetch_message(528322660606935040)
            await voteCount.edit(content="```Voters Voted: " + str(count) + "```")
            moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, your votes have been submitted. Thanks for voting!"))
        
            await votingLog.send("<@" + str(inputUser) + "> voted -- "  + str(voteValues))
            await getVotes(votingLog)
        else:
          moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, if you are not in a division, you cannot vote."))
        
      time.sleep(4)
  for i in moBotMessages:
    await i.delete()
# end voting

async def submitVote(trackVotingSheet, votes, driver, driverId):
  alreadyVoted = False
  count = 0
  driverFound = findDriver(trackVotingSheet.range("D5:D122"), str(driverId))
  votingTable = trackVotingSheet.range("C5:H122")
  if (driverFound > -1):
    for i in range(0, len(votingTable), 6):
      if (i / 6 == driverFound):
        alreadyVoted = True
  else:
    for i in range(0, len(votingTable), 6):
      if (len(votingTable[i].value) == 0):
        votingTable[i].value = driver
        votingTable[i+1].value = str(driverId)
        votingTable[i+2].value = votes[0]
        votingTable[i+3].value = votes[1]
        votingTable[i+4].value = votes[2]
        votingTable[i+5].value = votes[3]
        break
  if (not alreadyVoted):
    trackVotingSheet.update_cells(votingTable, value_input_option="USER_ENTERED")
    numVoters = trackVotingSheet.range("B5:B122")
    for i in range(0, len(numVoters)):
      if (numVoters[i].value != ""):
        count = int(numVoters[i].value)
  return alreadyVoted, count
# end submitVoteVote

async def compileDriverFromArgs(args, startIndex, finishIndex):
  driver = ""
  for i in range(startIndex, finishIndex):
    driver += args[i] + " "
  driver = driver[:-1] # remove trailing space
  return driver
# end compileDriver

async def getQualiPosition(message, driver, qualiTable, numCols):
  driverTime = ""
  driverAhead = ""
  driverAheadTime = ""
  driverAheadDif = ""
  position = ""
  division = ""
  fastestDivDriver = ""
  fastestDivTime = ""
  fastestDivTimeDif = ""
  fastestOverallDriver = qualiTable[1]
  fastestOverallTime = qualiTable[2]
  fastestOverallTimeDif = ""
  
  for i in range(0, len(qualiTable), numCols):
  
    position = int(qualiTable[i].value)
    division = int((position - 1) / 15) + 1
    
    if (qualiTable[i+1].value == driver):
      driverTime = qualiTable[i+2].value
      driverAheadDif = qualiTable[i+3].value
      fastestDivTimeDif = qualiTable[i+4].value
      fastestOverallTimeDif = qualiTable[i+5].value
      
    if ((position - 1) % 15 == 0):
      fastestDivDriver = qualiTable[i+1].value
      fastestDivTime = qualiTable[i+2].value
      
    if (i == 0):
      fastestOverallDriver = qualiTable[i+1].value
      fastestOverallTime = qualiTable[i+2].value
      
    if (position != 1):
      driverAhead = qualiTable[(i - 6) + 1].value
      driverAheadTime = qualiTable[(i - 6) + 2].value
    if (driverTime != ""):
      break
      
  if (str(position) == "11" or str(position) == "12" or str(position) == "13"):
      position = str(position) + "th"
  else:
    if (str(position)[-1] == "1"):
      position = str(position) + "st"
    elif (str(position)[-1] == "2"):
      position = str(position) + "nd"
    elif (str(position)[-1] == "3"):
      position = str(position) + "rd"
    else:
      position = str(position) + "th"
      
  divLeader = False
  if ((int(position[:-2]) - 1) % 15 == 0):
    divLeader = True
  reply = "```"
  reply += "Driver: " + driver
  reply += "\nTime: " + driverTime
  reply += "\nDivision: " + str(division)
  reply += "\nPosition: " + str(position)
  if (divLeader):
    reply += " (Division Leader)"
  if (position != "1st"): # if not leader
    reply += "\nDriver Ahead Time:\n  " + driverAheadTime + " set by " + driverAhead + " (Difference: " + driverAheadDif + ")"
  if (not divLeader): # if not div leader
    reply += "\nFastest Time In Division " + str(division) + ":\n  " + fastestDivTime + " set by " + fastestDivDriver + " (Difference: " + fastestDivTimeDif + ")"
  if (division != 1): # if not in d1
    reply += "\nFastest Overall Time:\n  " + fastestOverallTime + " set by " + fastestOverallDriver + " (Difference: " + fastestOverallTimeDif + ")"
  reply += "```"
  await message.channel.send(reply)
# end getQualiPosition
############# END OLD FUNCITONS #############

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