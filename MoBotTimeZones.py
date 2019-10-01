import discord
import asyncio
from datetime import datetime
from pytz import timezone

moBot = "449247895858970624"

timeZones = ["America/Los_Angeles", "America/Denver", "America/Chicago", "America/New_York", "Canada/Atlantic", "UTC", "Europe/London", "Europe/Monaco", "Europe/Moscow", "Australia/Queensland"]

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
  
  if (len(args) == 4): # @MoBot tz TZ1 TZ2
    await getTimeZoneDifference(message, client)

  elif (len(args) == 3):
    if (args[2] == "list"):
      global timeZones
      await message.channel.send(await getTimeZoneList(timeZones, datetime.now()))
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass

async def getTimeZoneDifference(message, client):
  global timeZones

  currentTime = datetime.now()

  userTimeZones = message.content.split("tz")[1].strip().split(" ")
  for i in range(len(userTimeZones)):
    userTimeZones[i] = userTimeZones[i].lower()

  times = []
  for tz in timeZones:
    tz = timezone(tz)
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(tz)
    if (convertedTime.tzname().lower() in userTimeZones):
      times.append([convertedTime.replace(tzinfo=None), convertedTime.tzname()])

  if (len(times) == 2):
    delta = (times[0][0] - times[1][0]).total_seconds()
    if (delta < 0):

      delta = (times[1][0] - times[0][0]).total_seconds()

      t = times[1]
      times[1] = times[0]
      times[0] = t

    hours = int(delta / 3600)
    minutes = int((delta - (hours * 3600)) / 60)

    reply = times[1][1] + " + " + str(hours) + ":" + str(minutes).rjust(2, "0") + " = " + times[0][1] + "\n\n"
    reply += "**Current Times**\n"
    reply += times[1][1] + ": " + times[1][0].strftime("%H:%M - %b %d") + "\n"
    reply += times[0][1] + ": " + times[0][0].strftime("%H:%M - %b %d")

    await message.channel.send(reply)

  else:
    msg = await message.channel.send("At least one of the two time zones provided is not recognized in *MoBot's Time Zone List*.\n\nWould you like to view the current list?")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(payload):
      return (payload.emoji.name == "✅" or payload.emoji.name == "❌") and payload.user_id == message.author.id

    payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=check)

    if (payload.emoji.name == "✅"):
      reply = await getTimeZoneList(timeZones, currentTime)
      await message.channel.send(reply)
# end getTimeZoneDifference

async def getTimeZoneList(timeZones, currentTime):
  tzList = "**MoBot's Time Zone List:**"

  for tz in timeZones:
    convertedTime = timezone("US/Central").localize(currentTime).astimezone(timezone(tz)) 
    name = "**" + convertedTime.tzname() + "**" if tz == "UTC" else convertedTime.tzname()
    tzList += "\n  " + name + " - " + tz

  tzList += "\n\nExample: `@MoBot#0697 tz UTC MSK`"
  tzList += "\n*If you would like to add a time zone to this list, join the `@MoBot#0697 server` and stick it in <#547247266361114655> (#requests-and-suggestions).*"

  return tzList
# end getTimeZoneList