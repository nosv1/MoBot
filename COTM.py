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
RESERVES_EMBED = 620811567210037253
VOTING_EMBED = 620778154197385256
VOTING_CHECKMARK = 620778190767390721
COTM_STREAMS_EMBED = 622137318513442816
START_ORDER_EMBEDS = [
  709412554119708762,
  709412559211593828,
  709412567386161195,
  709412576370360326,
  709412582133465150,
  709412597383954512,
  709412602819772509,
]

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
EXPERT_VOTER_ROLE = 727940758627287051

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
  702654859983454318,
  702654860478251128
]
num_divs = 7 # active div count



''' CLASSES '''
class Pit_Marshall:
  def __init__(self, pm_id, member_id, div, host_pm):
    self.pm_id = int(pm_id)
    self.member_id = int(member_id)
    self.div = int(div)
    self.host_pm = int(host_pm) # host = 1, pm = 0
# end Pit_Marshall

class Reserve:
  def __init__(self, reserve_id, date):
    self.reserve_id = reserve_id
    self.date = float(date) # total seconds
    self.member_id = int(reserve_id[:-2])
    self.div = int(reserve_id[-2])
    self.need_avail = int(reserve_id[-1]) # need = 1, avail = 0
# end Reserve



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

    if message.author.id == mo:
      if args[1] == "update":
        if args[2] == "startorder":
          await updateStartOrderEmbed(message.guild, int(args[3]))

    '''
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
      '''
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
      
    if message.id == RESERVES_EMBED:
      if payload.emoji.name == WAVE_EMOJI or payload.emoji.id in division_emojis:
        await handleReserveReaction(message, payload, member)
      elif payload.emoji.name in [X_EMOJI, ARROWS_COUNTERCLOCKWISE_EMOJI] and member.id == mo:
        if payload.emoji.name == X_EMOJI:
          await clear_reserves(message)
        reserves = getReserves()
        await updateReserveEmbed(message, reserves, getReserveCombos(reserves))
        updateReservesSpreadsheet(message.guild, getReserveCombos(reserves))
        await message.remove_reaction(payload.emoji.name, member)
      else:
        await message.remove_reaction(payload.emoji.name, member)

    if message.id == COTM_STREAMS_EMBED:
      if payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI:
        await updateStreamsEmbed(message.guild)
        await message.remove_reaction(payload.emoji.name, member)

    if message.id in START_ORDER_EMBEDS:
      if payload.emoji.name == ARROWS_COUNTERCLOCKWISE_EMOJI:
        await updateStartOrderEmbed(message.guild, START_ORDER_EMBEDS.index(message.id)+1)
        await message.remove_reaction(payload.emoji.name, member)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  member = message.guild.get_member(payload.user_id)
  if ("MoBot" not in member.name):
    if message.id == RESERVES_EMBED:
      if payload.emoji.name == WAVE_EMOJI or payload.emoji.id in division_emojis:
        await handleReserveReaction(message, payload, member)
      else:
        await message.remove_reaction(payload.emoji.name, member)

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
  mo_member = guild.get_member(mo)
  channel = guild.get_channel(EVENT_CHAT)
  await channel.send("%s has jumped(?) off the mountain... :eyes: %s, was he important?" % (member.display_name, mo_member.mention))
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

  if message.author.id == moBot: # not really necessary, but for testing with mobottest
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

      if role not in member.roles or not re.match(r"(^\[D\d\] )", member.display_name): # outdated role or name is missing [D\d]
        await member.edit(nick=f"[D{div}] {gamertag}")

      if role not in member.roles: # outdated role
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

      if driver.invalidated == "true": # invalid lap time
        embed.color = int("0x000000", 16)
        embed.set_author(name="Invalid Lap Time", icon_url=logos["cotm_white_trans"])

        embed.description = ""
        embed.description += f"**Driver:** {driver.gamertag}\n"
        embed.description += f"**Lap Time:** [~~{driver.lap_time}~~]({driver.screenshot_link})\n"
        embed.description += f"**Reason:** {driver.reason}\n"
        await member.edit(nick=driver.gamertag)

        edit_message = True
        
      if edit_message:
        message = await message.guild.get_channel(QUALI_TIMES).send(content=member.mention, embed=embed)
      
      await updateQualiRoles(message)
      break
# end handleQualiSubmission



''' VOTING '''
def getTotalVotesAvail(member):
  total_avail = 2 # default

  if EXPERT_VOTER_ROLE in [r.id for r in member.roles]:
    total_avail += 3

  return total_avail 
