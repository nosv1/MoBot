import discord
import asyncio
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import SecretStuff

import Collections

moBot = "449247895858970624"
spaceChar = "⠀"

nosStorageChannelID = 554885144498929680

coachReviewPageOrder = ["Resources", "Analysis", "Feedback"]
coachReviewPageDict = {
  coachReviewPageOrder[0] : "Base your rating on the quality of the following material provided: \n" + spaceChar + "- Videos\n" + spaceChar + "- Tips\n" + spaceChar + "- etc.\n\n",
  coachReviewPageOrder[1] : "Base your rating on the quality of the following material provided: \n" + spaceChar + "- Match Analysis\n" + spaceChar + "- Replay Analysis\n" + spaceChar + "- etc.\n\n",
  coachReviewPageOrder[2] : "We encourage you to provide extra feedback for our coaches as well as some comments on their quality. Be respectful and constructive.\n\nClick the ✏, and type your message below.",
}

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  coachRequestChannelID = 571863693718192128

  if (moBot in args[0]):
    if (args[1] == "request"):
      if (message.channel.id == coachRequestChannelID):
        await coachRequest(message, int(args[2][-19:-1]))
    elif (args[1] == "coach"):
      if (args[2] == "register"):
        await registerCoach(message, message.author, True, client)
        await message.delete()
      elif (args[2] == "bio"):
        await updateCoachBio(message, 1)
        await message.delete()

# end main

async def memberJoin(member):
  pass
# end memberJoin

async def memberRemove(member):
  pass
# end memberRemove

async def mainReactionAdd(message, payload, client): 

  try:
    embedAuthor = message.embeds[0].author.name
  except IndexError:
    embedAuthor = "None"

  if ("requested a <@&" in message.content):
    if (payload.emoji.name == "✅"):
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

      coach = message.guild.get_member(payload.user_id)
      try:
        playerClient = message.guild.get_member(int(message.content.split(">")[0][-18:]))
      except:
        playerClient = message.guild.get_member(int(message.content.split(">")[0][-17:]))

      for role in coach.roles:
        if ("Coach" in role.name):
          if ("Tier II" in role.name):
            await coachRequestTaken(message, coach, playerClient, client)
            break
          elif ("Tier I" in role.name):
            await coachRequestTaken(message, coach, playerClient, client)
            break

  elif (embedAuthor == "Coach Review Form"):
    embed = message.embeds[0].to_dict()
    pageNumber = int(embed["footer"]["text"].split("/")[0].split("Page")[1].strip())

    if (payload.emoji.name == "⬅"):
      pageNumber -= 1
      if (pageNumber == 0):
        pageNumber = len(coachReviewPageOrder)
      await leftRightCoachReviewForm(message, payload, embed, pageNumber, client)

    elif (payload.emoji.name == "➡"):
      pageNumber += 1
      if (pageNumber > len(coachReviewPageOrder)):
        pageNumber = 1
      await leftRightCoachReviewForm(message, payload, embed, pageNumber, client)
    
    elif (payload.emoji.name == "⬆"):
      await upDownCoachReviewForm(message, embed, "up", pageNumber, client)
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

    elif (payload.emoji.name == "⬇"):
      await upDownCoachReviewForm(message, embed, "down", pageNumber, client)
      await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

    elif (payload.emoji.name == "✏"):
      await message.channel.set_permissions(message.guild.get_member(payload.user_id), read_messages=True, send_messages=True)
      await message.add_reaction("✅")
      await message.channel.send("You may now type your comments.\n\nWhen you are finished, click the ✅ above to submit your ratings.\n*Note that only the last message sent will be saved as your comments to the coach. Make sure it's less than 500 characters.*\n\nThank you for your time.")
        
    elif (payload.emoji.name == "✅"):
      await endCoachingSession(message, embed, message.guild.get_member(payload.user_id), client)

  elif ("Review" in embedAuthor and "#" in embedAuthor):
    await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))

    embed = message.embeds[0].to_dict()
    pages = int(embed["footer"]["text"].split("/")[1].split("--")[0].strip())

    if (pages > 1):
      pageNumber = int(embed["footer"]["text"].split("/")[0].split("Page")[1].strip())  
      if (pageNumber == 1):
        embed = discord.Embed.from_dict(embed)
        embed.remove_field(-1)
        embed.remove_field(-1)
        embed = embed.to_dict()

      if (payload.emoji.name == "⬅"):
        pageNumber -= 1
        if (pageNumber == 0):
          pageNumber = pages
        await leftRightCoachPortfolio(message, payload, embed, pageNumber, client)

      elif (payload.emoji.name == "➡"):
        pageNumber += 1
        if (pageNumber > pages):
          pageNumber = 1
        await leftRightCoachPortfolio(message, payload, embed, pageNumber, client)

# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def leftRightCoachPortfolio(message, payload, embed, pageNumber, client):
  if (pageNumber > 1):
    channel = client.get_channel(nosStorageChannelID)
    reviewsMsg = await channel.fetch_message(int(embed["footer"]["text"].split("--")[1].strip()))
    reviews = reviewsMsg.content.split("->\n")
    for i in range(len(reviews)):
      reviews[i] += "->"
    tReview = reviews[pageNumber-2].split("<!")[1].split("->")[0].split(",")
    review = [tReview[0], reviews[pageNumber-2].split(tReview[0]+",")[1].split("," + tReview[-2])[0], tReview[-2], tReview[-1]]
    playerClient = message.guild.get_member(int(review[0]))

    embed["fields"][0]["name"] = "Client: " + playerClient.display_name + "#" + str(playerClient.discriminator)

    stars = [float(review[-2]), float(review[-1])]
    stars.append(round(sum(stars)/len(stars)*2)/2)

    for i in range(len(stars)):
      rating = stars[i]
      isHalf = rating + .5 - (int(rating) + .5) >= .5
      stars[i] = ""
      for j in range(int(rating)):
        stars[i] += "<:1star:592971666779537418>"
      if (isHalf):
        stars[i] += "<:halfstar:592971749461852174>"

    feedback = ""
    for i in range(1, len(review) - 2):
      feedback += review[i] + ","
    feedback = feedback[:-1]

    embed["fields"][0]["value"] = "Resources:\n" + stars[0] + "\n\n" + "Analysis:\n" + stars[1] + "\n\n" + "Feedback:\n*" + feedback + "*\n\n" + "Overall Rating:\n" + stars[-1] + "\n\nUse the ⬅/➡ to cycle between reviews."

    footer = "Page " + str(pageNumber) + "/" + embed["footer"]["text"].split("/")[1].strip()
    embed = discord.Embed.from_dict(embed)
    embed.set_footer(text=footer)
    await message.edit(embed=embed)

  else:
    workbook = await openCoachesSpreadsheet()
    coachOverviews = workbook.worksheet("Coach Overviews")
    overviews = coachOverviews.range("A2:F" + str(coachOverviews.row_count))

    for i in range(len(overviews)):
      if (overviews[i+3].value == str(message.id)):
        coach = message.guild.get_member(int(overviews[i].value))
        averageRating = float(overviews[i+5].value)
        isHalf = averageRating + .5 - (int(averageRating) + .5) >= .5
        stars = ""
        for j in range(int(averageRating)):
          stars += "<:1star:592971666779537418>"
        if (isHalf):
          stars += "<:halfstar:592971749461852174>"
        
        values = [coach, overviews[i+1].value, overviews[i+2].value, stars + "\n\nUse the ⬅/➡ to cycle between reviews."]
        footer = "Page " + str(pageNumber) + "/" + embed["footer"]["text"].split("/")[1].strip()
        embed = await updateCoachEmbedFrontPage(message, values)
        embed.set_footer(text=footer)
        await message.edit(embed=embed)
        break
# end leftRightCoachPortfolio

async def getCoachingLogs(message, playerClient):

  category = message.channel.category
  channels = category.channels

  for channel in channels:
    try:
      messages = channel.history(limit=10000)
    except AttributeError:
      pass

    if (channel.name == "resources" or channel.name == "analysis"):
      out = []
      async for msg in messages:
        out.append("<@" + str(msg.author.id)   + ">: "  + msg.content)

      outT = "__**Log of " + channel.name + "**__:\n"
      for i in range(len(out) - 1, -1, -1):
        outA = out[i] + "\n"
        if (len(outA) + len(outT) >= 2000):
          await playerClient.send(outT)
          outT = outA
        else:
          outT += outA
      try:
        await playerClient.send(outT)
      except discord.errors.HTTPException:
        pass

    await channel.delete()
  await category.delete()
# end getCoachingLogs

