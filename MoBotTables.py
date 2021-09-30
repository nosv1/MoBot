import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import inspect
import json
import re
from dateutil.relativedelta import relativedelta
from datetime import datetime

import SecretStuff
import MoBotDatabase
import RandomSupport
from RandomSupport import spaceChar, getDetailFromURL, updateDetailInURL, updateFieldValue, a1ToNumeric, numericToA1

moBot = 449247895858970624
mo = 405944496665133058

class Table:
  def __init__(self, tableID, creatorID, workbookKey, worksheetID, tableRange, autoUpdating, bufferMessages, leftAligned, rightAligned, centered, headers, smartMerging, guildID, channelID, messageIDs):
    self.tableID = tableID
    self.creatorID = int(creatorID)
    self.workbookKey = workbookKey
    self.worksheetID = int(worksheetID)
    self.tableRange = tableRange
    self.autoUpdating = int(autoUpdating)
    self.bufferMessages = int(bufferMessages)
    self.leftAligned = leftAligned.split(",")
    self.rightAligned = rightAligned.split(",")
    self.centered = centered.split(",")
    self.headers = int(headers)
    self.smartMerging = int(smartMerging)
    self.guildID = int(guildID)
    self.channelID = int(channelID)
    self.messageIDs = messageIDs.split(",")
# end Table

async def main(args, message, client):  
  if (len(args) >= 3):
    if (len(args) >= 4):
      if ("create" in args[2]):
        await setWorkbookKey(message, message.author)
      elif ("edit" in args[2]):
        await editTable(message)
      elif ("delete" in args[2]):
        await deleteTable(message)
# end main

async def mainReactionAdd(message, payload, client):
  embed = message.embeds[0]
  creatorID = int(embed.author.url.split("creatorID=")[1].split("/")[0])
  creator = message.guild.get_member(payload.user_id)

  if (creatorID == creator.id or creator.id == mo):
    if (payload.emoji.name in RandomSupport.numberEmojis[1:9+1] + [RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI]): # if detail was updated or table refreshed
      if (payload.emoji.name == RandomSupport.numberEmojis[1]):
        await setWorksheetID(message, embed, creator)
      elif (payload.emoji.name == RandomSupport.numberEmojis[2]):
        await setTableRange(message, embed, creator)
      elif (payload.emoji.name == RandomSupport.numberEmojis[3]):
        await toggleAutoUpdate(message, embed)
      elif (payload.emoji.name == RandomSupport.numberEmojis[4]):
        await setBufferMessages(message, embed, creator)
      elif (payload.emoji.name in RandomSupport.numberEmojis[5:7+1]):
        await setAlignment(message, embed, creator, payload)
      elif (payload.emoji.name == RandomSupport.numberEmojis[8]):
        await setNumberOfHeaders(message, embed, creator)
      elif (payload.emoji.name == RandomSupport.numberEmojis[9]):
        await toggleSmartMerging(message, embed)
      try:
        await sendTable(getTableFromEmbedURL(embed.author.url), message, client) # attempt to create and send table
      except discord.errors.HTTPException: # empty message
        pass

  try:
    await message.remove_reaction(payload.emoji, creator)
  except discord.errors.NotFound: # when the message was deleted before removing reaction
    pass
#end mainReactionAdd

async def deleteTable(message):
  tableMessageID = message.content.split("delete")[-1].strip()

  moBotDB = connectDatabase()

  table = findTable(moBotDB, tableMessageID, message.author.id)

  if (table): # exists
    if (table != -1): # is creator
      moBotDB.cursor.execute("DELETE FROM discord_tables WHERE message_ids LIKE '%s%s%s'" % ("%", tableMessageID, "%"))
      moBotDB.connection.commit()
      for msgID in table.messageIDs:
        try:
          msg = await message.guild.get_channel(table.channelID).fetch_message(int(msgID))
          await msg.delete()
        except discord.errors.NotFound:
          pass
        except discord.errors.Forbidden:
          pass
      await message.channel.send("**Table Deleted**", delete_after=7)

    else: # is not creator
      await message.channel.send("**Not Authorizied**\n%s, currently only the creator of the table is authorized to delete a table. The creator for the given table is `%s`." % (message.author.id, message.guild.get_member(table.creatorID).display_name))

  else: # doesn't exist
    await message.channel.send("**Table Not Found**\n%s, the `message_id` given was not found in any of MoBot's existing tables. Make sure the given `message_id` was actually an id of a table." % message.author.mention)
  moBotDB.connection.close()
