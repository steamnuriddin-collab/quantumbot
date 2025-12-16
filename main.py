import os
import logging
import asyncio
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

CRYPTO_IDS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana"
}


BOT_TOKEN = "8410698247:AAE0fkh3PriioG2Dy3fZN23V4B7p1eo2lEE"
DJANGO_SAVE_URL = "http://127.0.0.1:8000/api/save_message/"
DJANGO_UPLOAD_URL = "http://127.0.0.1:8000/api/upload/"
DJANGO_CHECK_USER_URL = "http://127.0.0.1:8000/api/check_user/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

BOT_MESSAGES = {}


PRODUCTS = {
    "p1": {"name_uz": "Spice ✨", "name_ru": "Спайс ✨", "price": 2410, "image": "https://narcological-clinic.ru/wp-content/uploads/2021/04/the-smoking-drug-spice.jpg"},
    "p2": {"name_uz": "Gash ☘️",  "name_ru": "Гаш ☘️",   "price": 4180, "image": "https://newsroom.kz/uploads/resized-images/2020/12/99326_boshka.jpg"},
    "p3": {"name_uz": "Mefedron 🗯️",   "name_ru": "Меф 🗯️", "price": 6120, "image": "https://abkhazinform.com/media/k2/items/cache/8007e3e80cde5eb6f0002eeca569b382_XL.jpg"},
    "p4": {"name_uz": "Chars 💥", "name_ru": "Чарс 💥",  "price": 4070, "image": "https://images.genius.com/a3d205a3c32cf6e48d610ceed33aa7a9.1000x750x1.jpg"},
}

REGIONS = {
    "uz": [
        ("r1", "Jizzax"),
        ("r2", "Guliston"),
        ("r3", "Yangiyer"),
        ("r4", "Xovos"),
        ("r5", "Chirchiq"),
        ("r6", "Yangibozor"),
        ("r7", "Baxt"),
        ("r8", "Sirdaryo"),
        ("r9", "Toshkent shahar"),
    ],
    "ru": [
        ("r1", "Джиззах"),
        ("r2", "Гулистан"),
        ("r3", "Янгиер"),
        ("r4", "Ховос"),
        ("r5", "Чирчик"),
        ("r6", "Янгибозор"),
        ("r7", "Бахт"),
        ("r8", "Сырдарья"),
        ("r9", "Город Ташкент"),
    ],
}

PAYMENTS = {
    "uz": [
        ("bal_top", "Balans To'ldirish 💳"),
        ("bal_pay", "Balans Orqali To'lov 💵"),
        ("eth", "Ethereum 🪙"),
        ("bnb", "BNB 🪙"),
        ("btc", "Bitcoin 🪙"),
        ("sol", "Solana 🪙"),
    ],
    "ru": [
        ("bal_top", "Пополнение баланса 💳"),
        ("bal_pay", "Оплата по балансу 💵"),
        ("eth", "Эфериум 🪙"),
        ("bnb", "BNB 🪙"),
        ("btc", "Биткойн 🪙"),
        ("sol", "Солaна 🪙"),
    ],
}


CRYPTO_WALLETS = {
    "eth": "0x59e80124443b0bdcbc08e23aeb34d8a0615b1367",
    "bnb": "0x59e80124443b0bdcbc08e23aeb34d8a0615b1367",
    "btc": "bc1qq3ea24242t4y7gt2rn2l3ncckychhh67hauxxj",
    "sol": "EJVEJZHsA2jqNNN2GsTS7VCWe9Zpo7UYLKj8Yh9PnxVg"
}

ADMINS = ["@NAVOPAY", "@best_obmenik", "@UZBobmennikTosh", "@zltsupport", "@caesar_obmen"]
OWNER = ["@aldikjanuzb"]
USER_LANG = {}



def register_bot_message(chat_id: int, message_id: int):
    BOT_MESSAGES.setdefault(chat_id, []).append(message_id)
    asyncio.create_task(auto_delete(chat_id, message_id))


async def auto_delete(chat_id: int, msg_id: int, delay=1800):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, msg_id)
    except Exception:
        pass


def get_payment_label(lang: str, paycode: str) -> str:
    for code, label in PAYMENTS[lang]:
        if code == paycode:
            return label
    return paycode



def send_to_django(data: dict):
    try:
        requests.post(DJANGO_SAVE_URL, json=data, timeout=5)
    except Exception as e:
        logging.error("Django ERROR: %s", e)


