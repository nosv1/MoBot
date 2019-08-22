import discord
import time

moBot = "449247895858970624"

async def main(args, message, client):
  if (args[0][-19:-1] == moBot):
    if (args[1] == "votes" and args[2] == "reset"):
      await resetVoteCounts(message, 552187996548366336, 550399085107085352)
  pass
# end main

async def mainReactionAdd(message, payload, client):
  user = message.guild.get_member(payload.user_id)
  if (user.name != "MoBot"):
    if (message.channel.id == 550399085107085352): # voting channel
      votingMessagesIds = [555548147678576643, 555548170881597440, 555548194466037802, 555548207581757440]
      if (message.id in votingMessagesIds):
        await voting(message, payload, votingMessagesIds)
# end mainReactionAdd

async def mainReactionRemove(message, payload, client):
  pass
# end mainReactionRemove

async def voting(message, payload, messageIds):
  one = "1⃣"
  two = "2⃣"
  three = "3⃣"
  four = "4⃣"
  check = "✅"
  inputUser  = payload.user_id
  user = message.guild.get_member(inputUser)
  votingLog = message.guild.get_channel(552187996548366336)
  messages = []
  moBotMessages = []
  if (payload.emoji.name == check):
    moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, checking your votes..."))
    for i in messageIds:
      msg = await message.channel.fetch_message(i)
      messages.append(msg)
      
    if (payload.emoji.name == check):
      await message.remove_reaction(payload.emoji, user)
      multiVotesForOneTracakMessage = False
      multiVotesForMultiTracakMessage = False
      voteValueCounts = [0, 0, 0, 0]
      voteValues = []
      for msg in messages:
        msgReactions = msg.reactions
        multiVotesForTracakCount = 0
        index = 0
        for reaction in msgReactions:
          if (reaction.emoji != check):
            users = reaction.users()
            async for user in users:
              if (user.id == inputUser):
                if (reaction.emoji == one):
                  voteValues.append(1)
                elif (reaction.emoji == two):
                  voteValues.append(2)
                elif (reaction.emoji == three):
                  voteValues.append(3)
                elif (reaction.emoji == four):
                  voteValues.append(4)
                await msg.remove_reaction(reaction.emoji, user)
                voteValueCounts[index] += 1 
                multiVotesForTracakCount += 1
              if (multiVotesForTracakCount >= 2):
                if (not multiVotesForOneTracakMessage):
                  moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you cannot have multiple values for the same option."))
                  
                  await votingLog.send("<@" + str(inputUser) + "> tried to vote with multiple values for the same option. -- " + str(voteValues))
                  multiVotesForOneTracakMessage = True
          index += 1
        if (max(voteValueCounts) > 1):
          if (not multiVotesForMultiTracakMessage):
            moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you cannot have the same value for multiple options."))
            
            await votingLog.send("<@" + str(inputUser) + "> tried to vote with the same value for multiple options. -- " + str(voteValues))
            multiVotesForMultiTracakMessage = True
        
      if (multiVotesForOneTracakMessage or multiVotesForMultiTracakMessage):
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, your votes have been cleared; try again."))
      elif (sum(voteValueCounts) < 4):
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you must vote for each option. Your votes have been cleared; try again."))
        
        await votingLog.send("<@" + str(inputUser) + "> tried to vote without voting for each option. -- " + str(voteValues))
      else:
        moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, submitting your votes..."))
        driver = message.guild.get_member(inputUser).nick
        if (driver == None):
          driver = message.guild.get_member(inputUser).name
        driverId = inputUser
        
        alreadyVoted, count = await submitVote(votingLog, voteValues, driver, driverId)
        if (alreadyVoted):
          moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, you have already voted."))
          
          await votingLog.send("<@" + str(inputUser) + "> tried to vote again after already voting. -- " + str(voteValues))
        else:
          if (count != None):
            voteCount = await message.channel.fetch_message(555549023700779021)
            await voteCount.edit(content="```Voters Voted: " + str(count) + "```")
          moBotMessages.append(await message.channel.send("<@" + str(inputUser) + ">, your votes have been submitted. Thanks for voting!"))
      
          await votingLog.send("<@" + str(inputUser) + "> voted -- "  + str(voteValues))
          await getVotes(votingLog)
        
      time.sleep(4)
  for i in moBotMessages:
    await i.delete()
# end voting

async def submitVote(votingLog, votes, driver, driverId):
  alreadyVoted = False
  count = 0
  getVotersList = await votingLog.fetch_message(552549895752646666)
  voteCounts = [552549921752875018, 552549945442304020, 552549970381766669, 552549988685578241]
  if (str(driverId) in getVotersList.content):
    alreadyVoted = True
    count = None
    return alreadyVoted, count

  await getVotersList.edit(content=getVotersList.content + "\n" + driver + "-" + str(driverId) + " - " + str(votes))

  # get count
  count = len(getVotersList.content.split("\n")) - 1
  for i in range(len(voteCounts)):
    voteCountMessage = await votingLog.fetch_message(voteCounts[i])
    newCount = "Track " + str(i+1) + ": " + str(int(voteCountMessage.content.split(": ")[1].split("\n")[0]) + int(votes[i])) + "\n"
    if (votes[i] == 4):
      newCount += "Pefect Votes: " + str(int(voteCountMessage.content.split(": ")[2]) + 1)
    else:
      newCount += "Perfect Votes: " + str(int(voteCountMessage.content.split(": ")[2]))
    await voteCountMessage.edit(content = newCount)

  return alreadyVoted, count
# end submitVoteVote

async def getVotes(channel):
  voteCounts = [552549921752875018, 552549945442304020, 552549970381766669, 552549988685578241]
  reply = ""
  for i in range(len(voteCounts)):
    voteCount = await channel.fetch_message(voteCounts[i])
    reply += voteCount.content + "\n\n"

  await channel.send("```" + reply + "```")
# end getVotes

async def resetVoteCounts(message, votingLog, trackVoting):
  trackVotingChannel = message.guild.get_channel(trackVoting)
  votingLogChannel = message.guild.get_channel(votingLog)
  voteCountMessage = await trackVotingChannel.fetch_message(555549023700779021)
  await voteCountMessage.edit(content = "```Voters Voted: 0```")

  getVotersList = await votingLogChannel.fetch_message(552549895752646666)
  voteCounts = [552549921752875018, 552549945442304020, 552549970381766669, 552549988685578241]

  await getVotersList.edit(content="Voters:")
  for i in range(len(voteCounts)):
    voteCountMessage = await votingLogChannel.fetch_message(voteCounts[i])
    await voteCountMessage.edit(content="Track " + str(i+1) + ": 0\nPerfect Votes: 0")
  await message.delete()
# end resetVotes