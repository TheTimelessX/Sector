from pyrubi import Client
from libraryshad import Bot
from telebot.async_telebot import AsyncTeleBot
from manager import SectorManager
import json
import asyncio
import os
import threading

sector = SectorManager()
users = {}
def makeFont(string: str):
    return string.translate(string.maketrans("qwertyuiopasdfghjklzxcvbnm", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ"))


global RubikaSender
async def RubikaSender(file_path: str, bot: AsyncTeleBot, **options):
    data = file_path
    if options.get("continueit") == None:
        users[options.get("user_id")] = {
            "phones": [],
            "guids": []
        }

        for _ in data:
            ks = list(_.keys())
            if 'malek' in ks:
                client = Client(auth=_['auth'], private=_['malek'], platform="android")
            elif 'key' in ks:
                client = Client(auth=_['auth'], private=_['key'], platform="android")
            else: continue
            contacts = client.get_contacts()
            
            if "users" in contacts:
                for user in contacts['users']:
                    if not user['is_deleted'] == True:
                        users[options.get("user_id")]['guids'].append(user['user_guid'])
                        users[options.get("user_id")]['phones'].append(user['phone'])
                
                if contacts['has_continue']:
                    th = threading.Thread(target=RubikaRunner, args=(file_path,bot), kwargs={"user_id": options['user_id'], "continueit": True, "nextid": contacts['next_start_id'], "token": _, "chat_id": options.get("chat_id"), "message_id": options.get("message_id")})
                    th.start()
                    th.join()
                else:
                    if _ == data[-1]:
                        open(str(options.get("user_id"))+".json", "w").write(json.dumps(users, indent=2))
                        phn = len(users[options.get("user_id")]['phones'])
                        gun = len(users[options.get("user_id")]['guids'])
                        del users[options.get("user_id")]
                        with open(str(options.get("user_id"))+".json", 'rb') as document:
                            bot.send_document(
                                chat_id=options.get("chat_id"),
                                data=document,
                                document=document,#str(options.get("user_id"))+".json",
                                reply_to_message_id=options.get("message_id"),
                                caption=makeFont(f"☎ | Listed {phn} phone numbers\n🌐 | Listed {gun} guids")
                            )
                            os.remove(str(options.get("user_id"))+".json")
                            await sector.makeItVerify(options.get("user_id"))
                        
            else: continue

    else:
        if options['continueit'] == True:
            for i in range(1):
                ks = list(options.get("token").keys())
                if 'malek' in ks:
                    client = Client(auth=options.get("token")['auth'], private=options.get("token")['malek'], platform="android")
                elif 'key' in ks:
                    client = Client(auth=options.get("token")['auth'], private=options.get("token")['key'], platform="android")
                else: continue
                contacts = client.get_contacts(start_id=options.get("nextid"))
                
                if "users" in contacts:
                    for user in contacts['users']:
                        if not user['is_deleted'] == True:
                            users[options.get("user_id")]['guids'].append(user['user_guid'])
                            users[options.get("user_id")]['phones'].append(user['phone'])
                    
                    if contacts['has_continue']:
                        th = threading.Thread(target=RubikaRunner, args=(file_path,bot), kwargs={"user_id": options['user_id'], "continueit": True, "nextid": contacts['next_start_id'], "token": options.get("token"), "chat_id": options.get("chat_id"), "message_id": options.get("message_id")})
                        th.start()
                        th.join()
                    else:
                      if options.get("token") == data[-1]:
                        open(str(options.get("user_id"))+".json", "w").write(json.dumps(users, indent=2))
                        phn = len(users[options.get("user_id")]['phones'])
                        gun = len(users[options.get("user_id")]['guids'])
                        del users[options.get("user_id")]
                        with open(str(options.get("user_id"))+".json", 'rb') as document:
                            bot.send_document(
                                chat_id=options.get("chat_id"),
                                data=document,
                                document=document,#str(options.get("user_id"))+".json",
                                reply_to_message_id=options.get("message_id"),
                                caption=makeFont(f"☎ | Listed {phn} phone numbers\n🌐 | Listed {gun} guids")
                            )
                            os.remove(str(options.get("user_id"))+".json")
                            await sector.makeItVerify(options.get("user_id"))
                else: continue


global RubikaRunner
def RubikaRunner(
    file_path: str,
    bot: AsyncTeleBot,
    user_id: int = None,
    continueit: bool = None,
    nextid = None,
    token: dict = {},
    chat_id: int = 0,
    message_id: int = 0
):
    asyncio.run(
        RubikaSender(
            file_path=file_path,
            bot=bot,
            user_id=user_id,
            continueit=continueit,
            nextid=nextid,
            token=token,
            chat_id=chat_id,
            message_id=message_id
        )
    )

# auth = [{"malek":"MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAOKtmTrGcC35WHfTxtyjFDfwl3WW54mlOxRXyZ1VPrfAfJ2gR9nxLd04RCn3JTwZRTlymYd/ICAl1/yKooHRKid/JRynAmBh2W6nWm1PS0JX3a2DSIVahAoKwFBZ0cCBLD++QNavYsxLxB5tLqOYP0xU7jK5/4i4aA7F0ShKlsM5AgMBAAECgYBaQcNEeuUJ+UG3nLSO/8Q6Lesw4CBbV1Y52Gan5dxuMA+ud7aEWhrn/dJuX0ENOAavRClLoVu6UTc6ED16sT018tnFsmAJnFvgw95iEKJAFfjmpScD+dIA9yGqL8TLYqcEIjXTjm7mebMlNYwyUK7KiYmz4S51KLLTfcA8EvX4zQJBAPo2QNwTR+CrN9j4Zs2YliFgjYywQpMv9IG73Qhm+X6ml8dTd+vNiq+ZpwRKvYurpz8fd6Fb0XbMFN68CzcOXdcCQQDn6/qQ8qWuTZsZdbIbvwHLuSruP+DnHTKSiXmhse4W+P99asmV/XPVOfKwZ0USrX4snTlTnaPSDnDlY1K1FCVvAkEAxSeqw76NjIJdZyGUH7xzz6j84DaivseyqecVq2E4hotOXUlv3OYAuY0hBUi/Qibnid2JriNjUXBNoZQaYi930QJBAK/wJ8yQFzpMq028KJq94yneVgAZu474amYaHoiYx6rryD4npbfAZ4Apjr9eCFtr/BzyRQv2udFfnSuXlqXCG8cCQQC8o9VgfGoyjXXAuGXGk+WeQv4Qjhr0+h0gN5HDY72WojHD+kcez8fRZ1+vOdzou3SBM/wowqcY3fY+arLFA1Kc","auth":"cughdqnisccbxyhydzddpgjnxlafqtkc"},{"malek":"MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAOOVafUVWmvwfaGWbf4znvwp9bbKygrluWuLUhG5sTn8AnBJ2YE3hzNsJ4a6qjGIGP7fCJMYYlks0GN+5ByOPafoiN/uPJLcm0Ge/vqscj7Q0PMn51ig9FFErL+rBqY/s1SniXxhBxWTOybkUWeXb17OoAG57W3FHEa5Jq/bnET/AgMBAAECgYBR0Hzu5mZDN4lydanFILme3VbAB9bqY/tsdgFi7eaQedBGncXbdiLckZ0ECkb014Bk37ktaC6y8DFaE1veCCSRcoI5HzqTDCF9MvWrUt8Uqj3DorQ7y4hoXQfCuPf7NTrQN0iADxpBYIPxbFIbkV8IxRtIVrbZAXQO60E98vzgwQJBAPz3I63AfCXi3WaKxo+tSuhjNewzWpMC6FauEwlqJ9OKRT4uUlc8ZgRPdd5zTs66zPFwyDa9kD5dhqBlhgl4Jx0CQQDmUFOptpDcOTPtfd8BRjfe1x4m14/VZRE/h+9L3zVY4lRSZkxKs3iXHvUVed8G1HLffMqSaHU171apZjmCOXXLAkAoq++fmwga60vflcZxCVK25GSiEmuooVoLvbcv11KJ73xMkBQLFJnubXwtBOsRz/TtiM2YB4hujoj7tvcDBL99AkAEsQgzQdPLmKK1KMY9KWgD8w/bLLLyXt+uEp/ORNq6V8nt78WIFAXV1jyZ1mSzp+o7ITijKNuSYLC8PKfZPkBnAkBTHM8QxP529TUHrX6sEPVXWNtljt2Ljx4/UuWyhf+TrztO6ta2yrgF7Tri+IenFMJCjOvaIGjSjhcCvSQKC69c","auth":"bxpptzitqntjxkdntbyxupjodmapdnxj"}]
# asyncio.run(RubikaSender(auth, user_id=2))
