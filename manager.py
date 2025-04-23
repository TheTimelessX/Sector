import sqlite3
import json
import os

from interface import UserResponse

class SectorManager(object):
    def __init__(self):
        self.manage = sqlite3.connect("hellnobroWTF.db", check_same_thread=False)
        self.setup()

    def setup(self):
        if not os.path.exists("underprintfiles"):
            os.mkdir("underprintfiles")
        
        self.manage.execute("CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, file_ids TEXT, verified INTEGER, step TEXT)")
        self.manage.execute("CREATE TABLE IF NOT EXISTS transes (from_wallet TEXT PRIMARY KEY)")

    async def doesWalletExist(self, wallet: str) -> bool:
        allwallets = self.manage.execute("SELECT * FROM transes").fetchall()
        for _wallet in allwallets:
            if _wallet == wallet: return True
        
        return False
    
    async def addWallet(self, wallet: str):
        self.manage.execute("INSERT INTO transes (from_wallet) VALUES (?)", (
            wallet,
        ))
        self.manage.commit()

        return {
            "status": "OK"
        }
    
    async def getAllWallets(self):
        return self.manage.execute("SELECT * FROM transes").fetchall()
    
    async def getAll(self):
        return self.manage.execute("SELECT * FROM users").fetchall()
    
    async def getUserById(self, uid: int) -> UserResponse:
        for user in await self.getAll():
            if user[0] == uid:
                return UserResponse({
                    "status": "OK",
                    "user": user
                })
            
        return UserResponse({
            "status": "ERROR"
        })
    
    async def addUser(self, uid: int):
        veri = await self.getUserById(uid)
        if veri.status == "OK":
            return {
                "status": "EXISTS_USER"
            }
        
        self.manage.execute("INSERT INTO users (uid, file_ids, verified, step) VALUES (?, ?, ?, ?)", (
            uid,
            "[]",
            0,
            ""
        ))

        self.manage.commit()

        return {
            "status": "OK"
        }
    
    async def addFileId(self, uid: int, file_id: str):
        user = await self.getUserById(uid)
        if user.status == "OK":
            if not file_id in user.user.file_ids:
                user.user.file_ids.append(
                    file_id
                )

                self.manage.execute("UPDATE users SET file_ids = ? WHERE uid = ?", (
                    json.dumps(user.user.file_ids),
                    uid
                ))

                self.manage.commit()

                return {
                    "status": "OK"
                }
            
            else: 
                return {
                    "status": "EXISTS_FILE_ID"
                }
            
        else: 
            return {
                "status": user.status
            }
        
    async def doesFileIdExist(self, uid: int, file_id: str) -> bool:
        user = await self.getUserById(uid)
        if user.status == "OK":
            if not file_id in user.user.file_ids: return False
            else: return True
            
        else: return False

    async def makeItVerify(self, uid: int):
        user = await self.getUserById(uid)

        if user.status == "OK":
            if user.user.verified == False: user.user.verified = True
            else: user.user.verified = False

            self.manage.execute("UPDATE users SET verified = ? WHERE uid = ?", (
                user.user.verified,
                uid
            ))
            self.manage.commit()

            return {
                "status": "OK"
            }
        
        else: return {
            "status": "INVALID_UID"
        }

    async def addStep(self, uid: int, step: str):
        user = await self.getUserById(uid)

        if user.status == "OK":
            self.manage.execute("UPDATE users SET step = ? WHERE uid = ?", (
                step,
                uid
            ))
            self.manage.commit()

            return {
                "status": "OK"
            }
        
        else: return {
            "status": "INVALID_UID"
        }

    async def getUploadedFiles(self):
        ivi = await self.getAll()
        l = 0
        for user in ivi:
            decoded = json.loads(user[1])
            for fid in decoded:
                l += 1
        
        return l