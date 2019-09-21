import discord
import asyncio
import sys
import os
from bs4 import BeautifulSoup as bSoup
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import operator
import copy
from difflib import get_close_matches

import RandomFunctions

spaceChar = "⠀"
CHECKMARK_EMOJI = "✅"
COUNTERCLOCKWISE_ARROWS_EMOJI = "🔄"
X_EMOJI = "❌"

adjustedDate = datetime.now() - relativedelta(months=3)
lastYear = adjustedDate.year-1
thisYear = adjustedDate.year

START_WEEK = datetime.strptime('2019-09-09', "%Y-%m-%d")
weekNumber = math.floor((datetime.today() - START_WEEK).days / 7) + 1

ABBRV_TO_LONG = {
  'ARI' : "Arizona Cardinals", 'ATL' : "Atlanta Falcons", 'BAL' : "Baltimore Ravens", 'BUF' : "Buffalo Bills", 'CAR' : "Carolina Panthers", 'CHI' : "Chicago Bears", 'CIN' : "Cincinnati Bengals", 'CLE' : "Cleveland Browns", 'DAL' : "Dallas Cowboys", 'DEN' : "Denver Broncos", 'DET' : "Detroit Lions", 'GB' : "Green Bay Packers", 'HOU' : "Houston Texans", 'IND' : "Indianapolis Colts", 'JAX' : "Jacksonville Jaguars", 'KC' : "Kansas City Chiefs", 'LAC' : "Los Angeles Chargers", 'LAR' : "Los Angeles Rams", 'MIA' : "Miami Dolphins", 'MIN' : "Minnesota Vikings", 'NE' : "New England Patriots", 'NO' : "New Orleans Saints", 'NYG' : "New York Giants", 'NYJ' : "New York Jets", 'OAK' : "Oakland Raiders", 'PHI' : "Philadelphia Eagles", 'PIT' : "Pittsburgh Steelers", 'SEA' : "Seattle Seahawks", 'SF' : "San Francisco 49ers", 'TB' : "Tampa Bay Buccaneers", 'TEN' : "Tennessee Titans", 'WAS' : "Washington Redskins"
}

SHORT_TO_ABBRV = {
  'Cowboys': 'DAL', 'Chiefs': 'KC', 'Eagles': 'PHI', 'Packers': 'GB', 'Redskins': 'WAS', 'Bills': 'BUF', 'Seahawks': 'SEA', 'Saints': 'NO', 'Patriots': 'NE', 'Falcons': 'ATL', 'Giants': 'NYG', 'Browns': 'CLE', 'Panthers': 'CAR', 'Rams': 'LAR', 'Colts': 'IND', 'Cardinals': 'ARI',
  'Bears': 'CHI', 'Ravens': 'BAL', 'Raiders': 'OAK', 'Buccaneers': 'TB', 'Broncos': 'DEN', 'Steelers': 'PIT', 'Jets': 'NYJ', 'Lions': 'DET', 'Bengals': 'CIN', 'Jaguars': 'JAX', '49ers': 'SF', 'Chargers': 'LAC', 'Dolphins': 'MIA', 'Vikings': 'MIN', 'Texans': 'HOU', 'Titans': 'TEN'
}

PLAYER_NAME_CORRECTIONS = {
  "Todd Gurley II" : "Todd Gurley", "Melvin Gordon III" : "Melvin Gordon", "Jeff Wilson Jr." : "Jeff Wilson", "Duke Johnson Jr." : "Duke Johnson", "Ronald Jones II" : "Ronald Jones", "Wayne Gallman Jr." : "Wayne Gallman", "Allen Robinson II" : "Allen Robinson", "Mark Ingram II" : "Mark Ingram ", "Will Fuller V" : "Will Fuller", "Marvin Jones Jr." : "Marvin Jones", "Gardner Minshew II" : "Gardner Minshew", "John Ross III" : "John Ross", "Willie Snead IV" : "Willie Snead", "DJ Chark Jr." : "DJ Chark", "Dwayne Haskins Jr." : "Dwayne Haskins", "Ted Ginn Jr." : "Ted Ginn", "Darrell Henderson Jr." : "Darrell Henderson", "Bennie Fowler III" : "Bennie Fowler", "Benny Snell Jr." : "Benny Snell", "Phillip Dorsett II" : "Phillip Dorsett", "Kerrith Whyte Jr." : "Kerrith Whyte", "Irv Smith Jr." : "Irv Smith" 
}

