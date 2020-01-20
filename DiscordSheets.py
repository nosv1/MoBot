import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

moBot = "449247895858970624"

arrows = ["⬅", "◀", "➡", "▶"]

async def main(args, message, client):  
  if (args[0][-19:-1] == moBot):
    if (args[2] == "table"):
      await message.channel.send("```Command not currenlty available.```")
    elif ("add" in args and "table" in args):
      await prepareTableDetails(message)
# end main

async def mainReactionAdd(message, payload, client):
  if (payload.user_id != int(moBot)):
    await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
    progress, value = await getAddTableProgress(message)
    if (payload.emoji.name in arrows):
      await incrementValue(message, payload, progress, value)
    elif (payload.emoji.name == "✅"):
      await addTable(message)
    elif (payload.emoji.name == "⬇"):
      await switchProgress(message, progress, "down")
    elif (payload.emoji.name == "⬆"):
      await switchProgress(message, progress, "up")
    elif (payload.emoji.name == "❌"):
      await cancelAddTable(message)
#end mainReactionAdd

async def getAllTables():
  workbook = await openSpreadsheet()
  sheets = workbook.worksheets()
  tables = {}
  
  for sheet in sheets:
    if (sheet.title != "Template"):
      tablesRange = sheet.range("A2:I" + str(sheet.row_count))
      tables[sheet.title] = [] 
      for i in range(0, len(tablesRange), 9):
        if (tablesRange[i].value != ""):
          tableDetails = {
            "ssName" : tablesRange[i+0].value,
            "sName" : tablesRange[i+1].value,
            "firstRow" : tablesRange[i+2].value,
            "firstColumn" : tablesRange[i+3].value,
            "lastRow" : tablesRange[i+4].value,
            "lastColumn" : tablesRange[i+5].value,
            "numberOfHeaders" : tablesRange[i+6].value,
            "refreshIcon" : tablesRange[i+7].value,
            "msgIds" : tablesRange[i+8].value
          }
          tables[sheet.title].append(tableDetails)

  return tables
async def cancelAddTable(message):
  pass
# end cancelAddTable

