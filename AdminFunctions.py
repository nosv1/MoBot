import discord
import asyncio
from datetime import datetime

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (args[2] == "roles"):
    await displayRoles(message, client)

# end main

async def mainReactionAdd(message, payload, client): 
  pass
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

async def displayRoles(message, client):
  await message.channel.trigger_typing()

  def check(msg):
    return msg.author.id == message.author.id and msg.channel.id == message.channel.id

  await message.channel.send("**From which guild would you like to get the roles from?**\nProvide the Guild_ID below")
  try:
    msg = await client.wait_for("message", timeout=60.0, check=check)
  except asyncio.TimeoutError:
    await message.channel.send("**TIMED OUT**")
    return
  
  guildID = int(msg.content)
  guild = client.get_guild(guildID)
  rolesString = ""
  for role in guild.roles:
    rolesString += "\n\nRole: " + role.name if ("everyone" not in role.name) else "\n\nRole: everyone"
    rolesString += "\n  ID: " + str(role.id)
    rolesString += "\n  Color: " + str(role.color.r) + ", " + str(role.color.g) + ", " + str(role.color.b)

  i = 2000
  while True:
    await message.channel.send(rolesString[i-2000:i]) # do
    if (i >= len(rolesString)): # while not this
      break
    i += 2000
# end getRoleNames