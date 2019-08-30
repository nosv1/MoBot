# MoBot made by Mo#9991

import discord # needed for discord
import asyncio # needed for discord and proper delays, usually you use asyncio.sleep(seconds), but when your functions are asynchronous, you gotta use 'await asyncio.sleep(seconds)'
from datetime import datetime, timedelta # needed for datetime stuff, timedelta lets us add and subtract dates easily
import time # needed for non asynchronous delays as said before
from pytz import timezone, utc # used to convert timezones
import gspread # used for google sheets and python integration
from oauth2client.service_account import ServiceAccountCredentials # allows connection to a google sheet with permissions
import sys # used for console printing
import random # used for random number generation
from dateutil.relativedelta import relativedelta
import traceback
import websockets
import httplib2
import feedparser
import SecretStuff

import ClocksAndCountdowns
import EventScheduler

import MoBotTimeZones
  
client = discord.Client() # discord.Client is like the user form of the bot, it knows the guilds and permissions and stuff of the bot

# these are 'statuses' for the bot, futher down I've got 50/50 random gen, to change status on every message sent
botsByMo = discord.Activity(type=discord.ActivityType.streaming, name="Bots by Mo#9991")
donate = discord.Activity(type=discord.ActivityType.watching, name="@MoBot donate")
server = discord.Activity(type=discord.ActivityType.watching, name="@MoBot server")
moBotHelp = discord.Activity(type=discord.ActivityType.watching, name="@MoBot help")

moBotSupport = 467239192007671818
mo = 405944496665133058

spaceChar = "⠀"

donations = {
  "TE Garrett#9569" : {
    "Date" : datetime(2019, 6, 12),
    "Donation" : 26 # 2 on 6/12, 15 on 7/9
  }
}

started = False
# when bot is first online
@client.event
async def on_ready():
  global started
  if (not started):
    print ("\nMoBotLoop is online - " + str(datetime.now()) + "\n")
    started = True
  else:
    sys.exit()
  
  mobotLog = client.get_guild(moBotSupport).get_channel(604099911251787776) # mobot log
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBotLoop Restarted")
  if (mobotLog != None):
    await mobotLog.send(embed=embed)
    await main(client)
# end on_ready

async def main(client):
  try:
    eventSheet, eventRange = await EventScheduler.getEventRange()
    scheduledEvents = await EventScheduler.getScheduledEvents(eventSheet, eventRange)
    print ("Scheduled Events Received")
    
    workbook = await openGuildClocksSpreadsheet()
    clocks = await getGuildClocks(workbook)
    print ("Clocks Received")
    countdowns = await getGuildCountdowns(workbook)
    print ("Countdowns Received")
  except httplib2.ServerNotFoundError:
    pass
  except gspread.exceptions.APIError:
    pass

  print ()
  lastSecond = 0
  while (True):
    try:
      currentTime = datetime.now() + timedelta(seconds=5)
      second = currentTime.second
      if (lastSecond == second):
        await asyncio.sleep(1)
        continue
      else:
        lastSecond = second

      sys.stdout.write("\rCurrent Time: " + str(currentTime))
      sys.stdout.flush() # allows rewriting the line above in the console, basically it keeps replacing the text instead of having a bunch of lines


      if (second % 30 == 0): # check for every 30 seconds
        await updateGuildCountdowns(client, currentTime, countdowns)
        await updateGuildClocks(client, currentTime, clocks)
        await updateMoBotStatus(client)

        if (second == 0):
          if (currentTime.minute % 5 == 0): # check for new scheduled messages every 5 minutes
            try:
              eventSheet, eventRange = await EventScheduler.getEventRange()
              scheduledEvents = await EventScheduler.getScheduledEvents(eventSheet, eventRange)
            except gspread.exceptions.APIError:
              print ("\nCould Not Get Scheduled Events\n")
            
          for event in scheduledEvents:
            eventTime = await EventScheduler.getEventTime(event)
            if (eventTime < currentTime):
              scheduledEvents = await EventScheduler.performScheduledEvent(event, client)

          try:
            workbook = await openGuildClocksSpreadsheet()
            clocks = await getGuildClocks(workbook)
            countdowns = await getGuildCountdowns(workbook)
          except gspread.exceptions.APIError:
            print ("\nCould Not Get Clocks or Countdowns\n")

          if (currentTime < donations["TE Garrett#9569"]["Date"] + relativedelta(months=int(donations["TE Garrett#9569"]["Donation"] / 2))):
            await checkTEGarrettPointApplications(datetime.now() - timedelta(hours=2), client)
          else:
            await client.get_user(int(mo)).send("<@97202414490226688>'s donation has expired.")

          '''
          if ((await convertTime(currentTime, "Europe/London", "to")).hour % 6 == 0 or currentTime.minute >= 32):
            nobleLeaguesGuild = client.get_guild(437936224402014208)
            nobleLeaugesDestination = nobleLeaguesGuild.get_channel(519260837727436810) # bot-setup

            embed = discord.Embed(color=int("0xd1d1d1", 16))
            embed.set_author(name="Noble Community News")

            check out.txt
            url = "https://noblecommunity.altervista.org/feed/"
            feed = feedparser.parse(url)
            for entry in feed.entries:
              fieldName = entry.title
              fieldValue = entry.summary
              embed.add_field(name=fieldName, value=fieldValue, inline=False)
            await nobleLeaugesDestination.send(embed=embed)'''
          
          await updateTimeZoneList(currentTime)

    except websockets.exceptions.ConnectionClosed:
      await asyncio.sleep(5)
    except gspread.exceptions.APIError:
      pass
    except:
      await asyncio.sleep(5)
      try:
        await client.get_user(int(mo)).send("MoBotLoop Error!```" + str(traceback.format_exc()) + "```")
      except:
        print ("\n" + str(datetime.now()) + "\nError -- " + str(traceback.format_exc()))
      sys.exit()

  # end infinte loop
