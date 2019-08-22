import discord
from datetime import datetime

moBot = "<@449247895858970624>"
self = "XboxGamertags.py"
  
# discord user,xboxGT,discord user last edited,gt added (time),gt edited (time)

async def addGT(message, client, xboxGTs):
  author = str(message.author)
  args = message.content.split(" ")
  reply = ""
  
  newLine = ""
  dUser = ""
  xboxGT = ""
  addTime = str(datetime.now())
  editTime = addTime
  if ("@" in args[len(args)-1]):
    goodToGo = True
    dUser = str(client.get_server(message.server.id).get_member(args[len(args)-1][-19:-1]))
    try:
      xboxGT = message.content.split("\"")[1]
    except IndexError:
      try:
        xboxGT = message.content.split("'")[1]
      except IndexError:
        goodToGo = False
        reply = "```Double check your input. There should be no extra spaces. '@MoBot gt add \"GT to add\" DiscordUser```"
        await client.send_message(message.channel, reply)
    if (goodToGo):
      # check to see if xboxGT is already in the database
      for i in range(len(xboxGTs)):
        if (xboxGT.lower() == xboxGTs[i][1].lower()):
          goodToGo = False
          reply = "```\"" + xboxGT + "\" has already been added.```"
          await client.send_message(message.channel, reply)
          break
      if (goodToGo):
        newLine = dUser + "," + xboxGT + "," + author + "," + addTime + "," + editTime + "\n"
        xboxGTs.append(newLine.split(","))
        await export(xboxGTs)
        reply = "```@" + author + " has added " + dUser + "'s gamertag, \"" + xboxGT + "\".```"
        await client.send_message(message.channel, reply)
  else:
    reply = "```Double check your input. There should be no extra spaces. @MoBot gt add \"GT to add\" DiscordUser```"
    await client.send_message(message.channel, reply)
# end addGT

'''
async def editGT(message, client, xboxGTs):
# end addGT

async def delGT(message, client, xboxGTs):
# end delGT
'''

async def getGT(self, message, client, xboxGTs):
  if (self == "FortKnight.py"):
    author = str(message.author)
    
    dUser = author
    xboxGT = ""
    editTime = ""
    for i in range(len(xboxGTs)):
      goodToGo = False
      if (dUser == xboxGTs[i][0]):
        goodToGo = True
        xboxGT = xboxGTs[i][1]
        break
    if (not goodToGo):
      reply = "```You need to add your gamertag before getting your rank.\nTo add a gamertag, @MoBot gt add 'Gamertag' @DiscordName```"
      await client.send_message(message.channel, reply)
    return (xboxGT)
  else:
    author = str(message.author)
    args = message.content.split(" ")
    reply = ""
    
    dUser = ""
    xboxGT = ""
    editTime = ""
    if ("@" in args[len(args)-1]):
      goodToGo = True
      dUser = str(client.get_server(message.server.id).get_member(args[len(args)-1][-19:-1]))
      # check if user is in database
      for i in range(len(xboxGTs)):
        goodToGo = False
        if (dUser == xboxGTs[i][0]):
          goodToGo = True
          xboxGT = xboxGTs[i][1]
          editTime = xboxGTs[i][4][:-1]
          reply = "```GT: \"" + xboxGT + "\"\nLast Edited: \"" + editTime + " (US Central)\"```"
          await client.send_message(message.channel, reply)
          break
      if (not goodToGo):
        reply = "```The gamertag of the requested user has not been added.\nTo add a gamertag, @MoBot gt add 'Gamertag' @DiscordName```"
        await client.send_message(message.channel, reply)
#end getGT

async def help(message, client):
  reply = "```@MoBot gt add 'Gamertag' @DiscordName\n  - adds gamertag\n\n"
  reply += "@MoBot gt @DiscordName\n  - gets gamertag```"
  await client.send_message(message.channel, reply)
# end help

async def export(xboxGTs):
  file = open(r"D:\Users\Nick\OneDrive\GTA Stuff\Mo Bot\MoBot\XboxGamertagDatabase.txt", "w")
  for i in range(len(xboxGTs)):
    line = ""
    for j in range(len(xboxGTs[i])):
      line += xboxGTs[i][j] + ","
    line = line[:-1]
    file.write(line)
  file.close()
# end expot

async def main(self, message, client):
  args = message.content.split(" ")
  # MoBot gt function gt duser
  
  xboxGTs = []
  file = open(r"D:\Users\Nick\OneDrive\GTA Stuff\Mo Bot\MoBot\XboxGamertagDatabase.txt", "r")
  lines = file.readlines()
  file.close()
  for line in lines:
    if ("," in line):
      xboxGTs.append(line.split(","))
  if ("help" in args):
    await help(message, client)
  elif ("add" in args):
    await addGT(message, client, xboxGTs)
  elif ("edit" in args):
    await editGT(message, client, xboxGTs)
  elif ("del" in args):
    await delGT(message, client, xboxGTs)
  else:
    xboxGT = await getGT(self, message, client, xboxGTs)
    return xboxGT
# end main
