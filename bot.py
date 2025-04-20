token = ""
wallet_bot = ""
admin_ids = []

from telebot.async_telebot import AsyncTeleBot
from telebot.types import ( Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery )
from manager import SectorManager

def makeFont(string: str):
    return string.translate(string.maketrans("qwertyuiopasdfghjklzxcvbnm", "Qᴡᴇʀᴛʏᴜɪᴏᴘᴀꜱᴅꜰɢʜᴊᴋʟᴢxᴄᴠʙɴᴍ"))

bot = AsyncTeleBot(token)
sector = SectorManager()
home_admin_keyboard = InlineKeyboardMarkup()
backhome_admin_keyboard = InlineKeyboardMarkup()

home_admin_keyboard.add(
    InlineKeyboardButton(makeFont("buy states 👥"), callback_data="buy_states"),
    InlineKeyboardButton(makeFont("all people 📃"), callback_data="all_people")
)

home_admin_keyboard.add(
    InlineKeyboardButton(makeFont("close"), callback_data="close_admin")
)

backhome_admin_keyboard.add(
    InlineKeyboardButton(makeFont("back home 🏠"), callback_data="backhome_admin")
)

@bot.message_handler()
async def onMessage(message: Message):
    if message.from_user.id in admin_ids:
        if message.text.startswith("/start"):
            await bot.send_message(
                message.chat.id,
                makeFont("🌊 | Sector Bot is online\n🎛 | Select one option below"),
                reply_markup=home_admin_keyboard,
                reply_to_message_id=message.id
            )

    else:
        if message.text.startswith("/start"):
            await bot.send_message(
                message.chat.id,
                makeFont("🔰 | command start detected from ") + f'<a href="tg://openmessage?user_id={message.from_user.id}">{message.from_user.first_name}</a>' \
                + makeFont("\n🛰 | transform money to the ") + f'<code>{wallet_bot}</code>' + makeFont("\n\n🔐 | or send a transaction link from tronscan to check it -> /check LINK"),
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

    elif call.data == "backhome_admin":
        try:
            await bot.edit_message_text(
                makeFont("🌊 | Sector Bot is online\n🎛 | Select one option below"),
                call.message.chat.id,
                call.message.id,
                reply_markup=home_admin_keyboard
            )
        except:pass