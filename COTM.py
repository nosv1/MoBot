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
import MoBotDatabase

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
PIT_MARSHALL_SIGNUP = 622831151320662036
MINI_CHAMPIONSHIPS = 630610458029588480
DRIVER_HISTORY = 631556653174620160
EVENT_CHAT = 527156400908926978
VOTING = 608472349712580608
VOTING_LOG = 530284914071961619
QUALI_TIMES = 705787893364555785

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

space_char = "⠀"
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
division_emojis = [
  702654860801081474,
  702654861006602299,
  702654861065322526,
  702655539112443997,
  702654861086294086,
  702655538831425547,
  702654860478251128,
]
num_divs = 7



''' CLASSES '''
class Pit_Marshall:
  def __init__(self, member_id, div, host_pm):
    self.member_id = int(member_id)
    self.div = int(div)
    self.host_pm = int(host_pm) # host = 1, pm = 0
# end Pit_Marshall



''' DISCORD FUNCTIONS '''
async def main(args, message, client):
  try:
    authorPerms = message.channel.permissions_for(message.author)
  except:
    pass
    
  qualifyingChannel = message.guild.get_channel(QUALIFYING)
  qualiScreenshotsChannel = message.guild.get_channel(QUALI_SCREENSHOTS)

  if str(moBot) in args[0] and len(args) > 1:
    if "newsignup" in args[1]:
      await handleFormSignup(message)
    elif "newqualitime" in args[1]:
      await handleQualiSubmission(message)

    if args[1] == "quali" and len(args) > 2:
      if args[2] == "missing" and authorPerms.administrator:
        await message.channel.trigger_typing()
        missing_qualifiers = getMissingQualifiers(message.guild)
        await message.channel.send(f"{len(missing_qualifiers)}```{', '.join(missing_qualifiers)}```")

    if (args[1] == "reserve" and authorPerms.administrator):
      await setManualReserve(message)
    elif (args[1] == "history"):
      await message.channel.trigger_typing()
      if (message.content.count("<@") > 1):
        driverID = int(message.content.split("<@")[-1].split(">")[0].replace("!", ""))
      else:
        driverID = message.author.id
      await updateDriverHistory(message, driverID, openSpreadsheet())
    if (message.author.id == mo):
      try:
        if (args[1] == "update"):
          if (args[2] == "standings"):
            await message.channel.trigger_typing()
            await updateStandings(message.guild, openSpreadsheet())
            await message.delete()
          elif (args[2] == "start" and args[3] == "orders"):
            await message.channel.trigger_typing()
            await updateStartOrders(message.guild, openSpreadsheet())
            await message.delete()
          elif (args[2] == "divlist"):
            await message.channel.trigger_typing()
            await updateDriverRoles(message.guild, getDivList(openSpreadsheet()))
            await message.delete()
          elif (args[2] == "driver" and args[3] == "history"):
            await updateDriverHistory(message, None, openSpreadsheet())
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
    if payload.emoji.name == CHECKMARK_EMOJI:
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

    if payload.emoji.name == RandomSupport.EXCLAMATION_EMOJI: # error updating quali roles
      if message.embeds:
        if message.embeds[0].author.name == "New Lap Time": # roles weren't updated
          await updateQualiRoles(message)
          
    if message.id == PIT_MARSHALL_SIGNUP:
      if payload.emoji.name in [CROWN, WRENCH]:
        await handlePitMarshallReaction(message, payload, member)
      elif payload.emoji.name in [X_EMOJI, ARROWS_COUNTERCLOCKWISE_EMOJI] and member.id == mo:
        if payload.emoji.name == X_EMOJI:
          await clear_pit_marshalls(message.guild)
        await updatePitMarshallEmbed(message)
        await message.remove_reaction(payload.emoji.name, member)



    if (message.id == 620811567210037253): # message id for Reserves Embed
      if (payload.emoji.name == WAVE_EMOJI):
        await reserveNeeded(message, member)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == FIST_EMOJI):
        await reserveAvailable(message, member, payload, client)
        await message.channel.send(".", delete_after=0)
      elif (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        if (member.id == mo):
          workbook = openSpreadsheet()
          await getReserves(workbook)
          await updateStartOrders(message.guild, workbook)
          await message.channel.send(content="Remember to remove any reserve roles, if necessary.\n*(deleting in 10 sec)*", delete_after=10)
          await message.remove_reaction(payload.emoji.name, member)

    if (message.id == 622137318513442816): # message id for streamer embed
      if (payload.emoji.name in ["Twitch", "Mixer", "Youtube"]):
        await addStreamer(message, member, payload, client)
      if (payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI):
        await refreshStreamers(message, openSpreadsheet())
        await message.remove_reaction(payload.emoji.name, member)
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
  await channel.send("%s has jumped(?) off the mountain... :eyes: %s, was he important?" % (member.display_name, mo.mention))
# end memberRemove



''' SIGNUP '''
async def handleFormSignup(message):
  if not message.webhook_id: # is not from webhook
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
      embed.description = f"We welcome {member.display_name}."

      await message.guild.get_channel(EVENT_CHAT).send(content=member.mention, embed=embed)
      await member.remove_roles(message.guild.get_role(PEEKER_ROLE))
      await member.add_roles(message.guild.get_role(CHILDREN_ROLE))
      break

  getRoster(message.guild) # just updating discord ids
# end handleFormSignup



''' QUALIFYING '''
async def updateQualiRoles(message):
  await message.remove_reaction(RandomSupport.EXCLAMATION_EMOJI, message.guild.get_member(moBot))

  if message.author.id == moBot:
    embed = message.embeds[0]
    embed.set_footer(text="updating roles...")
    await message.edit(embed=embed)

  try:
    workbook = openSpreadsheet()
    quali_sheet = workbook.worksheet("Qualifying")
    r = quali_sheet.range(f"C4:E{quali_sheet.row_count}") # div, driver, lap time

    def getChannel(div):
      return [channel for channel in message.guild.channels if channel.name == f"division-{div}"][0]

    def getCutoffTime(div):
      for i in range(len(r)-3, -1, -3): # start at the back
        d = r[i].value # div
        if d == "":
          continue
        if int(d) < int(div):
          return r[i+2].value # lap time
      return r[2].value # leader time
    # end getCutoffTime

    for i in range(0, len(r), 3):
      div = r[i].value
      gamertag = r[i+1].value

      if div == "":
        break

      member = getMember(gamertag, message.guild.members)

      role = getRole(f"Division {div}", message.guild.roles) # current div of driver

      if role not in member.roles: # outdated role
        await member.edit(nick=f"[D{div}] {gamertag}")
        
        for m_role in member.roles: # remove incorrect roles
          if "Division" in m_role.name and m_role != role:
            channel = getChannel(str(m_role)[-1])
            await member.remove_roles(m_role)
            await channel.send(f"> Toodles {member.mention}")

        channel = getChannel(div)
        await member.add_roles(role)
        t = ""
        t += f">>> Welcome {member.mention}\n"
        if div == "1":
          t += f"Division 1 Leader: {getCutoffTime(div)}"
        else:
          t += f"Division {int(div)-1} Cut-off: {getCutoffTime(div)}"
        await channel.send(t)

    embed = embed.to_dict()
    del embed["footer"]
    embed = discord.Embed.from_dict(embed)
  except:
    print(traceback.format_exc())
    try:
      embed.set_footer(text=f"{RandomSupport.EXCLAMATION_EMOJI} error updating roles")
      await message.add_reaction(RandomSupport.EXCLAMATION_EMOJI)
    except: # when there's invalid time but no embed cause they still got a position
      pass
  
  await message.edit(embed=embed)
# end updateQualiRoles

async def handleQualiSubmission(message):
  if not message.webhook_id: # is not from webhook
    return

  class Driver:
    def __init__(self, cell_link, screenshot_link, position, div, gamertag, lap_time, leader, division, interval, invalidated, reason):
      self.cell_link = cell_link
      self.screenshot_link = screenshot_link
      self.position = position
      self.div = div
      self.gamertag = gamertag
      self.lap_time = lap_time
      self.leader = leader
      self.division = division
      self.interval = interval
      self.invalidated = invalidated
      self.reason = reason
  # end Driver

  args = message.content.split("{")[1].split("}")[0].replace("\":", ",").replace("\"", "").split(",")

  def getArg(arg):
    for i, x in enumerate(args):
      if x == arg:
        return args[i+1]
  # end getArg

  driver = Driver(
    getArg("cell_link"),
    getArg("screenshot_link"),
    getArg("position"),
    getArg("div"),
    getArg("gamertag"),
    getArg("lap_time"),
    getArg("leader"),
    getArg("division"),
    getArg("interval"),
    getArg("invalidated").lower(),
    getArg("reason")
  )

  embed = discord.Embed()
  for member in message.guild.members: # only looping names to make sure guy is in server and to ping him
    member_name = member.display_name if "[D" not in member.display_name else member.display_name.split("] ")[1].strip()
    if driver.gamertag.lower() == member_name.lower():# or member.id == mo:

      edit_message = False
      if driver.position != "null" and driver.invalidated == "false": # valid lap time
        embed.color = [role.color for role in message.guild.roles if role.name == f"Division {driver.div}"][0]
        embed.set_author(name="New Lap Time", icon_url=logos["cotm_white_trans"])

        embed.description = "" 
        embed.description += f"**Driver:** [{driver.gamertag}]({driver.cell_link})\n"
        embed.description += f"**Lap Time:** [{driver.lap_time}]({driver.screenshot_link})\n"
        embed.description += f"**Division:** {driver.div}\n"
        embed.description += f"**Position:** {driver.position}\n"
        embed.description += "\n"
        embed.description += "__Gaps__\n"
        embed.description += f"to Leader: {driver.leader}\n"
        embed.description += f"to Div Leader: {driver.division}\n"
        embed.description += f"to Driver Ahead: {driver.interval}\n"
        
        edit_message = True

      if driver.position == "null" and driver.invalidated == "true": # invalid lap time
        embed.color = int("0x000000", 16)
        embed.set_author(name="Invalid Lap Time", icon_url=logos["cotm_white_trans"])

        embed.description = ""
        embed.description += f"**Driver:** {driver.gamertag}\n"
        embed.description += f"**Lap Time:** [~~{driver.lap_time}~~]({driver.screenshot_link})\n"
        await member.edit(nick=driver.gamertag)

        edit_message = True
        
      if edit_message:
        message = await message.guild.get_channel(QUALI_TIMES).send(content=member.mention, embed=embed)
      
      await updateQualiRoles(message)
      break
# end handleQualiSubmission



''' VOTING '''
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
    value=f"Select the number-button below to cast your vote. You have 4 votes to spend total. Spread them out, or stack them all on one option. Click the {X_EMOJI} to clear all your votes.\n{space_char}",
    inline=False
  )

  og_voting_embed = await (message.guild.get_channel(VOTING)).fetch_message(VOTING_EMBED)
  options = RandomSupport.getValueFromField(
    og_voting_embed.embeds[0], 
    "Options"
  ).split("\n")
  options = [f"{i+1}. {option} - 0" for i, option in enumerate(options) if space_char not in option]
  embed.add_field(
    name="**Options**", 
    value= "\n".join(options) + "\n" + space_char,
    inline=False
  )

  embed.add_field(
    name="**Current Option**",
    value=f"{options[0]}\n{space_char}",
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
    f"{options[new_option_number-1]}\n{space_char}"
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
    workbook = openSpreadsheet()
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



''' PIT-MARSHALLS '''
# what divs not available if in race
host_not_avail = [
  [1, 4, 7, 2, 5], # in div 1, can't host for these
  [2, 5, 1, 4, 7],
  [3, 6, 2, 5],
  [1, 4, 7, 2, 5],
  [2, 5, 1, 4, 7],
  [3, 6, 2, 5],
  [1, 4, 7, 2, 5]
]

pm_not_avail = [
  [1, 4, 7], # in div 1, can't pit marshall for these
  [2, 5],
  [3, 6],
  [1, 4, 7],
  [2, 5],
  [3, 6],
  [1, 4, 7]
]

def getPitMarshalls():
  moBotDB = connectDatabase()
  marshalls = []
  moBotDB.cursor.execute(f"""
    SELECT *
    FROM pit_marshalls
  """)
  for record in moBotDB.cursor:
    marshalls.append(Pit_Marshall(*record))
  moBotDB.connection.close()
  return marshalls
# end getCurrentPitMarshalls

async def clear_pit_marshalls(guild):
  pit_marshalls = getPitMarshalls()
  pm_role = getRole("Pit-Marshall", guild)
  for pm in pit_marshalls:
    member = guild.get_member(pm.member_id)
    await member.remove_roles(pm_role)

  moBotDB = connectDatabase()
  moBotDB.cursor.execute(f"""
    DELETE FROM pit_marshalls
  """)
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end clear_pit_marshalls

def addRemovePitMarshall(host_pm, pit_marshalls, member, member_divs, divs):

  ## remove 
  for pm in pit_marshalls:
    if pm.member_id == member.id and pm.host_pm == host_pm:
      if pm.div in divs: # if previously clicked div is clicked again, remove
        moBotDB = connectDatabase()
        moBotDB.cursor.execute(f"""
          DELETE FROM pit_marshalls
          WHERE 
            `id` = '{pm.member_id}' AND
            `div` = '{pm.div}' AND
            `host_pm` = '{host_pm}'
        """)
        moBotDB.connection.commit()
        moBotDB.connection.close()

        del member_divs[member_divs.index(pm.div)]
      else:
        member_divs.append(pm.div)


  ## add
  def refineAvail(not_avail, member_divs):
    new_not_avail = []
    for div in member_divs:
      new_not_avail += not_avail[div-1]
    
    return [i for i in range(1, num_divs+1) if i not in new_not_avail]
  # end refineAvail

  is_pit_marshalling = False
  if host_pm == 1: # if host
    hosts_needed = list(range(1,num_divs+1)) # get the divs where a host is needed
    for pit_marshall in pit_marshalls:
      if pit_marshall.host_pm == 1:
        del hosts_needed[pit_marshall.div-1]
    
    for div in hosts_needed:
      if div in refineAvail(host_not_avail, member_divs) and div in divs:
        is_pit_marshalling = True

        moBotDB = connectDatabase()
        moBotDB.cursor.execute(f"""
          INSERT INTO pit_marshalls (
            `id`, `div`, `host_pm`
          ) VALUES (
            '{member.id}',
            '{div}',
            '1'
          );
        """)
        moBotDB.connection.commit()
        moBotDB.connection.close()
        break

  else: # if pm
    pm_needed = list(range(1,num_divs+1)) # get the divs where a pm is needed
    for pit_marshall in pit_marshalls:
      if pit_marshall.host_pm == 0:
        del pm_needed[pit_marshall.div-1]
      
    for div in pm_needed:
      if div in refineAvail(pm_not_avail, member_divs) and div in divs:
        is_pit_marshalling = True

        member_divs.append(div)

        moBotDB = connectDatabase()
        moBotDB.cursor.execute(f"""
          INSERT INTO pit_marshalls (
            `id`, `div`, `host_pm`
          ) VALUES (
            '{member.id}',
            '{div}',
            '0'
          );
        """)
        moBotDB.connection.commit()
        moBotDB.connection.close()

  return is_pit_marshalling
# end addRemovePitMarshall

async def updatePitMarshallEmbed(pm_message):
  message = pm_message
  await message.channel.trigger_typing()

  embed = message.embeds[0]
  pit_marshalls = getPitMarshalls()

  embed = embed.to_dict()

  div_lines = [
    "Host -",
    "Pit-Marshall -",
    space_char
  ]

  for i in range(7):
    embed["fields"][i]["value"] = "\n".join(div_lines)

  for pm in pit_marshalls:
    pm_name = message.guild.get_member(pm.member_id).display_name
    div_lines = embed["fields"][pm.div-1]["value"].split("\n")
    if pm.host_pm == 1:
      div_lines[0] = f"Host - {pm_name}"
    else:
      div_lines[1] = f"Pit-Marshall - {pm_name}"
    embed["fields"][pm.div-1]["value"] = "\n".join(div_lines)

  await message.edit(embed=discord.Embed().from_dict(embed))
# end updatePitMarshallEmbed

async def handlePitMarshallReaction(message, payload, member):
  await message.channel.trigger_typing()

  pit_marshalls = getPitMarshalls()

  member_divs = [] # get the divs the member is in
  for role in member.roles: # racing in 
    if "Division" in role.name:
      member_divs.append(int(role.name[-1]))

  for pm in pit_marshalls: # already pit marshalling
    if pm.member_id == member.id:
      member_divs.append(pm.div)
  
  # figure out what the user wants to do, host/pm and what divs
  host_pm = -1 # host = 1 // pm = 0
  divs = []
  for reaction in message.reactions:
    async for user in reaction.users():
      if user.id == member.id:
        if reaction.emoji == CROWN:
          host_pm = 1
        elif reaction.emoji == WRENCH:
          host_pm = 0
        elif reaction.emoji.id in division_emojis:
          divs.append(division_emojis.index(reaction.emoji.id) + 1)
        break

  is_pit_marshalling = False
  if divs: # if user actually selected div
    is_pit_marshalling = addRemovePitMarshall(host_pm, pit_marshalls, member, member_divs, divs)
  else:
    await message.channel.send(f"**{member.mention}, please select the division(s) before selecting the {CROWN} or the {WRENCH}.**", delete_after=7)

  pm_role = getRole("Pit-Marshall", message.guild.roles)
  if is_pit_marshalling:
    await member.add_roles(pm_role)
  else:
    await member.remove_roles(pm_role)

  await updatePitMarshallEmbed(message)

  for reaction in message.reactions:
    async for user in reaction.users():
      if user.id == member.id:
        await message.remove_reaction(reaction.emoji, member)
        break
# end handlePitMarshallReaction



''' SUPPORT '''
def getMember(gamertag, members):
  print(gamertag)
  return [member for member in members if gamertag.lower() in member.display_name.lower()][0]
# end getMember
    
def getRole(name, roles):
  return [role for role in roles if role.name == name][0]
# end getRole

def getRoster(guild): # gamertag, discord_id, q_pos, status, youtube, stream
  workbook = openSpreadsheet()
  sheet = workbook.worksheet("Roster")
  roster_range = sheet.range(f"C4:H{sheet.row_count}") 
  discord_range = sheet.range(f"D4:D{sheet.row_count}")

  roster = [[] for i in range(6)]
  for i in range(0, len(roster_range), len(roster)):
    if roster_range[i].value == "":
      break

    for j in range(len(roster)):
      roster[j].append(roster_range[i+j]) # append cell object
    
  for i, cell in enumerate(roster[0]): # gamertag_range
    if cell.value == "":
      break
    
    if roster[3][i].value != "Retired":
      try:
        member = getMember(cell.value, guild.members)
        discord_range[i].value = f"<@{member.id}>"
      except IndexError: # member could not be found
        discord_range[i].value = "Inaccurate GT"
    else:
      discord_range[i].value = ""

  sheet.update_cells(discord_range, value_input_option="USER_ENTERED")

  for i in range(len(roster)):
    for j in range(len(roster[i])):
      roster[i][j] = roster[i][j].value

  return roster
# end getRoster

def getMissingQualifiers(guild):
  roster = getRoster(guild)

  missing_qualifiers = []
  for i, q_pos in enumerate(roster[2]): # q_pos
    if q_pos == "TBD":
      missing_qualifiers.append(roster[1][i]) # discord_id

  return missing_qualifiers
# end getMissingQualifiers




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
      embed["fields"][i]["value"] += space_char
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
  
  workbook = openSpreadsheet()
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

  workbook = openSpreadsheet()
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

  workbook = openSpreadsheet()
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
  value += "\n\n**Fastest Overall:**\n" + space_char + floatTimeToStringTime(fastestOverall[2]) + " (" + lapTimeDifferenceToString(lapTime - fastestOverall[2]) + ") by <@" + driversRange[findDriver(driversRange, fastestOverall[0])-1].value + ">"
  value += "\n**Fastest In Division:**\n" + space_char + floatTimeToStringTime(fastestInDiv[2]) + " (" + lapTimeDifferenceToString(lapTime - fastestInDiv[2]) + ") by <@" + driversRange[findDriver(driversRange, fastestInDiv[0])-1].value + ">"
  value += "\n**Driver Ahead:**\n" + space_char + floatTimeToStringTime(driverAhead[2]) + " (" + lapTimeDifferenceToString(lapTime - driverAhead[2]) + ") by <@" + driversRange[findDriver(driversRange, driverAhead[0])-1].value + ">"
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



''' RESOURCES '''
def connectDatabase():
  return MoBotDatabase.connectDatabase("COTM")
# end connectDatabase

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('cotmS4_client_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  season6Key = "1WgGMgiUF4NVZyFCo-8DW2gnY3kwhXB8l02ov0Cp4pRQ"
  workbook = clientSS.open_by_key(season6Key)
  return workbook
# end openSpreadsheet
