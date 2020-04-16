import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import sys
import traceback

import SecretStuff
import MoBotDatabase

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

# MESSAGES
PRIVATE_CHANNEL_CREATION = 700018067866124318

# EMOJIS 
SHOPPING_CART = "🛒"

spaceChar = "⠀"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()

  if str(moBot) in args[0]:
    if "inventory"in args[1].lower():
      await updateInventory(args, message, client)

# end main

async def mainReactionAdd(message, payload, client): 
  if message.id == PRIVATE_CHANNEL_CREATION:
    if payload.emoji.name == SHOPPING_CART:
      await createPrivateChannel(message, payload, client)
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

async def createPrivateChannel(message, payload, client):
  await message.channel.trigger_typing()
  user = message.guild.get_member(payload.user_id)

  channel = await message.guild.create_text_channel(
    f"inventory-{user.discriminator}", 
    overwrites={
      message.guild.get_role(message.guild.roles[0].id) : discord.PermissionOverwrite(read_messages=False),
      user : discord.PermissionOverwrite(
        read_messages=True,
        send_messages=True),
    },
    category=message.channel.category,
    position=sys.maxsize
  )

  await channel.send(f"{user.mention}, use `@MoBot#0697 inventory [code-name] [item] [quantity]` to update the inventory.\nEx. `@MoBot#0697 inventory [Testing] [Pistol] [-2]`")
# end createPrivateChannel

async def updateInventory(args, message, client):
  try:
    user_code_name = message.content.split("[")[1].split("]")[0].lower()
    user_item = message.content.split("[")[2].split("]")[0].lower()
    user_quantity = int(message.content.split("[")[3].split("]")[0])
  except:
    await message.channel.send("There was an error getting the code-name/item/quantity.\nEx. `&mobot inventory [Anarchy] [Pistol] [-2]`")
    return

  try:
    workbook = openSpreadsheet()
    sheets = workbook.worksheets()

    code_name_list_sheet = [sheet for sheet in sheets if sheet.id == 928459361][0]
    item_list_sheet = [sheet for sheet in sheets if sheet.id == 1204918089][0]
    inventory_sheet = [sheet for sheet in sheets if sheet.id == 489431694][0]

    item_list_range = item_list_sheet.range(f"B2:B{item_list_sheet.row_count}")
    item = [cell.value for cell in item_list_range if cell.value.lower() == user_item.lower()] # may be empty if bad item

    code_name_list_range = code_name_list_sheet.range(f"A2:B{code_name_list_sheet.row_count}")
    code_name = None
    for i in range(0, len(code_name_list_range), 2):
      if code_name_list_range[i].value == "":
        break
      
      if code_name_list_range[i].value.lower() in message.author.display_name.lower():
        code_name = code_name_list_range[i+1].value
        break

    if code_name: # discord name on spreadsheet 
      if code_name.lower() == user_code_name: # matching code names
        if item: # valid item
          if user_quantity != 0: # non zero
            inventory_range = inventory_sheet.range(f"A4:C{inventory_sheet.row_count}")
            for i, cell in enumerate(inventory_range):
              if cell.value == "":
                inventory_range[i].value = code_name
                inventory_range[i+1].value = item[0]
                inventory_range[i+2].value = user_quantity
                inventory_sheet.update_cells(inventory_range, value_input_option="USER_ENTERED")
                await message.channel.send(f"Inventory Updated\n`{code_name}` `{item[0]}` `{user_quantity}`")
                return
          else:
            await message.channel.send(f"Could not proceed. The given quantity must be non-zero.")
        else:
          await message.channel.send(f"Could not proceed. The given item name, `{user_item.title()}`, does not match any of the items on the spreadsheet.")
      else:
        await message.channel.send(f"Could not proceed. The given code name, `{user_code_name.title()}`, does not match the code name for your name on the spreadsheet.")
    else:
      await message.channel.send("Could not proceed. Your discord name does not contain any of the names listed on the spreadsheet.")

  except gspread.exceptions.APIError:
    print("\n" + str(datetime.now()) + "\nError -- " + str(traceback.format_exc()))
    sys.exit()
    await message.channel.send("There was a technical difficulty sending the information to the spreadsheet. Please try again in a moment.\nYou should be able to simply add a `.` or some character (not a space) to the end of your message to run the command again without having to retype or copy-paste.")
    return
# end updateInventory

def openSpreadsheet():
  scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
  creds = ServiceAccountCredentials.from_json_keyfile_name(SecretStuff.getJsonFilePath('MoBot_secret.json'), scope)
  clientSS = gspread.authorize(creds)  
  workbook = clientSS.open_by_key("1mpMyYLllzQH30RGkAR3Uuv3rwdAIUidT98LOBQvsGkE")
  return workbook
# end openSpreadsheet