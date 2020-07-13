import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector

import SecretStuff
import MoBotDatabase
import RandomSupport

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

spaceChar = "⠀"

async def sayEmbed(message, args, isEdit):
  mc = message.content
  empty = discord.Embed().Empty
  color = message.guild.get_member(moBot).roles[-1].color
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

async def editMessage(message, args):
  msg = None
  try:
    msg = await message.channel.fetch_message(int(args[2]))
  except discord.errors.NotFound:
    for channel in message.guild.channels:
      try:
        msg = await channel.fetch_message(int(args[2]))
        break
      except discord.errors.NotFound:
        pass
      except AttributeError:
        pass
  if (msg is None):
    await message.channel.send("Looks like something didn't go quite right... The command for editing a regular message is, `@MoBot#0697 edit [MessageID] [new_text]`. The command for editing an embed can be found using `@MoBot#0697 embed help`.")
  else:
    try:
      await msg.edit(content=message.content.split(args[2])[1].strip())
    except discord.errors.HTTPException: # trying to edit with blank message
      await message.channel.send("Looks like something didn't go quite right... The command for editing a regular message is, `@MoBot#0697 edit [message_id] [new_text]`. The command for edidint an embed can be found using `@MoBot#0697 embed help`.")
# end editMessage

async def clearMessages(message, args):
  try:
    if (args[2] == "welcome" and args[3] == "messages"):
      await message.channel.trigger_typing()
      msg = await message.channel.send("Deleted " + str(clearWelcomeMessages(message.channel)) + " messages.", delete_after=3)
      await message.delete()
    else:
      count = int(args[2]) + 1
      await message.channel.purge(limit=count)
  except discord.errors.Forbidden:
    await message.channel.send("**I need `Manage Messages` permissions for this command.**")
# end clearMessages 

async def deleteMessages(message):
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
      msg = await message.channel.send("Deleted " + str(len(purged) + 1) + " messages.", delete_after=5)
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
    await message.channel.send("**I need `Manage Messages` permissions for this command.**")
# end deleteMessages

async def deleteCategory(message, args):
  category = None
  for c in message.guild.categories:
    if str(c.id) in message.content:
      category = c
      break
  
  if not category:
    try:
      channel = message.guild.get_channel(int(args[3]))
      category = channel.category
    except:
      await message.channel.send("Cannot proceed... Likely the category_id or the channel_id you provided does not exist. If you are trying to delete all the channels in a category, use `@MoBot#0697 delete category <category_id>` `@MoBot#0697 delete category 717457000832958464`")
      return

  if category:
    try:
      await message.channel.send(f"Deleting channels in {category.name}.")
      for channel in category.channels:
        await channel.delete()
      await message.channel.send(f"All channels have been deleted in {category.name}.")
    except:
      await message.channel.send(f"Cannot proceed... Likely {message.guild.get_member(moBot).mention} does not have permission to 'Manage Channels'")
# end deleteCategory

async def addRemoveRole(message, args):
  r = args[3]
  try:
    member = message.guild.get_member(int(args[4]))
  except ValueError:
    member = None
  
  roles = message.guild.roles
  for role in roles:
    if (role.id == int(r)):
      if (member is None): # add role to everyone

        msg = None
        if (args[2] == "add"):
          msg = await message.channel.send("**Adding `%s` to `everyone`. It may take a moment.**" % role.name)
          for member in message.guild.members:
            try:
              await member.add_roles(role)
            except discord.errors.Forbidden:
              await message.channel.send("Could not add role to %s." % member.mention)

        if (args[2] == "remove"):
          msg = await message.channel.send("**Removing `%s` from `everyone`. It may take a moment.**" % role.name)
          for member in message.guild.members:
            try:
              await member.remove_roles(role)
            except discord.errors.Forbidden:
              await message.channel.send("Could not add role to %s." % member.mention)
        await message.channel.send("Done.", delete_after=5)
        if (msg is not None):
          await msg.delete()

      else:
        if (args[2] == "add"):
          await member.add_roles(role)
          await message.channel.send("**`%s` added to %s.**" % (role.name, member.display_name), delete_after=3)
        if (args[2] == "remove"):
          await member.remove_roles(role)
          await message.channel.send("**`%s` removed from %s.**" % (role.name, member.display_name), delete_after=3)
      break
# end addRemoveRole

