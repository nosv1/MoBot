import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
from numpy import exp, dot, random, array
import random

import SecretStuff
import MoBotDatabase

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

spaceChar = "⠀"

async def main(args, message, client):
  now = datetime.now()
  for i in range(len(args)):
    args[i].strip()
# end main

async def mainReactionAdd(message, payload, client): 
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

def play(mode):
  def checkForWinner(board):
    checks = []

    diagCheck1 = []
    diagCheck2 = []

    for i in range(3): 
      diagCheck1.append(board[i+(i*3)])
      diagCheck2.append(board[i*2+2])

      rowCheck = []
      colCheck = []

      for j in range(3):
        rowCheck.append(board[i*3+j])
        colCheck.append(board[j*3+i])

      checks.append(rowCheck)
      checks.append(colCheck)

    checks.append(diagCheck1)
    checks.append(diagCheck2)

    winner = None
    for check in checks:
      checkSpot = None
      i = 0
      while True:
        checkSpot = check[i]
        if (checkSpot == " "):
          break

        i += 1
        if (checkSpot != check[i]):
          break
        elif (i is 2):
          if (checkSpot == check[i]):
            winner = check[i]
            return winner
          break
    return winner
  # end checkForWinner

  def displayBoard(board):
    for i in range(0, 9, 3):
      print("|".join(board[i:i+3]))
  # end displayBoard

  def goPlayer(mode, players, playerTurn, board):
    def checkIfOpen(spot, board):
      return board[spot] == " "
    # end checkIfOpen

    while True:
      if (mode is 1):
        spot = random.randint(0, 8)

      if (checkIfOpen(spot, board)):
        board[spot] = "X" if ((playerTurn + 1) // 2 is 0) else "O"
        return board
  # end goPlayerOne

  players = []
  r = random.random()
  if (mode is 1):
    players = ["PC1", "PC2"]
  else:
    if (r > .5):
      players = ["PC1", "Human"]
    else:
      players = ["Human", "PC2"]

  print("\nX: %s\nO: %s\n" % (players[0], players[1]))

  board = [" "] * 9

  playerTurn = 1
  while True: # game loop
    playerTurn = playerTurn * -1

    print("Go %s" % ("X" if ((playerTurn + 1) // 2 is 0) else "O"))
    board = goPlayer(mode, players, playerTurn, board)
    displayBoard(board)

    winner = checkForWinner(board)
    if (winner is not None):
      return "Winner: %ss" % winner
    input()
  # end while
# end play

print(play(1))
#play(int(input("PC vs PC: 1\nHuman vs PC: 2\nChoose 1 or 2: ")))