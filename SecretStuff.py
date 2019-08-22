from os import path

def getToken(fileName):
  f = open(getFilepath(fileName), "r")
  key = f.read().strip()
  f.close()
  return key
# end getToken

def getJsonFilePath(fileName):
  return getFilepath(fileName)
# end getJsonFilePath 

def getFilepath(fileName):
  basepath = path.dirname(__file__)
  filepath = path.abspath(path.join(basepath, "..", "SecretStuff", fileName))
  return filepath
# end getFilepath
