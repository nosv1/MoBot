import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz

import SecretStuff
import MoBotDatabase
import RandomSupport

mo = 405944496665133058
moBot = 449247895858970624
moBotSupport = 467239192007671818
clockChannel = 579774370684207133 # channel in mobot support with clock

editorPages = {
  "Author" : "",
  "Number of Pages" : 0,
}

arrows = "🔼🔽⏫⏬"
repeatingOptions = [
  "Skip", "None", "Hourly", "Daily", "Weekly", "Bi-Weekly", "Monthly", "Yearly"
]
timeZones = [
  "US/Pacific", "US/Eastern", "UTC", "Europe/London", "Europe/Amsterdam", "Asia/Vientiane", "Japan", "Australia/Queensland"
]

class Clock:
  def __init__(self, channelID, timeFormat, timeZone):
    self.channelID = channelID
    self.timeFormat = timeFormat
    self.timeZone = timeZone
# end Clock

class Countdown:
  def __init__(self, channelID, endDatetime, timeZone, text, repeating):
    self.channelID = channelID
    self.endDatetime = endDatetime
    self.timeZone = timeZone
    self.text = text
    self.repeating = repeating
# end Countdown 

async def main(args, message, client):
  if (len(args) == 3): # args[1] == clock or countdown, # args[2] == channelID
    await message.channel.trigger_typing()
    await prepareEditor(message, args[1], args[2], 1, 0)
  elif (len(args) == 2):
    await message.channel.trigger_typing()
    msg = await message.channel.send("A channel has been created for you. It should be found near the top on the left side.")
    await prepareEditor(message, args[1], await createChannel(message, args[1]), 1, 0)
    await asyncio.sleep(10)
    await msg.delete()
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client, clockType): 
  if (payload.user_id != moBot):
    await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

    channelID = message.content.split("**Channel ID**: ")[1].split("\n")[0].strip()
    embed = message.embeds[0].to_dict()
    try:
      pageNumber = int(embed["footer"]["text"].split("/")[0].split(" ")[1].strip())
      numberOfPages = int(embed["footer"]["text"].split("/")[1])
    except KeyError:
      pageNumber = None
      numberOfPages = None

    isEditor = numberOfPages != None
    
    if (payload.emoji.name == "◀"):
      pageNumber = pageNumber - 1 if pageNumber - 1 > 0 else numberOfPages
      await prepareEditor(message, clockType, channelID, pageNumber, message.id)
    elif (payload.emoji.name == "▶"):
      pageNumber = pageNumber + 1 if pageNumber + 1 <= numberOfPages else 1
      await prepareEditor(message, clockType, channelID, pageNumber, message.id)
    elif (payload.emoji.name in arrows):
      await editEditorValue(message, payload, clockType)
    elif (payload.emoji.name == "✅"):
      embed = discord.Embed().from_dict(embed)
      nextStep = embed.author.url.split("next=")[1].split("/")[0]
      if (clockType == "clock"):
        if ("waitForTimeZone" == nextStep):
          await waitForTimeZone(message)
      if (isEditor):
        if (clockType == "countdown"):
          await updateCountdownInfo(message.guild, await getCountdownFromOverview(message))
          msg = await message.channel.send("Countdown Saved - Expect update within 1 minute")
        else:
          await updateClockInfo(message.guild, await getClockFromOverview(message))
          msg = await message.channel.send("Clock Saved - Expect update within 1 minute")
        await asyncio.sleep(3)
        await msg.delete()
      else:
        await closeEditor(message, payload, clockType, channelID, isEditor)
    elif (payload.emoji.name == "❌"):
      await closeEditor(message, payload, clockType, channelID, isEditor)
    elif (payload.emoji.name == "🗑"):
      await closeEditor(message, payload, clockType, channelID, isEditor)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def waitForTimeZone():
  # get number from history check against the times in the description, get time, find the timezones that match that time
  pass

# end waitForTimeZone

async def waitForApproxTimeZone(message):
  # get utc, get -11 to +12, figure out which 
  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.top_role.color)
  embed.set_author(name="MoBot Clocks", icon_url=moBotMember.avatar_url, url="https://google.com/current=waitForApproxTimeZone/next=waitForTimeZone")

  times = [] # array of all times, no duplicates
  t = [] # used to check for duplicate times before adding them to array
  utcnow = datetime.utcnow()
  for tz in pytz.all_timezones:
    time = pytz.timezone("UTC").localize(utcnow).astimezone(pytz.timezone(tz)).strftime("%H:%M")
    if (time not in t):
      t.append(time)
      time = [int(a) for a in time.split(":")] # "00:01" -> [0, 1]
      times.append([time[0]*60+time[1], time]) # times[-1] = [0*60+1, [0, 1]]
  times.sort(key=lambda x: x[0]) # sort on col 1 ... '0*60+1'
  t = []
  for i in range(0, len(times), 2):
    # times[i] = "` 0. 00:01` - ` 1. 01:01`"
    t.append("`%s. %s`" % (
        str(i + 1).rjust(2, " "),
        "%s:%s" % (
          str(times[i][1][0]).rjust(2, "0"),
          str(times[i][1][1]).rjust(2, "0"),
        )
      )
    )
    if (len(times) != i + 1):
      t[-1] += " - `%s. %s`" % (
        str(i + 2).rjust(2, " "),
        "%s:%s" % (
          str(times[i+1][1][0]).rjust(2, "0"),
          str(times[i+1][1][1]).rjust(2, "0"),
        )
      )
  times = t
  for t in times:
    print(t)

  embed.description = "%s\n%s\n\n%s\n\n%s" % (
    "**__What time is it?__**",
    "- To approximately determine which time zone the clock will use, type the number matching a time below.\n- ***Example:** If it's currently `12:00` and #1 says `12:00`, type 1.*\n- If you are using a 12-hour clock and it is currently after noon, take your time +12 hours. There will be options to format the clock after this.",
    "\n".join(times),
    "*Type the number that matches the current time, then click the %s to continue to setting the exact time zone.*" % RandomSupport.CHECKMARK_EMOJI,
  )
  msg = await message.channel.send(embed=embed)
  await msg.add_reaction(RandomSupport.CHECKMARK_EMOJI)
# end waitForApproxTimeZone

async def createChannel(message, clockType):
  guild = message.guild
  channelName = "Edit This Text:" if clockType.lower() == "countdown" else "New Clock Channel"
  channel = await guild.create_voice_channel(channelName)
  return channel.id
# end createChannel

async def checkClockAccuracy(client):
  n = datetime.now()
  guild = client.get_guild(moBotSupport)
  channel = guild.get_channel(clockChannel)
  timeZone = channel.name.split(" ")[1]
  
  if(n.minute - int(channel.name.split(":")[1][:2]) > 2):
    await RandomSupport.sendMessageToMo("**CLOCKS AREN'T UPDATED**\nCurrent Time: `%s`\nClock: `%s`" % (n.strftime("%H:%M%p " + timeZone + " - %b %d" ), channel.name), client, mo)
# end checkClockAccuracy