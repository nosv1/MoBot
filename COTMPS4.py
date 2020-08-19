import discord

moBot = "449247895858970624"

async def main(args, message, client):
  roles = []
  for role in message.guild.get_member(message.author.id).roles:
    roles.append(role.name.lower())

  # check if spreadsheet command
  if (args[0][-19:-1] == moBot):
    if (args[1] == "test"):
      pass
# end main

async def memberJoin(member):
  await member.send("Welcome to the Children of the Mountain (PS4) server. At this moment we are still gathering interest for the event. If you have joined via an invite and have not filled out the interest form (https://goo.gl/QDPqUX), please take 5 minutes and fill it out; otherwise, feel free to share the form link or the invite link (https://invite.gg/cotmps4).\n\nWe start qualifying (if all goes to plan) 5th April 5:00pm UTC.\n\nIf you have any questions, please message Mo#9991 or tag @Mo#9991 in #chat.")
  
  memberLog = member.guild.get_channel(554885483063279616) # member-log
  await memberLog.send("" + member.mention + " joined.")
# end memberJoin

async def memberRemove(member, client):
  memberLog = member.guild.get_channel(554885483063279616) # member-log
  await memberLog.send(member.name + " left.\n<@&53015536901029888>")
# end memberRemove

async def mainReactionAdd(message, payload, client):
  user = message.guild.get_member(payload.user_id)
  if (user.name != "MoBot"):
    if (message.channel.id == 555443974433931295): # welcome channel
      if (message.id == 555444886611034112): # welcome message
        await welcomeRoles(message, payload, user)
# end mainReactionAdd


async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def welcomeRoles(message, payload, user):
  roles = message.guild.roles
  cotmRole = None
  peekerRole = None

  flag = "🏁"
  eyes = "👀"

  for role in roles:
    if (role.name == "COTM"):
      cotmRole = role
    elif (role.name == "Peeker"):
      peekerRole = role

    if (cotmRole != None and peekerRole != None):
      break

  for reaction in message.reactions:
    async for member in reaction.users():
      if (member == user):
        if (payload.emoji.name == flag and reaction.emoji == eyes):
          await message.remove_reaction(reaction.emoji, message.guild.get_member(payload.user_id))
        elif (payload.emoji.name == eyes and reaction.emoji == flag):
          await message.remove_reaction(reaction.emoji, message.guild.get_member(payload.user_id))

  if (payload.emoji.name == flag):
    await user.add_roles(cotmRole)
    await user.remove_roles(peekerRole)
  elif (payload.emoji.name == eyes):
    await user.add_roles(peekerRole)
    await user.remove_roles(cotmRole)
# end welcomeRoles