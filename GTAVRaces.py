import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import traceback
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bsoup
import requests
import random

import SecretStuff
import MoBotDatabase
import RandomSupport

import GTACCHub
import GTAVehicles

# USER IDs
moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

# GTA V/Online Vehicle Info, Lap Times, and Top Speeds -- SHEET IDs
KEY_VEHICLE_INFO_SHEET_ID = 1689972026
HANDLING_DATA_BASIC_SHEET_ID = 110431106
OVERALL_LAP_TIME_SHEET_ID = 60309153

space_char = "⠀"

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

async def generateRandomRace(message, args, refresh):
  await message.channel.trigger_typing()

  platform = args[-1].lower()
  if platform not in ["xbox", "ps", "pc"]:
    await message.channel.send("**Platform not found.**\n\n`@MoBot#0697 gtarace random <xbox, ps, pc>`\n`@MoBot#0697 gtarace random xbox`")
    return

  try:
    cars = getCars()
    tracks, plat_sheet = getTracks(platform) # tracks are cells [[track, job_type], [track, job_type]]

    # get car
    car_classes_keys = list(GTAVehicles.car_classes.keys())
    car_class = car_classes_keys[random.randint(0, len(car_classes_keys)-1)]
    car_tiers = GTAVehicles.getTiers(car_class)

    car_tiers_keys = list(car_tiers.keys())
    car_tier = car_tiers_keys[random.randint(0, len(car_tiers_keys)-1)]
    car = car_tiers[car_tier][random.randint(0, len(car_tier)-1)]

    # get track
    i = random.randint(0, len(tracks)-1)
    job = tracks[i][0]
    try:
      link = plat_sheet.cell(job.row, job.col, value_render_option='FORMULA').value.split('"')[1]
    except IndexError:
      link = "Unknown"
    job = job.value
    job_type = {"R" : "Regular Racing Circuit", "O" : "Off-Road/Rally/RallyX Circuit", "T" : "Themed Circuit (Stunt/Challenge/Transform)", "" : ""}[tracks[i][1].value.upper()]

    s = f"Class: **{car_class}**\nTier: **{car_tier}**\nVehicle: **{car}**\nTrack: **{job}**\nType: **{job_type}**\nLink: <{link}>\n\nTracks - <https://bit.ly/cchubCatalogue>\nCars - <https://bit.ly/3fGklW8>\n\n*You can edit ur message, and it'll do the command again, plz don't spam... like really, don't spam it.*"
    if refresh:
      await message.edit(content=s)
    else:
      msg = await message.channel.send(s)
      #await msg.add_reaction(RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI)
  except gspread.exceptions.APIError:
    await message.channel.send("There were technical difficulties generating your race. Please try again in a minute or so.")
  except: # who knows
    print("CAUGHT EXCEPTION")
    print(traceback.format_exc())
# end generateRandomRace

def getCars():
  workbook = openSpreadsheet()
  sheets = workbook.worksheets()
  key_vehicle_info_sheet = [sheet for sheet in sheets if sheet.id == KEY_VEHICLE_INFO_SHEET_ID][0]
  vehicle_names = key_vehicle_info_sheet.range(f"B4:B{key_vehicle_info_sheet.row_count}")
  return [cell.value for cell in vehicle_names if cell.value != ""]
# end getCars

def getTracks(platform):
  workbook = GTACCHub.openSpreadsheet()
  sheets = workbook.worksheets()

  plat_sheet = None
  if (platform == "xbox"):
    plat_sheet = [sheet for sheet in sheets if sheet.id == GTACCHub.XBOX_SHEET_ID][0]
  elif (platform == "ps"):
    plat_sheet = [sheet for sheet in sheets if sheet.id == GTACCHub.PS_SHEET_ID][0]
  elif (platform == "pc"):
    plat_sheet = [sheet for sheet in sheets if sheet.id == GTACCHub.PC_SHEET_ID][0]

  jobs_and_types = plat_sheet.range(f"A12:B{plat_sheet.row_count-1}")
  jobs_and_types = RandomSupport.arrayFromRange(jobs_and_types)
  i = 0
  while i > -1:
    if (
      jobs_and_types[i][0].value == "" or 
      len(jobs_and_types[i][0].value == 1) or 
      "Jobs by" in jobs_and_types[i][0].value or
      "N" in jobs_and_types[i][1].value
    ):
      del jobs_and_types[i]
    i -= 1

  return [jobs_and_types, plat_sheet]
# end getTracks

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)
  workbook = clientSS.open_by_key("1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4")
  return workbook
# end openSpreadsheet