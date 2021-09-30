import discord
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

import SecretStuff

moBot = 449247895858970624
spaceChar = "⠀"

# GTACCHub Catalogue Sheets
XBOX_SHEET_ID = 0
PS_SHEET_ID = 1862312493
PC_SHEET_ID = 1701609275

# gta cc hub spreadsheet stuff
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('GTA CC Hub_client_secret.json'), scope)

catalogueLink = "https://bit.ly/cchubCatalogue"

async def main(args, message, client):
  
  catalogue = ["catalogue", "catalog", "catelogue", "catelog", "catalogur", "catlog", "cataloge", "catalgoue"]
  if (args[0][1:].lower() in catalogue):
    platform = ["xb1", "xbox", "ps4", "ps", "pc"]
    if (len(args) > 2 and args[1].lower() in platform):
      try:
        await getJob(message, args)
      except gspread.exceptions.APIError:
        await message.channel.send("**There were technical difficulties searching for a job. Try again in a minute or so.**")
      
# end main

async def mainReactionAdd(message, payload, client):
  pass
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionAdd

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member, client):
  pass
# end memberJoin

async def getJob(message, args):
  await message.channel.trigger_typing()
  workbook = openSpreadsheet()
  sheets = workbook.worksheets()
  platform = args[1].lower()
  platSheet = None
  if (platform == "xb1" or platform == "xbox"):
    platSheet = [sheet for sheet in sheets if sheet.id == XBOX_SHEET_ID][0]
  elif (platform == "ps4" or platform == "ps"):
    platSheet = [sheet for sheet in sheets if sheet.id == PS_SHEET_ID][0]
  elif (platform == "pc"):
    platSheet = [sheet for sheet in sheets if sheet.id == PC_SHEET_ID][0]
    
  jobs = platSheet.range("A12:A" + str(platSheet.row_count-1))
  jobTypes = platSheet.range("B12:B" + str(platSheet.row_count-1))
  jobListSplit = {}

  moBotMember = message.guild.get_member(moBot)
  embed = discord.Embed(color=moBotMember.roles[-1].color)
  embed.set_author(name="Catalogue Search Results", icon_url=moBotMember.avatar_url, url=catalogueLink)
  embed.set_thumbnail(url=message.guild.icon_url)
  embed.description = "[__Creation Catalogue Spreadsheet__](%s)" % catalogueLink

  jobType = None
  startJobName = 3
  jobTypeLetters = {"r" : "Regular Racing Circuits", "o" : "Off-Road/Rally/RallyX Circuit", "t" : "Themed Circuit (Stunt/Challenge/Transform)", "n" : "Non-race (Capture/LTS/TDM)"}
  if (args[2].lower() not in jobTypeLetters): # if no job type supplied
    startJobName = 2
  else:
    jobType = args[2]
    embed.add_field(name="**Job Type:**", value=jobTypeLetters[args[2].lower()], inline=False)
    await message.channel.trigger_typing()

  jobName = ""
  link = None
  for i in range(startJobName, len(args)):
    jobName += args[i] + " "
  jobName = jobName[:-1]
  embed.add_field(name="**Job Name:**", value=jobName, inline=False)

  # if there is a job type specification, fix jobs and jobTypes arrays to match specification
  if (jobType != None):
    i = 0
    while (i < len(jobs)):
      if (jobType.lower() not in jobTypes[i].value.lower()):
        del jobTypes[i]
        del jobs[i]
      else:
        i += 1

  jobFound = False
  job = ""
  for i in range(len(jobs)):
    cellValue = jobs[i].value.lower()
    if ("jobs by" not in cellValue and "..." not in cellValue and len(jobs[i].value) > 1):
      if (jobs[i].value.lower() == jobName.lower()):
        jobFound = True
        link = platSheet.cell(jobs[i].row, jobs[i].col, value_render_option='FORMULA').value.split('"')[1]
        job = jobs[i].value
        break
      elif (jobs[i].value != ""):
        splitJobName = []
        currentJobName = jobs[i].value
        for i in range(0, len(currentJobName)-2):
          splitJobName.append(currentJobName[i] + currentJobName[i+1] + currentJobName[i+2])
        jobListSplit[currentJobName] = [splitJobName, 0]
  
  value = ""

  if (jobFound):
    value = "[**__%s__**](%s)\n" % (job, link)
  else:
    potentialJobs = []
    splitJobName = []
    for i in range(0, len(jobName)-2):
      splitJobName.append(jobName[i] + jobName[i+1] + jobName[i+2])

    for i in range(len(splitJobName)):
      combo = splitJobName[i].lower()
      for job in jobListSplit:
        for j in range(len(jobListSplit[job][0])):
          if (jobListSplit[job][0][j].lower() in combo):
            jobListSplit[job][1] += -1
          else:
            jobListSplit[job][1] += 1
    for job in jobListSplit:
      try:
        score = float(jobListSplit[job][1] / len(jobListSplit[job][0]))
      except ZeroDivisionError:
        score = 0
      if (jobName == "x"):
        score = random.random()
      potentialJobs.append([job, score])
    
    potentialJobs.sort(key=lambda x:x[1])

    if (value == ""):
      if (jobName == "x"):
        value += "Here is a random list of jobs due to the 'job name' being 'x'.\n\n"
      else:
        value += "The job you inputted was not found; here are some close matches.\n"
      returnAmount = int(((.015 * len(potentialJobs)) + 1) / 2)
      if (returnAmount < 5):
        returnAmount = 5
        if (returnAmount > len(potentialJobs)):
          returnAmount = len(potentialJobs)
      for i in range(0, returnAmount):
        for j in range(0, len(jobs)):
          if (jobs[j].value == potentialJobs[i][0]):
            if (len(value) < 600):
              value += "\n[__**%s**__](%s)" % (jobs[j].value, catalogueLink)
              try:
                value = value.replace(catalogueLink, platSheet.cell(jobs[j].row, jobs[j].col, value_render_option='FORMULA').value.split('"')[1])
              except IndexError: # when there isn't a link for the job
                value += " - *Link Not Available*"
            break

  if (len(value) >= 600):
    value += "\n*There are more jobs than what are shown. Either view the spreadsheet, or to narrow your search, be more specific in the inputted job name.*"

  embed.add_field(name="**Result(s):**", value=value)
  embed.set_footer(text="If the track you have searched for is not appearing, it is most likely not currently on the Catalogue. Please DM a member of the admin team who can assist you and hopefully you will have the track added shortly! (You can request your own tracks or anyone else's)")

  await message.channel.send(embed=embed)

def openSpreadsheet():
  clientSS = gspread.authorize(creds)
  workbook = clientSS.open_by_key("195i7Zyf1mcZGCDhgszCjjN-8fyOTVjlg0eeW1hGaGRo")
  return workbook
# end openSpreadsheet
