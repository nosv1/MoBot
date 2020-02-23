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
    await prepareEditor(message, args[1], await createChannel(message, args[1]), 1, 0)
  elif len(args) > 3:
    if "countdown" in args[1]:
      await shorthand(message, args[2])
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


async def shorthand(message, channelID):
  # @MoBot countdown channel_id -10 minutes -- adjusts
  # @MoBot countdown channel_id +10 minutes -- adjusts
  # @MoBot countdown channel_id 23 hours 10 minutes -- sets

  channel = message.guild.get_channel(int(channelID))
  if channel is None:
    await message.channel.send("**Channel Does Not Exist**\n`@MoBot#0697 countdown channel_id ...`")
    return

  adjust = True
  isNegative = None
  amount = ""
  if "+" in message.content:
    isNegative = False
    amount = message.content.split("+")[1].strip()
  elif "-" in message.content:
    isNegative = True
    amount = message.content.split("-")[1].strip()
  else:
    adjust = False # setting countdown not adjusting
    amount = message.content.split(channelID)[1]

  values = {"year" : 0, "month" : 0, "week" : 0, "day" : 0, "hour" : 0, "minute" : 0, "second" : 0}
  for key in values:
    try:
      amount.index(key)
      try:
        values[key] = float(amount.split(key)[0].strip().split(" ")[-1].strip())
      except ValueError:
        await message.channel.send("**Could Not Parse Input**\nTo set the countdown based on the current time:\n  `@MoBot countdown channel_id 23 hours 10 minutes`\n  This will set the countdown 23 hours and 10 minutes from now.\nTo adjust the countdown from its current end time:\n  `@MoBot countdown channel_id +1 day 4 hours 1 minute`\n  This will add 1 day, 4 hours, and 1 minute. Conversely, you can use **-**1 day, for example, to remove time from the countdown.")
        return
    except ValueError: # key not present in text
      pass

  countdown = await getCountdown(message, message.guild.id, channel.id)
  tz = pytz.timezone(countdown.timeZone)
  endDatetime = tz.localize(datetime.strptime(countdown.endDatetime, "%m/%d/%Y %H:%M"))
  now = pytz.utc.localize(datetime.utcnow()).astimezone(tz)

  if adjust:
    endDatetime += (-1 if isNegative else 1) * relativedelta(years=values["year"], months=values["month"], weeks=values["week"], days=values["day"], hours=values["hour"], minutes=values["minute"], seconds=values["second"])
    countdown.endDatetime = endDatetime

  else:
    now += relativedelta(years=values["year"], months=values["month"], weeks=values["week"], days=values["day"], hours=values["hour"], minutes=values["minute"], seconds=values["second"])
    countdown.endDatetime = now

  endDatetime = countdown.endDatetime
  countdown.endDatetime = datetime.strftime(countdown.endDatetime.replace(tzinfo=None), "%m/%d/%Y %H:%M")
  await updateCountdownInfo(message.guild, countdown)
  await message.channel.send("**Countdown Updated**\nNew Time: `%s`\nExpect update within a minute." % datetime.strftime(endDatetime, "%H:%M:%S %Z - %b %d"))
# end shorthand


async def delete(clockType, channelID):
    moBotDB = MoBotDatabase.connectDatabase('MoBot')
    moBotDB.connection.commit()
    moBotDB.cursor.execute("""
      DELETE FROM %ss
      WHERE %ss.channel_id = '%s'
    """ % (clockType.lower(), clockType.lower(), channelID))
    moBotDB.connection.commit()
    moBotDB.connection.close()
# end delete

