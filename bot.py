token = "5872430886:AAEQUtZ8Sb9JaAK8gcLnDjcrn1DonGameIQ"
#wallet_bot = "TQxzn7A4NRYWjFuHZx1hM1KR9TyM7X5gnD"
wallet_bot = "TQA2Z63x5rN561gCZSEnNPK5A5HK4W813s"
admin_ids = []

from telebot import TeleBot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import ( Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Document )
from manager import SectorManager
from tronscan import TronscanClient
from senders import ( RubikaRunner, json )
import threading
import asyncio
import os
import traceback
import aiofiles

def makeFont(string: str):
    return string.translate(string.maketrans("qwertyuiopasdfghjklzxcvbnm", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ"))

bot = AsyncTeleBot(token)
syncbot = TeleBot(token)
sector = SectorManager()
tronscan = TronscanClient()
backhome_admin_keyboard = InlineKeyboardMarkup()

backhome_admin_keyboard.add(
    InlineKeyboardButton(makeFont("back home 🏠"), callback_data="backhome_admin")
)

print(asyncio.run(bot.get_me()))

def fileDownloader(document: Document, chat_id: int, message_id: int, uid: int):
    _file = syncbot.get_file(document.file_id)
    _content_file = syncbot.download_file(_file.file_path)
    with open(f"underprintfiles/{_file.file_id}", "wb") as _nfile:
        _nfile.write(_content_file)
        _nfile.close()
        asyncio.run(sector.addFileId(uid, _file.file_id))
        asyncio.run(sector.addStep(uid, "rubika"))
        syncbot.edit_message_text(
            makeFont(f"💎 | File downloaded\n\n🔓 | file-id: {_file.file_id}\n\n🛰 | file-size: {_file.file_size}\n\n🌐 | now use /file command to start the process"),
            chat_id=chat_id,
            message_id=message_id
        )


@bot.message_handler()
async def onMessage(message: Message):
    if message.from_user.id in admin_ids:
        if message.text.startswith("/start"):
            home_admin_keyboard = InlineKeyboardMarkup()
            home_admin_keyboard.add(
                InlineKeyboardButton(makeFont("buy states 👥"), callback_data="buy_states"),
                InlineKeyboardButton(makeFont("all people 📃"), callback_data="all_people"),
                InlineKeyboardButton(makeFont("up files 🍃"), callback_data="up_files")
            )
            veri = await sector.getUserById(message.from_user.id)
            if veri.status != "OK":
                home_admin_keyboard.add(
                    InlineKeyboardButton(makeFont("sign up 📤"), callback_data=f"sign_up_{message.from_user.id}")
                )
            home_admin_keyboard.add(
                InlineKeyboardButton(makeFont("close"), callback_data="close_admin")
            )
            await bot.send_message(
                message.chat.id,
                makeFont("🌊 | Sector Bot is online\n🔴 | Use /clean to delete all uploaded auth files\n🎛 | Select one option below"),
                reply_markup=home_admin_keyboard,
                reply_to_message_id=message.id
            )

        elif message.text.startswith("/clean"):
            rmsg = await bot.send_message(
                message.chat.id,
                makeFont("🏁 | cleaning-process is started\n♻ | trying to clean folder ..."),
                reply_to_message_id=message.id
            )
            allfiles = os.listdir("underprintfiles")
            await bot.edit_message_text(
                makeFont(f"📁 | detected {len(allfiles)} files\n♻ | trying to clean folder ..."),
                message.chat.id,
                rmsg.id
            )
            for afile in allfiles:
                try:os.remove(f"underprintfiles/{afile}")
                except:pass

            _allfiles = os.listdir("underprintfiles")
            await bot.edit_message_text(
                makeFont(f"📁 | detected {len(allfiles)} files\n♻ | {allfiles - _allfiles} files removed from folder"),
                message.chat.id,
                rmsg.id
            )
    else:
        if message.text.startswith("/start"):
            home_user_keyboard = InlineKeyboardMarkup()
            veri = await sector.getUserById(message.from_user.id)
            if veri.status != "OK":
                home_user_keyboard.add(
                    InlineKeyboardButton(makeFont("sign up 📤"), callback_data=f"sign_up_{message.from_user.id}")
                )
            await bot.send_message(
                message.chat.id,
                makeFont("🔰 | command start detected from ") + f'<a href="tg://openmessage?user_id={message.from_user.id}">{message.from_user.first_name}</a>' \
                + makeFont("\n🛰 | transform money to the ") + f'<code>{wallet_bot}</code>' + makeFont("\n\n🔐 | or send a transaction link from tronscan to check it -> /check LINK\n\n📁 | select an order by /buy"),
                reply_markup=home_user_keyboard,
                reply_to_message_id=message.id,
                parse_mode="HTML"
            )

    if message.text.startswith("/buy"):
        shop_markup = InlineKeyboardMarkup()
        shop_markup.add(
            InlineKeyboardButton(makeFont("Rubika 🎲"), callback_data=f"rubika_{message.from_user.id}"),
            InlineKeyboardButton(makeFont("Shad 🥓"), callback_data=f"shad_{message.from_user.id}")
        )

        shop_markup.add(
            InlineKeyboardButton(makeFont("Telegram 🍡"), callback_data=f"telegram_{message.from_user.id}")
        )

        shop_markup.add(
            InlineKeyboardButton(makeFont("close"), callback_data=f"close_{message.from_user.id}")
        )

        await bot.send_message(
            message.chat.id,
            makeFont(f"🍷 | Select an order to process"),
            reply_to_message_id=message.id,
            reply_markup=shop_markup
        )
    
    elif message.text.startswith("/check"):
        thash = message.text[6:].strip()
        if thash == "":
            await bot.reply_to(
                message,
                makeFont("❌ | Hash link-place was empty")
            )
        else:
            user = await sector.getUserById(message.from_user.id)
            if not user.status == "OK":
                await bot.send_message(message.chat.id, makeFont("🥤 | Signup with /start"), reply_to_message_id=message.id)
            elif user.user.verified == True:
                await bot.send_message(message.chat.id, makeFont("🔓 | You already have verified"), reply_to_message_id=message.id)
            else:
                try:
                    data = await tronscan.getInfo(thash)
                    if data.status_code == 200:
                        js = data.json()
                        print(js)
                        is_exs = await sector.doesWalletExist(js['hash'])
                        if is_exs == False:
                            is_match = await tronscan.isMatch(js, 5, wallet_bot)
                            print(is_match)
                            if is_match:
                                await sector.makeItVerify(message.from_user.id)
                                await sector.addWallet(js['hash'])
                                await bot.send_message(
                                    message.chat.id,
                                    makeFont("🌊 | You been verified and can use options by using /buy command"),
                                    reply_to_message_id=message.id
                                )

                            else:
                                await bot.send_message(
                                    message.chat.id,
                                    makeFont("🍃 | The cost is not 5 trx or receiver address is not for bot"),
                                    reply_to_message_id=message.id
                                )
                        else:
                            await bot.send_message(
                                message.chat.id,
                                makeFont("🔐 | Cannot use a transaction-link for twice"),
                                reply_to_message_id=message.id
                            )
                    else: await bot.send_message(
                        message.chat.id,
                        makeFont(f"🕷 | Hash or Link is invalid\n🔵 | Status - {data.status_code}"),
                        reply_to_message_id=message.id
                    )
                except Exception as e:
                    traceback.print_exc()
                    await bot.send_message(
                        message.chat.id,
                        makeFont(f"🥤 | Bot error: {e}"),
                        reply_to_message_id=message.id
                    )

    elif message.text.startswith("/rubika"):
        user = await sector.getUserById(message.from_user.id)
        if not user.status == "OK":
            await bot.send_message(message.chat.id, makeFont("🥤 | Signup with /start"), reply_to_message_id=message.id)
        elif not user.user.verified == True:
            await bot.send_message(message.chat.id, makeFont("🔐 | Please verify yourself first, use /start"), reply_to_message_id=message.id)
        else:
            if message.reply_to_message:
                if message.reply_to_message.text:
                    try:
                        auth = json.loads(message.reply_to_message.text)
                        if isinstance(auth, dict):
                            th = threading.Thread(target=RubikaRunner, args=([auth], syncbot, message.from_user.id, None, "", auth, message.chat.id, message.id))
                            th.start()
                            th.join()
                        
                        elif isinstance(auth, list):
                            th = threading.Thread(target=RubikaRunner, args=(auth, syncbot, message.from_user.id, None, "", auth, message.chat.id, message.id))
                            th.start()
                            th.join()

                        else:
                            await bot.send_message(
                                message.chat.id,
                                makeFont("🛰 | Invalid data-type"),
                                reply_to_message_id=message.id
                            )
                    except:
                        await bot.send_message(
                            message.chat.id,
                            makeFont("🛰 | Invalid data-type"),
                            reply_to_message_id=message.id
                        )

                elif message.reply_to_message.document:
                    rmsg = await bot.send_message(
                        message.chat.id,
                        makeFont("🍬 | Try to download the file ..."),
                        reply_to_message_id=message.id
                    )
                    thdl = threading.Thread(target=fileDownloader, args=(message.reply_to_message.document, message.chat.id, rmsg.id, message.from_user.id))
                    thdl.start()
                    thdl.join()

                else:
                    await bot.reply_to(
                        message,
                        makeFont("🥓 | Invalid message-type")
                    )

            else:
                await bot.reply_to(
                    message,
                    makeFont("👁 | No reply found")
                )

    elif message.text.startswith("/file"):
        user = await sector.getUserById(message.from_user.id)
        if not user.status == "OK":
            await bot.send_message(message.chat.id, makeFont("🥤 | Signup with /start"), reply_to_message_id=message.id)
        elif not user.user.verified == True:
            await bot.send_message(message.chat.id, makeFont("🔐 | Please verify yourself first, use /start"), reply_to_message_id=message.id)
        else:
            if len(user.user.file_ids) > 0:
                if user.user.step == "rubika":
                    try:
                        selected_fileid = user.user.file_ids[-1]
                        reader = await aiofiles.open(f"underprintfiles/{selected_fileid}", "r")
                        reader = await reader.read()
                        auth = json.loads(reader)
                        await bot.reply_to(message, makeFont("🕷 | Selected file-id: ") + f"<code>{selected_fileid}</code>", parse_mode="HTML")
                        if isinstance(auth, dict):
                                th = threading.Thread(target=RubikaRunner, args=([auth], syncbot, message.from_user.id, None, "", auth, message.chat.id, message.id))
                                th.start()
                                th.join()
                            
                        elif isinstance(auth, list):
                            th = threading.Thread(target=RubikaRunner, args=(auth, syncbot, message.from_user.id, None, "", auth, message.chat.id, message.id))
                            th.start()
                            th.join()

                    except Exception as ebf:
                        traceback.print_exc()
                        await bot.send_message(
                            message.chat.id,
                            makeFont(f"🥤 | Bot error: {ebf}"),
                            reply_to_message_id=message.id
                        )

@bot.callback_query_handler(lambda call: True)
async def onCallbackQuery(call: CallbackQuery):
    if call.data == "buy_states":
        allbuys = await sector.getAllWallets()
        await bot.edit_message_text(
            makeFont(f"👤 | {len(allbuys)} people have buy from sender"),
            call.message.chat.id,
            call.message.id,
            reply_markup=backhome_admin_keyboard
        )

    elif call.data == "all_people":
        allpeople = await sector.getAll()
        await bot.edit_message_text(
            makeFont(f"🍬 | {len(allpeople)} people have signed up"),
            call.message.chat.id,
            call.message.id,
            reply_markup=backhome_admin_keyboard
        )

    elif call.data == "up_files":
        allpeople = await sector.getUploadedFiles()
        await bot.edit_message_text(
            makeFont(f"🗃 | {allpeople} file have uploaded"),
            call.message.chat.id,
            call.message.id,
            reply_markup=backhome_admin_keyboard
        )

    elif call.data == "close_admin":
        try:
            await bot.delete_message(call.message.chat.id, call.message.id)
        except:pass

    elif call.data.startswith("close_") and not call.data == "close_admin":
        spl = call.data.split("_")
        uid = int(spl[1])
        if uid == call.from_user.id:
            try:
                await bot.delete_message(call.message.chat.id, call.message.id)
            except:pass

    elif call.data == "backhome_admin":
        try:
            home_admin_keyboard = InlineKeyboardMarkup()
            home_admin_keyboard.add(
                InlineKeyboardButton(makeFont("buy states 👥"), callback_data="buy_states"),
                InlineKeyboardButton(makeFont("all people 📃"), callback_data="all_people"),
                InlineKeyboardButton(makeFont("up files 🍃"), callback_data="up_files")
            )
            veri = await sector.getUserById(call.from_user.id)
            if veri.status != "OK":
                home_admin_keyboard.add(
                    InlineKeyboardButton(makeFont("sign up 📤"), callback_data=f"sign_up_{call.message.from_user.id}")
                )
            home_admin_keyboard.add(
                InlineKeyboardButton(makeFont("close"), callback_data="close_admin")
            )
            await bot.edit_message_text(
                makeFont("🌊 | Sector Bot is online\n🎛 | Select one option below"),
                call.message.chat.id,
                call.message.id,
                reply_markup=home_admin_keyboard
            )
        except:pass

    elif call.data.startswith("sign_up"):
        spl = call.data.split("_")
        uid = int(spl[-1])

        if call.from_user.id == uid:
            await sector.addUser(uid)
            await bot.edit_message_text(
                makeFont("📪 | user ") + f'<a href="tg://openmessage?user_id={uid}">'+makeFont(call.from_user.full_name)+'</a>'+makeFont(" has signed up"),
                call.message.chat.id,
                call.message.id,
                parse_mode="HTML"
            )

    elif call.data.startswith("rubika_") or call.data.startswith("shad_") or call.data.startswith("telegram_"):
        spl = call.data.split("_")
        uid = int(spl[1])
        if uid == call.from_user.id:
            user = await sector.getUserById(call.from_user.id)
            if user.status == "OK":
                if user.user.verified:
                    await sector.addStep(uid, "rubika")
                    await bot.edit_message_text(
                        makeFont("🌊 | Reply on document or text-auth by /select"),
                        call.message.chat.id,
                        call.message.id
                    )
                else: 
                    await bot.edit_message_text(
                        makeFont("🔐 | Please buy Subscription first"),
                        call.message.chat.id,
                        call.message.id
                    )
            else:
                await bot.edit_message_text(
                    makeFont("🥤 | Signup with /start"),
                    call.message.chat.id,
                    call.message.id
                )

if __name__ == "__main__":
    asyncio.run(bot.infinity_polling())
