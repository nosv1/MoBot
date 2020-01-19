import discord
import asyncio
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

import SecretStuff
import MoBotDatabase

moBot = 449247895858970624
reactionRoleCommand = "`@MoBot#0697 watch [emoji] [message_id] [#channel] [add/remove] [@Role @Role...]`\n`@MoBot#0697 watch :100: 592137813814804522 add @Subscribers @Verfied`\n`#channel` is only needed if you're using this command in a different channel"

class ReactionMessage:
  def __init__(self, guildName, guildID, channelID, messageID, emoji, roleIDs, addRemove):
    self.guildName = guildName
    self.guildID = guildID
    self.channelID = channelID
    self.messageID = messageID
    self.emoji = emoji
    self.roleIDs = roleIDs.split(",")
    self.addRemove = addRemove
# end ReactionMessage

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, cilent): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove


### --- Reaction Role --- ### 

async def reactionRole(message, payload, member, clickUnclick):
  emoji = payload.emoji.name if (payload.emoji.id == None) else "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
  moBotDB = connectDatabase()
  moBotDB.connection.commit()
  
  reactionMessages = getReactionMessages(moBotDB)

  for reactionMessage in reactionMessages:
    if (reactionMessage.emoji == emoji and reactionMessage.messageID == str(message.id)):
      try:
        for role in reactionMessage.roleIDs:
          try:
            role = message.guild.get_role(int(role))
          except ValueError:
            await message.channel.send("**Could Not Add/Remove Role**\nIt doesn't look like there is a role_id for this reaction...\n\n")
          
          if (reactionMessage.addRemove == "add"):
            await member.add_roles(role)
            try:
              await member.send("In `%s`, you have been %s the role, `%s`" % (
                message.guild.name,
                "added to" if clickUnclick == "click" else "removed from",
                role.name
              ))
            except discord.errors.Forbidden:
              pass
          else:
            await member.remove_roles(role)
            try:
              await member.send("In `%s`, you have been %s the role, `%s`" % (
                message.guild.name,
                "added to" if clickUnclick == "unclick" else "removed from",
                role.name
              ))
            except discord.errors.Forbidden:
              pass
      except discord.errors.Forbidden:
        await message.channel.send("**Cannot Add/Remove Role**\n<@%s> does not have permission." % moBot, delete_after=7)
        await message.remove_reaction(payload.emoji, member)
      break
  moBotDB.connection.close()
# end reactionRole

async def addReactionToMessage(msg, emojis):
  for emoji in emojis:
    await msg.add_reaction(emoji)
# end addReactionToMessage

async def addReactionRoleMessage(message, args):
  await message.channel.trigger_typing()

  moBotDB = connectDatabase()
  moBotDB.connection.commit()

  reactionMessages = getReactionMessages(moBotDB)

  if ("#" in message.content):
    channel = message.guild.get_channel(int(message.content.split("#")[1].split(">")[0].strip()))
    addRemove = message.content.split(str(channel.id) + ">")[1].strip().split(" ")[0].strip()
  else:
    channel = message.channel
    addRemove = message.content.split(args[3])[1].strip().split(" ")[0]
  
  roleIDs = message.content.split(addRemove)[1].strip().split(">")

  roles = []
  for role in roleIDs:
    if ("&" in role):
      roles.append(role.split("&")[1])
  roles = ",".join(roles)

  newReactionMessage = ReactionMessage(
    message.guild.name,
    message.guild.id,
    channel.id,
    args[3], # messageID
    args[2], # emoji
    roles,
    addRemove
  )

  messageExists = False
  for reactionMessage in reactionMessages:
    if (reactionMessage.emoji == newReactionMessage.emoji and reactionMessage.messageID == newReactionMessage.messageID):
      messageExists = True
      moBotDB.cursor.execute("""
        UPDATE reaction_roles
        SET 
          guild_name = '%s',
          guild_id = '%s',
          channel_id = '%s',
          message_id = '%s',
          emoji = '%s',
          role_ids = '%s',
          add_remove = '%s'
        WHERE
          message_id = '%s' AND
          emoji = '%s'
      """ % (
        newReactionMessage.guildName,
        newReactionMessage.guildID,
        newReactionMessage.channelID,
        newReactionMessage.messageID,
        newReactionMessage.emoji,
        ",".join(newReactionMessage.roleIDs),
        newReactionMessage.addRemove,
        newReactionMessage.messageID,
        newReactionMessage.emoji
      ))
      break

  if (not messageExists):
    moBotDB.cursor.execute("""
      INSERT INTO `MoBot`.reaction_roles
        (`guild_name`, `guild_id`, `channel_id`, `message_id`, `emoji`, `role_ids`, `add_remove`)
      VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
    """ % (
      newReactionMessage.guildName,
      newReactionMessage.guildID,
      newReactionMessage.channelID,
      newReactionMessage.messageID,
      newReactionMessage.emoji,
      ",".join(newReactionMessage.roleIDs),
      newReactionMessage.addRemove
    ))

  moBotDB.connection.commit()
  moBotDB.connection.close()

  try:
    await addReactionToMessage(await channel.fetch_message(int(newReactionMessage.messageID)), [newReactionMessage.emoji])
    await message.channel.send("**Now %s `%s` upon click of %s.**\n\nIf this looks wrong, makes sure your command is correct.\n%s" % (
      "adding" if addRemove == "add" else "removing",
      ", ".join([role.name for role in [message.guild.get_role(int(role)) for role in newReactionMessage.roleIDs]]), # convert [roleid, roleid] to Role.name, Role.name
      newReactionMessage.emoji,
      reactionRoleCommand
    ))
  except:
    await message.channel.send("**Error**\n%s, it looks like something didn't go quite right... my guess is there was something missing in the command.\n\n%s" % (message.author.mention, reactionRoleCommand))
