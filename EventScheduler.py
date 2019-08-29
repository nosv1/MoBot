import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone, utc

import SecretStuff
import MoBotTimeZones

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

embeds = {
  "getEvent" : {
    "author" : {
      "name" : "Event Scheduler",
      "url" : "https://google.com/EventScheduler",
    },
  }
}

permissions = {
  "read_message" : True,
  "send_messages" : True,
  "add_reactions" : True,
}

numCols = 14

class Event:
  def __init__(self, eventSheet, events, eventID, guildID, eventType, localChannelID, destinationChannelID, roleIDs, permissions, messageID, day, month, year, hour, minute, timezone):
    self.eventSheet = eventSheet
    self.events = events
    self.eventID = eventID
    self.guildID = guildID
    self.eventType = eventType
    self.localChannelID = localChannelID
    self.destinationChannelID = destinationChannelID
    self.roleIDs = roleIDs
    self.permissions = permissions
    self.messageID = messageID
    self.day = day
    self.month = month
    self.year = year
    self.hour = hour
    self.minute = minute
    self.timezone = timezone
# end Event

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def mainReactionAdd(message, payload, client): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def getEventTime(event):
  eventTime = datetime(event.year, event.month, event.day, event.hour, event.minute)
  timeZones = MoBotTimeZones.timeZones
  tz = timeZones[timeZones.index(event.timezone)]
  convertedTime = timezone(tz).localize(eventTime).astimezone(timezone("America/Chicago"))
  return datetime(convertedTime.year, convertedTime.month, convertedTime.day, convertedTime.hour, convertedTime.minute)
# end getEvent

async def sendMessageEvent(event, client):
  guild = client.get_guild(event.guildID)
  localChannel = guild.get_channel(event.localChannelID)
  destinationChannel = guild.get_channel(event.destinationChannelID)
  await destinationChannel.trigger_typing()

  sourceMessage = await localChannel.fetch_message(event.messageID)
  content = sourceMessage.content
  try:
    embed = sourceMessage.embeds[0]
  except IndexError:
    embed = None
  if (content is not ""):
    if (embed is not None):
      await destinationChannel.send(content=content, embed=embed)
    else:
      await destinationChannel.send(content=content)
  elif (embed is not None):
    await destinationChannel.send(embed=embed)
# end sendMessageEvent

async def performScheduledEvent(event, client):
  if (event.eventType == "sendMessage"):
    await sendMessageEvent(event, client)
    return await removeCompletedEvent(event)
# end performScheduledEvent

async def removeCompletedEvent(event):
  eventSheet = event.eventSheet
  events = event.events
  for i in range(0, len(events), numCols):
    if (events[i].value == str(event.eventID) and events[i+1].value == str(event.guildID)):
      for j in range(i, len(events)):
        try:
          events[j].value = events[j+numCols].value
        except IndexError:
          break
  
  eventSheet.update_cells(events, value_input_option="USER_ENTERED")
  return await getScheduledEvents(eventSheet, events)
# end removeCompletedEvent

async def getScheduledEvents(eventSheet, eventRange):
  events = []
  for i in range(0, len(eventRange), numCols):
    if (eventRange[i].value is not ""):
      event = Event(eventSheet, eventRange, int(eventRange[i].value), int(eventRange[i+1].value), eventRange[i+2].value, int(eventRange[i+3].value), int(eventRange[i+4].value), eventRange[i+5].value, eventRange[i+6].value, int(eventRange[i+7].value), int(eventRange[i+8].value), int(eventRange[i+9].value), int(eventRange[i+10].value), int(eventRange[i+11].value), int(eventRange[i+12].value), eventRange[i+13].value)
      events.append(event)
    else:
      break
  return events
# end getScheduledEvents

async def getEventRange():
  workbook = await openSpreadsheet()
  eventSheet = workbook.worksheet("Events")
  return eventSheet, eventSheet.range(2, 1, eventSheet.row_count, numCols)
# end getEventRange

async def getEventFromUser(message):
  pass
# end getEventFromUser

async def createEventSchedulerEmbed():
  pass
# end createEventSchedulerEmbed

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1dGEQAQEsIzuV4z1CQM3TKA8yIUoNHrRPqPSMYi6OhAc")
  return workbook
# end openSpreadsheet