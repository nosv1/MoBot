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

# USER IDs
moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

# GTA V/Online Vehicle Info, Lap Times, and Top Speeds -- SHEET IDs
KEY_VEHICLE_INFO_SHEET_ID = 1689972026
HANDLING_DATA_BASIC_SHEET_ID = 110431106
OVERALL_LAP_TIME_SHEET_ID = 60309153

space_char = "⠀"

car_classes = { # Spreadsheet Class : broughy website class
  "Supers" : "supers",
  "Sports" : "sports",
  "Muscle" : "muscle",
  "Sports Classics" : "classics",
  "Coupes" : "coupes",
  "Sedans" : "sedans",
  "SUVs" : "suvs",
  "Compacts" : "compacts",
  "Vans" : "vans",
  "Off-Road" : "offroads",
}

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
    car_classes_keys = list(car_classes.keys())
    car_class = car_classes_keys[random.randint(0, len(car_classes_keys)-1)]
    car_tiers = getTiers(car_class)

    car_tiers_keys = list(car_tiers.keys())
    car_tier = car_tiers_keys[random.randint(0, len(car_tiers_keys)-1)]
    car = car_tiers[car_tier][random.randint(0, len(car_tier)-1)]

    # get track
    i = random.randint(0, len(tracks)-1)
    job = tracks[i][0]
    link = plat_sheet.cell(job.row, job.col, value_render_option='FORMULA').value.split('"')[1]
    job = job.value

    s = f"**__Race Generated__**\nPlatform: **{platform.title()}**\nClass: **{car_class}**\nTier: **{car_tier}**\nVehicle: **{car}**\nTrack: **{job}**\nLink: <{link}>\n\nTracks from GTACCHub Catalogue - <https://bit.ly/cchubCatalogue>\nCars from Broughy1322 Spreadsheet - <https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4/edit#gid=999161401>\n\n*You can edit ur message, and it'll do the command again, plz don't spam... like really, don't spam it."
    if refresh:
      await message.edit(content=s)
    else:
      msg = await message.channel.send(s)
      #await msg.add_reaction(RandomSupport.COUNTER_CLOCKWISE_ARROWS_EMOJI)
  except: #likely resource exhausted error
    print("CAUGHT EXCEPTION")
    print(traceback.format_exc)
    await message.channel.send("There were technical difficulties generating your race. Please try again in a minute or so.")
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


