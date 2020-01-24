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
import MessageScheduler
import MoBotTimeZones
import EventScheduler
import MoBotDatabase
import MoBotTables

import AOR
  
client = discord.Client() # discord.Client is like the user form of the bot, it knows the guilds and permissions and stuff of the bot
moBotDB = None

# these are 'statuses' for the bot, futher down I've got 50/50 random gen, to change status on every message sent
testingMoBot = discord.Activity(type=discord.ActivityType.streaming, name="Testing MoBot")

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

started = False
# when bot is first online
@client.event
async def on_ready():

  global started
  if (not started):
    print("\nMoBotLoop is online - " + str(datetime.now()) + "\n")
    started = True
  else:
    sys.exit()
  
  await MessageScheduler.sendScheduledMessages(client)

  await main(client)
# end on_ready

async def main(client):
  global moBotDB
  moBotDB = MoBotDatabase.connectDatabase('MoBot')
  print ("Connected to MoBot Database")

  print()
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
      sys.stdout.flush()
        
      if (second % 30 == 0): # check for every 30 seconds
        await updateGuildClocks(client, currentTime, await getGuildClocks())
        await updateMoBotStatus(client)

        if (second == 0): 
          pass
        eventSheet, eventRange = await EventScheduler.getEventRange()
        scheduledEvents= await EventScheduler.getScheduledEvents(eventSheet, eventRange)
        for event in events:
          eventTime = await EventScheduler.getEventTime(event)
          if (eventTime < currentTime):
            scheduledEvents= await EventScheduler.performScheduledEvent(event, client)

        await MessageScheduler.sendScheduledMessages(client)

    except:
      print("\n" + str(datetime.now()) + "\nError -- " + str(traceback.format_exc()))
      sys.exit()
  # end infinte loop
# end main
async def updateDiscordTables():
  moBotDB = MoBotTables.connectDatabase()
  tables = MoBotTables.getSavedTables(moBotDB)
  for table in tables:
    r = random.random()
    if (r < 2/10 or True): # 20% chance every minute = update 12 times per hour = 1 time every 5 minutes
      await MoBotTables.sendTable(table, None, client)
# end updateDiscordTables

async def getGuildClocks():
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT * 
    FROM MoBot.clocks
    WHERE clocks.guild_id = '%s'
  """ % moBotSupport)

  clocks = []
  for record in moBotDB.cursor:
    clocks.append(Clock(record[0], record[1], record[2], record[3], record[4]))

  return clocks
# end getGuildClocks

async def updateGuildClocks(client, currentTime, clocks):
  for clock in clocks:
    guild = client.get_guild(clock.guildID)
    tz = clock.timeZone
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz))

    try:
      for channel in guild.voice_channels:
        if (channel.id == clock.channelID):
          try:
            await channel.edit(name=convertedTime.strftime(clock.timeFormat))
          except AttributeError:
            await client.get_user(int(mo)).send("**Could Not Update Clock**\nGuild ID: %s\nChannel ID: %s" % (guild.id, clock.channelID))
          break
    except AttributeError:
      await client.get_user(int(mo)).send("**Guild Has No Voice Channels**\nGuild ID: %s" % (guild.id))
      break
# end guildClocks

async def updateMoBotStatus(client):
  # changing bot status based on rand gen
  rand = int(random.random() * 100)
  if (rand < 1000): # 100%
    await client.change_presence(activity=testingMoBot)
# end updateMoBotStatus

async def openRandomLogs():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1x19iRicPBE00oPjTuf6jNURpdpB2nLUASst_JPv9WyU")
  return workbook

print("Connecting...")
client.run(SecretStuff.getToken("MoBotTestDiscordToken.txt"))