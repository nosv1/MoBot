import discord
import asyncio
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pytz import timezone, utc
from dateutil.relativedelta import relativedelta

import SecretStuff

moBot = "449247895858970624"

numberEmojis = {
 0 : "0⃣", 1 : "1⃣", 2 : "2⃣", 3 : "3⃣", 4 : "4⃣", 5 : "5⃣", 6 : "6⃣", 7 : "7⃣", 8 : "8⃣", 9 : "9⃣"
}
doubleArrowControl = {
  "Day" : 10, "Month" : 5, "Year" : 5, "Hour" : 5, "Minute" : 10
}
daysInMonth = {
  "1" : 31, "2" : 28, "3" : 31, "4" : 30, "5" : 31, "6" : 30, "7" : 31, "8" : 31, "9" : 30, "10" : 31, "11" : 30, "12" : 31
}
arrows = ["⬅", "◀", "➡", "▶"]

months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Nov", "Dec"]

timeZones = ["UK", "UTC", "ET", "PT"]

repeaters = ["Never", "Hourly", "Daily", "Weekly", "Bi-weekly", "Monthly", "Yearly"]

shortTimeZoneToProper = {"UK" : "Europe/London", "UTC" : "UTC", "ET" : "America/New_York", "PT" : "America/Los_Angeles"}

async def main(args, message, client):    
  
  if (args[0][-19:-1] == moBot):
    authorPerms = message.channel.permissions_for(message.author)
    manageMessagePerms = authorPerms.manage_messages
    if (len(args) == 5):
      if (args[1] == "schedule" and args[2] == "message" and manageMessagePerms):
        channelID = args[3][-19:-1]
        messageID = args[4]
        await prepareMessageToSchedule(message, channelID, messageID)
    elif (len(args) == 3):
      if (args[1] == "scheduled" and args[2] == "messages"):
        await getScheduledMessages(message)
    elif ("help" in message.content):
      await sendHelpMessage(message)
# end main

async def mainReactionAdd(message, payload, client):
  if (payload.user_id != int(moBot)):
    await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
    progress, value = await getMessageScheduleProgress(message)
    if (payload.emoji.name in arrows):
      await incrementValue(message, payload, progress, value)
    elif (payload.emoji.name == "✅"):
      await scheduleMessage(message, payload)
    elif (payload.emoji.name == "⬇"):
      await switchProgress(message, progress, "down")
    elif (payload.emoji.name == "⬆"):
      await switchProgress(message, progress, "up")
    elif (payload.emoji.name == "❌"):
      await cancelScheduledMessage(message)
#end mainReactionAdd

async def sendHelpMessage(message):
  reply = "To Schedule a Message:\n\t"
  reply += "@MoBot#0697 schedule message #destination_channel message_id\n\t\t"
  reply += "The '#destination_channel' is the channel in which MoBot will send the message.\n\t\t"
  reply += "The 'message_id' is the ID of the message that will be copied.\n\t\t"
  reply += "This will bring up a message with controls to edit the date/time details for the scheuduled msesage.\n\n"
  reply += "To View Scheduled Messages:\n\t"
  reply += "@MoBot#0697 scheduled messages\n\t\t"
  reply += "This will bring up a message that will display infromation about all currently scheduled messages.\n\n"
  reply += "To Edit an Existing Scheduled Message:\n\t"
  reply += "You are able to use the existing message scheduler when you first scheduled the message, or you can retype the command to scheudle a message, and MoBot will edit the existing details.\n\n"
  reply += "To Cancel an Existing Scheduled Message:\n\t"
  reply += "Re-open the message scheduler, or use the existing one, then click the ❌."

  await message.channel.send("```" + reply + "```")
# end sendHelpMessage

async def deleteSentMessages(r, sheet, msgIDs):

  for msgID in msgIDs:
    for i in range(0, len(r), 13):
      if (r[i+2].value == str(msgID)):
        for j in range(0, 13):
          r[i+j].value = ""
        break
  
  sheet.update_cells(r, value_input_option="USER_ENTERED")
# end deleteSentMessages