# end deleteTable

async def editTable(message):
  await message.channel.trigger_typing()

  tableMessageID = message.content.split("edit")[-1].strip()

  moBotDB = connectDatabase()

  table = findTable(moBotDB, tableMessageID, message.author.id)

  if (table): # exists
    if (type(table) != int): # is creator
      moBotMember = message.guild.get_member(moBot)
      embed = defaultEmbed(
        moBotMember, 
        await openUserSpreadsheet(
          table.workbookKey, 
          message.guild.get_channel(table.channelID), 
          message.author, 
          moBotMember
        ), 
        table.workbookKey, 
        table.guildID, 
        table.channelID, 
        message.author
      )

      tableDict = vars(table)
      for var in tableDict: # update the embed with table values
        if (var != "tableID"):
          tableDict[var] = ",".join(tableDict[var]) if type(tableDict[var]) == list else tableDict[var] # converts arrays to csv strings
          embed = updateDetailInURL(embed, var, tableDict[var])

      workbook = await openUserSpreadsheet(table.workbookKey, message.channel, message.author, moBotMember)
      for sheet in workbook.worksheets():
        if (sheet.id == table.worksheetID):
          embed = updateFieldValue(embed, 'Sheet Name', spaceChar * 2 + " " + sheet.title)
          break
      embed = updateFieldValue(embed, 'Table Range', spaceChar * 2 + " " + RandomSupport.stripZero(table.tableRange))
      embed = updateFieldValue(embed, 'Auto Updating', spaceChar * 2 + " " + ("Yes" if table.autoUpdating == 1 else "No"))
      embed = updateFieldValue(embed, 'Number of Buffer Messages', spaceChar * 2 + " " + str(table.bufferMessages))
      embed = updateFieldValue(embed, 'Left Aligned Ranges', spaceChar * 2 + " " + RandomSupport.stripZero(table.leftAligned))
      embed = updateFieldValue(embed, 'Right Aligned Ranges', spaceChar * 2 + " " + RandomSupport.stripZero(table.rightAligned))
      embed = updateFieldValue(embed, 'Centered Ranges', spaceChar * 2 + " " + RandomSupport.stripZero(table.centered))
      embed = updateFieldValue(embed, 'Number of Headers', spaceChar * 2 + " " + str(table.headers))
      embed = updateFieldValue(embed, 'Smart Merging', spaceChar * 2 + " " + ("Yes" if table.smartMerging == 1 else "No"))

      msg = await message.channel.send(embed=embed)
      await addReactions(msg)

    else: # is not creator
      creatorID = table
      await message.channel.send("**Not Authorizied**\n%s, currently only the creator of the table is authorized to edit a table. The creator for the given table is `%s`." % (message.author.mention, message.guild.get_member(creatorID).display_name))

  else: # doesn't exist
    await message.channel.send("**Table Not Found**\n%s, the `message_id` given was not found in any of MoBot's existing tables. Make sure the given `message_id` was actually an id of a table." % message.author.mention)

  moBotDB.connection.close()
# end editTable

