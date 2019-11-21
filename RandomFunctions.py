import discord
import asyncio

numberEmojis = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

def numberToEmojiNumbers(number):
  emojiNumbers = ""
  digits = str(number)
  for c in digits:
    for i in range(len(numberEmojis)):
      if (int(c) == i):
        emojiNumbers += numberEmojis[i]
  return emojiNumbers
# end emojiCounter

def emojiNumbertoNumber(emoji):
  return numberEmojis.index(emoji)
# end emojiNumbertoNumber

async def sendErrorToMo(fileName, client, moID):
  await client.get_user(int(moID)).send("%s Error!```%s```" % (fileName, str(traceback.format_exc())))
# end sendErrorToMo

async def sendMessageToMo(message, client, moID):
  await client.get_user(int(moID)).send(message)
# end sendMessageToMo
