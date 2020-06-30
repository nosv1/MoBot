import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

import SecretStuff
import MoBotTimeZones
import MoBotDatabase

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

eventNumCols = 14
reminderNumCols = 6

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

class Reminder:
  def __init__(self, reminder_id, guild_id, channel_id, member_id, text, date):
    self.reminderID = int(reminder_id)
    self.guildID = int(guild_id)
    self.channelID = int(channel_id)
    self.memberID = int(member_id)
    self.text = str(text)
    self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S") if type(date) == type("") else date
#end Reminder



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

async def memberRemove(member, client):
  pass
# end memberRemove

''' REMINDER STUFF'''
async def sendReminder(reminder, client):
  guild = client.get_guild(reminder.guild_id)
  channel = guild.get_channel(reminder.channel_id)
  await channel.send("Reminder for <@" + str(reminder.memberID) + ">: " + reminder.text)
  reminders = await removeReminder(reminder)
  return reminders
# end sendReminder

async def removeReminder(reminder):
  mobot_db = connectDatabase()
  mobot_db.cursor.exeucte(f"""
    DELETE FROM reminders WHERE reminder_id = {reminder.reminder_id}
  """)
  
  mobot_db.connection.commit()
  mobot_db.connection.close()

  return await getReminders()
# end removeCompletedEvent

async def getReminders():
  mobot_db = connectDatabase()
  
  reminders = []
  mobot_db.cursor.exeucte("""
    SELECT * FROM reminders
  """)

  for r in mobot_db.cursor:
    reminders.append(Reminder(*r))

  mobot_db.connection.close()
  return reminders
# end getReminders

async def setReminder(message):
  await message.channel.trigger_typing()
  timeDelta = {
    "second" : 0,
    "minute" : 0,
    "hour" : 0,
    "day" : 0,
    "week" : 0,
    "month" : 0,
    "year" : 0
  }
  reminder_text = " ".join(message.content.split("remindme")[1].strip().split(" ")[:-3])
  reminderWord = message.content.split(" ")[-1].strip()
  reminderNumber = message.content.split(" ")[-2].strip()
  for delta in timeDelta:
    if (delta in reminderWord):
      timeDelta[delta] = float(reminderNumber)

  reminder_date = datetime.utcnow() + relativedelta(years=timeDelta["year"], months=timeDelta["month"], weeks=timeDelta["week"], days=timeDelta["day"], hours=timeDelta["hour"], minutes=timeDelta["minute"], seconds=timeDelta["second"])

  mobot_db = connectDatabase()
  mobot_db.cursor.execute(f"""
    INSERT INTO reminders (
      `guild_id`, `channel_id`, `member_id`, `text`, `date`
    ) VALUES (
      '{message.guild_id}',
      '{message.channel}',
      '{message.author.id}',
      '{reminder_text}',
      '{reminder_date}'
    )
  """)

  mobot_db.connection.commit()
  mobot_db.connection.close()

  await message.channel.send("**You will be reminded at " + reminder_date.strftime("%H:%M:%S UTC on %d %b %Y.") + "**")
# end setReminder



''' EVENT STUFF '''

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
  if (content != ""):
    if (embed != None):
      await destinationChannel.send(content=content, embed=embed)
    else:
      await destinationChannel.send(content=content)
  elif (embed != None):
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
  for i in range(0, len(events), eventNumCols):
    if (events[i].value == str(event.eventID) and events[i+1].value == str(event.guildID)):
      for j in range(i, len(events)):
        try:
          events[j].value = events[j+eventNumCols].value
        except IndexError:
          break
  
  eventSheet.update_cells(events, value_input_option="USER_ENTERED")
  return await getScheduledEvents(eventSheet, events)
# end removeCompletedEvent

async def getScheduledEvents(eventSheet, eventRange):
  events = []
  for i in range(0, len(eventRange), eventNumCols):
    if (eventRange[i].value != ""):
      event = Event(eventSheet, eventRange, int(eventRange[i].value), int(eventRange[i+1].value), eventRange[i+2].value, int(eventRange[i+3].value), int(eventRange[i+4].value), eventRange[i+5].value, eventRange[i+6].value, int(eventRange[i+7].value), int(eventRange[i+8].value), int(eventRange[i+9].value), int(eventRange[i+10].value), int(eventRange[i+11].value), int(eventRange[i+12].value), eventRange[i+13].value)
      events.append(event)
    else:
      break
  return events
# end getScheduledEvents

async def getEventRange(workbook):
  eventSheet = workbook.worksheet("Events")
  return eventSheet, eventSheet.range(2, 1, eventSheet.row_count, eventNumCols)
# end getEventRange

async def getEventFromUser(message):
  pass
# end getEventFromUser

async def createEventSchedulerEmbed():
  pass
# end createEventSchedulerEmbed



''' RESOURCES '''
def connectDatabase():
  return MoBotDatabase.connectDatabase("MoBot")
# end connectDatabase

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1dGEQAQEsIzuV4z1CQM3TKA8yIUoNHrRPqPSMYi6OhAc")
  return workbook
# end openSpreadsheet