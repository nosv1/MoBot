import discord
import asyncio
from datetime import datetime
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

import Collections

moBot = "449247895858970624"
spaceChar = "⠀"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (args[1] == "reservations"):
    pass
  elif (args[2] == "create"):
    await createReservation(message, client)
  elif (args[2] == "display"):
    await Collections.displayCollection(message, False, message.content.split("display")[1].strip(), message.guild.id, True, client)
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  if (payload.emoji.name == "✅" or payload.emoji.name == "❌"):
    await addRemoveNameToList(message, payload, client)
    
    # COTM STUFF
    pmSignupMessage = 605985769718284299 # pit marshall signup embed
    pmRole = 527220681859923980 # pit marshall role
    pmSignupLog = message.guild.get_channel(605985616605347850) # pit marshall signup log
    if (message.id == pmSignupMessage): 
      user = message.guild.get_member(payload.user_id)
      roles = message.guild.roles
      for role in roles:
        if (role.id == pmRole): 
          if (payload.emoji.name == "✅"):
            await user.add_roles(role)
            await pmSignupLog.send("<@" + str(user.id) + ">, has signed-up for " + message.embeds[0].footer.text + ".")
          elif (payload.emoji.name == "❌"):
            await user.remove_roles(role)
            await pmSignupLog.send("<@" + str(user.id) + ">, has un-signed-up for " + message.embeds[0].footer.text + ".")
          break
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def addRemoveNameToList(message, payload, client):
  embed = message.embeds[0]
  embed = embed.to_dict()
  emojis = embed["author"]["url"].split("emojis=")[1].split("/")[0].strip()

  member = message.guild.get_member(payload.user_id)
  addRemove = "add" if (payload.emoji.name == "✅") else "remove"
  reactions = message.reactions
  for reaction in reactions:
    if (str(reaction.emoji) in emojis):
      async for user in reaction.users():
        if (user.id == member.id):
          #await message.clear_reactions()
          for i in range(len(embed["fields"])):
            fieldName = embed["fields"][i]["name"]
            if (str(reaction.emoji) in fieldName):
              fieldValue = embed["fields"][i]["value"]
              lines = fieldValue.split("\n")
              newValue = ""
              for line in lines:
                if (addRemove == "add"):
                  if (line == spaceChar):
                    line = spaceChar + "- " + "" + member.mention + "\n"
                    newValue += line
                  elif (str(member.id) not in line):
                    newValue += line + "\n"
                elif (addRemove == "remove"):
                  if (str(member.id) in line or line == spaceChar):
                    continue
                  else:
                    newValue += line + "\n"
              newValue += spaceChar
              embed["fields"][i]["value"] = newValue
              break
          break

  await message.clear_reactions()
  embed = discord.Embed.from_dict(embed)
  await message.edit(embed=embed)

  for r in ["💾", "⬅", "➡"]:
    await message.add_reaction(r)
  for emoji in emojis.split(","):
    await message.add_reaction(emoji)
  for r in ["✅", "❌", "🗑"]:
    await message.add_reaction(r)
# end addRemoveNameToList

