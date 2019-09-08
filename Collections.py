import discord
import asyncio
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from numberConversion import *

import SecretStuff

import Reservations

moBot = "449247895858970624"
nosV1ID = 475325629688971274
mo = 405944496665133058

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (args[1] == "collections"):
    await getCollections(message)
  elif (args[2] == "create"):
    await createCollection(message, client)
  elif (args[2] == "display"):
    try:
      collectionName = message.content.split("display")[1].split("@")[0].strip().lower()
    except IndexError:
      await message.channel.send("Include a 'Collection Name' when using the collection display command. To get a list of this server's collections, use `@MoBot#0697 collections`\n\n`@Mobot#0697 collection display [Collection_Name]`")
    await displayCollection(message, False, collectionName, message.guild.id, False, client)
  elif (args[2] == "link"):
    await linkCollectionEmbeds(message, client)
  elif (args[2] == "unlink"):
    nosV1User, nosChannel, nosMsg = await getNosChannel(client)
    parentMsg = await message.channel.fetch_message(int(message.content.split("unlink")[1].strip().split(" ")[0].strip()))
    await unlinkCollection(message, nosChannel, parentMsg, False)
    await nosMsg.delete()
  elif (args[2] == "replace"):
    currentEmbedMsgID = int(message.content.split("replace")[1].strip().split(" ")[0])
    newEmbedMsgID = int(message.content.split(str(currentEmbedMsgID))[1].strip())
    await replaceCollectionEmbed(message, currentEmbedMsgID, newEmbedMsgID, client)
  elif (args[2] == "delete"):
    await deleteCollection(message, client)
  elif (args[2] == "insert"):
    await insertRemoveEmbeds(message, "insert", client)
  elif (args[2] == "remove"):
    await insertRemoveEmbeds(message, "remove", client)
  elif (args[2] == "color"):
    await setCollectionColor(message, client)
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, embed, client):
  if (payload.emoji.name == "💾"):
    member = message.guild.get_member(payload.user_id)
    try:
      msg = await member.send(embed=embed)
      await msg.add_reaction("⬅")
      await msg.add_reaction("➡")
    except discord.errors.Forbidden:
      pass

  elif (payload.emoji.name == "⬅"):
    await collectionControl(message, "left", embed, client)
  elif (payload.emoji.name == "➡"):
    await collectionControl(message, "right", embed, client)
  elif (payload.emoji.name == "➕"):
    await collectionControl(message, "in", embed, client)
    await message.remove_reaction("➕", message.guild.get_member(payload.user_id))
  elif (payload.emoji.name == "➖"):
    await collectionControl(message, "out", embed, client)
    await message.remove_reaction("➖", message.guild.get_member(payload.user_id))
# end mainReactionAdd

async def mainReactionRemove(message, payload, embed, client):
  if (payload.emoji.name == "⬅"):
    await collectionControl(message, "left", embed, client)

  elif (payload.emoji.name == "➡"):
    await collectionControl(message, "right", embed, client)
# end mainReactionRemove

async def getCollections(message):
  await message.channel.trigger_typing()

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  collections = "Collections:\n"
  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == "" and collectionsRange[i-1].value == ""):
      break
    elif (collectionsRange[i].value == str(message.guild.id)):
      collections += collectionsRange[i+2].value + "\n  - "

  await message.channel.send(collections)
# end getCollections

async def setCollectionColor(message, client):
  await message.channel.trigger_typing()

  nosV1User, nosChannel, nosMsg = await getNosChannel(client)

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  collectionColor = message.content.split("#")[1].split(" ")[0].strip()
  collectionName = message.content.split(collectionColor)[1].strip()

  if (collectionName.lower() != "help menu" or message.guild.id != 467239192007671818 or message.author.id == mo): #mobot support

    for i in range(len(collectionsRange)):
      if (collectionsRange[i].value == str(message.guild.id)):
        if (collectionsRange[i+2].value.lower() == collectionName.lower()):
          collectionMsg = await nosChannel.fetch_message(int(collectionsRange[i+1].value))
          collectionIDs = collectionMsg.content.split("Collection:")[1].strip().split(",")

          for msgID in collectionIDs:
            await message.channel.trigger_typing()

            embedMsg = await nosChannel.fetch_message(int(msgID))
            embed = embedMsg.embeds[0].to_dict()

            embed["color"] = int("0x" + collectionColor, 16)
            embedURL = embed["author"]["url"]
            if ("color=" in embedURL):
              embedURL.replace("color=" + embedURL.split("color=")[1].split("/")[0], "color=" + str(embed["color"]))
            else:
              embedURL += "/color=" + str(embed["color"])
            embed["author"]["url"] = embedURL

            embed = discord.Embed.from_dict(embed)
            await embedMsg.edit(embed=embed)
          await message.channel.send("**Collection Color Updated**")
          break

  await nosMsg.delete()
