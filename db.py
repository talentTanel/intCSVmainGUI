import sqlite3

conn = sqlite3.connect("./database/data.db")

def createTable(tableName):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS {} (timeStamp float, pl float, pc float, pr float)".format(tableName))

#createTable("test12")