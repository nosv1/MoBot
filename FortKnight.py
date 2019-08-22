import discord
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

import XboxGamertags

moBot = "<@449247895858970624>"
self = "FortKnight.py"


async def main(args, message, client):
  
  # check if spreadsheet command
  if (args[0][-19:-1] == moBot[-19:-1]):
    try:
      if ("fk " in message.content.lower() and "help" in message.content.lower()):
        await moBotHelp(message, client)
      else:
        await fkSS(args, message, client)
    except IndexError:
      await client.send_message(message.channel, "```" + moBot + "``` for " + moBot + "'s commands.")   
# end main

async def moBotHelp(message, client):
  reply = ""
  reply += "```@Fk rank \"gamertag\"```Find user rank from the spreadsheet.\n"
  reply += "```@Fk stats \"gamertag\"```Find stats for a player.\n"
  reply += "```@Fk registered week #```Displays the registration list for the given week.\n"
  await client.send_message(message.channel, reply)
# end moBotHelp

async def fkSS(args, message, client):
  await client.send_typing(message.channel)
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('FortKnight_client_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open("FortKnight Duos")
  
  stats = workbook.worksheet("Stats")
  registrations = workbook.worksheet("Registration & Placements")
  
  # find rank of specified user
  if (args[1] == "rank"):
    nameFound = False
    nameInput = (await XboxGamertags.main(args, message, client)).lower()
    statNumRows = stats.row_count 
    statNames = stats.range("b2:b" + str(statNumRows))
    mmrs = stats.range("d2:d" + str(statNumRows))
    ranks = stats.range("c2:c" + str(statNumRows))
    rankUpValues = stats.range("g2:g" + str(statNumRows))
    rankDownValues = stats.range("h2:h" + str(statNumRows))
    for i in range(0, len(statNames)):
      if (statNames[i].value != "" and statNames[i].value.lower() == nameInput):
        nameFound = True
        reply = "Rank: " + str(ranks[i].value) + " (" + str(mmrs[i].value) + ")\n"
        reply += "To Next Rank: " + str(rankUpValues[i].value) + "\n"
        reply += "To Rank Below: " + str(rankDownValues[i].value)
        await client.send_message(message.channel, reply)
        break
    if (not nameFound):
      reply = "```Double check your input. To find the rank of a player, type @Fk rank.```"
      await client.send_message(message.channel, reply)
  elif (args[1] == "stats"):
    nameFound = False
    nameInput = message.content.split("\"")[1].lower()
    statNumRows = stats.row_count
    statNames = stats.range("b2:b" + str(statNumRows))
    tournyWins = stats.range("i2:i" + str(statNumRows))
    highestFinishes = stats.range("l2:l" + str(statNumRows))
    for i in range(0, len(statNames)):
      if (statNames[i].value != "" and statNames[i].value.lower() == nameInput):
        nameFound = True
        numWins = tournyWins[i].value
        highestFinsih = highestFinishes[i].value
        reply = "Tournament Wins: " + numWins + "\n"
        reply += "Highest Finish: " + highestFinsih
        await client.send_message(message.channel, reply)
        break
    if (not nameFound):
      reply = "```Double check your input. To find the rank of a player, type @Fk rank.```"
      await client.send_message(message.channel, reply)
      
  elif (args[1] == "registered" and args[2] == "week"):
    OFFSET_PER_WEEK = 6
    FIRST_ROW = 4
    LAST_ROW = 19
    weekNum = int(args[3])
    offset = (6 * (weekNum - 1)) + 1
    col1 = registrations.range(FIRST_ROW, offset, LAST_ROW, offset)
    col2 = registrations.range(FIRST_ROW, offset + 1, LAST_ROW, offset + 1)
    col1Width = 0
    col2Width = 0
    for i in range(0, len(col1)):
      if (col1[i].value != ""):
        if (len(col1[i].value) > col1Width):
          col1Width = len(col1[i].value)
        if (len(col2[i].value) > col2Width):
          col2Width = len(col2[i].value)
    reply = ("```{:>2} {:^" + str(col1Width) + "} {:^" + str(col2Width) + "}\n").format("#", "Player 1", "Player 2")
    for i in range(0, len(col1)):
      if (col1[i].value != ""):
        reply += ("{:>2} {:^" + str(col1Width) + "} ").format(i + 1, col1[i].value)
        reply += ("{:^" + str(col2Width) + "}\n").format(col2[i].value)
    reply += "```"
    await client.send_message(message.channel, reply)
# end fkSS