# end setCollectionColor

async def setCollectionAuthorIcon(message, client):
  await message.channel.trigger_typing()

  nosV1User, nosChannel, nosMsg = await getNosChannel(client)

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  authorIconUrl = "http" + message.content.split("http")[1].split(" ")[0].strip()
  collectionName = message.content.split(authorIconUrl)[1].strip()

  if (collectionName.lower() != "help menu" or message.guild.id != 467239192007671818 or message.author.id == mo): #mobot support

    for i in range(len(collectionsRange)):
      if (collectionsRange[i].value == str(message.guild.id)):
        if (collectionsRange[i+2].value.lower() == collectionName.lower()):
          collectionMsg = await nosChannel.fetch_message(int(collectionsRange[i+1].value))
          collectionIDs = collectionMsg.content.split("Collection:")[1].strip().split(",")

          for msgID in collectionIDs:
            await message.channel.trigger_typing()

            embedMsg = await nosChannel.fetch_message(int(msgID))
            embed = embedMsg.embeds[0].to_dict()

            embed["author"]["icon_url"] = authorIconUrl
            embedURL = embed["author"]["url"]
            if ("iconURL=" in embedURL):
              embedURL.replace("iconURL=" + embedURL.split("iconURL=")[1].split("/")[0], "iconURL=" + str(embed["author"]["icon_url"]))
            else:
              embedURL += "/iconURL=" + str(embed["author"]["icon_url"])
            embed["author"]["url"] = embedURL

            embed = discord.Embed.from_dict(embed)
            await embedMsg.edit(embed=embed)
          await message.channel.send("**Collection Author Icon Updated**")
          break

  await nosMsg.delete()
# end setCollectionAuthorIcon

