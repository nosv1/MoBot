import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import RLRanks

import SecretStuff
import MoBotDatabase

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

spaceChar = "⠀"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if (str(moBot) in args[0]):
    if (args[1].lower() == "dsn"):
      await sendDSN(message, args)
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

async def sendDSN(message, args):
  await message.channel.trigger_typing()

  platform = args[2].replace("pc", "steam")
  playerID = " ".join(args[3:]).strip()
  trackerURL = "No URL Available"
  mmrs, trackerURL = RLRanks.getMMRs(platform, playerID)
  platform = trackerURL.split("/")[-2]
  trackerID = trackerURL.split("/")[-1]
  dsn = getDSN(mmrs)
  try:
    mmrs, trackerURL = RLRanks.getMMRs(platform, playerID)
    platform = trackerURL.split("/")[-2]
    trackerID = trackerURL.split("/")[-1]
    dsn = getDSN(mmrs)
  except: # any errors should mean the id doesn't exist
    await message.channel.send("**Something went wrong... Is the ID correct?**\n`@MoBot#0697 dsn steam/xbox/ps id`\n`@MoBot#0697 dsn xbox Mo v0`")
    return

  if (dsn is None):
    await message.channel.send("**Not enough MMRs to calculate DSN.**\n<%s>" % trackerURL)
    return

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(
    name="Designated Skill Number", 
    url="https://google.com/ogMessageID=%s/memberID=%s/playerID=%s/platform=%s/trackerID=%s/dsn=%s/" % (
      message.id,
      message.author.id, 
      playerID.replace(" ", "%20"),
      platform,
      trackerID,
      dsn.dsn if dsn.dsn >= 0 else "Invalid"
    ), 
    icon_url=message.guild.icon_url
  )

  description = "ID: `%s`\n" % playerID
  description += "Platform: `%s`\n\n" % platform

  description += "**Games Played (1s, 2s, 3s):**\n"
  for season in list(mmrs.keys())[:3]:
    games_played = []
    for mode in mmrs[season]:
      games_played.append(str(mmrs[season][mode]["games"]))
    description += "Season %s: `%s`\n" % (season, ", ".join(games_played))
  description += "\n"

  description += "**MMRs:**\n"
  description += "Season %s %ss: `%s`\n" % (
    dsn.first_peak.season, 
    dsn.first_peak.mode, 
    dsn.first_peak.mmr
  )
  description += "Season %s %ss: `%s`\n\n" % (
    dsn.second_peak.season, 
    dsn.second_peak.mode,
    dsn.second_peak.mmr
  )

  description += "**DSN: `%s`**\n" % (dsn.dsn if dsn.dsn >= 0 else "Invalid")
  description += "[__Tracker__](%s)" % trackerURL
  embed.description = description

  msg = await message.channel.send(embed=embed)
# end sendDSN

def getDSN(mmrs): # mmrs are got from rlranks.getMMRs(platform, id)
  class DSN:
    def __init__(self):
      self.first_peak = MMR(0, 0, 0) # from last 3 seasons "13, 12, 11", 2s or 3s
      self.second_peak = MMR(0, 0, 0)

      self.dsn = 0
  # end DSN

  class MMR:
    def __init__(self, mmr, season, mode):
      self.mmr = mmr
      self.season = season
      self.mode = mode
  # end MMR
  
  dsn = DSN()
  seasons = list(mmrs.keys())

  '''
  dsn = 
  75% of first peak 3s or 2s from last 3 seasons +
  25% of second peak 3s or 2s from last 3 seasons
  '''

  def getPeaks(): # 1st and 2nd highest peaks across last 3 seasons, 2s or 3s
    peaks = [0, 0]
    for rank in [1, 2]: # 1st highest, 2nd highest
      temp_peak = MMR(0, 0, 0)
      for mode in [2, 3]: # 2s, 3s
        for season in seasons[:3]: # last 3 seasons
          mmr = MMR(
            mmrs[seasons[0]][mode]["peak" if season == seasons[0] else "current"], seasons[0], 
            mode
          )
          if rank == 1:
            if mmr.mmr > temp_peak.mmr:
              temp_peak = mmr
          elif rank == 2:
            if mmr.mmr > temp_peak.mmr and (mmr.mmr < peaks[0].mmr or peaks[0].mmr == 0):
              temp_peak = mmr

      peaks[rank-1] = temp_peak
    return peaks[0], peaks[1]
  # end getPeak

  dsn.first_peak, dsn.second_peak = getPeaks()

  if 0 not in [dsn.first_peak.mmr, dsn.second_peak.mmr]:
    dsn.dsn = dsn.first_peak.mmr * .75 + dsn.second_peak.mmr * .25
  else:
    dsn.dsn = -1

  return dsn
# end getDSN