statsTables = {
  "defenseScoring" : {
    "URL" : "http://www.nfl.com/stats/categorystats?archive=false&conference=null&role=OPP&offensiveStatisticCategory=null&defensiveStatisticCategory=SCORING&season=&&YEAR&&&seasonType=REG&tabSeq=2&qualified=false&Submit=Go",
    "PAGES" : False,
    str(lastYear) : None,
    str(thisYear) : None,
  },
  "defenseOther" : {
    "URL" : "http://www.nfl.com/stats/categorystats?archive=false&conference=null&role=OPP&offensiveStatisticCategory=null&defensiveStatisticCategory=SACKS&season=&&YEAR&&&seasonType=REG&tabSeq=2&qualified=false&Submit=Go",
    "PAGES" : False,
    str(lastYear) : None,
    str(thisYear) : None,
  },
  "offenseRushing" : {
    "URL" : "http://www.nfl.com/stats/categorystats?tabSeq=0&season=&&YEAR&&&seasonType=REG&Submit=Go&experience=&archive=true&d-447263-p=&&PAGE&&&statisticCategory=RUSHING&conference=null&qualified=true",
    "PAGES" : True,
    str(lastYear) : None,
    str(thisYear) : None,
  },
  "offensePassing" : {
    "URL" : "http://www.nfl.com/stats/categorystats?tabSeq=0&season=&&YEAR&&&seasonType=REG&Submit=Go&experience=&archive=true&d-447263-p=&&PAGE&&&statisticCategory=PASSING&conference=null&qualified=true",
    "PAGES" : True,
    str(lastYear) : None,
    str(thisYear) : None,
  },
  "offenseReceiving" : {
    "URL" : "http://www.nfl.com/stats/categorystats?tabSeq=0&season=&&YEAR&&&seasonType=REG&Submit=Go&experience=&archive=true&d-447263-p=&&PAGE&&&statisticCategory=RECEIVING&conference=null&qualified=true",
    "PAGES" : True,
    str(lastYear) : None,
    str(thisYear) : None,
  },
  "offenseScoring" : {
    "URL" : "http://www.nfl.com/stats/categorystats?tabSeq=0&season=&&YEAR&&&seasonType=REG&Submit=Go&experience=&archive=false&d-447263-p=&&PAGE&&&statisticCategory=SCORING&conference=null&qualified=true",
    "PAGES" : True,
    str(lastYear) : None,
    str(thisYear) : None,
  },
}

playerNamesToIDs = {} # used to search when getting player limitations and must haves

class Player:
  def __init__(self, name, id, pos, fpos, price, game, team, appg):
    self.name = name.strip()
    self.id = id
    self.pos = pos
    self.fpos = fpos
    self.price = int(price)
    self.team = team
    self.value = 0 # will be updated after player values are gathered
    self.valuePerDollar = 0 # will be updated after player values are gathered
    self.appg = appg
    self.game = game
# end Player

class DefenseScoringStatsPerGame:
  def __init__(self, games, points, pkfgReturnTD, interceptionReturnTD, fumbleReturnTD, blkPntFgReturnTD, safety, twoPtReturn):
    self.points = (points / games) 
    self.pkfgReturnTD = (pkfgReturnTD / games)
    self.interceptionReturnTD  = (interceptionReturnTD / games)
    self.fumbleReturnTD = (fumbleReturnTD / games)
    self.blkPntFgReturnTD = (blkPntFgReturnTD / games)
    self.safety = (safety / games)
    self.twoPtReturn = (twoPtReturn / games)
# end DefenseScoringStatsPerGame

class DefenseOtherStatsPerGame:
  def __init__(self, games, sacks, interceptions, fumbleRecoveries):
    self.sacks = (sacks / games)
    self.interceptions = (interceptions / games)
    self.fumbleRecoveries = (fumbleRecoveries / games)
# end otherStats

