import discord
import asyncio
from datetime import datetime, timedelta
import math

moBot = 449247895858970624

spaceChar = "⠀"
CALENDEAR_EMOJI = "📅"
COUNTER_CLOCKWISE_EMOJI = "🔄"

weatherPeriod = 384
gameHourLength = 120
sunriseTime = 5
sunsetTime = 21

b = datetime(1970, 1, 1) # used to get total_seconds

async def mainReactionAdd(message, payload, client): 
  member = message.guild.get_member(payload.user_id)

  if (payload.emoji.name == CALENDEAR_EMOJI):
    await handleFutureCast(message, member)
  elif (payload.emoji.name == COUNTER_CLOCKWISE_EMOJI):
    await sendWeatherForecast(message)
    await message.remove_reaction(COUNTER_CLOCKWISE_EMOJI, member)
# end mainReactionAdd

class Weather:
  def __init__(self, name, emoji, thumbnailDay, thumbnailNight):
    self.name = name
    self.emoji = emoji
    self.thumbnailDay = thumbnailDay
    self.thumbnailNight = thumbnailNight
# end Weather

class GTAWeatherState:
  def __init__(self, description, thumbnailURL, gameTimeHrs, gameTimeStr, currentWeatherEmoji, currentWeatherDescription, rainEtaSec, rainEtaStr, isRaining):
    # Describes the time/date the forecast is for (formatted for Discord!)
    self.description = description

    # URL to a thumbnail picture showing the weather
    self.thumbnailURL = thumbnailURL

    # Current in-game time as the number of hours [0.0, 24.0)
    self.gameTimeHrs = int(gameTimeHrs)

    # Current in-game time, formatted as HH:MM (24-hour)
    self.gameTimeStr = gameTimeStr

    # Emoji showing the weather
    self.currentWeatherEmoji = currentWeatherEmoji

    # Name of the weather condition
    self.currentWeatherDescription = currentWeatherDescription

    # Time until it starts/stops raining, in seconds (see `isRaining`)
    self.rainEtaSec = int(rainEtaSec)

    # Time until it starts/stops raining, as a human-readable string (see `isRaining`)
    self.rainEtaStr = rainEtaStr

    # Shows if it's raining.
    # If `true`, then `rainEtaSec` and `rainEtaStr` show when the rain stops, otherwise they show when it starts
    self.isRaining = isRaining
# end GTAWeatherState

class rainETA:
  def __init__(self, etaSec, etaStr, isRaining):
    self.etaSec = etaSec
    self.etaStr = secToVerboseInterval(etaSec)
    self.isRaining = isRaining
# end rainETA

class GTATime:
  def __init__(self, gameTimeHrs, gameTimeStr, weatherPeriodTime):
    self.gameTimeHrs = gameTimeHrs
    self.gameTimeStr = gameTimeStr
    self.weatherPeriodTime = weatherPeriodTime
# end GTATime

# weather states
clearWeatherState = Weather("Clear", "☀️", "https://i.imgur.com/LerUU1Z.png", "https://i.imgur.com/waFNkp1.png")
rainWeatherState = Weather("Raining", "🌧️", "https://i.imgur.com/qsAl41k.png", "https://i.imgur.com/jc98A0G.png")
drizzleWeatherState = Weather("Drizzling", "🌦️", "https://i.imgur.com/Qx18aHp.png", "https://i.imgur.com/EWSCz5d.png")
mistWeatherState = Weather("Misty", "🌁", "https://i.imgur.com/mjZwX2A.png", "https://i.imgur.com/Mh1PDXS.png")
fogWeatherState = Weather("Foggy", "🌫️", "https://i.imgur.com/mjZwX2A.png", "https://i.imgur.com/Mh1PDXS.png")
hazeWeatherState = Weather("Hazy", "🌫️", "https://i.imgur.com/mjZwX2A.png", "https://i.imgur.com/Mh1PDXS.png") # 🏭
snowWeatherState = Weather("Snowy", "❄️", "https://i.imgur.com/WJEjWM6.png", "https://i.imgur.com/1TxfthS.png")
cloudyWeatherState = Weather("Cloudy", "☁️", "https://i.imgur.com/1oMUp2V.png", "https://i.imgur.com/qSOc8XX.png")
mostlyCloudyWeatherState = Weather("Mostly cloudy", "🌥️", "https://i.imgur.com/aY4EQhE.png", "https://i.imgur.com/2LIbOFC.png")
partlyCloudyWeatherState = Weather("Partly cloudy", "⛅", "https://i.imgur.com/aY4EQhE.png", "https://i.imgur.com/2LIbOFC.png")
mostlyClearWeatherState = Weather("Mostly clear", "🌤️", "https://i.imgur.com/aY4EQhE.png", "https://i.imgur.com/2LIbOFC.png")