async def updateTable(message, tableDetails):
  await message.channel.trigger_typing()

  userWorkbook = await openUserSpreadsheet(tableDetails['ssName'])
  userWorksheet = userWorkbook.worksheet(tableDetails['sName'])

  firstRow = int(tableDetails['firstRow'])
  firstColumn = int(tableDetails['firstColumn'])
  lastRow = tableDetails['lastRow']
  lastColumn = tableDetails['lastColumn']
  numberOfHeaders = int(tableDetails["numberOfHeaders"])
  msgIds = tableDetails["msgIds"]

  if (lastRow == "MAX"):
    lastRow = userWorksheet.row_count
  else:
    lastRow = int(lastRow)
  
  if (lastColumn == "MAX"):
    lastColumn = userWorksheet.col_count
  else:
    lastColumn = int(lastColumn)

  numCols = lastColumn - firstColumn + 1
  numRows = lastRow - firstRow + 1

  if (numCols < 1 or numRows < 1):
    await message.channel.send("**Invalid Rows/Columns**\nMake sure the last column and last row is greater than the first column and first row...")
    return

  tableRange = userWorksheet.range(firstRow, firstColumn, lastRow, lastColumn)

  table = [""] # header, body -- in array to add more 'body' elements if needed
  maxWidths = []
  for i in range(numCols):
    maxWidths.append(0)

  for i in range(0, len(tableRange), numCols):
    for j in range(0, numCols):
      if (len(tableRange[i+j].value) > maxWidths[j]):
        maxWidths[j] = len(tableRange[i+j].value)

  horizontalBoarder = ""
  for i in range(sum(maxWidths) + numCols + 1):
    horizontalBoarder += "-"
  table[0] += horizontalBoarder + "\n"
  
  # get the headers
  previousCellWasBlank = True
  rowIsBlank = True
  i = 0
  while (i < numberOfHeaders):
    rowIsBlank = True
    row = "|"
    for j in range(i * numCols, (i + 1) * numCols):
      if (j == i * numCols and tableRange[j].value != ""):
        rowIsBlank = False
        row = "|" + tableRange[j].value.center(maxWidths[j-(i*numCols)])
        previousCellWasBlank = False
      else:
        if (tableRange[j].value == ""):
          row += tableRange[j].value.center(maxWidths[j-(i*numCols)])
          previousCellWasBlank = True
        else:
          rowIsBlank = False
          if (not previousCellWasBlank):
            row += "|"
          else:
            row += " "
          row += tableRange[j].value.center(maxWidths[j-(i*numCols)])
          previousCellWasBlank = False

    if (previousCellWasBlank):
      row += " "
    row += "|\n"

    if (not rowIsBlank):
      table[0] += row + horizontalBoarder + "\n"
    else:
      numberOfHeaders += 1
    i += 1

  # get the body
  previousCellWasBlank = True
  rowIsBlank = True
  previousRowWasBlank = False
  for i in range(numCols * numberOfHeaders, len(tableRange), numCols):
    previousRowWasBlank = rowIsBlank
    rowIsBlank = True
    row = "|"
    for j in range(0, numCols):
      if (j == 0 and tableRange[j+i].value != ""):
        rowIsBlank = False
        row = "|" + tableRange[j+i].value.center(maxWidths[j]) + "|"
        previousCellWasBlank = False
      else:
        if (tableRange[j+i].value != ""):
          rowIsBlank = False
          row = row[:-1] + "|" + tableRange[j+i].value.center(maxWidths[j]) + "|"
          previousCellWasBlank = False
        else:
          row = row[:-1] + " " + tableRange[j+i].value.center(maxWidths[j]) + "|"
    
    if (rowIsBlank):
      row = horizontalBoarder + "\n"
    else:
      row += "\n"
    
    if (len(table[len(table)-1]) > 1900):
      table.append("")

    if (previousRowWasBlank and rowIsBlank):
      table[len(table)-1] = table[len(table)-1][:-len(horizontalBoarder)-1]
      break
    else:
      table[len(table)-1] += row

  table[len(table)-1] += horizontalBoarder


  msgIds = tableDetails["msgIds"]
  tableMsg = None
  if (msgIds == "0"):
    msgIds = ""
    for i in range(len(table)):
      tableMsg = await message.channel.send("```\n" + table[i] + "```")
      msgIds += str(tableMsg.id) + ","
    msgIds = msgIds[:-1]
    tableDetails["msgIds"] = msgIds

  else:
    msgIds = msgIds.split(",")
    if (len(msgIds) == len(table)):
      for i in range(len(table)):
        tableMsg = await message.channel.fetch_message(int(msgIds[i]))
        await tableMsg.edit(content="```\n" + table[i] + "```")

    elif (len(msgIds) < len(table)):
      for i in range(len(msgIds)):
        tableMsg = await message.channel.fetch_message(int(msgIds[i]))
        await tableMsg.edit(content="```\n" + table[i] + "```")
        await tableMsg.remove_reaction("🔄", message.guild.get_member(int(moBot)))
      for i in range(len(msgIds), len(table)):
        tableMsg = await message.channel.send("```\n" + table[i] + "```")
        msgIds.append(str(tableMsg.id))

    elif (len(msgIds) > len(table)):
      for i in range(len(table)):
        tableMsg = await message.channel.fetch_message(int(msgIds[i]))
        await tableMsg.edit(content="```\n" + table[i] + "```")
      i = len(table)
      j = len(msgIds)-1
      while (j >= i):
        msg = await message.channel.fetch_message(int(msgIds[j]))
        await msg.delete()
        del msgIds[j]
        j -= 1
    
    temp = ""
    for i in msgIds:
      temp += i + ","
    tableDetails["msgIds"] = temp[:-1]

  if (tableDetails["refreshIcon"] == "Yes"):
    await tableMsg.add_reaction("🔄")

  workbook = await openSpreadsheet()
  guildSheet = workbook.worksheet(str(message.guild.id))
  tablesRange = guildSheet.range("A2:I" + str(guildSheet.row_count))

  for i in range(0, len(tablesRange), 9):
    if (tablesRange[i+8].value.split(",")[0] == tableDetails["msgIds"].split(",")[0]):
      tablesRange[i+8].value = tableDetails["msgIds"]

  guildSheet.update_cells(tablesRange, value_input_option="USER_ENTERED")