# end main

async def checkTEGarrettPointApplications(nowPacificTime, client):
  guild = client.get_guild(237064972583174144)
  pointsTest = 588443266383347742
  points = 338844984725995522
  if (nowPacificTime >= datetime(2019, 8, 1)):
    pointsChannel = guild.get_channel(points) 
  else:
    pointsChannel = guild.get_channel(pointsTest) 

  pointApplicationsWorkbook = await openTEGarrettPointApplicationsSpreadsheet()

  formResponsesSheet = pointApplicationsWorkbook.worksheet("Form Responses 1")
  dateRange = formResponsesSheet.range("A2:A" + str(formResponsesSheet.row_count))
  checkMarksRange = formResponsesSheet.range("B2:B" + str(formResponsesSheet.row_count))
  picutresRange = formResponsesSheet.range("C2:C" + str(formResponsesSheet.row_count))
  nameRange = formResponsesSheet.range("T2:Y" + str(formResponsesSheet.row_count))

  randomLogsWorkbook = await openRandomLogs()
  pointApplicationsLogSheet = randomLogsWorkbook.worksheet("TE Garrett Point Applications")
  pointApplicationsLogRange = pointApplicationsLogSheet.range("A2:A" + str(pointApplicationsLogSheet.row_count))

  logUpdated = False
  for i in range(len(checkMarksRange)):
    if (checkMarksRange[i].value == "TRUE"):
      blankRow = 0
      pictureSent = False
      for j in range(len(pointApplicationsLogRange)):
        if (dateRange[i].value == pointApplicationsLogRange[j].value):
          pictureSent = True
          break
        if (pointApplicationsLogRange[j].value == ""):
          blankRow = j
          break
      if (not pictureSent):
        picture = picutresRange[i].value
        reply = ""
        if ("http" in picture):
          for j in range(i*6, i*6+6): # based on col width of nameRange
            if (nameRange[j].value != ""):
              reply += nameRange[j].value + ", "
          if (reply != ""):
            reply = reply[:-2] + "\n"
          reply += picutresRange[i].value
          await pointsChannel.send(reply)
        pointApplicationsLogRange[blankRow].value = dateRange[i].value
        logUpdated = True

  if (logUpdated):
    pointApplicationsLogSheet.update_cells(pointApplicationsLogRange, value_input_option="USER_ENTERED")

async def updateMoBotStatus(client):
  # changing bot status based on rand gen
  rand = int(random.random() * 100)
  if (rand < 10): # 10%
    await client.change_presence(activity=botsByMo)
  elif (rand < 20): # 10%
    await client.change_presence(activity=server)
  elif (rand < 30): # 10%
    serverCount = discord.Activity(type=discord.ActivityType.watching, name=str(len(client.guilds)) + " servers")
    await client.change_presence(activity=serverCount)
  elif (rand >= 30): # 70%
    if (rand >= 65): # 50%
      await client.change_presence(activity=moBotHelp)
    else: # 50%
      await client.change_presence(activity=donate)