weatherStateChanges = [
  [0, partlyCloudyWeatherState],
  [4, mistWeatherState],
  [7, mostlyCloudyWeatherState],
  [11, clearWeatherState],
  [14, mistWeatherState],
  [16, clearWeatherState],
  [28, mistWeatherState],
  [31, clearWeatherState],
  [41, hazeWeatherState],
  [45, partlyCloudyWeatherState],
  [52, mistWeatherState],
  [55, cloudyWeatherState],
  [62, fogWeatherState],
  [66, cloudyWeatherState],
  [72, partlyCloudyWeatherState],
  [78, fogWeatherState],
  [82, cloudyWeatherState],
  [92, mostlyClearWeatherState],
  [104, partlyCloudyWeatherState],
  [105, drizzleWeatherState],
  [108, partlyCloudyWeatherState],
  [125, mistWeatherState],
  [128, partlyCloudyWeatherState],
  [131, rainWeatherState],
  [134, drizzleWeatherState],
  [137, cloudyWeatherState],
  [148, mistWeatherState],
  [151, mostlyCloudyWeatherState],
  [155, fogWeatherState],
  [159, clearWeatherState],
  [176, mostlyClearWeatherState],
  [196, fogWeatherState],
  [201, partlyCloudyWeatherState],
  [220, mistWeatherState],
  [222, mostlyClearWeatherState],
  [244, mistWeatherState],
  [246, mostlyClearWeatherState],
  [247, rainWeatherState],
  [250, drizzleWeatherState],
  [252, partlyCloudyWeatherState],
  [268, mistWeatherState],
  [270, partlyCloudyWeatherState],
  [272, cloudyWeatherState],
  [277, partlyCloudyWeatherState],
  [292, mistWeatherState],
  [295, partlyCloudyWeatherState],
  [300, mostlyCloudyWeatherState],
  [306, partlyCloudyWeatherState],
  [318, mostlyCloudyWeatherState],
  [330, partlyCloudyWeatherState],
  [337, clearWeatherState],
  [367, partlyCloudyWeatherState],
  [369, rainWeatherState],
  [376, drizzleWeatherState],
  [377, partlyCloudyWeatherState]
]

async def handleFutureCast(message, member):
  await message.remove_reaction(CALENDEAR_EMOJI, member)
  n = datetime.utcnow()
  history = await message.channel.history(after=message, oldest_first=False).flatten()
  for msg in history:
    if (msg.author.id is member.id):
      try:
        n = datetime.strptime(msg.content.strip(), "%d %m %y %H:%M")
      except ValueError:
        await message.channel.send("**Could not convert message to date**\nPlease use the format `dd mm yy hh:mm`. The numbers MUST BE zero-padded (`1 -> 01`).")
        return None
      break

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(name="GTA V Weather Forecast", icon_url=moBotMember.avatar_url)

  futurecast = "**4-Hour Futurecast for `%s`:**```%s```" % (n.strftime("%a %b %d %H:%M UTC"), getFuturecast(n))

  embed.description = futurecast
  msg = await message.channel.send(embed=embed)
# end updateWeather

async def sendWeatherForecast(message):
  n = datetime.utcnow()

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(name="GTA V Weather Forecast", icon_url=moBotMember.avatar_url)

  currentWeather = getForecast(n)
  currentWeatherStr = "**The in-game time is `%s`, and it is currently `%s` %s.**" % (currentWeather.gameTimeStr, currentWeather.currentWeatherDescription.lower(), currentWeather.currentWeatherEmoji)
  currentRainStr = "**Rain will `%s` in `%s`.**" % ("end" if currentWeather.isRaining else "begin", currentWeather.rainEtaStr.strip())

  future_weather = getForecast(n + timedelta(seconds=currentWeather.rainEtaSec, minutes=1))
  future_weather_str = "**The roads will be `%s` for `%s`.**" % ("dry" if currentWeather.isRaining else "wet", future_weather.rainEtaStr.strip())

  '''futurecast = "**3-Hour Futurecast for `%s`:**```%s```" % (n.strftime("%a %b %d %H:%M UTC"), getFuturecast(n))
  futureRainStr = "**Rain in the next 12 hours:```%s```**" % getFutureRain(n)'''
  
  specificDateInstructions = "**To use a specific date:**\n1. Type a date in the format `dd mm yy hh:mm`\n2. Click the %s\n*The numbers MUST BE zero-padded, and the time zone used is UTC.*\n__Example:__\n`1 February 2003 04:05 UTC` -> `01 02 03 04:05`" % CALENDEAR_EMOJI

  embed.description = "`%s UTC`\n\n%s\n%s\n%s\n\n%s" % (n.strftime("%a %b %d %H:%M"), currentWeatherStr, currentRainStr, future_weather_str, specificDateInstructions)
  embed.set_footer(text="| %s Refresh |" % COUNTER_CLOCKWISE_EMOJI)

  if (message.author.id != moBot):
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction(CALENDEAR_EMOJI)
    await msg.add_reaction(COUNTER_CLOCKWISE_EMOJI)
  else:
    msg = await message.edit(embed=embed)
