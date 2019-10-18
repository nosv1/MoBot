import subprocess

def foo():
  p = subprocess.Popen(["python", "D:/Users/Nick/OneDrive/GTA Stuff/Bots/MoBot/MoBot/MoBot.py"], shell=True, stdout=subprocess.PIPE)
  p = subprocess.Popen(["python", "D:/Users/Nick/OneDrive/GTA Stuff/Bots/MoBot/MoBot/MoBotLoop.py"], shell=True, stdout=subprocess.PIPE)

foo()