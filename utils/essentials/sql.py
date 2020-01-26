import mysql.connector

from utils.essentials.functions import func
from utils.essentials import functions

config = functions.get("utils/config.json")
global mydb

def createConnection():
    global mydb
    mydb = mysql.connector.connect(
        host=config.mysql_host,
        user=config.mysql_user,
        passwd=config.mysql_pass,
        database=config.mysql_db,
        port=config.mysql_port
    )
    return mydb

def Entry_Check(Check, Row, Table):
    mydb = createConnection()
    cur = mydb.cursor(buffered=True)
    query = (f"SELECT {Row} FROM `{config.mysql_db}`.`{Table}`")
    cur.execute(query)

    for Row in cur:
        if Check in Row:
            cur.close()
            return True

def Fetch(Row, Table, Where, Value):
    table = str.maketrans(dict.fromkeys("()"))
    cur = mydb.cursor()
    query = (f"SELECT {Row} FROM `{config.mysql_db}`.`{Table}` WHERE {Where} = {Value}")
    cur.execute(query)
    row = str(cur.fetchone())
    return row.translate(table)