async def getClock(message, guildID, channelID):  
  clockFormats = {
    "%I:%M%p %Z" : "12-hour",
    "%I:%M%p %Z - %b %d" : "12-hour + date",
    "%H:%M %Z" : "24-hour",
    "%H:%M %Z - %b %d" : "24-hour + date",
  }
  
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
  SELECT clocks.channel_id, clocks.time_format, clocks.time_zone
  FROM clocks
  WHERE 
    clocks.guild_id = '%s' AND
    clocks.channel_id = '%s'
  """ % (guildID, channelID))
  for record in moBotDB.cursor:
    return Clock(record[0], clockFormats[record[1]], record[2])

  return None
# end getClock

async def getCountdown(message, guildID, channelID):  
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
  SELECT countdowns.channel_id, countdowns.end_datetime, countdowns.time_zone, countdowns.text, countdowns.repeating
  FROM countdowns
  WHERE 
    countdowns.guild_id = '%s' AND
    countdowns.channel_id = '%s'
  """ % (guildID, channelID))
  for record in moBotDB.cursor:
    return Countdown(record[0], record[1], record[2], record[3], record[4])

  return None
# end getCountdown

async def getClockFromOverview(message):
  mc = message.content

  clock = Clock(
    mc.split("**Channel ID**: ")[1].split("\n")[0].strip(),
    mc.split("**Format**: ")[1].split("\n")[0].strip(),
    mc.split("**Time Zone**: ")[1].split("\n")[0].strip()
  )
  return clock
# end getClockFromOverview

async def getCountdownFromOverview(message):
  mc = message.content

  countdown = Countdown(
    mc.split("**Channel ID**: ")[1].split("\n")[0].strip(),
    mc.split("**End Datetime**: ")[1].split("\n")[0].strip(),
    mc.split("**Time Zone**: ")[1].split("\n")[0].strip(),
    mc.split("**Text**: ")[1].split("\n")[0].strip(),
    mc.split("**Repeating**: ")[1].split("\n")[0].strip()
  )

  return countdown
# end getCountdownFromOverview

async def getOverviewFromClock(message, clock, channelID):
  overview = "**Overview**\n"
  overview += "  **Channel ID**: " + str(channelID) + "\n"
  overview += "  **Format**: " + clock.timeFormat + "\n"
  overview += "  **Time Zone**: " + clock.timeZone + "\n"

  return overview
# end getOverviewFromClock

async def getOverviewFromCountdown(message, countdown, channelID):
  overview = "**Overview**\n"
  overview += "  **Channel ID**: " + str(channelID) + "\n"
  overview += "  **End Datetime**: " + countdown.endDatetime + "\n"
  overview += "  **Time Zone**: " + countdown.timeZone + "\n"
  overview += "  **Text**: " + countdown.text + "\n"
  overview += "  **Repeating**: " + countdown.repeating + "\n"

  return overview
# end getOverviewFromCountdown

async def updateClockInfo(guild, clock):
  clockFormats = {
    "24-hour" : "%H:%M %Z",
    "24-hour + date" : "%H:%M %Z - %b %d",
    "12-hour" : "%I:%M%p %Z",
    "12-hour + date" : "%I:%M%p %Z - %b %d",
  }

  oldClock = None
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT * 
    FROM clocks
    WHERE clocks.channel_id = '%s'
  """ % clock.channelID)
  for record in moBotDB.cursor:
    oldClock = record # just to test if cursor is empty

  if (oldClock is not None):
    moBotDB.cursor.execute("""
      UPDATE clocks
      SET
        clocks.time_format = '%s',
        clocks.time_zone = '%s'
      WHERE
        clocks.channel_id = '%s'
    """ % (clockFormats[clock.timeFormat], clock.timeZone, clock.channelID))
  else:
    moBotDB.cursor.execute("""
      INSERT INTO `MoBot`.`clocks` 
        (`channel_id`, `guild_id`, `guild_name`, `time_format`, `time_zone`)
      VALUES
        ('%s', '%s', '%s', '%s', '%s')
    """ % (clock.channelID, guild.id, guild.name, clockFormats[clock.timeFormat], clock.timeZone))
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end updateClockInfo

async def updateCountdownInfo(guild, countdown):
  oldCountdown = None
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT *
    FROM countdowns
    WHERE countdowns.channel_id = '%s'
  """ % countdown.channelID)
  for record in moBotDB.cursor:
    oldCountdown = record

  if (oldCountdown is not None):
    moBotDB.cursor.execute("""
      UPDATE countdowns
      SET
        countdowns.end_datetime = '%s',
        countdowns.time_zone = '%s',
        countdowns.text = '%s',
        countdowns.repeating = '%s'
      WHERE
        countdowns.channel_id = '%s'
    """ % (countdown.endDatetime, countdown.timeZone, MoBotDatabase.replaceChars(countdown.text), countdown.repeating, countdown.channelID))
  else:
    moBotDB.cursor.execute("""
      INSERT INTO MoBot.countdowns
        (channel_id, guild_id, guild_name, end_datetime, time_zone, text, repeating)
      VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
    """ % (countdown.channelID, guild.id, MoBotDatabase.replaceChars(guild.name), countdown.endDatetime, countdown.timeZone, MoBotDatabase.replaceChars(countdown.text), countdown.repeating))
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end updateCountdownInfo

