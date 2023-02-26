import sqlite3

conn = sqlite3.connect("./database/data.db")

# Creates a table in database with the file's name
def createTable(tableName):
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS {} (timeStamp float, pl float, pc float, pr float, InsertionPointX float, InsertionPointY)".format(tableName))

# Inserts data to a file's table
def insertToTable(tableName, ts, pl, pc, pr, ipXY):
    createTable(tableName)
    cur = conn.cursor()
    j=0
    cur.execute("DELETE FROM {}".format(tableName))
    if ipXY:
        cur.execute("INSERT INTO \"{}\" VALUES ({}, {}, {}, {}, {}, {})".format(tableName, ts[0], pl[0], pc[0], pr[0], ipXY[0],ipXY[1]))
        j=1
    for i in range(len(ts)-1):
        cur.execute("INSERT INTO \"{}\" (timeStamp, pl, pc, pr) VALUES ({}, {}, {}, {})".format(tableName, ts[i+j], pl[i+j], pc[i+j], pr[i+j]))
    conn.commit()

def getTable(tableName):
    tsD, plD, pcD, prD = [], [], [], []
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM {}".format(tableName))
    j=0
    for dbData in result.fetchall():
        tsD.append(dbData[0])
        plD.append(dbData[1])
        pcD.append(dbData[2])
        prD.append(dbData[3])
        if j==0:
            ipX = dbData[4]
            ipY = dbData[5]
            j = j + 1
    data = [tsD, plD, pcD, prD]
    return data, ipX, ipY

def getAllTables():
    tables = []
    cur = conn.cursor()
    result = cur.execute("SELECT * FROM sqlite_schema WHERE type='table'")
    for table in result.fetchall():
        tables.append(table[1])
    return tables

#data, ipx, ipy = getTable("C660913142637")
#print (data[0])
