import discord
import asyncio
from datetime import datetime

import SecretStuff
import MoBotDatabase

spaceChar = "⠀"
CINEMA_EMOJI = "🎦"

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

class Command:
  def __init__(self, 
    command, 
    description,
    permissions,
    demoLink,
    exampleInput, 
    exampleOutput, 
    extraInformation
  ):
    self.command = command
    self.description = description
    self.permissions = permissions
    self.demoLink = demoLink
    self.exampleInput = exampleInput
    self.exampleOutput = exampleOutput
    self.extraInformation = extraInformation
  # end Command

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  command = searchCommands(message.content.split("?")[1].strip().lower())
  await sendCommandEmbed(message, command)
# end main

async def mainReactionAdd(message, payload, client): 
  embed = message.embeds[0]
  member = message.guild.get_member(payload.user_id)

  if (payload.emoji.name == CINEMA_EMOJI):
    await toggleDemo(message, embed)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  embed = message.embeds[0]
  member = message.guild.get_member(payload.user_id)

  if (payload.emoji.name == CINEMA_EMOJI):
    await message.channel.trigger_typing()
    await toggleDemo(message, embed)
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove

async def sendCommandEmbed(message, command):
  embed = commandToEmbed(message, command)
  hasDemo = command.demoLink not in ["", None]

  if (hasDemo):
    embed.set_footer(text="Toggle Demo - %s" % (CINEMA_EMOJI))
  
  try:
    msg = await message.channel.send(embed=embed)
  except discord.errors.Forbidden:
    msg = await message.edit(embed=embed)

  if (hasDemo):
    await msg.add_reaction(CINEMA_EMOJI)
# end sendCommandEmbed

async def toggleDemo(message, embed):
  embed = embed.to_dict()
  if ("image" in embed):
    del embed["image"]
    embed = discord.Embed().from_dict(embed)
  else:
    embed = discord.Embed().from_dict(embed)
    demoLink = getDemoLinkFromURL(embed.author.url)
    embed.set_image(url=demoLink)
  await message.edit(embed=embed)
# end toggleDemo

def getDemoLinkFromURL(url):
  command = url.split("command=")[1].split("/")[0].strip().replace("_", " ")

  moBotDB = MoBotDatabase.connectDatabase("MoBot")
  moBotDB.cursor.execute("""
  SELECT demo_link
  FROM mobot_commands
  WHERE command = '%s'
  """ % (MoBotDatabase.replaceChars(command)))
  for record in moBotDB.cursor:
    moBotDB.connection.close()
    return record[0]
# end getDemoFromURL

def commandToEmbed(message, command):

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(
    name="MoBot Commands", 
    url=("https://google.com/MoBotCommands/command=%s/" % (
    command.command,
    )).replace(" ", "_"), 
    icon_url=moBotMember.avatar_url_as()
  )

  description = "**Command:** `@MoBot#0697 %s`\n%s\n%s" % (command.command, command.description, spaceChar)
  embed.description = description

  example = "**Input:** `%s`" % command.exampleInput
  example += "\n**Output:** `%s`" % command.exampleOutput  
  embed.add_field(name="**Example**", value="%s\n%s" % (example, spaceChar), inline=False)

  if (command.extraInformation not in ["", None]):
    embed.add_field(name="**Extra Information**", value="*%s*\n%s" % (command.extraInformation, spaceChar))

  permsString = ""
  perms = decodePermissions(command)
  if (perms):
    for perm in perms:
      permsString += "\n%s" % (perm)
  else:
    permsString += "*None*"
  embed.add_field(name="**Required Permissions**", value=permsString)
  return embed
# end commandToEmbed

def decodePermissions(command):
  permsCode = command.permissions
  perms = []

  if (permsCode[0] == "1"):
    perms.append("Administrator")
  if (permsCode[1] == "1"):
    perms.append("Manage Messages")
  if (permsCode[2] == "1"):
    perms.append("Manage Roles")
  if (permsCode[3] == "1"):
    perms.append("Manage Channels")
  if (permsCode[4] == "1"):
    perms.append("Change Nickname")
  
  return perms
# end decodePermissions

def searchCommands(searchInput):
  commands = getCommands()
  for command in commands:
    if (searchInput == command.command):
      return command
# end searchCommands

def getCommands():
  commands = []

  moBotDB = MoBotDatabase.connectDatabase("MoBot")
  moBotDB.cursor.execute("""
  SELECT 
    command, 
    description, 
    permissions, 
    demo_link,
    example_input, 
    example_output, 
    extra_information
  FROM 
    mobot_commands
  """)

  for record in moBotDB.cursor:
    commands.append(Command(*record))
  moBotDB.connection.close()
  return commands
# end getCommands