async def getGuildCountdowns(workbook):
  countdownsSheet = workbook.worksheet("Countdowns")

  countdownsTable = countdownsSheet.range("A2:G" + str(countdownsSheet.row_count))
  countdowns = {}

  for i in range(0, len(countdownsTable), 7):
    if (countdownsTable[i].value != ""):
      if (int(countdownsTable[i+1].value) not in countdowns):
        countdowns[int(countdownsTable[i+1].value)] = []

      countdowns[int(countdownsTable[i+1].value)].append({
          "Guild Name" : countdownsTable[i].value,
          "Channel ID" : int(countdownsTable[i+2].value),
          "End Datetime" : countdownsTable[i+3].value,
          "Time Zone" : countdownsTable[i+4].value,
          "Text" : countdownsTable[i+5].value,
          "Repeating" : countdownsTable[i+6].value
        })
    else:
      break

  return countdowns
# end getGuildCountdowns

async def getGuildClocks(workbook):
  clocksSheet = workbook.worksheet("Clocks")

  clocksTable = clocksSheet.range("A2:E" + str(clocksSheet.row_count))
  clocks = {}

  for i in range(0, len(clocksTable), 5):
    if (clocksTable[i].value != ""):
      if (int(clocksTable[i+1].value) not in clocks):
        clocks[int(clocksTable[i+1].value)] = []

      clocks[int(clocksTable[i+1].value)].append({
          "Guild Name" : clocksTable[i].value,
          "Channel ID" : int(clocksTable[i+2].value),
          "Format" : clocksTable[i+3].value,
          "Time Zone" : clocksTable[i+4].value
        })
    else:
      break

  return clocks
# end getGuildClocks

async def updateRepeatingCountdown(guild, endDatetime, countdown):
  repeatingOptions = {
    "Hourly" : 0,
    "Daily" : 1,
    "Weekly" : 7,
    "Bi-weekly" : 14,
    "Monthly" : 0,
    "Yearly" : 0
  }

  try:
    repeatingDays = repeatingOptions[countdown["Repeating"]]

    newEndDatetime = endDatetime + timedelta(days=repeatingDays)
    if (countdown["Repeating"] == "Hourly"):
      newEndDatetime = endDatetime + relativedelta(hours=1)
    elif (countdown["Repeating"] == "Monthly"):
      newEndDatetime = endDatetime + relativedelta(months=1)
    elif (countdown["Repeating"] == "Yearly"):
      newEndDatetime = endDatetime + relativedelta(years=1)
    countdown["End Datetime"] = newEndDatetime.strftime("%m/%d/%Y %H:%M")
    await ClocksAndCountdowns.updateCountdownInfo(guild, countdown)
  except KeyError:
    pass
# end updateRepeatingCountdown

async def updateGuildCountdowns(client, currentTime, countdowns):
  
  for guildID in countdowns:
    guild = client.get_guild(guildID)
    for countdown in countdowns[guildID]:
      tz = countdown["Time Zone"]
      endDatetime = datetime.strptime(countdown["End Datetime"], "%m/%d/%Y %H:%M")
      convertedEndTime = timezone(tz).localize(endDatetime).astimezone(timezone("US/Central"))
      convertedEndTime = datetime(convertedEndTime.year, convertedEndTime.month, convertedEndTime.day, convertedEndTime.hour, convertedEndTime.minute)
      td = convertedEndTime - currentTime

      timeDiff = {
        "Days" : td.days,
        "Hours" : 0,
        "Minutes" : 0,
      }

      timeDiff["Hours"], seconds = divmod(td.seconds, 3600)
      timeDiff["Minutes"], seconds = divmod(seconds, 60)
      if (timeDiff["Days"] < 2):
        timeDiff["Hours"] += timeDiff["Days"] * 24
        timeDiff["Days"] = 0
        if (timeDiff["Hours"] < 2):
          timeDiff["Minutes"] += timeDiff["Hours"] * 60
          timeDiff["Hours"] = 0
          if (timeDiff["Minutes"] < 2):
            seconds += timeDiff["Minutes"] * 60
            timeDiff["Minutes"] = 0
      
      seconds += 1
      if (seconds == 60):
        timeDiff["Minutes"] += 1

      countdownString = ""
      channelFound = False
      for channel in guild.voice_channels:
        if (channel.id == countdown["Channel ID"]):
          channelFound = True
          try:
            if (countdown["Repeating"] != "Skip"):
              if (timeDiff["Days"] > 1):
                countdownString = str(timeDiff["Days"] + round(timeDiff["Hours"] / 24, 1)) + " days"
              elif (timeDiff["Hours"] > 1):
                countdownString = str(timeDiff["Hours"] + round(timeDiff["Minutes"] / 60, 1)) + " hours"
              elif (timeDiff["Minutes"] > 1):
                countdownString = str(timeDiff["Minutes"] + round(((seconds - 60) * -1) / 60, 1)) + " minutes"
              elif (seconds > 0):
                countdownString = str(seconds) + " seconds"
              else:
                countdownString = "0 seconds"
                await updateRepeatingCountdown(guild, endDatetime, countdown)
              try:
                currentText = channel.name.split(":")[0]
              except IndexError:
                currentText = ""
              if (currentText != countdown["Text"]):
                countdown["Text"] = currentText
                await ClocksAndCountdowns.updateCountdownInfo(guild, countdown)
              await channel.edit(name=countdown["Text"].strip() + ": " + countdownString)
            else:
              await channel.edit(name=countdown["Text"].strip() + ": " + "Skip")
          except AttributeError:
            print ("Could Not Update Countdown")
          break

      if (not channelFound):
        continue
        #await ClocksAndCountdowns.delete("countdown", countdown["Channel ID"])
