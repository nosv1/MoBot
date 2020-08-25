import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector

import SecretStuff
import MoBotDatabase
import RandomSupport

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

RESERVE_EMBED = 747465079523508334

RESERVE_ROLE = 720256259948937237
DRIVER_ROLE = 719961302700654702

space_char = "⠀"



class Reserve:
  def __init__(self, driver_id, requested_id, date):
    self.driver_id, self.need_avail = self.needAvail(driver_id)
    self.requested_id = int(requested_id)
    self.date = float(date)
  # end __init__

  def needAvail(self, driver_id):
    if driver_id[-1] == "1":
      return (int(driver_id[:-1]), 1)
    else:
      return (int(driver_id[:-1]), 0)
  # end needAvail
# end Reserve

class ReserveCombo:
  def __init__(self, driver_id, reserve_id):
    self.driver_id = driver_id
    self.reserve_id = reserve_id
# end ReserveCombo


''' DISCORD '''

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def mainReactionAdd(message, payload, client): 
  member = message.guild.get_member(payload.user_id)

  if member.id != moBot:
    if message.id == RESERVE_EMBED:
      member_roles = [role.id for role in member.roles]
      
      if (
        (
          RESERVE_ROLE in member_roles and
          payload.emoji.name == RandomSupport.FIST_EMOJI
        ) or (
          DRIVER_ROLE in member_roles and
          payload.emoji.name == RandomSupport.WAVE_EMOJI
        )
      ):
        await handleReserveButton(message, member, payload.emoji.name, True)

      elif member.id == mo and payload.emoji.name == RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI:
        await updateReservesEmbed(message, getReserveCombos(getReserves()))
        await message.remove_reaction(payload.emoji.name, member)
      
      else:
        await message.remove_reaction(payload.emoji.name, member)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  member = message.guild.get_member(payload.user_id)

  if member.id != moBot:
    if message.id == RESERVE_EMBED:
      await handleReserveButton(message, member, payload.emoji.name, False)
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove



''' RESEREVES '''
async def handleReserveButton(message, member, button, on_click):
  embed = message.embeds[0]

  if on_click:
    await onClick(member, button)
  else:
    await onUnclick(member, button)

  reserves = getReserves()
  reserve_combos = getReserveCombos(reserves)
  await updateReservesEmbed(message, reserve_combos)

# end handleReserveButton

def getReserveCombos(reserves):
  reserve_combos = [] # [driver_id, reserve_id]

  for i, r1 in enumerate(reserves):
    if (
      r1.driver_id not in [r.driver_id for r in reserve_combos] and 
      r1.driver_id not in [r.reserve_id for r in reserve_combos]
    ): # not assigned as driver or reserve
      if r1.need_avail == 1 and r1.requested_id != 0: # needs and has reserve
        reserve_combos.append(ReserveCombo(r1.driver_id, r1.requested_id))
      
      if r1.need_avail == 1 and r1.requested_id == 0: # needs doesn't have
        reserve_found = False
        for j in range(i, len(reserves)):
          if j == i:
            continue

          r2 = reserves[j]
          if r2.driver_id not in [r.reserve_id for r in reserve_combos]: # not already reserving
            if r2.need_avail == 0 and r2.requested_id == 0: # is avail
              reserve_found = True
              reserve_combos.append(ReserveCombo(r1.driver_id, r2.driver_id))
              break

        if not reserve_found: # need but none avail
          reserve_combos.append(ReserveCombo(r1.driver_id, 0))

  for r1 in reserves:
    if r1.need_avail == 0: # maybe avail
      if r1.driver_id not in [r.reserve_id for r in reserve_combos]: # avail, but not needed
        reserve_combos.append(ReserveCombo(0, r1.driver_id))
            
  return reserve_combos
# end getReserveCombos

async def updateReservesEmbed(message, reserve_combos):
  embed = message.embeds[0].to_dict()
  embed["fields"][0]["value"] = ""
  embed["fields"][1]["value"] = ""

  for combo in reserve_combos:
    if combo.driver_id != 0:
      if combo.reserve_id != 0:
        embed["fields"][0]["value"] += f"{message.guild.get_member(combo.driver_id).display_name} rsv. by {message.guild.get_member(combo.reserve_id).display_name}\n"
        embed["fields"][1]["value"] += f"{message.guild.get_member(combo.reserve_id).display_name} rsv. for {message.guild.get_member(combo.driver_id).display_name}\n"
      else:
        embed["fields"][0]["value"] += f"{message.guild.get_member(combo.driver_id).display_name}\n"
    else:
        embed["fields"][1]["value"] += f"{message.guild.get_member(combo.reserve_id).display_name}\n"
  
  embed["fields"][0]["value"] += f"{space_char}"
  embed["fields"][1]["value"] += f"{space_char}"

  await message.edit(embed=discord.Embed.from_dict(embed))
# end updateReservesEmbed

async def onClick(member, button):
  db = connectDatabase()
  db.cursor.execute(f"""
    INSERT INTO reserves (
      `driver_id`, `requested_id`
    ) VALUES (
      '{str(member.id) + ("1" if button == RandomSupport.WAVE_EMOJI else "0")}',
      '0'
    )
  """)
  db.connection.commit()
  db.connection.close()
# end onClick

async def onUnclick(member, button):
  db = connectDatabase()
  db.cursor.execute(f"""
    DELETE FROM reserves
    WHERE `driver_id` = '{str(member.id) + ("1" if button == RandomSupport.WAVE_EMOJI else "0")}'
  """)
  db.connection.commit()
  db.connection.close()
# end onUnclick

def getReserves():
  db = connectDatabase()
  db.cursor.execute("""
    SELECT *
    FROM reserves
  """)

  reserves = []
  for r in db.cursor:
    reserves.append(Reserve(*r))
  reserves.sort(key=lambda r:r.date)

  db.connection.close()
  return reserves
# end getReserves


''' SUPPORT '''
def connectDatabase():
  return MoBotDatabase.connectDatabase("Grotti F1")
# end connectDatabase

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('cotmS4_client_secret.json'), scope) # yes i know im using COTM secret for another event
  clientSS = gspread.authorize(creds)  
  season_4_key = "1GRMcntFXVqNnuwhTyTYvODreE_t8rpcrlNFULR_KuG8"
  workbook = clientSS.open_by_key(season_4_key)
  return workbook
# end openSpreadsheet