# end openWeatherSession

# --- GET WEATHER FROM UTC DATE ---

def secToVerboseInterval(seconds):
  if (seconds < 60):
    return "Less than 1 minute"
  
  sMod60 = seconds % 60
  hours = math.floor(seconds / 3600 + (sMod60 / 3600))
  minutes = math.floor((seconds - (hours * 3600)) / 60 + (sMod60 / 60))
  ret = (
    ((str(hours) + (" hours " if (hours > 1) else " hour ")) if (hours > 0) else "") + 
    ((str(minutes) + (" minutes " if (minutes > 1) else " minute ")) if (minutes > 0) else "")
  )

  return ret
# end secToVerboseInterval

def hrsToHHMM(hrs):
  hh = "%02d" % math.floor(hrs)
  mm = "%02d" % math.floor((hrs - math.floor(hrs)) * 60)
  return "%s:%s" % (hh, mm)
# end hrsToHHMM

def getGTATimeFromDate(d):
  timestamp = math.floor((d-b).total_seconds())
  gtaHoursTotal = timestamp / gameHourLength
  gtaHoursDay = gtaHoursTotal % 24

  return GTATime(gtaHoursDay, hrsToHHMM(gtaHoursDay), gtaHoursTotal % weatherPeriod)
# end getGTATimeFromDate

def getWeatherForPeriodTime(periodTime):
  ret = None
  
  if (periodTime > weatherPeriod or periodTime < 0):
    return ret

  for i in range(len(weatherStateChanges)):
    if (weatherStateChanges[i][0] > periodTime):
      ret = weatherStateChanges[i-1][1]
      break

  if (ret is None):
    ret = weatherStateChanges[len(weatherStateChanges) - 1][1]

  return ret
# end getWeatherForPeriodTime

def getRainETA(periodTime, currentWeather):
  if (periodTime > weatherPeriod or periodTime < 0):
    return None
  
  raining = isRaining(currentWeather)
  def getETA():
    for i in range(len(weatherStateChanges) * 2):
      index = i % len(weatherStateChanges)
      offset = math.floor(i / len(weatherStateChanges)) * weatherPeriod
      if (weatherStateChanges[index][0] + offset >= periodTime):
        if (raining ^ isRaining(weatherStateChanges[index][1])):
          return ((weatherStateChanges[index][0] + offset) - periodTime) * gameHourLength
  # end getETA

  eta = getETA()
  return rainETA(eta, eta, raining)
# end getRainETA

def isRaining(state):
  return state is rainWeatherState or state is drizzleWeatherState
# end isRaining 

def isDayTime(gameTimeOfDayHrs):
  return gameTimeOfDayHrs >= sunriseTime and gameTimeOfDayHrs < sunsetTime
# end isDayTime

def getFutureRain(n):
  rainStr = ""
  oldRainState = None
  t = n
  while (t < n + timedelta(hours=24)):
    currentWeather = getForecast(t)
    rainState = currentWeather.isRaining
    if (rainState != oldRainState):
      if (rainState):
        rainStr += "%s - %s\n" % (t.strftime("%H:%M"), currentWeather.rainEtaStr)
    oldRainState = rainState
    t += timedelta(minutes=1)
  return rainStr
# end getFutureRain

def getFuturecast(n):
  report = ""
  t = n
  oldWeatherDescription = None
  while (t < n + timedelta(hours=4)):
    currentWeather = getForecast(t)
    if (currentWeather.currentWeatherDescription != oldWeatherDescription):
      report += "%s - %s\n" % (t.strftime("%H:%M"), currentWeather.currentWeatherDescription.title())
    oldWeatherDescription = currentWeather.currentWeatherDescription
    t += timedelta(minutes=1)
  return report
# end getFuturecast

def getForecast(currentDate):
  gtaTime = getGTATimeFromDate(currentDate)
  currentWeather = getWeatherForPeriodTime(gtaTime.weatherPeriodTime)
  if (currentWeather is None):
    return "Failed to determine current weather"
  rainETA = getRainETA(gtaTime.weatherPeriodTime, currentWeather)
  if (rainETA is None):
    return "Failed to calculate rain ETA"

  return GTAWeatherState(
    "Forecast for **%s**" % currentDate.strftime("%b %d %H:%M UTC"),
    (currentWeather.thumbnailDay if isDayTime(gtaTime.gameTimeHrs) else currentWeather.thumbnailNight),
    gtaTime.gameTimeHrs,
    gtaTime.gameTimeStr,
    currentWeather.emoji,
    currentWeather.name,
    rainETA.etaSec,
    rainETA.etaStr,
    rainETA.isRaining
  )
# end getForecast

# --- END GET WEATHER FROM UTC DATE ---