# end updateGuildCountdowns

async def updateGuildClocks(client, currentTime, clocks):

  for guildID in clocks:
    guild = client.get_guild(guildID)
    for clock in clocks[guildID]:
      tz = clock["Time Zone"]
      convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))

      channelFound = False
      for channel in guild.voice_channels:
        if (channel.id == clock["Channel ID"]):
          channelFound = True
          try:
            await channel.edit(name=convertedTime.strftime(clock["Format"]))
          except AttributeError:
            print ('Could Not Update Clock')
          break

      if (not channelFound):
        continue
        #await ClocksAndCountdowns.delete("clock", clock["Channel ID"])
          
  #print ()
# end guildClocks

async def updateTimeZoneList(currentTime):
  moBotSupportGuild = client.get_guild(moBotSupport)
  timeZonesChannel = moBotSupportGuild.get_channel(607323514042712074)
  timeZonesListMessage = await timeZonesChannel.fetch_message(607323599925149706)

  timeZones = MoBotTimeZones.timeZones

  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="Time Zones")
  embed.set_footer(text="*Currently Experiencing Daylight Savings Time")

  def is_dst(zonename):
    tz = timezone(zonename)
    now = utc.localize(datetime.utcnow())
    return now.astimezone(tz).dst() != timedelta(0)

  for tz in timeZones:
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))
    convertedTimeStr = convertedTime.strftime("%H:%M " + convertedTime.tzname() + " (%z)")
    value = "**" + convertedTimeStr + "**" if (tz == "UTC") else convertedTimeStr
    if (is_dst(tz)):
      value += "*"
    name = "__" + tz + "__" if (tz == "UTC") else tz
    embed.add_field(name=name, value=spaceChar + value, inline=False)
  
  await timeZonesListMessage.edit(embed=embed)
# end updateTimeZoneList

async def convertTime(currentTime, tz, toFrom):
  timeZones = {"CET" : "Europe/Monaco", "UK" : "Europe/London", "UTC" : "UTC", "ET" : "US/Eastern", "PT" : "US/Pacific"}
  if (toFrom == "to"): # from local to foreign
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))
  elif (toFrom == "from"): # from foregin to local
    convertedTime = timezone(timeZones[tz]).localize(currentTime).astimezone(timezone("US/Central"))
  return convertedTime
# end convertTime

async def openGuildClocksSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1Cz-NGa_mqSIw-Ae4tU1DX1AOsS-zC_5l1HLiIbVjr4M")
  return workbook

async def openTEGarrettPointApplicationsSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("14Lv2kUP7_2ekMiaPj-Wfhro_qkrTC5X9_Q5FUnAYZUw")
  return workbook

async def openRandomLogs():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1x19iRicPBE00oPjTuf6jNURpdpB2nLUASst_JPv9WyU")
  return workbook
# end openRandomLogs

print ("Connecting...")
client.run(SecretStuff.getToken("MoBotToken.txt"))