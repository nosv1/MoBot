import discord
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup as bSoup
import requests
import feedparser
import os

moBot = 449247895858970624
officialServer = 298938326306521098
pcF9 = 592086506068377624

spreadsheetKeys = {
 "pc" : {
   "eu" : {
     "f9" : "1KNXakJhzAwfA8p1N-_X0J-zregWANH3alUxWPGkokQc"
    },
   "america" : {
     "f2" : "14YQLkU7C8IuyLJXVZ9IIJZuYhnp5ezsZkeeyI-NUkQQ",
    }
  }
}

flags = {
  "AM" : "🇦🇲",
  "AR" : "🇦🇷",
  "AT" : "",
  "AU" : "",
  "BA" : "",
  "BD" : "",
  "BE" : "",
  "BG" : "",
  "BH" : "",
  "BO" : "",
  "BR" : "🇧🇷",
  "BY" : "",
  "CA" : "🇨🇦",
  "CH" : "",
  "CL" : "🇨🇱",
  "CN" : "",
  "CO" : "",
  "CY" : "",
  "CZ" : "",
  "DE" : "🇩🇪",
  "DK" : "🇩🇰",
  "DZ" : "",
  "EE" : "",
  "ENGLAND" : "",
  "ES" : "🇪🇸",
  "EUROPEANUNION" : "",
  "FI" : "",
  "FR" : "",
  "GB" : "🇬🇧",
  "GE" : "",
  "GI" : "",
  "GR" : "🇬🇷",
  "HK" : "",
  "HR" : "🇭🇷",
  "HU" : "🇭🇺",
  "IE" : "",
  "IL" : "",
  "IN" : "",
  "IS" : "",
  "IT" : "",
  "JM" : "",
  "JP" : "",
  "KR" : "",
  "LB" : "",
  "LT" : "",
  "LU" : "",
  "LV" : "",
  "MA" : "",
  "MC" : "",
  "ME" : "",
  "MK" : "",
  "MT" : "",
  "MX" : "",
  "MY" : "",
  "NL" : "🇳🇱",
  "NO" : "",
  "NORTHERN-IRELAND" : "",
  "NZ" : "",
  "PK" : "",
  "PL" : "🇵🇱",
  "PR" : "🇵🇷",
  "PT" : "",
  "RO" : "",
  "RS" : "🇷🇸",
  "RU" : "🇷🇺",
  "SCOTLAND" : "",
  "SE" : "",
  "SG" : "",
  "SI" : "",
  "SK" : "",
  "SO" : "",
  "TH" : "",
  "TR" : "",
  "UA" : "",
  "US" : "🇺🇸",
  "VE" : "",
  "WALES" : "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
  "ZA" : "",
}

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (str(moBot) in args[0]):
    if (message.guild.id == officialServer):
      if (args[1].lower() == "aor"):
        if ("add game emojis" in message.content):
          await addGameEmojis(message)  
# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def addGameEmojis(message):
  directory = os.fsencode("C:/Users/Owner/Desktop/AOR Emojis/Games")
  for file in os.listdir(directory):
    filename = os.fsdecode(file)
    image = open(os.fsdecode(directory) + "/" + filename, "rb")
    f = image.read()
    b = bytearray(f)
    emoji = await message.guild.create_custom_emoji(name=filename.split(".")[0], image=b)
    emojiImage = "<:" + emoji.name + ":" + str(emoji.id) + ">"
    await message.channel.send(emoji.name + " -> " + emojiImage)

async def udpateRSSChannel(client):
  channel = client.get_guild(467239192007671818).get_channel(547274914319826944)
  
  embed = discord.Embed()
  url = "https://apexonlineracing.com/community/forums/aor-pc-f9-league-season-18.1535/index.rss"
  feed = feedparser.parse(url)
  '''for c in str(feed.entries):
    try:
      print (c, end="")
    except:
      pass
  return'''
  for entry in feed.entries:
    fieldName = entry.title
    fieldValue = entry.summary[:1024]
    embed.add_field(name=fieldName, value=fieldValue, inline=False)
    await channel.send(embed=embed)
    break
# end udpateRSSChannel

async def getStandings(message):
  await message.channel.trigger_typing()

  platform = "pc"
  region = "eu"
  split = "f9"
  url = "https://docs.google.com/spreadsheets/d/" + spreadsheetKeys[platform][region][split] + "/pubhtml?hl=en&widget=false&headers=false"
  standingsTable = await getSpreadsheet(platform, region, split, url)

  embed = discord.Embed(color=int("0xc71c0a", 16))
  embed.set_author(name=platform.upper() + " " + region.upper() + " " + split.upper(), url=url)

  value = ""
  for i in range(len(standingsTable)):
    try:
      value += standingsTable[i][0] + ". "
      try:
        value += flags[standingsTable[i][1].split("flags/")[1].upper()]
      except KeyError:
        pass
      value += " **" + standingsTable[i][2] + "** - " + standingsTable[i][-5] + "\n"
    except IndexError:
      pass
  value += "__[League Results](" + url + ")__"
  embed.add_field(name="Driver Standings", value=value)

  await message.channel.send(embed=embed)
# end getStandings

async def getSpreadsheet(platform, region, split, url):  
  soup = bSoup(requests.get(url).text, "html.parser")
  rows = soup.findAll("tr")
  table = []
  for i in range(5, 25):
    columns = str(rows[i]).split("<td")
    j = len(columns) - 1
    while j > 31:
      del columns[j]
      j -= 1
    del columns[0:2]
    for j in range(len(columns)):
      columns[j] = columns[j].split("</td")[0].split(".png")[0].split("\">")[-1]
    table.append(columns)
  return table
# end getSpreadsheet
