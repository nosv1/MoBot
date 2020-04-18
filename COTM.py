'''
NOTES FOR NEXT SEASON
Issues:
  Reserves:
    Manual Reserves - Use dates to order reserves in database
    Ping the resereve even if they are full time reserve
    Show if a reserve was requested
  Voting:
    Get more fellers to vote 
    Better voting code
  General Information:
    Easier to find slightly less information
      better faq?

'''

import discord
from datetime import datetime, timedelta
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import asyncio
import operator
import traceback
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import os
import sys
import re

import SecretStuff

import RandomSupport

GUILD_ID = 527156310366486529

# common member ids
mo = 405944496665133058
moBot = 449247895858970624
moBotTest = 476974462022189056

# common messages 
VOTING_EMBED = 620778154197385256
VOTING_CHECKMARK = 620778190767390721

# common channels
COTM_STREAMS = 527161746473877504
QUALIFYING = 607693838642970819
QUALI_SCREENSHOTS = 607694176133447680
START_ORDERS = 622484589465829376
STANDINGS = 622467542497099786
RESERVE_STANDINGS = 628747564480462858
ROOKIE_STANDINGS = 628758523643166761
LEAST_IMPROVED = 628758491477180446
TOT_POS_GAIN_LOST = 628766947709812756
DIVISION_UPDATES = 527319768911314944
RESERVE_SEEKING = 620811051335680013
ACTION_LOG = 527355464216739866
PIT_MARSHALL_SIGNUP = 605985462502555679
MINI_CHAMPIONSHIPS = 630610458029588480
DRIVER_HISTORY = 631556653174620160
EVENT_CHAT = 527156400908926978
VOTING = 608472349712580608
VOTING_LOG = 530284914071961619

# common emojis
X_EMOJI = "❌"
CHECKMARK_EMOJI = "✅"
ARROWS_COUNTERCLOCKWISE_EMOJI  = "🔄"
THUMBSUP_EMOJI = "👍"
WAVE_EMOJI = "👋"
FIST_EMOJI = "✊"
CROWN = "👑"
WRENCH = "🔧"
GLOBE_WITH_LINES = "🌐"

# common roles
EVERYONE = 527156310366486529
PEEKER_ROLE = 534230087244185601
CHILDREN_ROLE = 529112570448183296