async def sendTable(tableDetails, message, client): # embed may be None
  refreshed = datetime.strftime(datetime.utcnow(), "*Refreshed: %b %d %H:%M UTC*")

  try:
    guild = client.get_guild(tableDetails.guildID)
    channel = guild.get_channel(tableDetails.channelID)
    creator = guild.get_member(tableDetails.creatorID)
    moBotMember = guild.get_member(moBot)
  except discord.errors.NotFound:
    return
  except AttributeError:
    return

  workbook = await openUserSpreadsheet(tableDetails.workbookKey, channel, creator, moBotMember)
  tables = createTable(tableDetails, workbook)  

  msgIDs = [int(msgID) for msgID in tableDetails.messageIDs]
  if (msgIDs[0] == -1):
    msgIDs = []

  async def clearMessages():
    await channel.trigger_typing()
    for msgID in msgIDs:
      try:
        msg = await channel.fetch_message(msgID)
        await msg.delete()
      except discord.errors.NotFound:
        pass
    return []
  # end clearMessages

  async def sendNewMessages():
    await channel.trigger_typing()
    for table in tables:
      msg = await channel.send("%s\n%s" % (refreshed if (tables.index(table) == 0) else "", table))
      msgIDs.append(msg.id)
  # end sendNewMessages

  async def sendBufferMessages():
    og_msg = await channel.fetch_message(msgIDs[0])

    buffer_messages_present = 0
    for i, msgID in enumerate(msgIDs):
      msg = await channel.fetch_message(msgID)
      buffer_messages_present += 1 if msg.content == spaceChar else 0

    if og_msg.created_at + relativedelta(minutes=7) > datetime.utcnow(): # this means if the table is trying to be updated after 7 minutes, it will not send new buffer messages if the buffer message number is increased
      for i in range(buffer_messages_present, tableDetails.bufferMessages):
        msg = await channel.send(spaceChar)
        msgIDs.append(msg.id)
  # end sendBufferMessages

  if (tables is not None):
    await channel.trigger_typing()

    for msgID in msgIDs: # first assuming table is already created
      try:
        msg = await channel.fetch_message(msgID)
        await msg.edit(content="%s\n%s" % (refreshed if (msgIDs.index(msgID) == 0) else "", tables[msgIDs.index(msgID)]))
      except discord.errors.NotFound: # if message doesn't exist, delete all existing messages
        msgIDs = await clearMessages()
        await sendNewMessages()
        break
      except IndexError: # less tables than messages
        for msgID in msgIDs[len(tables):]:
          try:
            msg = await channel.fetch_message(msgID)
            await msg.edit(content=spaceChar)
          except discord.errors.NotFound:
            pass

    if not msgIDs: # first time around, no messages exist
      for table in tables:
        msg = await channel.send("%s\n%s" % (refreshed if (tables.index(table) == 0) else "", table))
        msgIDs.append(msg.id)
    await sendBufferMessages()

    if (message is not None):
      embed = message.embeds[0]
      embed = updateDetailInURL(embed, "messageIDs", ",".join([str(msgID) for msgID in msgIDs]))
      await message.edit(embed=embed)
    tableDetails.messageIDs = [str(msgID) for msgID in msgIDs]
    saveTable(tableDetails)
# end sendTable


### --- SETTERS --- ###

