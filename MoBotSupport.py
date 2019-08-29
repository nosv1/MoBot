import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
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

async def memberRemove(member):
  pass
# end memberRemove