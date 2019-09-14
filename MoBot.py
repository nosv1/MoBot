# MoBot made by Mo#9991

import discord
import asyncio
from datetime import datetime, timedelta
import random
from pytz import timezone
import traceback
import gspread

import SecretStuff

# importing server specific files
import COTM
import COTMPS4
import IG
import FortKnight
import GTAVRacingEvents
import GTACCHub
import CreatorChallenge
import XB1WEC
import Noble2sLeague
import NobleGaming
import NobleHub
import AOR

# importing external functions files
import getGTAWeather
import XboxGamertags
import watchWords
#import tTeams // no longer supported
import MessageScheduler
import ticketManager
import DiscordSheets
import ClocksAndCountdowns
import RLScrims
import ReactionRole
import CollectionsOLD
import Collections
import Reservations
import MoBotTimeZones
import RLRanks
import AdminFunctions
import EventScheduler

import Hangman

# getting server ids
servers = {}
file = open("MoBotServers.txt", "r")
lines = file.readlines()
file.close()
for line in lines:
  servers[line.split(",")[1]] = line.split(",")[0]
  
client = discord.Client()

moBot = 449247895858970624

# common guilds
cotm = 527156310366486529
moBotSupport = 467239192007671818
noble2sLeauge = 437936224402014208

# common users
mo = 405944496665133058
nosv1 = 475325629688971274

spaceChar = "⠀"

# question words -- who what when where why how will can are am 
yesNoQuestionResponses = [
  ["yes", [
    "Sure, why not?",
    "Do I need a dollar? ||hint - @MoBot#0697 donate :sunglasses:||", 
    ]
  ],
  ["no", [
    "Not a chance, lol", 
    ]
  ],
  ["maybe", [
    "Hell if I know...", 
    "Perhaps...", 
    ]
  ],
]

questionWords = {
  "will" : yesNoQuestionResponses,
  "can" : yesNoQuestionResponses,
  "are" : yesNoQuestionResponses,
  "am" : yesNoQuestionResponses,
  "is" : yesNoQuestionResponses,
}

 # updated upon connectivity of MoBot
reactionMessages = {}
autoRoles = {} 
isConnected = False

@client.event
async def on_ready():
  print("MoBot is online - " + str(datetime.now()))

  workbook = await ReactionRole.openReactionRoleSpreadsheet()

  global reactionMessages
  reactionMessages = await ReactionRole.updateReactionMessages(reactionMessages, workbook)
  print ("Reaction Messages Received")

  global autoRoles
  autoRoles = await ReactionRole.updateAutoRoles(autoRoles, workbook)
  print ("AutoRoles Received")

  # priming the temp storage
  msg = await client.get_user(nosv1).send(".")
  await msg.delete()
  
  mobotLog = client.get_guild(moBotSupport).get_channel(604099911251787776) # mobot log
  embed = discord.Embed(color=int("0xd1d1d1", 16))
  embed.set_author(name="MoBot Restarted")
  await mobotLog.send(embed=embed)
  
  global isConnected
  isConnected = True
# end on_ready

@client.event
async def on_raw_message_edit(payload):
  pd = payload.data
  try:
    guild = client.get_guild(int(pd["guild_id"]))
    channel = guild.get_channel(int(pd["channel_id"]))
    message = await channel.fetch_message(int(pd["id"]))
  except:
    try:
      channel = client.get_channel(int(pd["channel_id"]))
      message = await channel.fetch_message(int(pd["id"]))
    except:
      return
  
  try:
    if (not message.author.bot and isConnected):
      await on_message(message)
  except:
    print ("Error -- " + str(traceback.format_exc()))
    pass

