import discord
import asyncio
from datetime import datetime, timedelta
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credsOffSeason = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('Noble Leagues Off-Season_client_secret.json'), scope)

async def main(args, message, client):
  pass
#end main

async def mainReactionAdd(message, payload, client):
  teamScrimsTableMessageId = 567832261278433305
  playerScrimsTableMessageId = 567832269755252767
  rankAScrimsTableMessageId = 570726509891944448
  rankBScrimsTableMessageId = 570726526463770645
  
  if (payload.emoji.name == "🔄"): # if update button is clicked
    workbookScrimsResults = await openSpreadsheet(credsOffSeason, "Scrims Results")
    if (message.id == teamScrimsTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getTeamScrimsLeaderboard(message, workbookScrimsResults)
    elif (message.id == playerScrimsTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getPlayerScrimsLeaderboard(message, workbookScrimsResults)
    elif (message.id == rankAScrimsTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getRankScrimsLeaderboard(message, workbookScrimsResults, "A")
    elif (message.id == rankBScrimsTableMessageId):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      await getRankScrimsLeaderboard(message, workbookScrimsResults, "B")
#end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  user = message.guild.get_member(payload.user_id)
  if (user.name != "MoBot"):
    pass
# end mainReactionRemove

async def getRankScrimsLeaderboard(message, workbook, rank):
  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Updating Table```"))
  leaderboardSheet = workbook.worksheet("Leaderboard")
  cells = "F11:H" + str(leaderboardSheet.row_count) if rank == "A" else "J11:L" + str(leaderboardSheet.row_count)
  r = leaderboardSheet.range(cells)

  numCols = 3
  nameWidth = 0
  for i in range(6,len(r), numCols):
    if (len(r[i].value) > nameWidth):
      nameWidth = len(r[i].value)

  horizontalBoarder = ""
  for i in range(numCols + 1 + nameWidth + len(r[4].value) + len(r[5].value)):
    horizontalBoarder += "-"

  tableHeader = "\n" + horizontalBoarder + "\n"
  tableHeader += "|" + str(r[0].value).center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"
  tableHeader += "|" + r[3].value + "".center(nameWidth - len(r[3].value), " ") + "|" + r[4].value.center(6, " ") + "|" + r[5].value.center(5, " ") + "|\n" + horizontalBoarder + "\n"# secondary header

  table = tableHeader

  for i in range(6, len(r), numCols):
    if (r[i].value != ""):
      table += "|" + r[i].value + "".center(nameWidth - len(r[i].value), " ") + "|" + r[i+1].value.center(len(r[4].value), " ") + "|" + r[i+2].value.center(len(r[5].value), " ") + "|\n"
  table += horizontalBoarder 

  await message.edit(content="```" + table + "```")
  moBotMessages.append(await message.channel.send("```Table Updated```"))
  asyncio.sleep(3)
  for msg in moBotMessages:
    await msg.delete()
#end getRankScrimsLeaderboard

async def getTeamScrimsLeaderboard(message, workbook):
  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Updating Table```"))
  leaderboardSheet = workbook.worksheet("Leaderboard")
  r = leaderboardSheet.range("B2:D9")

  numCols = 3
  nameWidth = 0
  for i in range(6,len(r), numCols):
    if (len(r[i].value) > nameWidth):
      nameWidth = len(r[i].value)

  horizontalBoarder = ""
  for i in range(numCols + 1 + nameWidth + len(r[4].value) + len(r[5].value)):
    horizontalBoarder += "-"

  tableHeader = "\n" + horizontalBoarder + "\n"
  tableHeader += "|" + str(r[0].value).center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"
  tableHeader += "|" + r[3].value + "".center(nameWidth - len(r[3].value), " ") + "|" + r[4].value.center(6, " ") + "|" + r[5].value.center(5, " ") + "|\n" + horizontalBoarder + "\n"# secondary header

  table = tableHeader

  for i in range(6, len(r), numCols):
    if (r[i].value != ""):
      table += "|" + r[i].value + "".center(nameWidth - len(r[i].value), " ") + "|" + r[i+1].value.center(len(r[4].value), " ") + "|" + r[i+2].value.center(len(r[5].value), " ") + "|\n"
  table += horizontalBoarder 

  await message.edit(content="```" + table + "```")
  moBotMessages.append(await message.channel.send("```Table Updated```"))
  asyncio.sleep(3)
  for msg in moBotMessages:
    await msg.delete()
#end getTeamScrimsLeaderboard

async def getPlayerScrimsLeaderboard(message, workbook):
  moBotMessages = []
  moBotMessages.append(await message.channel.send("```Updating Table```"))
  leaderboardSheet = workbook.worksheet("Leaderboard")
  r = leaderboardSheet.range("B11:D" + str(leaderboardSheet.row_count))

  numCols = 3
  nameWidth = 0
  for i in range(6, len(r), numCols):
    if (len(r[i].value) > nameWidth):
      nameWidth = len(r[i].value)

  horizontalBoarder = ""
  for i in range(numCols + 1 + nameWidth + len(r[4].value) + len(r[5].value)):
    horizontalBoarder += "-"

  tableHeader = "\n" + horizontalBoarder + "\n"
  tableHeader += "|" + str(r[0].value).center(len(horizontalBoarder) - 2, " ") + "|\n" + horizontalBoarder + "\n"
  tableHeader += "|" + r[3].value + "".center(nameWidth - len(r[3].value), " ") + "|" + r[4].value.center(6, " ") + "|" + r[5].value.center(5, " ") + "|\n" + horizontalBoarder + "\n"# secondary header

  table = tableHeader

  for i in range(6, len(r), numCols):
    if (r[i].value != ""):
      table += "|" + r[i].value + "".center(nameWidth - len(r[i].value), " ") + "|" + r[i+1].value.center(len(r[4].value), " ") + "|" + r[i+2].value.center(len(r[5].value), " ") + "|\n"
    else:
      break
  table += horizontalBoarder 

  await message.edit(content="```" + table + "```")
  moBotMessages.append(await message.channel.send("```Table Updated```"))
  asyncio.sleep(3)
  for msg in moBotMessages:
    await msg.delete()
#end getPlayerScrimsLeaderboard

async def openSpreadsheet(creds, ssName):
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open(ssName)    
  return workbook
# end openSpreadsheet