def is_user_blocked(chat_id: int) -> bool:
    try:
        r = requests.get(f"{DJANGO_CHECK_USER_URL}?chat_id={chat_id}", timeout=5)
        return r.json().get("blocked", False)
    except Exception:
        return False


def build_regions_kb(lang: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for rid, rname in REGIONS[lang]:
        kb.add(
            types.InlineKeyboardButton(
                text=rname,
                callback_data=f"region:{lang}:{rid}"
            )
        )
    kb.adjust(2)
    return kb.as_markup()



def build_products_kb(lang: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for pid, info in PRODUCTS.items():
        name = info["name_uz"] if lang == "uz" else info["name_ru"]
        kb.add(
            types.InlineKeyboardButton(
                text=name,
                callback_data=f"prod:{lang}:{pid}"
            )
        )
    kb.adjust(2)
    return kb.as_markup()



def build_qty_kb(lang: str, pid: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for q in ["0.5", "1", "2"]:
        kb.add(
            types.InlineKeyboardButton(
                text=q,
                callback_data=f"qty:{pid}:{q}"
            )
        )
    kb.adjust(3)
    return kb.as_markup()



def build_payments_kb(lang: str, pid: str, qty_str: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, label in PAYMENTS[lang]:
        kb.add(
            types.InlineKeyboardButton(
                text=label,
                callback_data=f"pay:{lang}:{pid}:{qty_str}:{code}"
            )
        )
    kb.adjust(2)
    return kb.as_markup()


def get_crypto_rates_rub():
    try:
        ids = ",".join(CRYPTO_IDS.values())
        r = requests.get(
            COINGECKO_API,
            params={
                "ids": ids,
                "vs_currencies": "rub"
            },
            timeout=10
        )

        data = r.json()

        if not isinstance(data, dict):
            return {}

        rates = {}

        for key, cid in CRYPTO_IDS.items():
            if cid in data and "rub" in data[cid]:
                rates[key] = data[cid]["rub"]

        return rates

    except Exception as e:
        logging.error(f"CoinGecko error: {e}")
        return {}


def rub_to_crypto(rub_amount: int, rates: dict):
    if not rates:
        return {}

    result = {}
    for code, rub_price in rates.items():
        if rub_price and rub_price > 0:
            result[code] = rub_amount / rub_price
    return result



@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if is_user_blocked(message.chat.id):
        await message.answer("❌ Siz bloklangansiz.")
        return

    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang:uz"),
        types.InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang:ru")
    )
    msg = await message.answer("Tilni tanlang / Выберите язык:", reply_markup=kb.as_markup())
    register_bot_message(message.chat.id, msg.message_id)
    send_to_django({"chat_id": message.chat.id, "type": "command", "text": "/start"})


@dp.callback_query(F.data.startswith("lang:"))
async def on_lang(cb: types.CallbackQuery):
    _, lang = cb.data.split(":", 1)

    USER_LANG[cb.from_user.id] = lang

    await cb.message.answer(
        "Viloyat yoki Shaharni Tanlang:"
        if lang == "uz"
        else "Выберите регион:",
        reply_markup=build_regions_kb(lang)
    )
    await cb.answer()



@dp.callback_query(F.data.startswith("region:"))
async def on_region(cb: types.CallbackQuery):
    _, lang, rid = cb.data.split(":", 2)

    USER_LANG[cb.from_user.id] = lang

    await cb.message.answer(
        "Mahsulotni Tanlang:"
        if lang == "uz"
        else "Выберите товар:",
        reply_markup=build_products_kb(lang)
    )
    await cb.answer()



@dp.callback_query(F.data.startswith("prod:"))
async def on_prod(cb: types.CallbackQuery):
    _, lang, pid = cb.data.split(":", 2)

    USER_LANG[cb.from_user.id] = lang

    info = PRODUCTS.get(pid)
    if not info:
        await cb.answer("Mahsulot topilmadi", show_alert=True)
        return


    name = info["name_uz"] if lang == "uz" else info["name_ru"]
    image = info.get("image")

    caption = (
        f"📦 <b>{name}</b>\n\nNechi gram kerak?"
        if lang == "uz"
        else f"📦 <b>{name}</b>\n\nСколько грамм нужно?"
    )

    if image:
        await cb.message.answer_photo(
            photo=image,
            caption=caption,
            reply_markup=build_qty_kb(lang, pid)
        )
    else:
        await cb.message.answer(
            caption,
            reply_markup=build_qty_kb(lang, pid)
        )

    await cb.answer()



@dp.callback_query(F.data.startswith("qty:"))
async def on_qty(cb: types.CallbackQuery):
    try:
        _, pid, q_str = cb.data.split(":", 2)
    except ValueError:
        await cb.answer("Invalid data", show_alert=True)
        return

    try:
        qty = float(q_str)
    except Exception:
        await cb.answer("Invalid quantity", show_alert=True)
        return

    info = PRODUCTS.get(pid)
    if not info:
        await cb.answer("Product not found", show_alert=True)
        return

    prev_text = (cb.message.text or "").lower()
    lang = USER_LANG.get(cb.from_user.id, "uz")

    name = info["name_uz"] if lang == "uz" else info["name_ru"]
    price = info["price"]
    total = int(price * qty)
    rates = get_crypto_rates_rub()
    crypto_prices = rub_to_crypto(total, rates)

    crypto_text = ""
    if crypto_prices:
        crypto_texts = {
           "uz":( 
                f"\n\n🪙<b>Kriptoda Narxlar:</b>\n"
                f"• BTC: <code>{crypto_prices.get('btc', 0):.8f}</code>\n"
                f"• BNB: <code>{crypto_prices.get('bnb', 0):.4f}</code>\n"
                f"• ETH: <code>{crypto_prices.get('eth', 0):.6f}</code>\n"
                f"• SOL: <code>{crypto_prices.get('sol', 0):.4f}</code>\n"
           ),
           "ru":(
                f"\n\n🪙<b>Цены на криптовалюты:</b>\n"
                f"• BTC: <code>{crypto_prices.get('btc', 0):.8f}</code>\n"
                f"• BNB: <code>{crypto_prices.get('bnb', 0):.4f}</code>\n"
                f"• ETH: <code>{crypto_prices.get('eth', 0):.6f}</code>\n"
                f"• SOL: <code>{crypto_prices.get('sol', 0):.4f}</code>\n"
           )
        }
        crypto_text = crypto_texts.get(lang, "")


    text = (
        f"📦 {name}\n🔢 Miqdor: <b>{q_str} gr</b>\n💰 Umumiy narx: <b>{total:,} rubl</b>\n\n{crypto_text}\n\nTo‘lov turini tanlang:"
        if lang == "uz" else
        f"📦 {name}\n🔢 Количество: <b>{q_str} гр</b>\n💰 Общая цена: <b>{total:,} рубл</b>\n\n{crypto_text}\n\nВыберите способ оплаты:"
    )

    await cb.message.answer(text, reply_markup=build_payments_kb(lang, pid, q_str))
    await cb.answer()


@dp.callback_query(F.data.startswith("pay:"))
async def on_pay(cb: types.CallbackQuery):

    user_balance = 0  

    wallets_text = "\n".join(
        f"{k.upper()}: {v}" for k, v in CRYPTO_WALLETS.items()
    
    )
    owners_text = "\n".join(OWNER)

    try:
        _, lang, pid, q_str, paycode = cb.data.split(":", 4)
    except ValueError:
        await cb.answer("Invalid data", show_alert=True)
        return

    try:
        qty = float(q_str)
    except ValueError:
        await cb.answer("Invalid quantity", show_alert=True)
        return

    info = PRODUCTS.get(pid)
    if not info:
        await cb.answer("Product not found", show_alert=True)
        return

    total = int(info["price"] * qty)
    name = info["name_uz"] if lang == "uz" else info["name_ru"]

    if paycode == "bal_pay":
        if user_balance < total:
            text = (
                "❌ Hisobingizda Mablag‘ yetarli emas!\n\n"
                "Iltimos 'Balans To'ldirish' Tugmasi Orqali Rekvizitlarni Olib Hisobingizni To‘ldiring\n\n"
                "❗Hisobingizni To'ldiring va To'lov Chekini Adminga Yuborishni Unutmang\n" + owners_text
                if lang == "uz" else
                "❌ Недостаточно средств на балансе!\n\n"
                "Пожалуйста пополните свой счет используя кнопку 'Пополнение Баланса'\n\n"
                "❗Не забудьте пополнить свой счет и отправить платежный чек админy\n" + owners_text
            )
            await cb.message.answer(text)
            await cb.answer()
            return

    wallet = CRYPTO_WALLETS.get(paycode)

    owners_text = "\n".join(OWNER)
    admins_text = "\n".join(ADMINS)

    rates = get_crypto_rates_rub()
    crypto_prices = rub_to_crypto(total, rates)

    crypto_text = ""
    if crypto_prices:
        crypto_texts = {
           "uz":( 
                f"\n\n🪙<b>Kriptoda Narxlar:</b>\n"
                f"• BTC: <code>{crypto_prices.get('btc', 0):.8f}</code>\n"
                f"• BNB: <code>{crypto_prices.get('bnb', 0):.4f}</code>\n"
                f"• ETH: <code>{crypto_prices.get('eth', 0):.6f}</code>\n"
                f"• SOL: <code>{crypto_prices.get('sol', 0):.4f}</code>\n"
           ),
           "ru":(
                f"\n\n🪙<b>Цены на криптовалюты:</b>\n"
                f"• BTC: <code>{crypto_prices.get('btc', 0):.8f}</code>\n"
                f"• BNB: <code>{crypto_prices.get('bnb', 0):.4f}</code>\n"
                f"• ETH: <code>{crypto_prices.get('eth', 0):.6f}</code>\n"
                f"• SOL: <code>{crypto_prices.get('sol', 0):.4f}</code>\n"
           )
        }
        crypto_text = crypto_texts.get(lang, "")

    if wallet:
        text = (
            f"💳 To‘lov turi: <b>{get_payment_label(lang, paycode)}</b>\n"
            f"📦 Mahsulot: <b>{name}</b>\n"
            f"🔢 Miqdor: <b>{q_str} gr</b>\n"
            f"💰 Umumiy summa: <b>{total:,} rubl</b>\n\n"
            f"{crypto_text}\n\n"
            f"🔗 Hamyon:\n<code>{wallet}</code>\n\n"
            f"👥 Obmenniklar:\n{admins_text}\n\n"
            f"❗ To‘lovdan so‘ng chekni adminga yuboring:\n{owners_text}"
            if lang == "uz" else
            f"💳 Способ оплаты: <b>{get_payment_label(lang, paycode)}</b>\n"
            f"📦 Товар: <b>{name}</b>\n"
            f"🔢 Количество: <b>{q_str} гр</b>\n"
            f"💰 Сумма: <b>{total:,} руб</b>\n\n"
            f"{crypto_text}\n\n"
            f"🔗 Кошелек:\n<code>{wallet}</code>\n\n"
            f"👥 Обменники:\n{admins_text}\n\n"
            f"❗ После оплаты отправьте чек админу:\n{owners_text}"
        )
    else:
        text = (
            f"Hisobingizni To'ldirishni Xoxlaysizmi? Obmeniki 👇\n{admins_text}\n\n❗Hisobingizni To'ldiring va To'lov Chekini Adminga Yuborishni Unutmang\n{owners_text}\n\nKripto Hamyonlar 👇\n{wallets_text}"
            if lang == "uz" else
            f"Хотите пополнить свой счёт? Обменики 👇\n{admins_text}\n\n❗Не забудьте пополнить свой счет и отправить платежный чек админy\n{owners_text}\n\nКриптовалютные кошельки 👇\n{wallets_text}"
        )
    

    await cb.message.answer(text)
    await cb.answer()



def upload_to_django(file_url, chat_id):
    try:
        tf = requests.get(file_url, timeout=10)
        if tf.status_code != 200:
            return None
        files = {"file": ("media.jpg", tf.content)}
        data = {"chat_id": chat_id}
        r = requests.post(DJANGO_UPLOAD_URL, files=files, data=data, timeout=10)
        try:
            return r.json().get("url")
        except Exception:
            return None
    except Exception:
        return None


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    media_url = upload_to_django(url, message.chat.id)
    send_to_django({"chat_id": message.chat.id, "username": message.from_user.username, "type": "photo", "file_url": media_url})
    await message.answer("📸 Rasm qabul qilindi!")


@dp.message(F.video)
async def handle_video(message: types.Message):
    file_id = message.video.file_id
    file = await bot.get_file(file_id)
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    media_url = upload_to_django(url, message.chat.id)
    send_to_django({"chat_id": message.chat.id, "username": message.from_user.username, "type": "video", "file_url": media_url})
    await message.answer("🎥 Video qabul qilindi!")


@dp.message()
async def fallback(message: types.Message):
    send_to_django({"chat_id": message.chat.id, "username": message.from_user.username, "type": "message", "text": message.text})
    await message.answer("✔ Xabar qabul qilindi")


async def main():
    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