@client.event
async def on_message(message):
  if (not isConnected):
    return
  message.content = message.content.replace('“','"').replace('”','"').replace("  ", " ")

  args = message.content.split(" ")
  for i in range(0, len(args)):
    args[i] = args[i].split("\n")[0].strip()
  
  logActionToConsole(message, message.author, "message")

  if (str(message.author) != "MoBot#0697"):
    if ((message.author.id == 209584832030834688 or mo == message.author.id) and "beep" in args): # if potterman says beep...
      await message.channel.send("boop")

    if (args[0][-19:-1] == str(moBot)):
      authorPerms = message.channel.permissions_for(message.author)
      isBotSpam = message.channel.id == 593911201658961942
      isMo = mo == message.author.id
      isNos = nosv1 == message.author.id
      permissions = {
        "changeNicknamePerms" : isNos or isMo or authorPerms.change_nickname or isBotSpam,
        "manageChannelPerms" : isNos or isMo or authorPerms.manage_channels or isBotSpam,
        "manageMessagePerms" : isNos or isMo or authorPerms.manage_messages or isBotSpam,
        "manageChannelPerms" : isNos or isMo or authorPerms.manage_channels or isBotSpam,
        "manageRolePerms" : isNos or isMo or authorPerms.manage_roles or isBotSpam,
        "administratorPerms" : isNos or isMo or authorPerms.administrator
      }

      if (len(args) == 1):
        await message.channel.send("Use `@MoBot#0697 help` to see a list of commands.")

      ## commands that have seperate files
      elif (args[1] == "ticket"):
        await ticketManager.main(args, message, client)
      elif ("schedule" in args[1] and "message" in args[2]):
          await MessageScheduler.main(args, message, client)
      elif (args[1] == "sheets"):
        await DiscordSheets.main(args, message, client)
      elif ((args[1] == "countdown" or args[1] == "clock") and permissions["manageChannelPerms"]):
        await ClocksAndCountdowns.main(args, message, client)
      elif (args[1] == "scrims"):
        await RLScrims.main(args, message, client)
      elif (args[1] == "watch" and permissions["manageRolePerms"]):
        global reactionMessages 
        reactionMessages = await ReactionRole.addReactionRoleMessage(message, args, reactionMessages)
        reactionMessages = await ReactionRole.clearDeletedMessages(reactionMessages, client)
      elif (args[1] == "autorole" and permissions["manageRolePerms"]):
        global autoRoles
        if (args[2] == "add"):
          autoRoles = await ReactionRole.addAutoRole(message, autoRoles)
        elif (args[2] == "clear"):
          autoRoles = await ReactionRole.clearAutoRole(message, autoRoles)
      elif ("collection" in args[1]):
        await Collections.main(args, message, client)
      elif ("reservation" in args[1]):
        await Reservations.main(args, message, client)
      elif ("tz" in args[1]):
        await MoBotTimeZones.main(args, message, client)
      elif (args[1] == "rlrank"):
        await RLRanks.main(args, message, client)
      elif (args[1] == "remindme"):
        await EventScheduler.setReminder(message)

      ## general use server commands
      elif (args[1] == "say" and permissions["manageMessagePerms"]):
        if (args[2] == "embed"):
          await moBotEmbed(message, args, False)
        else:
          try:
            await message.delete()
          except discord.errors.Forbidden:
            pass
          await message.channel.send(message.content[26:])
      # edit a message based on given id
      elif (args[1] == "edit" and permissions["manageMessagePerms"]):
        if (args[2] == "embed"):
          await moBotEmbed(message, args, True)
        else:
          try:
            msg = await message.channel.fetch_message(int(args[2]))
          except:
            await message.channel.send("Looks like something didn't go quite right... The command for editing a regular message is, `@MoBot#0697 edit [MessageID] [new_text]`. The command for editing an embed can be found using `@MoBot#0697 embed help`.")
          await msg.edit(content=message.content.split(args[2])[1].strip())
      elif (args[1] == "channel" and permissions["manageChannelPerms"]):
        channel = message.guild.get_channel(int(args[2]))
        await channel.edit(name=message.content.split(str(channel.id))[1].strip())
        try:
          await message.delete()
        except discord.errors.Forbidden:
          pass
      elif (args[1] == "nick" and permissions["changeNicknamePerms"]):
        if (message.guild.id == noble2sLeauge):
          await Noble2sLeague.setnick(message)
        else:
          await message.author.edit(nick=message.content.split("nick")[1].strip())
          try:
            await message.delete()
          except discord.errors.Forbidden:
            pass
      elif (args[1] == "monick" and isMo):
        await client.get_user(moBot).edit(nick=message.content.split(args[1]+" ")[1])
      # add a reaction to a message based on given id 
      elif (args[1] == "add"):
        if (args[2] == "reaction"):
          if (len(args) > 2):
            try:
              await message.delete()
            except discord.errors.Forbidden:
              pass
            await ReactionRole.addReactionToMessage(await message.channel.fetch_message(int(args[4])), args[3])
      # clear messages based on given count
      elif (args[1] == "clear" and permissions["manageMessagePerms"]):
        try:
          if (args[2] == "welcome" and args[3] == "messages"):
            await message.channel.trigger_typing()
            count = 0
            history = message.channel.history(before=message)
            async for msg in history:
              if (msg.type == discord.MessageType.new_member):
                count += 1
                await msg.delete()
            msg = await message.channel.send("Deleted " + str(count) + " messages.")
            await asyncio.sleep(3)
            await msg.delete()
            await message.delete()
          else:
            count = int(args[2]) + 1
            await message.channel.purge(limit=count)
        except discord.errors.Forbidden:
          await message.channel.send("**I need Manage Message permissions for this command.**")
      elif (args[1] == "delete" and permissions["manageMessagePerms"]):
        try:
          topMsgID = int(message.content.split("delete ")[1].split(" ")[0].strip())
          try:
            if ("delete" not in message.content.split(" ")[-2]):
              bottomMsgID = int(message.content.split(" ")[-1].strip())
            else:
              bottomMsgID = message.id
          except ValueError:
            bottomMsgID = message.id
          try:
            topMsg = await message.channel.fetch_message(topMsgID)
            bottomMsg = await message.channel.fetch_message(bottomMsgID)
            purged = await message.channel.purge(after=topMsg, before=bottomMsg)
            try:
              await topMsg.delete()
            except discord.errors.NotFound:
              pass
            try:
              await bottomMsg.delete()
            except discord.errors.NotFound:
              pass
            try:
              await message.delete()
            except discord.errors.NotFound:
              pass
            msg = await message.channel.send("Deleted " + str(len(purged) + 1) + " messages.")
            await asyncio.sleep(5)
            await msg.delete()
          except discord.errors.NotFound:
            await message.channel.send("Message Not Found -- Check the ID you gave -- For futher help, use `@MoBot#0697 help` -> General Use -> `@MoBot#0697 delete`")
          except AttributeError:
            topMsg = await message.channel.fetch_message(topMsgID)
            bottomMsg = await message.channel.fetch_message(bottomMsgID)
            history = message.channel.history(after=topMsg, before=bottomMsg)
            await topMsg.delete()
            async for msg in history:
              try:
                await msg.delete()
              except:
                pass
        except discord.errors.Forbidden:
          await message.channel.send("**I need Manage Message permissions for this command.**")
      # remove/add role to user
      elif (args[1] == "role" and permissions["manageRolePerms"]):
        r = args[3]
        user = client.get_user(int(args[4]))
        
        roles = message.guild.roles
        if (args[2] == "add"):
          for role in roles:
            if (role.id == int(r)):
              await user.add_roles(role)
        elif (args[2] == "remove"):
          for role in roles:
            if (role.id == int(r)):
              await user.remove_roles(role)
      elif (args[1] == "copy" and permissions["manageMessagePerms"]):
        await message.channel.trigger_typing()

        try:
          destChannel = message.guild.get_channel(int(message.content.split("#")[1].split(">")[0].strip())) # checked error statement

          msgIDs = message.content.split("copy")[1].strip().split("<#")[0].strip().split(" ")
          for msgID in msgIDs:
            if (msgID == "embed"):
              continue
            msg = await message.channel.fetch_message(int(msgID))
            if (msg.content != ""):
              content = msg.content
            else:
              content = None
            if (args[2] == "embed"):
              try:
                await destChannel.send(embed=msg.embeds[0], content=content)
              except IndexError:
                await message.channel.send("**No Embed in Message**\n<" + msg.jump_url + ">.")
            else:
              content = msg.content
              for attachment in msg.attachments:
                content += "\n" + attachment.url
              content += " " + spaceChar
              await destChannel.send(content=content)
        except IndexError:
          await message.channel.send("**No [#destination-channel] Given**\n\n`@MoBot#0697 copy [embed] [Message_ID] [#destination-channel]` *(`[embed]` is only needed if there is an embed in the source message)*")

      ## random commands
      elif (args[1] == "admin" and isMo):
        await AdminFunctions.main(args, message,client) 
      elif (args[1] == "avatar"):
        member = message.guild.get_member(int(args[2]))
        await message.channel.send(str(member.avatar_url))
      elif (args[1] == "hangman"):
        await Hangman.newGame(message, client)
      elif (message.content.split("> ")[1].strip() == "2 + 2"):
        msg = await message.channel.send("2 + 2 = 5")
        await asyncio.sleep(3)
        await msg.edit(content="2.4 + 2.4 = 4.8 = 5")
      elif (args[1] == "ping"):
        pong = await message.channel.send("pong")
        ping = message.created_at
        await asyncio.sleep(3)
        await message.channel.send("Well, was it slow?")
        await asyncio.sleep(1)
        await message.channel.send("ping was sent at " + str(ping) + "\n" + "pong was sent at " + str(pong.created_at))
      elif (args[1].lower() in questionWords):
        await moBotQuestions(message, args)
      elif (args[1] == "markdown"):
        if (args[2] == "emoji"):
          await message.channel.send("```" + message.content.split("emoji")[1].strip().replace(" ", "\"\n\"") + "```")
        else:
          await message.channel.send("```" + message.content.split("markdown")[1].strip() + "```")
          
      elif (args[1] == "ids"):
        reply = "**How to get IDs:**\n"
        reply += "Settings -> Appearance -> Developer Mode -> On\n\n"
        reply += "With Developer Mode you will be able to right click various 'things', or hold if you are on mobile. Upon right clicking you will see an option to 'Copy ID'. These IDs are used in many of MoBot's commands.\n\n"

        reply += "**Using IDs in Messages:**\n"
        reply += "@User = <@user_ID>\n"
        reply += "#channel = #channel_ID\n"
        reply += "@Role = <@&role_ID>"

        await message.channel.send(reply)
      elif (args[1] == "invite"):
        await message.channel.send("Invite <@449247895858970624> to your server\nhttps://discordapp.com/oauth2/authorize?client_id=449247895858970624&scope=bot&permissions=469920856")
      elif (args[1] == "help"):
        await Collections.displayCollection(message, False, "Help Menu", moBotSupport, False, client)
        #await prepareHelp(message, 1, 0)
      elif ((args[1] == "servers" or args[1] == "guilds") and isMo):
        guilds = client.guilds
        guildCount = len(guilds)
        memberCount = 0
        for i in range(len(guilds)):
          members = guilds[i].members
          joinDate = guilds[i].get_member(449247895858970624).joined_at
          guilds[i] = [guilds[i].name, len(members), joinDate]
          memberCount += len(members)

        reply = ""
        guilds.sort(key=lambda x:x[2])
        for i in range(len(guilds)):
          reply += "**" + guilds[i][0] + "** - " + str(guilds[i][1]) + " - " + guilds[i][2].strftime("%b %d %Y") + "\n"
        reply += "\nGuild Count: " + str(guildCount) + "\n"
        reply += "Member Count: " + str(memberCount) + "\n"

        await message.channel.send(reply)
      elif (args[1] == "embed"):
        if (args[2] == "help"):
          # its not that complex
          await message.channel.send("*<@" + str(message.author.id) + ">, trust me, it's less complex than it looks... :D*\nFirst, here's an example of an Embed with all the editable attributes MoBot offers.")
          await asyncio.sleep(1)

          # example embed
          moBotUser = client.get_user(int(moBot))
          embed = discord.Embed(colour=0xd1d1d1)
          embed.set_thumbnail(url=moBotUser.avatar_url)
          embed.set_author(name="Author Line", icon_url=moBotUser.avatar_url)
          embed.add_field(name="Field Name 1", value='Field Value 1\n' + spaceChar, inline=False)
          embed.add_field(name="Field Name 2", value='Field Value 2', inline=False)
          embed.set_image(url=message.author.avatar_url)
          embed.set_footer(text="Footer")
          await message.channel.send(embed=embed)

          await asyncio.sleep(2)

          reply1 = "**Detailed Embed Help**\nMoBot has the functionality to let a user send an embed. Fortunately, embeds have a lot of potential in what you can display with them, however, unfortunately, there is a lot of 'checking' MoBot has to do to understand what the user wants.\n\n__Embed Attributes__\n  - #Color (the colored line on the left)\n  - $$Author Icon$$\n  - !!Author Line!!\n  - %%Thumbnail%%\n  - @@Field Name@@\n  - Field Value\n  - &&Embed Picture&&\n  - ##Footer##\n\n__How to Send an Embed as <@449247895858970624>__\nWhat you see below must be followed exactly, each new element of the embed, must be separated by hitting the return key. *You should be able to copy and paste if you're on mobile - it's its own message.*"

          reply2 = "```@MoBot#0697 say embed #d1d1d1\n!!Author Line!!\n@@Field Name 1@@\nField Value 1\n\n@@Field Name 2@@\nField Value 2\n\n##Footer##\n$$author_picture_address$$\n%%thumbnail_picture_address%%\n&&big_picture_address&&```"

          reply3 = "***Note 1:** You are able to send an embed even if you don't have one of these attributes, for example if you didn't include @@Footer@@ it would just send everything else.*\n***Note 2:** In the edit embed 593862550861512704 command you are able to insert pictures without an address by inserting them into your message. More details below.*\n\n__How to Edit an Embed as <@449247895858970624>__\nThe edit embed 593862550861512704 command can only change one attribute at a time; however, if you are going to edit any of the field names/values they must all be re-typed in one message.\n\nExample: Insert/edit thumbnail picture\n```@MoBot#0697 edit embed 593862550861512704\n%%thumbnail_picture_address%%```\n***Note:** If you are inserting/editing pictures, you don't need the picture address; you are able to send the picture with the message, but just put %%%% instead.*\n\nExample: Editing the color\n```@MoBot#0697 edit embed 593862550861512704 #0000ff```\nExample: Editing the author line\n```@MoBot#0697 edit embed 593862550861512704 !!New_Author_Text!!```\n\n***Final Notes:** Unfortunately, embeds don't enable for tags anywhere except for the Field Value spots. For example, you can't have the clickable links like <@449247895858970624> or <#" + str(message.channel.id) + "> in places except for the Field Values.*"

          reply4 = "<@" + str(message.author.id) + ">, for future format referencing, use `@MoBot#0697 embed format`. It'll post the example embed, and the example `@MoBot#0697 say embed` command."

          await message.channel.send(reply1)
          await message.channel.send(reply2)
          await message.channel.send(reply3)
          await message.channel.send(reply4)
        if (args[2] == "format"):
          content = "Remember, you don't need every attribute of the embed, but make sure everything after the #color is on a new line as seen below. Feel free to copy and paste, then remove anything you don't want/need.```@MoBot#0697 say embed #ff0000\n!!Author Line!!\n@@Field Name 1@@\nField Value 1\n\n@@Field Name 2@@\nField Value 2\n\n##Footer##\n$$author_picture_address$$\n%%thumbnail_picture_address%%\n&&big_picture_address&&```"

          moBotUser = client.get_user(int(moBot))
          embed = discord.Embed(colour=0xd1d1d1)
          embed.set_thumbnail(url=moBotUser.avatar_url)
          embed.set_author(name="Author Line", icon_url=moBotUser.avatar_url)
          embed.add_field(name="Field Name 1", value='Field Value 1\n' + spaceChar, inline=False)
          embed.add_field(name="Field Name 2", value='Field Value 2', inline=False)
          embed.set_image(url=message.author.avatar_url)
          embed.set_footer(text="Footer")
          await message.channel.send(embed=embed, content=content)
      elif (args[1] == "bug"):
        if (len(args) > 2):
          await bugReport(message)
        else:
          await message.channel.send("If there was an issue with a MoBot function, please use `@MoBot#0697 bug [issue]` to submit a bug report.\nFeel free to include a screenshot, as well as what your input was, what happened, and what you thought should have happened.\n\n<@" + str(mo) + "> may reach out to you if he needs more information.")
      elif (args[1] == "send" and permissions["administratorPerms"]):
        if (args[2] == "collection"):
          await CollectionsOLD.sendCollection(message, args, True, client)
        elif(args[2] == "fail"):
          await CollectionsOLD.sendCollection(message, args, True, client)
      elif (args[1] == "test" and isMo):
        await test(message, client)

      ## MoBot promo commands
      elif (args[1].lower() == "donate"):
        await message.channel.send("I wouldn't mind a dollar...✌😎✌\n||<https://venmo.com/MoBot_>  ||\n||<https://paypal.me/MoShots>||\n\nFor just $2/month, or $15/year, you can ask for any custom commands you may want/need.")
      elif (args[1].lower() == "server"):
        await message.channel.send("Join my server... It's where you can see features that are in development and such, if you're into that... https://discord.gg/bgyEpEh")

    ## calling server specific file 
    if (str(message.guild.id) in servers):
      # the servers dict is imported from a text file, found in the folder MoBotServers.txt
      await eval(servers[str(message.guild.id)] + ".main(args, message, client)")

    if ((message.guild.id == cotm or message.guild.id == moBotSupport) and "<@" + str(moBot) + ">" in message.content):
      try:
        #await message.channel.send("```" + message.content + "```")
        await ReactionRole.addReactionToMessage(message, "🇲")
        await ReactionRole.addReactionToMessage(message, "🇴")
        await ReactionRole.addReactionToMessage(message, "🇧")
        await ReactionRole.addReactionToMessage(message, "🅾")
        await ReactionRole.addReactionToMessage(message, "🇹")
      except discord.errors.NotFound:
        pass

  if (message.author.id == mo):
    pass