async def editEditorValue(message, payload, clockType):
  embed = message.embeds[0].to_dict()
  field = embed["fields"][0]
  fieldName = field["name"]
  fieldValue = field["value"]
  pageNumber = int(embed["footer"]["text"].split("/")[0].split(" ")[1].strip())

  if (clockType == "countdown"):
    countdown = await getCountdownFromOverview(message)

    endDatetime = datetime.strptime(countdown.endDatetime, "%m/%d/%Y %H:%M")
    year = endDatetime.year
    month = endDatetime.month
    day = endDatetime.day
    hour = endDatetime.hour
    minute = endDatetime.minute

    isDouble = (payload.emoji.name == "⏫" or payload.emoji.name == "⏬")

    if (payload.emoji.name == "🔼" or payload.emoji.name == "⏫"):
      if (fieldName == "Year"):
        year = int(fieldValue) + 1

      elif (fieldName == "Month"):
        if (isDouble):
          month = int(fieldValue) + 2
        else:
          month = int(fieldValue) + 1
        if (month > 12):
          month = 1

      elif (fieldName == "Day"):
        if (isDouble):
          day = int(fieldValue) + 7
        else:
          day = int(fieldValue) + 1
        try:
          datetime(year, month, day, hour, minute)
        except ValueError:
          day = 1

      elif ("Hour" in fieldName):
        if (isDouble):
          hour = int(fieldValue) + 4
        else:
          hour = int(fieldValue) + 1
        if (hour > 23):
          hour = 0

      elif (fieldName == "Minute"):
        if (isDouble):
          minute = int(fieldValue) + 10
        else:
          minute = int(fieldValue) + 1
        if (minute > 59):
          minute = 0

      elif (fieldName == "Time Zone"):
        countdown.timeZone = timeZones[timeZones.index(fieldValue) - (len(timeZones) - 1)]
        
      elif (fieldName == "Repeating"):
        countdown.repeating = repeatingOptions[repeatingOptions.index(fieldValue) - (len(repeatingOptions) - 1)]

    elif (payload.emoji.name == "🔽" or payload.emoji.name == "⏬"):
      if (fieldName == "Year"):
        year = int(fieldValue) - 1

      elif (fieldName == "Month"):
        if (isDouble):
          month = int(fieldValue) - 2
        else:
          month = int(fieldValue) - 1
        if (month < 1):
          month = 12

      elif (fieldName == "Day"):
        if (isDouble):
          day = int(fieldValue) - 7
        else:
          day = int(fieldValue) - 1
        try:
          datetime(year, month, day, hour, minute)
        except ValueError:
          day = (datetime(year, month, 1, hour, minute) + relativedelta(months=+1) - timedelta(days=1)).day

      elif ("Hour" in fieldName):
        if (isDouble):
          hour = int(fieldValue) - 4
        else:
          hour = int(fieldValue) - 1
        if (hour < 0):
          hour = 23

      elif (fieldName == "Minute"):
        if (isDouble):
          minute = int(fieldValue) - 10
        else:
          minute = int(fieldValue) - 1
        if (minute < 0):
          minute = 59

      elif (fieldName == "Time Zone"):
        countdown.timeZone = timeZones[timeZones.index(fieldValue) - 1]
          
      elif (fieldName == "Repeating"):
        countdown.repeating = repeatingOptions[repeatingOptions.index(fieldValue) - 1]

    countdown.endDatetime = datetime(year, month, day, hour, minute).strftime("%m/%d/%Y %H:%M")

    overview = await getOverviewFromCountdown(message, countdown, countdown.channelID)
    await message.edit(content=overview)

  elif (clockType == "clock"):
    clock = await getClockFromOverview(message)

    if (payload.emoji.name == "🔼" or payload.emoji.name == "🔽"):
      if (fieldName == "Format"):
        if (clock.timeFormat == "24-hour"):
          clock.timeFormat = "24-hour + date"
        elif (clock.timeFormat == "24-hour + date"):
          clock.timeFormat = "12-hour"
        elif (clock.timeFormat == "12-hour"):
          clock.timeFormat = "12-hour + date"
        elif (clock.timeFormat == "12-hour + date"):
          clock.timeFormat = "24-hour"
      
      else:
        if (payload.emoji.name == "🔽"):
          clock.timeZone = timeZones[timeZones.index(fieldValue) - 1]
        else:
          clock.timeZone = timeZones[timeZones.index(fieldValue) - (len(timeZones) - 1)]

    overview = await getOverviewFromClock(message, clock, clock.channelID)
    await message.edit(content=overview)

  editorPages["Page " + str(pageNumber)] = {
    "Header" : fieldName,
    "Fields" : [
      [fieldName, fieldValue]
    ]
  }

  if (clockType == "countdown"):
    await prepareEditor(message, clockType, countdown.channelID, pageNumber, message.id)
  else:
    await prepareEditor(message, clockType, clock.channelID, pageNumber, message.id)
