import discord
from datetime import datetime

moBot = "<@449247895858970624>"
self = "IG.py"

async def main(args, message, client):
  author = message.author

  # check if author is DynoBot
  #if (str(author) == str("Dyno#3861")):
  #  await DynoBot(message, client)
# end main
      
async def DynoBot(message, client):
  # get actual message
  try:
    print (str(datetime.now()), str(": " + message.embeds[0][ "description" ]))
    msg = message.embeds[0][ "description" ]
  except IndexError:
    print (message.content)
    msg = (await client.fetch_message(channel, msgId)).content.lower()    
    
  
  if ("FN Recruitee" in msg or "RL Recruitee" in msg):
    # target channel to reply in
    recruitmentProcess = client.get_channel("461218901288812544")
    recruitment = client.get_channel("461228579896819722")
    fnRecruitment = client.get_channel("461226028719931392")
    rlRecruitment = client.get_channel("461227558910951424")
    igOwner = "<@ &" + discord.utils.get(message.server.roles, name = "IG | Owner").id + ">"
    igRecruitment = "<@ &" + discord.utils.get(message.server.roles, name = "IG | Recruitment").id + ">"
    
    userID = msg.split("**")[1].split(" ")[0]
    replyRP = userID + " we are glad you have decided to apply for Impromptu Gaming, please read the above post."
    replyFR = "A new recruit has joined, check <#" + str(fnRecruitment.id) + "> " + str(igOwner) + " " + str(igRecruitment) + "."
    replyRR = "A new recruit has joined, check <#" + str(rlRecruitment.id) + "> " + str(igOwner) + " " + str(igRecruitment) + "."
    
    # check what role was given
    if (msg.find("given the `eSports Recruit`") != -1):
      await client.send_message(recruitmentProcess, replyRP)
    elif (msg.find("given the `FN Recruitee`") != -1):
      await client.send_message(recruitment, replyFR)
    elif (msg.find("given the `RL Recruitee`") != -1):
      await client.send_message(recruitment, replyRR)
# end DynoBot