async def sendScheduledMessages(client):
  workbook = await openSpreadsheet()
  sheet = workbook.worksheet("Scheduled Messages")
  r = sheet.range("A2:M" + str(sheet.row_count))
  scheduleMessages = await getScheduledMessagesAsArray(r)

  sentMsgs = []
  n = datetime.utcnow()
  for msg in scheduleMessages:
    guild = client.get_guild(int(msg[0]))
    if (msg[-2] <= n):

      destChannel = guild.get_channel(int(msg[3]))
      await destChannel.trigger_typing()
          
      msgLocation = None
      message = None

      for channel in guild.channels:
        if (msgLocation == None):
          try:
            message = await channel.fetch_message(int(msg[2]))
            msgLocation = channel
          except:
            continue

      if (message != None):
        content = message.content
        try:
          embed = message.embeds[0]
        except IndexError:
          embed = None

        if (content != ""):
          if (content[:3] == "```" and content[-3:] == "```"):
            content = content[3:-3]

          if (embed != None):
            await destChannel.send(content=content, embed=embed)
          else:
            await destChannel.send(content=content)
        elif (embed != None):
            await destChannel.send(embed=embed)

      else:
        member = guild.get_member(int(msg[4]))
        reply = "```Scheduled message was unable to send.```"
        reply += "Source Channel: <#" + str(msg[1]) + ">\n"
        reply += "Desination Channel: <#" + str(msg[3]) + ">\n"
        reply += "Message ID: " + str(msg[2]) + "\n"
        link = "https://discordapp.com/channels/" + str(msg[0]) + "/" + str(msg[1]) + "/" + str(msg[2])

        await member.send(reply + "```Basically, either MoBot can no longer view the channel where the message is, or the source channel, destination channel, or the orginal message has been deleted.```" + "The link to the message:\n" + link)

      if (msg[-1] != "Never"):
        repeating = msg[-1]
        date = msg[-2]
        if (repeating == "Hourly"):
          date += relativedelta(hours=1)
        elif (repeating == "Daily"):
          date += relativedelta(days=1)
        elif (repeating == "Weekly"):
          date += relativedelta(weeks=1)
        elif (repeating == "Bi-Weekly"):
          date += relativedelta(weeks=2)
        elif (repeating == "Monthly"):
          date += relativedelta(months=1)
        elif (repeating == "Yearly"):
          date += relativedelta(years=1)
        msg[-2] = date
        for i in range(len(r)):
          if (r[i].value == str(msg[2])):
            r[i+3].value = date.month
            r[i+4].value = date.day
            r[i+5].value = date.year
            r[i+6].value = date.hour if date.hour <= 12 else 12 - date.hour
            r[i+6].value = 12 if r[i+6].value == 0 else r[i+6].value
            r[i+7].value = date.minute
            r[i+8].value = "AM" if date.hour < 12 else "PM"
      else:
        sentMsgs.append(msg[2])
  await deleteSentMessages(r, sheet, sentMsgs)      
# end sendScheduledMessages

async def getScheduledMessagesAsArray(r):
  messages = []
  for i in range(0, len(r), 13):
    if (r[i].value == ""):
      continue
    date = getMessageTime([c.value for c in r[i+5:i+13]])
    messages.append([c.value for c in r[i:i+5]] + [date] + [r[i+12].value])
  return messages
# end getScheduledMessagesAsArray

