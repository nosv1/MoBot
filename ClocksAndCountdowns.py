import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import SecretStuff

moBot = "449247895858970624"

editorPages = {
  "Author" : "",
  "Number of Pages" : 0,
}

arrows = "🔼🔽⏫⏬"
repeatingOptions = [
  "Skip", "None", "Hourly", "Daily", "Weekly", "Bi-Weekly", "Monthly", "Yearly"
]
timeZones = [
  "US/Eastern", "UTC", "Europe/London", "Australia/Queensland"
]


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

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client, clockType): 
  if (payload.user_id != int(moBot)):
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
          await updateCountdownInfo(message.guild, await getCountdownFromOverview(message, clockType))
          msg = await message.channel.send("Countdown Saved - Expect update within 1 minute")
        else:
          await updateClockInfo(message.guild, await getClockFromOverview(message, clockType))
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

async def delete(clockType, channelID):
  workbook = await openSpreadsheet()
  if (clockType == "countdown"):
    countdownsSheet = workbook.worksheet("Countdowns")
    countdownsRange = countdownsSheet.range("A2:G" + str(countdownsSheet.row_count))

    for i in range(0, len(countdownsRange), 7):
      if (countdownsRange[i+2].value == str(channelID)):
        for j in range(i, len(countdownsRange)):
          try:
            countdownsRange[j].value = countdownsRange[j+7].value
          except IndexError:
            break
        break

    countdownsSheet.update_cells(countdownsRange, value_input_option="USER_ENTERED")

  elif (clockType == "clock"):
    clocksSheet = workbook.worksheet("Clocks")
    clocksRange = clocksSheet.range("A2:E" + str(clocksSheet.row_count))

    for i in range(0, len(clocksRange), 5):
      if (clocksRange[i+2].value == str(channelID)):
        for j in range(i, len(clocksRange)):
          try:
            clocksRange[j].value = clocksRange[j+5].value
          except IndexError:
            break
        break

    clocksSheet.update_cells(clocksRange, value_input_option="USER_ENTERED")
# end delete

async def getClock(message, guildID, channelID):
  workbook = await openSpreadsheet()
  clocksSheet = workbook.worksheet("Clocks")
  clocksTable = clocksSheet.range("A2:E" + str(clocksSheet.row_count))

  clock = {}

  clockFormats = {
    "%I:%M%p %Z" : "12-hour",
    "%I:%M%p %Z - - %b %d" : "12-hour + date",
    "%H:%M %Z" : "24-hour",
    "%H:%M %Z - %b %d" : "24-hour + date",
  }

  for i in range(0, len(clocksTable), 5):
    if (clocksTable[i].value != ""):
      if (clocksTable[i+1].value == guildID and clocksTable[i+2].value == channelID):
        clock["Format"] = clockFormats[clocksTable[i+3].value]
        clock["Time Zone"] = clocksTable[i+4].value
        break
    else:
      break

  return clock
# end getClock

async def getCountdown(message, guildID, channelID):
  workbook = await openSpreadsheet()
  countdownsSheet = workbook.worksheet("Countdowns")
  countdownsTable = countdownsSheet.range("A2:G" + str(countdownsSheet.row_count))

  countdown = {}

  for i in range(0, len(countdownsTable), 7):
    if (countdownsTable[i].value != ""):
      if (countdownsTable[i+1].value == guildID and countdownsTable[i+2].value == channelID):
        countdown["End Datetime"] = countdownsTable[i+3].value
        countdown["Time Zone"] = countdownsTable[i+4].value
        countdown["Text"] = countdownsTable[i+5].value
        countdown["Repeating"] = countdownsTable[i+6].value
        break
    else:
      break

  return countdown
# end getCountdown

async def getClockFromOverview(message, clockType):
  mc = message.content

  clock = {}
  clock["Channel ID"] = mc.split("**Channel ID**: ")[1].split("\n")[0].strip()
  clock["Format"] = mc.split("**Format**: ")[1].split("\n")[0].strip()
  clock["Time Zone"] = mc.split("**Time Zone**: ")[1].split("\n")[0].strip()

  return clock
# end getClockFromOverview

