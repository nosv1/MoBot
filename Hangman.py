import discord
import asyncio
from datetime import datetime
import random
from requests_html import HTMLSession
import RandomSupport


moBot = 449247895858970624
mo = 405944496665133058
spaceChar = "⠀"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, cilent): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def newGame(message, client):
  word = await getWord()
  try:
    defintion = await getDefinition(word)
  except:
    await RandomSupport.sendErrorToMo("Hangman", client, mo)
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Hangman", url="https://google.come/word=" + word) # will be more hidden later
  hangmanBoard = [
    "________\n",
    " |     |\n",
    " |      \n",
    " |      \n",
    "_|_     \n\n",
  ]

  wordLocation = ""
  for i in range(len(word)):
    wordLocation += "_ "

  embed.add_field(name=spaceChar, value="```\n" + await getHangMan(False, "", hangmanBoard) + wordLocation + "```", inline=False)
  embed.add_field(name=spaceChar, value="When you want to pick a letter, simply type the letter.\nFor every pick, you get 60 seconds.", inline=False)
  msg = await message.channel.send(embed=embed)

  def check(letterMsg):
    return len(letterMsg.content) == 1 and (letterMsg.author == message.author or str(letterMsg.author.id) in message.content) and letterMsg.channel == message.channel

  correctLetters = []
  trashLetters = "\n\n"
  winner = False
  loser = False
  outOfTime = False
  while True:
    try:
      letterMsg = await client.wait_for("message", timeout=60.0, check=check)
    except asyncio.TimeoutError:
      loser = True
      outOfTime = True

    letter = letterMsg.content.lower()
    if (letter in word):
      correctLetters.append(letter)
      winner = len(correctLetters) == len(set(word))
    else:
      trashLetters += letter
      loser = len(trashLetters.replace("\n", "")) >= 8

    wordLocation = ""
    for c in word:
      if (c in correctLetters or winner or loser):
        wordLocation += c + " "
      else:
        wordLocation += "_ "

    embed = embed.to_dict()
    embed["fields"][0]["value"] = "```\n" + await getHangMan(winner, trashLetters, hangmanBoard) + wordLocation + trashLetters + "```"
    if winner or loser:
      if (winner):
        embed["color"] = int("0x008000", 16)
        embed["fields"][1]["value"] = "**Winner**"
      elif (loser):
        if (outOfTime):
          embed["fields"][1]["value"] = "**Out of Time**"
        else:
          embed["fields"][1]["value"] = "**Loser**"
        embed["color"] = int("0xFF0000", 16)
      embed["fields"][1]["value"] += f"\n*{defintion}*"

    embed = discord.Embed.from_dict(embed)
    try:
      await msg.edit(embed=embed)
      await letterMsg.delete()
    except discord.errors.NotFound:
      break

    if (winner or loser):
      break
  # end newGame

async def getHangMan(winner, trashLetters, hangmanBoard):
  trashLetters = trashLetters.replace("\n", "")

  steps = {
    "head" : " |     O\n",
    "head2" :" |    \O/\n",
    "body" : " |     |\n",
    "arms1" : " |     |\ \n",
    "arms2" : " |    /|\ \n",
    "legs" : "_|_    |\n\n",
    "feet1" : "_|_    |_\n\n",
    "feet2" : "_|_   _|_\n\n",
    "dead1" : "_|_    |\n",
    "dead2" : "      //\n\n",
  } 

  if (not winner):
    if (len(trashLetters) >= 1):
      hangmanBoard[2] = steps["head"]
    if (len(trashLetters) >= 2):
      hangmanBoard[3] = steps["body"]
    if (len(trashLetters) >= 3):
      hangmanBoard[3] = steps["arms1"]
    if (len(trashLetters) >= 4):
      hangmanBoard[3] = steps["arms2"]
    if (len(trashLetters) >= 5):
      hangmanBoard[4] = steps["legs"]
    if (len(trashLetters) >= 6):
      hangmanBoard[4] = steps["feet1"]
    if (len(trashLetters) >= 7):
      hangmanBoard[4] = steps["feet2"]
    if (len(trashLetters) >= 8):
      hangmanBoard[4] = steps["dead1"]
      hangmanBoard.append(steps["dead2"])
  else:
    hangmanBoard[1] = hangmanBoard[1][:-2] + "\n"
    hangmanBoard[2] = steps["head2"]
    hangmanBoard[3] = steps["body"]
    hangmanBoard[4] = steps["feet2"]

  hangmanText = ""
  for i in hangmanBoard:
    hangmanText += i

  return hangmanText
# end getHangMan

async def getWord():
  wordList = open("wordList.txt", "r")
  words = []
  for line in wordList:
    words.append(line.strip())

  word = words[int(random.random() * len(words)) % len(words)]
  return word
# end getWord

async def getDefinition(word):
  session = HTMLSession()
  r = session.get(f"https://www.dictionary.com/browse/{word}")
  html = r.html.html
  return html.split('<meta name="description"')[1].split("See more.")[0].split("content=\"")[1].strip()
# end getDefinition