async def insertRemoveEmbeds(message, insertRemove, client):
  await message.channel.trigger_typing()

  nosV1User, nosChannel, nosMsg = await getNosChannel(client)

  # get current embed msg
  if (insertRemove == "insert"):
    beforeAfter = message.content.split("insert")[1].strip().split(" ")[0].strip()
    currentEmbedMsg = await message.channel.fetch_message(int(message.content.split(beforeAfter)[1].strip().split(" ")[0].strip()))
  elif (insertRemove == "remove"):
    currentEmbedMsg = await message.channel.fetch_message(int(message.content.split("remove")[1].strip().split(" ")[0].strip()))

  currentEmbed = currentEmbedMsg.embeds[0]
  currentEmbedURL = currentEmbed.author.url

  if (currentEmbed.author.name != "MoBot's Command Help Menu" or message.author.id == mo):

    reactions = currentEmbedMsg.reactions
    await currentEmbedMsg.clear_reactions()

    # get collection IDs
    collectionMsg = await nosChannel.fetch_message(int(currentEmbedURL.split("collection=")[1].split("/")[0].strip()))
    collectionIDs = collectionMsg.content.split("Collection:")[1].strip().split(",")

    if (insertRemove == "insert"):
      newIds = message.content.split(str(currentEmbedMsg.id))[1].strip().split(" ")
    elif (insertRemove == "remove"):
      countToRemove = int(message.content.split(str(currentEmbedMsg.id))[1].strip())
      if (countToRemove == len(collectionIDs)):
        workbook = await openCollectionsSpreadsheet()
        sheet = workbook.worksheet("Collections")
        r = sheet.range("A2:C" + str(sheet.row_count))
        await deleteCollectionFromNOS(message, collectionMsg.id, client)
        await deleteCollectionFromSpreadsheet(message, collectionMsg.id, sheet, r)
        collectionIDs = []
      else:
        i = collectionIDs.index(currentEmbedURL.split("id=")[1].split("/")[0])
        count = 0
        while (count < countToRemove):
          collectionEmbed = await nosChannel.fetch_message(int(collectionIDs[i]))
          await unlinkCollection(message, nosChannel, collectionEmbed, True)
          await collectionEmbed.delete()
          del collectionIDs[i]

          try:
            i = collectionIDs.index(currentEmbedURL.split("right=")[1].split("/")[0])
          except ValueError:
            break
          count += 1

    # get new collection message content
    if (insertRemove == "insert"):
      currentEmbedIndex = collectionIDs.index(currentEmbedURL.split("id=")[1].split("/")[0])
      if (beforeAfter.lower() == "before"):
        for i in range(len(newIds)-1, -1, -1):
          if (newIds[i].strip() != ""):
            newMsg = await message.channel.fetch_message(int(newIds[i].strip()))
            newEmbed = newMsg.embeds[0]
            newEmbedMsg = await nosChannel.send(embed=newEmbed)
            collectionIDs.insert(currentEmbedIndex, str(newEmbedMsg.id))

      elif (beforeAfter.lower() == "after"):
        for i in range(len(newIds)-1, -1, -1):
          if (newIds[i].strip() != ""):
            newMsg = await message.channel.fetch_message(int(newIds[i].strip()))
            newEmbed = newMsg.embeds[0]
            newEmbedMsg = await nosChannel.send(embed=newEmbed)
            collectionIDs.insert(currentEmbedIndex + 1, str(newEmbedMsg.id))


    # update collectionMsg
    reply = "Collection: "
    for embedID in collectionIDs:
      reply += embedID + ","
    reply = reply[:-1]

    # update left/rights
    for i in range(len(collectionIDs)):

      msg = await nosChannel.fetch_message(int(collectionIDs[i]))
      embed = msg.embeds[0].to_dict()
      embed["author"]["url"] = "https://google.com/MoBotCollection"
      embed["author"]["url"] += "/collection=" + str(collectionMsg.id)
      embed["author"]["url"] += "/id=" + str(msg.id)

      if (len(collectionIDs) == 1):
        embed["author"]["url"] += "/left=" + str(msg.id) + "/right=" + str(msg.id)
      else:
        if (beforeAfter.lower() == "after" and currentEmbedIndex + 1 == len(collectionIDs) - 1 and i == 0):
          prevMsg = await nosChannel.fetch_message(int(collectionIDs[i-2]))
        else:
          prevMsg = await nosChannel.fetch_message(int(collectionIDs[i-1]))
        try:
          nextMsg = await nosChannel.fetch_message(int(collectionIDs[i+1]))
        except IndexError:
          nextMsg = await nosChannel.fetch_message(int(collectionIDs[0]))

        embed["author"]["url"] += "/left=" + str(prevMsg.id) + "/right=" + str(nextMsg.id)

        prevEmbedURL = prevMsg.embeds[0].author.url
        nextEmbedURL = nextMsg.embeds[0].author.url

        out = ""
        if ("out=" in prevEmbedURL):
          out = "/out=" + prevEmbedURL.split("out=")[1].split("/")[0]
        elif ("out=" in nextEmbedURL):
          out = "/out=" + nextEmbedURL.split("out=")[1].split("/")[0] 
        embed["author"]["url"] += out

      embed = discord.Embed.from_dict(embed)
      await msg.edit(embed=embed)

      # ONLY RELEVANT TO INSERTREMOVE FUNCTION
      if (insertRemove == "insert"):
        if (collectionIDs[i] == currentEmbedURL.split("id=")[1].split("/")[0]):
          currentEmbedURL = embed.author.url
          await currentEmbedMsg.edit(embed=embed)
      elif (insertRemove == "remove"):
        if (collectionIDs[i] == currentEmbedURL.split("left=")[1].split("/")[0]):
          currentEmbedURL = embed.author.url
          await currentEmbedMsg.edit(embed=embed)
      # ---

    if (len(collectionIDs) > 0):
      await collectionMsg.edit(content=reply)
      for reaction in reactions:
        await currentEmbedMsg.add_reaction(reaction.emoji)
      if ("in=" not in currentEmbedURL):
        await currentEmbedMsg.remove_reaction("➕", currentEmbedMsg.author)
      if ("out=" not in currentEmbedURL):
        await currentEmbedMsg.remove_reaction("➖", currentEmbedMsg.author)
    else:
      try:
        await collectionMsg.delete()
      except discord.errors.NotFound:
        pass

    if (insertRemove == "insert"):
      await message.channel.send("**Embeds Inserted**")
    elif (insertRemove == "remove"):
      await message.channel.send("**Embeds Removed**")

  await nosMsg.delete()
# end insertEmbeds