async def getCountdownFromOverview(message, clockType):
  mc = message.content

  countdown = {}
  countdown["Channel ID"] = mc.split("**Channel ID**: ")[1].split("\n")[0].strip()
  countdown["End Datetime"] = mc.split("**End Datetime**: ")[1].split("\n")[0].strip()
  countdown["Time Zone"] = mc.split("**Time Zone**: ")[1].split("\n")[0].strip()
  countdown["Text"] = mc.split("**Text**: ")[1].split("\n")[0].strip()
  countdown["Repeating"] = mc.split("**Repeating**: ")[1].split("\n")[0].strip()

  return countdown
# end getCountdownFromOverview

async def getOverviewFromClock(message, clock, channelID):
  overview = "**Overview**\n"
  overview += "  **Channel ID**: " + str(channelID) + "\n"
  overview += "  **Format**: " + clock["Format"] + "\n"
  overview += "  **Time Zone**: " + clock["Time Zone"] + "\n"

  return overview
# end getOverviewFromClock

async def getOverviewFromCountdown(message, countdown, channelID):
  overview = "**Overview**\n"
  overview += "  **Channel ID**: " + str(channelID) + "\n"
  overview += "  **End Datetime**: " + countdown["End Datetime"] + "\n"
  overview += "  **Time Zone**: " + countdown["Time Zone"] + "\n"
  overview += "  **Text**: " + countdown["Text"] + "\n"
  overview += "  **Repeating**: " + countdown["Repeating"] + "\n"

  return overview
# end getOverviewFromCountdown

async def updateClockInfo(guild, clock):
  workbook = await openSpreadsheet()
  clocksSheet = workbook.worksheet("Clocks")
  clocksTable = clocksSheet.range("A2:E" + str(clocksSheet.row_count))

  clockFormats = {
    "24-hour" : "%H:%M %Z",
    "24-hour + date" : "%H:%M %Z - %b %d",
    "12-hour" : "%I:%M%p %Z",
    "12-hour + date" : "%I:%M%p %Z - %b %d",
  }

  for i in range(0, len(clocksTable), 5):
    if (clocksTable[i+2].value == str(clock["Channel ID"])):
      clocksTable[i+3].value = clockFormats[clock["Format"]]
      clocksTable[i+4].value = clock["Time Zone"]
      break
    if (clocksTable[i].value == ""):
      clocksTable[i].value = guild.name
      clocksTable[i+1].value = str(guild.id)
      clocksTable[i+2].value = clock["Channel ID"]
      clocksTable[i+3].value = clockFormats[clock["Format"]]
      clocksTable[i+4].value = clock["Time Zone"]
      break
  
  clocksSheet.update_cells(clocksTable, value_input_option="USER_ENTERED")
# end updateClockInfo

async def updateCountdownInfo(guild, countdown):
  workbook = await openSpreadsheet()
  countdownsSheet = workbook.worksheet("Countdowns")
  countdownsTable = countdownsSheet.range("A2:G" + str(countdownsSheet.row_count))

  for i in range(0, len(countdownsTable), 7):
    if (countdownsTable[i+2].value == str(countdown["Channel ID"])):
      countdownsTable[i+3].value = countdown["End Datetime"]
      countdownsTable[i+4].value = countdown["Time Zone"]
      countdownsTable[i+5].value = countdown["Text"]
      countdownsTable[i+6].value = countdown["Repeating"]
      break
    if (countdownsTable[i].value == ""):
      countdownsTable[i].value = guild.name
      countdownsTable[i+1].value = str(guild.id)
      countdownsTable[i+2].value = countdown["Channel ID"]
      countdownsTable[i+3].value = countdown["End Datetime"]
      countdownsTable[i+4].value = countdown["Time Zone"]
      countdownsTable[i+5].value = countdown["Text"]
      countdownsTable[i+6].value = countdown["Repeating"]
      break
  
  countdownsSheet.update_cells(countdownsTable, value_input_option="USER_ENTERED")
# end updateCountdownInfo