async def updateCoachBio(message, pageNumber):
  await message.channel.trigger_typing()
  bio = message.content.split("bio")[1].strip()

  workbook = await openCoachesSpreadsheet()
  coachOverviews = workbook.worksheet("Coach Overviews")
  overviews = coachOverviews.range("A2:F" + str(coachOverviews.row_count))
  coach = message.author

  for i in range(len(overviews)):
    if (overviews[i].value == str(coach.id)):
      overviews[i+1].value = bio
      try:
        averageRating = float(overviews[i+5].value)
        isHalf = averageRating + .5 - (int(averageRating) + .5) >= .5
        stars = ""
        for j in range(int(averageRating)):
          stars += "<:1star:592971666779537418>"
        if (isHalf):
          stars += "<:halfstar:592971749461852174>"
      except ValueError:
        stars = "No Reviews Available"
      
      embedMsg = await message.channel.fetch_message(int(overviews[i+3].value))
      embed = embedMsg.embeds[0].to_dict()

      values = [coach, overviews[i+1].value, overviews[i+2].value, stars + "\n\nUse the ⬅/➡ to cycle between reviews."]
      footer = "Page " + str(pageNumber) + "/" + embed["footer"]["text"].split("/")[1].strip()
      embed = await updateCoachEmbedFrontPage(message, values)
      embed.set_footer(text=footer)
      await embedMsg.edit(embed=embed)
      break
#end updateCoachBio

async def updateCoachEmbedFrontPage(message, values):

  embed = discord.Embed(color=0x000000)
  embed.set_author(name=values[0].display_name + "#" + str(values[0].discriminator) + " Reviews")
  embed.add_field(name="Bio:", value=values[1] + "\n" + spaceChar, inline=False)
  embed.add_field(name="Tier:", value="<@&" + values[2] + ">\n" + spaceChar, inline=False)
  embed.add_field(name="Average Rating:", value=values[3], inline=False)

  return embed
# end updateCoachEmbed

async def registerCoach(message, coach, fromCommand, client):
  await message.channel.trigger_typing()

  workbook = await openCoachesSpreadsheet()
  coachOverviews = workbook.worksheet("Coach Overviews")
  coaches = coachOverviews.range("A2:E" + str(coachOverviews.row_count))

  roles = coach.roles
  coachRole = None
  for role in roles:
    if (role.id == 557301449252405268 or role.id == 557301354029383700):
      coachRole = role
      break
  
  if (coachRole != None):
    for i in range(len(coaches)):
      if (coaches[i].value == str(coach.id)):
        if (fromCommand):
          await message.channel.send("You have already registered as a coach.")
        break
      if (coaches[i].value == ""):
        coaches[i].value = str(coach.id)
        coaches[i+1].value = "Use `@MoBot#0697 coach bio [insert_bio]`"
        coaches[i+2].value = str(coachRole.id)

        values = [coach, coaches[i+1].value, coaches[i+2].value, "No Reviews Available\n\nUse the ⬅/➡ to cycle between reviews."]

        reviewsMsg = await client.get_channel(nosStorageChannelID).send("---")
        coaches[i+4].value = str(reviewsMsg.id)
      
        reviewsChannel = message.guild.get_channel(574622480984047627)
        embed = await updateCoachEmbedFrontPage(message, values)
        embed.set_thumbnail(url=values[0].avatar_url)
        embed.set_footer(text="Page 1/1 -- " + str(reviewsMsg.id))
        embedMsg = await reviewsChannel.send(embed=embed)
        coaches[i+3].value = str(embedMsg.id)
        await embedMsg.add_reaction("⬅")
        await embedMsg.add_reaction("➡")

        coachOverviews.update_cells(coaches, value_input_option="USER_ENTERED")
        return embedMsg, embed
  else:
    await message.channel.send("You may not register as a coach without a coach role.")
# end registerCoach

