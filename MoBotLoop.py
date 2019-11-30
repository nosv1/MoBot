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
import RandomSupport

import ClocksAndCountdowns
import EventScheduler
import MoBotDatabase
import AOR

import MoBotTimeZones
  
client = discord.Client() # discord.Client is like the user form of the bot, it knows the guilds and permissions and stuff of the bot

# these are 'statuses' for the bot, futher down I've got 50/50 random gen, to change status on every message sent
botsByMo = discord.Activity(type=discord.ActivityType.streaming, name="Bots by Mo#9991")
donate = discord.Activity(type=discord.ActivityType.watching, name="@MoBot donate")
server = discord.Activity(type=discord.ActivityType.watching, name="@MoBot server")
moBotHelp = discord.Activity(type=discord.ActivityType.watching, name="@MoBot help")

moBotSupport = 467239192007671818
mo = 405944496665133058

class Clock:
  def __init__(self, channelID, guildID, guildName, timeFormat, timeZone):
    self.channelID = int(channelID)
    self.guildID = int(guildID)
    self.guildName = guildName
    self.timeFormat = timeFormat
    self.timeZone = timeZone
# end Clock

class Countdown:
  def __init__(self, channelID, guildID, guildName, endDatetime, timeZone, text, repeating):
    self.channelID = int(channelID)
    self.guildID = int(guildID)
    self.guildName = guildName
    self.endDatetime = endDatetime
    self.timeZone = timeZone
    self.text = text
    self.repeating = repeating
# end Countdown

spaceChar = "⠀"

donations = {
  "TE Garrett#9569" : {
    "Date" : datetime(2019, 6, 12),
    "Donation" : 26 # 2 on 6/12, 15 on 7/9
  }
}

scheduledEvents = []
reminders = []

tenMinutetime = datetime.now()
messagesSent = 0
messageRate = 0

isConnected = False
# when bot is first online
@client.event
async def on_ready():
  global isConnected
  if (not isConnected):
    print("\nMoBotLoop is online - " + str(datetime.now()) + "\n")
    isConnected = True
  else:
    sys.exit()
  
  mobotLog = client.get_guild(moBotSupport).get_channel(604099911251787776) # mobot log
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBotLoop Restarted")
  if (mobotLog != None):
    await mobotLog.send(embed=embed)
    await main(client)
# end on_ready

@client.event
async def on_message(message):
  global isConnected
  global tenMinutetime
  global messagesSent
  global messageRate
  global messageRate

  if (not isConnected):
    return
  
  n = datetime.now()
  d = n - tenMinutetime

  messagesSent += 1
  messageRate = messagesSent / d.total_seconds()

  if (d.seconds > 600):
    messagesSent = 0
    tenMinutetime = n
# end on_message

async def main(client):
  try:
    global scheduledEvents, reminders
    workbook = await EventScheduler.openSpreadsheet()
    eventSheet, eventRange = await EventScheduler.getEventRange(workbook)
    scheduledEvents = await EventScheduler.getScheduledEvents(eventSheet, eventRange)
    remindersSheet, remindersRange = await EventScheduler.getRemindersRange(workbook)
    reminders = await EventScheduler.getReminders(remindersSheet, remindersRange)
    print("Scheduled Events Received")
  except httplib2.ServerNotFoundError:
    try:
      await client.get_user(int(mo)).send("Just checking when this happenes\nMoBotLoop Error!```" + str(traceback.format_exc()) + "```")
    except:
      pass
  except gspread.exceptions.APIError:
    pass
  

  print()
  lastSecond = 0
  while (True):
    try:
      currentTime = datetime.now() + timedelta(seconds=5)
      currentUTC = datetime.utcnow()
      second = currentTime.second
      if (lastSecond is second):
        await asyncio.sleep(1)
        continue
      else:
        lastSecond = second

      sys.stdout.write("\rCurrent Time: " + str(currentTime))
      sys.stdout.flush() # allows rewriting the line above in the console, basically it keeps replacing the text instead of having a bunch of lines

      if (second is 0): # check for every 60 seconds
        clocks = await getGuildClocks()
        countdowns = await getGuildCountdowns()

        try:
          await updateGuildCountdowns(client, currentTime, countdowns)
          await updateGuildClocks(client, currentTime, clocks)
          await updateMoBotStatus(client)
        except UnboundLocalError: # when there's an error intially getting the countdowns/clocks
          pass

        if (currentTime.minute % 5 is 0): # check every 5 minutes
          try:
            workbook = await EventScheduler.openSpreadsheet()
            eventSheet, eventRange = await EventScheduler.getEventRange(workbook)
            scheduledEvents = await EventScheduler.getScheduledEvents(eventSheet, eventRange)
            remindersSheet, remindersRange = await EventScheduler.getRemindersRange(workbook)
            reminders = await EventScheduler.getReminders(remindersSheet, remindersRange)
          except gspread.exceptions.APIError:
            pass
          
        for event in scheduledEvents:
          eventTime = await EventScheduler.getEventTime(event)
          if (eventTime < currentTime):
            scheduledEvents = await EventScheduler.performScheduledEvent(event, client)
        for reminder in reminders:
          reminderTime = reminder.date
          if (reminderTime < currentUTC):
            reminders = await EventScheduler.sendReminder(reminder, client)

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
        await AOR.updateStandings(client)
    except gspread.exceptions.APIError:
      eType, value, eTraceback = sys.exc_info()
      try:
        if (str(value("error")("code"))[0] == "5"):
          pass
        else:
          await RandomSupport.sendErrorToMo("MoBotLoop", client, mo)
      except TypeError: 
        await RandomSupport.sendErrorToMo("MoBotLoop", client, mo)
    except:
      try:
        await RandomSupport.sendErrorToMo("MoBotLoop", client, mo)
      except:
        print("\n" + str(datetime.now()) + "\nError -- " + str(traceback.format_exc()))
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
  
  ranges = formResponsesSheet.range("A2:Y%s" % formResponsesSheet.row_count)
  dateRange = []
  checkMarksRange = []
  picutresRange = []
  nameRange = []
  for cell in ranges:
    if (cell.col == 1): # A
      dateRange.append(cell)
    elif (cell.col == 2): # B
      checkMarksRange.append(cell)
    elif (cell.col == 3): # C
      picutresRange.append(cell)
    elif (cell.col >= 20 and cell.col <= 25): # T:Y
      nameRange.append(cell)
    else:
      continue

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
    pointApplicationsLogSheet.resize(rows=pointApplicationsLogSheet.row_count + 1)

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
  elif (rand < 40): # 10%
    msgRate = discord.Activity(type=discord.ActivityType.watching, name="Msg/Sec: %.2f" % messageRate)
    await client.change_presence(activity=msgRate)
  elif (rand >= 40):
    if (rand >= 50): 
      await client.change_presence(activity=moBotHelp)
    else:
      await client.change_presence(activity=donate)
