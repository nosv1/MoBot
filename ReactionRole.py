import discord
import asyncio
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread

import SecretStuff

moBot = "449247895858970624"

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

async def addReactionToMessage(msg, emoji):
  await msg.add_reaction(emoji)
# end addReactionToMessage

async def addReactionRoleMessage(message, args, reactionMessages):
  await message.channel.trigger_typing()

  workbook = await openReactionRoleSpreadsheet()
  sheet = workbook.worksheet("Reaction Messages")
  messages = sheet.range("A2:G" + str(sheet.row_count))


  if ("#" in message.content):
    channel = message.guild.get_channel(int(message.content.split("#")[1].split(">")[0].strip()))
    addRemove = message.content.split(str(channel.id) + ">")[1].strip().split(" ")[0].strip()
  else:
    channel = message.channel
    addRemove = message.content.split(args[3])[1].strip().split(" ")[0]
  
  roleIDs = message.content.split(addRemove)[1].strip().split(">")

  roles = ""
  for role in roleIDs:
    if ("&" in role):
      roles += role[-18:] + ","
  roles = roles[:-1]

  for i in range(0, len(messages), 7):
    if (messages[i].value == ""):
      messages[i].value = message.guild.name
      messages[i+1].value = str(message.guild.id)
      messages[i+2].value = str(channel.id)
      messages[i+3].value = args[3]
      messages[i+4].value = args[2]
      messages[i+5].value = str(roles)
      messages[i+6].value = addRemove
      msg = await message.channel.send("**Now watching message for reaction.**")
      break
    elif (messages[i+4].value == args[2] and messages[i+3].value == args[3]):
      messages[i].value = message.guild.name
      messages[i+1].value = str(message.guild.id)
      messages[i+2].value = str(channel.id)
      messages[i+3].value = args[3]
      messages[i+4].value = args[2]
      messages[i+5].value = str(roles)
      messages[i+6].value = addRemove
      msg = await message.channel.send("**Role updated.**")
      break
      
  try:
    await addReactionToMessage(await channel.fetch_message(int(args[3])), args[2])
    sheet.update_cells(messages, value_input_option="USER_ENTERED")
  except:
    await msg.delete()
    await message.channel.send("Looks like something didn't go quite right... Double check there aren't any double spaces, and your command looks like this \n`@MoBot#0697 watch [insert_emoji] [Message_ID] [#channel] [add/remove] [@Roles to Add]`\n`@MoBot#0697 watch :100: 592137813814804522 @Subscribers @Verfied`\n\nNote the #channel is only needed if you are not using the command in the same channel as the message you are adding reactions to.")

  return await updateReactionMessages(reactionMessages, workbook)
# end addReactionRoleMessage

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

async def updateReactionMessages(reactionMessages, workbook):
  sheet = workbook.worksheet("Reaction Messages")
  messages = sheet.range("A2:G" + str(sheet.row_count))
  for i in range(0, len(messages), 7):
    if (messages[i].value == ""):
      break
    else:
      if (messages[i+4].value not in reactionMessages):
        reactionMessages[messages[i+4].value] = {
          int(messages[i+3].value) : {
            "RoleID" : [messages[i+5].value.split(","), messages[i+6].value],
          }
        }
      else:
        reactionMessages[messages[i+4].value][int(messages[i+3].value)] = {
          "RoleID" : [messages[i+5].value.split(","), messages[i+6].value],
        }
  return reactionMessages
# end updateReactionMessages

async def clearDeletedMessages(reactionMessages, client):
  workbook = await openReactionRoleSpreadsheet()
  sheet = workbook.worksheet("Reaction Messages")
  messages = sheet.range("A2:G" + str(sheet.row_count))
  for i in range(len(messages)-7, -1, -7):
    if (messages[i].value != ""):
      error = False
      try:
        guild = client.get_guild(int(messages[i+1].value))
        channel = guild.get_channel(int(messages[i+2].value))
        message = await channel.fetch_message(int(messages[i+3].value))
      except discord.errors.NotFound:
        error = True
      except AttributeError:
        error = True

      if (error):
        for j in range(i, len(messages), 7):
          for k in range(j, j+7):
            if (messages[k].value != ""):
              messages[k].value = messages[k+7].value
  sheet.update_cells(messages, value_input_option="USER_ENTERED")

  return await updateReactionMessages(reactionMessages, workbook)
# end clearDeletedMessages

async def openReactionRoleSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1z09wBDnfvEFRivmbq-w2fkYCgUX5KWXGP7zbC0UShmI")
  return workbook
# end openSpreadsheet