# end getTotalVotesAvail

async def openVotingChannel(message, member):
  await message.channel.trigger_typing()

  guild = message.guild
  category_channels = message.channel.category.channels

  for channel in category_channels:
    if re.sub(r"[\[\]]", "", member.display_name.lower()) in channel.name.replace("-", " "): # channel already created
      await message.channel.send(f"{channel.mention}", delete_after=10)
      return

  channel = await guild.create_text_channel(
    f"voting-{member.display_name}",
    overwrites = {
      guild.get_role(EVERYONE) : discord.PermissionOverwrite(read_messages=False),
      member : discord.PermissionOverwrite(
        read_messages=True,
        send_messages=True
      ),
    },
    category=message.channel.category,
    position=sys.maxsize
  )
  msg = await channel.send(
    content=member.mention,
    embed=(await createOgVotingEmbed(message, member))
  )
  await msg.add_reaction(X_EMOJI)
  for emoji in RandomSupport.numberEmojis[0:getTotalVotesAvail(member)+1]:
    await msg.add_reaction(emoji)
# end openVotingChannel

async def createOgVotingEmbed(message, member):
  total_votes_avail = getTotalVotesAvail(member)

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
    value=f"Select the number-button below to cast your vote. You have {total_votes_avail} votes to spend total. Spread them out, or stack them all on one option. Click the {X_EMOJI} to clear all your votes.\n{space_char}",
    inline=False
  )

  options = [f"Track {c} - 0" for c in "ABCD"]
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
    value=total_votes_avail,
    inline=False
  )

  return embed
# end createOgVotingEmbed