async def handleUserVehicleInput(message, client):
  moBotMember = message.guild.get_member(moBot) # used for role color

  embed = discord.Embed() # make base embed
  embed.set_author(name="GTA V Vehicle Search", url=f"https://google.com/vehicle=None/{'/'.join(f'tier_{c}=None' for c in 'SABCDEFGHIJ')}/", icon_url=moBotMember.avatar_url)
  embed.color = moBotMember.roles[-1].color

  vehicle = message.content.split("car ")[1].strip() # get vehicle update user on status
  embed.description = f"Searching for `{vehicle}`..."
  embed = RandomSupport.updateDetailInURL(embed, "vehicle", vehicle)
  msg = await message.channel.send(embed=embed)

  vehicles = []
  try: # search for possible vehicles

    workbook = openSpreadsheet()
    sheets = workbook.worksheets()
    key_vehicle_info_sheet = [sheet for sheet in sheets if sheet.id == KEY_VEHICLE_INFO_SHEET_ID][0]
    handling_data_basic_info_sheet = [sheet for sheet in sheets if sheet.id == HANDLING_DATA_BASIC_SHEET_ID][0]
    overall_lap_time_sheet = [sheet for sheet in sheets if sheet.id == OVERALL_LAP_TIME_SHEET_ID][0]

    poss_vehicles = searchVehicle(key_vehicle_info_sheet, vehicle)
    if poss_vehicles:
      vehicles = getVehicleInfo(
        key_vehicle_info_sheet, 
        handling_data_basic_info_sheet, 
        overall_lap_time_sheet,
        [Vehicle(v) for v in poss_vehicles[:9]]
      ) # list of complete vehicle objects, just waiting for user selection now
  except: # likely issue with gspread
    print("CAUGHT EXCEPTION")
    print(traceback.format_exc())
    embed.description = "There were technical difficulties searching for your vehicle. Please try again in a minute or so."
    await msg.edit(embed=embed)
    return

  if vehicles: # ask user which vehicle is correct
    emojis = []

    embed.description = "**Which Vehicle?**\n"
    for i, v in enumerate(poss_vehicles[:9]):
      e = RandomSupport.numberEmojis[i+1]
      embed.description += f"{e} {v}\n"
      emojis.append(e)

    if emojis[1:]: # if more than one option get selection from user
      for e in emojis:
        await msg.add_reaction(e)
      await msg.edit(embed=embed)

      try: # handle user selection
        def check(payload):
          return payload.user_id == message.author.id and payload.emoji.name in emojis

        payload = await client.wait_for("raw_reaction_add", timeout=60.0, check=check)
        await msg.clear_reactions()
        vehicle = vehicles[emojis.index(payload.emoji.name)]
      except asyncio.TimeoutError:
        embed.description += "\n\n**TIMED OUT WAITING FOR USER INPUT**"
        await msg.clear_reactions()
        await msg.edit(embed=embed)
        return 

    else:
      vehicle = vehicles[0]

    embed = RandomSupport.updateDetailInURL(embed, "vehicle", vehicle._Vehicle)

    wiki_urls = getVehicleImage(vehicle)
    try:
      embed.set_thumbnail(url=wiki_urls["image_url"])
    except: # not sure what could go wrong here... may not find correct page i guess
      print("CAUGHT EXCEPTION")
      print(traceback.format_exc())

    embed.description = f"**Vehicle:** {vehicle._Vehicle} - [__wiki__]({wiki_urls['wiki_url']})\n"
    embed.description += f"**Class:** {vehicle._Class}\n"
    embed.description += f"[__Overall (Lap Time)__](https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4/edit#gid=60309153&range=B{vehicle._overall_lap_time_row}) - "
    embed.description += f"[__Key Info__](https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4/edit#gid=1689972026&range=B{vehicle._key_info_row}) - "
    embed.description += f"[__Handling Data (Basic)__](https://docs.google.com/spreadsheets/d/1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4/edit#gid=110431106&range=D{vehicle._handling_data_basic_row})\n{space_char}\n"

    v = ""
    v += f"**Drivetrain:** {vehicle._Drivetrain}\n"
    v += f"**Seats:** {vehicle._Seats}\n"
    v += f"**Source:** {vehicle._Source}\n"
    v += f"**Cost:** {vehicle._Cost}\n"
    embed.add_field(name="**__Basic Information__**", value=f"{v}{space_char}")

    v = ""
    v += f"**Race Tier:** {vehicle._Race_Tier}\n"
    v += f"**Lap Time:** {vehicle._Lap_Time__m_ss_000_}\n"
    v += f"**Top Speed:** {vehicle._Top_Speed__mph_}\n"
    embed.add_field(name="**__Basic Performance__**", value=f"{v}{space_char}")

    v = ""
    v += f"**Spoiler:** {vehicle._Spoiler}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Tyres Clip:** {vehicle._Tyres_Clip}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Bouncy:** {vehicle._Bouncy}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Engine:** {vehicle._Engine}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    embed.add_field(name="**__Features / AHF Issues__**", value=f"{v}{space_char}")

    embed.set_footer(text="All information is retrieved from Broughy's Spreadsheet, \"GTA V/Online Vehicle Info, Lap Times, and Top Speeds\". Information may not be absolutely accurate.")
    try:
      await msg.edit(embed=embed)
    except discord.errors.HTTPException: # bad thumbnail
      embed = embed.to_dict()
      del embed["thumbnail"]
      await msg.edit(embed=discord.Embed.from_dict(embed))

    # add tier lists to url
    tiers = getTiers(vehicle._Class)
    for tier in tiers:
      detail = f"tier_{tier}"
      value = '&'.join(tiers[tier])
      embed = RandomSupport.updateDetailInURL(embed, detail, value)
      await msg.add_reaction(RandomSupport.letter_emojis[tier.lower()])
    await msg.edit(embed=embed)

  else:
    embed.description = f"No vehicles with a name close to `{vehicle}` could be found."
    await msg.edit(embed=embed)
# end handleUserVehicleInput

def getVehicleImage(vehicle):
  session = HTMLSession()
  url = f"https://gta.fandom.com/wiki/{vehicle._Vehicle.replace(' ', '_')}"
  r = session.get(url)
  image_url = r.html.html.split("image image-thumbnail")[1].split("src=\"")[1].split("\"")[0]
  return {"wiki_url" : url, "image_url" : image_url}
# end getVehicleImage