async def replaceCollectionEmbed(message, currentEmbedMsgID, newEmbedMsgID, client):
  await message.channel.trigger_typing()

  nosV1User, nosChannel, collectionMsg = await getNosChannel(client)

  currentEmbedMsg = None
  newEmbedMsg = None
  reactions = None
  for channel in message.guild.channels:
    try:
      currentEmbedMsg = await channel.fetch_message(currentEmbedMsgID)
      reactions = currentEmbedMsg.reactions
      await currentEmbedMsg.clear_reactions()
    except discord.errors.NotFound:
      pass
    except AttributeError:
      pass

    try:
      newEmbedMsg = await channel.fetch_message(newEmbedMsgID)
    except discord.errors.NotFound:
      pass
    except AttributeError:
      pass

    if (currentEmbedMsg != None and newEmbedMsg != None):
      currentEmbed = currentEmbedMsg.embeds[0]
      currentEmbed = currentEmbed.to_dict()
      newEmbed = newEmbedMsg.embeds[0]
      newEmbed = newEmbed.to_dict()

      if (currentEmbed["author"]["name"] != "MoBot's Command Help Menu" or message.author.id == mo):

        try:
          nosEmbedMsgID = int(currentEmbed["author"]["url"].split("id=")[1].split("/")[0])
          nosEmbedMsg = await nosChannel.fetch_message(nosEmbedMsgID)

          newEmbed["author"]["url"] = currentEmbed["author"]["url"]
          newEmbed = discord.Embed.from_dict(newEmbed)
          currentEmbedMsg = await message.channel.fetch_message(currentEmbedMsgID)
          if (newEmbed.author.url == currentEmbedMsg.embeds[0].author.url):
            await nosEmbedMsg.edit(embed=newEmbed)
            await currentEmbedMsg.edit(embed=newEmbed)
          break
        except KeyError:
          break
      break

  if (reactions != None):
    for reaction in reactions:
      await currentEmbedMsg.add_reaction(reaction.emoji)

  await collectionMsg.delete()
# end replaceCollectionEmbed

async def unlinkCollection(message, nosChannel, embedMsg, isDelete):
  await message.channel.trigger_typing()

  async def removeOutIn(outIn, embed):
    embed = embed.to_dict()
    embedURL = embed["author"]["url"]
    try:
      embedURL = embedURL.replace("/" + outIn + "=" + embedURL.split(outIn + "=")[1].split("/")[0], "")
    except IndexError:
      pass
    embed["author"]["url"] = embedURL
    embed = discord.Embed.from_dict(embed)
    return embed
  # end removeOut    

  if (not isDelete):
    await embedMsg.remove_reaction("➕", embedMsg.author)
    await embedMsg.edit(embed=await removeOutIn("in", embedMsg.embeds[0]))

  embed = embedMsg.embeds[0]
  embedMsg = await nosChannel.fetch_message(int(embed.author.url.split("id=")[1].split("/")[0]))
  embedURL = embedMsg.embeds[0].author.url

  if (embedMsg.embeds[0].author.name != "MoBot's Command Help Menu" or message.author.id == mo):

    if (isDelete):
      if ("out=" in embedURL):
        parentMsg = await nosChannel.fetch_message(int(embedURL.split("out=")[1].split("/")[0]))
        await parentMsg.edit(embed=await removeOutIn("in", parentMsg.embeds[0]))

        if (not isDelete):
          while ("out=" in embedURL):
            await embedMsg.edit(embed=await removeOutIn("out", embedMsg.embeds[0]))
            embedMsg = await nosChannel.fetch_message(int(embedMsg.embeds[0].author.url.split("right=")[1].split("/")[0]))
            embedURL = embedMsg.embeds[0].author.url

    if ("in=" in embedURL):
      await embedMsg.edit(embed=await removeOutIn("in", embedMsg.embeds[0]))
      embedMsg = await nosChannel.fetch_message(int(embedURL.split("in=")[1].split("/")[0]))
      embedURL = embedMsg.embeds[0].author.url
      
      while ("out=" in embedURL):
        await embedMsg.edit(embed=await removeOutIn("out", embedMsg.embeds[0]))
        embedMsg = await nosChannel.fetch_message(int(embedMsg.embeds[0].author.url.split("right=")[1].split("/")[0]))
        embedURL = embedMsg.embeds[0].author.url

    await message.channel.send("**Collection Unlinked**")
# end unlinkCollection