# end addReactionRoleMessage

def getReactionMessages(moBotDB):
  moBotDB.cursor.execute("SELECT * FROM reaction_roles")
  
  reactionMessages = []
  for record in moBotDB.cursor:
    reactionMessages.append(ReactionMessage(*record[1:]))
  return reactionMessages
# end getReactionMessages


### --- Auto Roles --- ###

async def clearAutoRole(message, autoRoles):
  await message.channel.trigger_typing()
  
  guildID = message.guild.id

  workbook = await openReactionRoleSpreadsheet()
  sheet = workbook.worksheet("AutoRoles")
  roles = sheet.range("A2:C" + str(sheet.row_count))

  for i in range(len(roles)):
    if (roles[i].value == str(guildID)):
      for j in range(-1, 2):
        roles[i+j].value = ""
      for j in range(i-1, len(roles)):
        try:
          roles[j].value = roles[j+3].value
        except IndexError:
          break
      break

  sheet.update_cells(roles, value_input_option="USER_ENTERED")
  await message.channel.send("No longer adding roles to new members.")
  
  return await updateAutoRoles(autoRoles, workbook)
# end clearAutoRole

async def addAutoRole(message, autoRoles):
  await message.channel.trigger_typing()

  guildID = message.guild.id
  roleIDs = message.content.split("add")[1].strip().split(" ")

  reply = "Will now add the following role(s) upon 'Member Join':\n"
  roleIDsString = ""
  for i in range(len(roleIDs)):
    roleIDs[i] = roleIDs[i].strip()
    if (roleIDs[i] != ""):
      roleIDsString += roleIDs[i] + ","
      print(roleIDs[i])
      for role in message.guild.roles:
        print(role.id)
        if (role.id == int(roleIDs[i])):
          print(role.name)
          reply += role.name + ", "
          break
    
  reply = reply[:-2] + "\n\n*As long as the above list has all the role names in it and <@449247895858970624> is above them in the server roles list, then all should work out...*"
  roleIDsString = roleIDsString[:-1]

  workbook = await openReactionRoleSpreadsheet()
  sheet = workbook.worksheet("AutoRoles")
  roles = sheet.range("A2:C" + str(sheet.row_count))

  for i in range(len(roles)):
    if (roles[i].value == str(guildID)):
      roles[i+1].value = roleIDsString
      break

    if (roles[i].value == ""):
      roles[i].value = message.guild.name
      roles[i+1].value = str(guildID)
      roles[i+2].value = roleIDsString
      break

  sheet.update_cells(roles, value_input_option="USER_ENTERED")
  await message.channel.send(reply)

  return await updateAutoRoles(autoRoles, workbook)      
# end addAutoRole

async def addAutoRoleToUser(member, roleIDs):
  roles = member.guild.roles
  
  for roleID in roleIDs:
    for role in roles:
      if (role.id == int(roleID)):
        try:
          await member.add_roles(role)
        except:
          pass
        break
# end addAutoRoleToUser

async def updateAutoRoles(autoRoles, workbook):
  sheet = workbook.worksheet("AutoRoles")
  roles = sheet.range("A2:C" + str(sheet.row_count))
  for i in range(0, len(roles), 3):
    if (roles[i].value == ""):
      break
    else:
      if (roles[i+1].value not in autoRoles):
        autoRoles[roles[i+1].value] = {
          "RoleIDs" : roles[i+2].value.split(",")
        }
      else:
        autoRoles[roles[i+1].value]["RoleIDs"] = roles[i+2].value.split(",")
  return autoRoles
# end updateAutoRoles


async def openReactionRoleSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1z09wBDnfvEFRivmbq-w2fkYCgUX5KWXGP7zbC0UShmI")
  return workbook
# end openSpreadsheet

def connectDatabase():
  return MoBotDatabase.connectDatabase('MoBot')
# end connectDatabase