import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

moBotDB = None

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

spaceChar = "⠀"
OK_EMOJI = "🆗"
ONE_EMOJI = "1⃣"
TWO_EMOJI = "2⃣"
FLOPPY_DISK_EMOJI = "💾"
MAG_EMOJI = "🔍"
CHECKMARK_EMOJI = "✅"
X_EMOJI = "❌"

class Command:
  def __init__(self, command_id, trigger, response):
    self.command_id = command_id
    self.trigger = trigger.decode('utf-8')
    self.response = response.decode('utf-8')
# end Command

async def main(args, message, client, MoBotDB):
  global moBotDB
  moBotDB = MoBotDB

  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (args[1] in ["new", "add", "create"]):
    await createCommandSession(message, client)
  elif (args[1] in ["change", "edit", "alter"]):
    await editCommandSession(args, message, client)
  elif (args[1] in ["remove", "delete"]):
    await deleteCommand(args, message, client)
  elif (args[1] == "commands"):
    await displayCommands(message, client)
# end main

async def mainReactionAdd(message, payload, client, MoBotDB): 
  global moBotDB
  moBotDB = MoBotDB

  embed = message.embeds[0]
  commandOwner = message.guild.get_member(int(embed.author.url.split("command_owner_id=")[1].split("/")[0]))

  authorPerms = message.channel.permissions_for(message.author)
  if (not authorPerms.manage_messages):
    await message.channel.send("**Not Permitted**\nOnly members with the Manage Message permission may create/edit/delete MoBot Custom Commands.")
    return

  if (payload.user_id == commandOwner.id):
    if (payload.emoji.name == ONE_EMOJI):
      await handleNewTrigger(commandOwner, message, embed)
    elif (payload.emoji.name == TWO_EMOJI):
      await handleNewResponse(commandOwner, message, embed)
    elif (payload.emoji.name == FLOPPY_DISK_EMOJI):
      await saveCommand(message, embed)
    elif (payload.emoji.name == MAG_EMOJI):
      await displayFullResponse(message, embed)
  await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def displayFullResponse(message, embed):
  await message.channel.send("``` %s ```" % embed.fields[1].value)
# end displayFullResponse

async def displayCommands(message, client):
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Custom Commands", icon_url=client.user.avatar_url, url="https://google.com/SimpleCommands/")
  commandList = getGuildCommands(message.guild.id)
  commandsString = "\n__Trigger -- Response__\n"
  for command in commandList:
    commandsString += "%s. %s -- %s%s\n" % (commandList.index(command) + 1, command.trigger, command.response[:20], ("..." if len(command.response) >= 20 else ""))
  embed.description = "---\n**%s Commands**\n%s\n---" % (message.guild.name, commandsString[:-1])
  await message.channel.send(embed=embed)
# end displayCommands

async def deleteCommand(args, message, client):
  mc = " ".join(args)
  trigger = mc.split("%s %s" % (args[1], args[2]))[1].strip() # split on "delete command"
  command = triggerExists(trigger, getGuildCommands(message.guild.id))

  if (command is None):
    embed = discord.Embed(color=int("0xd1d1d1", 16))
    embed.set_author(name="MoBot Custom Commands", icon_url= client.user.avatar_url)
    embed.description = "---\n**COMMAND NOT FOUND**\nA command with the trigger `%s` was not found. To view this server's commands, use `@MoBot#0697 commands`.\n---" % trigger
    await message.channel.send(embed=embed)
    return
  else:
    def checkEmoji(payload):
      return payload.user_id == message.author.id and payload.channel_id == message.channel.id and payload.emoji.name in [CHECKMARK_EMOJI, X_EMOJI]
    # end checkEmoji

    msg = await message.channel.send("**Delete this command?**")
    await msg.add_reaction(CHECKMARK_EMOJI)
    await msg.add_reaction(X_EMOJI)
    try:
      payload = await client.wait_for("raw_reaction_add", timeout=60, check=checkEmoji)
    except asyncio.TimeoutError:
      await msg.clear_reactions()
      await msg.edit(content="~~ %s ~~\n**TIMED OUT**" % (msg.content))
      return
    
    if (payload.emoji.name == CHECKMARK_EMOJI):
      moBotDB.connection.commit()
      moBotDB.cursor.execute("""
      DELETE FROM 
        custom_commands
      WHERE 
        custom_commands.command_id = '%s'""" % command.command_id)
      moBotDB.connection.commit()

      await msg.clear_reactions()
      await msg.edit(content="~~ %s ~~\n**DELETED**" % (msg.content))

    elif (payload.emoji.name == X_EMOJI):
      await msg.clear_reactions()
      await msg.edit(content="~~ %s ~~\n**CANCELED**" % (msg.content))
# end deleteCommand

async def editCommandSession(args, message, client): # for editing commands
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Custom Commands", icon_url=client.user.avatar_url, url="https://google.com/SimpleCommands/command_id=None/guild_id=%s/command_owner_id=%s" % (message.guild.id, message.author.id))

  mc = " ".join(args)
  trigger = mc.split("%s %s" % (args[1], args[2]))[1].strip() # split on "edit command"
  command = triggerExists(trigger, getGuildCommands(message.guild.id))

  if (command is None):
    embed.description = "---\n**COMMAND NOT FOUND**\nA command with the trigger `%s` was not found. To view this server's commands, use `@MoBot#0697 commands`.\n---" % trigger
    await message.channel.send(embed=embed)
    return
  else:
    embed = embed.to_dict()
    embed["author"]["url"] = embed["author"]["url"].replace("command_id=None", "command_id=%s" % command.command_id)
    embed = discord.Embed().from_dict(embed)

  embed.description = "---\n**Are you editing the trigger or the response?**\n\nType your changes, then to update the trigger, click the %s, or to update the response, click the %s.\n---" % (ONE_EMOJI, TWO_EMOJI)
  embed.add_field(name="__**Trigger**__", value="%s" % trigger, inline=True)
  embed.add_field(name="__**Response**__", value="%s" % (command.response[:40] + ("..." if len(command.response) >= 40 else "")), inline=True)
  embed.set_footer(text="%s - Save Command %s - Full Response " % (FLOPPY_DISK_EMOJI, MAG_EMOJI))

  msg = await message.channel.send(embed=embed)
  await msg.add_reaction(ONE_EMOJI)
  await msg.add_reaction(TWO_EMOJI)
  await msg.add_reaction(FLOPPY_DISK_EMOJI)
  await msg.add_reaction(MAG_EMOJI)