# end updateTable

async def addTable(message):
  await message.channel.trigger_typing()

  guildSheet = await getGuildSheet(message)
  tablesRange = guildSheet.range("A2:I" + str(guildSheet.row_count))

  mc = message.content

  tableDetails = {
    "ssName" : mc.split("Spreadsheet Name: ")[1].split("\n")[0],
    "sName" : mc.split("Sheet Name: ")[1].split("\n")[0],
    "firstRow" : mc.split("First Row [")[1].split("]")[0],
    "firstColumn" : mc.split("First Column [")[1].split("]")[0],
    "lastRow" : mc.split("Last Row [")[1].split("]")[0],
    "lastColumn" : mc.split("Last Column [")[1].split("]")[0],
    "numberOfHeaders" : mc.split("Number of Headers [")[1].split("]")[0],
    "refreshIcon" : mc.split("Refresh Icon [")[1].split("]")[0],
    "msgIds" : "0"
  }
  '''tableExists = False
  for i in range(0, len(tablesRange), 9):
    if (tablesRange[i+0].value == tableDetails["ssName"] and tablesRange[i+1].value == tableDetails["sName"] and tablesRange[i+2].value == tableDetails["firstRow"] and tablesRange[i+3].value == tableDetails["firstColumn"]):
      tableExists = True
      await message.channel.send("```Could not add this table. The First Row and First Column match an existing table. To see your tables, use\n\t@MoBot#0697 sheets tables.```")
      break'''
    
  for i in range(0, len(tablesRange), 9):
    if (tablesRange[i].value == ""):
      tablesRange[i+0].value = tableDetails["ssName"]
      tablesRange[i+1].value = tableDetails["sName"]
      tablesRange[i+2].value = tableDetails["firstRow"]
      tablesRange[i+3].value = tableDetails["firstColumn"]
      tablesRange[i+4].value = tableDetails["lastRow"]
      tablesRange[i+5].value = tableDetails["lastColumn"]
      tablesRange[i+6].value = tableDetails["numberOfHeaders"]
      tablesRange[i+7].value = tableDetails["refreshIcon"]
      msg = await message.channel.send("```Table has been added.```")
      tableDetails["msgIds"] = str(msg.id)
      tablesRange[i+8].value = tableDetails["msgIds"]
      guildSheet.update_cells(tablesRange, value_input_option="USER_ENTERED")
      break
  
  await updateTable(message, tableDetails)
# end addTable

async def incrementValue(message, payload, progress, value):

  oldValue = value
  nonNumberedProgresses = [
    "Refresh Icon"
  ]

  goodValue = True
  if (progress not in nonNumberedProgresses):
    if (oldValue == "MAX"):
      value = 1
    else:
      value = int(oldValue)

    if (payload.emoji.name == "➡"):
      value += 1
    elif (payload.emoji.name == "▶"):
      value += 10
    elif (payload.emoji.name == "⬅"):
      value -= 1
    elif (payload.emoji.name == "◀"):
      value -= 10

    if (progress == "First Row" or progress == "First Column"):
      goodValue = value >= 1
    else:
      if (value < 1):
        value = "MAX"
    
  elif (progress == nonNumberedProgresses[0]):
    if (value == "No"):
      value = "Yes"
    else:
      value = "No"

  if (goodValue):
    mc = message.content
    msgParts = mc.split(progress + " [")
    msgParts[1] = str(value) + "]\n" + mc.split(progress + " [" + oldValue + "]\n")[1]
    await message.edit(content=msgParts[0] + progress + " [" + msgParts[1])