async def linkCollectionEmbeds(message, client):
  await message.channel.trigger_typing()

  parentMsgID = int(message.content.split("link")[1].strip().split(" ")[0])
  childCollectionName = message.content.split(str(parentMsgID))[1].strip().lower()
  try:
    parentMsg = await message.channel.fetch_message(parentMsgID)
    reactions = parentMsg.reactions
    await parentMsg.clear_reactions()
  except:
    await message.channel.send("There was an error getting the 'Parent Collection Message ID'.\n\nWhen using the 'collection link' command, first get the Message ID of the 'Parent Collection', then use `@MoBot#0697 collection link [Parent_Collection_Message_ID] [Child_Collection_Name]`")

  try:
    linkCollection = False

    parentEmbed = parentMsg.embeds[0]
    parentEmbed = parentEmbed.to_dict()
    parentURL = parentEmbed["author"]["url"]
    parentEmbedID = parentURL.split("id=")[1].split("/")[0]

    if (parentEmbed["author"]["name"] != "MoBot's Command Help Menu" or message.author.id == mo):

      if ("in=" in parentURL):
        def checkEmoji(payload):
          messageID = payload.message_id
          userID = payload.user_id
          return userID == message.author.id and moBotMessage.id == messageID and (payload.emoji.name == "✅" or payload.emoji.name == "❌")

        moBotMessage = await message.channel.send("This page is already linked to a collection.\n\n**Would you like to replace it?** *This cannot be undone.*")
        await moBotMessage.add_reaction("✅")
        await moBotMessage.add_reaction("❌")

        payload = await client.wait_for('raw_reaction_add', check=checkEmoji)
        if (payload.emoji.name == "✅"):
          await message.channel.trigger_typing()
          linkCollection = True

        elif (payload.emoji.name == "❌"):
          await message.channel.send("**Collection Link Canceled**")
      else:
        linkCollection = True

      if (linkCollection):
        workbook = await openCollectionsSpreadsheet()
        collectionsSheet = workbook.worksheet("Collections")
        collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

        for i in range(len(collectionsRange)):
          if (collectionsRange[i].value == ""):
            break
          elif (collectionsRange[i-2].value == str(message.guild.id) and collectionsRange[i].value.lower() == childCollectionName):
            nosV1User, nosChannel, collectionMsg = await getNosChannel(client)

            childCollectionID = int(collectionsRange[i-1].value)
            childCollectionMsg = await nosChannel.fetch_message(childCollectionID)
            childCollectionMsgIDs = childCollectionMsg.content.split("Collection:")[1].strip().split(",")

            for i in range(len(childCollectionMsgIDs)):
              childEmbedMsg = await nosChannel.fetch_message(int(childCollectionMsgIDs[i]))
              childEmbed = childEmbedMsg.embeds[0]
              childEmbed = childEmbed.to_dict()
              childURL = childEmbed["author"]["url"]
              if ("out=" not in childURL):
                childURL += "/out=" + str(parentEmbedID)
              else:
                childURL = childURL.replace(childURL.split("out=")[1].split("/")[0], str(parentEmbedID))
              childEmbed["author"]["url"] = childURL
              childEmbed = discord.Embed.from_dict(childEmbed)
              await childEmbedMsg.edit(embed=childEmbed)

            if ("in=" not in parentURL):
              parentURL += "/in=" + str(childCollectionMsgIDs[0])
            else:
              parentURL = parentURL.replace(parentURL.split("in=")[1].split("/")[0], str(childCollectionMsgIDs[0]))
            parentEmbed["author"]["url"] = parentURL
            parentEmbed = discord.Embed.from_dict(parentEmbed)
            await parentMsg.edit(embed=parentEmbed)

            await replaceCollectionEmbed(message, parentMsg.id, parentMsg.id, client)
            await message.channel.send("**Collections Linked**")

            for reaction in reactions:
              await parentMsg.add_reaction(reaction.emoji)
            await parentMsg.add_reaction("➕")

            await collectionMsg.delete()
            break

    else:
      for reaction in reactions:
        await parentMsg.add_reaction(reaction.emoji)

  except IndexError:
    await message.channel.send("The Message ID you provided did not have an embed. Make sure you're providing the Message ID of the Parent Collection. It should also be noted, the page currently displayed is what will link the two collections.")
# end linkCollectionEmbeds

