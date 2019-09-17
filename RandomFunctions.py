import asyncio

numberEmojis = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

async def numberToEmojiNumbers(number):
  emojiNumbers = ""
  digits = str(number)
  for c in digits:
    for i in range(len(numberEmojis)):
      if (int(c) == i):
        emojiNumbers += numberEmojis[i]
  return emojiNumbers
# end emojiCounter

async def emojiNumbertoNumber(emoji):
  return numberEmojis.index(emoji)
# end emojiNumbertoNumber