async def getScheduledMessages(message):
  await message.channel.trigger_typing()

  workbook = await openSpreadsheet()
  scheduledMessagesSheet = workbook.worksheet("Scheduled Messages")
  scheduledMessagesRange = scheduledMessagesSheet.range("A2:M" + str(scheduledMessagesSheet.row_count))

  scheduledMessages = []

  messageExists = False
  for i in range(0, len(scheduledMessagesRange), 13):
    if (scheduledMessagesRange[i].value == str(message.guild.id)):
      messageExists = True
      temp = []
      for j in range(0, 13):
        temp.append(scheduledMessagesRange[i+j].value)
      scheduledMessages.append(temp)

  if (not messageExists):
    await message.channel.send("```There are no scheduled messages for this server.```")
  else:    
    for i in range(len(scheduledMessages)):
      msgLocation = None
      msg = None
      try:
        destChannel = message.guild.get_channel(int(scheduledMessages[i][2]))       

        for channel in message.guild.channels:
          if (msgLocation == None):
            try:
              msg = await msgLocation.fetch_message(int(scheduledMessages[i][1]))
              msgLocation = channel
            except:
              continue

          reply = "\nMessage " + str(i+1) + " of " + str(len(scheduledMessages)) + "\n\t"
          reply += "Destination Channel: #" + destChannel.name + "\n\t"
          reply += "Message Snippet: " + msg.content.replace("```", "")[:25].strip() + "...\n\t"
          reply += "Message ID: " + str(msg.id) + "\n\t"

          member = message.guild.get_member(int(scheduledMessages[i][3]))
          if (member.nick != None):
            reply += "Last Edited By: " + member.nick + "\n\t"
          else:
            reply += "Last Edited By: " + member.name + "\n\t"

          reply += "Date: " + months[int(scheduledMessages[i][4])] + " " + scheduledMessages[i][6] + ", " + scheduledMessages[i][7] + "\n\t"
          reply += "Time: " + scheduledMessages[i][8] + ":" + "{:02d}".format(int(scheduledMessages[i][9])) + scheduledMessages[i][10] + " " + scheduledMessages[i][11] + "\n\t"
        reply = reply[:-2]
        await message.channel.send("```" + reply + "```")

      except:
        pass

      if (msg == None):
        reply = "```There are/is " + str(len(scheduledMessages)) + " scheduled message(s) for this server. The following message could not be found.```"
        reply += "Source Channel: <#" + scheduledMessages[i][1] + ">\n"
        reply += "Desination Channel: <#" + scheduledMessages[i][3] + ">\n"
        reply += "Message ID: " + scheduledMessages[i][2] + "\n"
        link = "https://discordapp.com/channels/" + scheduledMessages[i][0] + "/" + scheduledMessages[i][1] + "/" + scheduledMessages[i][2]

        await message.channel.send(reply + "```Basically, either MoBot can no longer view the channel where the message is, or the source channel, destination channel, or the orginal message has been deleted.```" + "The link to the message:\n" + link)
# end getsch

async def cancelScheduledMessage(message):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  scheduledMessagesSheet = workbook.worksheet("Scheduled Messages")
  scheduledMessagesRange = scheduledMessagesSheet.range("A2:M" + str(scheduledMessagesSheet.row_count))

  mc = message.content
  msgId = mc.split("Message ID: ")[1].split("\n")[0]

  messageExists = False
  for i in range(0, len(scheduledMessagesRange), 13):
    if (scheduledMessagesRange[i+2].value == msgId):
      messageExists = True
      for j in range(0, 13):
        scheduledMessagesRange[i+j].value = ""
      scheduledMessagesSheet.update_cells(scheduledMessagesRange, value_input_option="USER_ENTERED")
      await message.channel.send("```Message has been unscheduled.```")
      break

  if (not messageExists):
    await message.channel.send("```Cannot unschedle message. Message has not previously been scheduled.\nYou can see this server's scheduled messages by using\n\t@MoBot#0697 scheduled messages```")
# end cancelScheduledMessage

