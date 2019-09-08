import discord
import asyncio
from datetime import datetime
import random
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import traceback

import SecretStuff

moBot = "449247895858970624"
emojis = ["2⃣", "4⃣", "6⃣", "8⃣", "✅", "❌", "⚪", "🔴", "🔷", "🔶"]
numbers = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣"]
spaceChar = "ᅠ"
nosV1ID = 475325629688971274

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  await message.channel.trigger_typing()

  success = False
  if (args[2] == "createlobby"):
    success = await createLobby(message)
  elif (args[2] == "leaderboard"):
    success = await displayLeaderboard(message, None, None, client)
    await message.delete()
  elif (args[2] == "rank"):
    if (len(args) == 4):
      success = await getRanks(message, args[3], None, True)
    elif (len(args) == 5):
      success= await getRanks(message, args[3], args[4][-19:-1], True)

  if (not success):
    msg = await message.channel.send("Command Not Found\n\nAvailable Scrims Commands:\n  `@MoBot#0697 scrims createlobby`\n  `@MoBot#0697 scrims leaderboard`\n  `@MoBot#0697 scrims rank @User`\n*For more help, use `@MoBot help` -> Specific Use -> RLScrims*")
    await asyncio.sleep(60)
    await msg.delete()
    await message.delete()
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client, member): 
  embed = message.embeds[0].to_dict()

  if ("MoBot - RLScrims" in embed["author"]["name"]):

    if ("Leaderboard" in embed["author"]["name"]):
  
      lType = embed["author"]["name"].split("|")[1].strip()[0].lower()
      mType = embed["author"]["name"].split("|")[0].split("\n")[1].strip()[0]

      if (payload.emoji.name == "⬅"):
        messageID = int(embed["author"]["url"].split("left=")[1].split("/")[0])
        await goToMessage(message, messageID, client)
      elif (payload.emoji.name == "➡"):
        messageID = int(embed["author"]["url"].split("right=")[1].split("/")[0])
        await goToMessage(message, messageID, client)

      elif (payload.emoji.name == "🌐"):
        messageID = int(embed["author"]["url"].split("g" + mType + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)
      elif (payload.emoji.name == "🏠"):
        messageID = int(embed["author"]["url"].split("l" + mType + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)

      elif (payload.emoji.name == "1⃣"):
        messageID = int(embed["author"]["url"].split(lType + "1" + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)
      elif (payload.emoji.name == "2⃣"):
        messageID = int(embed["author"]["url"].split(lType + "2" + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)
      elif (payload.emoji.name == "3⃣"):
        messageID = int(embed["author"]["url"].split(lType + "3" + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)
      elif (payload.emoji.name == "4⃣"):
        messageID = int(embed["author"]["url"].split(lType + "4" + "=")[1].split("/")[0])
        await goToMessage(message, messageID, client)

      elif (payload.emoji.name == "🔄"):
        msg = await message.channel.send("Updating Leaderboards... It'll be a second.")
        ids = embed["author"]["url"].split("=")
        await deleteLeaderboardEmbeds(ids, client)

        await displayLeaderboard(message, embed["author"]["name"].split("|")[1].strip().lower(), embed["author"]["name"].split("|")[0].split("\n")[1].strip()[:-1], isRefresh, client)

        await msg.edit(content="Leaderboards updated :thumbsup:")
        await asyncio.sleep(3)
        await msg.delete()

      elif (payload.emoji.name == "❌"):
        member = message.guild.get_member(payload.user_id)
        memberPerms = message.channel.permissions_for(member)
        if (memberPerms.send_messages):
          await message.delete()
          ids = embed["author"]["url"].split("=")
          await deleteLeaderboardEmbeds(ids, client)
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

    elif ("RLScrims Rank" in embed["author"]["name"]):
      if (payload.emoji.name == "❌"):
        if (str(member.id) in embed["author"]["url"]):
          await message.delete()
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
          
    else:
      host = embed["fields"][0]["value"].split(">")[0]
      host = int(host.split("@")[1]) if ("!" not in host) else int(host.split("!")[1])
      host = message.guild.get_member(host)

      if (host.id == member.id):
        if (payload.emoji.name == "✅"):
          if (embed["fields"][-1]["name"] == "Lobby Size"):
            await setMaxPlayers(message, host, embed)
          elif ("Player Pool" in embed["fields"][-1]["name"]):
            if (embed["fields"][-1]["value"].count("@") % 2 == 0):
              await pickCaptains(message, host, embed)
            else:
              await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
              msg = await message.channel.send("" + member.mention + ", you cannot start a match with an odd number of players.")
              await asyncio.sleep(5)
              await msg.delete()
        elif (payload.emoji.name == "❌"):
          await message.delete()
      
      if ("Player Pool" in embed["fields"][-1]["name"]):
        if (payload.emoji.name == "⚪"):
          await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
          await playerJoin(message, host, member, embed)
        elif (payload.emoji.name == "🔴"):
          await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
          await playerLeave(message, member, embed)
      elif ("Available Players" in embed["fields"][-1]["name"]):
        captain = message.content.split(">")[0]
        captain = int(captain.split("@")[1]) if ("!" not in captain) else int(captain.split("!")[1])
        captain = message.guild.get_member(captain)

        if (member.id == captain.id):
          if (payload.emoji.name == "✅"):
            await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
            await pickPlayer(message, host, captain, embed)
        else:
          await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      elif ("Match Result" in embed["fields"][-1]["name"]):
        mc = message.content
        c1 = mc.split("and")[0].strip()
        c2 = mc.split("and")[1].split(",")[0].strip()

        if (str(member.id) in c1 or str(member.id) in c2):
          if (payload.emoji.name == "✅"):
            blueCount = 0
            orangeCount = 0
            for reaction in message.reactions:
              if (reaction.emoji == "🔷"):
                blueCount = len(await reaction.users().flatten())
              if (reaction.emoji == "🔶"):
                orangeCount = len(await reaction.users().flatten())
              elif (reaction.emoji == payload.emoji.name):
                users = await reaction.users().flatten()
                if (len(users) == 3 and (blueCount == 3 or orangeCount == 3)):
                  await confirmMatchResult(message, "🔷" if blueCount >= orangeCount else "🔶", host, embed, c1, c2)
          elif (payload.emoji.name != "🔷" and payload.emoji.name != "🔶"):
            await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

        else:
          await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
      elif ("Next Match" in embed["fields"][-1]["name"]):
        pass

      elif ("Lobby Size" not in embed["fields"][-1]["name"]):
        await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def createLobby(message):
  embed = discord.Embed(colour=0xd1d1d1)
  embed.add_field(name="Lobby Creator", value="<@" + str(message.author.id) + ">\n" + spaceChar, inline=False)
  embed.add_field(name="Lobby Size", value="What is the max number of players?", inline=False)
  embed.set_footer(text="Select a number, and then click the ✅.")

  lobbyName = "Lobby Name: " + message.content.strip().split("createlobby")[-1]
  author = "MoBot - RLScrims\n"
  if (lobbyName[-1] != " "):
    author += lobbyName
  else:
    author += "Lobby Name: "
    for word in message.guild.name.split(" "):
      author += word[0]
    author += " Scrim"

  embed.set_author(name=author)

  msg = await message.channel.send(embed=embed)
  for emoji in emojis:
    if (emoji != "⚪"):
      await msg.add_reaction(emoji)
    else:
      break
  
  await message.delete()
  return True
# end createLobby

async def setMaxPlayers(message, host, embed):
  sizeFound = False
  for reaction in message.reactions:
    users = reaction.users()
    async for user in users:
      if (user.id == host.id and reaction.emoji != "✅"):
        sizeFound = True
        lobbySize = (emojis.index(reaction.emoji) + 1) * 2
        embed["fields"][1]["value"] = str(lobbySize)
        await message.clear_reactions()
        break

  if (not sizeFound):
    msg = await message.channel.send("<@" + str(host.id) + ">, you need to click a number before clicking ✅.")
    await asyncio.sleep(5)
    await msg.delete()
  else:
    embed["fields"][-1]["value"] += "\n" + spaceChar

    name = embed["author"]["name"].split(":")[1].strip()
    password = await generateRandomString(4)
    
    embed = discord.Embed.from_dict(embed)

    embed.add_field(name="Lobby Details", value="Host: TBD\nName: `" + name + "`\nPassword: `" + password + "`\n" + spaceChar, inline=False)
    embed.add_field(name="Player Pool", value="No players have joined yet.")
    embed.set_footer(text="Click the ⚪ to join and the 🔴 to leave. -- " + str(host.display_name) + ", click the ✅ to continue to team assignment, or click the ❌ to destroy the lobby.")
    await message.edit(embed=embed)
    await message.add_reaction("⚪")
    await message.add_reaction("🔴")
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# end setMaxPlayers

async def playerJoin(message, host, member, embed):
  lobbySize = int(embed["fields"][-3]["value"].split("\n")[0].strip())

  playerPool = embed["fields"][-1]["value"] + "\n"
  if ("@" not in playerPool): # if no players have joined yet
    playerPool = "" + member.mention + "\n"
    embed["fields"][-1]["value"] = playerPool
  elif (str(member.id) not in playerPool):
    players = playerPool.split("\n")
    del players[-1]
    playerPool = ""
    for player in players:
      playerPool += player + "\n"
    playerPool += "" + member.mention + "\n"
    embed["fields"][-1]["value"] = playerPool

  if (len(playerPool.split("\n")) - 1 == lobbySize):
    await pickCaptains(message, host, embed)
  else:
    embed["fields"][-1]["name"] = "Player Pool - " + str(len(playerPool.split("\n"))-1)
    embed = discord.Embed.from_dict(embed)
    await message.edit(embed=embed)
# end playerJoin

async def playerLeave(message, member, embed):
  playerPool = embed["fields"][-1]["value"] + "\n"
  if (str(member.id) in playerPool):
    players = playerPool.split("\n")
    del players[-1]

    for player in players:
      if (str(member.id) in player):
        del players[players.index(player)]
        break

    playerPool = ""
    for player in players:
      playerPool += player + "\n"

    embed["fields"][-1]["name"] = "Player Pool - " + str(len(playerPool.split("\n"))-1)
    embed["fields"][-1]["value"] = playerPool
    embed = discord.Embed.from_dict(embed)
    try:
      await message.edit(embed=embed)
    except discord.errors.HTTPException:
      embed = embed.to_dict()
      embed["fields"][-1]["name"] = "Player Pool"
      embed["fields"][-1]["value"] = "No players have joined yet."
      embed = discord.Embed.from_dict(embed)
      await message.edit(embed=embed)
# end playerLeave

async def pickCaptains(message, host, embed):
  await message.clear_reactions()

  players = embed["fields"][-1]["value"].split("\n")
  if (players[-1] == ""):
    del players[-1]

  c1, c2 = await getRandomCaptains(players)

  teamSize = str(int(len(players) / 2))
  embed["fields"][-3]["name"] = "Match Type"
  matchType = teamSize + "v" + teamSize + "\n" + spaceChar

  embed["fields"][-3]["value"] = matchType

  del players[players.index(c1)]
  del players[players.index(c2)]
  
  workbook = await openSpreadsheet()
  c1Ranks = await getRanks(message, c1, message.channel.id, workbook)
  c2Ranks = await getRanks(message, c2, message.channel.id, workbook)

  try:
    c1 = c1 + " - " + c1Ranks[matchType.split("\n")[0]][0] + " (" + c1Ranks[matchType.split("\n")[0]][1] + ")"
  except TypeError:
    c1 = c1 + " - 0 (Theta)"
  try:
    c2 = c2 + " - " + c2Ranks[matchType.split("\n")[0]][0] + " (" + c2Ranks[matchType.split("\n")[0]][1] + ")"
  except TypeError:
    c2 = c2 + " - 0 (Theta)"

  embed["fields"][-1]["name"] = "Teams"
  embed["fields"][-1]["value"] = "🔷 Blue:\n" + spaceChar + c1 + "\n🔶 Orange:\n" + spaceChar + c2 + "\n" + spaceChar

  embed = discord.Embed.from_dict(embed)

  remPlayers = ""
  for i in range(len(players)):
    player = players[i]
    playerRanks = await getRanks(message, player, message.channel.id, workbook)
    try:
      player = player + " - " + playerRanks[matchType.split("\n")[0]][0] + " (" + playerRanks[matchType.split("\n")[0]][1] + ")"
    except TypeError:
      player = player + " - 0 (Theta)"
    remPlayers += numbers[i] + " - " + player + "\n"
  if (remPlayers != ""):
    content = c1 + ", pick 1 player for your team.\nClick the ✅ to confirm your pick."
    embed.add_field(name="Available Players - " + str(len(players)), value=remPlayers, inline=False)
    embed.set_footer(text=str(host.display_name) + ", click the ❌ to destroy the lobby.")
    await message.edit(content=content, embed=embed)

    for i in range(len(players)):
      await message.add_reaction(numbers[i])
    
    await message.add_reaction("✅")
    await message.add_reaction("❌")
  else:
    await awaitMatchResult(message, host, embed)
# end pickCaptains

async def pickPlayer(message, host, captain, embed):
  picksLeft = int(message.content.split("pick ")[1].split(" ")[0])
  picks = []
  for reaction in message.reactions:
    users = reaction.users()
    async for user in users:
      if (user.id == captain.id and reaction.emoji in numbers):
        picks.append(reaction.emoji)
        picksLeft -= 1
        await message.remove_reaction(reaction, user)
        await message.remove_reaction(reaction, message.guild.get_member(int(moBot)))
        break
    if (picksLeft == 0):
      break

  if (len(picks) != 0):
    players = (embed["fields"][-1]["value"] + "\n").split("\n")
    del players[-1]

    for pick in picks:
      for player in players:
        if (pick in player):
          picks[picks.index(pick)] = "<" + player.split("<")[1].strip()
          del players[players.index(player)]
          break

    teams = embed["fields"][-2]["value"].split(":")
    captains = [teams[1].split(">")[0][2:].strip(), teams[2].split(">")[0][2:].strip()]

    matchIsReady = False
    if (picksLeft > 0):
      content = message.content.replace(" 2 ", " 1 ")
    elif (len(players) > 0):
      nextPick = captains[0] if (captains[1] in message.content) else captains[1]
      if (len(players) > 1):
        content = nextPick + ">, pick 2 players for your team.\nClick the ✅ to confirm your picks."
      else:
        content = nextPick + ">, pick 1 player for your team.\nClick the ✅ to confirm your pick."
    else:
      content = ""
      await message.clear_reactions()
      matchIsReady = True

    if (len(picks) > 0):
      team1 = teams[1].split("🔶")[0].strip()
      team2 = teams[2][:-1].strip()

      for pick in picks:
        if (captains[1] in message.content):
          team2 += "\n" + spaceChar + pick
        else:
          team1 += "\n" + spaceChar + pick

      team2 += "\n" + spaceChar
      team1 += "\n"
    embed["fields"][-2]["value"] = "🔷 Blue:\n" + team1 + "🔶 Orange:\n" + team2

    remPlayers = ""
    for player in players:
      remPlayers += player + "\n"
    if (remPlayers != ""):
      embed["fields"][-1]["name"] = "Available Players - " + str(len(players))
      embed["fields"][-1]["value"] = remPlayers

      embed = discord.Embed.from_dict(embed)
    else:
      index = len(embed["fields"]) - 1
      embed = discord.Embed.from_dict(embed)
      embed.remove_field(index)

    if (matchIsReady):
      await awaitMatchResult(message, host, embed)
    else:
      embed.set_footer(text=str(host.display_name) + ", click the ❌ to destroy the lobby.")
      await message.edit(content=content, embed=embed)

  else:
    msg = await message.channel.send("<@" + str(captain.id) + ">, click a player number, and then click the ✅ to confirm your pick.")
    await asyncio.sleep(5)
    await msg.delete()
# end pickPlayer

async def awaitMatchResult(message, host, embed):
  embed = embed.to_dict()

  c1 = "<" + embed["fields"][-1]["value"].split(":")[1].split("<")[1].split("-")[0].strip()
  c2 = "<" + embed["fields"][-1]["value"].split(":")[2].split("<")[1].split("-")[0].strip()
  
  if ("TBD" in embed["fields"][-2]["value"]):
    embed["fields"][-2]["value"] = "Host: " + c1 + "\n" + embed["fields"][-2]["value"].split("TBD\n")[1].strip()

  embed = discord.Embed.from_dict(embed)

  embed.add_field(name="Match Result", value="Awaiting Match Result", inline=False)
  content = c1 + " and " + c2 + ", when the match is over, click the winning team's button (🔷🔶), and click the ✅.\n\n*The match will not be closed until both captains report the same winner.*"

  embed.set_footer(text=str(host.display_name) + ", click the ❌ to destroy the lobby.")
  await message.edit(embed=embed, content=content)

  await message.add_reaction("🔷")
  await message.add_reaction("🔶")
  await message.add_reaction("✅")
  await message.add_reaction("❌")
# end matchIsReady

async def confirmMatchResult(message, winner, host, embed, c1, c2):
  await message.clear_reactions()

  teams = embed["fields"][-2]["value"].split(">")
  memberCount = 0

  blueTeam = embed["fields"][-2]["value"].split("Blue:")[1].split("Orange:")[0].strip().split(">")
  orangeTeam = embed["fields"][-2]["value"].split("Orange:")[1].strip().split(">")

  matchType = embed["fields"][1]["value"]
  embed = await updateRanks(winner, blueTeam, orangeTeam, str(message.channel.id), matchType, embed)

  content = ""
  for member in teams:
    try:
      content += "<" + member.split("<")[1].strip() + ">, "
      memberCount += 1
    except IndexError:
      pass

  queueTimer = 60 # defualt 60
  content += "the match result has been reported. If you would like to play again, click an option below.\n\n**The queue opens in " + str(queueTimer) + " seconds.**"

  embed["fields"][-1]["value"] = "Winner: " + winner + "\n" + spaceChar
  embed = discord.Embed.from_dict(embed)

  nextMatchValue = "🔁 - Rematch (All Players Must Click)\n"
  nextMatchValue += "🔀 - New Captains"
  embed.add_field(name="Next Match", value=nextMatchValue)
  
  await message.edit(embed=embed, content=content)
  await message.add_reaction("🔁")
  await message.add_reaction("🔀")
  await message.add_reaction("❌")

  await asyncio.sleep(int(queueTimer/2)) # 30
  await message.edit(content=message.content.replace(" " + str(queueTimer), " " + str(int(queueTimer/2))))
  await asyncio.sleep(int(queueTimer/3)-3) # 20
  await message.edit(content=message.content.replace(" " + str(int(queueTimer/2)), " " + str(int(queueTimer/3))))
  await asyncio.sleep(int(queueTimer/6)-3) # 10

  updatedMessage = await message.channel.fetch_message(message.id)

  rematchCount = 0
  newCaptainCount = 0
  for reaction in updatedMessage.reactions:
    users = reaction.users()
    async for user in users:
      if (str(user.id) in content):
        memberCount -= 1
        if (reaction.emoji == "🔁"):
          rematchCount += 1
        if (reaction.emoji == "🔀"):
          newCaptainCount += 1

  if (memberCount == 0 and newCaptainCount == 0):
    await rematch(message, embed, c1, c2, matchType)
  else:
    await newCaptains(await message.channel.fetch_message(message.id), host, embed)
# end confirmMatchResult

async def updateRanks(winner, blueTeam, orangeTeam, channelID, matchType, embed):
  matchTypeOffset = int(matchType[0]) - 1 + int(matchType[0])

  workbook = await openSpreadsheet()
  sheet = workbook.worksheet(channelID)
  ids = sheet.range("F3:F" + str(sheet.row_count))
  matchTypeRange = sheet.range(3, matchTypeOffset + 6, sheet.row_count, matchTypeOffset + 6)
  rankBreakDown = sheet.range("A3:D9")

  async def getNewMatchTypeValue(team):
    for i in range(len(ids)):
      if (ids[i].value == ""):
        ids[i].value = memberID
        matchTypeRange[i].value = 10 if (team == winner) else 0
        smrChange = 10 if (team == winner) else 0
        currentRank = "Theta"
        currentSmr = 0
        return smrChange, currentRank, currentSmr
      elif (memberID in ids[i].value):
        currentSmr = int(matchTypeRange[i].value) if (matchTypeRange[i].value != "") else 0
        smrChange = 0
        for j in range(0, len(rankBreakDown), 4):
          if (int(rankBreakDown[j].value) > currentSmr):
            smrChange = int(rankBreakDown[j-4+1].value) if (team == winner) else int(rankBreakDown[j-4+2].value)
            matchTypeRange[i].value = currentSmr + smrChange if (currentSmr >= abs(smrChange) or smrChange > 0) else 0
            currentRank = rankBreakDown[j-4+3].value
            break
          elif (j+4 == len(rankBreakDown)):
            smrChange = int(rankBreakDown[j+1].value) if (team == winner) else int(rankBreakDown[j+2].value)
            matchTypeRange[i].value = currentSmr + smrChange if (currentSmr >= abs(smrChange) or smrChange > 0) else 0
            currentRank = rankBreakDown[j+3].value
            break
        return smrChange, currentRank, currentSmr

  value = "🔷 Blue:\n"
  for member in blueTeam:
    if ("@" in member):
      memberID = member.split("@")[1] if ("!" not in member) else member.split("!")[1]
      smrChange, currentRank, currentSmr = await getNewMatchTypeValue("🔷")
      smrChange = "+" + str(smrChange) if (smrChange > 0) else "-" + str(smrChange * - 1)
      value += spaceChar + "<@" + memberID + "> - " + str(currentSmr) + " " + smrChange + " (" + currentRank + ")\n"

  value += "🔶 Orange:\n"
  for member in orangeTeam:
    if ("@" in member):
      memberID = member.split("@")[1] if ("!" not in member) else member.split("!")[1]
      smrChange, currentRank, currentSmr = await getNewMatchTypeValue("🔶")
      smrChange = "+" + str(smrChange) if (smrChange > 0) else "-" + str(smrChange * - 1)
      value += spaceChar + "<@" + memberID + "> - " + str(currentSmr) + " " + smrChange + " (" + currentRank + ")\n"
  value += spaceChar
  embed["fields"][-2]["value"] = value

  sheet.update_cells(ids, value_input_option="USER_ENTERED")
  sheet.update_cells(matchTypeRange, value_input_option="USER_ENTERED")

  return embed
# end updateRanks

async def rematch(message, embed, c1, c2, matchType):
  await message.clear_reactions()
  embed.remove_field(-1)

  embed = embed.to_dict()
  embed["fields"][-1]["value"] = "Awaiting Match Result"
  content = c1 + " and " + c2 + ", when the match is over, click the winning team's button (🔷🔶), and click the ✅.\n\n*The match will not be closed until both captains report the same winner.*"


  blueTeam = embed["fields"][-2]["value"].split("Blue:")[1].split("Orange:")[0].strip().split(">")
  orangeTeam = embed["fields"][-2]["value"].split("Orange:")[1].strip().split(">")

  workbook = await openSpreadsheet()
  value = "🔷 Blue:\n"
  for member in blueTeam:
    if ("@" in member):
      memberID = member.split("@")[1] if ("!" not in member) else member.split("!")[1]
      playerRanks = await getRanks(message, member, message.channel.id, workbook)
      value += member + "> - " + playerRanks[matchType.split("\n")[0]][0] + " (" + playerRanks[matchType.split("\n")[0]][1] + ")\n"

  value += "🔶 Orange:\n"
  for member in orangeTeam:
    if ("@" in member):
      memberID = member.split("@")[1] if ("!" not in member) else member.split("!")[1]
      playerRanks = await getRanks(message, member, message.channel.id, workbook)
      value += member + "> - " + playerRanks[matchType.split("\n")[0]][0] + " (" + playerRanks[matchType.split("\n")[0]][1] + ")\n"
  value += spaceChar

  embed["fields"][-2]["value"] = value
  embed = discord.Embed.from_dict(embed)
  await message.edit(content=content, embed=embed)

  await message.add_reaction("🔷")
  await message.add_reaction("🔶")
  await message.add_reaction("✅")
  await message.add_reaction("❌")
# end rematch

async def newCaptains(message, host, embed):

  players = []
  for reaction in message.reactions:
    users = reaction.users()
    async for user in users:
      player = "<@" + str(user.id) + ">"
      if (player not in players and not user.bot):
        players.append(player)

  embed.remove_field(-1) # next match
  embed.remove_field(-1) # match result
  embed.remove_field(-1) # match teams

  embed = embed.to_dict()
  lobbySize = embed["fields"][1]["value"].split("v")
  lobbySize = int(lobbySize[0]) + int(lobbySize[1].split("\n")[0])
  embed = discord.Embed.from_dict(embed)
  embed.set_field_at(index=1, name="Lobby Size", value=str(lobbySize) + "\n" + spaceChar, inline=False)

  playerPool = ""
  for player in players:
    playerPool += player + "\n"

  embed.add_field(name="Player Pool - " + str(len(players)), value=playerPool if (playerPool != "") else "No players have joined yet.", inline=False)

  embed.set_footer(text="Click the ⚪ to join and the 🔴 to leave. -- " + str(host.display_name) + ", click the ✅ to continue to team assignment, or click the ❌ to destroy the lobby.")

  await message.edit(embed=embed, content="")
  if (len(players) == lobbySize):
    await pickCaptains(message, host, embed.to_dict())
  else:
    await message.clear_reactions()
    await message.add_reaction("⚪")
    await message.add_reaction("🔴")
    await message.add_reaction("✅")
    await message.add_reaction("❌")
# end newCaptains

async def updateLobbySize(message, embed):
  pass
# end updateLobbySize

async def displayLeaderboard(message, refreshLtype, refreshMType, client):
  workbook = await openSpreadsheet()
  sheets = workbook.worksheets()

  channels = message.guild.channels

  serverSheets = []
  for sheet in sheets:
    if (sheet.title != "template"):
      for channel in channels:
        if (channel.id == int(sheet.title)):
          serverSheets.append(sheet)
          break

  leaderboards = {
    "global" : {
      "1v1" : [],
      "2v2" : [],
      "3v3" : [],
      "4v4" : [],
    },
    "local" : {
      "1v1" : [],
      "2v2" : [],
      "3v3" : [],
      "4v4" : [],
    }
  }

  for sheet in serverSheets:
    ids = sheet.range("F3:F" + str(sheet.row_count))
    ones = sheet.range("G3:H" + str(sheet.row_count))
    twos = sheet.range("I3:J" + str(sheet.row_count))
    threes = sheet.range("K3:L" + str(sheet.row_count))
    fours = sheet.range("M3:N" + str(sheet.row_count))

    for i in range(len(ids)):
      if (ids[i].value != ""):
        id = "<@" + str(ids[i].value) + ">"
        smrs = [ones[i*2].value, twos[i*2].value, threes[i*2].value, fours[i*2].value]
        ranks = [ones[i*2+1].value, twos[i*2+1].value, threes[i*2+1].value, fours[i*2+1].value]

        found = False
        for i in range(len(smrs)):
          player = [id, smrs[i], ranks[i]]

          if (player[1] != ""):
            player[1] = int(player[1])
          else:
            player[1] = 0
            player[2] = "Theta"

          mType = str(i+1) + "v" + str(i+1)
          for j in range(len(leaderboards["global"][mType])):
            if (leaderboards["global"][mType][j][0] == player[0]):
              found = True
              if (leaderboards["global"][mType][j][1] < player[1]):
                leaderboards["global"][mType][j] = player
              break

          if (not found):
            leaderboards["global"][mType].append(player)
          
          if (sheet.title == str(message.channel.id)):
            leaderboards["local"][mType].append(player)

      else:
        break

  for lType in leaderboards:
    for mType in leaderboards[lType]:
      leaderboards[lType][mType].sort(key=lambda x:x[1], reverse=True)

  embeds = {
    "global" : {
      "1v1" : [],
      "2v2" : [],
      "3v3" : [],
      "4v4" : [],
    },
    "local" : {
      "1v1" : [],
      "2v2" : [],
      "3v3" : [],
      "4v4" : [],
    }
  }

  leaderboardHeader = "MoBot - RLScrims Leaderboard\n"
  for lType in leaderboards:
    for i in range(1, 5):
      embed = []
      embed.append(discord.Embed(color=0xd1d1d1))  
      mType = str(i) + "v" + str(i)
      lName = leaderboardHeader + mType + "s | " + lType[0].upper() + lType[1:]
      embed[len(embed)-1].set_author(name=lName, url="https://google.com/" + str(message.author.id))
      embed[len(embed)-1].set_footer(text="| Numbers - Match Types | 🌐- Server | 🏠- Local Channel |")
      ranks = {
        "Alpha" : "750",
        "Beta" : "500",
        "Gamma" : "350",
        "Delta" : "200",
        "Epsilon" : "100",
        "Zeta" : "50",
        "Theta" : "0",
      }

      playersOnPage = 0
      playersInRank = 0
      currentRank = ""
      value = ""
      for player in leaderboards[lType][mType]:
        if (player[2] + " - " + ranks[player[2]] != currentRank.split("(cont.)")[0].strip()):
          if (currentRank != ""):
            if ("-" in value):
              embed[len(embed)-1].add_field(name=currentRank, value=value + spaceChar, inline=False)
            value = ""

          currentRank = player[2] + " - " + ranks[player[2]]
          playersInRank = 0

        value += spaceChar + str(player[1]) + " - " + player[0] + "\n"

        playersOnPage += 1
        playersInRank += 1

        if (playersOnPage >= 50):
          playersOnPage = 0
          playersInRank = 0

          embed.append(discord.Embed(color=0xd1d1d1))
          embed[len(embed)-1].set_author(name=lName + " (cont.)", url="https://google.com/" + str(message.author.id))
          embed[len(embed)-1].set_footer(text="| Numbers - Match Types | 🌐- Server | 🏠- Local Channel |")
        
        if (playersInRank >= 20):
          playersInRank = 0

          if ("-" in value):
            embed[len(embed)-1].add_field(name=currentRank, value=value + spaceChar, inline=False)
          currentRank = currentRank.split("(cont.)")[0].strip() + " (cont.)"
          value = ""
        
      if ("-" in value):
        embed[len(embed)-1].add_field(name=currentRank, value=value + spaceChar, inline=False)

      embeds[lType][mType] = embed

  messageIDs = {
    "global" : {
      "1v1" : "",
      "2v2" : "",
      "3v3" : "",
      "4v4" : "",
    },
    "local" : {
      "1v1" : "",
      "2v2" : "",
      "3v3" : "",
      "4v4" : "",
    }
  }

  await message.channel.trigger_typing()
  nosV1User = client.get_user(nosV1ID)
  for lType in embeds:
    for mType in embeds[lType]:
      for i in range(len(embeds[lType][mType])):
        try:
          embeds[lType][mType][i] = await nosV1User.send(embed=embeds[lType][mType][i])
          messageIDs[lType][mType] = str(embeds[lType][mType][i].id) if (messageIDs[lType][mType] == "") else messageIDs[lType][mType]
        except discord.errors.HTTPException:
          pass

      await message.channel.trigger_typing()
      for i in range(len(embeds[lType][mType])):
        try:
          embed = embeds[lType][mType][i].embeds[0]
          try:
            nextMsg = embeds[lType][mType][i+1]
          except IndexError:
            nextMsg = embeds[lType][mType][0]
          prevMsg = embeds[lType][mType][i-1]

          embed = embed.to_dict()
          embed["author"]["url"] += "/left=" + str(prevMsg.id) + "/right=" + str(nextMsg.id)
          embed = discord.Embed().from_dict(embed)

          await embeds[lType][mType][i].edit(embed=embed)
        except AttributeError:
          pass

  await message.channel.trigger_typing()
  for lType in embeds:
    for mType in embeds[lType]:
      for i in range(len(embeds[lType][mType])):
        embed = embeds[lType][mType][i].embeds[0]
        embed = embed.to_dict()
        for lType2 in messageIDs:
          for mType2 in messageIDs[lType2]:
            embed["author"]["url"] += "/" + lType2[0] + mType2[0] + "=" + messageIDs[lType2][mType2]
        embed = discord.Embed().from_dict(embed)

        await embeds[lType][mType][i].edit(embed=embed)
  
  if (refreshLtype == None):
    msg = await message.channel.send(embed=embeds["global"]["1v1"][0].embeds[0])
    await msg.add_reaction("⬅")
    await msg.add_reaction("➡")
    await msg.add_reaction("🌐")
    await msg.add_reaction("🏠")
    await msg.add_reaction("1⃣")
    await msg.add_reaction("2⃣")
    await msg.add_reaction("3⃣")
    await msg.add_reaction("4⃣")
    await msg.add_reaction("🔄")
    await msg.add_reaction("❌")
  else:
    await message.edit(embed=embeds[refreshLtype][refreshMType][0].embeds[0])

  return True
#end getLeaderboard

async def goToMessage(message, messageID, client):
  nosV1User = client.get_user(nosV1ID)
  newPage = await nosV1User.send(".")
  await newPage.delete()
  newPage = await newPage.channel.fetch_message(messageID)

  await message.edit(embed=newPage.embeds[0])
# end leaderboardLeftRight

async def deleteLeaderboardEmbeds(ids, client):
  nosV1User = client.get_user(nosV1ID)
  channel = await nosV1User.send(".")
  await channel.delete()
  channel = channel.channel

  for i in range(1, len(ids)):
    try:
      msg = await channel.fetch_message(int(ids[i].split("/")[0]))
      await msg.delete()
    except ValueError:
      pass
    except discord.errors.NotFound:
      pass
# end deleteLeaderboardEmbeds

async def getRanks(message, user, channel, fromCommand):
  if (fromCommand == True):
    workbook = await openSpreadsheet()
  else:
    workbook = fromCommand

  sheet = None

  try:
    if (channel != None):
      sheet = workbook.worksheet(str(channel))
    else:
      sheet = workbook.worksheet(str(message.channel.id))
  except gspread.exceptions.WorksheetNotFound:
    if (fromCommand == True):
      msg = await message.channel.send("The channel provided hasn't had any scrims played in it. If no channel was provided, then this channel hasn't had any scrims played in it either.\n\n*The RLScrims ranks and leaderboards are channel specific.*")
      await asyncio.sleep(60)
      await msg.delete()
      await message.delete()
      return True
    else:
      sheet = workbook.duplicate_sheet(source_sheet_id=1793179111, insert_sheet_index=1, new_sheet_name=str(channel))
  except gspread.exceptions.APIError:
    if (fromCommand == True):
      msg = await message.channel.send("Command not availabe right now, try again in a couple seconds...")
      await asyncio.sleep(10)
      await msg.delete()
      await message.delete()
      return True

  ranks = None
  if (sheet != None):
    r = sheet.range("F3:N" + str(sheet.row_count))

    for i in range(0, len(r), 9):
      if (r[i].value != ""):

        if (r[i].value in user):
          user = r[i].value
          ranks = {
            "1v1" : [r[i+1].value, r[i+2].value],
            "2v2" : [r[i+3].value, r[i+4].value],
            "3v3" : [r[i+5].value, r[i+6].value],
            "4v4" : [r[i+7].value, r[i+8].value],
          }
          break
      else:
        user = ""
        break

    if (fromCommand == True):
      try:
        user = message.guild.get_member(int(user))
          
        embed = discord.Embed(colour=0xd1d1d1)
        embed.set_author(name= "MoBot - RLScrims Rank\n" + user.display_name + " | Local", url="https://gooogle.com/userID=" + str(message.author.id))
        for i in range(1, 5):
          name = str(i) + "v" + str(i)
          value = ranks[name][1] + " - " + ranks[name][0]
          embed.add_field(name=name, value=spaceChar + value + "\n" + spaceChar, inline=False)

        msg = await message.channel.send(embed=embed)
        await message.delete()
        await msg.add_reaction("❌")
      except ValueError:
        msg = await message.channel.send("The user given has not played any scrims in this channel.\n\n*The RLScrims ranks and leaderboards are channel specific.*")
        await asyncio.sleep(60)
        await msg.delete()
        await message.delete()
      return True
    else:
      return ranks

  else:
    msg = await message.channel.send("Could not get all players ranks, however, they will still be updated after the match.")
    #r = await getRanks(message, user, channel, fromCommand)
    #await msg.delete()
    #return r
# end getRanks

async def getRandomCaptains(players):

  rand1 = int(random.random() * 100) % len(players)
  rand2 = int(random.random() * 100) % len(players)
  if (rand2 == rand1):
    rand2 = rand1 - 1
    if (rand2 < 0):
      rand2 = rand1 + 1

  c1 = players[rand1]
  c2 = players[rand2]

  return c1, c2
# end getRandomCaptains

async def generateRandomString(stringLength):
  s = ""
  for i in range(stringLength):
    r = [
      int(random.random() * 100) % (57 - 48 + 1) + 48, # number
      #int(random.random() * 100) % (90 - 65 + 1) + 65, # big letter
      int(random.random() * 100) % (122 - 97 + 1) + 97 # small letter
    ]
    s += chr(r[int(random.random() * 100) % 2])

  return s
# end generateRandomString

async def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1VgAd4K4M8C8UMOCbg5WV-ru5aD6X_XLAbC8vvzUh-hE")
  return workbook
# end openSpreadsheet