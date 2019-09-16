# MoBot made by Mo#9991

import discord
import asyncio 
from datetime import datetime, timedelta 
import RLRanks
import sys
import traceback

mo = 405944496665133058
  
client = discord.Client()

started = False
# when bot is first online
@client.event
async def on_ready():
  global started
  if (not started):
    print("\nRLRanksUpdater is online - " + str(datetime.now()) + "\n")
    started = True
    try:
      print("Starting Loop")
      await RLRanks.updateUserRolesLoop(client)
    except:
      try:
        await client.get_user(int(mo)).send("RLRanksUpdater Error!```" + str(traceback.format_exc()) + 
        "```")
      except:
        print(str(traceback.format_exc()))
      sys.exit()
  else:
    sys.exit()
# end on_ready

print("Connecting...")
client.run("NDQ5MjQ3ODk1ODU4OTcwNjI0.D1jdgQ.bhBue3MvDD7BGIMIxLqlm9bpTNI")