class OffensePassingStatsPerGame:
  def __init__(self, totalYards, passingTDs, passingYards, interceptions):
    try:
      games = round(totalYards / passingYards)
    except ZeroDivisionError:
      games = 1
    self.passingTDs = (passingTDs / games) * (games // 2)
    self.passingYards = passingYards * (games // 2)
    self.interceptions = (interceptions / games) * (games // 2)
# end OffensePassingStatsPerGame

class OffenseRushingStatsPerGame:
  def __init__(self, totalYards, rushingTDs, rushingYards, fumbles):
    try:
      games = round(totalYards / rushingYards)
    except ZeroDivisionError:
      games = 1
    self.rushingTDs = (rushingTDs / games) * (games // 2)
    self.rushingYards = rushingYards * (games // 2)
    self.fumbles = (fumbles / games) * (games // 2)
# end OffenseRushingStatsPerGame

class OffenseReceivingStatsPerGame:
  def __init__(self, totalYards, receivingTDs, receivingYards, receptions):
    try:
      games = round(totalYards / receivingYards)
    except ZeroDivisionError:
      games = 1
    self.receivingTDs = (receivingTDs / games) * (games // 2)
    self.receivingYards = receivingYards * (games // 2)
    self.receptions = (receptions / games) * (games // 2)
# end OffenseReceivingStatsPerGame

class OffenseScoringStatsPerGame:
  def __init__(self, points, totalPoints, pkfgReturnTDs, twoPtConversions, fumbleReturnTDs):
    games = (totalPoints / points)
    self.pkfgReturnTDs = (pkfgReturnTDs / games) * (games // 2)
    self.twoPtConversions = (twoPtConversions / games) * (games // 2)
    self.fumbleReturnTDs = (fumbleReturnTDs / games) * (games // 2)
# end OffenseScoringStatsPerGame

async def main(args, message, client):

  global statsTables

  embed = discord.Embed(
    color=int("0xF39343", 16),
    footer=("Stats After Week %d - Lineups For Week %d" % (weekNumber, weekNumber+1))
  )
  embed.set_author(name="DraftKings Lineup Generator", icon_url="https://i.gyazo.com/48378c434886d1fa6bf1af6197ff3f32.png")
  embed.add_field(name="Slate:", value=spaceChar, inline=True)
  embed.add_field(name="Lineup Type:", value=spaceChar, inline=True)
  embed.add_field(name="Lineup Style:", value=spaceChar, inline=True)
  embed.add_field(name="Player Limitations:", value=spaceChar, inline=True)
  embed.add_field(name="Must Haves:", value=spaceChar, inline=True)
  embed.add_field(name="Lineup:", value=spaceChar, inline=False)
  embed.set_footer(text="REM. SALARY: TBD TOTAL FPPG: TBD")
  embed = embed.to_dict()
  moBotMessage = await message.channel.send(embed=discord.Embed.from_dict(embed))
  
  salaries = open(await getFile(message.author, moBotMessage, embed, client), "r")
  players = getPlayersFromSalaries(salaries)

  statsTables = await getStatsTables(moBotMessage, embed, statsTables)

  embed["description"] = "*Calculating Player Values*"
  await editEmbed(moBotMessage, embed)
  for player in players:
    player = players[player]
    playerNamesToIDs[player.name] = player.id
    pos = player.pos

    if (pos == "DST"):
      lastYearStats, thisYearStats = getDefenseStats(player.name, "DEFENSE", lastYear), getDefenseStats(player.name, "DEFENSE", thisYear)
      player.value = getPlayerValueByCombiningStats(lastYearStats, thisYearStats, weekNumber)
      player.valuePerDollar = player.value / player.price
    else:
      lastYearStats, thisYearStats = getOffenseStats(player.name, "OFFENSE", lastYear), getOffenseStats(player.name, "OFFENSE", thisYear)
      player.value = getPlayerValueByCombiningStats(lastYearStats, thisYearStats, weekNumber)
      player.valuePerDollar = player.value / player.price

  lineupType = await getLineupType(message.author, moBotMessage, embed, client)
  playerLimitations = await getRestrictions([], 3, message.author, moBotMessage, embed, client)
  mustHaves = await getRestrictions([], 4, message.author, moBotMessage, embed, client)
  while True:
    valueListOption = await getLineupStyle(message.author, moBotMessage, embed, client)
    valueList = getValueList(players, valueListOption)
    await printValueList(valueList, None, moBotMessage)

    embed["description"] = "*Creating Lineups*"
    await editEmbed(moBotMessage, embed)
    try:
      if (lineupType == "Classic"):
        lineup = createClassicLineup(players, valueList, valueListOption, playerLimitations, copy.deepcopy(mustHaves))
      elif (lineupType == "Showdown"):
        lineup = createShowdownLineup(players, valueList, valueListOption, playerLimitations, copy.deepcopy(mustHaves))
      await printLineup(lineup, moBotMessage, embed)
    except IndexError:
      embed["footer"]["text"] = "Could Not Create A Lineup"
      await moBotMessage.add_reaction(COUNTERCLOCKWISE_ARROWS_EMOJI)
      await moBotMessage.add_reaction(X_EMOJI)
      await editEmbed(moBotMessage, embed)        

    try:
      playerLimitations = await getNewPlayerLimitations(playerLimitations, message.author, moBotMessage, embed, client)
      if (playerLimitations is None):
        lineupType = await getLineupType(message.author, moBotMessage, embed, client)
        playerLimitations = await getRestrictions([], 3, message.author, moBotMessage, embed, client)
        mustHaves = await getRestrictions([], 4, message.author, moBotMessage, embed, client)
      elif (playerLimitations == "exit"):
        break
    except asyncio.TimeoutError:
      await moBotMessage.channel.send("**TIMED OUT**")
      break
# end main

def createShowdownLineup(players, valueList, valueListOption, playerLimitations, mustHaves):
  positions = {"CPT" : {}, "FLEX" : {}}
  lineup = {"CPT" : [None], "FLEX" : [None, None, None, None, None]}
  for player in players:
    player = players[player]
    cpt = copy.copy(player)
    flex = copy.copy(player)

    cpt.price = cpt.price * 1.5

    positions["CPT"][cpt.name] = cpt
    positions["FLEX"][flex.name] = flex

  salary = 50000

  # get must haves

  # get benchmark
  lineup, salary = getBenchmark(lineup, positions, playerLimitations, salary)
  # get lineup
  lineup, salary = getLineup(lineup, salary, mustHaves, playerLimitations, valueList)
  return lineup
# end createShowdownLineup

def createClassicLineup(players, valueList, valueListOption, playerLimitations, mustHaves):
  positions = {"QB" : {}, "RB" : {}, "WR" : {}, "TE" : {}, "FLEX" : {}, "DST" : {}}
  lineup = {"QB" : [None], "RB" : [None, None], "WR" : [None, None, None], "TE" : [None], "FLEX" : [None], "DST" : [None]}
  for player in players:
    player = players[player]
    positions[player.pos][player.name] = player
    if (player.pos in ["RB", "WR", "TE"]):
      positions["FLEX"][player.name] = player
      
  salary = 50000

  # get must haves
  if (valueListOption != "BASIC"):
    pos1 = valueListOption.split("_")[0]
    pos2 = valueListOption.split("_")[1]
    playerPos1 = None
    playerPos2 = None
    i = len(valueList) - 1
    while (not (playerPos1 and playerPos2)):
      player = valueList[i]
      if (player.id not in playerLimitations):
        if (pos1 in player.fpos and not playerPos1):
          playerPos1 = player
          mustHaves.append(player.id)
          i = len(valueList) - 1
        elif (pos2 in player.fpos and not playerPos2 and playerPos1 is not None and player.team == playerPos1.team):
          playerPos2 = player
          mustHaves.append(player.id)
      i -= 1
  lineup, salary = addMustHaves(lineup, valueList, mustHaves, salary)

  # get benchmark
  lineup, salary = getBenchmark(lineup, positions, playerLimitations, salary)

  # get lineup
  lineup, salary = getLineup(lineup, salary, mustHaves, playerLimitations, valueList)
  return lineup
# end createClassicLineup

def getLineup(lineup, salary, mustHaves, playerLimitations, valueList):
  sameSalaryCount = 0
  while sameSalaryCount < 10:
    oldLineup = lineup
    oldSalary = salary
    for position in lineup:
      pPlayers = lineup[position] # list of players at position in lineup

      for i in range(len(pPlayers)):
        currentPlayer = pPlayers[i]
        potentialPlayer = currentPlayer
        if (potentialPlayer.id in mustHaves):
          continue
        salary += currentPlayer.price # preparing for switch

        for vPlayer in valueList:
          if (vPlayer.pos == position or (position == "FLEX" and "FLEX" in vPlayer.fpos)):
            if (vPlayer.value > potentialPlayer.value and vPlayer.appg > potentialPlayer.appg):
              newPlayer = vPlayer
              if (salary - newPlayer.price >= 0):
                if (not isInLineup(lineup, newPlayer) and newPlayer.id not in playerLimitations):
                  lineup[position][i] = newPlayer # switch
                  salary -= newPlayer.price
                  break
              potentialPlayer = newPlayer

        if (lineup[position][i] == currentPlayer): # when a switch is not made
          currentPlayer = lineup[position][i]
          salary -= currentPlayer.price
    sameSalaryCount += 1 if oldSalary == salary else 0
  return lineup, salary
# end getLineup

def addMustHaves(lineup, valueList, mustHaves, salary):
  for player in valueList:
    if (player.id in mustHaves):
      for position in lineup:
        if (position == player.pos):
          for i in range(len(lineup[position])):
            currentPlayer = lineup[position][i]
            if (currentPlayer == None):
              lineup[position][i] = player
              salary -= player.price
              break
  return lineup, salary
# end getMustHaves

def getBenchmark(lineup, positions, playerLimitations, salary):
  for position in positions:
    valuePerDollarList = sorted(positions[position].values(), key=operator.attrgetter('valuePerDollar'))
    for i in range(len(lineup[position])):
      if (lineup[position][i] != None):
        continue

      player = valuePerDollarList[-(i+1)]
      inLineupCount = i+1
      while True:
        player = valuePerDollarList[-(inLineupCount)]
        if (not isInLineup(lineup, player) and player.id not in playerLimitations and salary - player.price >= 0):
          lineup[position][i] = player
          salary -= player.price
          break
        else:
          inLineupCount += 1
  return lineup, salary
# end getBenchmark

def getValueList(players, valueListOption):
  players = copy.deepcopy(players)
  for player in players:

    if (valueListOption == "QB_FLEX"):
      qb = players[player]
      if (qb.pos == "QB"):
        for player in players:
          player = players[player]
          if (player.team == qb.team and player.pos == "FLEX"):
            player.value = player.value * qb.value

    elif (valueListOption == "DST_RB"):
      team = players[player]
      if (team.pos == "DST"):
        for player in players:
          player = players[player]
          if (player.team == team.team and player.pos == "RB"):
            player.value = player.value * team.value

  valueList = sorted(players.values(), key=operator.attrgetter("value"))
  return valueList
# end getValueList

def isInLineup(lineup, player):
  for position in lineup: # dict item
    for lPlayer in lineup[position]: # list item
      try:
        if (lPlayer.id == player.id):
          return True
      except AttributeError: # error occurs when first setting benchmark lineup when player == None
        pass
  return False
# end isInLineup

def getOffenseStats(player, pos, year):
  statGroups = []

  # --- PASSING STATS --- #
  stats = parseStatsTable(player, "offensePassing", year)
  if (stats != []):
    totalYards = int(stats[8].replace(",", ""))
    passingYards = float(stats[10]) # already per game format
    passingTDs = int(stats[11])
    interceptions = int(stats[12])
    statGroups.append(OffensePassingStatsPerGame(totalYards, passingTDs, passingYards, 
    interceptions))
  # --- END PASSING STATS --- #

  # --- RUSHING STATS --- #
  stats = parseStatsTable(player, "offenseRushing", year)
  if (stats != []):
    totalYards = int(stats[6].replace(",", ""))
    rushingYards = float(stats[8]) # already per game format
    rushingTDs = int(stats[9])
    fumbles = int(stats[15])
    statGroups.append(OffenseRushingStatsPerGame(totalYards, rushingTDs, rushingYards, fumbles))
  # --- END RUSHING STATS --- #

  # --- RECEIVING STATS --- #
  stats = parseStatsTable(player, "offenseReceiving", year)
  if (stats != []):
    totalYards = int(stats[5].replace(",", ""))
    receivingYards = float(stats[7]) # already per game format
    receivingTDs = int(stats[9])
    receptions = int(stats[4])
    statGroups.append(OffenseReceivingStatsPerGame(totalYards, receivingTDs, receivingYards, receptions))
  # --- END RECEIVING STATS --- #

  # --- SCORING STATS --- #
  stats = parseStatsTable(player, "offenseScoring", year)
  if (stats != []):
    totalPoints = int(stats[4])
    points = float(stats[5]) # already per game format
    pkfgReturnTDs = int(stats[8]) + int(stats[9])
    twoPtConversions = int(stats[17])
    fumbleReturnTDs = int(stats[11])
    statGroups.append(OffenseScoringStatsPerGame(points, totalPoints, pkfgReturnTDs, twoPtConversions, fumbleReturnTDs))
  # --- END SCORING STATS --- #

  adjustedStats = {}
  for statGroup in statGroups:
    adjustedStats = convertToFppg(statGroup, adjustedStats, pos)
  
  return adjustedStats
# end getQBStats

def getDefenseStats(team, pos, year): # team = Short Name
  teamName = ABBRV_TO_LONG[SHORT_TO_ABBRV[team]]
  statGroups = []

  # --- SCORING STATS --- # 
  stats = parseStatsTable(teamName, "defenseScoring", year)
  games = int(stats[2])
  points = int(stats[4])
  pkfgReturnTD = int(stats[9]) + int(stats[9])
  interceptionReturnTD = int(stats[11])
  fumbleReturnTD = int(stats[12])
  blkPntFgReturnTD = int(stats[13]) + int(stats[14])
  safety = int(stats[17])
  twoPtReturn = int(stats[18])
  statGroups.append(DefenseScoringStatsPerGame(games, points, pkfgReturnTD, interceptionReturnTD, fumbleReturnTD, blkPntFgReturnTD, safety, twoPtReturn))
  # --- END SCORING STATS --- #

  # --- OTHER STATS --- #
  stats = parseStatsTable(teamName, "defenseOther", year)
  games = int(stats[2])
  sacks = float(stats[8])
  interceptions = int(stats[11])
  fumbleRecoveries = int(stats[16])
  statGroups.append(DefenseOtherStatsPerGame(games, sacks, interceptions, fumbleRecoveries))
  # --- END OTHER STATS --- # 

  adjustedStats = {}
  for statGroup in statGroups:
    adjustedStats = convertToFppg(statGroup, adjustedStats, pos)
  
  return adjustedStats
# end getDefenseStats

def convertToFppg(stats, adjustedStats, pos):
  weights = { # used to determine how good/bad the stat is
    "DEFENSE" : {
      "points" : {
        "0" : 1.4,
        "6" : 1.1,
        "13" : 0.8,
        "20" : 0.5,
        "27" : 0.4,
        "34" : 0.3,
        "35" : 0 # 35+
      },
      "pkfgReturnTD" : 1,
      "interceptionReturnTD" : 1,
      "fumbleReturnTD" : 1,
      "blkPntFgReturnTD" : 1,
      "safety" : .6,
      "twoPtReturn" : .6,
      "sacks" : .5,
      "interceptions" : .6,
      "fumbleRecoveries" : .6,
    },
    "OFFENSE" : {
      "passingTDs" : .833,
      "passingYards" : .173,
      "passingYards300" : .667,
      "interceptions" : .0,
      "rushingTDs" : 1.167,
      "rushingYards" : .183,
      "rushingYards100" : .667,
      "receivingTDs" : 1.167,
      "receivingYards" : .183,
      "receivingYards100" : .667,
      "receptions" : .333,
      "pkfgReturnTDs" : 1.167,
      "fumbles" : 0,
      "twoPtConversions" : .5,
      "fumbleReturnTDs" : 1.167,
    }
  }
  stats = vars(stats)
  for var in stats:
    if (var == "points"):
      for point in weights[pos][var]:
        if (stats[var] <= int(point)):
          adjustedStats[var] = weights[pos][var][point]
          break
      if (var not in adjustedStats):
        adjustedStats[var] = weights[pos][var]["35"]
    elif (var == "passingYards"):
      adjustedStats[var] = stats[var] * weights[pos][var]
      if (stats[var] > 300):
        adjustedStats[var] += weights[pos]["passingYards300"]
    elif (var == "rushingYards"):
      adjustedStats[var] = stats[var] * weights[pos][var]
      if (stats[var] > 100):
        adjustedStats[var] += weights[pos]["rushingYards100"]
    elif (var == "receivingYards"):
      adjustedStats[var] = stats[var] * weights[pos][var]
      if (stats[var] > 100):
        adjustedStats[var] += weights[pos]["receivingYards100"]
    else:
      adjustedStats[var] = stats[var] * weights[pos][var]
  return adjustedStats
# end convertToFppg

def getPlayerValueByCombiningStats(lastYearStats, thisYearStats, weekNumber):
  lastYearMultiplier = (16 - (weekNumber * 2)) / 16.1
  thisYearMultiplier = (weekNumber * 2) / 16.1
  playerValue = 0
  for stat in lastYearStats:
    lastYearStat = lastYearStats[stat] * lastYearMultiplier
    thisYearStat = thisYearStats[stat] * thisYearMultiplier
    playerValue += lastYearStat + thisYearStat
    '''print("\n", stat, playerValue)
    print(lastYearStat, lastYearStats[stat])
    print(thisYearStat, thisYearStats[stat])'''
  return playerValue
# end combineStats

def parseStatsTable(name, tableName, year):
  table = statsTables[tableName][str(year)]
  stats = []
  for i in range(len(table)):
    if (name in str(table[i])):
      stats = table[i].split("</td")
      for j in range(len(stats)):
        stats[j] = stats[j].split(">")[-1].strip()
      break
  return stats
# end parseStatsTable

async def printValueList(valueList, pos, moBotMessage):
  #os.remove("ValueList.txt")
  valueListFile = open("ValueList.txt", "w")
  valueListFile.write("Value List (%s):" % (pos))
  for player in valueList:
    if (pos != None):
      if (pos in player.fpos):
        valueListFile.write("%s %s" % (player.name, player.value))
    else:
      valueListFile.write("\n%s %s %s %s %s %s %s" % (player.pos, player.name, player.value, player.appg, player.price, player.team, player.game))
  valueListFile.close()
  '''valueListFile = open("ValueList.txt", "r")
  await moBotMessage.channel.send(file=discord.File(valueListFile))
  valueListFile.close()'''
# end printValueList

async def printLineup(lineup, moBotMessage, embed):
  embed["fields"][5]["value"] = "__Pos. - Player Name - Appg. - Price - Team__"
  playerCount = 0
  remSalary = 50000
  totalAppg = 0
  for position in lineup:
    for player in lineup[position]:
      try:
        playerCount += 1
        emojiNumber = RandomFunctions.numberToEmojiNumbers(playerCount)
        game = player.game.replace(player.team, "**" + player.team + "**")
        embed["fields"][5]["value"] += ("\n%s %s - **%s** - %s - %s - %s" % (emojiNumber, position, player.name, player.appg, player.price, game))
        remSalary -= int(player.price)
        totalAppg += float(player.appg)
        await moBotMessage.add_reaction(emojiNumber)
      except AttributeError: # when not printing full lineup
        print(position, None)
  await moBotMessage.add_reaction(CHECKMARK_EMOJI)
  await moBotMessage.add_reaction(COUNTERCLOCKWISE_ARROWS_EMOJI)
  await moBotMessage.add_reaction(X_EMOJI)
  embed["footer"]["text"] = ("REM. SALARY: $%s TOTAL FPPG: %s" % (remSalary, totalAppg))
  await editEmbed(moBotMessage, embed)
# end printLineup

async def editEmbed(moBotMessage, embed):
  await moBotMessage.edit(embed=discord.Embed.from_dict(embed))
# end editEmbed

def getPlayersFromSalaries(salaries):
  players = {}
  # players[playerName] = Player object
  lines = salaries.readlines()[1:] # remove header
  # line = [pos,name(id),name,id,rosterPos,price,game date time,team,fppg]
  for line in lines:
    line = line.split(",")
    name = line[2].strip()
    name = PLAYER_NAME_CORRECTIONS[name] if (name in PLAYER_NAME_CORRECTIONS) else name
    id = line[3].strip()
    pos = line[0].strip()
    fpos = line[4].strip()
    price = line[5].strip()
    game = line[6].split(" ")[0]
    team = line[7].strip()
    appg = line[8].strip()
    if (fpos != "CPT"):
      players[name] = Player(name, id, pos, fpos, price, game, team, appg)

  return players
# end getPlayersFromSalaries

async def getRestrictions(restrictions, fieldIndex, member, moBotMessage, embed, client):
  
  def checkEmoji(payload):
    return payload.user_id == member.id and payload.channel_id == moBotMessage.channel.id and payload.emoji.name == CHECKMARK_EMOJI
  # end checkEmoji

  def checkMessage(msg):
    return msg.channel.id == moBotMessage.channel.id and member.id == msg.author.id
  # end checkMessage

  restrictionName = embed["fields"][fieldIndex]["name"][:-1]
  embed["description"] = "**Type the names of any '" + restrictionName + "' below (one name per line)... If none, type 'none'.**"
  await editEmbed(moBotMessage, embed)
  try:
    msg = await client.wait_for("message", timeout=300, check=checkMessage)
    newRestrictions = msg.content.split("\n") if msg.content.lower() != "none" else []
    await msg.delete()
  except asyncio.TimeoutError:
    newRestrictions = []

  if (len(newRestrictions) > 0):
    embed["fields"][fieldIndex]["value"] = ""
    content = "**Is this name correct?**"
    moBotMessage2 = await moBotMessage.channel.send(content)
    for i in range(len(newRestrictions)):
      try:
        playerName = get_close_matches(newRestrictions[i], playerNamesToIDs)[0]
        await moBotMessage2.edit(content=content + "\n`" + playerName + "`")
      except IndexError:
        await moBotMessage2.edit(content="**Entered Name Not Found - CLICK " + CHECKMARK_EMOJI + "**")
        playerName = spaceChar
      await moBotMessage2.add_reaction(CHECKMARK_EMOJI)
      try:
        payload = await client.wait_for("raw_reaction_add", timeout=60, check=checkEmoji)
        await moBotMessage2.remove_reaction(CHECKMARK_EMOJI, member)
        embed["fields"][fieldIndex]["value"] += "\n" + playerName
        if (playerName != spaceChar):
          newRestrictions[i] = playerNamesToIDs[playerName]
        else:
          embed["fields"][fieldIndex]["value"] = spaceChar
        await editEmbed(moBotMessage, embed)
      except asyncio.TimeoutError:
        await moBotMessage2.edit(content="**TIMED OUT**")
    await moBotMessage2.delete()

  for newRestriction in newRestrictions:
    restrictions.append(newRestriction)
  return restrictions
# end getRestrictions

async def getNewPlayerLimitations(playerLimitations, member, moBotMessage, embed, client):
  
  def checkEmoji(payload):
    return payload.user_id == member.id and payload.channel_id == moBotMessage.channel.id and payload.emoji.name in [CHECKMARK_EMOJI, COUNTERCLOCKWISE_ARROWS_EMOJI, X_EMOJI]
  # end checkEmoji
  
  lineup = embed["fields"][5]["value"].split("\n")
  embed["description"] = "**Use the numbers below to remove any players, then click the " + CHECKMARK_EMOJI + " to continue.**"
  await editEmbed(moBotMessage, embed)
  payload = await client.wait_for("raw_reaction_add", timeout=300, check=checkEmoji)
  if (payload.emoji.name == CHECKMARK_EMOJI):
    moBotMessage = await moBotMessage.channel.fetch_message(moBotMessage.id)
    for reaction in moBotMessage.reactions: # get players
      emoji = str(reaction.emoji)
      async for user in reaction.users():
        if (user.id == member.id):
          for line in lineup:
            if (emoji in line):
              player = line.split("**")[1]
              embed["fields"][3]["value"] += "\n" + player
              embed["fields"][5]["value"] = embed["fields"][5]["value"].replace(line, "*Removed*")
              playerLimitations.append(playerNamesToIDs[player])
              break
          break
    await moBotMessage.clear_reactions()
    if (len(embed["fields"][3]["value"]) > 1):
      embed["fields"][3]["value"] = embed["fields"][3]["value"].replace(spaceChar, "")
    await editEmbed(moBotMessage, embed)
    return playerLimitations
  elif (payload.emoji.name == COUNTERCLOCKWISE_ARROWS_EMOJI):
    await moBotMessage.clear_reactions()
    for i in range(1, 6):
      embed["fields"][i]["value"] = spaceChar
    embed["footer"]["text"] = spaceChar
    await editEmbed(moBotMessage, embed)
    return None
  elif (payload.emoji.name == X_EMOJI):
    return "exit"
# end getNewPlayerLimitations

async def getLineupStyle(member, moBotMessage, embed, client):
  
  def checkEmoji(payload):
    return payload.user_id == member.id and payload.channel_id == moBotMessage.channel.id and payload.emoji.name in RandomFunctions.numberEmojis
  # end checkEmoji

  lineupStyles = [
    "BASIC",
    "QB_WR",
    "DST_RB",
    #"QB_FLEX_DST_RB",
  ]
  embed["description"] = "*Lineup Styles:*"
  for i in range(len(lineupStyles)):
    emojiNumber = RandomFunctions.numberToEmojiNumbers(i+1)
    embed["description"] += "\n" + spaceChar + emojiNumber + " - " + lineupStyles[i]
    await moBotMessage.add_reaction(emojiNumber)

  embed["description"] += "\n**Select a Lineup Style:**"
  await editEmbed(moBotMessage, embed)
  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60, check=checkEmoji)
    lineupStyle = lineupStyles[RandomFunctions.emojiNumbertoNumber(payload.emoji.name)-1]
  except asyncio.TimeoutError:
    await moBotMessage.channel.send("**TIMED OUT**")
    lineupStyle = lineupStyles[0]

  embed["fields"][2]["value"] = lineupStyle
  await editEmbed(moBotMessage, embed)
  await moBotMessage.clear_reactions()
  return lineupStyle
# end getLineupStyle

async def getLineupType(member, moBotMessage, embed, client):
  
  def checkEmoji(payload):
    return payload.user_id == member.id and payload.channel_id == moBotMessage.channel.id and payload.emoji.name in RandomFunctions.numberEmojis
  # end checkEmoji

  lineupTypes = ["Classic", "Showdown"]
  embed["description"] = "*Lineup Types:*"
  for i in range(len(lineupTypes)):
    emojiNumber = RandomFunctions.numberToEmojiNumbers(i+1)
    embed["description"] += "\n" + spaceChar + emojiNumber + " - " + lineupTypes[i]
    await moBotMessage.add_reaction(emojiNumber)

  embed["description"] += "\n**Select a Lineup Type:**"
  await editEmbed(moBotMessage, embed)
  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60, check=checkEmoji)
    lineupType = lineupTypes[RandomFunctions.emojiNumbertoNumber(payload.emoji.name)-1]
  except asyncio.TimeoutError:
    await moBotMessage.channel.send("**TIMED OUT**")
    lineupType = lineupTypes[0]

  embed["fields"][1]["value"] = lineupType
  await editEmbed(moBotMessage, embed)
  await moBotMessage.clear_reactions()
  return lineupType
# end getLineupType

async def getFile(member, moBotMessage, embed, client):  

  def checkEmoji(payload):
    return payload.user_id == member.id and payload.channel_id == moBotMessage.channel.id and payload.emoji.name in RandomFunctions.numberEmojis
  # end checkEmoji

  embed["description"] = "*Salaries Files:*"
  await editEmbed(moBotMessage, embed)
  dkSalariesDir = os.getcwd() + "\\DKSalaries"
  files = []
  for dir in os.walk(dkSalariesDir):
    for file in dir[-1]:
      if (file[-3:] == "csv" and str(weekNumber+1) in file):
        files.append(file)
        emojiNumber = RandomFunctions.numberToEmojiNumbers(len(files))
        embed["description"] += "\n" + spaceChar + emojiNumber + " - " + file
        await moBotMessage.add_reaction(emojiNumber)

  embed["description"] += "\n**Select a File Number:**"
  await editEmbed(moBotMessage, embed)
  try:
    payload = await client.wait_for("raw_reaction_add", timeout=60, check=checkEmoji)
    file = files[RandomFunctions.emojiNumbertoNumber(payload.emoji.name)-1]
  except asyncio.TimeoutError:
    await moBotMessage.channel.send("**TIMED OUT**")
    file = files[0]

  embed["fields"][0]["value"] = file
  await editEmbed(moBotMessage, embed)
  await moBotMessage.clear_reactions()
  return dkSalariesDir + "\\" + file
# end getFile

def getTableFromURL(url):
  soup = bSoup(requests.get(url).text, "html.parser")
  title = str(soup.title)
  if ("National Football League Stats" not in title):
    return []
  oddRows = soup.findAll("tr", {"class" : "odd"})
  evenRows = soup.findAll("tr", {"class" : "even"})
  table = []
  for i in range(len(oddRows)):
    table.append(str(oddRows[i]))
    try:
      table.append(str(evenRows[i]))
    except IndexError:
      break
  return table
# end getTableFromURL 

async def getStatsTables(moBotMessage, embed, statsTables):
  embed["description"] = ("*Getting Stat Tables (%1d)*" % (len(statsTables)))
  await editEmbed(moBotMessage, embed)
  def combineStatsTables(oldTable, newTable):
    table = oldTable
    for i in newTable:
      table.append(i)
    return table

  for table in statsTables:
    embed["description"] += "\n" + spaceChar + table
    await editEmbed(moBotMessage, embed)
    oldTable = []
    for year in range(lastYear, thisYear+1):
      if (statsTables[table]["PAGES"]):
        page = 1
        while (page >= 1):
          url = statsTables[table]["URL"].replace("&&YEAR&&", str(year)).replace("&&PAGE&&", str(page))
          newTable = getTableFromURL(url)
          oldTable = combineStatsTables(oldTable, newTable)
          if (len(newTable) == 0):
            page = 0
          else:
            page += 1
        # end while
      else:
        url = statsTables[table]["URL"].replace("&&YEAR&&", str(year))
        oldTable = getTableFromURL(url)
      statsTables[table][str(year)] = oldTable
  return statsTables
# end getStatsTables