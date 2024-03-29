import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
from difflib import get_close_matches
import traceback
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup as bsoup
import requests

import SecretStuff
import MoBotDatabase
import RandomSupport

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
  "Open Wheel" : "openwheels",
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

class_aliases = [
  ["Compacts", "comapact"],
  ["Coupes", "coupe"],
  ["motorcycle"],
  ["Muscle"],
  ["Off-Road", "offroad"],
  ["Open Wheel", "openwheel"],
  ["Sedans", "sedan"],
  ["Sports", "sport"],
  ["Sports Classics", "sports classic", "sportsclassics"],
  ["Supers", "super"],
  ["SUVs", "suv"],
  ["Vans", "van"],
]

class Vehicle: # attributes are being added in functions
  def __init__(self, name):
    self._name = name
  pass
# end Vehicle

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def mainReactionAdd(message, payload, client): 
  letter_emojis = list(RandomSupport.letter_emojis.values())
  symbol_emojis = list(RandomSupport.symbol_emojis.values())
  if payload.emoji.name in letter_emojis + symbol_emojis:
    try:
      char_clicked = list(RandomSupport.letter_emojis.keys())[letter_emojis.index(payload.emoji.name)]
    except ValueError:
      char_clicked = list(RandomSupport.symbol_emojis.keys())[symbol_emojis.index(payload.emoji.name)]
    await toggleTierList(message, char_clicked, "add")
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  letter_emojis = list(RandomSupport.letter_emojis.values())
  symbol_emojis = list(RandomSupport.symbol_emojis.values())
  if payload.emoji.name in letter_emojis + symbol_emojis:
    try:
      char_clicked = list(RandomSupport.letter_emojis.keys())[letter_emojis.index(payload.emoji.name)]
    except ValueError:
      char_clicked = list(RandomSupport.symbol_emojis.keys())[symbol_emojis.index(payload.emoji.name)]
    await toggleTierList(message, char_clicked, "remove")
# end mainReactionRemove

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberRemove



async def handleUserVehicleInput(message, client):
  moBotMember = message.guild.get_member(moBot) # used for role color

  embed = discord.Embed() # make base embed
  embed.set_author(name="GTA V Vehicle Search", url=f"https://google.com/vehicle=None/{'/'.join(f'tier_{c}=None' for c in '+SABCDEFGHIJ')}/", icon_url=moBotMember.avatar_url)
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
    
    key_info_range = key_vehicle_info_sheet.range(f"A2:M{key_vehicle_info_sheet.row_count}")
    handling_data_basic_range = handling_data_basic_info_sheet.range(f"A2:T{handling_data_basic_info_sheet.row_count}")
    overall_lap_time_range = overall_lap_time_sheet.range(f"A2:F{overall_lap_time_sheet.row_count}")

    poss_vehicles = searchVehicle(key_vehicle_info_sheet, vehicle)
    if poss_vehicles:
      vehicles = getVehicleInfo(
        key_info_range, 
        handling_data_basic_range, 
        overall_lap_time_range,
        [Vehicle(v) for v in poss_vehicles[:9]]
      ) # list of complete vehicle objects, just waiting for user selection now
    poss_vehicles = [poss_vehicles[0]] if poss_vehicles[0].lower() == vehicle.lower() else poss_vehicles
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

    embed.description = ":boom: MoBot's GTA functions are being depreciated in the winter. Invite the bot version of [GTALens](https://discord.com/api/oauth2/authorize?client_id=872899427457716234&permissions=36507511808&scope=bot) for similar functionailty (tracks/cars/weather... - `.lens help`).\n\n"

    embed.description += f"**Vehicle:** {vehicle._Vehicle} - [__wiki__]({wiki_urls['wiki_url']})\n"
    embed.description += f"**Manufacturer:** {vehicle._Manufacturer}\n"
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
    v += f"**Off-Roads:** {vehicle._Off_Roads}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Suspension:** {vehicle._Suspension}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Boost:** {vehicle._Boost}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Drift Tyres:** {vehicle._Drift_Tyres}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    embed.add_field(name="**__Improvements__**", value=f"{v}{space_char}")

    v = ""
    v += f"**Bouncy:** {vehicle._Bouncy}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    v += f"**Engine:** {vehicle._Engine}\n".replace("✔", RandomSupport.CHECKMARK_EMOJI)
    embed.add_field(name="**__Adv. Handling Flags__**", value=f"{v}{space_char}")

    embed.set_footer(text="All information is retrieved from Broughy's Spreadsheet, \"GTA V/Online Vehicle Info, Lap Times, and Top Speeds\". Information may not be absolutely accurate.")
    try:
      await msg.edit(embed=embed)
    except discord.errors.HTTPException: # bad thumbnail
      embed = embed.to_dict()
      del embed["thumbnail"]
      await msg.edit(embed=discord.Embed.from_dict(embed))

    # add tier lists to url
    try:
      tiers = getTiersSpreadsheet(key_info_range, overall_lap_time_range, vehicle)
      for tier in tiers:
        detail = f"tier_{tier}"
        value = '&'.join(["%20".join(a) for a in tiers[tier]]) # value is Car%20Time&...
        try:
          embed = RandomSupport.updateDetailInURL(embed, detail, value)
          await msg.add_reaction(RandomSupport.letter_emojis[tier.lower()])
        except (KeyError, IndexError) as e: # S+ tier
          embed = RandomSupport.updateDetailInURL(embed, detail.replace("S+", "+"), value)
          await msg.add_reaction(RandomSupport.symbol_emojis[tier.replace("S+", "+")])
    except: # likely vehicle selected is not raceable
      print(traceback.format_exc())
      pass
    await msg.edit(embed=embed)

  else:
    embed.description = f"No vehicles with a name close to `{vehicle}` could be found."
    await msg.edit(embed=embed)