# end editEditorValue

async def closeEditor(message, payload, clockType, channelID, isEditor):

  clockType = "C" + clockType[1:]
  if (isEditor):
    if (payload.emoji.name == "❌"):
      embed = discord.Embed(colour=0x36393f)
      embed.set_author(name=clockType + " Editor")
      embed.add_field(name="Close Editor", value="Are you sure you want to close the " + clockType + " Editor? All unsaved changes will be lost.", inline=False)

      await message.edit(embed=embed)

      await message.remove_reaction("🗑", message.guild.get_member(moBot))
      await message.remove_reaction("◀", message.guild.get_member(moBot))
      await message.remove_reaction("▶", message.guild.get_member(moBot))
      await message.remove_reaction("🔼", message.guild.get_member(moBot))
      await message.remove_reaction("⏫", message.guild.get_member(moBot))
      await message.remove_reaction("⏬", message.guild.get_member(moBot))
      await message.remove_reaction("🔽", message.guild.get_member(moBot))

    elif (payload.emoji.name == "🗑"):
      embed = discord.Embed(colour=0x36393f)
      embed.set_author(name=clockType + " Editor")
      embed.add_field(name="Delete " + clockType, value="Are you sure you want to delete the " + clockType + "?", inline=False)

      await message.edit(embed=embed)

      await message.remove_reaction("🗑", message.guild.get_member(moBot))
      await message.remove_reaction("◀", message.guild.get_member(moBot))
      await message.remove_reaction("▶", message.guild.get_member(moBot))
      await message.remove_reaction("🔼", message.guild.get_member(moBot))
      await message.remove_reaction("⏫", message.guild.get_member(moBot))
      await message.remove_reaction("⏬", message.guild.get_member(moBot))
      await message.remove_reaction("🔽", message.guild.get_member(moBot))
  else:
    if (payload.emoji.name == "✅"):
      embed = message.embeds[0].to_dict()
      author = embed["author"]["name"]
      field = embed["fields"][0]
      fieldName = field["name"]
      if ("Editor" in author):
        if ("Delete" in fieldName):
          await delete(clockType, channelID)

          try:
            channel = message.guild.get_channel(int(channelID))
            await channel.delete()
          except:
            pass

        history = message.channel.history(limit=3)
        async for msg in history:
          if (str(channelID) in msg.content):
            await msg.delete()

    elif (payload.emoji.name == "❌"):
      await prepareEditor(message, clockType, channelID, 1, message.id)
      await message.add_reaction("🗑")
      await message.add_reaction("◀")
      await message.add_reaction("▶")