async def collectionControl(message, control, embed, client):
  nosV1User, nosChannel, collectionMsg = await getNosChannel(client)

  embed = embed.to_dict()
  if (control == "left"):
    nextPageID = embed["author"]["url"].split("left=")[1].split("/")[0]
  elif (control == "right"):
    nextPageID = embed["author"]["url"].split("right=")[1].split("/")[0]
  elif (control == "in"):
    nextPageID = embed["author"]["url"].split("in=")[1].split("/")[0]
  elif (control == "out"):
    nextPageID = embed["author"]["url"].split("out=")[1].split("/")[0]

  try:
    nextPage = await nosChannel.fetch_message(int(nextPageID))
  except discord.errors.NotFound:
    if (control == "left" or control == "right"):
      await message.clear_reactions()
      await message.edit(content="**Collection No Longer Exists**")
    elif (control == "in"):
      await message.remove_reaction("➕", message.author)
      embed["author"]["url"] = embed["author"]["url"].replace("/in=" + embed["author"]["url"].split("in=")[1].split("/")[0], "")
      embed = discord.Embed.from_dict(embed)
      await message.edit(embed=embed)
      await replaceCollectionEmbed(message, message.id, message.id, client)
    elif (control == "out"):
      await message.remove_reaction("➖", message.author)
    await collectionMsg.delete()
    return

  nextPageEmbed = nextPage.embeds[0].to_dict()
  nextPageURL = nextPageEmbed["author"]["url"]
  if ("color=" in nextPageURL):
    nextPageEmbed["color"] = int(nextPageURL.split("color=")[1].split("/")[0])
  nextPageEmbed = discord.Embed.from_dict(nextPageEmbed)
  nextPageEmbed = await correctMoBotHelpMenu(nextPage, nextPageEmbed)
  await message.edit(embed=nextPageEmbed)

  isReservation = "MoBotReservation" in nextPageURL
  if (isReservation):
      await asyncio.sleep(2.5)
      message = await message.channel.fetch_message(message.id)
      if (message.embeds[0].author.url == nextPageURL):
        r = ["💾", "⬅", "➡"]
        reactions = message.reactions
        for reaction in reactions:
          if (reaction.emoji not in r):
            users = reaction.users()
            async for user in users:
              try:
                await message.remove_reaction(reaction.emoji, user)
              except discord.Forbidden:
                pass

        emojis = nextPageURL.split("emojis=")[1].split("/")[0].split(",")
        for emoji in emojis:
          await message.add_reaction(emoji)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        await message.add_reaction("🗑")

  if ("in=" in nextPageURL):
    await message.add_reaction("➕")
  else:
    await message.remove_reaction("➕", message.author)

  if ("out=" in nextPageURL):
    await message.add_reaction("➖")
  else:
    await message.remove_reaction("➖", message.author)

  isMoBotHelpMenu = "MoBot's Command Help Menu" in nextPageEmbed.author.name
  if (isMoBotHelpMenu):
    await asyncio.sleep(5)
    message = await message.channel.fetch_message(message.id)
    if (message.embeds[0].author.url == nextPageURL):
      history = await message.channel.history(limit=10).flatten()
      header = "Guild: " + message.guild.name + "\nChannel: #" + message.channel.name + "\n\n"
      content = ""
      for msg in history:
        content = "<@" + str(msg.author.id) + ">: " + msg.content + "\n" + content
      content = header + content
      embed = message.embeds[0]
      #if (str(member.id) != str(mo)):
      await client.get_user(int(mo)).send(content=content, embed=embed)
    
  await collectionMsg.delete()
# end collectionControl

async def displayCollection(message, toDMs, collectionName, guildID, isReservation, client):
  await message.channel.trigger_typing()

  if (isReservation):
    workbook = await Reservations.openReservationsSpreadsheet()
    collectionsSheet = workbook.worksheet("Reservations")
  else:
    workbook = await openCollectionsSpreadsheet()
    collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value.lower() == collectionName.lower()):
      if (collectionsRange[i-2].value == str(guildID)):
        nosV1User, nosChannel, msg = await getNosChannel(client)


        collectionMsgID = int(collectionsRange[i-1].value)
        collectionMsg = await nosChannel.fetch_message(collectionMsgID)
        firstEmbedMsgID = int(collectionMsg.content.split("Collection:")[1].split(",")[0].strip())
        firstEmbedMsg = await nosChannel.fetch_message(firstEmbedMsgID)
        firstEmbed = firstEmbedMsg.embeds[0]
        firstEmbedURL = firstEmbed.author.url

        if (toDMs):
          roleIDs = message.content.split(str(collectionMsg.id))[1].strip().split(">")
          roles = message.guild.roles
          
          for role in roles:
            for roleID in roleIDs:
              if (str(role.id) in roleID):
                for member in role.members:
                  try:
                    firstEmbed = await correctMoBotHelpMenu(firstEmbedMsg, firstEmbed)
                    embedMsg = await message.channel.send(embed=firstEmbed)
                    await message.channel.send("Message sent to " + member.mention + ".")
                    await embedMsg.add_reaction("💾")
                    await embedMsg.add_reaction("⬅")
                    await embedMsg.add_reaction("➡")
                    if ("in=" in firstEmbedURL):
                      await embedMsg.add_reaction("➕")
                    if ("out=" in firstEmbedURL):
                      await embedMsg.add_reaction("➖")

                  except discord.errors.Forbidden:
                    await message.channel.send("Message not sent to " + member.mention + ".")
                break

        else:
          embedMsg = await message.channel.send(embed=firstEmbed)
          await embedMsg.add_reaction("💾")
          await embedMsg.add_reaction("⬅")
          await embedMsg.add_reaction("➡")
          if ("in=" in firstEmbedURL):
            await embedMsg.add_reaction("➕")
          if ("out=" in firstEmbedURL):
            await embedMsg.add_reaction("➖")

          if (isReservation):
            emojis = firstEmbed.author.url.split("emojis=")[1].split("/")[0].split(",")
            for emoji in emojis:
              await embedMsg.add_reaction(emoji)
            await embedMsg.add_reaction("✅")
            await embedMsg.add_reaction("❌")
            await embedMsg.add_reaction("🗑")

        await msg.delete()
        break