# end incrementValue

async def getAddTableProgress(message):
  mc = message.content
  progress = mc.split("➡")[1]
  value = progress.split("[")[1].split("]")[0]
  progress = progress.split(" [")[0]
  return progress, value
# end getMessageScheduleProgress

async def switchProgress(message, progress, direction):

  mc = message.content
  mc = mc.replace("➡", "  ")

  if (direction == "up"):
    if (progress != "First Row"):
      msgParts = mc.split(progress + " [")
      previousAttribute = msgParts[0].split("\n    ")[-2]
      reply = msgParts[0].split(previousAttribute)[0][:-2] + "➡" + previousAttribute + "\n    " + progress + " [" + msgParts[1]
      await message.edit(content=reply)
  elif (direction == "down"):
    if (progress != "Refresh Icon"):
      msgParts = mc.split(progress + " [")
      nextAttribute = "\n  ➡" + msgParts[1].split("\n    ")[1]
      reply = msgParts[0] + progress + " [" + msgParts[1].split("]")[0] + "]" + nextAttribute + msgParts[1].split(nextAttribute[4:])[1]
      await message.edit(content=reply)
# end switchProgress

async def prepareTableDetails(message):
  await message.channel.trigger_typing()
  mc = message.content
  ssName = mc.split("sheets")[1].split("add")[0].strip()
  sName = mc.split("table")[1].strip()
  
  userWorkbook = None
  userWorkSheet = None
  try:
    userWorkbook = await openUserSpreadsheet(ssName)
    try:
      userWorkSheet = userWorkbook.worksheet(sName)
    except:
      await message.channel.send("```MoBot could not find the sheet name. Make sure you've typed the sheet name exactly as it is.```")
  except:
    await message.channel.send("```Spreadsheet name could not be found. Make sure you've typed the spreadsheet name exactly as it is and you've sent an invite to edit to (see private message).```")
    await message.author.send("Invite the email below be an editor on your spreadsheet. In other words share your spreadsheeet with MoBot.") 
    await message.author.send("mobot-635@mobot-240604.iam.gserviceaccount.com")
  
  if (userWorkbook == None or userWorkSheet == None):
    await message.channel.send("```@MoBot#0697 sheets spreadsheet_name add table sheet_name```")
  else:
    reply = "Add Table\n\n"
    reply += "Spreadsheet Details:\n    "
    reply += "Spreadsheet Name: " + ssName + "\n    "
    reply += "Sheet Name: " + sName + "\n\n"
    reply += "Table Details:\n  ➡"
    reply += "First Row [1]\n    "
    reply += "First Column [1]\n    "
    reply += "Last Row [10]\n    "
    reply += "Last Column [1]\n    "
    reply += "Number of Headers [0]\n    "
    reply += "Refresh Icon [No]\n    "
    reply += "*For the First and Last Column, to get the column numbers, type =column() in a cell in that column."

    msg = await message.channel.send("```" + reply + "```")

    await msg.add_reaction("⬅")
    await msg.add_reaction("◀")
    await msg.add_reaction("➡")
    await msg.add_reaction("▶")
    await msg.add_reaction("⬆")
    await msg.add_reaction("⬇")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
# end addTableDetails

async def getGuildSheet(message):  
  workbook = await openSpreadsheet()
  guild = message.guild
  try:
    guildSheet = workbook.worksheet(str(guild.id))
  except:
    guildSheet = workbook.duplicate_sheet(812751280,new_sheet_name=str(guild.id))
  
  return guildSheet
# end getGuildSheet

async def openUserSpreadsheet(ssName):
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open(ssName)
  return workbook
  
async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1yQeIeccmJlIYJhRODofxI6BuzI3z9tt9-pQkHPiuAn4")
  return workbook
# end openSpreadsheet