async def endCoachingSession(message, embed, playerClient, client):
  await message.channel.send("Thank you for submitting your feedback.\n\nDeleting channels and sending you and your coach a log.")

  workbook = await openCoachesSpreadsheet()
  coachReviews = workbook.worksheet('Coach Reviews')
  coachOverviews = workbook.worksheet("Coach Overviews")
  reviews = coachReviews.range("A2:E" + str(coachReviews.row_count))
  overviews = coachOverviews.range("A2:F" + str(coachOverviews.row_count))

  channel = client.get_channel(nosStorageChannelID)
  reviewsMsg = await channel.fetch_message(int(embed["footer"]["text"].split("--")[1].strip()))
  
  coachID = reviewsMsg.content.split("Coach ID: ")[1].split("\n")[0].strip()
  feedback = await message.channel.history(limit=2).flatten()
  feedback = "None Provided" if feedback[1].author.bot else feedback[1].content
  resourcesRating = reviewsMsg.content.split("Values: ")[1].split(",")[0].strip()
  analysisRating = reviewsMsg.content.split("Values: ")[1].split(",")[1].split("\n")[0].strip()
  for i in range(len(reviews)):
    if (reviews[i].value == ""):
      reviews[i].value = coachID
      reviews[i+1].value = str(playerClient.id)
      reviews[i+2].value = feedback
      reviews[i+3].value = resourcesRating
      reviews[i+4].value = analysisRating
      coachReviews.update_cells(reviews, value_input_option="USER_ENTERED")
      break

  await getCoachingLogs(message, playerClient)
  
  embed = None
  for i in range(len(overviews)):
    if (overviews[i].value == str(coachID)):
      reviewsChannel = message.guild.get_channel(574622480984047627)
      embedMsg = await reviewsChannel.fetch_message(int(overviews[i+3].value))
      embed = embedMsg.embeds[0].to_dict()

      overallRating = [float(resourcesRating), float(analysisRating)]
      if ("#" not in overviews[i+5].value):
        overallRating.append(float(overviews[i+5].value))
      overallRating = round(sum(overallRating)/len(overallRating)*2)/2
      
      reviewsMsg = await channel.fetch_message(int(overviews[i+4].value))
      review = "\n<!" + str(playerClient.id) + "," + feedback + "," + resourcesRating + "," + analysisRating + "->"
      await reviewsMsg.edit(content=reviewsMsg.content.split("---")[0] + review + "---")
      break

  isHalf = overallRating + .5 - (int(overallRating) + .5) >= .5
  stars = ""
  for j in range(int(float(overallRating))):
    stars += "<:1star:592971666779537418>"
  if (isHalf):
    stars += "<:halfstar:592971749461852174>"
  embed["fields"][-1]["value"] = stars + "\n\nUse the ⬅/➡ to cycle between reviews."

  pages = int(embed["footer"]["text"].split("/")[1].split("--")[0].strip()) + 1
  footer = embed["footer"]["text"].split("/")[0] + "/" + str(pages) + " -- " + embed["footer"]["text"].split("--")[1].strip()

  embed = discord.Embed.from_dict(embed)
  embed.set_footer(text=footer)
  await embedMsg.edit(embed=embed)
# end endCoachingSession

async def leftRightCoachReviewForm(message, payload, embed, pageNumber, client):

  currentRating = "-"
  embed["fields"][0]["name"] = coachReviewPageOrder[pageNumber-1]

  value = coachReviewPageDict[coachReviewPageOrder[pageNumber-1]] + "`Current Rating: " + str(currentRating) + "/5`\n" + spaceChar if (pageNumber < len(coachReviewPageOrder)) else  coachReviewPageDict[coachReviewPageOrder[pageNumber-1]]
  embed["fields"][0]["value"] = value

  embed["footer"]["text"] = "Page " + str(pageNumber) + "/" + embed["footer"]["text"].split("/")[1].strip()

  embed = discord.Embed.from_dict(embed)
  await message.edit(embed=embed)

  await message.remove_reaction(payload.emoji, message.guild.get_member(payload.user_id))
  if (pageNumber == len(coachReviewPageOrder)):
    await message.remove_reaction("⬆", message.author)
    await message.remove_reaction("⬇", message.author)
    await message.add_reaction("✏")
  else:
    await message.remove_reaction("✏", message.author)
    await message.add_reaction("⬆")
    await message.add_reaction("⬇")

    embed = embed.to_dict()

    dmMsgID = int(embed["footer"]["text"].split("--")[1].strip())
    channel = client.get_channel(nosStorageChannelID)
    valuesMsg = await channel.fetch_message(dmMsgID)
    values = valuesMsg.content.split("Values: ")[1].split(",")
    currentRating = values[pageNumber-1]

    value = coachReviewPageDict[coachReviewPageOrder[pageNumber-1]] + "`Current Rating: " + str(currentRating) + "/5`\n" + spaceChar
    embed["fields"][0]["value"] = value

    embed = discord.Embed.from_dict(embed)
    await message.edit(embed=embed)
# end leftRightCoachReviewForm

async def upDownCoachReviewForm(message, embed, direction, pageNumber, client):
  currentRating = float(embed["fields"][0]["value"].split("/")[0].split("Current Rating: ")[1].strip())
  if (direction == "up"):
    if (currentRating <= 4.5):
      currentRating += .5 
    else:
      currentRating = int(5)
  elif (direction == "down"):
    if (currentRating >= .5):
      currentRating -= .5 
    else:
      currentRating = int(0)

  currentRating = int(currentRating) if (".0" in str(currentRating)) else currentRating

  embed["fields"][0]["value"] = embed["fields"][0]["value"].split("Current Rating: ")[0] + "Current Rating: " + str(currentRating) + "/5`\n" + spaceChar

  dmMsgID = int(embed["footer"]["text"].split("--")[1].strip())

  embed = discord.Embed.from_dict(embed)
  await message.edit(embed=embed)

  channel = client.get_channel(nosStorageChannelID)
  valuesMsg = await channel.fetch_message(dmMsgID)
  values = valuesMsg.content.split("Values: ")[1].split(",")
  values[pageNumber-1] = str(currentRating)

  newValues = ""
  for value in values:
    newValues += value + ","
  newValues = newValues[:-1]

  await valuesMsg.edit(content=valuesMsg.content.split("Values: ")[0] + "Values: " + newValues)
