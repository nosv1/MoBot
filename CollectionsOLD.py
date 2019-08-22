import discord
import asyncio
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

moBot = "449247895858970624"
nosV1ID = 475325629688971274

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, cilent): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def getCollections(message):
  await message.channel.trigger_typing()

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:B" + str(collectionsSheet.row_count))

  collections = "Collection IDs:\n"
  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == ""):
      break
    elif (collectionsRange[i].value == str(message.guild.id)):
      collections += collectionsRange[i+1].value + "\n"

  await message.channel.send(collections)
# end getCollections

async def leftRightCollection(message, leftRight, embed, client):
  nosV1User = client.get_user(nosV1ID)
  collectionMsg = await nosV1User.send(".")
  channel = collectionMsg.channel

  embed = embed.to_dict()
  if (leftRight == "left"):
    nextPageID = embed["footer"]["text"].split("-- (")[1].split("•")[0]
  else:
    nextPageID = embed["footer"]["text"].split("-- (")[1].split("•")[1][:-1]

  nextPage = await channel.fetch_message(int(nextPageID))
  await message.edit(embed=nextPage.embeds[0])
    
  await collectionMsg.delete()
# end leftRightCollection

async def sendCollection(message, args, toDms, client):
  await message.channel.trigger_typing()

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:B" + str(collectionsSheet.row_count))

  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == ""):
      break
    else:
      if (collectionsRange[i].value in args[3]):
        nosV1User = client.get_user(nosV1ID)
        collectionMsg = await nosV1User.send(".")
        channel = collectionMsg.channel
        await collectionMsg.delete()

        collectionMsg = await channel.fetch_message(int(collectionsRange[i].value))
        page1 = await channel.fetch_message(int(collectionMsg.content.split("Collection:")[1].strip().split(",")[0].strip()))
        embed = page1.embeds[0]

        if (toDms):
          roleIDs = message.content.split(str(collectionMsg.id))[1].strip().split(">")
          roles = message.guild.roles
          
          for role in roles:
            for roleID in roleIDs:
              if (str(role.id) in roleID):
                for member in role.members:
                  try:
                    msg = await member.send(embed=embed)
                    await message.channel.send("Message sent to <@" + str(member.id) + ">.")
                    await msg.add_reaction("⬅")
                    await msg.add_reaction("➡")
                  except discord.errors.Forbidden:
                    await message.channel.send("Message not sent to <@" + str(member.id) + ">.")
                break
        else:
          msg = await message.channel.send(embed=embed)
          await msg.add_reaction("⬅")
          await msg.add_reaction("➡")
        break

# end sendCollection

async def collections(message, isEdit, client):
  await message.channel.trigger_typing()

  nosV1User = client.get_user(nosV1ID)
  if (not isEdit):
    collectionMsg = await nosV1User.send("Collection:")
    channel = collectionMsg.channel

    sourceMessageIDS = message.content.split("create")[1].split(" ")
  else:
    collectionMsg = await nosV1User.send(".")
    channel = collectionMsg.channel
    await collectionMsg.delete()

    collectionMsgID = message.content.split("edit")[1].strip().split(" ")[0]
    collectionMsg = await channel.fetch_message(int(collectionMsgID))
    collectionMsgIDs = collectionMsg.content.split("Collection:")[1].split(",")
    await collectionMsg.edit(content="Collection:")

    sourceMessageIDS = message.content.split(collectionMsgID)[1].split(" ")

    for collectionMsgID in collectionMsgIDs:
      if (collectionMsgID != ""):
        msg = await channel.fetch_message(int(collectionMsgID))
        await msg.delete()

  collectionMsgIDs = ""

  # update collection message
  for sourceMessageID in sourceMessageIDS:
    if (sourceMessageID != ""):
      msg = await message.channel.fetch_message(int(sourceMessageID.strip()))
      embed = msg.embeds[0]
      msg = await nosV1User.send(embed=embed)
      collectionMsgIDs += str(msg.id) + ","
  collectionMsgIDs = collectionMsgIDs[:-1]

  await collectionMsg.edit(content=collectionMsg.content + " " + collectionMsgIDs)

  # update spreadsheet
  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:B" + str(collectionsSheet.row_count))
  
  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == ""):
      collectionsRange[i].value = str(message.guild.id)
      collectionsRange[i+1].value = str(collectionMsg.id)
      collectionsSheet.update_cells(collectionsRange, value_input_option="USER_ENTERED")
      break
  
  # update footers
  collectionMsgIDs = collectionMsgIDs.split(",")
  for i in range(len(collectionMsgIDs)):
    msg = await channel.fetch_message(int(collectionMsgIDs[i]))
    embed = msg.embeds[0].to_dict()
    try:
      embed["footer"]["text"] += " -- ("
    except KeyError:
      embed = discord.Embed.from_dict(embed)
      embed.set_footer(text="-- (")
      embed = embed.to_dict()

    if (len(collectionMsgIDs) == 1):
      embed["footer"]["text"] += str(msg.id) + ")"
    else:
      prevMsg = await channel.fetch_message(int(collectionMsgIDs[i-1]))
      try:
        nextMsg = await channel.fetch_message(int(collectionMsgIDs[i+1]))
      except IndexError:
        nextMsg = await channel.fetch_message(int(collectionMsgIDs[0]))
      embed["footer"]["text"] += str(prevMsg.id) + "•" + str(nextMsg.id) + ")"

    embed = discord.Embed.from_dict(embed)
    await msg.edit(embed=embed)

  await message.channel.send("I think it worked...")
# end createCollection

async def openCollectionsSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("18IkL0Hgm8CjwXaS0BUUPNUSJPbKROrfiSpFehEgD-wE")
  return workbook
# end openCollectionsSpreadsheet