async def createReservation(message, client):
  nosUser, nosChannel, nosMessage = await Collections.getNosChannel(client)
  
  def specifierCheck(msg):
    return msg.channel == message.channel and msg.author == message.author

  await message.channel.send("**What would you like to name this 'reservation list'?**\nThis name will appear at the top of your embed(s).")

  looped = False
  while True:
    try:
      reservationNameMsg = await client.wait_for("message", timeout=10*60, check=specifierCheck)
    except asyncio.TimeoutError:
      await message.channel.send("**Reservation Creation Canceled**")
      await nosMessage.delete()
      return

    reservationName = reservationNameMsg.content.strip()

    def nameEditCheck(payload):
      return payload.message_id == reservationNameMsg.id

    reply = "Reservation Name: " + reservationName
    if (not looped):
      msg = await message.channel.send(reply)
    else:
      await msg.edit(content=reply)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def confirmCheck(payload):
      return payload.user_id == message.author.id and payload.message_id == msg.id and (payload.emoji.name == "✅" or payload.emoji.name == "❌")
          
    try:
      payload = await client.wait_for("raw_reaction_add", timeout=60, check=confirmCheck)
      await msg.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))

    except asyncio.TimeoutError:
      await message.channel.send("**Reservation Creation Canceled**")
      await msg.clear_reactions()
      await nosMessage.delete()
      return

    if (payload.emoji.name == "✅"):
      await msg.clear_reactions()
      break
    elif (payload.emoji.name == "❌"):
      await msg.edit(content="Edit your message above naming this reservation.")
      await msg.clear_reactions()

      try:
        payload = await client.wait_for("raw_message_edit", timeout=10*60, check=nameEditCheck)

      except asyncio.TimeoutError:
        await message.channel.send("**Reservation Creation Canceled**")
        await nosMessage.delete()
        return

      looped = True

  await message.channel.send("**What are the page specifiers?**\n\nType them below seperating each specifier with a comma.")

  pageSpecifiers = []
  pageSubSpecifiers = []
  looped = False
  while True:
    if (not looped):
      try:
        pageSpecifiersMsg = await client.wait_for("message", timeout=10*60, check=specifierCheck)
      except asyncio.TimeoutError:
        await message.channel.send("**Reservation Creation Canceled**")
        await nosMessage.delete()
        return
    pageSpecifiers = pageSpecifiersMsg.content.split(",")

    def specifierEditCheck(payload):
      return payload.message_id == pageSpecifiersMsg.id

    reply = "Page Specifier(s):\n"
    for i in range(len(pageSpecifiers)):
      pageSpecifiers[i] = pageSpecifiers[i].strip()
      reply += "  - " + pageSpecifiers[i] + "\n"
    reply += "\n**Are these correct?**"

    if (not looped):
      msg = await message.channel.send(reply)
    else:
      await msg.edit(content=reply)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    try:
      payload = await client.wait_for("raw_reaction_add", timeout=60, check=confirmCheck)
      await msg.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))

    except asyncio.TimeoutError:
      await message.channel.send("**Reservation Creation Canceled**")
      await msg.clear_reactions()
      await nosMessage.delete()
      return

    if (payload.emoji.name == "✅"):
      pageSubSpecifiers = []
      for pageSpecifier in pageSpecifiers:
        await msg.clear_reactions()
        await msg.edit(content="**What are the page sub-specifiers for '" + pageSpecifier + "'?\nInclude the emojis the user will click to add their name to the list.**\n\nType specifiers and the emojis that go with them below, seperating each specifier with a comma. If there are none, still include an emoji, but type \"None\" for the specifier.\n\nExample: 1⃣ Specifier One, 2⃣ Specifier Two\n*Make sure there's a space in between the emoji and the specifier.*")

        looped = False
        while True:
          if (not looped):
            try:
              pageSubSpecifiersMsg = await client.wait_for("message", timeout=10*60, check=specifierCheck)
            except asyncio.TimeoutError:
              await message.channel.send("**Reservation Creation Canceled**")
              await nosMessage.delete()
              return
          pageSubSpecifiersTemp = pageSubSpecifiersMsg.content.split(",")

          def subSpecifierEditCheck(payload):
            return payload.message_id == pageSubSpecifiersMsg.id

          reply = "Page Sub-specifier(s):\n"
          for i in range(len(pageSubSpecifiersTemp)):
            pageSubSpecifiersTemp[i] = pageSubSpecifiersTemp[i].strip()
            reply += "  - " + pageSubSpecifiersTemp[i] + "\n"
          reply += "\n**Are these correct?**"

          if (not looped):
            msg = await message.channel.send(reply)
          else:
            await msg.edit(content=reply)
          await msg.add_reaction("✅")
          await msg.add_reaction("❌")
                
          try:
            payload = await client.wait_for("raw_reaction_add", timeout=60, check=confirmCheck)
            await msg.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))

          except asyncio.TimeoutError:
            await message.channel.send("**Reservation Creation Canceled**")
            await msg.clear_reactions()
            await nosMessage.delete()
            return

          if (payload.emoji.name == "✅"):
            pageSubSpecifiers.append(pageSubSpecifiersTemp)
            
            await msg.clear_reactions()
            break
          elif (payload.emoji.name == "❌"):
            await msg.edit(content="Edit your message above listing your page sub-specifiers and seperating each specifier with a comma.")
            await msg.clear_reactions()

            try:
              payload = await client.wait_for("raw_message_edit", timeout=10*60, check=subSpecifierEditCheck)

            except asyncio.TimeoutError:
              await message.channel.send("**Reservation Creation Canceled**")
              await nosMessage.delete()
              return

            looped = True

      await msg.clear_reactions()
      break

    elif (payload.emoji.name == "❌"):
      await msg.edit(content="Edit your message above listing your page specifiers and seperating each specifier with a comma.")
      await msg.clear_reactions()

      try:
        payload = await client.wait_for("raw_message_edit", timeout=10*60, check=specifierEditCheck)

      except asyncio.TimeoutError:
        await message.channel.send("**Reservation Creation Canceled**")
        await nosMessage.delete()
        return

      looped = True

  # create embeds
  embeds = []
  subSpecifiers = []
  emojis = []
  for i in range(len(pageSpecifiers)):
    embed = discord.Embed(color=int("0xd1d1d1", 16))
    embed.set_author(name=reservationName + "\n" + pageSpecifiers[i] + "\n" + spaceChar)
    embed.set_footer(text=pageSpecifiers[i])
    
    tSubSpecifiers = []
    tEmojis = []
    for j in range(len(pageSubSpecifiers[i])):
      if ("<" == pageSubSpecifiers[i][j][0]):
        pageSubSpecifierEmoji = pageSubSpecifiers[i][j].split(">")[0] + ">"
        pageSubSpecifier = pageSubSpecifiers[i][j].split(">")[1].strip()
      else:
        pageSubSpecifierEmoji = pageSubSpecifiers[i][j][:2]
        pageSubSpecifier = pageSubSpecifiers[i][j][2:].strip()
      if ("None" in pageSubSpecifiers[i][j]):
        pageSubSpecifier = spaceChar

      tSubSpecifiers.append(pageSubSpecifier)
      tEmojis.append(pageSubSpecifierEmoji)

      embed.add_field(name=pageSubSpecifier + " - " + pageSubSpecifierEmoji, value=spaceChar, inline=False) 
  
    embed.add_field(name="*How To Add/Remove Your Name:*", value="*Click the corresponding emoji, then either click the ✅ or the ❌.*", inline=False)

    subSpecifiers.append(tSubSpecifiers)
    emojis.append(tEmojis)

    embeds.append(embed)

  collectionMsgIDs = ""
  for embed in embeds:
    msg = await nosUser.send(embed=embed)
    collectionMsgIDs += str(msg.id) + ","
  collectionMsgIDs = collectionMsgIDs[:-1]

  await nosMessage.edit(content=nosMessage.content + " " + collectionMsgIDs)

  # update spreadsheet
  workbook = await openReservationsSpreadsheet()
  reservationsSheet = workbook.worksheet("Reservations")
  reservationsRange = reservationsSheet.range("A2:C" + str(reservationsSheet.row_count))

  duplicateCount = 0
  for i in range(len(reservationsRange)):
    if (reservationsRange[i].value == ""):
      reservationsRange[i].value = str(message.guild.id)
      reservationsRange[i+1].value = str(nosMessage.id)
      reservationsRange[i+2].value = reservationName
      break
    elif (reservationsRange[i].value.lower() == reservationName.lower().split("(" + str(duplicateCount) + ")")[0]):
      duplicateCount += 1
      reservationName += "(" + str(duplicateCount) + ")"

  reservationsSheet.update_cells(reservationsRange, value_input_option="USER_ENTERED")

  # update urls
  collectionMsgIDs = collectionMsgIDs.split(",")
  for i in range(len(collectionMsgIDs)):
    msg = await nosChannel.fetch_message(int(collectionMsgIDs[i]))
    embed = msg.embeds[0].to_dict()
    embed["author"]["url"] = "https://google.com/MoBotReservation"
    embed["author"]["url"] += "/collection=" + str(nosMessage.id)
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

    embed["author"]["url"] += "/creator=" + str(message.author.id)

    tEmojis = "/emojis="
    tSubSpecifiers = "/sub_specifiers="
    for j in range(len(subSpecifiers[i])):
      tEmojis += emojis[i][j] + ","
      tSubSpecifiers += subSpecifiers[i][j] + ","
    embed["author"]["url"] += tEmojis[:-1].strip()
    embed["author"]["url"] += tSubSpecifiers[:-1].strip().replace(" ", "_")
    embed["author"]["url"] = embed["author"]["url"].replace(" ", "")
    embed["author"]["url"] = embed["author"]["url"].replace("\n", "")
    print(embed["author"]["url"])

    embed = discord.Embed.from_dict(embed)
    await msg.edit(embed=embed)

  await message.channel.send("**Reservation Created**\n\nTo display the embed, use `@MoBot#0697 reservation display " + reservationName + "`.")
# end createReservation

async def openReservationsSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1VVq791ALcZ6QIrwaxIv8Eb8GCJKntq7YDhmPbWlMueA")
  return workbook
# end openCollectionsSpreadsheet