async def openEditor(message, editorPages, pageNumber, editorID, clockType, countdown, channelID):
  moBotMessages = []

  if (clockType == "countdown"):
    overview = await getOverviewFromCountdown(message, countdown, channelID)
  elif (clockType == "clock"):
    overview = await getOverviewFromClock(message, countdown, channelID)

  editor = discord.Embed(colour=0x36393f)
  editor.set_author(name=editorPages["Author"])

  for i in range(0, len(editorPages["Page " + str(pageNumber)]["Fields"])):
    field = editorPages["Page " + str(pageNumber)]["Fields"][i]
    editor.add_field(name=field[0], value=field[1], inline=False)
  
  editor.set_footer(text="\nPage " + str(pageNumber) + "/" + str(editorPages["Number of Pages"]))
  editorMsg = None
  if (editorID == 0):
    editorMsg = await message.channel.send(content=overview, embed=editor)
    await editorMsg.add_reaction("✅")
    await editorMsg.add_reaction("❌")
    await editorMsg.add_reaction("🗑")
    await editorMsg.add_reaction("◀")
    await editorMsg.add_reaction("▶")

  else:
    editorMsg = await message.channel.fetch_message(editorID)
    await editorMsg.edit(embed=editor)

  if (pageNumber > 1):
    await editorMsg.add_reaction("🔼")
    if (clockType == "countdown"):
      await message.add_reaction("⏫")
      await message.add_reaction("⏬")
    await editorMsg.add_reaction("🔽")
  else:
    await editorMsg.remove_reaction("🔼", message.guild.get_member(moBot))
    if (clockType == "countdown"):
      await message.remove_reaction("⏫", message.guild.get_member(moBot))
      await message.remove_reaction("⏬", message.guild.get_member(moBot))
    await editorMsg.remove_reaction("🔽", message.guild.get_member(moBot))
# end openEditor