# end displayCollection

async def deleteCollectionFromNOS(message, collectionMsgID, client):
  nosV1User, nosChannel, nosMsg = await getNosChannel(client)

  msg = await nosChannel.fetch_message(collectionMsgID)
  msgIDs = msg.content.split("Collection: ")[1].split(",")

  for msgID in msgIDs:
    try:
      tMsg = await nosChannel.fetch_message(int(msgID))
      await unlinkCollection(message, nosChannel, tMsg, True)
      await tMsg.delete()
    except discord.errors.NotFound:
      pass
  await msg.delete()

  await nosMsg.delete()
# end deleteCollectionFromNOS

async def deleteCollectionFromSpreadsheet(message, collectionMsgID, collectionsSheet, collectionsRange):
  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == str(collectionMsgID)):
      for j in range(i-1, len(collectionsRange)):
        try:
          collectionsRange[j].value = collectionsRange[j+3].value
        except IndexError:
          break
      break

  collectionsSheet.update_cells(collectionsRange, value_input_option="USER_ENTERED")
  await message.channel.send("**Collection Deleted**")

  return collectionsRange
# end deleteCollectionFromSpreadsheet

async def deleteCollection(message, client):
  await message.channel.trigger_typing()

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  collectionName = message.content.split("delete")[1].strip()

  for i in range(len(collectionsRange)):
    if (collectionsRange[i].value == "" and collectionsRange[i-1].value == ""):
      await message.channel.send("Could not find a collection with the name '" + collectionName + "'.")
      break
    elif (collectionsRange[i].value.lower() == collectionName.lower()):
      if (collectionsRange[i-2].value == str(message.guild.id)):
        if (collectionsRange[i-2].value != 467239192007671818 or collectionsRange[i].value.lower() != "help menu"):
          await deleteCollectionFromNOS(message, int(collectionsRange[i-1].value), client)
          await deleteCollectionFromSpreadsheet(message, int(collectionsRange[i-1].value), collectionsSheet, collectionsRange)
          break
# end deleteCollection