async def editEditorValue(message, payload, clockType):
  embed = message.embeds[0].to_dict()
  field = embed["fields"][0]
  fieldName = field["name"]
  fieldValue = field["value"]
  pageNumber = int(embed["footer"]["text"].split("/")[0].split(" ")[1].strip())

  if (clockType == "countdown"):
    countdown = await getCountdownFromOverview(message, clockType)

    endDatetime = datetime.strptime(countdown["End Datetime"], "%m/%d/%Y %H:%M")
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
        countdown["Time Zone"] = timeZones[timeZones.index(fieldValue) - (len(timeZones) - 1)]
        
      elif (fieldName == "Repeating"):
        countdown["Repeating"] = repeatingOptions[repeatingOptions.index(fieldValue) - (len(repeatingOptions) - 1)]

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
        countdown["Time Zone"] = timeZones[timeZones.index(fieldValue) - 1]
          
      elif (fieldName == "Repeating"):
        countdown["Repeating"] = repeatingOptions[repeatingOptions.index(fieldValue) - 1]

    countdown["End Datetime"] = datetime(year, month, day, hour, minute).strftime("%m/%d/%Y %H:%M")

    overview = await getOverviewFromCountdown(message, countdown, countdown["Channel ID"])
    await message.edit(content=overview)

  elif (clockType == "clock"):
    clock = await getClockFromOverview(message, clockType)

    if (payload.emoji.name == "🔼" or payload.emoji.name == "🔽"):
      if (fieldName == "Format"):
        if (clock["Format"] == "24-hour"):
          clock["Format"] = "24-hour + date"
        elif (clock["Format"] == "24-hour + date"):
          clock["Format"] = "12-hour"
        elif (clock["Format"] == "12-hour"):
          clock["Format"] = "12-hour + date"
        elif (clock["Format"] == "12-hour + date"):
          clock["Format"] = "24-hour"
      
      else:
        if (payload.emoji.name == "🔽"):
          clock["Time Zone"] = timeZones[timeZones.index(fieldValue) - 1]
        else:
          clock["Time Zone"] = timeZones[timeZones.index(fieldValue) - (len(timeZones) - 1)]

    overview = await getOverviewFromClock(message, clock, clock["Channel ID"])
    await message.edit(content=overview)

  editorPages["Page " + str(pageNumber)] = {
    "Header" : fieldName,
    "Fields" : [
      [fieldName, fieldValue]
    ]
  }

  if (clockType == "countdown"):
    await prepareEditor(message, clockType, countdown["Channel ID"], pageNumber, message.id)
  else:
    await prepareEditor(message, clockType, clock["Channel ID"], pageNumber, message.id)
# end editEditorValue

async def closeEditor(message, payload, clockType, channelID, isEditor):

  clockType = "C" + clockType[1:]
  if (isEditor):
    if (payload.emoji.name == "❌"):
      embed = discord.Embed(colour=0x36393f)
      embed.set_author(name=clockType + " Editor")
      embed.add_field(name="Close Editor", value="Are you sure you want to close the " + clockType + " Editor? All unsaved changes will be lost.", inline=False)

      await message.edit(embed=embed)

      await message.remove_reaction("🗑", message.guild.get_member(int(moBot)))
      await message.remove_reaction("◀", message.guild.get_member(int(moBot)))
      await message.remove_reaction("▶", message.guild.get_member(int(moBot)))
      await message.remove_reaction("🔼", message.guild.get_member(int(moBot)))
      await message.remove_reaction("⏫", message.guild.get_member(int(moBot)))
      await message.remove_reaction("⏬", message.guild.get_member(int(moBot)))
      await message.remove_reaction("🔽", message.guild.get_member(int(moBot)))

    elif (payload.emoji.name == "🗑"):
      embed = discord.Embed(colour=0x36393f)
      embed.set_author(name=clockType + " Editor")
      embed.add_field(name="Delete " + clockType, value="Are you sure you want to delete the " + clockType + "?", inline=False)

      await message.edit(embed=embed)

      await message.remove_reaction("🗑", message.guild.get_member(int(moBot)))
      await message.remove_reaction("◀", message.guild.get_member(int(moBot)))
      await message.remove_reaction("▶", message.guild.get_member(int(moBot)))
      await message.remove_reaction("🔼", message.guild.get_member(int(moBot)))
      await message.remove_reaction("⏫", message.guild.get_member(int(moBot)))
      await message.remove_reaction("⏬", message.guild.get_member(int(moBot)))
      await message.remove_reaction("🔽", message.guild.get_member(int(moBot)))
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
    await editorMsg.remove_reaction("🔼", message.guild.get_member(int(moBot)))
    if (clockType == "countdown"):
      await message.remove_reaction("⏫", message.guild.get_member(int(moBot)))
      await message.remove_reaction("⏬", message.guild.get_member(int(moBot)))
    await editorMsg.remove_reaction("🔽", message.guild.get_member(int(moBot)))