# end upDownCoachReviewForm

async def coachRequestTaken(message, coach, playerClient, client):

  await message.edit(content="<@" + str(coach.id) + "> has accepted coach request from <@" + str(playerClient.id) + ">.")
  await message.clear_reactions()

  coachName = coach.nick if coach.nick != None else coach.name
  playerClientName = playerClient.nick if playerClient.nick != None else playerClient.name
  category = await message.guild.create_category_channel("Coach: " + coachName + " Client: " + playerClientName)

  await category.edit(position=1)

  for role in message.guild.roles:
    if (role.name == "@everyone"):
      await category.set_permissions(role, read_messages=False)
      break

  await category.set_permissions(coach, read_messages=True)
  await category.set_permissions(playerClient, read_messages=True)

  guild = message.guild
  resources = await guild.create_text_channel("resources")
  analysis = await guild.create_text_channel("analysis")
  feedback = await guild.create_text_channel("feedback")
  coachingVoice = await guild.create_voice_channel("Coaching Voice")

  await resources.edit(category=category, sync_permissions=True)
  await analysis.edit(category=category, sync_permissions=True)
  await feedback.edit(category=category, sync_permissions=True)
  await coachingVoice.edit(category=category, sync_permissions=True)

  await feedback.set_permissions(coach, send_messages=False)
  await feedback.set_permissions(playerClient, send_messages=False, read_messages=True)

  # feedback embed
  values = ""
  for i in range(len(coachReviewPageOrder)-1):
    values += "2.5,"
  values = values[:-1]
  msg = await client.get_user(475325629688971274).send("Coach ID: " + str(coach.id) + "\nValues: " + values)
  embed = discord.Embed(colour=0x000000)
  embed.set_author(name="Coach Review Form")
  embed.add_field(name=coachReviewPageOrder[0], value=coachReviewPageDict[coachReviewPageOrder[0]] + "`Current Rating: 2.5/5`\n" + spaceChar, inline=False)
  embed.set_footer(text="Page 1/3 -- " + str(msg.id))

  await resources.send("Your Coach will display all relevant information regarding your session here.")
  await analysis.send("Please find all information regarding your match analysis here.")
  fbMsg = await feedback.send(embed=embed, content="<@" + str(playerClient.id) + ">, once your session is complete, please use the form below to give feedback and review your coach.\n\nUse the ⬅/➡ to flip through the pages, and use the arrows, ⬆/⬇ to assign a rating (1 being the worst, and 5 being the best).\n\nOn the last page, click the ✏ to write extra comments.\n\n*The channel is locked until the ✏ is clicked, at which point you can type any comments.*")

  await fbMsg.add_reaction("⬅")
  await fbMsg.add_reaction("➡")
  await fbMsg.add_reaction("⬆")
  await fbMsg.add_reaction("⬇")

  await registerCoach(message, coach, False, client)
# end coachRequestTaken

async def coachRequest(message, coachRole):
  coachTiers = {
    "Tier I" : [557301449252405268, 572580710355828746], # [roleID, channelID]
    "Tier II" : [557301354029383700, 572580898906832926],
    557301449252405268 : "Tier I",
    557301354029383700 : "Tier II"
  }

  coachTier = coachTiers[coachRole]
  coachChannel = message.guild.get_channel(coachTiers[coachTier][1])

  requestMsg = await coachChannel.send("<@" + str(message.author.id) + "> has requested a <@&" + str(coachRole) + ">; please click the ✅ if you can take this request.")
  await requestMsg.add_reaction("✅")

  coachesRequestedCount = await message.channel.fetch_message(586234715670052878)
  count = int(coachesRequestedCount.content.split(":")[1][:-1].strip()) + 1
  await coachesRequestedCount.edit(content="`Total Coaches Requested: " + str(count) + "`")
  msg = await message.channel.send("A request has been sent. Once a Coach accepts your request, you will be added to private channels at the top of the server.")
  await asyncio.sleep(30)
  await msg.delete()
  await message.delete()
# end coachRequest

async def openCoachesSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1p1jYdtNASCre51oxt7ZgKAe6Vq8qinO8A0lyNYUCSxA")
  return workbook
# end openCoachesSpreadsheet