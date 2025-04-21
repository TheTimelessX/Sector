token = "5872430886:AAEQUtZ8Sb9JaAK8gcLnDjcrn1DonGameIQ"
wallet_bot = "TQxzn7A4NRYWjFuHZx1hM1KR9TyM7X5gnD"
admin_ids = []

from telebot.async_telebot import AsyncTeleBot
from telebot.types import ( Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery )
from manager import SectorManager
from senders import ( RubikaRunner, json )
import threading
import asyncio

def makeFont(string: str):
    return string.translate(string.maketrans("qwertyuiopasdfghjklzxcvbnm", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ"))

bot = AsyncTeleBot(token)
sector = SectorManager()
backhome_admin_keyboard = InlineKeyboardMarkup()

backhome_admin_keyboard.add(
    InlineKeyboardButton(makeFont("back home 🏠"), callback_data="backhome_admin")
)

print(asyncio.run(bot.get_me()))

@bot.message_handler()
async def onMessage(message: Message):
    if message.from_user.id in admin_ids:
        home_admin_keyboard = InlineKeyboardMarkup()
        home_admin_keyboard.add(
            InlineKeyboardButton(makeFont("buy states 👥"), callback_data="buy_states"),
            InlineKeyboardButton(makeFont("all people 📃"), callback_data="all_people")
        )
        veri = await sector.getUserById(message.from_user.id)
        if veri.status != "OK":
            home_admin_keyboard.add(
                InlineKeyboardButton(makeFont("sign up 📤"), callback_data=f"sign_up_{message.from_user.id}")
            )
        home_admin_keyboard.add(
            InlineKeyboardButton(makeFont("close"), callback_data="close_admin")
        )

        if message.text.startswith("/start"):
            await bot.send_message(
                message.chat.id,
                makeFont("🌊 | Sector Bot is online\n🎛 | Select one option below"),
                reply_markup=home_admin_keyboard,
                reply_to_message_id=message.id
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
                + makeFont("\n🛰 | transform money to the ") + f'<code>{wallet_bot}</code>' + makeFont("\n\n🔐 | or send a transaction link from tronscan to check it -> /check LINK\n\n📁 | select an order by /shop"),
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

    elif message.text.startswith("/rubika"):
        if message.reply_to_message:
            if message.reply_to_message.text:
                try:
                    auth = json.loads(message.reply_to_message.text)
                    if isinstance(auth, dict):
                        th = threading.Thread(target=RubikaRunner, args=(auth, bot, message.from_user.id, "", auth))
                        th.start()
                        th.join()
                except:
                    await bot.send_message(
                        message.chat.id,
                        makeFont("🛰 | Invalid data-type"),
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
                InlineKeyboardButton(makeFont("all people 📃"), callback_data="all_people")
            )
            veri = await sector.getUserById(call.message.from_user.id)
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