import mysql.connector
import SecretStuff

def connectDatabase(dbName):
  class MoBotDB:
    def __init__(self, connection, cursor):
      self.connection = connection
      self.cursor = cursor
  # end MoBotDB

  dbConnection = mysql.connector.connect(
    host="10.0.0.227",
    user="MoBot",
    passwd=SecretStuff.getToken("MoBotDatabaseToken.txt"),
    database=dbName,
    charset="utf8mb4",
    use_unicode=True,
    buffered=True
  )
  dbCursor = dbConnection.cursor()
  return MoBotDB(dbConnection, dbCursor)
# end connectDatabase

def replaceChars(badString):
  return badString.replace("'", "''").replace("\\", "\\\\")
# end replaceChars