# end openEditor

async def prepareEditor(message, clockType, channelID, pageNumber, editorID):
  moBotMessages = []
  if (clockType == "countdown"):
    if (editorID == 0):
      countdown = await getCountdown(message, str(message.guild.id), channelID)

      if (len(countdown) == 0):  
        channel = message.guild.get_channel(int(channelID))
        await channel.edit(name="Edit This Text:")
        now = datetime.now()
        countdown = {
          "Channel ID" : str(channel.id),
          "End Datetime" : now.strftime("%m/%d/%Y %H:%M"),
          "Time Zone" : "Europe/London",
          "Text" : "Edit This Text:",
          "Repeating" : "None"
        }
        await updateCountdownInfo(message.guild, countdown)
    else:
      countdown = await getCountdownFromOverview(message, clockType)

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
        ["Year", countdown["End Datetime"].split("/")[2].split(" ")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # month
    editorPages["Page 3"] = {
      "Header" : "Month",
      "Fields" : [
        ["Month", countdown["End Datetime"].split("/")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # day
    editorPages["Page 4"] = {
      "Header" : "Day",
      "Fields" : [
        ["Day", countdown["End Datetime"].split("/")[1].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # hour (24 hour)
    editorPages["Page 5"] = {
      "Header" : "Hour (24-Hour)",
      "Fields" : [
        ["Hour (24-Hour)", countdown["End Datetime"].split(" ")[1].split(":")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # minute
    editorPages["Page 6"] = {
      "Header" : "Minute",
      "Fields" : [
        ["Minute", countdown["End Datetime"].split(":")[1].split("\n")[0].strip()]
      ]
    }
    editorPages["Number of Pages"] += 1

    # time zone
    editorPages["Page 7"] = {
      "Header" : "Time Zone",
      "Fields" : [
        ["Time Zone", countdown["Time Zone"]]
      ]
    }
    editorPages["Number of Pages"] += 1

    # repeating
    editorPages["Page 8"] = {
      "Header" : "Repeating",
      "Fields" : [
        ["Repeating", countdown["Repeating"]]
      ]
    }
    editorPages["Number of Pages"] += 1

    await openEditor(message, editorPages, pageNumber, editorID, clockType, countdown, channelID)
  elif (clockType == "clock"):
    if (editorID == 0):
      clock = await getClock(message, str(message.guild.id), channelID)

      if (len(clock) == 0):
        channel = message.guild.get_channel(int(channelID))
        await channel.edit(name="New Clock Channel")
        now = datetime.now()
        clock = {
          "Channel ID" : str(channel.id),
          "Format" : "24-hour",
          "Time Zone" : "Europe/London",
        }
        await updateClockInfo(message.guild, clock)
    else:
      clock = await getClockFromOverview(message, clockType)

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
        ["Format", clock["Format"]],
      ]
    }
    editorPages["Number of Pages"] += 1

    # time zone
    editorPages["Page 3"] = {
      "Header" : "Time Zone",
      "Fields" : [
        ["Time Zone", clock["Time Zone"]]
      ]
    }
    editorPages["Number of Pages"] += 1

    await openEditor(message, editorPages, pageNumber, editorID, clockType, clock, channelID)
# end prepareEditor

async def createChannel(message, clockType):
  guild = message.guild
  channelName = "Edit This Text:" if clockType.lower() == "countdown" else "New Clock Channel"
  channel = await guild.create_voice_channel(channelName)
  return channel.id
# end createChannel

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1Cz-NGa_mqSIw-Ae4tU1DX1AOsS-zC_5l1HLiIbVjr4M")
  return workbook
# end openSpreadsheet