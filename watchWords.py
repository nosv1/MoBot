import discord
from datetime import datetime

moBot = "449247895858970624"

# user uses @MoBot watch "word1" "word2" word3"
# words are stored in dictionary with arrays of the user who is watching those words
  # dictionary will be in a text file, then create dictionary by importing
  # word,user,user,user
# MoBot sends DM with message link, messge content, and author, server, channel


async def watchWord(message, client, dic):
  word = message.content.lower().split("\"")[1]
  author = str(message.author)
  if (word in dic):
    if (author in dic[word]):
      reply = "```MoBot is already watching, '" + word + "', for you.```"
    else:
      dic[word].append(author)
  else:
    dic[word] = []
    dic[word].append(author)
  reply = "```MoBot will start watching for '" + word + "' in all the servers you and MoBot are both in. This means if \'" + word + "' is mentioned at all in a message (including within another word, unfortunatley), you will get a message from MoBot.```"
  await client.send_message(message.channel, reply)
  await export(dic)
# end watchWord

async def unwatchWord(message, client, dic):
  word = message.content.lower().split("\"")[1]
  author = str(message.author)
  if (word in dic):
    del dic[word][dic[word].index(author)]
    reply = "```MoBot will stop watching, '" + word + "', for you.```"
    if (len(dic[word]) == 0):
      dic.pop(word)
  else:
    reply = "```MoBot cannot unwatch a word that you don't have it watching... '@MoBot watching' to see what words MoBot is currently watching for you.```"
  await client.send_message(message.channel, reply)
  await export(dic)
# end unwatchWord

async def watching(message, client, dic):
  wordList = ""
  author = str(message.author)
  for word in dic:
    for user in dic[word]:
      if (author == user):
        wordList += "'" + word + "', "
  wordList = wordList[:-2]
  reply = "```You currenlty have MoBot watching the word(s): " + wordList + ".```"
  await client.send_message(message.channel, reply)
# end watching

async def export(dic):
  file = open(r"D:\Users\Nick\OneDrive\GTA Stuff\Bots\MoBot\MoBot\WordDictionary.txt", "w")
  for word in dic:
    line = word + ","
    for user in dic[word]:
      line += str(user) + ","
    line = line[:-1] + "\n"
    file.write(line)
  file.close()    
# end export

async def help(message, client):
  reply = "```@MoBot watch \"word\"\n  - MoBot will start watching for that word in every server you and MoBot are both in.\n"
  reply += "@MoBot unwatch \"word\"\n  - MoBot will stop watching for that word.\n"
  reply += "@MoBot watching\n  - returns the words MoBot is currenlty watching for you.\n"
  reply += "\nWhen MoBot finds a word that someone is watching, it will send a DM including the message, server, channel, and link to where the word was mentioned.```"
  await client.send_message(message.channel, reply)
# end help

async def main(self, message, client, args):
  # import dictionary
  dic = {}
  file = open(r"D:\Users\Nick\OneDrive\GTA Stuff\Bots\MoBot\MoBot\WordDictionary.txt", "r")
  lines = file.readlines()
  file.close
  for line in lines:
    line = line.split(",")
    line[len(line)-1] = line[len(line)-1][:-1]
    dic[line[0]] = []
    for i in range(1, len(line)):
      dic[line[0]].append(line[i])
        
  if (args[0] == moBot and " watch " in message.content.lower()):
    if (args[0] == moBot and "help" in message.content.lower()):
      await help(message, client)
    else: 
      await watchWord(message, client, dic)
  elif (args[0] == moBot and "unwatch" in message.content.lower()):
    await unwatchWord(message, client, dic)
  elif (args[0] == moBot and "watching" in message.content.lower()):
    await watching(message, client, dic)
  else:
    msg = message.content.lower()
    try:
      server = message.server.id
    except AttributeError:
      return
    members = discord.Client.get_server(client, str(server)).members
    for word in dic:
      if (word in msg):
        link = "https://discordapp.com/channels/" + message.server.id + "/" + message.channel.id + "/" + message.id
        users = dic[word]
        reply = str(message.author) + " mentioned '" + word + "' in a server you are in. This is what " + str(message.author).split("#")[0] + " said:```\"" + str(message.content) + "\"\n" + str(message.server) + " - " + str(message.channel) + "``` You can jump to the message using this link: " + link
        for user in users:
          user = message.server.get_member_named(user)
          for member in members:
            if (str(user) == str(member)):
              await client.send_message(user, reply)
  # is user adding words
# end main
