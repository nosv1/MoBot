import discord
import asyncio
from datetime import datetime
import gspread 
from oauth2client.service_account import ServiceAccountCredentials
import mysql.connector
import random

import SecretStuff

moBot = 449247895858970624
moBotTest = 476974462022189056
mo = 405944496665133058

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

def mazeBuilder(size):

  def buildMazeFromSquares(squares):
    maze = ""
    for i in range(len(squares)): # each row
      for j in range(3): # each part in square ( top, leftside/rightside, bottom)
        for k in range(len(squares[i])): # each square in row
          if (j in [0, 2]):
            if (j == 0):
              maze += squares[i][k][0]
            elif (j == 2):
              maze += squares[i][k][-1]
          else:
            maze += "".join(squares[i][k][1:3])
        maze += "\n"
    return maze
  # end buildMazeFromSquares

  def buildBaseMaze(size):
    squares = []
    for i in range(size):
      squares.append([])
      for j in range(size):
        squares[i].append(["----", "| ", " |", "----"])
    return squares
  # end buildBaseMaze

  def generateStart(squares):
    startSquare = random.randint(0, size*4-4)

    square = -1
    while (square <= startSquare):
      for i in range(size): # loop thruogh top
        square += 1
        if (square == startSquare):
          if (i == 0): # top left
            squares[0][i][0] = "-  -" # top
            squares[0][i][1] = "  " # left
          elif (i == size-1):  # top right
            squares[0][i][0] = "-  -" # top
            squares[0][i][2] = "  " # right
          else:
            squares[0][i][0] = "-  -" # top
          squares = generateRoute(squares, size, 0, i)
          break

      for i in range(size): # loop thruogh bottom
        square += 1
        if (square == startSquare):
          if (i == 0): # bottom left
            squares[-1][i][-1] = "-  -" # bottom
            squares[-1][i][1] = "  " # left
          elif (i == size-1):  # bottom right
            squares[-1][i][-1] = "-  -" # bottom
            squares[-1][i][2] = "  " # right
          else:
            squares[-1][i][-1] = "-  -"
          squares = generateRoute(squares, size, size-1, i)
          break

      for i in range(1, size-1): # loop through left
        square += 1
        if (square == startSquare):
          squares[i][0][1] = "  "
          squares = generateRoute(squares, size, i, 0)
          break

      for i in range(1, size-1): # loop through right
        square += 1
        if (square == startSquare):
          squares[i][-1][2] = "  "
          squares = generateRoute(squares, size, i, size-1)
          break
    return squares
  # end generateStart

  def generateRoute(squares, size, i, j): # i = row, j = square in row
    def isEdge(size, newSquare):
      return (
        newSquare[0] in [-1, size] or 
        newSquare[1] in [-1, size]
      )
    # end isEdge
  
    def goToSquare(r, squares, i, j, newSquare):
      def isClosed(r, i, j):
        if (r is 0): # up
          return squares[i][j][0] == "----" # top wall
        elif (r is 1): # right
          return squares[i][j][2] == " |" # right wall
        elif (r is 2): # down
          return squares[i][j][-1] == "----" # bottom wall
        elif (r is 3): # left
          return squares[i][j][1] == "| " # left wall
      # end isClosed

      if (r is 0): # up
        if (isClosed(r, i, j)):
          squares[i][j][0] = "-  -"
          squares[newSquare[0]][newSquare[1]][-1] = "-  -"
        else:
          squares[i][j][0] = "----"
          squares[newSquare[0]][newSquare[1]][-1] = "----"
      if (r is 1): # right
        if (isClosed(r, i, j)):
          squares[i][j][2] = "  "
          squares[newSquare[0]][newSquare[1]][1] = "  "
        else:
          squares[i][j][2] = " |"
          squares[newSquare[0]][newSquare[1]][1] = "| "
      if (r is 2): # down
        if (isClosed(r, i, j)):
          squares[i][j][-1] = "-  -"
          squares[newSquare[0]][newSquare[1]][0] = "-  -"
        else:
          squares[i][j][-1] = "----"
          squares[newSquare[0]][newSquare[1]][0] = "----"
      if (r is 3): # left
        if (isClosed(r, i, j)):
          squares[i][j][1] = "  "
          squares[newSquare[0]][newSquare[1]][2] = "  "
        else:
          squares[i][j][1] = "| "
          squares[newSquare[0]][newSquare[1]][2] = " |"

      return squares
    # end goToSquare

    def breakEdgeWall(size, squares, newSquare):      
      newSquare[0] = 0 if (newSquare[0] <= 0) else newSquare[0]
      newSquare[0] = size-1 if (newSquare[0] >= size-1) else newSquare[0]
      newSquare[1] = 0 if (newSquare[1] <= 0) else newSquare[1]
      newSquare[1] = size-1 if (newSquare[1] >= size-1) else newSquare[1]

      if (newSquare[0] <= 0): # top row
        squares[0][newSquare[1]][0] = "-  -"
      if (newSquare[0] >= size-1): # bottom row
        squares[size-1][newSquare[1]][-1] = "-  -"
      if (newSquare[1] <= 0): # left edge
        squares[newSquare[0]][0][1] = "  "
      if (newSquare[1] >= size-1): # right edge
        squares[newSquare[0]][size-1][2] = "  "
      return squares
    # end breakEdgeWall

    routeLength = 0
    foundEdge = False
    previousSquares = [[i, j]]
    while (not foundEdge):
      newSquare = [i, j]
      while (True):
        r = random.randint(0, 3)
        if (r is 0): # go up
          newSquare = [i-1, j]
        elif (r is 1): # go right
          newSquare = [i, j+1]
        elif (r is 2): # go down
          newSquare = [i+1, j]
        elif (r is 3): # go left
          newSquare = [i, j-1]

        foundEdge = isEdge(size, newSquare)
        if (not foundEdge):
          if (newSquare not in previousSquares):
            squares = goToSquare(r, squares, i, j, newSquare)
            previousSquares.append(newSquare)
            routeLength += 1
          else:
            squares = goToSquare(r, squares, i, j, newSquare)
            del previousSquares[previousSquares.index([i, j])]
            routeLength -= 1
          i, j = newSquare[0], newSquare[1]
          break
        else:
          if (routeLength >= size*(size/1.75)):
            squares = breakEdgeWall(size, squares, newSquare)
            break
          else:
            foundEdge = False

    return squares
  # end generateRoute

  def breakWalls(squares):
    for i in range(len(squares)): # each row
      for j in range(len(squares[i])): # each square in row
        if (random.random() < .1):
          for k in range(4): # each side of square
            if (random.random() < .1): # percent chance of getting wall knocked down
              localSquare = squares[i][j]
              if (k is 0 and i is not 0): # top
                localSquare[k] = "-  -"
                try:
                  squares[i-1][j][3] = localSquare[k]
                except IndexError: # no neighbor
                  pass

              elif (k is 1 and j is not 0): # left
                localSquare[k] = "  "
                try:
                  squares[i][j-1][2] = localSquare[k]
                except IndexError: # no neighbor
                  pass

              elif (k is 2 and j is not size-1): # right
                localSquare[k] = "  "
                try:
                  squares[i][j+1][1] = localSquare[k]
                except IndexError: # no neighbor
                  pass

              elif (k is 3 and i is not size-1): # bottom
                localSquare[k] = "-  -"
                try:
                  squares[i+1][j][0] = localSquare[k]
                except IndexError: # no neighbor
                  pass

                squares[i][j] = localSquare
    return squares
  # end breakWalls

  squares = buildBaseMaze(size)
  squares = generateStart(squares)
  #squares = breakWalls(squares)

  return buildMazeFromSquares(squares)
# end mazeBuilder