spaceChar = "⠀"
logos = {
  "cotmFaded" : "https://i.gyazo.com/e720604af6507b3fc905083e8c92edf7.png",
  "cotm_white_trans" : "https://i.gyazo.com/226faa8d1f43c56d579faa9d81ff9e86.png",
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

  if str(moBot) in args[0]:
    if "newsignup" in args[1]:
      await handleFormSignup(message)
    if (args[1] == "quali" and authorPerms.administrator):
      await submitQualiTime(message, qualifyingChannel, None, None, client)
    if (args[1] == "reserve" and authorPerms.administrator):
      await setManualReserve(message)
    elif (args[1] == "history"):
      await message.channel.trigger_typing()
      if (message.content.count("<@") > 1):
        driverID = int(message.content.split("<@")[-1].split(">")[0].replace("!", ""))
      else:
        driverID = message.author.id
      await updateDriverHistory(message, driverID, await openSpreadsheet())
    if (message.author.id == mo):
      try:
        if (args[1] == "update"):
          if (args[2] == "standings"):
            await message.channel.trigger_typing()
            await updateStandings(message.guild, await openSpreadsheet())
            await message.delete()
          elif (args[2] == "start" and args[3] == "orders"):
            await message.channel.trigger_typing()
            await updateStartOrders(message.guild, await openSpreadsheet())
            await message.delete()
          elif (args[2] == "divlist"):
            await message.channel.trigger_typing()
            await updateDriverRoles(message.guild, getDivList(await openSpreadsheet()))
            await message.delete()
          elif (args[2] == "driver" and args[3] == "history"):
            await updateDriverHistory(message, None, await openSpreadsheet())
        elif (args[1] == "reset"):
          if (args[2] == "pitmarshalls"):
            await message.channel.trigger_typing()
            await resetPitMarshalls(message.guild)
            await message.delete()
          elif (args[2] == "reserves"):
            await message.channel.trigger_typing()
            await resetReserves(message.guild)
            await message.delete()
        elif (args[1] == "add" and args[2] == "driver"):
          await message.channel.trigger_typing()
          await addDriver(message)
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
      if (message.id == VOTING_CHECKMARK): # track-voting
        await openVotingChannel(message, member)
        await message.remove_reaction(payload.emoji.name, member)

    if re.match(r"(voting)(?!.*-log)", message.channel.name): # is voting-name channel
      if payload.emoji.name in RandomSupport.numberEmojis[0:5]:
        await votePlaced(message, member)
      elif payload.emoji.name == X_EMOJI:
        await resetVotes(message)
      elif payload.emoji.name == CHECKMARK_EMOJI:
        await submitVotes(message, member)

    if (message.id == 620811567210037253): # message id for Reserves Embed
      if (payload.emoji.name == WAVE_EMOJI):
        await reserveNeeded(message, member)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveAvailable(message, member, payload, client)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        if (member.id == mo):
          workbook = await openSpreadsheet()
          await getReserves(workbook)
          await updateStartOrders(message.guild, workbook)
          await message.channel.send(content="Remember to remove any reserve roles, if necessary.\n*(deleting in 10 sec)*", delete_after=10)
          await message.remove_reaction(payload.emoji.name, member)

    if (message.id == 622137318513442816): # message id for streamer embed
      if (payload.emoji.name in ["Twitch", "Mixer", "Youtube"]):
        await addStreamer(message, member, payload, client)
      if (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        await refreshStreamers(message, await openSpreadsheet())
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

async def memberRemove(member, client):
  guild = client.get_guild(GUILD_ID)
  mo = guild.get_member(mo)
  channel = guild.get_channel(EVENT_CHAT)
  await channel.send("%s has remaining :eyes: Was he important?\n||%s||" % (member.mention, mo.mention))
# end memberRemove



async def handleFormSignup(message):
  if not message.webhook_id or True: # is not from webhook
    return

  args = message.content.split("[")[1:]
  number = args[0].split("]")[0]
  discord_name = args[1].split("]")[0]
  gamertag = args[2].split("]")[0]
  was_edited = args[3].split("]")[0] == "true"

  if was_edited:
    return

  for member in message.guild.members:
    if f"{member.name}#{member.discriminator}" == discord_name:
      await member.edit(nick=gamertag)

      embed = discord.Embed()
      embed.color = int("0xFFFFFE", 16)
      embed.set_author(name=f"Child #{number}", icon_url=logos["cotm_white_trans"])
      embed.description = f"We welcome {member.mention}."

      await message.guild.get_channel(EVENT_CHAT).send(embed=embed)
      await member.remove_roles(message.guild.get_role(PEEKER_ROLE))
      await member.add_roles(message.guild.get_role(CHILDREN_ROLE))
      return
# end handleFormSignup



async def openVotingChannel(message, member):
  await message.channel.trigger_typing()

  guild = message.guild
  category_channels = message.channel.category.channels

  for channel in category_channels:
    if member.display_name.lower() in channel.name.replace("-", " "): # channel already created
      await message.channel.send(f"{channel.mention}", delete_after=10)
      return

  channel = await guild.create_text_channel(
    f"voting-{member.display_name}",
    overwrites = {
      guild.get_role(EVERYONE) : discord.PermissionOverwrite(read_messages=False),
      member : discord.PermissionOverwrite(
        read_messages=True,
        send_messages=False
      ),
    },
    category=message.channel.category,
    position=sys.maxsize
  )
  msg = await channel.send(
    content=member.mention,
    embed=(await createOgVotingEmbed(message))
  )
  await msg.add_reaction(X_EMOJI)
  for emoji in RandomSupport.numberEmojis[0:5]:
    await msg.add_reaction(emoji)
# end openVotingChannel

async def createOgVotingEmbed(message):

  embed = discord.Embed()
  embed.color = int("0xFFFFFE", 16)
  embed.set_footer(text="Please do not spam the number-buttons... If there are issues, contact @Mo#9991 :)")
  embed.set_author(
    name="Voting",
    icon_url=logos["cotm_white_trans"],
    url="https://google.com/current_option=1/1=0/2=0/3=0/4=0/"
  )

  embed.add_field(
    name="**Instructions**",
    value=f"Select the number-button below to cast your vote. You have 4 votes to spend total. Spread them out, or stack them all on one option. Click the {X_EMOJI} to clear all your votes.\n{spaceChar}",
    inline=False
  )

  og_voting_embed = await (message.guild.get_channel(VOTING)).fetch_message(VOTING_EMBED)
  options = RandomSupport.getValueFromField(
    og_voting_embed.embeds[0], 
    "Options"
  ).split("\n")
  options = [f"{i+1}. {option} - 0" for i, option in enumerate(options) if spaceChar not in option]
  embed.add_field(
    name="**Options**", 
    value= "\n".join(options) + "\n" + spaceChar,
    inline=False
  )

  embed.add_field(
    name="**Current Option**",
    value=f"{options[0]}\n{spaceChar}",
    inline=False
  )

  embed.add_field(
    name="**Votes Remaining**",
    value="4",
    inline=False
  )

  return embed
# end createOgVotingEmbed

async def resetVotes(message):
  await message.clear_reactions()
  await message.edit(embed=(await createOgVotingEmbed(message)))
  await message.add_reaction(X_EMOJI)
  for emoji in RandomSupport.numberEmojis[0:5]:
    await message.add_reaction(emoji)
# end resetVotes

async def votePlaced(message, member):
  await message.channel.trigger_typing()

  embed = message.embeds[0]
  url = embed.author.url
  reactions = message.reactions

  current_option_number = int(RandomSupport.getDetailFromURL(url, "current_option"))
  votes_remaining = int(RandomSupport.getValueFromField(embed, "Votes Remaining"))
  
  vote = None
  for r in reactions:
    if r.emoji == X_EMOJI:
      continue
    
    number = RandomSupport.numberEmojis.index(r.emoji)
    if len(await r.users().flatten()) > 1 and not vote: # vote hasn't been found
      vote = number
      votes_remaining = votes_remaining - vote
      break

  new_vote = vote + int(RandomSupport.getDetailFromURL(url, str(current_option_number)))
  embed = RandomSupport.updateDetailInURL( # update vote count for option
    embed, 
    str(current_option_number),
    str(new_vote)
  )

  options = RandomSupport.getValueFromField(embed, "Options")
  options = options.split("\n")
  options[current_option_number-1] = options[current_option_number-1][:-1] + str(new_vote)
  #re.sub(r"( - \d$)", options[current_option_number-1], f" - {new_vote}")) # not sure why this does't work
  embed = RandomSupport.updateFieldValue(embed, "Options", "\n".join(options)) # update options with correct vote counts

  embed = RandomSupport.updateFieldValue(embed, "Votes Remaining", str(votes_remaining)) # update votes remaining

  option_numbers = [1, 2, 3, 4]
  new_option_number = option_numbers[option_numbers.index(current_option_number)-3]
  embed = RandomSupport.updateDetailInURL(embed, "current_option", str(new_option_number)) # increment by 1, update current option number

  embed = RandomSupport.updateFieldValue( # update current option
    embed, "Current Option", 
    f"{options[new_option_number-1]}\n{spaceChar}"
  )

  if votes_remaining == 0:
    embed = RandomSupport.updateFieldValue(
      embed, 
      "Votes ", 
      f"You have no votes remaining. Click the {CHECKMARK_EMOJI} to submit."
    )

  await message.edit(embed=embed)

  for r in reactions:
    if r.emoji == X_EMOJI:
      continue
    if r.emoji == CHECKMARK_EMOJI:
      continue

    number = RandomSupport.numberEmojis.index(r.emoji)
    await message.remove_reaction(r.emoji, member)
    if number > votes_remaining or votes_remaining == 0:
      await message.remove_reaction(r.emoji, message.guild.get_member(moBot))

  if votes_remaining == 0:
    await message.add_reaction(CHECKMARK_EMOJI)
# end votesPlaced

async def submitVotes(message, member):
  await message.channel.trigger_typing()

  try:
    workbook = await openSpreadsheet()
    sheets = workbook.worksheets()
    sheet = [sheet for sheet in sheets if sheet.id == 242811195][0] # Voting Sheet
    r = sheet.range(f"C4:G{sheet.row_count}")
    user_found = findDriver(r, member.display_name)

    if user_found != -1:
      await message.channel.send(f"**Cancelling Submssion**\nYou cannot vote more than once. If this is a mistake, contact <@{mo}>.")
      await message.clear_reactions()
      return

    for i, cell in enumerate(r):

      if cell.value == "": # append vote
        vote_embed = message.embeds[0]
        votes = [int(RandomSupport.getDetailFromURL(vote_embed.author.url, str(j))) for j in range(1, 5)]
        r[i].value = member.display_name
        for j in range(1, 5):
          r[i+j].value = votes[j-1]
        sheet.update_cells(r, value_input_option="USER_ENTERED")
        await message.channel.send("**Votes Submitted**\nThank you for voting. :)")

        totals = [0] * 4 # getting totals
        for j in range(0, len(r), 5):
          if r[j].value == "":
            break

          for k in range(4):
            totals[k] += int(r[j+k+1].value)
        
        log_embed = discord.Embed() # send to log
        log_embed.color = int("0xFFFFFE", 16)
        log_embed.set_author(name="Vote Submission", icon_url=logos["cotm_white_trans"])
        options = RandomSupport.getValueFromField(vote_embed, "Options")
        log_embed.add_field(
          name=member.display_name,
          value=options,
          inline=False
        )
        options = options.split("\n")
        for j in range(0, len(options)-1): # space char at end
          options[j] = options[j][:-1] + str(totals[j])

        log_embed.add_field(
          name="Votes",
          value="\n".join(options),
          inline=False
        )

        count = RandomSupport.numberToEmojiNumbers(i // 5 + 1)
        log_embed.add_field(
          name="Count",
          value=count
        )

        voting_log = message.guild.get_channel(VOTING_LOG)
        await voting_log.send(embed=log_embed)

        voting = message.guild.get_channel(VOTING) # update total voters
        voting_msg = await voting.fetch_message(VOTING_EMBED)
        voting_embed = voting_msg.embeds[0]
        voting_embed = RandomSupport.updateFieldValue(voting_embed, "Total Voters", count)
        await voting_msg.edit(embed=voting_embed)

        await message.channel.delete() # delete channel
        break
  except gspread.exceptions.APIError:
    await message.channel.send(f"**<@{member.id}>, there were technical difficulties submitting your vote. Wait a copule seconds, then click the {CHECKMARK_EMOJI} again.**", delete_after=10)
    return
# end submitVotes




async def addDriver(message):
  divisionUpdatesChannel = message.guild.get_channel(DIVISION_UPDATES)

  workbook = await openSpreadsheet()

  moBotMessage = await message.channel.send("*Getting Number of Divisions*")
  driverHistorySheet = workbook.worksheet("Driver History")
  numberOfDivs = driverHistorySheet.range("D1:D1")[0].value

  await moBotMessage.edit(content="*Getting Driver ID and Gamertag*")
  driverID = message.content.split("<@")[-1].split(">")[0].replace("!", "")
  driverGT = message.content.split(driverID)[-1].split(">")[-1].strip()
  driverMember = message.guild.get_member(int(driverID))
  
  await moBotMessage.edit(content="*Saving Driver ID and Gamertag*")
  driversRange, driversSheet = getDriversRange(workbook)
  driverIndex = findDriver(driversRange, driverID) 
  if (driverIndex == -1):
    for i in range(len(driversRange)):
      if (driversRange[i].value == ""):
        driversRange[i].value = str(driverID)
        driversRange[i+1].value = driverGT
        break
  else:
    driversRange[driverIndex+1].value = driverGT
  driversSheet.update_cells(driversRange, value_input_option="USER_ENTERED")

  await moBotMessage.edit(content="*Adding Driver Gamertag to Standings*")
  standingsSheet = workbook.worksheet("Standings")
  standingsRange = standingsSheet.range("C4:C%s" % standingsSheet.row_count)
  if (findDriver(standingsRange, driverGT) == -1):
    for i in range(len(standingsRange)-1, 0-1, -1):
      if (standingsRange[i-1].value != ""):
        standingsRange[i].value = driverGT

        await driverMember.edit(nick="[D%s] %s" % (numberOfDivs, driverGT))

        for role in message.guild.roles:
          if (role.name == "Division %s" % numberOfDivs):
            await driverMember.add_roles(role)
            await divisionUpdatesChannel.send("%s has been added to %s." % (driverMember.mention, role.name))
          elif (role.name == "COTM"):
            await driverMember.add_roles(role)
          elif (role.name == "Peeker"):
            await driverMember.remove_roles(role)

        await message.channel.send("**Driver Added**\nRemember to update the standings and the start orders.")
        break
  else:
    await message.channel.send("**Cannot Add Driver**\nDriver is already in the standings.")

  await moBotMessage.delete()
  standingsSheet.update_cells(standingsRange, value_input_option="USER_ENTERED")
# end addDriver

async def resetPitMarshalls(guild):
  message = await guild.get_channel(PIT_MARSHALL_SIGNUP).fetch_message(622831151320662036)
  await message.clear_reactions()

  embed = message.embeds[0].to_dict()
  for i in range(len(embed["fields"])):
    if ("Division" in embed["fields"][i]["name"]):
      embed["fields"][i]["value"] = "Host -\nPit-Marshall -\n" + spaceChar

  for member in message.guild.members:
    for role in member.roles:
      if ("Pit-Marshalls" in role.name):
        await member.remove_roles(role)
        await message.channel.send("%s has been removed from Pit-Marshalls." % (member.mention), delete_after=3)
        break
  
  #await message.channel.purge(after=message)
  await message.edit(embed=discord.Embed().from_dict(embed))
  await message.add_reaction(CROWN)
  await message.add_reaction(WRENCH)
# end resetPitMarshalls

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

async def refreshStreamers(message, workbook):
  await message.channel.trigger_typing()

  class Streamer:
    def __init__(self, driverID, streamLink):
      self.member = message.guild.get_member(int(driverID))
      member = self.member

      reserveDivs = []
      for role in member.roles:
        if ("Reserve" in role.name):
          reserveDivs.append(role.name[-1])

      self.div = member.display_name.split("]")[0][-1]
      self.reserveDivs = reserveDivs
      self.streamLink = streamLink
  # end Streamer

  driversRange, driverSheet = getDriversRange(workbook)
  driverIDs = driverSheet.range("B3:B" + str(driverSheet.row_count))
  streamLinks = driverSheet.range("H3:H" + str(driverSheet.row_count))

  def getStreamers():
    streamers = []
    for i in range(len(streamLinks)):
      if (streamLinks[i].value != ""):
        try:
          streamers.append(Streamer(driverIDs[i].value, streamLinks[i].value))
        except AttributeError: # When member == None
          pass 
    return streamers
  # end getStreamers

  def getEmoji(streamLink):
    if ("twitch" in streamLink.lower()):
      return "<:Twitch:622139375282683914> "
    elif ("youtube" in streamLink.lower()):
      return "<:Youtube:622139522502754304>"
    elif ("mixer" in streamLink.lower()):
      return "<:Mixer:622139665306353675>"
  # end getEmoji

  embed = discord.Embed(
    color=int("0xd1d1d1", 16),
    description="Below are this season's streamers. If you wish to join this list, simply click the appropiate emoji below representing your streaming platform, then send your channel link."
  )
  embed.set_author(
    name="Children of the Mountain - Season 5",
    icon_url="https://i.gyazo.com/efe464c59dfdc7abde20b305e896ced8.png"
  )
  embed.set_footer(
    text="To add your channel, simply click a platform, and paste your channel link."
  )

  multiStreams = {}
  multiStreamLink = "https://multistre.am/"
  for i in range(1, 6):
    embed.add_field(
      name="Division %s:" % (str(i)),
      value="",
      inline=False
    )
    multiStreams[str(i)] = multiStreamLink

  embed = embed.to_dict()
  streamers = getStreamers()
  for i in range(len(embed["fields"])):
    for streamer in streamers:
      if (streamer.div in embed["fields"][i]["name"] or embed["fields"][i]["name"][-2] in streamer.reserveDivs):
        emoji = getEmoji(streamer.streamLink)
        try:
          embed["fields"][i]["value"] += "%s __[%s](%s)__\n" % (emoji, streamer.member.display_name, streamer.streamLink)
          if ("twitch" in emoji.lower()):
            multiStreams[str(i+1)] += streamer.streamLink.split("/")[-1] + "/"
        except AttributeError: # if a member leaves
          pass
    if (multiStreams[str(i+1)] != multiStreamLink):
      embed["fields"][i]["value"] += multiStreams[str(i+1)] + "\n"
    if (i != len(embed["fields"]) - 1):
      embed["fields"][i]["value"] += spaceChar
  await message.edit(embed=discord.Embed().from_dict(embed))
# end refreshStreamers

async def addStreamer(message, member, payload, client):
  await message.channel.trigger_typing()

  def checkMsg(msg):
    return msg.channel.id == message.channel.id and msg.author.id == payload.user_id
  # end checkMsg

  async def failed(moBotMessage):
    await message.channel.set_permissions(member, overwrite=None)
    await message.remove_reaction(payload.emoji.name, member)
    await moBotMessage.delete()
  # end failed

  try:
    await message.channel.set_permissions(member, read_messages=True, send_messages=True)
    moBotMessage = await message.channel.send(member.mention + ", please link your channel.\nEx. <https://twitch.tv/MoShots> *Must include the beginning 'http' bit*")
    msg = await client.wait_for("message", timeout=300, check=checkMsg)
    await message.channel.set_permissions(member, overwrite=None)
    link = msg.content if ("http" in msg.content) else None
    await moBotMessage.delete()
    await msg.delete()

  except asyncio.TimeoutError:
    await message.channel.send(content="**TIMED OUT**", delete_after=20)
    await failed(moBotMessage)
    return None

  if (link is None):
    await message.channel.send(member.mention + ", you did not provide a proper link. Link ex. <https://twitch.tv/moshots>.", delete_after=20)
    await failed(moBotMessage)
    return None
  
  workbook = await openSpreadsheet()
  driversRange, driverSheet = getDriversRange(workbook)
  driverIDs = driverSheet.range("B3:B" + str(driverSheet.row_count))
  streamLinks = driverSheet.range("H3:H" + str(driverSheet.row_count))

  for i in range(len(driverIDs)):
    if (driverIDs[i].value == str(member.id)):
      streamLinks[i].value = link
      driverSheet.update_cells(streamLinks, value_input_option="USER_ENTERED")
      await refreshStreamers(message, workbook)
      break
# end addStreamer

async def removeStreamer(message, member, payload):
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet()
  driversRange, driverSheet = getDriversRange(workbook)
  driverIDs = driverSheet.range("B3:B" + str(driverSheet.row_count))
  streamLinks = driverSheet.range("H3:H" + str(driverSheet.row_count))

  for i in range(len(driverIDs)):
    if (driverIDs[i].value == str(member.id)):
      streamLinks[i].value = ""
      driverSheet.update_cells(streamLinks, value_input_option="USER_ENTERED")
      await refreshStreamers(message, workbook)
      break
# end removeStreamer

async def memberStartedStreaming(member, client):
  try:
    message = await member.guild.get_channel(COTM_STREAMS).fetch_message(622137318513442816)
    streamEmbed = message.embeds[0]
    streamEmbed = streamEmbed.to_dict()

    twitchStreamers = streamEmbed["fields"][0]["value"]
    #multiStreams = streamEmbed["fields"][3]["value"]
  except:
    await client.get_member(mo).send(str(traceback.format_exc()))
# end startedStreaming

async def getReserveDiv(member):
  workbook = await openSpreadsheet()
  driversSheet = workbook.worksheet("Drivers")
  driversRange = driversSheet.range("B3:F" + str(driversSheet.row_count))
  for i in range(len(driversRange)):
    if (driversRange[i].value == str(member.id)):
      return int(driversRange[i+4].value)
  return -1
# end getReserveDiv

async def setManualReserve(message):
  reserve = message.content.split("for")[0].split("<@")[-1].split(">")[0].replace("!", "")
  driver = message.content.split("for")[-1].split("<@")[-1].split(">")[0].replace("!", "")

  reserve = message.guild.get_member(int(reserve))
  driver = message.guild.get_member(int(driver))

  msg = await message.guild.get_channel(RESERVE_SEEKING).fetch_message(620811567210037253)
  embed = msg.embeds[0]
  embed = embed.to_dict()
  embed["fields"][0]["value"] = "%s\n%s" % (driver.display_name, embed["fields"][0]["value"].replace(driver.display_name + "\n", ""))

  
  reserveDiv = driver.display_name.split("]")[0][-1]
  for i in range(len(embed["fields"])):
    if ("D%s" % reserveDiv in embed["fields"][i]["name"]):
      embed["fields"][i]["value"] = "%s\n%s" % (reserve.display_name, embed["fields"][i]["value"].replace(reserve.display_name + "\n", ""))
      break

  workbook = await openSpreadsheet()
  moBotMessage = await message.channel.send(content="**Setting Reserves Needed**")
  await setReservesNeeded(driver, embed["fields"][0]["value"], workbook)
  await moBotMessage.edit(content="**Setting Reserves Available**")
  await setReservesAvailable(embed, workbook)
  await moBotMessage.edit(content="**Updating Start Orders**")
  await updateStartOrders(message.guild, workbook)

  await msg.edit(embed=discord.Embed().from_dict(embed))
  await message.delete()
  await moBotMessage.delete()
# end setManualReserve

async def resetReserves(guild):
  message = await guild.get_channel(RESERVE_SEEKING).fetch_message(620811567210037253)
  divUpdatesChannel = guild.get_channel(DIVISION_UPDATES)
  embed = message.embeds[0].to_dict()
  embed["fields"][0]["value"] = spaceChar
  for i in range(len(embed["fields"])):
    if ("Available for" in embed["fields"][i]["name"]):
      embed["fields"][i]["value"] = spaceChar
  await message.edit(embed=discord.Embed().from_dict(embed))

  for member in guild.members:
    if ("[R]" not in member.display_name):
      for role in member.roles:
        if ("Reserve" in role.name):
          await member.remove_roles(role)
          await divUpdatesChannel.send("%s has been removed from %s." % (member.mention, role.name))

  await message.clear_reactions()
  await message.add_reaction(WAVE_EMOJI)
  await message.add_reaction(FIST_EMOJI)
# end resetReserves

async def reserveNeeded(message, member):
  embed = message.embeds[0].to_dict()
  reservesNeeded = embed["fields"][0]["value"][:-1].strip()
  if (member.display_name not in reservesNeeded):
    embed["fields"][0]["value"] = reservesNeeded + "\n" + member.display_name + "\n" + spaceChar
  await message.edit(embed=discord.Embed.from_dict(embed))

  workbook = await openSpreadsheet()
  await setReservesNeeded(member, embed["fields"][0]["value"], workbook)
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

    reserveMember = None  
    divs = []
    for reaction in moBotMessage.reactions:
      if (str(reaction.emoji) != CHECKMARK_EMOJI):
        async for user in reaction.users():
          if (user.id == member.id):
            reserveMember = member
            divs.append(str(reaction.emoji).split(":")[1][-1])
    if (divs != []):
      for i in range(len(embed["fields"])):
        for div in divs:
          if ("D" + div in embed["fields"][i]["name"]):
            if (reserveMember.display_name not in embed["fields"][i]["value"]):
              embed["fields"][i]["value"] = embed["fields"][i]["value"][:-1] + reserveMember.display_name + "\n" + spaceChar
      await message.edit(embed=discord.Embed.from_dict(embed))

      workbook = await openSpreadsheet()
      await setReservesAvailable(embed, workbook)
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
  for i in range(len(embed["fields"])):
    if ("Available" in embed["fields"][i]["name"]):
      newValue = ""
      value = embed["fields"][i]["value"][:-1].strip()
      for line in value.split("\n"):
        if (member.display_name not in line):
          newValue += line + "\n"
      newValue += spaceChar
      embed["fields"][i]["value"] = newValue
  await message.edit(embed=discord.Embed.from_dict(embed))
  
  for role in member.roles:
    if ("Reserve Division" in role.name and "[R]" not in member.display_name):
      await member.remove_roles(role)
      await message.guild.get_channel(DIVISION_UPDATES).send(member.mention + " has been removed from " + role.name)

  workbook = await openSpreadsheet()
  await setReservesAvailable(embed, workbook)
  await updateStartOrders(message.guild, workbook)
# end reserveNotAvailable

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

async def updateDriverRoles(guild, divList):
  divisionUpdateChannel = guild.get_channel(DIVISION_UPDATES)

  for div in divList:
    drivers = divList[div]
    for driver in drivers:
      driverMember = guild.get_member(int(driver.driverID))
      if (driverMember is None):
        continue
      else:
        for role in guild.roles:
          if (role.name == "Division " + str(driver.div)): # add correct div role
            hasRole = False
            for dRole in driverMember.roles:
              if (dRole == role):
                hasRole = True
                break
            if (not hasRole):
              await driverMember.add_roles(role)
              await driverMember.edit(nick="[D%s] %s" % (driver.div, driver.driverName))
              await divisionUpdateChannel.send(driverMember.mention + " has been added to " + role.name + ".")
            break
        for role in driverMember.roles:
          if ("Division" in role.name and "Reserve" not in role.name and str(driver.div) not in role.name): # remove other div roles
            await driverMember.remove_roles(role)
            await divisionUpdateChannel.send(driverMember.mention + " has been removed from " + role.name + ".")
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
      if (driver == None): # when there is an empty start position
        continue
      driverMember = guild.get_member(driver.driverID)
      try:
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
      except AttributeError: # when driverMember or reserveMember is None
        await guild.get_member(mo).send("**SOMEONE MAY HAVE LEFT COTM**\nDriver:%s\nReserve:%s" % (driver.driverID, driver.reserveID))
    startOrderEmbeds.append(embed)

  await startOrdersChannel.purge()
  for embed in startOrderEmbeds:
    try:
      await startOrdersChannel.send(embed=discord.Embed.from_dict(embed))
    except discord.errors.HTTPException: # when a division has no drivers
      pass
# end updateStartOrders

async def updateStandings(guild, workbook):
  standings = getStandings(workbook)

  purged = None
  for standing in standings:
    standingsChannel = guild.get_channel(standing.channelID)
    standingsEmbeds = []
    embed = discord.Embed(color=int("0xd1d1d1", 16))
    embed.set_author(name="Children of the Mountain - Season 5", icon_url=logos["cotmFaded"])
    embed.add_field(name=standing.name, value="Pos. Driver - %s" % (standing.specifier), inline=False)
    embed = embed.to_dict()
    standingsEmbeds.append(embed)

    for i in range(len(standing.standings)):
      if (i % 15 == 0):
        embed = discord.Embed(color=int("0xd1d1d1", 16))
        embed.add_field(name=("Pos. %d - %d" % (i+1, i+15)), value="", inline=False)
        embed = embed.to_dict()
        standingsEmbeds.append(embed)

      driverMember = guild.get_member(standing.standings[i].driverID)
      standingsEmbeds[len(standingsEmbeds)-1]["fields"][0]["value"] += ("%d. %s - %d" % (standing.standings[i].position, driverMember.display_name, standing.standings[i].specifierAmt)) + "\n"

    if (purged != standingsChannel.id): # to avoid purging the channel > 1 time
      await standingsChannel.purge()
      purged = standingsChannel.id
    for embed in standingsEmbeds:
      await standingsChannel.send(embed=discord.Embed.from_dict(embed))
# end updateStandings

async def createDriverHistoryChart(driver, driverMember, filePath):
  
  def autoLabel(values):
    if (type(values[0]) != mpl.lines.Line2D):
      for i in range(len(values)):
        value = values[i]
        height = value.get_height()
        ax.text(value.get_x() + value.get_width()/2., 1.05*height, '%d' % int(height), weight="bold", ha="center", va="bottom")
    else:
      line = values[0]
      x = line._x
      y = line._y
      for i in range(len(x)):
        height = y[i]
        ax.text(i+.05, 1.05*height, "%d" % int(height), weight="bold", ha="center", va="bottom")
    # end autoLabel

  ndx = np.arange(len(driver.divisions))

  textColor = "#839496"
  facecolor = "#33363B"
  gridColor = "#363942"
  mpl.rcParams["text.color"] = textColor
  mpl.rcParams["axes.labelcolor"] = textColor
  mpl.rcParams["xtick.color"] = textColor
  mpl.rcParams["ytick.color"] = textColor
  mpl.rcParams["legend.facecolor"] = facecolor
  mpl.rcParams["grid.color"] = textColor
  mpl.rcParams["grid.alpha"] = .2
  fig, ax = plt.subplots(facecolor=facecolor)
  ax.grid()

  ax.set_title(driverMember.display_name + "\n")
  ax.set_xlabel("Round")
  ax.set_xticks(ndx)
  ax.set_xticklabels(range(1, len(ndx) + 1))

  barWidth = .2
  startPosBars = ax.bar(ndx - barWidth/2, driver.startPositions, barWidth)
  finishPosBars = ax.bar(ndx + barWidth/2, driver.finishPositions, barWidth)

  divisionPoints = ax.plot(driver.divisions)
  pointsPoints = ax.plot(driver.points)

  ax.legend(("Division", "Points", "Start Position", "Finish Position"))
  autoLabel(startPosBars)
  autoLabel(finishPosBars)
  autoLabel(divisionPoints)
  autoLabel(pointsPoints)

  plt.savefig(filePath, facecolor=fig.get_facecolor(), transparent=True)
  plt.close()
# end createDriverHistoryChart

async def updateDriverHistory(message, driverID, workbook):
  guild = message.guild
  driverHistoryChannel = guild.get_channel(DRIVER_HISTORY)
  if (message.channel.id == driverHistoryChannel.id):
    await driverHistoryChannel.purge()

  driverHistory = getDriverHistory(workbook)
  driverHistory = sorted(driverHistory, key=lambda driver: driver.totalPoints)

  for driver in driverHistory:
    if (message.channel.id != driverHistoryChannel.id):
      if (driver.driverID != driverID):
        continue
    if (len(driver.divisions) == 0):
      continue
    driverMember = guild.get_member(driver.driverID)
    if (driverMember == None):
      continue

    filePath = "%s_Driver_History.png" % (driverMember.display_name)
    await createDriverHistoryChart(driver, driverMember, filePath)

    driverHistoryGraph = open(filePath, "rb")
    #plt.show()
    if (message.channel.id != driverHistoryChannel.id):
      await message.channel.send(file=discord.File(driverHistoryGraph))
    else:
      await driverHistoryChannel.send(file=discord.File(driverHistoryGraph))
    driverHistoryGraph.close()
    os.remove(filePath)
# end updateDriverHistory

def getStandings(workbook):
  class Driver:
    def __init__(self, position, driverID, specifier, specifierAmt):
      self.position = position
      self.driverID = driverID
      self.specifier = specifier
      self.specifierAmt = specifierAmt
  # end Driver

  class Standings:
    def __init__(self, name, leftCol, rightCol, specifier, channelID):
      self.name = name
      self.standings = []
      self.leftCol = leftCol
      self.rightCol = rightCol
      self.specifier = specifier
      self.channelID = channelID
  # end Standings

  standingsSheet = workbook.worksheet("Standings")
  driversRange, driverSheet = getDriversRange(workbook)

  standings = [
    Standings("Standings", "G", "J", "Total Points", STANDINGS),
    Standings("Rookie Standings", "W", "Z", "Total Points", ROOKIE_STANDINGS),
    Standings("Reserve Standings", "L", "O", "Res. Points", RESERVE_STANDINGS),
    Standings("Least Improved", "R", "U", "Pos. Diff.", LEAST_IMPROVED),
    Standings("Total Positions Gained/Lost", "AB", "AE", "Tot. Pos. G/L", TOT_POS_GAIN_LOST),
    Standings("Mini-Championship 1", "AG", "AJ", "Total Points", MINI_CHAMPIONSHIPS),
    Standings("Mini-Championship 2", "AL", "AO", "Total Points", MINI_CHAMPIONSHIPS),
    Standings("Mini-Championship 3", "AQ", "AT", "Total Points", MINI_CHAMPIONSHIPS),
    Standings("Mini-Championship 4", "AV", "AY", "Total Points", MINI_CHAMPIONSHIPS),
    Standings("Mini-Championship 5", "BA", "BD", "Total Points", MINI_CHAMPIONSHIPS),
    Standings("Mini-Championship 6", "BF", "BI", "Total Points", MINI_CHAMPIONSHIPS),
  ]

  for standing in standings:
    standingsRange = standingsSheet.range("%s4:%s%s" % (standing.leftCol, standing.rightCol, standingsSheet.row_count))

    for i in range(0, len(standingsRange), 4):
      if (standingsRange[i].value == ""):
        break  
      position = int(standingsRange[i].value)
      driverID = int(driversRange[findDriver(driversRange, standingsRange[i+2].value)-1].value)
      specifier = standing.specifier
      specifierAmt = int(standingsRange[i+3].value.split(".")[0])
      standing.standings.append(Driver(position, driverID, specifier, specifierAmt))
  return standings
# end getStandings

def getDivList(workbook):
  class Driver:
    def __init__(self, div, driverName, driverID):
      self.div = div
      self.driverName = driverName
      self.driverID = driverID
  #end Driver
    
  standingsSheet = workbook.worksheet("Standings")
  divListRange = standingsSheet.range("B4:C" + str(standingsSheet.row_count))
  driversRange, driverSheet = getDriversRange(workbook)

  divList = {}
  for i in range(0, len(divListRange), 2):
    if (divListRange[i].value == ""):
      break
    div = divListRange[i].value[-1]
    driverName = divListRange[i+1].value
    driverID = driversRange[findDriver(driversRange, driverName)-1].value
    driver = Driver(div, driverName, driverID)
    if (div in divList):
      divList[div].append(driver)
    else:
      divList[div] = [driver]
  return divList
# end getDivList

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

def getDriverHistory(workbook):
  class Driver:
    def __init__(self, driverID, totalPoints, divisions, startPositions, finishPositions, points):
      self.driverID = int(driverID)
      self.totalPoints = totalPoints
      self.divisions = divisions
      self.startPositions = startPositions
      self.finishPositions = finishPositions
      self.points = points # per race
  # end Driver

  driverHistorySheet = workbook.worksheet("Driver History")
  driverHistoryRange = driverHistorySheet.range("B3:CH%s"  % (driverHistorySheet.row_count))
  driverHistoryRangeCols = 85
  driversRange, driversSheet = getDriversRange(workbook)
  currentWeek = int(driverHistorySheet.range("B1:B1")[0].value)

  drivers = []

  for i in range(driverHistoryRangeCols, len(driverHistoryRange), driverHistoryRangeCols):
    if (driverHistoryRange[i].value == ""):
      break

    driverID = None
    totalPoints = 0
    divisions = []
    startPositions = []
    finishPositions = []
    points = []
    for j in range(driverHistoryRangeCols):
      
      if (driverHistoryRange[j].value == "Driver"):
        driverName = driverHistoryRange[i+j].value
        driverID = driversRange[findDriver(driversRange, driverName)-1].value

      elif (driverHistoryRange[j].value == "Div"):
        div = driverHistoryRange[i+j].value
        if (div != "OUT"):
          div = div.split("D")[-1]
        else:
          break
        try:
          divisions.append(int(div))
        except ValueError:
          divisions.append(0)
          startPositions.append(0)
          finishPositions.append(0)
          points.append(0)
      try:
        if (divisions[-1] == 0):
          continue
      except IndexError: # still looping to get to the first week
        continue

      if (driverHistoryRange[j].value == "Total Points"):
        totalPoints = int(driverHistoryRange[i+j].value.split(".")[0])
      if (driverHistoryRange[j].value == "Start"):
        startPositions.append(int(driverHistoryRange[i+j].value))
      elif (driverHistoryRange[j].value == "Finish"):
        finishPositions.append(int(driverHistoryRange[i+j].value))
      elif (driverHistoryRange[j].value == "Points"):
        points.append(int(driverHistoryRange[i+j].value))

      if (len(points) + 1 == currentWeek):
        break
    
    if (len(divisions) != 0):
      drivers.append(Driver(driverID, totalPoints, divisions[1:], startPositions, finishPositions, points))

  return drivers
# end getDriverHistory

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

async def setReservesAvailable(embed, workbook):
  reservesSheet = workbook.worksheet("Reserves")
  reservesAvailableRange = reservesSheet.range("D4:E" + str(reservesSheet.row_count))
  reservesAvailable = []
  for i in range(len(embed["fields"])):
    if ("Available" in embed["fields"][i]["name"]):
      for line in embed["fields"][i]["value"].split("\n"):
        if ("]" not in line):
          break
        reservesAvailable.append(embed["fields"][i]["name"].split(":")[1][-1])
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
    for i in range(0, 28):
      startOrder.append(None)
    for i in range(0, len(divisionRostersRanges[division]), 5):
      divisionRoster = divisionRostersRanges[division]
      if (divisionRoster[i].value != ""):
        driverID = int(driversRange[findDriver(driversRange, divisionRoster[i+2].value)-1].value)
        totalPoints = int(divisionRoster[i+3].value.split(".")[0])
        lastWeeksDiv = divisionRoster[i+1].value
        startPosition = int(divisionRoster[i+4].value) 
        if (driverID in reserves):
          reserveID = reserves[driverID].reserveID
        else:
          reserveID = None
        startOrder[startPosition-1] = Driver(driverID, totalPoints, lastWeeksDiv, reserveID)
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
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('cotmS4_client_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  season6Key = "1WgGMgiUF4NVZyFCo-8DW2gnY3kwhXB8l02ov0Cp4pRQ"
  workbook = clientSS.open_by_key(season6Key)
  return workbook
# end openSpreadsheet