def defaultEmbed(moBotMember, workbook, workbookKey, guildID, channelID, creator):

  embed = discord.Embed(
    color = moBotMember.roles[-1].color,
    description = """
**To create a table, %s needs some details:**
- `Spreadsheet Name` (already recieved from url)
- `Sheet Name` (Tab Name) 
- `Table Range` (A1:B10, A:B10, 1:B, A:10, etc.)
- `Auto Updating` (auto updates randomly every 30 minutes)
- `Number of Buffer Messages` (used to avoid character limits for messages)
- `Alignments` (what ranges will be centred or left/right aligned)
- `Number of Headers` (how many rows at the top are headers, used for `smart merging`)
- `Smart Merging` (if a header cell has a blank cell to the right, it will be merged)

**Instructions:**
1. Type the table detail
2. Click the button related to that detail.

**Examples: Setting the `Table Range`**
1. Type a range, `A1:B10`
2. Click the %s

**Notes:**
- `Number of Buffer Messages` is defaulted to at least 1, but if you think your table will get bigger, you can increase this. (Tables will not include blank rows, If a row is blank, that will mark the end of the table.)
- **The max number of total messages is 10.**
- `Auto Updating` and `Smart Merging` are toggleable; no need to type out `Yes` or `No`.
- The `alignment details` take range inputs. Much like the `Table Range` detail but instead of 1 range, each range you want to be aligned needs to be inputted at the same time - `A1:B1 A3:B3`. Inputs can also be `All` or `None` for these details.
- **Once the `Sheet Name` is verified, and the `Table Range` is inputted, a table should be sent to this channel.**
- The table details will be saved and can be edited using this editor or by using the command `@MoBot#0697 table edit message_id`. The `message_id` can be any of the *table messages*. 
- To delete a table, simply `@MoBot#0697 table delete table_message_id`. If you delete a table message, it'll simply resend it (if it's on auto-update).
- Feel free to change the spreadsheet name and sheet name whenever you want; they are only used to get the IDs of the spreadsheet and sheet (which never change).

**Table Details:**
    """ % (moBotMember.mention, RandomSupport.numberEmojis[2]) # keep text unindented!
  )
  embed.set_author(
    name="MoBot Tables (Google Sheets to Discord)", 
    icon_url=moBotMember.avatar_url, 
    url="https://google.com/mobot_tables/creatorID=%s/workbookKey=%s/worksheetID=-1/tableRange=-1/autoUpdating=0/bufferMessages=1/leftAligned=All/rightAligned=None/centered=None/headers=0/smartMerging=0/guildID=%s/channelID=%s/messageIDs=-1" % (creator.id, workbookKey, guildID, channelID)
  )

  embed.add_field(
    name="**%s Spreadsheet Name:**" % RandomSupport.CHECKMARK_EMOJI, 
    value=spaceChar * 2 + " " + workbook.title,
    inline=False
  )
  embed.add_field(
    name="**%s Sheet Name:**" % RandomSupport.numberEmojis[1], 
    value=spaceChar,
    inline=False
  )
  embed.add_field(
    name="**%s Table Range:**" % RandomSupport.numberEmojis[2], 
    value=spaceChar,
    inline=False
  )
  embed.add_field(
    name="**%s Auto Updating:**" % RandomSupport.numberEmojis[3], 
    value=spaceChar * 2 + " " + "No",
    inline=False
  )
  embed.add_field(
    name="**%s Number of Buffer Messages:**" % RandomSupport.numberEmojis[4], 
    value=spaceChar * 2 + " " + "1",
    inline=False
  )
  embed.add_field(
    name="**%s Left Aligned Ranges:**" % RandomSupport.numberEmojis[5],
    value=spaceChar * 2 + " " + "All",
    inline=False
  )
  embed.add_field(
    name="**%s Right Aligned Ranges:**" % RandomSupport.numberEmojis[6],
    value=spaceChar * 2 + " " + "None",
    inline=False
  )
  embed.add_field(
    name="**%s Centered Ranges:**" % RandomSupport.numberEmojis[7],
    value=spaceChar * 2 + " " + "None",
    inline=False
  )
  embed.add_field(
    name="**%s Number of Headers:**" % RandomSupport.numberEmojis[8], 
    value=spaceChar * 2 + " " + "0",
    inline=False
  )
  embed.add_field(
    name="**%s Smart Merging:**" % RandomSupport.numberEmojis[9], 
    value=spaceChar * 2 + " " + "No",
    inline=False
  )
  embed.set_footer(
    text="| Pro-Tip: When setting `Table Details`, you can use the same message. Simply edit the message and click a different button. It should make for an easier cleanup once the table is created. |"
  )

  return embed
# end defaultEmbed

async def setWorkbookKey(message, creator): # step 1, after getting url from command invocation
  moBotMember = message.guild.get_member(moBot)

  url = message.content.split("create")[-1].strip().split(" ")[0] # spliting on " " incase of word after url
  workbookKey = getWorkbookKeyFromURL(url)
  workbook = await openUserSpreadsheet(workbookKey, message.channel, creator, moBotMember)

  msg = None
  if (workbookKey is not None):

    if (workbook is not None):

      msg = await message.channel.send(embed=defaultEmbed(moBotMember, workbook, workbookKey, message.guild.id, message.channel.id, creator))
      await addReactions(msg)

    else: # they already got message for why workbook is none
      return
      
  else:
    await message.channel.send("**Invalid Spreadsheet URL**\n`@MoBot#0697 table create [spreadsheet_url]`")
    return
# end setWorkbookKey

async def setWorksheetID(message, embed, creator):
  moBotMember = message.guild.get_member(moBot)

  url = embed.author.url
  tableDetails = getTableFromEmbedURL(url)
  workbook = await openUserSpreadsheet(tableDetails.workbookKey, message.channel, creator, moBotMember)

  if (workbook is not None):
    sheetName = await getDetailFromHistory(message, creator)

    if (sheetName is not None): # sheet was given
      worksheet = await getSheetFromSheetName(workbook, sheetName, message, creator)

      if (worksheet is not None): # sheet given is valid
        embed = updateDetailInURL(embed, "worksheetID", worksheet.id)
        embed = updateFieldValue(embed, "Sheet Name", spaceChar * 2 + " " + worksheet.title)
        await message.edit(embed=embed)

      else: # message already sent if sheet is none
        return

    else:
      await messageNotFound(message, creator, "Sheet Name", RandomSupport.numberEmojis[2])

  else: # message already sent if workbook is none
    return