# end editCommandSession

async def createCommandSession(message, client):
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Custom Commands", icon_url=client.user.avatar_url, url="https://google.com/SimpleCommands/command_id=None/guild_id=%s/command_owner_id=%s" % (message.guild.id, message.author.id))

  embed.description = "---\n**Follow the instructions below.**\n\nTo set your command, you will need to set a trigger and a response. To set your trigger, type your trigger, then click the %s. To set your response, type your response, then click the %s. Once both the trigger and the response are set, click the %s to save.\n---" % (ONE_EMOJI, TWO_EMOJI, FLOPPY_DISK_EMOJI)

  embed.add_field(name="__**Trigger**__", value=spaceChar, inline=True)
  embed.add_field(name="__**Response**__", value=spaceChar, inline=True)
  embed.set_footer(text="%s - Save Command %s - Full Response " % (FLOPPY_DISK_EMOJI, MAG_EMOJI))

  msg = await message.channel.send(embed=embed)
  await msg.add_reaction(ONE_EMOJI)
  await msg.add_reaction(TWO_EMOJI)
  await msg.add_reaction(FLOPPY_DISK_EMOJI)
  await msg.add_reaction(MAG_EMOJI)
# end createCommandSession

async def handleNewTrigger(commandOwner, message, embed):
  history = await message.channel.history(after=message).flatten()
  trigger = None
  for msg in history:
    if (msg.author == commandOwner):
      trigger = msg.content

  oldTrigger = embed.fields[0].value[1:-3]
  if (trigger != oldTrigger):
    if (not triggerExists(trigger, getGuildCommands(message.guild.id))):
      embed.description = "---".join(embed.description.split("---")[:-1]) + "---"
      embed = embed.to_dict()
      embed["fields"][0]["value"] = trigger
      embed = discord.Embed().from_dict(embed)
    else:
      embed = updateEmbedStateError(embed, 'error', 'DuplicateTrigger', trigger)
    await message.edit(embed=embed)
# end handleNewTrigger

async def handleNewResponse(commandOwner, message, embed):
  history = await message.channel.history(after=message).flatten()
  response = None
  for msg in history:
    if (msg.author == commandOwner):
      response = msg.content

  command = getCommand(embed.fields[0].value, message.guild.id)
  try:
    oldResponse = command.response
  except AttributeError: # when commmand == None
    oldResponse = None  
  if (response != oldResponse and response is not None):
    embed.description = "---".join(embed.description.split("---")[:-1]) + "---"
    embed = embed.to_dict()
    embed["fields"][1]["value"] = response[:40] + ("..." if len(response) >= 40 else "")
    embed = discord.Embed().from_dict(embed)
    await message.edit(embed=embed)
# end handleNewResponse

async def saveCommand(message, embed):
  trigger = embed.fields[0].value
  response = embed.fields[1].value
  guild = message.guild
  owner = guild.get_member(int(embed.author.url.split("owner_id=")[1].split("/")[0]))
  command_id = embed.author.url.split("command_id=")[1].split("/")[0]

  if (spaceChar in trigger + response):
    return

  moBotDB.connection.commit()
  if (not triggerExists(trigger, getGuildCommands(message.guild.id))):  
    moBotDB.cursor.execute("""
    INSERT INTO 
      `MoBot`.`custom_commands` (`trigger`, `response`, `owner_name`, `owner_id`, `guild_name`, `guild_id`)      VALUES ('%s', '%s', '%s', '%s', '%s', '%s');
    """ % (trigger, response, owner, owner.id, guild.name, guild.id))

  else:
    moBotDB.cursor.execute("""
    UPDATE custom_commands
    SET
      custom_commands.response = '%s',
      custom_commands.owner_name = '%s',
      custom_commands.owner_id = '%s',
      custom_commands.guild_name = '%s'
    WHERE
      custom_commands.command_id = %s""" % (response, owner, owner.id, guild.name, command_id))

  moBotDB.connection.commit()
  await message.channel.send("**Command Saved**", delete_after=2)
# end saveCommand

def triggerExists(trigger, commandList):
  command = [command for command in commandList if command.trigger == trigger]
  return None if not command else command[0]
# end triggerExists

def getGuildCommands(guildID):
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""SELECT * FROM custom_commands 
    WHERE custom_commands.guild_id = %s""" % guildID)
  commandList = []
  for record in moBotDB.cursor:
    print(record[0], record[1], record[2])
    commandList.append(Command(record[0], record[1], record[2]))
  return commandList
# end getGuildCommands

def getCommand(trigger, guildID):
  moBotDB.connection.commit()
  moBotDB.cursor.execute("""
    SELECT custom_commands.command_id, custom_commands.trigger, custom_commands.response
    FROM custom_commands
    WHERE custom_commands.guild_id = '%s' AND custom_commands.trigger = '%s'""" % (guildID, trigger))
  for record in moBotDB.cursor:
    return Command(record[0], record[1], record[2])
  return None
# end getCommand
