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

  elif (args[2] == "members"):
    await displayRoleMembers(message)

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
    rolesString += "\n  Color: #" + str(hex(role.color.value).replace("0x", "")).rjust(6, "0")

  i = 2000
  while True:
    await message.channel.send(rolesString[i-2000:i]) # do
    if (i >= len(rolesString)): # while not this
      break
    i += 2000
# end getRoleNames

async def displayRoleMembers(message):
  role_id = message.content.split("members")[1].trim()
  role = [r for r in message.guilds.roles if str(r.id) == role_id][0]

  msg = await message.channel.send('two sec')
  await msg.edit(content="\n".join(role.members))
# end displayRoleMembers