# end setWorksheetID

async def setTableRange(message, embed, creator):
  moBotMember = message.guild.get_member(moBot)

  url = embed.author.url
  tableDetails = getTableFromEmbedURL(url)
  workbook = await openUserSpreadsheet(tableDetails.workbookKey, message.channel, creator, moBotMember)

  if (workbook is not None):
    tableRange = await getDetailFromHistory(message, creator)

    if (tableRange is not None):
      tableRange = numericToA1(a1ToNumeric(tableRange)) # validated range
      embed = updateDetailInURL(embed, "tableRange", tableRange)
      embed = updateFieldValue(
        embed, 
        "Table Range", 
        spaceChar * 2 + " " + RandomSupport.stripZero(tableRange)
      )
      await message.edit(embed=embed)

    else:
      await messageNotFound(message, creator, "Table Range", RandomSupport.numberEmojis[2])

  else:
    return
# end setTableRange

async def toggleAutoUpdate(message, embed):
  url = embed.author.url
  autoUpdateStatus = int(getDetailFromURL(url, "autoUpdating"))
  autoUpdateStatus = 1 if autoUpdateStatus is 0 else 0
  autoUpdate = "Yes" if autoUpdateStatus is 1 else "No"
  
  embed = updateDetailInURL(embed, "autoUpdating", autoUpdateStatus)
  embed = updateFieldValue(embed, "Auto Updating", spaceChar * 2 + " " + autoUpdate)
  await message.edit(embed=embed)
# end toggleAutoUpdate

async def setBufferMessages(message, embed, creator):
  url = embed.author.url
  bufferMessages = await getDetailFromHistory(message, creator)
  try:
    bufferMessages = str(int(bufferMessages.split(" ")[0]))
  except ValueError: # no number given
    await message.channel.send("**Invalid Value for `Number of Buffer Messages`**\n%s, Should be a number... 0, 1, 5, etc." % creator.mention)
    return
  
  embed = updateDetailInURL(embed, "bufferMessages", bufferMessages)
  embed = updateFieldValue(embed, "Number of Buffer Messages", spaceChar * 2 + " " + bufferMessages)
  await message.edit(embed=embed)
# end setBufferMessages

async def setAlignment(message, embed, creator, payload):
  url = embed.author.url
  ranges = (await getDetailFromHistory(message, creator)).upper()
  while "  " in ranges:
    ranges = ranges.replace("  ", " ")
  if (ranges.split(" ")[0] not in ["ALL", "NONE"]):
    ranges = [x.strip() for x in re.sub(r'[^A-Z0-9: ]', '', ranges).split(" ")] # keep good chars, split into sep ranges
    for i in range(len(ranges)):
      ranges[i] = numericToA1(a1ToNumeric(ranges[i]))
    ranges = ", ".join(ranges)
  else:
    ranges = ranges.title()

  if (payload.emoji.name == RandomSupport.numberEmojis[5]):
    embed = updateDetailInURL(embed, "leftAligned", ranges.replace(" ", ""))
  elif (payload.emoji.name == RandomSupport.numberEmojis[6]):
    embed = updateDetailInURL(embed, "rightAligned", ranges.replace(" ", ""))
  elif (payload.emoji.name == RandomSupport.numberEmojis[7]):
    embed = updateDetailInURL(embed, "centered", ranges.replace(" ", ""))
  
  ranges = ranges.split(",")
  for i in range(len(ranges)):
    if (ranges[i][-1] == "0"):
      ranges[i] = ranges[i][:-1]

  embed = updateFieldValue(embed, payload.emoji.name, spaceChar * 2 + " " + "".join(ranges))
  await message.edit(embed=embed)
# end setAlignment

