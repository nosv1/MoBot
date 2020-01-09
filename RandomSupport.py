import discord
import asyncio
import traceback
from datetime import datetime
import os
import random
import requests
import re

moBotSupport = 467239192007671818
randomStorage = 649014730622763019

numberEmojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
CHECKMARK_EMOJI = "✅"
spaceChar = "⠀"

def numberToEmojiNumbers(number):
  emojiNumbers = ""
  digits = str(number)
  for c in digits:
    for i in range(len(numberEmojis)):
      if (int(c) == i):
        emojiNumbers += numberEmojis[i]
  return emojiNumbers
# end numberToEmojiNumbers

def emojiNumbertoNumber(emoji):
  return numberEmojis.index(emoji)
# end emojiNumbertoNumber

async def sendErrorToMo(fileName, client, moID):
  await client.get_user(int(moID)).send("%s Error!```%s```" % (fileName, str(traceback.format_exc())))
# end sendErrorToMo

async def sendMessageToMo(message, client, moID):
  await client.get_user(int(moID)).send(message)
# end sendMessageToMo

async def saveImageReturnURL(attachment, client):
  guild = client.get_guild(moBotSupport)
  channel = guild.get_channel(randomStorage)

  n = datetime.utcnow()
  fileName = "%s_%s" % (n.microsecond, attachment.filename)
  await attachment.save(fileName)
  
  f = open(fileName, "rb")
  msg = await channel.send(file=discord.File(f, spoiler=True))
  f.close()
  os.remove(fileName)

  return msg.attachments[0].url
# end saveImageReturnURL

def getRole(guild, roleID):
  for role in guild.roles:
    if (role.id == roleID):
      return role
  else:
    return False
# end getRole

def getRandomCondition(x):
  return random.triangular(0, 1) < x
# end getRandom

def steamIDToSteam64(steamID):
  url = "https://steamid.io/lookup/" + steamID
  site = requests.get(url)
  body = site.text

  return body.split("<a href=\"https://steamid.io/lookup/")[1].split("\"")[0]
# end steamIDToSteam64