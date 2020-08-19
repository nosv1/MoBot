import discord
import asyncio
from datetime import datetime
import random
from requests_html import HTMLSession
import RandomSupport
import MoBotDatabase
import re
import traceback


moBot = 449247895858970624
mo = 405944496665133058
spaceChar = "⠀"
MEDAL_EMOJI = "🏅"

class Player:
  def __init__(self, user_id, guild_id, percent_correct, wins, losses, games_played):
    self.user_id = user_id
    self.guild_id = guild_id
    self.percent_correct = percent_correct
    self.wins = wins
    self.losses = losses
    self.games_played = games_played
# end Player



async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if args[1].lower() == "hangman":
    players = [message.author.id] + [m.id for m in message.mentions[1:]]
    await newGame(players, message, client)
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client):
  member = message.guild.get_member(payload.user_id)

  if payload.emoji.name == MEDAL_EMOJI:
    await sendLeaderboard(message)

  if payload.emoji.name == RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI:
    players = [member.id]
    await newGame(players, message, client)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove


async def sendLeaderboard(message):
  players = getLeaderboard(message.guild.id)
  players.sort(key=lambda x : x.percent_correct, reverse=True) # best to worst
  top_10 = [p for p in players if p.games_played >= 10][:10] # top 10

  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name=f"{message.guild}\nHangman Leaderboard")
  
  des = ""
  des += f"__Top {len(top_10)} of {len(players)}__\n"
  for i, p in enumerate(top_10):
    des += f"{str(i+1).rjust(2, ' ')}. **{message.guild.get_member(int(p.user_id))}** ({p.percent_correct}% - {p.games_played})\n"

  embed.description = des
  await message.channel.send(embed=embed)
# end sendLeaderboard


async def newGame(players, message, client):
  word = await getWord()
  word = word.lower()
  try:
    defintion = await getDefinition(word)
  except:
    defintion = ""
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
    return (
      len(letterMsg.content) == 1 and 
      letterMsg.author.id in players and 
      letterMsg.channel == message.channel
    )

  correctLetters = set()
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
      correctLetters.add(letter)
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

      if len(message.mentions) <= 1:
        player, leaderboard = await updateLeaderboard(players[0], message.guild.id, winner)
        
        i = len(leaderboard) - 1
        while i >= 0:
          p = leaderboard[i]
          if p.games_played < 10:
            del leaderboard[i]
          i -= 1

        if player.games_played >= 10:
          server_position = str(leaderboard.index(player) + 1)
          if re.match(r"(11$)|(12$)|(13$)|[4567890]$", server_position):
            server_position += "th"
          else:
            end = server_position[-1]
            if "1" == end:
              server_position += "st"
            elif "2" == end:
              server_position += "nd"
            elif "3" == end:
              server_position += "rd"

        v = ""
        v += f"**Stat Line - {message.guild.get_member(player.user_id).display_name}**\n"
        v += f"Win %: `{str(player.percent_correct)}%`\n"
        v += f"Wins/Losses: `{player.wins}/{player.losses}`\n"
        v += f"Games Played: `{player.games_played}`\n"
        v += f"Server Position: `{server_position if player.games_played >= 10 else str(10 - player.games_played) + ' games left'}`\n"
        try:
          v += f"Player Ahead Win %: `{leaderboard[leaderboard.index(player)-1].percent_correct}%`"
        except IndexError: # is leader
          pass
        except ValueError: # not placed yet
          pass

        embed = discord.Embed.from_dict(embed)
        embed.add_field(name=spaceChar, value=v, inline=False)
        embed.set_footer(text=f"| {MEDAL_EMOJI} Leaderboard | {RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI} New Game |")
        await msg.add_reaction(MEDAL_EMOJI)
        await msg.add_reaction(RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI)
        embed = embed.to_dict()


        if message.channel.name == "hangman":
          if leaderboard:
            leader = leaderboard[0]
            try:
              leader_name = message.guild.get_member(int(leader.user_id))
            except:
              leader_name = "unkown..."
            try:
              await message.channel.edit(topic=f"Leader: {leader_name}\nWin %: {leader.percent_correct}%\nGames Played: {leader.games_played}")
            except:
              print("CAUGHT EXCEPTION\n",traceback.format_exc())

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

async def updateLeaderboard(user_id, guild_id, is_winner):
  leaderboard = getLeaderboard(guild_id)

  player_found = None
  for player in leaderboard:
    if player.user_id == str(user_id):
      if is_winner:
        player.wins += 1
      else:
        player.losses += 1
      player.games_played += 1
      player.percent_correct = int((player.wins / player.games_played) * 1000) / 10 # .987 -> 987 -> 98.7
      player_found = player
      break
  
  moBotDB = connectDatabase()

  if player_found:
    moBotDB.cursor.execute(f"""
      UPDATE hangman_leaderboard
      SET 
        percent_correct = '{player_found.percent_correct}',
        {"wins" if is_winner else "losses"} = '{player_found.wins if is_winner else  player_found.losses}',
        games_played = '{player_found.games_played}'
      WHERE 
        user_id = '{player_found.user_id}' AND
        guild_id = '{player_found.guild_id}';
    """)

  else:
    leaderboard.append(Player(
      user_id, guild_id,
      100 if is_winner else 0,  # perc correct
      1 if is_winner else 0,  # wins
      0 if is_winner else 1,  # losses
      1)) # games played
    player_found = leaderboard[-1]
    moBotDB.cursor.execute(f"""
    INSERT INTO hangman_leaderboard (
      `user_id`, `guild_id`, `percent_correct`, `wins`, `losses`, `games_played`
    ) VALUES (
      '{player_found.user_id}',
      '{player_found.guild_id}',
      '{player_found.percent_correct}',
      '{player_found.wins}',
      '{player_found.losses}',
      '{player_found.games_played}'
    );
    """)

  moBotDB.connection.commit()
  moBotDB.connection.close()

  leaderboard.sort(key=lambda x : float(x.percent_correct), reverse=True)
  return player_found, leaderboard
# end updateLeaderboard

def getLeaderboard(guild_id):
  players = []
  moBotDB = connectDatabase()
  moBotDB.cursor.execute(f"""
    SELECT *
    FROM hangman_leaderboard
    WHERE guild_id = '{guild_id}'
  """)
  for record in moBotDB.cursor:
    players.append(Player(*record))
  moBotDB.connection.close()
  return players
# end getLeaderboard



def connectDatabase():
  return MoBotDatabase.connectDatabase("MoBot")
# end getLeaderboard