def getVehicleInfo(key_vehicle_info_sheet, handling_data_basic_info_sheet, overall_lap_time_sheet, vehicles):
  key_info_range = key_vehicle_info_sheet.range(f"A2:J{key_vehicle_info_sheet.row_count}")
  handling_data_basic_range = handling_data_basic_info_sheet.range(f"A2:R{handling_data_basic_info_sheet.row_count}")
  overall_lap_time_range = overall_lap_time_sheet.range(f"A2:F{overall_lap_time_sheet.row_count}")

  key_info = RandomSupport.arrayFromRange(key_info_range)
  key_info[1][0].value = "Class"
  key_info[1][1].value = "Vehicle"

  handling_data_basic_info = RandomSupport.arrayFromRange(handling_data_basic_range)
  handling_data_basic_info[1][0].value = "Class"
  handling_data_basic_info[1][1].value = "Vehicle"

  overall_lap_time_info = RandomSupport.arrayFromRange(overall_lap_time_range)
  overall_lap_time_info[0][0].value = "Overall Position"
  overall_lap_time_info[0][1].value = "In Class Position"

  def fix_attr(attr):
    return re.sub(r"[\s\-\(\):.]", "_", attr)

  for i, attr in enumerate(
    key_info[1] + 
    handling_data_basic_info[1] +
    overall_lap_time_info[0]
  ): # add attributes to class
    if attr.value.strip() != "":
      attr = fix_attr(attr.value)
      exec(f"Vehicle._{attr} = None")
  Vehicle._key_info_row = None
  Vehicle._handling_data_basic_row = None
  Vehicle._overall_lap_time_row = None

  for vehicle in vehicles:

    for i, v in enumerate(key_info):
      if v[1].value == vehicle._name:
        for j, prop in enumerate(key_info[i]):
          attr = fix_attr(key_info[1][j].value)
          exec(f'vehicle._{attr} = "{prop.value}"')
        vehicle._key_info_row = i + 2 # + 2 is for headers

    for i, v in enumerate(handling_data_basic_info):
      if v[1].value == vehicle._name:
        for j, prop in enumerate(handling_data_basic_info[i]):
          attr = fix_attr(handling_data_basic_info[1][j].value)
          exec(f'vehicle._{attr} = "{prop.value}"')
        vehicle._handling_data_basic_row = i + 2 # + 2 is for headers

    for i, v in enumerate(overall_lap_time_info):
      if v[3].value == vehicle._name:
        for j, prop in enumerate(overall_lap_time_info[i]):
          attr = fix_attr(overall_lap_time_info[0][j].value)
          exec(f'vehicle._{attr} = "{prop.value}"')
        vehicle._overall_lap_time_row = i + 2 # + 2 is for headers

  return vehicles
# end getVehicleInfo

def searchVehicle(key_vehicle_info_sheet, vehicle):
  vehicle_names = key_vehicle_info_sheet.range(f"B4:B{key_vehicle_info_sheet.row_count}")
  poss_vehicles = get_close_matches(vehicle.lower(), [v.value.lower() for v in vehicle_names])

  for i, pv in enumerate(poss_vehicles): # fix vehicle names to be proper
    for v in vehicle_names:
      if pv == v.value.lower():
        poss_vehicles[i] = v.value
  return poss_vehicles
# end searchVehicle


async def toggleTierList(message, tier, toggle):
  url_tier = f"tier_{tier.upper()}"
  embed = message.embeds[0]
  cars = "\n".join(RandomSupport.getDetailFromURL(embed.author.url, url_tier).split("&"))
  
  tier_name = f"{tier.upper()} Tier"
  check = RandomSupport.getValueFromField(embed, tier_name)
  if not check: # not check is True if tier is not present
    if toggle == "add":
      embed.add_field(name=f"**__{tier_name}__**", value=cars)
      await message.edit(embed=embed)

  elif toggle == "remove":
    embed = embed.to_dict()
    for i, field in enumerate(embed["fields"]):
      if tier_name in embed["fields"][i]["name"]:
        del embed["fields"][i]
        break
    await message.edit(embed=discord.Embed.from_dict(embed))
# end toggleTierList

def getTiers(car_class):

  url = f"https://broughy.com/gta5{car_classes[car_class]}"
  soup = bsoup(requests.get(url).text, "html.parser")
  tier_lists = str(soup).split("<strong>")[1:]
  tier_lists = [t.split("</div>")[0] for t in tier_lists]
  tiers = {}
  for t in tier_lists:
    tier = t.split("</")[0]
    cars = t.split("<br/>")
    cars[-1] = cars[-1].split("</p>")[0]
    cars[0] = cars[0].split(">")[-1]
    tiers[tier] = cars

  # tiers = {S : [car1, car2...], A : []}
  return tiers
# end getTier

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)
  workbook = clientSS.open_by_key("1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4")
  return workbook
# end openSpreadsheet