async def createCollection(message, client):
  await message.channel.trigger_typing()

  workbook = await openCollectionsSpreadsheet()
  collectionsSheet = workbook.worksheet("Collections")
  collectionsRange = collectionsSheet.range("A2:C" + str(collectionsSheet.row_count))

  nosV1User, nosChannel, collectionMsg = await getNosChannel(client)

  # get message IDs
  sourceMessageIDS = message.content.split("create")[1].split(" ")

  # get collection name
  await message.channel.send("What would you like to name this collection?\n*Type the name below.*")

  def checkName(msg):
    return msg.author == message.author and message.channel == msg.channel

  def checkEditedName(payload):
    channelID = int(payload.data["channel_id"])
    authorID = int(payload.data["author"]["id"])
    return authorID == message.author.id and channelID == message.channel.id

  def checkEmoji(payload):
    messageID = payload.message_id
    userID = payload.user_id
    return userID == message.author.id and moBotMessage.id == messageID and (payload.emoji.name == "✅" or payload.emoji.name == "❌")

  msg = await client.wait_for('message', check=checkName)
  moBotMessage = await message.channel.send(content="Collection Name: '" + msg.content + "'")
  await moBotMessage.add_reaction("✅")
  await moBotMessage.add_reaction("❌")

  while (True):
    payload = await client.wait_for('raw_reaction_add', check=checkEmoji)
    await moBotMessage.remove_reaction(payload.emoji, client.get_user(payload.user_id))
    if (payload.emoji.name == "✅"):
      updated = False
      for i in range(0, len(collectionsRange), 3):
        if (collectionsRange[i].value == ""):
          updated = True
          collectionsRange[i].value = str(message.guild.id)
          collectionsRange[i+1].value = str(collectionMsg.id)
          collectionsRange[i+2].value = msg.content
          break

        elif (int(collectionsRange[i].value) == message.guild.id and collectionsRange[i+2].value.lower() == msg.content.lower()):
          await moBotMessage.edit(content="**Collection Already Exists**\n\nWould you like to replace it? *This action cannot be undone.*")
          payload = await client.wait_for('raw_reaction_add', check=checkEmoji)
          await moBotMessage.remove_reaction(payload.emoji, client.get_user(payload.user_id))

          if (payload.emoji.name == "✅"):
            await message.channel.trigger_typing()
            await deleteCollectionFromNOS(message, int(collectionsRange[i+1].value), client)
            collectionsRange = await deleteCollectionFromSpreadsheet(message, int(collectionsRange[i+1].value), collectionsSheet, collectionsRange)
            await message.channel.send("Old Collection Deleted")

            updated = True
            collectionsRange[i].value = str(message.guild.id)
            collectionsRange[i+1].value = str(collectionMsg.id)
            collectionsRange[i+2].value = msg.content

            break
          elif (payload.emoji.name == "❌"):
            await moBotMessage.edit(content="Edit your message above to set the name of your collection.")
            payload = await client.wait_for('raw_message_edit', check=checkEditedName)
            await moBotMessage.edit(content="Collection Name: '" + msg.content + "'")
          break

      if (updated):
        await message.channel.trigger_typing()
        await moBotMessage.clear_reactions()
        break
        
    elif (payload.emoji.name == "❌"):
      await moBotMessage.edit(content="Edit your message above to set the name of your collection.")
      payload = await client.wait_for('raw_message_edit', check=checkEditedName)
      await moBotMessage.edit(content="Collection Name: '" + msg.content + "'")

  collectionName = msg.content
  collectionMsgIDs = ""

  # update collection message  
  embeds = []
  for sourceMessageID in sourceMessageIDS:
    if (sourceMessageID != ""):
      msg = await message.channel.fetch_message(int(sourceMessageID.strip()))
      try:
        embed = msg.embeds[0]
        embed = embed.to_dict()
        author = embed["author"]["name"] # tryna trigger the key error
        embed = discord.Embed().from_dict(embed)
        embeds.append(embed)
      except IndexError:
        await message.channel.send("**Canceling Collection Creation Request**\n\nAt least one message does not contain an embed:\nhttps://discordapp.com/channels/" + str(message.guild.id) + "/" + str(message.channel.id) + "/" + str(msg.id))
        await collectionMsg.delete()
        return
      except KeyError:
        await message.channel.send("**Canceling Collection Creation Request**\n\nAt least one message does not contain an embed with an *Author Line*:\nhttps://discordapp.com/channels/" + str(message.guild.id) + "/" + str(message.channel.id) + "/" + str(msg.id) + "\n\nTo include an author line in an embed, use\n`@MoBot#0697 edit embed [Message_ID]\n!!Insert_Text_Here!!`")
        await collectionMsg.delete()
        return

  for embed in embeds:
    msg = await nosV1User.send(embed=embed)
    collectionMsgIDs += str(msg.id) + ","
  collectionMsgIDs = collectionMsgIDs[:-1]

  await collectionMsg.edit(content=collectionMsg.content + " " + collectionMsgIDs)

  collectionsSheet.update_cells(collectionsRange, value_input_option="USER_ENTERED")
  
  # update author urls
  collectionMsgIDs = collectionMsgIDs.split(",")
  for i in range(len(collectionMsgIDs)):
    msg = await nosChannel.fetch_message(int(collectionMsgIDs[i]))
    embed = msg.embeds[0].to_dict()
    embed["author"]["url"] = "https://google.com/MoBotCollection"
    embed["author"]["url"] += "/collection=" + str(collectionMsg.id)
    embed["author"]["url"] += "/id=" + str(msg.id)

    if (len(collectionMsgIDs) == 1):
      embed["author"]["url"] += "/left=" + str(msg.id) + "/right=" + str(msg.id)
    else:
      prevMsg = await nosChannel.fetch_message(int(collectionMsgIDs[i-1]))
      try:
        nextMsg = await nosChannel.fetch_message(int(collectionMsgIDs[i+1]))
      except IndexError:
        nextMsg = await nosChannel.fetch_message(int(collectionMsgIDs[0]))
      embed["author"]["url"] += "/left=" + str(prevMsg.id) + "/right=" + str(nextMsg.id)

    embed = discord.Embed.from_dict(embed)
    await msg.edit(embed=embed)

  await message.channel.send("**Collection Created**\n\nTo display this collection, use `@MoBot#0697 collection display " + collectionName + "`")
# end createCollection

async def correctMoBotHelpMenu(message, embed):
  embed = embed.to_dict()
  if (embed["author"]["name"] == "MoBot's Command Help Menu"):
    embed["author"]["icon_url"] = "https://cdn.discordapp.com/attachments/547274914319826944/603345955684614145/MoBot_Logo_-_Friday_Black_Metallic.png"
    embed["color"] = int("0xd1d1d1", 16)

  return discord.Embed.from_dict(embed)
# end checkMoBotHelpMenu

async def getNosChannel(client):
  nosV1User = client.get_user(nosV1ID)
  collectionMsg = await nosV1User.send("Collection:")
  return nosV1User, collectionMsg.channel, collectionMsg
# end getNosChannel

async def openCollectionsSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("18IkL0Hgm8CjwXaS0BUUPNUSJPbKROrfiSpFehEgD-wE")
  return workbook
# end openCollectionsSpreadsheet