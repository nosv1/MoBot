import discord
import time
import asyncio

moBot = "449247895858970624"

async def main(args, message, client):
  
  if (args[2] == "open"):
    fromReaction = False
    await openTicket(message, message.author, fromReaction, client)
  elif (args[2] == "close"):
    await closeTicket(message)
  elif (args[2] == "add"):
    await addUserToTicket(message)

# end main

async def getTicketLog(message, ticketCategory):
  channels = message.guild.channels
  
  for channel in channels:
    name = channel.name.lower()
    if ("ticket" in name and "log" in name):
      return channel

  channel = await message.guild.create_text_channel("ticket log")
  roles = message.guild.roles
  for role in roles:
    if (role.name == "@everyone"):
      await channel.set_permissions(role, read_messages=False)
  await channel.send("This is where @MoBot#0697 will log the tickets when they are created and closed.")
  await channel.edit(category=ticketCategory, sync_permissions=True)

  await message.channel.send("**Ticket Log Created**")
  return channel
# end checkForTicketLog

async def checkForMultipleTickets(message, user):
  sender = user
  channels = message.guild.channels
  
  count = 0
  for i in channels:
    if ("ticket" in i.name.lower()):
      if (str(sender.id) in i.name):
        count += 1
  return count
# end checkForMultipleTickets

async def createTicketChannel(message, ticketLog, ticketCategory, user, fromReaction, client):
  channels = message.guild.channels

  async def createChannel():
    name = user.display_name
    channel = await message.guild.create_text_channel("ticket " + name + " " + str(user.id))
    await channel.edit(category=ticketCategory, sync_permissions=True)
    await channel.set_permissions(user, read_messages=True, send_messages=True)
    return channel

  async def sendTicketResponses(ticketResponse, channel):
    await ticketLog.send(ticketResponse) # sends the current ticket response to the log, then below will send an updated message to the channel      
    ticketResponse += "\n---\nTo add users to this channel, either add them manually or use `@MoBot#0697 ticket add @user @user ... @user`. The former will allow <@" + str(moBot) + "> to send a message of the conclusion."
    ticketResponse += "\nWhen a conclusion has been reached, use `@MoBot#0697 ticket close [conclusion]` to log the ticket and send a message to the users invovled.\n---"
    for i in message.attachments:
      ticketResponse += i.url + "\n"
    await channel.send(ticketResponse)

  ticketChannel = None
  if (fromReaction):
    ticketChannel = await createChannel()
    def check(msg):
      return msg.channel.id == ticketChannel.id and msg.author.id == user.id
    await ticketChannel.send("**<@" + str(user.id) + ">, what is your reason for opening this ticket?**\nPlease type your response below.")
    try:
      msg = await client.wait_for("message", timeout=120.0, check=check)
      ticketResponse = ticketChannel.name + " opened by <@" + str(user.id) + "> - " + msg.content
      await sendTicketResponses(ticketResponse, ticketChannel)
    except asyncio.TimeoutError:
      await ticketChannel.send("**TIMED OUT**")
    await ticketChannel.send("<@" + str(user.id) + ">, please list the user(s) involved, if any.")

  else:
    try:
      reason = message.content.split("open ")[1].strip()
      ticketChannel = await createChannel()
      ticketResponse = ticketChannel.name + " opened by <@" + str(user.id) + "> - " +  reason
      await sendTicketResponses(ticketResponse, ticketChannel)
      await message.delete()
      
    except IndexError:
      msg = await message.channel.send("**Please include a brief reason to open a ticket channel.**\n\n`@MoBot#0697 ticket open [reason]`")
      message.delete()
      await asyncio.sleep(5)
      await msg.delete()
  return ticketChannel
#end createTicketChannel

async def getTicketCateogry(message):
  categories = message.guild.by_category()

  for category in categories:
    try:
      if ("tickets" in category[0].name.lower() or "disputes" in category[0].name.lower()):
        return category[0]
    except AttributeError:
      pass

  await message.channel.send("**Ticket Category Created**\n\nBe sure to edit the category permissions to allow the proper roles to read and send messages in tickets. The created ticket category is where <@449247895858970624> will put the tickets when they are created.\n\nIf you are going to rename the category, make sure either 'tickets' or 'disputes' is in the name, otherwise, <@449247895858970624> won't know where to put the tickets.")
  category = await message.guild.create_category_channel("Tickets (Disputes)")

  for role in message.guild.roles:
    if (role.name == "@everyone"):
      await category.set_permissions(role, read_messages=False)
      return category
# end getTicketCateogry

async def openTicket(message, user, fromReaction, client):
  ticketCategory = await getTicketCateogry(message)
  ticketLog = await getTicketLog(message, ticketCategory)
  if (await checkForMultipleTickets(message, user) > 2):
    await message.channel.send("**Cannot Create Ticket**\nTry again when one of your current tickets has been resolved.")
  else:
    ticketChannel = await createTicketChannel(message, ticketLog, ticketCategory, user, fromReaction, client)
    if (ticketChannel != None):
      msg = await message.channel.send("**Ticket Channel Created**\n<#" + str(ticketChannel.id) + ">")
      await asyncio.sleep(5)
      await msg.delete()
# end openTicket

async def closeTicket(message):
  ticketLog = await getTicketLog(message, await getTicketCateogry(message))
      
  if ("ticket" in message.channel.name):
    if (not(str(message.author.id) in message.channel.name)):
      try:
        conclusion = message.content.split("close ")[1]
        await ticketLog.send(message.channel.name  + " closed by <@" + str(message.author.id) + "> - " + conclusion)
        await message.channel.send("**Conclusion sent to <#" + str(ticketLog.id) + ">.**")
        
        members = message.channel.members
        for member in members:
          if (str(member.id) in message.channel.name):
            await messageUser(message, member.id, conclusion)
        await message.channel.send("**Conclusion sent to ticket creator and added user(s).**")
        
        await message.channel.send("**Deleting Channel**")
        await message.channel.delete()
      except IndexError:
        await message.channel.send("**Include a conclusion when closing a ticket.**")
    else:
      await message.channel.send("**Cannot Close Ticket**\nYou either opened the ticket or were added to it.")
# end closeTicket

async def messageUser(message, userId, text):
  await message.guild.get_member(int(userId)).send(text)
# end messageUser

async def addUserToTicket(message):
  for i in message.content.split("add ")[1].split(">"):
    try:
      try:
        userId = i[-18:]
        user = message.guild.get_member(int(userId))
      except:
        userId = i[-17:]
        user = message.guild.get_member(int(userId))
      
      await message.channel.set_permissions(user, send_messages=True, read_messages=True)
      await message.channel.send("<@" + str(userId) + "> has been added to ticket.")
      
      print(message.channel.name + " " + str(userId))
      await message.channel.edit(name=message.channel.name + " @" + str(userId))
    except ValueError:
      continue
# end addUserToTicket