# end on_message

@client.event
async def on_member_join(member):
  if (not isConnected):
    return

  if (str(member.guild.id) in autoRoles):
    await ReactionRole.addAutoRoleToUser(member, autoRoles[str(member.guild.id)]["RoleIDs"])

  if (str(member.guild.id) in servers):
    await eval(servers[str(member.guild.id)] + ".memberJoin(member)")
# end on_member_join

@client.event
async def on_member_remove(member):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    await eval(servers[str(member.guild.id)] + ".memberRemove(member)")
# end on_member_remove

# when a reactio is added to a message
@client.event
async def on_raw_reaction_add(payload):
  if (not isConnected):
    return
  
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id
  try:

    try:
      guild = client.get_guild(guildID)
      channel = guild.get_channel(channelID)
      msg = await channel.fetch_message(messageID)
      member = msg.guild.get_member(payload.user_id)
    except AttributeError:
      try:
        msg = await client.get_channel(channelID).fetch_message(messageID)
        member = client.get_user(payload.user_id)
      except AttributeError:  
        member = client.get_user(payload.user_id)
        msg = await member.send(".")
        await msg.delete()
        msg = await msg.channel.fetch_message(messageID)  
    except discord.errors.NotFound:
      return

    message = msg

    # needed embed stuff
    try:
      embedAuthor = str(message.embeds[0].author.name)
    except IndexError:
      embedAuthor = "None"

    try:
      embedFooter = str(message.embeds[0].footer.text)
    except IndexError:
      embedFooter = "None"

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"
    # end embed stuff

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"

    try:
      pName = payload.emoji.name if (payload.emoji.id == None) else "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
      msg = reactionMessages[pName][message.id]
      roles = message.guild.roles
      for role in roles:
        for roleID in msg["RoleID"][0]:
          if (role.id == int(roleID)):
            if (msg["RoleID"][1] == "add"):
              await member.add_roles(role)
              await message.channel.send(content="**" + role.name + " Role Added to " + member.mention + "**", delete_after=5.0)
            else:
              await member.remove_roles(role)
              await message.channel.send(content="**" + role.name + " Role Removed from " + member.mention + "**", delete_after=5.0)
    except KeyError:
      pass
    except discord.errors.Forbidden:
      await message.channel.send("Cannot add role, <@449247895858970624> does not have permission...")
      await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))

    if (not member.bot):
      logActionToConsole(message, member, "reactionAdd")
      if (len(message.embeds) > 0):
        if ("RLScrims" in embedAuthor):
          await RLScrims.mainReactionAdd(message, payload, client, member)

        elif (("MoBotCollection" in embedAuthorURL or "MoBotReservation" in embedAuthorURL) and message.author.id == int(moBot)):
          if (message.author.id == int(moBot)):
            await Collections.mainReactionAdd(message, payload, message.embeds[0], client)
            if ("MoBotReservation" in message.embeds[0].author.url):
              await Reservations.mainReactionAdd(message, payload, client)

        elif ("Countdown Editor" in embedAuthor):
          await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
        elif ("Clock Editor" in embedAuthor):
          await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "clock")
        elif ("•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
          if (payload.emoji.name == "⬅"):
            await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
          elif (payload.emoji.name == "➡"):
            await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)

      elif ("open a ticket" in message.content.lower()):
        if (payload.emoji.name == "✅"):
          await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
          await ticketManager.openTicket(message, member, True, client)
      elif ("Add Table" in message.content):
        await DiscordSheets.mainReactionAdd(message, payload, client)
      elif ("Message Scheduler" in message.content):
        await MessageScheduler.mainReactionAdd(message, payload, client)
      elif (len(message.embeds) > 0 and "Countdown Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "countdown")
      elif (len(message.embeds) > 0 and "Clock Editor" in embedAuthor):
        await ClocksAndCountdowns.mainReactionAdd(message, payload, client, "clock")
      elif (len(message.embeds) > 0 and "•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
        if (payload.emoji.name == "⬅"):
          await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
        elif (payload.emoji.name == "➡"):
          await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)

      if (str(message.guild.id) in servers):
        await eval(servers[str(message.guild.id)] + ".mainReactionAdd(message, payload, client)")

      if (payload.emoji.name == "🔄"):
        tableExists = False
        try:
          moBotTables = await DiscordSheets.getAllTables()
        except gspread.exceptions.APIError:
          await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
          msg = await message.channel.send("**Error Getting Table**\nTry again in a minute or so...")
          await asyncio.sleep(10)
          try:
            await msg.delete()
          except discord.errors.Forbidden:
            pass
        try:
          for table in moBotTables[str(guildID)]:
            for msgId in table["msgIds"].split(","):
              if (messageID == int(msgId)):
                tableExists = True
                await DiscordSheets.updateTable(message, table)
                await message.remove_reaction(payload.emoji, client.get_user(payload.user_id))
                msg = await message.channel.send("**Table Updated**")
                await asyncio.sleep(3)
                try:
                  await msg.delete()
                except discord.errors.Forbidden:
                  pass
                break
            if (tableExists):
              break
        except KeyError:
          pass
  except discord.errors.Forbidden:
    pass
# end on_reaction_add

@client.event
async def on_raw_reaction_remove(payload):
  if (not isConnected):
    return
  
  channelID = payload.channel_id
  messageID = payload.message_id
  guildID = payload.guild_id
  try:

    try:
      guild = client.get_guild(guildID)
      channel = guild.get_channel(channelID)
      msg = await channel.fetch_message(messageID)
      member = msg.guild.get_member(payload.user_id)
    except AttributeError:
      try:
        msg = await client.get_channel(channelID).fetch_message(messageID)
        member = client.get_user(payload.user_id)
      except AttributeError:  
        member = client.get_user(payload.user_id)
        msg = await member.send(".")
        await msg.delete()
        msg = await msg.channel.fetch_message(messageID)  

    message = msg

    # needed embed stuff
    try:
      embedAuthor = str(message.embeds[0].author.name)
    except IndexError:
      embedAuthor = "None"

    try:
      embedFooter = str(message.embeds[0].footer.text)
    except IndexError:
      embedFooter = "None"

    try:
      embedAuthorURL = str(message.embeds[0].author.url)
    except IndexError:
      embedAuthorURL = "None"
    # end embed stuff

    try:
      pName = payload.emoji.name if (payload.emoji.id == None) else "<:" + payload.emoji.name + ":" + str(payload.emoji.id) + ">"
      msg = reactionMessages[pName][message.id]
      roles = message.guild.roles
      for role in roles:
        for roleID in msg["RoleID"][0]:
          if (role.id == int(roleID)):
            if (msg["RoleID"][1] == "add"):
              await member.remove_roles(role)
              await message.channel.send(content="**" + role.name + " Role Removed from " + member.mention + "**", delete_after=5.0)
            else:
              await member.add_roles(role)
              await message.channel.send(content="**" + role.name + " Role Added to " + member.mention + "**", delete_after=5.0)
    except KeyError:
      pass
    except discord.errors.Forbidden:
      pass

    if (not member.bot or member.id == 476974462022189056):
      logActionToConsole(message, member, "reactionRemove")

      if (len(message.embeds) > 0 and "•" in embedFooter and "-- (" in embedFooter and ")" in embedFooter):
        if (payload.emoji.name == "⬅"):
          await CollectionsOLD.leftRightCollection(message, "left", message.embeds[0], client)
        elif (payload.emoji.name == "➡"):
          await CollectionsOLD.leftRightCollection(message, "right", message.embeds[0], client)  
      elif (len(message.embeds) > 0 and ("MoBotCollection" in embedAuthorURL or "MoBotReservation" in embedAuthorURL)):
        if (message.author.id == int(moBot)):
          await Collections.mainReactionRemove(message, payload, message.embeds[0], client)

      # calling server specific file but mainReactionRemove function instead of main
      elif (str(message.guild.id) in servers):
        await eval(servers[str(message.guild.id)] + ".mainReactionRemove(message, payload, client)")
  except discord.errors.NotFound:
    pass
# end on_reaction_remove

@client.event
async def on_member_update(before, after):
  if (not isConnected):
    return
  
  bRoles = before.roles
  aRoles = after.roles

  if (len(aRoles) > len(bRoles)):
    for role in aRoles:
      if (role not in bRoles):
        await on_member_role_add(after, role)
        break
  elif (len(bRoles) > len(aRoles)):
    for role in bRoles:
      if (role not in aRoles):
        await on_member_role_remove(after, role)
        break
  try:
    await eval(servers[str(before.guild.id)] + ".mainMemberUpdate(before, after, client)")
  except KeyError:
    pass
  except AttributeError:
    pass
# end on_member_update

# called in on_member_update
async def on_member_role_add(member, role):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    try:
      await eval(servers[str(member.guild.id)] + ".memberRoleAdd(member, role)")
    except AttributeError:
      pass
# end on_role_update

# called in on_member_update
async def on_member_role_remove(member, role):
  if (not isConnected):
    return
  
  if (str(member.guild.id) in servers):
    try:
      await eval(servers[str(member.guild.id)] + ".memberRoleRemove(member, role)")
    except AttributeError:
      pass
# end on_role_update

def logActionToConsole(message, user, logType):
  try:
    logMessage = str(datetime.now().strftime("%H:%M:%S.%f")) + " : G - " + str(message.guild) + " : C - " + str(message.channel)

    if (logType == "message"): 
      logMessage += " : MS - "
      if (str(message.author.id) != moBot and message.author.bot):
        return
    elif (logType == "reactionAdd"):
      logMessage += " : RA - "
    elif (logType == "reactionRemove"):
      logMessage += " : RR - "

    logMessage += str(user.display_name)
    if (len(message.guild.members) < 1000):
      print (logMessage)
  except AttributeError: # None type as message is in DM
    pass
# end logMessage

async def moBotQuestions(message, args):
  r = int(random.random() * 100)
  reply = questionWords[args[1].lower()][r % len(questionWords[args[1].lower()])][1]
  reply = reply[r % len(reply)]
  await message.channel.send(reply)
# end moBotQuestions

async def moBotEmbed(message, args, isEdit):
  mc = message.content
  empty = discord.Embed().Empty
  color = empty
  authorIcon = empty
  authorLine = None
  authorURL = None
  thumbnail = empty
  fields = []
  embedPicture = None
  footer = None
  embed = None
  isCollection = False
  isReservation = False
  if (isEdit):
    try:
      msg = None
      try:
        msg = await message.channel.fetch_message(int(args[3]))
      except discord.errors.NotFound:
        for channel in message.guild.channels:
          try:
            msg = await channel.fetch_message(int(args[3]))
            break
          except discord.errors.NotFound:
            pass
          except AttributeError:
            pass
      if (msg is None):
        await message.channel.send("**Message ID Not Found**")
        return
      mc = mc.replace(args[3] + " ", "")
      embed = msg.embeds[0]
      color = embed.color
      embed = embed.to_dict()

      try:
        authorIcon = embed["author"]["icon_url"]
      except KeyError:
        pass

      try:
        authorURL = embed["author"]["url"]
        isCollection = "MoBotCollection" in authorURL
        isReservation = "MoBotReservation" in authorURL
      except KeyError:
        pass

      try:
        descripton = embed["description"]
      except KeyError:
        pass

      try:
        authorLine = embed["author"]["name"]
      except KeyError:
        pass

      try:
        thumbnail = embed["thumbnail"]["url"]
      except KeyError:
        pass

      try:
        eFields = embed["fields"]
        for i in range(len(eFields)):
          fields.append([eFields[i]["name"], eFields[i]["value"]])
      except KeyError:
        pass

      try:
        embedPicture = embed["image"]["url"]
      except KeyError:
        pass

      try:
        footer = embed["footer"]["text"]
      except KeyError:
        pass

      embed = discord.Embed().from_dict(embed)
    except:
      await message.channel.send("Looks like something wasn't quite right... Either the MessageID you typed isn't correct, or the MessageID of the message doesn't have an embed already. You also need to be in the same channel as the embed. Use `@MoBot#0697 embed help` for further guidence.")
      return

  # get color
  try:
    color = int("0x" + mc.split("embed #")[1].split("\n")[0].strip(), 16)
  except IndexError:
    pass
  if (isEdit):
    embed.color = color
  else:
    embed = discord.Embed(color=color)

  # get author stuff
  try:
    authorIcon = mc.split("$$")[1].split("\n")[0].strip()
    authorIcon = authorIcon if (authorIcon != "") else empty

    try:
      authorIcon = message.attachments[0].url
    except IndexError:
      pass

  except IndexError:
    pass

  try:
    authorLine = mc.split("!!")[1].split("\n")[0].strip().replace("\\n", "\n")
  except IndexError:
    pass

  if (authorIcon != empty and authorLine == None):
    if (isCollection):
      embed.set_author(name=spaceChar, icon_url=authorIcon, url=authorURL)
    else:
      embed.set_author(name=spaceChar, icon_url=authorIcon)
  elif (authorLine != None):
    if (isCollection or isReservation):
      embed.set_author(name=authorLine, icon_url=authorIcon, url=authorURL)
    else:
      embed.set_author(name=authorLine, icon_url=authorIcon)
    
  try:
    description = mc.split("^^")[1].split("\n")[0].strip()
    embed.description = description.replace("\\n", "\n")
  except IndexError:
    pass

  # get footer
  try:
    footer = mc.split("##")[1].split("\n")[0].strip()
    embed.set_footer(text=footer)
  except IndexError:
    pass

  # get thumbnail
  try:
    thumbnail = mc.split("%%")[1].split("\n")[0].strip()

    if (thumbnail == ""):
      try:
        thumbnail = message.attachments[0].url
      except IndexError:
        thumbnail = None

    if (thumbnail == None):
      embed = embed.to_dict()
      try:
        embed.pop("thumbnail")
      except KeyError:
        pass
      embed = discord.Embed().from_dict(embed)
    else:
      embed.set_thumbnail(url=thumbnail)
  except IndexError:
    pass

  # get embed picture
  try:
    embedPicture = mc.split("&&")[1].split("\n")[0].strip()

    if (embedPicture == ""):
      try:
        embedPicture = message.attachments[0].url
      except IndexError:
        embedPicture = None

    if (embedPicture == None):
      embed = embed.to_dict()
      try:
        embed.pop("image")
      except KeyError:
        pass
      embed = discord.Embed().from_dict(embed)
    else:
      embed.set_image(url=embedPicture)
  except IndexError:
    pass

  newFields = []
  # get fields
  lines = mc.split("\n")
  symbols = ["!!", "^^", "@@", "##", "$$", "%%", "&&"]
  i = 1
  while (i < len(lines)):
    if (lines[i].strip() == ""):
      lines[i] = spaceChar

    fieldName = ""
    fieldValue = ""
    symbolInLine = False
    for symbol in symbols:
      symbolInLine = symbol in lines[i]
      if (symbolInLine):
        break

    if ("@@" in lines[i]):
      fieldName = lines[i].split("@@")[1].split("\n")[0].strip()

    elif (not symbolInLine):
      fieldName = spaceChar if (fieldName == "") else fieldName
      fieldValue = lines[i] + "\n"
    
    if (fieldName != ""):
      i += 1
      j = i
      while (j < len(lines)):
        if (lines[j].strip() == ""):
          lines[j] = spaceChar

        symbolInLine = False
        for symbol in symbols:
          symbolInLine = symbol in lines[j]
          if (symbolInLine):
            break

        if ("@@" in lines[j]):
          i = j
          break

        elif (not symbolInLine):
          fieldValue += lines[j] + "\n"
          i = j + 1
          j = i

        else:
          i = j + 1
          break
    else:
      i += 1

    if (fieldName != "" and fieldValue != ""):
      newFields.append([fieldName, fieldValue])
    elif (fieldName != "" and fieldValue == ""):
      newFields.append([fieldName, spaceChar])
  # end while

  fields = newFields if (newFields != []) else fields
  if (len(newFields) != 0):
    embed.clear_fields()
    for field in fields:
      embed.add_field(name=field[0].replace("\\n", "\n"), value=field[1].replace("\\n", "\n"), inline=False)

  try:
    if (isEdit):
      await msg.edit(embed=embed)
      await message.channel.send("**Message Edited**", delete_after=5.0)
      if (isCollection or isReservation):
        await Collections.replaceCollectionEmbed(message, msg.id, msg.id, client)
    else:
      msg = await message.channel.send(embed=embed)
      await message.channel.send("If you'd like to edit the embed above, in your original message, replace `say embed` with `edit embed " + str(msg.id) + "`. You don't need to copy and paste, or re-send the message, simply edit your original message, and press enter. You can also copy your embed to another channel by using `@MoBot#0697 copy embed  " + str(msg.id) + " [#destination-channel]`.")
  except discord.errors.HTTPException:
    await message.channel.send("Looks like something didn't go quite right... Discord has a limit on how long a message can be, 2000 characters  ... but there is also a limit on how big a field value can be, 1024 characters. If you have a large field value, perhaps adding another field header, and splitting the field value might work.")
# end moBotEmbed

async def bugReport(message):
  moBotSupportServer = client.get_guild(moBotSupport)
  bugReportChannel = moBotSupportServer.get_channel(593895342030716928)

  bug = str(message.guild.id) + "-" + str(message.channel.id) + "-" + str(message.author.id) + "\n\n**Bug Report:**\n"
  try:
    bug += message.content + "\n"
  except IndexError:
    pass

  bug += "\n**Attatchments:**\n"
  for i in message.attachments:
    bug += i.url + "\n" 
  await bugReportChannel.send(bug)
  await message.channel.send("Thank you for reporting a bug!\nJoin `@MoBot#0697 server` to stay updated on udpates and patches.")

async def test(message, client):
  msg = await message.channel.fetch_message(600812373212921866)
  print (msg.embeds[0].color)
# end test

print ("Connecting...")
client.run(SecretStuff.getToken("MoBotToken.txt"))