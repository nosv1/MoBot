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
X_EMOJI = "❌"
COUNTER_CLOCKWISE_ARROWS_EMOJI = "🔄"
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

def arrayFromRange(tableRange): # google sheets / gspread range
  table = [[tableRange[0]]] # table[row][col]
  for i in range(1, len(tableRange)):
    cell = tableRange[i]
    if (cell.row == table[-1][-1].row):
      table[-1].append(cell)
    else:
      table.append([cell])
  return table
# end arrayFromRange

def getDetailFromURL(url, detail):
  return url.split(detail + "=")[1].split("/")[0]
# end splitOnDetail

def getValueFromField(embed, fieldName):
  embed = embed.to_dict() if type(embed) != dict else embed
  for i in range(len(embed["fields"])):
    if (fieldName in embed["fields"][i]["name"]):
      return embed["fields"][i]["value"]
# end getValueFromField

def updateDetailInURL(url, detail, new):
  old = url.split(detail + "=")[1].split('/')[0]
  return url.replace("%s=%s" % (detail, old), "%s=%s" % (detail, new.replace(" ", "%20")))
# end updateDetailInURL 

def a1ToNumeric(a1): # "A1:B10" -> [[1, 2], [1, 10]]
  a1 = (a1.upper() + ":").split(":")[0:2] # adding : to make sure no error
  cols = []
  rows = []
  for x in a1: # where x is A1 or B10 in A1:B10
    digits = [(ord(c)-ord("A")+1) for c in re.findall(r'[A-Z]', x)] # col = 0 if blank
    digits.reverse()
    for i in range(len(digits)):
      digits[i] = 26 ** i * digits[i]
    cols.append(sum(digits))
    rows.append("".join(re.findall(r'\d', x)))

  # handle blanks 1:B -> cols [1, 2], rows [1, 0] where 0 is max or A1:2 -> cols [1, 0], rows [1,]
  cols[0] = 1 if (cols[0] is 0) else int(cols[0])
  cols[1] = 0 if (cols[1] is 0) else int(cols[1]) # max cols
  rows[0] = 1 if (rows[0] == "") else int(rows[0])
  rows[1] = 0 if (rows[1] == "") else int(rows[1]) # max rows
  if (cols[0] > cols[1] and cols[1] != 0): # big column after small column
    col0= cols[0]
    cols[0] = cols[1]
    cols[1] = col0
  return [cols, rows]
# end a1ToNumeric

def numericToA1(numeric): # [[1, 2], [1, 10]] -> A1:B10
  def colNumToLetters(colNum): # idk how it works, it just does
    letters = []
    while True: # work backwards, get remainder, get letter from remainder, subtract remainder, repeat
      letter = round(((colNum / 26) - (colNum // 26)) * 26) # remainder * 26 is the letter
      letter = 26 if letter == 0 else letter # 26 is Z not 0
      letters.append(chr(letter - 1 + ord('A'))) # get letter
      colNum = (colNum - 1) // 26 # colNum - 1 to avoid 26 / 26
      if (colNum <= 26): # we've reached the last (first) 'digit' letter A if ABC
        if (colNum > 0): # if 0 then ignore
          letters.append(chr(colNum - 1 + ord('A')))
        letters.reverse()
        return "".join(letters)
  # end colNumToLetters

  numeric[0] = [colNumToLetters(x) for x in numeric[0]]
  return "%s%s:%s%s" % (numeric[0][0], numeric[1][0], numeric[0][1], numeric[1][1])
# end numericToA1
