import mysql.connector

from utils import functions

config = functions.get("utils/config.json")

def createConnection():
    mydb = mysql.connector.connect(
        host=config.mysql_host,
        user=config.mysql_user,
        passwd=config.mysql_pass,
        database=config.mysql_db,
        port=config.mysql_port
    )
    return mydb

def Entry_Check(Check, Row, Table):
    try:
        mydb = createConnection()
        cur = mydb.cursor(buffered=True)
        query = (f"SELECT {Row} FROM `{config.mysql_db}`.`{Table}`")
        cur.execute(query)

        for Row in cur:
            if Check in Row:
                cur.close()
                return True
    finally:
        mydb.close()

def Fetch(Row, Table, Where, Value):
    try:
        mydb = createConnection()
        table = str.maketrans(dict.fromkeys("()"))
        cur = mydb.cursor()
        query = (f"SELECT {Row} FROM `{Table}` WHERE {Where} = {Value}")
        cur.execute(query)
        row = str(cur.fetchone())
        return row.translate(table)
    finally:
        mydb.close()

# Cards ----------------------------------------------------------------------------------------------------------------

def AddCard(MessageID, Name, Tier, SentTime, Image):
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"INSERT INTO `cards` (MessageID, Name, Tier, TimeSent, Image) VALUES ('{MessageID}', '{Name}', '{Tier}', '{SentTime}', '{Image}')")
        mydb.commit()
    except Exception:
        return None
    finally:
        mydb.close()

def CardClaimed(MessageID, Claimer, Version, TimeClaimed, Event=None):
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        if Event:
            cur.execute(f"UPDATE `cards` SET Claimed = 1, Claimer = '{Claimer}', Version = {Version}, TimeClaimed = '{TimeClaimed}', Event_Active = 1 WHERE MessageID = {MessageID}")
            mydb.commit()
        else:
            cur.execute(f"UPDATE `cards` SET Claimed = 1, Claimer = '{Claimer}', Version = {Version}, TimeClaimed = '{TimeClaimed}' WHERE MessageID = {MessageID}")
            mydb.commit()
    except Exception as e:
        return None
    finally:
        mydb.close()

def LastClaimedCard(UserID):
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT Name FROM `cards` WHERE Claimer = '{UserID}' ORDER BY ID DESC")
        row = cur.fetchone()
        return row[0]
    except Exception:
        return None
    finally:
        mydb.close()

def RarestCard(UserID):
    return "Soon"

def TotalCardCount(UserID):
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT COUNT(*) FROM `cards` WHERE Claimer = '{UserID}'")
        row = cur.fetchone()
        return row[0]
    except Exception:
        return None
    finally:
        mydb.close()

def CardsHistory():
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT Name, Claimed, Tier, TimeSent FROM `cards` ORDER BY TimeSent DESC LIMIT 20")
        rows = cur.fetchall()
        return rows
    except Exception:
        return None
    finally:
        mydb.close()

def GetLeaderboard():
    try:
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"SELECT Event_Active, Claimer, COUNT(*) AS `count` FROM cards WHERE Claimer IS NOT NULL AND Event_Active = 1 GROUP BY Claimer ORDER BY count DESC LIMIT 10")
        rows = cur.fetchall()
        return rows
    except Exception:
        return None
    finally:
        mydb.close()

# sCoin ----------------------------------------------------------------------------------------------------------------

def sLog(user, type, log, date):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"INSERT INTO sCoin_Logs (User, LogType, Log, Timestamp) VALUES ('{user}', {type}, '{log}', '{date}') ")
        mydb.commit()
    except Exception as e:
        return None
    finally:
        mydb.close()

def accountExists(id):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT User FROM sCoin WHERE User = {id}")
        row = cur.fetchone()
        if row:
            return row[0]
        else:
            return None
    except:
        return None

    finally:
        mydb.close()

def addUser(id):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"INSERT INTO sCoin (User) VALUES ('{id}')")
        mydb.commit()
        return True
    except:
        return None
    finally:
        mydb.close()

def accountBalance(id):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT Balance FROM sCoin WHERE User = {id}")
        row = cur.fetchone()
        if row:
            return row[0]
        else:
            return None
    except:
        return None
    finally:
        mydb.close()