async def resetVotes(message, member):
  await message.clear_reactions()
  await message.edit(embed=(await createOgVotingEmbed(message, member)))
  await message.add_reaction(X_EMOJI)
  for emoji in RandomSupport.numberEmojis[0:getTotalVotesAvail(member)+1]:
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
    r = sheet.range(f"C10:G{sheet.row_count}")
    user_found = findDriver(r, member.display_name)

    if user_found != -1:
      await message.channel.send(f"**Cancelling Submssion**\nYou cannot vote more than once. If this is a mistake, contact <@{mo}>.")
      await message.clear_reactions()
      return

    for i, cell in enumerate(r):

      if cell.value == "": # append vote
        vote_embed = message.embeds[0]
        votes = [int(RandomSupport.getDetailFromURL(vote_embed.author.url, str(j))) for j in range(1, 5)]
        if sum(votes) != getTotalVotesAvail(member): # if user spams, they sometimes can get more than 4 total votes in...
          await resetVotes(message, member)
          return
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

        count = RandomSupport.numberToEmojiNumbers(i // 10 + 1)
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



''' PIT MARSHALLS '''
# what divs not available if in race
host_not_avail = [ # not actually using this, changed the restrictions...
  [1, 4, 7], # in div 1, can't host for these
  [2, 5, 1, 4, 7],
  [3, 6, 2, 5],
  [1, 4, 7],
  [1, 4, 7],
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
  pm_role = getRole("Pit Marshall", guild.roles)
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
        del divs[divs.index(pm.div)]
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
        del hosts_needed[hosts_needed.index(pit_marshall.div)]
    
    for div in hosts_needed:
      if div in refineAvail(pm_not_avail, member_divs) and div in divs:
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
        del pm_needed[pm_needed.index(pit_marshall.div)]
      
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
    "Pit Marshall -",
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
      div_lines[1] = f"Pit Marshall - {pm_name}"
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
        
  if divs: # if user actually selected div
    addRemovePitMarshall(host_pm, pit_marshalls, member, member_divs, divs)
  else:
    await message.channel.send(f"**{member.mention}, please select the division(s) before selecting the {CROWN} or the {WRENCH}.**", delete_after=7)

  pm_role = getRole("Pit Marshall", message.guild.roles)
  if member.id in [pm.member_id for pm in getPitMarshalls() if pm.member_id == member.id]:
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



''' RESERVES '''
def getReserves():
  moBotDB = connectDatabase()
  reserves = []
  moBotDB.cursor.execute(f"""
    SELECT *
    FROM reserves
  """)
  for record in moBotDB.cursor:
    reserves.append(Reserve(*record))
  moBotDB.connection.close()

  reserves.sort(key=lambda r:r.date)
  return reserves
# end getReserves

async def clear_reserves(message):
  await message.clear_reactions()
  await message.add_reaction(WAVE_EMOJI)
  for i in range(num_divs):
    div_emoji = f"<:D{i+1}:{division_emojis[i]}>"
    await message.add_reaction(div_emoji)

  reserves = getReserves()
  pm_role = getRole("Pit Marshall", message.guild.roles)

  for r in reserves:
    member = message.guild.get_member(r.member_id)
    for role in member.roles:
      if "Reserve" in role.name:
        await member.remove_roles(role)

  moBotDB = connectDatabase()
  moBotDB.cursor.execute(f"""
    DELETE FROM reserves
  """)
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end clear_pit_marshalls

def getReserveCombos(reserves):
  reserve_combos = {"need" : [], "avail" : [], "div" : []} # only complete pairs

  for r_need in reserves:
    if r_need.need_avail == 1: # needs reserve
      for r_avail in reserves:
        if r_avail.div == r_need.div and r_avail.need_avail == 0:
          is_avail = True
          for i, r in enumerate(reserve_combos["avail"]): # see if thre is a a matching div for this driver
            if r == r_avail.member_id and reserve_combos["div"][i] == r_need.div: # already reserving for someone in this div
              is_avail = False
              break
          if is_avail:
            reserve_combos["need"].append(r_need.member_id)
            reserve_combos["avail"].append(r_avail.member_id)
            reserve_combos["div"].append(r_need.div)
            break

  return reserve_combos
# end getReserveCombos

def handleNeedReserve(t_need, need, member): # just updating the database
  moBotDB = connectDatabase()
  try:
    if t_need == -1 and need == -1: # doesn't need and didn't need
      pass

    elif t_need > -1 and need == -1: # does need and didn't need
      moBotDB.cursor.execute(f"""
        INSERT INTO reserves
          (`reserve_id`, `date`)
        VALUES
          ('{member.id}{t_need}{1}', '{(datetime.utcnow() - datetime(2020, 1, 1)).total_seconds()}')
      """)

    elif t_need > -1 and need > -1: # does need and did need
      pass

    elif t_need == -1 and need > -1: # doesn't and did need
      moBotDB.cursor.execute(f"""
        DELETE FROM reserves
        WHERE `reserve_id` = '{member.id}{need}{1}'
      """)

    moBotDB.connection.commit()
  except: # likely duplicate primary key error
      pass
  moBotDB.connection.close()
# end handleNeedReserve

def handleAvailReserve(reserves, avail, member): 
  moBotDB = connectDatabase()
  remove = []
  for r in reserves:
    if r.member_id == member.id and r.need_avail == 0:
      if r.div not in avail: # in database, not clicked
        remove.append(r.div)
      elif r.div in avail: # in database, already clicked
        del avail[avail.index(r.div)] # don't need to add

  for d in remove:
    moBotDB.cursor.execute(f"""
      DELETE FROM reserves
      WHERE `reserve_id` = '{member.id}{d}{0}'
    """)
    moBotDB.connection.commit()

  for d in avail:
    try:
      moBotDB.cursor.execute(f"""
        INSERT INTO reserves
          (`reserve_id`, `date`)
        VALUES
          ('{member.id}{d}{0}', '{(datetime.utcnow() - datetime(2020, 1, 1)).total_seconds()}')
      """)
      moBotDB.connection.commit()
    except: # likely duplicate primary key error
      pass
  
  moBotDB.connection.close()
# end handleAvailReserve

async def updateReserveRoles(guild, before_reserve_combos, after_reserve_combos):

  divs_updated = set()
  # remove fellers who have role that shouldn't
  for i, before_r in enumerate(before_reserve_combos["avail"]):
    reserve = before_r
    reservee = before_reserve_combos["need"][i]
    div = before_reserve_combos["div"][i]

    no_longer_reserving = False # could be but for diff person, would still be false
    for j, after_r in enumerate(after_reserve_combos["avail"]):
      if (
        after_reserve_combos["need"][j] == reservee and
        after_reserve_combos["avail"][j] == reserve and
        after_reserve_combos["div"][j] == div
      ):
        no_longer_reserving = True
        break

    if not no_longer_reserving:
      reserve = guild.get_member(reserve)
      await guild.get_channel(DIVISION_UPDATES).send(f"{reserve.mention} is no longer reserving for {guild.get_member(reservee).mention}.")
      await reserve.remove_roles(getRole(f"Reserve Division {div}", guild.roles))
      divs_updated.add(div)
    
  for i, r in enumerate(after_reserve_combos["avail"]):
    reserve = guild.get_member(r)
    reservee = after_reserve_combos["need"][i]
    div = after_reserve_combos["div"][i]
    role = getRole(f"Reserve Division {div}", guild.roles)

    if role not in reserve.roles:
      await guild.get_channel(DIVISION_UPDATES).send(f"{reserve.mention} is now reserving for {guild.get_member(reservee).mention}.")
      await reserve.add_roles(role)
      divs_updated.add(div)

  for div in divs_updated:
    await updateStartOrderEmbed(guild, int(div))
# end updateReserveRoles

async def updateReserveEmbed(message, reserves, reserve_combos):
  embed = message.embeds[0].to_dict()

  values = ["" for i in range(num_divs+1)]
  for r in reserves:
    if r.need_avail == 1: # needs reserve
      reservee = message.guild.get_member(r.member_id)

      if r.member_id in reserve_combos["need"]:
        reserve = message.guild.get_member(reserve_combos["avail"][reserve_combos["need"].index(reservee.id)])
        values[0] += f"{reservee.display_name} rsv. by {reserve.display_name}\n"
      else:
        values[0] += reservee.display_name + "\n"
    
    else: # is avail
      reserve = message.guild.get_member(r.member_id)

      reservee = None
      for i, r_avail in enumerate(reserve_combos["avail"]):
        if r_avail == reserve.id:
          if reserve_combos["div"][i] == r.div:
            reservee = message.guild.get_member(reserve_combos["need"][i])
            values[r.div] += f"{reserve.display_name} rsv. for {reservee.display_name}\n"
            break
      
      if not reservee:
        values[r.div] += reserve.display_name + "\n"

  for i, v in enumerate(values):
    embed["fields"][i]["value"] = v + space_char

  await message.edit(embed=discord.Embed().from_dict(embed))
# end updateReserveEmbed

def updateReservesSpreadsheet(guild, reserve_combos):
  workbook = openSpreadsheet()
  sheet = [sheet for sheet in workbook.worksheets() if sheet.id == 762852343][0] # 'my sheet'
  r = sheet.range(f"M2:N{sheet.row_count}")

  for cell in r:
    cell.value = ""

  for i in range(len(reserve_combos["need"])):
    r[(i*2)].value = guild.get_member(reserve_combos["need"][i]).display_name.split("]")[-1].strip()
    r[(i*2)+1].value = guild.get_member(reserve_combos["avail"][i]).display_name.split("]")[-1].strip()

  sheet.update_cells(r, value_input_option="USER_ENTERED")
# end updateReservesSpreadsheet

async def handleReserveReaction(message, payload, member):
  await message.channel.trigger_typing()

  before_reserves = getReserves() # both reserves needed and available
  before_reserve_combos = getReserveCombos(before_reserves)

  member_divs = [] # get the divs the member is in
  for role in member.roles: # racing in 
    if "Division" in role.name:
      member_divs.append(int(role.name[-1]))
  
  if not member_divs:
    for reaction in message.reactions:
      async for user in reaction.users():
        if user.id == member.id:
          await message.remove_reaction(reaction.emoji, member)
          break
    return

  need = -1
  for r in before_reserves:
    if r.member_id == member.id:
      if r.need_avail == 1:
        need = r.div

  # figure out what the user has clicked currently
  t_need = -1
  avail = []
  for reaction in message.reactions:
    async for user in reaction.users():
      if user.id == member.id:
        if reaction.emoji == WAVE_EMOJI:
          t_need = member_divs[-1]
        elif reaction.emoji.id in division_emojis:
          d = division_emojis.index(reaction.emoji.id) + 1
          driver_div = member_divs[-1]
          if d in [driver_div-1, driver_div+1]: # user can reserve for div
            avail.append(d)
          else:
            await message.remove_reaction(reaction.emoji, member)

  handleNeedReserve(t_need, need, member)
  handleAvailReserve(before_reserves, avail, member)

  after_reserves = getReserves()
  after_reserve_combos = getReserveCombos(after_reserves)

  updateReservesSpreadsheet(message.guild, after_reserve_combos)
  await updateReserveRoles(message.guild, before_reserve_combos, after_reserve_combos)
  await updateReserveEmbed(message, after_reserves, after_reserve_combos)

  if t_need > -1:
    await updateStartOrderEmbed(message.guild, member_divs[-1])
# end handleReserveReaction


''' START ORDERS '''
async def updateStartOrderEmbed(guild, main_div): # also updates div roles
  members = guild.members
  message = await (guild.get_channel(START_ORDERS)).fetch_message(START_ORDER_EMBEDS[main_div-1])
  embed = message.embeds[0]

  div_updates_channel = guild.get_channel(DIVISION_UPDATES)

  first_col = (main_div - 1) * 6 + 2 # pos
  last_col = first_col + 4 # pts

  workbook = openSpreadsheet()
  sheet = workbook.worksheet("Start Orders")
  r = sheet.range(4, first_col, 31, last_col) # pos, div, driver, reserve, pts
  start_order = RandomSupport.arrayFromRange(r)

  reserves = getReserves() # using to see if driver needs reserve but does not have one

  description = ""
  for row in start_order:
    pos = row[0].value
    div = row[1].value
    gamertag = row[2].value
    res_gamertag = row[3].value
    pts = row[4].value.split(".")[0]

    if pos == "":
      break

    div_role = getRole(f"Division {main_div}", guild.roles)

    description += f"\n{pos}.".rjust(3, " ")
    try:
      driver = getMember(gamertag, members)

      needs_reserve = driver.id in [r.member_id for r in reserves if r.need_avail == 1]

      if div_role.name not in [r.name for r in driver.roles]:
        for role in driver.roles:
          if "Division" in role.name and "Reserve" not in role.name:
            await driver.remove_roles(role)
            await div_updates_channel.send(f"{driver.mention} has been removed from {role.name}.")

        await driver.edit(nick=f"[D{main_div}] {gamertag}")
        await driver.add_roles(div_role)
        await div_updates_channel.send(f"{driver.mention} has been added to {div_role.name}.")
    except: # doesn't match
      await message.channel.send(f"<@{mo}>, {gamertag} wasn't found.")
      return

    if res_gamertag == "" and not needs_reserve:
      description += f" **{driver.display_name}** ({pts} - D{div})"
    else:
      reserve = None
      if needs_reserve and res_gamertag:
        try:
          reserve = getMember(res_gamertag, members)
        except: # doesn't match
          await message.channel.send(f"<@{mo}>, {res_gamertag} wasn't found.")
          return

      description += f" ~~{driver.display_name}~~ ({pts} - D{div})\n{space_char * 4}**{reserve.display_name if reserve else 'Needs Reserve'}**"
  
  embed.description = description

  await message.edit(embed=embed)
# end getStartOrders



''' STREAMS '''
async def updateStreamsEmbed(guild):

  def getEmoji(stream_link):
    if ("twitch" in stream_link.lower()):
      return "<:Twitch:622139375282683914> "
    elif ("youtube" in stream_link.lower()):
      return "<:Youtube:622139522502754304>"
    elif ("mixer" in stream_link.lower()):
      return "<:Mixer:622139665306353675>"
  # end getEmoji

  message = await (guild.get_channel(COTM_STREAMS).fetch_message(COTM_STREAMS_EMBED))
  embed = message.embeds[0].to_dict()

  roster = getRoster(guild)

  divs_values = ["" for i in range(num_divs)]

  for i in range(num_divs):
    div_role = getRole(f"Division {i+1}", guild.roles)
    reserve_role = getRole(f"Reserve Division {i+1}", guild.roles)

    twitch_profiles = []
    for member in div_role.members + reserve_role.members:
      try:
        j = roster[1].index(f"<@{member.id}>")
      except ValueError: # not in list
        continue

      stream_link = roster[5][j]
      if "twitch" in stream_link:
        profile = stream_link.split("twitch.tv/")[1].split("/")[0]
        twitch_profiles.append(profile)
        stream_link = f"https://twitch.tv/{profile}"
      
      if stream_link != "":
        divs_values[i] += f"{getEmoji(stream_link)} [__{member.display_name}__]({stream_link})\n"

    if twitch_profiles:
      multi_stream = f"https://multistre.am/{'/'.join(twitch_profiles)}\n"

      if len(divs_values[i]) + len(multi_stream) < 1024:
        divs_values[i] += multi_stream

    if i != num_divs -1:
      divs_values[i] += space_char

  try:
    del embed["fields"]
  except:
    print(traceback.format_exc())

  embed = discord.Embed().from_dict(embed)

  for i in range(num_divs):
    embed.add_field(
      name=f"**Division {i+1}**",
      value=divs_values[i] if divs_values[i] != "" else space_char,
      inline=False
    )

  await message.edit(embed=embed)
# end updateStreamsEmbed


''' HISTORY / STATS '''
'''
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

async def sendDriverHistory(message):
  driverHistory = getDriverHistory(workbook)

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

    await message.channel.send(file=discord.File(driverHistoryGraph))
    driverHistoryGraph.close()
    os.remove(filePath)
# end updateDriverHistory
'''



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