async def setNumberOfHeaders(message, embed, creator):
  url = embed.author.url
  numberOfHeaders = await getDetailFromHistory(message, creator)
  try:
    numberOfHeaders = str(int(numberOfHeaders.split(" ")[0]))
  except ValueError: # no number given
    await message.channel.send("**Invalid Value for `Number of Headers`**\n%s, Should be a number... 0, 1, 5, etc." % creator.mention)
    return
  
  if (int(numberOfHeaders) > -1):
    embed = updateDetailInURL(embed, "headers", numberOfHeaders)
    embed = updateFieldValue(embed, "Number of Headers", spaceChar * 2 + " " + numberOfHeaders)
  await message.edit(embed=embed)
# end setNumberOfHeaders

async def toggleSmartMerging(message, embed):
  url = embed.author.url
  smartMergingStatus = int(getDetailFromURL(url, "smartMerging"))
  smartMergingStatus = 1 if smartMergingStatus is 0 else 0
  smartMerging = "Yes" if smartMergingStatus is 1 else "No"
  
  embed = updateDetailInURL(embed, "smartMerging", smartMergingStatus)
  embed = updateFieldValue(embed, "Smart Merging", spaceChar * 2 + " " + smartMerging)
  await message.edit(embed=embed)
# end toggleSmartMerging

### --- END SETTERS --- ####


### --- SUPPORT --- ###
async def getDetailFromHistory(message, creator):
  history = await message.channel.history(after=message, oldest_first=False).flatten()
  for msg in history:
    if (msg.author.id == creator.id):
      return msg.content
# end getDetailFromHistory

def getTableFromEmbedURL(url):
  return Table(
    *[
      -1,
      getDetailFromURL(url, "creatorID"),
      getDetailFromURL(url, "workbookKey"),
      getDetailFromURL(url, "worksheetID"),
      getDetailFromURL(url, "tableRange"),
      getDetailFromURL(url, "autoUpdating"),
      getDetailFromURL(url, "bufferMessages"),
      getDetailFromURL(url, "leftAligned"),
      getDetailFromURL(url, "rightAligned"),
      getDetailFromURL(url, "centered"),
      getDetailFromURL(url, "headers"),
      getDetailFromURL(url, "smartMerging"),
      getDetailFromURL(url, "guildID"),
      getDetailFromURL(url, "channelID"),
      getDetailFromURL(url, "messageIDs"),
    ]
  )
# end getTableDetails

async def getSheetFromSheetName(workbook, sheetName, message, creator):
  for sheet in workbook.worksheets():
    if (sheet.title.lower().strip() == sheetName.lower().strip()):
      return sheet
  await message.channel.send("**Sheet Not Found**\n%s, the sheet name given was not found in the spreadsheet. Please double check your spelling." % creator.mention, delete_after=30)
# end getSheetFromSheetName

def getWorkbookKeyFromURL(url):
  try:
    return url.split("d/")[1].split("/")[0]
  except IndexError: # when d/ not in url
    return None
# end getWorkbookKeyFromURL

async def messageNotFound(message, creator, detail, emoji):
  await message.channel.send(content="**Message Not Found**\n%s, a message could not be found, from you, in this channel, containing a `%s`.\n\nType the `%s`, then click the %s." % (creator.mention, detail, detail, emoji), delete_after=30)
# end messageNotFound

async def addReactions(message):
  for i in range(1, 10):
    await message.add_reaction(RandomSupport.numberEmojis[i])
  await message.add_reaction(RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI)
# end addReactions

def getMoBotMember(message):
  return message.guild.get_member(moBot)
# end getMoBotMember

