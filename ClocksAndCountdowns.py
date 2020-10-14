import discord
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import re
import traceback

import SecretStuff
import MoBotDatabase
import RandomSupport

mo = 405944496665133058
mobot = 449247895858970624
mobot_support_server = 467239192007671818
mobot_timezone_channel = 607323514042712074
mobot_timezone_message = 607323599925149706

space_char = "⠀"

time_zones = [
  "US/Pacific", "US/Mountain", "US/Eastern", "America/Argentina/Buenos_Aires", "UTC", "Europe/London", "Europe/Amsterdam", "Asia/Vientiane", "Japan", "Australia/Queensland", "Australia/Sydney"
]

class Clock:
  def __init__(self, message_id, channel_id, guild_id, time_format, time_zone):
    self.message_id = int(message_id)
    self.channel_id = int(channel_id)
    self.guild_id = int(guild_id)
    self.time_format = time_format.replace("_", " ")
    self.time_zone = time_zone.replace("|", "/")
# end Clock


''' DISCORD FUNCTIONS '''
async def main(args, message, client):
  if len(args) == 2: # @mobot clock/countdown
    if args[1] == "clock":
      await createClock(message)
    elif args[1] == "countdown":
      await message.channel.send("Countdowns have not been implemented yet - coming very soon.")
# end main

async def mainReactionAdd(message, payload, client, clock_countdown):
  if clock_countdown == "clock":
    if payload.emoji.name in RandomSupport.numberEmojis[1:2+1]:
      await editClockEmbed(message, payload)

    elif payload.emoji.name == RandomSupport.FLOPPY_DISK_EMOJI:
      clock = saveClock(getClockFromURL(message.embeds[0].author.url))
      if clock:
        await updateClock(client, clock, datetime.utcnow())
        await message.channel.send("**Clock Saved and Updated**", delete_after=5)

    await message.remove_reaction(payload.emoji.name, message.guild.get_member(payload.user_id))
# end mainReactionAdd



''' ACTIONS '''
def defaultEditClockEmbed(message, clock):
  mobot_member = message.guild.get_member(mobot)

  embed = discord.Embed()
  color = mobot_member.roles[-1].color
  embed.set_author(
    name="MoBot Clock Editor", 
    icon_url=mobot_member.avatar_url, 
    url=f"https://google.com/message_id={clock.message_id}/channel_id={clock.channel_id}/guild_id={clock.guild_id}/time_format={clock.time_format.replace(' ', '_')}/time_zone={clock.time_zone}"
  )

  embed.description = f"""
**Available Time Zones:**
`{"` - `".join(time_zones)}`
*type any of these time zones exactly as they appear above*

**Time Format Key:**
{space_char * 2}%H - 24-hour clock (zero-padded)
{space_char * 2}%I - 12-hour clock (zero-padded)
{space_char * 2}%p - AM or PM indicator
{space_char * 2}%M - minute (zero-padded)
{space_char * 2}%Z - time zone
{space_char * 2}%d - day of month (zero-padded)
{space_char * 2}%a - weekday's abbreviated name
{space_char * 2}%A - weekday's full name
{space_char * 2}%b - month's abbreviated name
{space_char * 2}%B - month's full name
*can do these in any order with any characters in between, but letter casing does matter*
[__full list of format codes__](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)

---

**Instructions:**
1. Type the input.
2. Click the button related to the input.

**Example - Setting Time Zone:**
1. Type an available time zone (listed above), `US/Eastern`
2. Click the {RandomSupport.numberEmojis[1]}

**Example - Setting Time Format:**
1. Type your preferred format, `%H:%M %Z - %B %d`
{space_char * 2}a. This would be displayed as 24-hour clock with abbreviated time zone, full month name, and day of the month.
{space_char * 2}b. 12:34 EDT - May 21
2. Click the {RandomSupport.numberEmojis[2]}

---

**Clock Details:**
"""

  embed.add_field(
    name=f"{RandomSupport.numberEmojis[1]} Time Zone", 
    value=f"{space_char * 2}{clock.time_zone}", 
    inline=False
  )
  embed.add_field(
    name=f"{RandomSupport.numberEmojis[2]} Time Format", 
    value = "%s%s -> %s " % (space_char * 2, clock.time_format, timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(clock.time_zone)).strftime(clock.time_format)),
    inline=False
  )

  embed.set_footer(text=f"| {RandomSupport.FLOPPY_DISK_EMOJI} - Save Clock |")

  return embed
# end defaultEditClockEmbed

async def editClockEmbed(message, payload):
  embed = message.embeds[0]

  if payload: # is None from createClock
    detail = await getDetailFromHistory(message, payload.user_id)

    if detail:
      if payload.emoji.name == RandomSupport.numberEmojis[1]:
        if detail in time_zones:
          embed = RandomSupport.updateDetailInURL(embed, "time_zone", detail.replace("/", "|"))
          embed =RandomSupport.updateFieldValue(embed, "Time Zone", f"{space_char* 2}{detail}")
        else:
          await message.channel.send(f"The time zone `{detail}` is not availble.", delete_after=7)

      elif payload.emoji.name == RandomSupport.numberEmojis[2]:
        embed = RandomSupport.updateDetailInURL(embed, "time_format", detail.replace(" ", "_"))
        
        clock = getClockFromURL(embed.author.url)
        embed = RandomSupport.updateFieldValue(
          embed, 
          "Time Format", 
          "%s%s -> %s " % (space_char * 2, detail, timezone("UTC").localize(datetime.utcnow()).astimezone(timezone(clock.time_zone)).strftime(clock.time_format))
        )

      await message.edit(embed=embed)
  for i in range(2):
    await message.add_reaction(RandomSupport.numberEmojis[i+1])
  await message.add_reaction(RandomSupport.FLOPPY_DISK_EMOJI)
