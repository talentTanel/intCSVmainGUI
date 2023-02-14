import sqlite3

conn = sqlite3.connect("./database/data.db")

# Creates a table in database with the file's name
def createTable(tableName):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS {} (timeStamp float, pl float, pc float, pr float)".format(tableName))

# Inserts data to a file's table
def insertToTable(tableName, ts, pl, pc, pr):
    createTable(tableName)
    cur = conn.cursor()
    print(ts[len(ts)-1])
    for i in range(len(ts)):
        cur.execute("INSERT INTO \"{}\" VALUES ({}, {}, {}, {})".format(tableName, ts[i], pl[i], pc[i], pr[i]))
    conn.commit()