def createTable(tableDetails, workbook):

  worksheetID = tableDetails.worksheetID
  tableRange = tableDetails.tableRange

  if ("-1" not in [worksheetID, tableRange]): # if we have 2 valid inputs
    sheet = None
    for worksheet in workbook.worksheets():
      if (worksheet.id == worksheetID):
        sheet = worksheet

    rnge = None
    if (sheet is not None):
      tableRange = a1ToNumeric(tableRange)
      cols = tableRange[0]
      rows = tableRange[1]
      cols[1] = sheet.col_count if cols[1] == 0 else cols[1]
      rows[1] = sheet.row_count if rows[1] == 0 else rows[1]
      rnge = sheet.range(rows[0], cols[0], rows[1], cols[1])

      table = RandomSupport.arrayFromRange(rnge) # table[row[col, ...], row[col, ...]] / table[row][col]

      maxWidths = [1 for cell in table[0]] # set widths to 1
      for i in range(len(table)): # loop rows, skipping the headers
        if ("".join([table[i][k].value for k in range(len(table[i]))]) == ""): # if blank row
          if i <= len(table) - 2:
            if "".join([table[i+1][k].value for k in range(len(table[i+1]))]) == "": # if 2 blank rows back to back
              break
          else:
            break

        for j in range(len(table[0])): # loop columns
          maxWidths[j] = len(table[i][j].value) if len(table[i][j].value) > maxWidths[j] else maxWidths[j]

      headerWidths = [[1 for cell in row] for row in table[:tableDetails.headers]]
      for i in range(tableDetails.headers): # loop row
        j = 0
        while j < len(headerWidths[i]): # loop col
          countAdjBlanks = 0
          for k in range(j+1, len(table[i])):
            if (table[i][k].value.strip() == ""):
              countAdjBlanks += 1 
            else:
              break
          if (countAdjBlanks > 0 and tableDetails.smartMerging == 1):
            headerWidths[i][j] = sum(maxWidths[j:j+1+countAdjBlanks]) + countAdjBlanks * 3
            for k in range(j+1, j+1+countAdjBlanks):
              table[i][k].value = "MoBot Merged"
          else: # need to figure out when header width > table width
            headerWidths[i][j] = maxWidths[j]
          j += 1
               
      tables = [] # will be completed tables seperated to fit in a single message
      lines = []

      for o, row in enumerate(table):
        isHeader = table.index(row) < tableDetails.headers
        blank_row = False
        if "".join([cell.value for cell in row]) == "": # if blank row
          if o <= len(table) - 2:
            if "".join([cell.value for cell in table[o+1]]) == "": # if 2 blank rows in a row
              break
            else:
              blank_row = True # force it to put a line
          else:
            break
        line = ""
        for cell in row:
          tempLines = [["" for i in range(3)] for i in range(3)] # templines[i][0 and 1] are for top and bottom border, but not in use right now...
          if (not isHeader):
            for r in tableDetails.leftAligned:
              if (
                RandomSupport.cellInRange(cell, a1ToNumeric(r)) and
                not any(RandomSupport.cellInRange(cell, a1ToNumeric(r2)) for r2 in tableDetails.leftAligned[:tableDetails.leftAligned.index(r)])
              ): # in range but not in any other ranges before this one... 
                tempLines[0][1] += " %s " % (cell.value.ljust(maxWidths[row.index(cell)], " "))
                tempLines[0][1] += '|' if (row.index(cell) + 1 != len(row)) else ""

            for r in tableDetails.rightAligned:
              if (
                RandomSupport.cellInRange(cell, a1ToNumeric(r))
              ): # in range but not in any other ranges before this one... 
                tempLines[1][1] += " %s " % (cell.value.rjust(maxWidths[row.index(cell)], " "))
                tempLines[1][1] += '|' if (row.index(cell) + 1 != len(row)) else ""

            for r in tableDetails.centered:
              if (
                RandomSupport.cellInRange(cell, a1ToNumeric(r)) and 
                not any(RandomSupport.cellInRange(cell, a1ToNumeric(r2)) for r2 in tableDetails.centered[:tableDetails.centered.index(r)])
              ): # in range but not in any other ranges before this one... 
                tempLines[2][1] += " %s " % (cell.value.center(maxWidths[row.index(cell)], " "))
                tempLines[2][1] += '|' if (row.index(cell) + 1 != len(row)) else ""
          else:
            if (cell.value != "MoBot Merged"):
              tempLines[2][1] += " %s " % (cell.value.center(headerWidths[table.index(row)][row.index(cell)], " "))
            try:
              tempLines[2][1] += '|' if table[table.index(row)][row.index(cell)+1:][0].value != "MoBot Merged" else ""
            except IndexError: # when last cell in row
              pass

          line += tempLines[-1][1] if tempLines[-1][1] != "" else (tempLines[-2][1] if tempLines[-2][1] != "" else tempLines[-3][1])

        line = "`%s`" % line
        if (isHeader):
          line += "\n` %s `" % "".center(len(line)-4,"-") # borders for headers,
        if (len("\n".join(lines) + line) < 1900):
          lines.append(line)
        else:
          tables.append("\n".join(lines))
          lines = [line]
      tables.append("\n".join(lines))
      return tables