# end editClock

async def createClock(message):
  await message.channel.trigger_typing()

  mobot_member = message.guild.get_member(mobot)

  time_zone = "UTC"
  time_format = "%H:%M %Z"

  embed = discord.Embed()
  embed.color = mobot_member.roles[-1].color
  embed.set_author(name="UTC", url=f"https://google.com/message_id=None/channel_id={message.channel.id}/guild_id={message.guild.id}/time_format={time_format.replace(' ', '_')}/time_zone={time_zone.replace('/', '|')}/")

  time = timezone(time_zone).localize(datetime.utcnow()).astimezone(timezone(time_zone)).strftime(time_format)
  embed.description = time
  msg = await message.channel.send(embed=embed)
  embed = RandomSupport.updateDetailInURL(embed, "message_id", msg.id)
  await msg.edit(embed=embed)

  clock = getClockFromURL(embed.author.url)

  mobot_db = connectDatabase()
  mobot_db.cursor.execute(f"""
    INSERT INTO clocks (
      `message_id`, `channel_id`, `guild_id`, `guild_name`, `time_format`, `time_zone`
    ) VALUES (
      '{clock.message_id}',
      '{clock.channel_id}',
      '{clock.guild_id}',
      '{message.guild.name.replace('\'','\'\'')}',
      '{clock.time_format.replace("_", " ")}',
      '{clock.time_zone}'
    )
  """)
  mobot_db.connection.commit()
  mobot_db.connection.close()

  embed = defaultEditClockEmbed(message, clock)
  msg = await message.channel.send(embed=embed)
  await editClockEmbed(msg, None)
  await message.channel.send("```fix\nMo: Yes I know it looks complicated; it's not. Look at the instructions and the examples for guidance.```", delete_after=60)
# end createClock

async def updateClock(client, clock, time): # time should be UTC
  guild = client.get_guild(clock.guild_id)
  channel = guild.get_channel(clock.channel_id)
  message = await channel.fetch_message(clock.message_id)

  mobot_member = guild.get_member(mobot)

  embed = message.embeds[0]
  embed.set_author(name=clock.time_zone, url=f"https://google.com/message_id={clock.message_id}/channel_id={clock.channel_id}/guild_id={clock.guild_id}/time_format={clock.time_format.replace(' ', '_')}/time_zone={clock.time_zone}")
  embed.color = mobot_member.roles[-1].color

  tz = clock.time_zone
  converted_time = timezone("UTC").localize(time).astimezone(timezone(tz))
  time = converted_time.strftime(clock.time_format)
  embed.description = re.sub(r"-(?=\d\d)", "UTC-", time.replace("+", "UTC+"))
  await message.edit(embed=embed)
# end updateClock



''' SUPPORT FUNCTIONS '''
def saveClock(clock):
  mobot_db = connectDatabase()
  mobot_db.cursor.execute(f"""
    UPDATE clocks SET 
      `time_format` = '{clock.time_format}',
      `time_zone` = '{clock.time_zone}'
    WHERE `message_id` = '{clock.message_id}'
    ;
  """)
  mobot_db.connection.commit()
  mobot_db.connection.close()
  return clock
# end saveClockFromURL

def getClockFromURL(url):
  return Clock(
    RandomSupport.getDetailFromURL(url, "message_id"),
    RandomSupport.getDetailFromURL(url, "channel_id"),
    RandomSupport.getDetailFromURL(url, "guild_id"),
    RandomSupport.getDetailFromURL(url, "time_format"),
    RandomSupport.getDetailFromURL(url, "time_zone"),
  )
# end getClockFromURL

async def getDetailFromHistory(message, user_id):
  history = await message.channel.history(after=message, oldest_first=False).flatten()
  for msg in history:
    if (msg.author.id == user_id):
      return msg.content
# end getDetailFromHistory

def getClock(clock_message_id):
  clocks = getClocks()
  for clock in clocks:
    if str(clock.message_id) == str(clock_message_id):
      return clock
# end getClock

def getClocks():
  mobot_db = connectDatabase()

  clocks = []
  mobot_db.cursor.execute("""
    SELECT
      `message_id`, `channel_id`, `guild_id`, `time_format`, `time_zone` 
    FROM clocks
  """)
  for r in mobot_db.cursor:
    try:
      clocks.append(Clock(*r))
    except ValueError: # should never happen, but likley when id is none
      print("CAUGHT EXCEPTION")
      print(traceback.format_exc())
      pass

  mobot_db.connection.close()
  return clocks
#end getClocks

async def clockCheck(client):
  timezone_channel = client.get_guild(mobot_support_server).get_channel(mobot_timezone_channel)
  timezone_msg = await timezone_channel.fetch_message(mobot_timezone_message)
  return timezone_msg.edited_at
# end clockCheck



''' RESOURCES '''
def connectDatabase():
  return MoBotDatabase.connectDatabase("MoBot")
# end connectDatabase