async def prepareEditor(message, clockType, channelID, pageNumber, editorID):
  if (channelID is None): # when a channel couldn't be created
    return

  moBotMessages = []
  if (clockType == "countdown"):
    if (editorID == 0):
      countdown = await getCountdown(message, str(message.guild.id), channelID)

      if (countdown is None):  
        channel = message.guild.get_channel(int(channelID))
        try:
          await channel.edit(name="Edit This Text:")
        except discord.errors.Forbidden:
          await message.channel.send("**Not Enough Permissions**\n<@%s> does not have permissions to edit channels." % moBot)
          return
        now = datetime.now()
        countdown = Countdown(
          str(channel.id),
          now.strftime("%m/%d/%Y %H:%M"),
          "Europe/London",
          "Edit This Text:",
          "None"
        )
        await updateCountdownInfo(message.guild, countdown)
    else:
      countdown = await getCountdownFromOverview(message)

    editorPages["Author"] = "Countdown Editor"

    # instructions
    editorPages["Page 1"] = {
      "Header" : "Instructions",
      "Fields" : [
        ["Instructions", "Use the ◀/▶ to maneuver through the editor.\nUse the 🔼/🔽 to adjust the values.\nClick the ✅ to save. (May take up to a minute to update countdown)\nClick the ❌ when you're finished.\nClick the 🗑 to delete the countdown - this will delete the channel too."]
      ]
    }
    editorPages["Number of Pages"] = 1

    # year
    editorPages["Page 2"] = {
      "Header" : "Year",
      "Fields" : [
        ["Year", countdown.endDatetime.split("/")[2].split(" ")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # month
    editorPages["Page 3"] = {
      "Header" : "Month",
      "Fields" : [
        ["Month", countdown.endDatetime.split("/")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # day
    editorPages["Page 4"] = {
      "Header" : "Day",
      "Fields" : [
        ["Day", countdown.endDatetime.split("/")[1].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # hour (24 hour)
    editorPages["Page 5"] = {
      "Header" : "Hour (24-Hour)",
      "Fields" : [
        ["Hour (24-Hour)", countdown.endDatetime.split(" ")[1].split(":")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # minute
    editorPages["Page 6"] = {
      "Header" : "Minute",
      "Fields" : [
        ["Minute", countdown.endDatetime.split(":")[1].split("\n")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # time zone
    editorPages["Page 7"] = {
      "Header" : "Time Zone",
      "Fields" : [
        ["Time Zone", countdown.timeZone]
      ]
    }
    editorPages["Number of Pages"] += 1

    # repeating
    editorPages["Page 8"] = {
      "Header" : "Repeating",
      "Fields" : [
        ["Repeating", countdown.repeating]
      ]
    }
    editorPages["Number of Pages"] += 1

    await openEditor(message, editorPages, pageNumber, editorID, clockType, countdown, channelID)
  elif (clockType == "clock"):
    if (editorID == 0):
      clock = await getClock(message, str(message.guild.id), channelID)

      if (clock is None):
        channel = message.guild.get_channel(int(channelID))
        try:
          await channel.edit(name="New Clock Channel")
        except discord.errors.Forbidden:
          await message.channel.send("**Not Enough Permissions**\n<@%s> does not have permissions to edit channels." % moBot)
          return
        now = datetime.now()
        clock = Clock(
          str(channel.id),
          "24-hour",
          "Europe/London"
        )
        await updateClockInfo(message.guild, clock)
    else:
      clock = await getClockFromOverview(message)

    editorPages["Author"] = "Clock Editor"

    # instructions
    editorPages["Page 1"] = {
      "Header" : "Instructions",
      "Fields" : [
        ["Instructions", "Use the ◀/▶ to maneuver through the editor.\nUse the 🔼/🔽 to adjust the values.\nClick the ✅ to save. (May take up to a minute to update clock)\nClick the ❌ when you're finished.\nClick the 🗑 to delete the clock - this will delete the channel too."]
      ]
    }
    editorPages["Number of Pages"] = 1

    # format
    editorPages["Page 2"] = {
      "Header" : "Format",
      "Fields" : [
        ["Format", clock.timeFormat],
      ]
    }
    editorPages["Number of Pages"] += 1

    # time zone
    editorPages["Page 3"] = {
      "Header" : "Time Zone",
      "Fields" : [
        ["Time Zone", clock.timeZone]
      ]
    }
    editorPages["Number of Pages"] += 1

    await openEditor(message, editorPages, pageNumber, editorID, clockType, clock, channelID)
# end prepareEditor

async def createChannel(message, clockType):
  guild = message.guild
  channelName = "Edit This Text:" if clockType.lower() == "countdown" else "New Clock Channel"
  try:
    channel = await guild.create_voice_channel(channelName)
    await message.channel.send("**Channel Created**\nIt should be near the top of the channel list.", delete_after=10)
    return channel.id
  except discord.errors.Forbidden:
    await message.channel.send("**Not Enough Permissions**\n<@%s> does not have permissions to create channels." % moBot)
    return None
# end createChannel

async def checkClockAccuracy(client):
  n = datetime.now()
  guild = client.get_guild(moBotSupport)
  channel = guild.get_channel(clockChannel)
  timeZone = channel.name.split(" ")[1]
  
  if(n.minute - int(channel.name.split(":")[1][:2]) > 2):
    await RandomSupport.sendMessageToMo("**CLOCKS AREN'T UPDATED**\nCurrent Time: `%s`\nClock: `%s`" % (n.strftime("%H:%M%p " + timeZone + " - %b %d" ), channel.name), client, mo)
# end checkClockAccuracy