def sCoinStats():
    mydb = createConnection()
    cur = mydb.cursor()

    stats = []

    try:
        cur.execute(f"SELECT COUNT(*), SUM(Balance) FROM sCoin")
        row = cur.fetchone()
        stats.append(row[0])
        stats.append(row[1])

        cur.execute(f"SELECT COUNT(*) FROM sCoin_Logs WHERE LogType = 3")
        row = cur.fetchone()
        stats.append(row[0])

        return stats
    except:
        return None
    finally:
        mydb.close()

def accountHistory(id):
    mydb = createConnection()
    cur = mydb.cursor()

    try:
        cur.execute(f"SELECT * FROM sCoin_Logs WHERE User = {id} ORDER BY Timestamp DESC LIMIT 10 ")
        rows = cur.fetchall()
        return rows
    except:
        return None
    finally:
        mydb.close()

def getAccount(id):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT * FROM sCoin WHERE User = {id}")
        row = cur.fetchall()
        if row:
            return row[0]
        else:
            return None
    except:
        return None
    finally:
        mydb.close()

def upgradeAccount(id, upgrade):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"UPDATE sCoin SET Account_Type = {upgrade} WHERE User = {id}")
        mydb.commit()
        return True
    except:
        return None
    finally:
        mydb.close()

def setCoins(id, amount):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"UPDATE sCoin SET Balance = {amount} WHERE User = {id}")
        mydb.commit()
        return True
    except:
        return None
    finally:
        mydb.close()

def closeAccount(id):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"DELETE FROM sCoin WHERE User = {id}")
        mydb.commit()
        return True
    except:
        return None
    finally:
        mydb.close()

# ------------------ Access

def GetAccess(userid):
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT Access FROM `{config.mysql_db}`.`access` WHERE User = '{userid}'")
        row = cur.fetchone()
        
        if row:
            return row[0]
        else:
            return None
    finally:
        mydb.close()

def isStaff(user):
    if isOwner(user) or isAdmin(user):
        return True

    return False

def SetAccess(user, type):
    if not isAdmin(user):
        mydb = createConnection()
        cur = mydb.cursor()
        cur.execute(f"INSERT into `{config.mysql_db}`.`access` (User, Access) VALUES ('{user.id}', {type})")
        mydb.commit()
        return True

    return False

def getallAccess():
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT * FROM `{config.mysql_db}`.`access`")
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(e)
    finally:
        mydb.close()

def DelAccess(user):
    if isAdmin(user):
        mydb = createConnection()
        cur = mydb.cursor()
        try:
            cur.execute(f"DELETE FROM `{config.mysql_db}`.`access` WHERE User = '{user.id}'")
            mydb.commit()
            return True
        except Exception as e:
            print(e)
        finally:
            mydb.close()

    return False

def isOwner(user):
    access = GetAccess(user.id)

    if access == 2:
        return True

def isAdmin(user):
    access = GetAccess(user.id)

    if access == 1 or access == 2:
        return True

# ------------- Color Roles

def delSupportRole(roleid):
    if isSupporter(roleid):
        mydb = createConnection()
        cur = mydb.cursor()
    try:
        cur.execute(f"DELETE from `colour_roles` WHERE roleid = '{roleid}'")
        mydb.commit()
        return True
    finally:
        mydb.close()

def addSupportRole(roleid):
    if not isSupporter(roleid):
        mydb = createConnection()
        cur = mydb.cursor()
    try:
        cur.execute(f"INSERT into `colour_roles` (roleid) VALUES ({roleid})")
        mydb.commit()
        return True
    finally:
        mydb.close()

def isSupportRole(roleid):
    if Entry_Check(str(roleid), "roleid", "colour_roles"):
        return True

async def isSupporter(user):
    for roles in user.roles:
        if Entry_Check(str(roles.id), "roleid", "colour_roles"):
            return True

def getSupportRoles():
    list = []
    mydb = createConnection()
    cur = mydb.cursor()
    try:
        cur.execute(f"SELECT roleid from colour_roles")
        for Row in cur:
            list.append(Row[0])

        return list
    finally:
        mydb.close()