# end createTable

async def openUserSpreadsheet(key, channel, creator, moBotMember):
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key(key)
  try:
    workbookTitle = workbook.title
  except gspread.exceptions.APIError:
    eType, value, eTraceback = sys.exc_info()
    errorStatus = json.loads(value.__dict__["response"].__dict__["_content"])["error"]["status"]
    if (errorStatus == "PERMISSION_DENIED"):
      await channel.send("**No Access**\n%s, %s does not have access to the spreadsheet. You should have received a message containing an email to share the spreadsheet with. Upon sharing the spreadsheet, you may get an email saying `Delivery Status Notification (Failure)`; you can ignore it.\n\n*At no point will %s edit your spreadsheet, nor share any data.*" % (creator.mention, moBotMember.mention, moBotMember.mention))
      await creator.send("mobot-635@mobot-240604.iam.gserviceaccount.com")
      return None
  return workbook
# end await openUserSpreadsheet


### --- DATABASE --- ###

def saveTable(tableDetails):
  moBotDB = connectDatabase()
  moBotDB.connection.commit()

  tables = getSavedTables(moBotDB)
  tableExists = False
  for table in tables:
    oneMessageID = any(msgID in table.messageIDs for msgID in tableDetails.messageIDs)
    sameRange = tableDetails.workbookKey == table.workbookKey and table.worksheetID == tableDetails.worksheetID and table.tableRange == tableDetails.tableRange
    if (oneMessageID or sameRange):
      tableExists = True
      moBotDB.cursor.execute("""
        UPDATE discord_tables
        SET 
          creator_id = '%s',
          workbook_key = '%s',
          worksheet_id = '%s',
          table_range = '%s',
          auto_updating = '%s',
          buffer_messages = '%s',
          left_aligned = '%s',
          right_aligned = '%s',
          centered = '%s',
          headers = '%s',
          smart_merging = '%s',
          guild_id = '%s',
          channel_id = '%s',
          message_ids = '%s'
        WHERE 
          table_id = '%s'
      """ % (
        tableDetails.creatorID,
        tableDetails.workbookKey,
        tableDetails.worksheetID,
        tableDetails.tableRange,
        tableDetails.autoUpdating,
        tableDetails.bufferMessages,
        ",".join(tableDetails.leftAligned),  
        ",".join(tableDetails.rightAligned),
        ",".join(tableDetails.centered),
        tableDetails.headers,
        tableDetails.smartMerging,
        tableDetails.guildID,
        tableDetails.channelID,
        ",".join(tableDetails.messageIDs),
        table.tableID
      ))

  if (not tableExists):
    moBotDB.cursor.execute("""
      INSERT INTO `MoBot`.`discord_tables`
       (`creator_id`, `workbook_key`, `worksheet_id`, `table_range`, `auto_updating`, `buffer_messages`, `left_aligned`, `right_aligned`, `centered`, `headers`, `smart_merging`, `guild_id`, `channel_id`, `message_ids`)
      VALUES 
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
    """ % (
        tableDetails.creatorID,
        tableDetails.workbookKey,
        tableDetails.worksheetID,
        tableDetails.tableRange,
        tableDetails.autoUpdating,
        tableDetails.bufferMessages,
        ",".join(tableDetails.leftAligned),  
        ",".join(tableDetails.rightAligned),
        ",".join(tableDetails.centered),
        tableDetails.headers,
        tableDetails.smartMerging,
        tableDetails.guildID,
        tableDetails.channelID,
        ",".join(tableDetails.messageIDs),
    ))
  moBotDB.connection.commit()
  moBotDB.connection.close()
# end saveTable

def getSavedTables(moBotDB):
  tables = []
  moBotDB.cursor.execute("SELECT * FROM discord_tables")
  for record in moBotDB.cursor:
    tables.append(Table(*record))
  return tables
# end getSavedTables

def findTable(moBotDB, tableMessageID, creatorID):
  tables = getSavedTables(moBotDB)
  for table in tables:
    if (tableMessageID in table.messageIDs):
      if (table.creatorID == creatorID):
        return table
      else:
        return table.creatorID
  return None
# end findTable

def connectDatabase():
  return MoBotDatabase.connectDatabase('MoBot')
# end connectDatabase