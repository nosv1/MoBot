# MoBot
This is MoBot - a custom Discord Bot.

Nah, but seriously, enjoy what is here. There's not many comments and it's a mess in the older files, but in case I die, now someone can else run this shit.

MoBot is a bot that hosts custom features for other servers. Instead of making multiple little bots, it has been found easier to have one bot for everything. MoBot isn't just for organization, it's not just for moderation, it's simply a jack of 'most' trades. It's contiously beeing updated to include more features per request, donation, and as seen fit.

Feel free to join the support server to stay up to date on all things MoBot https://discord.gg/bgyEpEh, or feel free to invite the bot yourself https://discordapp.com/oauth2/authorize?client_id=449247895858970624&scope=bot&permissions=469920856. 


# How MoBot Works, kinda
MoBot has two files that run all the time. The MoBot.py and the MoBotLoop.py.
MoBot.py is where the events are handeld like on_message, and on_member_join. This is where commands are handled and where MoBot controls what to do on certain events.

MoBotLoopy.py is, as the name suggests, a loop file. When the bot gets passed the on_ready event, an infinite loop is statrted; it runs the clocks and does checks to manage functions based on time. 