# end updateMoBotStatus

async def getGuildCountdowns():
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT * 
    FROM MoBot.countdowns
  """)

  countdowns = []
  for record in moBotDB.cursor:
    countdowns.append(Countdown(record[0], record[1], record[2], record[3], record[4], record[5], record[6]))

  moBotDB.connection.close()
  return countdowns
# end getGuildCountdowns

async def getGuildClocks():
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT * 
    FROM MoBot.clocks
  """)

  clocks = []
  for record in moBotDB.cursor:
    clocks.append(Clock(record[0], record[1], record[2], record[3], record[4]))

  moBotDB.connection.close()
  return clocks
# end getGuildClocks

async def updateGuildClocks(client, currentTime, clocks):
  for clock in clocks:
    guild = client.get_guild(clock.guildID)
    if (guild is None):
      #await ClocksAndCountdowns.delete("clock", clock.channelID)
      #await client.get_user(int(mo)).send("GUILD ID: %s" % clock.guildID)
      continue

    tz = clock.timeZone
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))

    try:
      channel = guild.get_channel(clock.channelID)
      await channel.edit(name=convertedTime.strftime(clock.timeFormat))
    except AttributeError: # when channel doesn't exist
      #await ClocksAndCountdowns.delete("clock", clock.channelID)
      #await client.get_user(int(mo)).send("GUILD ID: %s\nCHANNEL ID: %s" % (guild.id, clock.channelID))
      pass
# end guildClocks

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
    repeatingDays = repeatingOptions[countdown.repeating]

    newEndDatetime = endDatetime + timedelta(days=repeatingDays)
    if (countdown.repeating == "Hourly"):
      newEndDatetime = endDatetime + relativedelta(hours=1)
    elif (countdown.repeating == "Monthly"):
      newEndDatetime = endDatetime + relativedelta(months=1)
    elif (countdown.repeating == "Yearly"):
      newEndDatetime = endDatetime + relativedelta(years=1)
    countdown.endDatetime = newEndDatetime.strftime("%m/%d/%Y %H:%M")
    await ClocksAndCountdowns.updateCountdownInfo(guild, countdown)
  except KeyError:
    pass
# end updateRepeatingCountdown

async def updateGuildCountdowns(client, currentTime, countdowns):
  for countdown in countdowns:
    guild = client.get_guild(countdown.guildID)
    if (guild is None):
      #await ClocksAndCountdowns.delete("countdown", countdown.channelID)
      #await client.get_user(int(mo)).send("GUILD ID: %s" % countdown.guildID)
      continue

    tz = countdown.timeZone
    endDatetime = datetime.strptime(countdown.endDatetime, "%m/%d/%Y %H:%M")
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
    try:
      channel = guild.get_channel(countdown.channelID)
      if (countdown.repeating != "Skip"):
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
        if (currentText != countdown.text):
          countdown.text = currentText
          await ClocksAndCountdowns.updateCountdownInfo(guild, countdown)
        await channel.edit(name=countdown.text.strip() + ": " + countdownString)
      else:
        await channel.edit(name=countdown.text.strip() + ": " + "Skip")
    except AttributeError: # when channel doesn't exist
      #await ClocksAndCountdowns.delete("countdown", countdown.channelID)
      #await client.get_user(int(mo)).send("GUILD ID: %s\nCHANNEL ID: %s" % (guild.id, countdown.channelID))
      pass
# end updateGuildCountdowns

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

print("Connecting...")
client.run(SecretStuff.getToken("MoBotDiscordToken.txt"))