async def scheduleMessage(message, payload):
  await message.channel.trigger_typing()
  
  workbook = await openSpreadsheet()
  scheduledMessagesSheet = workbook.worksheet("Scheduled Messages")
  scheduledMessagesRange = scheduledMessagesSheet.range("A2:M" + str(scheduledMessagesSheet.row_count))

  mc = message.content

  guildId = str(message.guild.id)
  msgLocation = mc.split("Source Channel ID: ")[1].split("\n")[0]
  msgId = mc.split("Message ID: ")[1].split("\n")[0]
  destChannel = mc.split("Destination Channel ID: ")[1].split("\n")[0]
  lastEditedBy = str(payload.user_id)
  month = mc.split("Month [")[1].split("]")[0]
  day = mc.split("Day [")[1].split("]")[0]
  year = mc.split("Year [")[1].split("]")[0]
  hour = mc.split("Hour [")[1].split("]")[0]
  minute = mc.split("Minute [")[1].split("]")[0]
  amPm = mc.split("AM/PM [")[1].split("]")[0]
  tz = mc.split("Time zone [")[1].split("]")[0]
  repeating = mc.split("Repeating [")[1].split("]")[0]

  messageScheduled = False
  for i in range(0, len(scheduledMessagesRange), 13):
    if (scheduledMessagesRange[i].value == "" or scheduledMessagesRange[i+2].value == msgId):
      messageScheduled = True
      scheduledMessagesRange[i+0].value = guildId
      scheduledMessagesRange[i+1].value = msgLocation
      scheduledMessagesRange[i+2].value = msgId
      scheduledMessagesRange[i+3].value = destChannel
      scheduledMessagesRange[i+4].value = lastEditedBy
      scheduledMessagesRange[i+5].value = month
      scheduledMessagesRange[i+6].value = day
      scheduledMessagesRange[i+7].value = year
      scheduledMessagesRange[i+8].value = hour
      scheduledMessagesRange[i+9].value = minute
      scheduledMessagesRange[i+10].value = amPm
      scheduledMessagesRange[i+11].value = tz
      scheduledMessagesRange[i+12].value = repeating

      scheduledMessagesSheet.update_cells(scheduledMessagesRange, value_input_option="USER_ENTERED")
      await message.channel.send("```Message has been scheduled. Feel free to edit your scheduled message or this 'Message Scheduler' at anytime. You can also simply retype the '@MoBot schedule message' command to update the existing scheduled message's Date/Time Details.```")
      break

  if (not messageScheduled):
    await message.channel.send("```Message could not be scheduled. Ran out of space... Contact Mo#9991```")
# end scheduleMessage

async def switchProgress(message, progress, direction):

  mc = message.content
  mc = mc.replace("➡", "  ")

  if (direction == "up"):
    if (progress != "Month"):
      msgParts = mc.split(progress + " [")
      previousAttribute = msgParts[0].split("\n    ")[-2]
      reply = msgParts[0].split(previousAttribute)[0][:-2] + "➡" + previousAttribute + "\n    " + progress + " [" + msgParts[1]
      await message.edit(content=reply)
  elif (direction == "down"):
    if (progress != "Repeating"):
      msgParts = mc.split(progress + " [")
      nextAttribute = "\n  ➡" + msgParts[1].split("\n    ")[1]
      reply = msgParts[0] + progress + " [" + msgParts[1].split("]")[0] + "]" + nextAttribute + msgParts[1].split(nextAttribute[4:])[1]
      await message.edit(content=reply)
# end switchProgress

async def incrementValue(message, payload, progress, value):

  oldValue = value
  if (progress not in ["AM/PM", "Time zone", "Repeating"]):
    value = int(oldValue)

    if (payload.emoji.name == "➡"):
      value += 1
    elif (payload.emoji.name == "▶"):
      value += doubleArrowControl[progress]
    elif (payload.emoji.name == "⬅"):
      value -= 1
    elif (payload.emoji.name == "◀"):
      value -= doubleArrowControl[progress]

  elif (progress == "AM/PM"):
    if (value == "AM"):
      value = "PM"
    else:
      value = "AM"
  elif (progress == "Time zone"):
    if (payload.emoji.name == "⬅"):
      i = timeZones.index(value)
      value = timeZones[i+1]
    elif (payload.emoji.name == "➡"):
      i = timeZones.index(value)
      value = timeZones[i-1]
  elif (progress == "Repeating"):
    i = len(repeaters) * -1 + repeaters.index(value)
    if (payload.emoji.name == "⬅"):
      value = repeaters[i-1]
    elif (payload.emoji.name == "➡"):
      value = repeaters[i+1]


  goodValue = False
  if (progress == "Month"):
    goodValue = value <= 12 and value >= 1
  elif (progress == "Day"):
    selectedMonth = message.content.split("Month [")[1].split("]")[0]
    goodValue = value <= daysInMonth[selectedMonth] and value >= 1
  elif (progress == "Year"):
    goodValue = True
  elif (progress == "Hour"):
    goodValue = value <= 12 and value >= 1
  elif (progress == "Minute"):
    goodValue = value <= 59 and value >= 0
    value = "{:02d}".format(value)
  elif (progress == "AM/PM"):
    goodValue = True
  elif (progress == "Time zone"):
    goodValue = True
  elif (progress == "Repeating"):
    goodValue = True
    
  if (goodValue):
    mc = message.content
    msgParts = mc.split(progress + " [")
    msgParts[1] = str(value) + "]\n" + mc.split(progress + " [" + oldValue + "]\n")[1]
    await message.edit(content=msgParts[0] + progress + " [" + msgParts[1])
