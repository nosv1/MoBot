import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector

import SecretStuff
import MoBotDatabase

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

GRG_GUILD_ID = 427103715678355476

spaceChar = "⠀"

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

async def memberRemove(member, client):
  pass
# end memberRemove

async def combineRoles(changed_role, member, guild): # https://discordapp.com/channels/@me/592132941774192641/675386871437721620
  for guild_role in guild.roles:
    if changed_role.name.lower() in guild_role.name.lower() and changed_role.name.lower() != guild_role.name.lower(): # combo role found

      for member_role_1 in member.roles:
        if member_role_1.name.lower() in guild_role.name.lower() and member_role_1.name.lower() != guild_role.name.lower(): # first role found

          for member_role_2 in member.roles:
            if member_role_1.name != member_role_2.name:
              if member_role_2.name.lower() in guild_role.name.lower() and member_role_2.name.lower() != guild_role.name.lower(): # second role found

                await member.add_roles(guild_role)
                return

      await member.remove_roles(guild_role)
      break
# end combineRoles