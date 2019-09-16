import discord
from datetime import datetime

moBot = "<@449247895858970624>"
self = "tTeams.py"

# user's prefix needs to be better 'set'

async def main(self, message, client):
  author = message.author
  args = message.content.split(" ")
  
  hasPermissions = False
  roles = author.roles
  for role in roles:
    if (message.guild.id == 437936224402014208): # if noble leagues server
      if (role.name == "Admin"): 
        hasPermissions = True
        break
    else:
      hasPermissions = True
      break
  
  if (args[0] == "!t" and hasPermissions):
    if (len(args) > 1):
      # create team
      if (args[1] == "create"):
        if (len(args) > 2):
          # check if user is already a captain on another team
          teams = await getServerTeams(message.guild.id)
          isCaptain = False
          for team in teams:
            if (str(message.author.id) == teams[team][2]):
              isCaptain = True
              break
          if (not(isCaptain)):
            await createTeam(message, client, args)
          else:
            await message.channel.send("```You are a captain on another team. You can only create one team.```")
        else:
          await message.channel.send("```!t create team_name -- It looks like you didn't give a team name.```")
      if (args[1] == "game"):
        if (len(args) >= 4): # check if game and team was given
          t = []
          game = ""
          if (args[2].lower() == "fortnite"):
            t = await wasTeamGiven(message, args, 3)
            game = "Fortnite"
          elif (args[2].lower() == "rocket" and args[3].lower() == "league"):
            t = await wasTeamGiven(message, args, 4)
            game = "Rocket League"
          else:
            await message.channel.send("```Please specify a valid game: Fortnite, Rocket League\n!t game Fortnite/Rocket Leauge team_name```")
            
          if (len(t) == 0):
            await message.channel.send("```!t game Fortnite/Rocket Leauge team_name -- It looks like you didn't give a team name. !t captain @user team_name If you don't know the team name, type !t roster prefix```")
          else:
            team = t[1]
            teams = t[0]
            # check if caller is captain
            try:
              if (str(message.author.id) == teams[team][2]):
                await updateGame(message, teams, team, game)
              else:
                await message.channel.send("```You are not a captain of that team.```")
            except KeyError:
              await message.channel.send("```!t game Fortnite/Rocket Leauge team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
        else:
          await message.channel.send("```!t game Fortnite/Rocket Leauge team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
      # update captain
      elif (args[1].lower() == "fortnite" or args[1].lower() == "rocket"):
        game = "Fortnite"
        if (len(args) > 2):
          if (args[2].lower() == "league"):
            game = "Rocket League"
        teams = await getServerTeams(message.guild.id)
        t = []
        for team in teams:
          if (teams[team][1] == game):
            t.append(team)
        reply = "Teams Associated with [ " + game + " ]:\n"
        if (len(t) != 0):
          for team in t:
            reply += "\t [" + teams[team][0] + "] " + team + "\n"
          reply = reply[:-1] # remove trailing new line
          await message.channel.send("```" + reply + "```")
        else:
          await message.channel.send("```There are no teams associated with " + game + ".```")
      elif (args[1] == "captain"):
        if (len(args) >= 4): # check if user and team was given
          t = await wasTeamGiven(message, args, 3)
          if (len(t) == 0):
            await message.channel.send("```!t captain @user team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
          else:
            team = t[1]
            teams = t[0]
          
            id = "" # double check if user was given
            for i in range(len(args[2])):
              try:
                if (int(args[2][i]) >= 0):
                  id += args[2][i]
              except ValueError:
                continue
            user = message.guild.get_member(int(id))
            if (user != None):
              # check if caller is captain
              try:
                if (str(message.author.id) == teams[team][2]):
                  await updateCaptain(message, teams, team, user.id)
                else:
                  await message.channel.send("```You are not a captain of that team.```")
              except KeyError:
                await message.channel.send("```!t captain @user team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
            else:
              await message.channel.send("```!t captain @user team_name -- It looks like you did not give a valid user. Please make sure you tag the user you are trying to make captain !t captain @user team_name```")
        else:
          await message.channel.send("```!t captain @user team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
      # update prefix 
      elif (args[1] == "prefix"):
        if (len(args) >= 4): # check if prefix and team were given
          t = await wasTeamGiven(message, args, 3)
          if (len(t) == 0):
            await message.channel.send("```!t prefix new_prefix team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
          else:
            team = t[1]
            teams = t[0]
            # check if caller is captain
            try:
              if (str(message.author.id) == teams[team][2]):          
                await updatePrefix(message, client, args, teams, team)
              else:
                await message.channel.send("```You are not a captain of that team.```")
            except KeyError:
              await message.channel.send("```!t prefix new_prefix team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
        else:
          await message.channel.send("```!t prefix new_prefix team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
      elif (args[1] == "active"):
        t = await wasTeamGiven(message, args, 2)
        if (len(t) == 0):
          await message.channel.send("```!t active team_name -- Please include a team name when sending command. If you don't know the team name, type !t roster prefix```")
        else:
          team = t[1]
          teams = t[0]
          try:
            prefix = teams[team][0]
            await removePrefixFromUser(message, message.author.id)
            await addPrefixToUser(message, message.author.id, prefix)         
            try:
              await message.channel.send("```Prefix updated for [ " + message.author.nick + " ]```")
            except TypeError:
              await message.channel.send("```Prefix updated for [ " + message.author.name + " ]```")
          except:
            await message.channel.send("```!t active team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix then type !t active team_name to set your active prefix.```")     
      # add/remove user
      elif (args[1] == "add" or args[1] == "remove"):
        if (len(args) >= 4): # check if user and team was given
          t = await wasTeamGiven(message, args, 3)
          if (len(t) == 0):
            await message.channel.send("```!t active team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
          else:
            team = t[1]
            teams = t[0]
          
            id = "" # double check if user was given
            for i in range(len(args[2])):
              try:
                if (int(args[2][i]) >= 0):
                  id += args[2][i]
              except ValueError:
                continue
            user = message.guild.get_member(int(id))
            if (user != None):
              # check if caller is captain
              try:
                if (str(message.author.id) == teams[team][2]):
                  if (args[1] == "add"):
                    await addUserToTeam(message, user.id, team)
                  else:
                    await removeUserFromTeam(message, await getServerTeams(message.guild.id), team, user.id)
                else:
                  await message.channel.send("```You are not a captain of that team.```")
              except KeyError:
                await message.channel.send("```!t add/remove @user team_name -- It looks like you didn't give a team name. If you don't know the team name, type !t roster prefix```")
            else:
              await message.channel.send("```!t add/remove @user team_name -- A user was not given. To add a user to your team, type !t add @user team_name```")
        else:
          await message.channel.send("```!t add/remove @user team_name -- A team was not given. to add a user to your team, type !t add @user team_name```")
      # leave team
      elif (args[1] == "leave"):
        t = await wasTeamGiven(message, args, 2)
        if (len(t) == 0):
          await message.channel.send("```!t leave team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
        else:
          team = t[1]
          teams = t[0]
          await removeUserFromTeam(message, teams, team, message.author.id)
      # delete team
      elif (args[1] == "delete"):
        if (len(args) >= 3):
          t = await wasTeamGiven(message, args, 2)
          if (len(t) == 0):
            await message.channel.send("```!t delete team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
          else:
            team = t[1]
            teams = t[0]
            if (str(message.author.id) == teams[team][2] or str(message.author.id) == str(375436924757999657)):
              for t in teams:
                if (t.lower() == team.lower()):
                  await deleteTeam(message, teams, team)
                  break
                elif (team.lower() == teams[t][0].lower()):
                  await message.channel.send("```!t delete team_name -- It looks like you gave a prefix instead of a team name. If you would like to delete a team, type !t delete team_name If you don't know the team name, type !t roster prefix```")
                  break
            else:
              await message.channel.send("```You are not the captain of the team you are trying to delete. Only captains can delete their own team.```")
        else:
          await message.channel.send("```!t delete team_name -- Please include a team name when sending command. !t roster team_name or, if you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
      elif (args[1] == "edit"): 
        if (len(args) >= 3):
          teams = await getServerTeams(message.guild.id)
          newTeamName = ""
          for i in range(2, len(args)):
            newTeamName += args[i] + " "
          newTeamName = newTeamName[:-1]
            
          if (len(newTeamName) == 0):
            await message.channel.send("```!t edit team_name -- Please include the new team name sending command.```")
          else:
            # get users team 
            t = await getCaptainsTeam(message, message.author.id)
            tSplit = t.split()
            for i in tSplit:
              args.append(i)
            t = await wasTeamGiven(message, args, len(args) - len(tSplit))
            # check if user is captain
            team = t[1]
            teams = t[0]
            if (str(message.author.id) == teams[team][2] or str(message.author.id) == str(375436924757999657)):
              for t in teams:
                if (t.lower() == team.lower()):
                  await editTeam(message, teams, team, newTeamName)
                  break
                elif (team.lower() == teams[t][0].lower()):
                  await message.channel.send("```!t edit team_name -- It looks like you gave a prefix instead of a team name. If you would like to delete a team, type !t delete team_name If you don't know the team name, type !t roster prefix```")
                  break
            else:
              await message.channel.send("```You are not the captain of the team you are trying to edit. Only captains can edit their own team.```")
        else:
          await message.channel.send("```!t edit new_team_name -- Please include the new team name when sending command.```")
      # get roster
      elif (args[1] == "roster"):
        if (len(args) >= 3):
          t = await wasTeamGiven(message, args, 2)
          if (len(t) == 0):
            await message.channel.send("```!t roster team_name -- Please include a team name, or prefix, when sending command. !t roster team_name or !t roster prefix```")
          else:
            team = t[1]
            teams = t[0]
            for t in teams:
              if (t.lower() == team.lower() or team.lower() == teams[t][0].lower()):
                await getRoster(message, teams, t)
        else:
          await message.channel.send("```!t roster team_name -- Please include a team name or prefix when sending command. !t roster team_name or !t roster prefix If you don't know the team name, type !t teams prefix to return the teams with the given prefix.```")
      # get teams in server
      elif (args[1] == "teams"):
        teams = await getServerTeams(message.guild.id)
        reply = "Teams:\n"
        for team in teams:
          reply += "\t[" + teams[team][0] + "] " + team + "\n"
        reply = reply[:-1]
        await message.channel.send("```" + reply + "```")
      # help
      elif (args[1] == "help"):
        await help(message)
    # help
    else:
      await  help(message)
  elif (args[0] == "!t" and not hasPermissions):
    await message.channel.send("```Not enough permissions.```")
# end main

async def createTeam(message, client, args):
  teams = await getServerTeams(message.guild.id)

  team = ""
  for i in range(2, len(args)):
    team += str(args[i]).strip() + " "
  team = team[:-1] # remove trailing space
  
  if (team in teams): # check if team has been added already
    await message.channel.send("```Team [ " + team + " ], with Prefix [ " + teams[team][0] + " ], already exists```")
  else:
    prefix = team
    temp = prefix.split(" ")
    if (len(temp) > 1):
      prefix = ""
      for i in range(len(temp)):
        prefix += temp[i][0]
    
    user = message.guild.get_member(message.author.id)
    teams[team] = [prefix, "None", user.id, []]
    await writeTeams(message.guild.id, teams)
    await message.channel.send("```Team [ " + team + " ] created with Prefix [ " + prefix + " ]```")
    await addUserToTeam(message, user.id, team)
# end createTeam

async def updateGame(message, teams, team, newGame):
  teams[team][1] = newGame
  await message.channel.send("```Game for [ " + team + " ] has been udpated. Game: [ " + newGame + " ]```")
  await writeTeams(message.guild.id, teams)
# end updateGame

async def updateCaptain(message, teams, team, newCaptain):
  teams[team][2] = newCaptain
  try:
    await message.channel.send("```Captain for [ " + team + " ] has been udpated. New Captain: [ " + message.guild.get_member(newCaptain).nick + " ]```")
  except TypeError:
    await message.channel.send("```Captain for [ " + team + " ] has been udpated. New Captain: [ " + message.guild.get_member(newCaptain).name + " ]```")
  await writeTeams(message.guild.id, teams)
# end updateCaptain

async def deleteTeam(message, teams, team):
  for tm in teams[team][3]:
    try:
      await message.channel.send("``` Member [ " + message.guild.get_member(int(tm)).nick + " ] has been removed from [ " + team + " ]```")
    except TypeError:
      await message.channel.send("``` Member [ " + message.guild.get_member(int(tm)).name + " ] has been removed from [ " + team + " ]```")
    await removePrefixFromUser(message, int(tm))
  del teams[team]
  await message.channel.send("```Team [ " + team + " ] has been deleted```")
  await writeTeams(message.guild.id, teams)
# end deleteTeam

async def editTeam(message, teams, team, newTeamName):
  teams[newTeamName] = teams[team]
  del teams[team]
  print(teams)
  await message.channel.send("```Team [ " + team + " ] has a new team name [ " + newTeamName + " ]```")
  await message.channel.send("```To update prefix, !t prefix new_prefix team_name```")
  await writeTeams(message.guild.id, teams)
# end editTeam

async def getRoster(message, teams, team):
  roster = " Roster - [ " + team + " ]:\n"
  for tm in teams[team][3]:
    roster += "\t"
    try:
      roster += message.guild.get_member(int(tm)).nick
    except TypeError:
      roster += message.guild.get_member(int(tm)).name
    if (tm == teams[team][2]):
      roster += " [C]"
    roster += "\n"
  roster = roster[:-1]
  await message.channel.send("```" + roster + "```")
# end getRoster

async def updatePrefix(message, client, args, teams, team):
  user = message.guild.get_member(message.author.id)
  nogo = False
  for team in teams:
    if (str(user.id) == teams[team][2]): # check if caller is a captain
      if (len(args) > 2): # check if a new prefix was given
        newPrefix = args[2]
        teams[team][0] = newPrefix # update prefix
        # update other team members nicknames
        for tm in teams[team][3]:
          await removePrefixFromUser(message, int(tm))
          await addPrefixToUser(message, int(tm), newPrefix)
        await message.channel.send("```Prefix updated for [ " + team + " ] to [ " + newPrefix + " ]```")
        await writeTeams(message.guild.id, teams)
        nogo = False
        break
      else: 
        await message.channel.send("```No prefix was given. !t prefix newPrefix```")
    else: 
      nogo = True
    
  if (nogo):
    try:
      await message.channel.send("```[ " + user.nick + " ] is not a captain of a team. Only captains can change prefixes```")
    except TypeError:
      await message.channel.send("```[ " + user.name + " ] is not a captain of a team. Only captains can change prefixes```")
# end updatePrefix

async def addUserToTeam(message, user, teamToJoin):
  teams = await getServerTeams(message.guild.id)
  if (str(user) not in teams[teamToJoin][3]):
    user = message.guild.get_member(user)
    teams[teamToJoin][3].append(user.id)
    await removePrefixFromUser(message, user.id)
    await addPrefixToUser(message, user.id, teams[teamToJoin][0])
    await writeTeams(message.guild.id, teams)
    try:
      await message.channel.send("```[ " + user.nick + " ] added to team [ " + teamToJoin + " ]```")
    except TypeError:
      await message.channel.send("```[ " + user.name + " ] added to team [ " + teamToJoin + " ]```")
      
  else:
    try:
      await message.channel.send("``` [ " + user.nick + " ] is already on this team...```")
    except TypeError:
      await message.channel.send("``` [ " + user.name + " ] is already on this team...```")
# end addToTeam

async def removeUserFromTeam(message, teams, team, user):
  del teams[team][3][teams[team][3].index(str(user))]
  await removePrefixFromUser(message, user)
  await writeTeams(message.guild.id, teams)
  try:
    await message.channel.send("``` [ " + message.guild.get_member(user).nick + " ] has been removed from [ " + team + " ]```")
  except TypeError:
    await message.channel.send("``` [ " + message.guild.get_member(user).name + " ] has been removed from [ " + team + " ]```")
  if (len(teams[team][3]) == 0):
    await message.channel.send("``` There are no more members a part of [ " + team + " ]```")
    await deleteTeam(message, teams, team)
# end removeUserFromTeam

async def addPrefixToUser(message, user, prefix):
  user = message.guild.get_member(user)
  if (prefix != ""):
    if (user.nick != None): # update nickname
      await user.edit(nick="[" + prefix + "] " + user.nick)
    else:
      await user.edit(nick="[" + prefix + "] " + user.name)
    
# end addPrefixToUser

async def removePrefixFromUser(message, user):
  user = message.guild.get_member(user)
  
  try:
    if ("] " in user.nick): # make sure there is a prefix
      newNick = user.nick.split("] ")
      newNick = newNick[-1]
      await user.edit(nick=newNick)
  except TypeError:
    pass
# end removePrefixFromUser

async def getServerTeams(guildID):
  guild = {} # {Team : [Prefix, Captain, [Team Members]]}
  iFile = open("tTeamsList.txt", "r")
  lines = iFile.readlines()
  iFile.close()
  if (len(lines) > 0):
    for line in lines:
      l = line.split(",")
      if ("\n" in l[-1]):
        l[-1] = l[-1][:-1] # remove new line
      if (l[0] not in guild):
        guild[l[0]] = {}
      guild[l[0]][l[1]] = [l[2], l[3], l[4], []] # get team, prefix, game, and captain
      for i in range(5, len(l)):
        guild[l[0]][l[1]][3].append(l[i]) # get team members
  if (str(guildID) not in guild):
    guild[str(guildID)] = {}
  return guild[str(guildID)]
# end getServerTeams

async def getAllTeams():
  guild = {} # {Team : [Prefix, Captain, [Team Members]]}
  iFile = open("tTeamsList.txt", "r")
  lines = iFile.readlines()
  iFile.close()
  if (len(lines) > 0):
    for line in lines:
      l = line.split(",")
      if ("\n" in l[-1]):
        l[-1] = l[-1][:-1] # remove new line
      if (l[0] not in guild):
        guild[l[0]] = {}
      guild[l[0]][l[1]] = [l[2], l[3], l[4], []] # get team as key, prefix, game, and captain, empty user array
      for i in range(5, len(l)):
        guild[l[0]][l[1]][3].append(l[i]) # get team members
  return guild

async def getTeam(message, user):
  teams = await getServerTeams(message.guild.id)
  for team in teams:
    if (str(user) in teams[team][3]):
      return team
# end getTeam

async def getCaptainsTeam(message, user):
  teams = await getServerTeams(message.guild.id)
  for team in teams:
    if (str(user) == teams[team][2]):
      return team
# end getCaptainsTeam

async def writeTeams(guildID, teams):
  print(teams)
  guild = await getAllTeams()
  guild[str(guildID)] = teams
  print(guild[str(guildID)])
  output = ""
  for gID in guild:
    for team in guild[gID]:
      output += gID + "," + team + "," + guild[gID][team][0] + "," + str(guild[gID][team][1]) + "," + str(guild[gID][team][2]) + ","
      for i in range(len(guild[gID][team][3])):
        output += str(guild[gID][team][3][i]) + ","
      output = output[:-1] + "\n" # remove trailing comma and add new line
  output = output[:-1] # remove trailing new line
  
  oFile = open("tTeamsList.txt", "w")
  oFile.write(output)
  oFile.close()
# end writeTeams

async def wasTeamGiven(message, args, startIndex):
  teams = await getServerTeams(message.guild.id)
  if (len(args) >= startIndex): # check if team was given
    team = "" # double check if team was given
    for i in range(startIndex, len(args)):
      team += args[i] + " "
    team = team[:-1] # remove trailing space
    if (team != ""):
      t = [teams, team]
      return t
    else:
      return []
  else:
    return []
# end wasTeamGiven

async def help(message):
  reply = "!t create team_name -- creates a team, and makes the member that sent the command the captain (only captains can add/remove members to/from a team, delete the team, and change the team's prefix)\n\n"
  reply += "!t game Fortnite/Rocket League -- sets game to team\n\n"
  reply += "!t Fortnite/Rocket League -- returns the teams that are associated with that game\n\n"
  reply += "!t prefix new_prefix team_name -- changes the prefix of the team\n\n"
  reply += "!t add @user team_name or !t remove @user team_name -- adds/removes user to/from the team the captain that sent the command is on\n\n"
  reply += "!t captain @user team_name -- updates the captain of the team\n\n"
  reply += "!t active team_name -- sets prefix to user based on active team\n\n"
  reply += "!t leave team_name -- removes the member that sent the command from the team he/she is on\n\n"
  reply += "!t delete team_name -- deletes the team that the captain that sent the command is on\n\n"
  reply += "!t edit new_team_name -- edits the users team name if they are captain\n\n"
  reply += "!t roster team_name or !t roster prefix -- gets the roster of the respective team\n\n"
  reply += "!t teams -- gets all the teams currently in use\n\n"
  reply = reply[:-2]
  await message.channel.send("```" + reply + "```")
# end help