# end incrementValue

async def getMessageScheduleProgress(message):
  mc = message.content
  progress = mc.split("➡")[1]
  value = progress.split("[")[1].split("]")[0]
  progress = progress.split(" [")[0]
  return progress, value
# end getMessageScheduleProgress

async def prepareMessageToSchedule(message, channelID, messageID):
  await message.channel.trigger_typing()

  msgLocation = None
  msg = None
  destChannel = None

  for channel in message.guild.channels:
    if (msgLocation == None):
      try:
        msg = await channel.fetch_message(int(messageID))
        msgLocation = channel
      except:
        continue

  try:
    destChannel = message.guild.get_channel(int(channelID))
  except:
    pass
  
  if (msgLocation != None and destChannel != None and msg != None):
    tomorrow = datetime.now() + timedelta(days=1)

    reply = "Message Scheduler\n\nMessage Details:\n    Destination Channel: #" + destChannel.name + "\n    Destination Channel ID: " + str(destChannel.id) + "\n\n    Message Snippet: '" + msg.content.replace("```", "")[:25].strip() + "...'\n    Message ID: " + str(msg.id) + "\n\n    Source Channel: #" + msgLocation.name + "\n    Source Channel ID: " + str(msgLocation.id) + "\n\nDate/Time Details:\n  ➡Month [" + str(tomorrow.month) + "]\n    Day [" + str(tomorrow.day) + "]\n    Year [" + str(tomorrow.year) + "]\n    Hour [6]\n    Minute [30]\n    AM/PM [AM]\n    Time zone [UK]\n    Repeating [Never]\n\nTime Zones Available:\n    UK = United Kingdom\n    UTC = Universal Time Coordinated\n    ET = United States Eastern Time\n    PT = United States Pacific Time\n\nHow to Use:\n    The left/right arrows adjust the values.\n    The up/down arrows move through the 'Date/Time Details'.\n    When you've the 'Date/Time Details' as you want them, click the ✅ to schedule the message."

    messageScheduler = await message.channel.send("```" + reply + "```")
    
    await messageScheduler.add_reaction("⬅")
    await messageScheduler.add_reaction("◀")
    await messageScheduler.add_reaction("➡")
    await messageScheduler.add_reaction("▶")
    await messageScheduler.add_reaction("⬆")
    await messageScheduler.add_reaction("⬇")
    await messageScheduler.add_reaction("✅")
    await messageScheduler.add_reaction("❌")
  else:
    reply = ""
    if (msgLocation == None and msg == None):
      reply += "Message ID was not found."
      workbook = await openSpreadsheet()
      sheet = workbook.worksheet("Scheduled Messages")
      await deleteSentMessages(sheet.range("A2:M" + str(sheet.row_count)), sheet, [messageID])
    elif (destChannel == None):
      reply += "Destination channel was not found."
    reply += "\n\t@MoBot#0697 schedule message #destination-channel message_id\n\n"
    reply += "`#destination-channel` is the channel where MoBot will send the message\n"
    reply += "`message_id` is the id of the message that MoBot will copy"
    await message.channel.send("```" + reply + "```")
# end scheduleMessage

def getMessageTime(messageTime):
  messageTime[3] = 0 if messageTime[3] == "12" else messageTime[3]
  eventTime = datetime(
    int(messageTime[2]), # year
    int(messageTime[0]), # month
    int(messageTime[1]), # day
    int(messageTime[3]) if messageTime[5] == "AM" else 12 + int(messageTime[3]), # hour
    int(messageTime[4]) # minute
  )
  convertedTime = timezone(shortTimeZoneToProper[messageTime[6]]).localize(eventTime).astimezone(timezone("UTC"))
  return datetime(convertedTime.year, convertedTime.month, convertedTime.day, convertedTime.hour, convertedTime.minute)
# end getMessageTime

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1aG8azyXl0zio6h50rV_0vrww89qpDvjCPq0cyikv3bQ")
  return workbook
# end openSpreadsheet
