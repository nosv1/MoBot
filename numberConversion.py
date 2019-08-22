def intToBraile(number):
  one = 10241 # "⠁" beginning of braile in unicode goes to 10495

  oldT = number
  braile = ""
  while (True):
    newT = int(oldT/255)
    r = oldT - (255*newT)
    if (r == 0 and newT == 0):
      break
    else:
      braile += chr(one+r)
      oldT = newT

  return braile if (braile != "") else chr(one-1)

def braileToInt(braile):
  number = 0

  for i in range(len(braile)-1, -1, -1):
    number += (ord(braile[i]) - 10241) * 255 ** i

  return number