# end handleUserVehicleInput

async def displayTier(message, args):

  await message.channel.trigger_typing()
  try:

    workbook = openSpreadsheet()
    sheets = workbook.worksheets()

    key_vehicle_info_sheet = [sheet for sheet in sheets if sheet.id == KEY_VEHICLE_INFO_SHEET_ID][0]
    overall_lap_time_sheet = [sheet for sheet in sheets if sheet.id == OVERALL_LAP_TIME_SHEET_ID][0]

    key_info_range = key_vehicle_info_sheet.range(f"A2:L{key_vehicle_info_sheet.row_count}")
    overall_lap_time_range = overall_lap_time_sheet.range(f"A2:F{overall_lap_time_sheet.row_count}")
  
  except gspread.exceptions.APIError:
    await message.channel.send("There were technical difficulties getting the tier. Please try again in a mintue or so.")
    return

  exec(f"Vehicle._Class = None")
  v = Vehicle("_")
  v._Class = None
  v._Lap_Time__m_ss_000_ = "0:00.000"

  for ca in class_aliases:
    for c in ca:
      if c.lower() in " ".join(args[1:-1]).lower():
        v._Class = ca[0]

  if not v._Class:
    await message.channel.send(f"`{' '.join(args[1:-1])}` could not be found as a class alias. Edit your message, and try again.")
    return

  tiers = getTiersSpreadsheet(key_info_range, overall_lap_time_range, v)

  tier = tiers[args[-1].upper()] if args[-1].upper() in tiers else None

  if not tier:
    await message.channel.send(f"`{args[-1]}` is not a tier for {v._Class}. Edit your message, and try again.")
    return
    

  embed = discord.Embed()
  moBotMember = message.guild.get_member(moBot) # used for role color
  embed.color = moBotMember.roles[-1].color

  embed.title = f"{v._Class} {args[-1].upper()}"

  embed.description = "\n".join([f"`{getDelta(c[0], tier[0][0])}` {c[1]}" for c in tier])

  await message.channel.send(embed=embed)
# end displayTier

def getVehicleImage(vehicle):
  session = HTMLSession()
  url = f"https://gta.fandom.com/wiki/{vehicle._Vehicle.replace(' ', '_')}"
  r = session.get(url)
  try:
    image_url = r.html.html.split("pi-image-thumbnail")[0].split("image image-thumbnail")[-1].split("src=\"")[1].split("\"")[0]
  except IndexError:
    image_url = "https://google.com"
  return {"wiki_url" : url, "image_url" : image_url}
# end getVehicleImage

def getVehicleInfo(key_info_range, handling_data_basic_range, overall_lap_time_range, vehicles):

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
  cars = RandomSupport.getDetailFromURL(embed.author.url, url_tier).split("&")
  for i, car in enumerate(cars):
    car = car.split(" ")
    delta = car[0]
    car = " ".join(car[1:])
    if RandomSupport.getDetailFromURL(embed.author.url, "vehicle") == car:
      car = f"**{car}**"
    cars[i] = f"`{delta.rjust(6, ' ')}` {car}"
  cars = "\n".join(cars)
  
  tier = "S+" if tier == "+" else tier
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

def getTiersSpreadsheet(key_info_range, overall_lap_time_range, vehicle):

  key_info = RandomSupport.arrayFromRange(key_info_range)
  key_info = key_info[2:] # row 3:end

  overall_lap_times = RandomSupport.arrayFromRange(overall_lap_time_range)
  overall_lap_times = overall_lap_times[2:] # row 3:end

  # tiers = {S : [[car1, delta], ...], A : []} delta is difference between car and og vehicle
  tiers = {}
  for i in range(len(overall_lap_times)):
    if overall_lap_times[i][2].value != vehicle._Class: # class match
      continue

    for j in range(len(key_info)):
      if key_info[j][0].value != vehicle._Class: # class match
        continue

      veh_name = key_info[j][1].value
      if veh_name == overall_lap_times[i][3].value: # vehicle match
        race_tier = key_info[j][5].value
        race_tier = "S+" if race_tier == "" else race_tier
        if race_tier == "-":
          break
        if race_tier not in tiers:
          tiers[race_tier] = []
        tiers[race_tier].append([getDelta(overall_lap_times[i][4].value, vehicle._Lap_Time__m_ss_000_), veh_name])
  return tiers



def getTiersWeb(car_class):
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

def getDelta(time_1, time_2):
  def minuteToSeconds(time):
    return int(time.split(":")[0]) * 60 + float(time.split(":")[1])

  def secondsToMinute(time):
    minutes = int(time / 60)
    seconds = time - (minutes * 60)
    formatted = "+" if time > 0 else "-"
    
    if abs(minutes) > 0:
      formatted += f"{minutes}:"

    seconds = str(int(abs(seconds) * 1000)).zfill(4)
    formatted += f"{seconds[:-3]}.{seconds[-3:]}"
    return formatted
  # end secondsToMinute
  
  try:
    return secondsToMinute(round(minuteToSeconds(time_1) - minuteToSeconds(time_2), 3))
  except:
    return "TBD"
# end getDelta

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)
  workbook = clientSS.open_by_key("1nQND3ikiLzS3Ij9kuV-rVkRtoYetb79c52JWyafb4m4")
  return workbook
# end openSpreadsheet