async def copyMessage(message, args):
  await message.channel.trigger_typing()

  try:
    destChannel = message.guild.get_channel(int(message.content.split("#")[1].split(">")[0].strip())) # checked error statement

    msgIDs = message.content.split("copy")[1].strip().split("<#")[0].strip().split(" ")
    for msgID in msgIDs:
      if (msgID == "embed"):
        continue
      msg = await findMessageInGuild(message, msgID)
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
    await message.channel.send("**No `[#destination-channel]` Given**\n\n`@MoBot#0697 copy [embed] [Message_ID] [#destination-channel]` *(`[embed]` is only needed if there is an embed in the source message)*")
# end copyMessage

async def replaceMessage(message, args):
  await message.channel.trigger_typing()

  async def replaceMsg(oldMessage, newMessage):
    try:
      try:
        await oldMessage.edit(content=newMessage.content, embed=newMessage.embeds[0])
      except IndexError: # when there is no embed
        await oldMessage.edit(content=newMessage.content)
      await message.channel.send("**Message Replaced in <#%s>**" % oldMessage.channel.id)
    except discord.errors.Forbidden:
      await message.channel.send("**@MoBot#0697 can only edit its own messages.**")
  # end replaceMsg

  oldMessages = args[args.index("replace")+1:-1]
  newMessage = await findMessageInGuild(message, int(args[-1]))
  if (oldMessages):
    for i in range(len(oldMessages)):
      try:
        await replaceMsg(await findMessageInGuild(message, int(oldMessages[i].strip())), newMessage)
      except ValueError: # when user didn't provide int
        await message.channel.send("**%s is not a `[Message_ID]`**" % oldMessages[i])
        return
  else:
    await message.channel.send("**Only 1 `Message_ID` given.**\n`@MoBot#0697 [Old_Message_ID Old_Message_ID ...] [New_Message_ID]`")
# end replaceMessage

async def findMessageInGuild(message, messageID):
  try:
    msg = await message.channel.fetch_message(int(messageID))
  except discord.errors.NotFound:
    for channel in message.guild.text_channels:
      try:
        msg = await channel.fetch_message(int(messageID))
        break
      except discord.errors.NotFound:
        pass
  return msg
# end findMessageInGuild

async def clearWelcomeMessages(channel):
  history = channel.history()
  count = 0
  async for msg in history:
    if (msg.type == discord.MessageType.new_member):
      count += 1
      await msg.delete()
  return count
# end clearWelcomeMessages

async def pingRole(message, authorPerms):
  return
  moBot_messages = []

  # check for manage message perm
  if authorPerms.manageMessages: # has perm
    
    for role in message.guild.roles:
      if " @%s" % role.name.lower() in " %s " % message.content.lower() and not role.mentionable: # role in message and to avoid trying to mention a role that is mentionable, idk
        
        try:
          moBot_messages.append(await message.channel.send("**Preparing to Ping Unpingable Role**"))

          moBot_messages.append(await message.channel.send("**Creating Temporary Role: `Temp %s`**" % role.name))
          temp_role = await message.guild.create_role(
            name="Temp %s" % role.name,
            mentionable=True
            )

          moBot_messages.append(await message.channel.send("**Adding `%s` `%s` Users to `%s`**\nThis may take some time..." % (
            len(role.members),
            role.name,
            temp_role.name
          )))


          quarterDone = int(len(role.members) / 4)
          for i, member in enumerate(role.members):
            try:
              await member.add_roles(temp_role)
            except discord.errors.Forbidden:
              await message.channel.send("**Unable to Add Role to %s (Ghost Pinging)**" % member.mention, delete_after=3)
            except: # in case member leaves whilst in pinging process, i think it'll be add_roles to NoneType
              pass

            if i in [quarterDone * i for i in range(1, 4)]:
              moBot_messages.append(await message.channel.send("**%s of %s Users Added to `%s`**" % (i, len(role.members), temp_role.name)))

          moBot_messages.append(await message.channel.send(temp_role.mention))
          moBot_messages.append(await message.channel.send("**Unpingable Role Pinged**"))

          await temp_role.delete()
          moBot_messages.append(await message.channel.send("**`%s` Deleted**" % temp_role.name))

          await RandomSupport.deleteMoBotMessages(moBot_messages)

        except discord.errors.Forbidden:
          await message.channel.send("**Could Not Ping Un-pingable Role**\n%s needs to create a temporary role, but it does not have have the `Manage Roles` permission.", delete_after=7)
# end pingRole