 
# ---------------------------------------------------
# File Name: shrink.py
# Description: A Pyrogram bot for downloading files from Telegram channels or groups 
#              and uploading them back to Telegram.
# Author: Gagan
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Last Modified: 2025-01-11
# Version: 2.0.5
# License: MIT License
# ---------------------------------------------------

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import random
import requests
import string
import aiohttp
from html import escape
from devgagan import app
from devgagan.core.func import *
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB, WEBSITE_URL, AD_API, LOG_GROUP  
 
 
tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]
 
 
async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)
 
 
 
Param = {}
 
START_IMAGE_URL = "https://files.catbox.moe/cuivxy.jpg"
PROFILE_LINK = "https://t.me/itzrishu"

 
async def generate_random_param(length=8):
    """Generate a random parameter."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
 
 
async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
 
     
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()   
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None
 
 
async def is_user_verified(user_id):
    """Check if a user has an active session."""
    session = await token.find_one({"user_id": user_id})
    return session is not None
 
 
def start_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("DEVELOPER 🧑‍💻", url=PROFILE_LINK),
                InlineKeyboardButton("UPDATES 🚨", url=PROFILE_LINK),
            ],
            [
                InlineKeyboardButton("Help", callback_data="start_help"),
                InlineKeyboardButton("ABOUT ME 😎", callback_data="about_me"),
            ],
        ]
    )


async def send_start_message(message):
    """Send the redesigned welcome message and its action buttons."""
    start_text = (
        "<b><i>Yoo 𒐕𒐕𒐕 !! Welcome Aboard</i></b>\n\n"
        "<b><i>I Can Save Posts From Channels or Groups\n"
        "Even When Forwarding is Disabled (Yep, I’m\n"
        "That Powerful😎)</i></b>\n\n"
        "<b><i>For Public Channel Just Send the Link of the\n"
        "Post & For Private Channel Use /login First\n"
        "🔑</i></b>"
    )
    try:
        await message.reply_photo(
            START_IMAGE_URL,
            caption=start_text,
            reply_markup=start_keyboard(),
            parse_mode="html",
        )
    except Exception:
        await message.reply(
            start_text,
            reply_markup=start_keyboard(),
            parse_mode="html",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("start"))
async def token_handler(client, message):
    """Handle the /start command and deep-link verification."""
    join = await subscribe(client, message)
    if join == 1:
        return
    user_id = message.chat.id
    if len(message.command) <= 1:
        await send_start_message(message)
        return  
 
    param = message.command[1] if len(message.command) > 1 else None
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return
 
     
    if param:
        if user_id in Param and Param[user_id] == param:
             
            await token.insert_one({
                "user_id": user_id,
                "param": param,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=3),
            })
            del Param[user_id]   
            await message.reply("✅ You have been verified successfully! Enjoy your session for next 3 hours.")
            return
        else:
            await message.reply("❌ Invalid or expired verification link. Please generate a new token.")
            return


@app.on_callback_query(filters.regex(r"^start_help$"))
async def start_help_callback(client, callback_query):
    """Open the existing /help flow and remove the welcome message."""
    from devgagan.modules.start import send_or_edit_help_page

    await callback_query.answer()
    await send_or_edit_help_page(client, callback_query.message, 0)


@app.on_callback_query(filters.regex(r"^about_me$"))
async def about_me_callback(client, callback_query):
    """Show the bot details screen from the welcome message."""
    user = callback_query.from_user
    display_name = escape(
        " ".join(part for part in (user.first_name, user.last_name) if part)
    )
    profile_url = f"tg://user?id={user.id}"
    about_text = (
        "<b><i>▸⁉️ MY DETAILS ❞</i></b>\n\n"
        f"<b>• MY NAME :</b> Save restricted content bot\n"
        f"<b>• MY BEST FRIEND :</b> <a href=\"{profile_url}\">{display_name}</a> ❤️\n"
        "<b>• DEVELOPER :</b> ISHAN BOTZ\n"
        "<b>• LIBRARY :</b> PYROGRAM\n"
        "<b>• LANGUAGE :</b> PYTHON 3\n"
        "<b>• DATABASE :</b> MONGO DB\n"
        "<b>• BOT SERVER :</b> HEROKU\n"
        "<b>• BUILD STATUS :</b> V2.7.1 [STABLE]"
    )
    about_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("SUPPORT 📡", url=PROFILE_LINK),
                InlineKeyboardButton("JOIN NOW 🚨", url=PROFILE_LINK),
            ],
            [
                InlineKeyboardButton("CLOSE ❌", callback_data="close_about"),
                InlineKeyboardButton("⬅️ Back", callback_data="about_back"),
            ],
        ]
    )
    await callback_query.answer()
    try:
        await callback_query.message.edit_media(
            media=InputMediaPhoto(
                START_IMAGE_URL,
                caption=about_text,
                parse_mode="html",
            ),
            reply_markup=about_keyboard,
        )
    except Exception:
        await callback_query.message.edit_text(
            about_text,
            reply_markup=about_keyboard,
            parse_mode="html",
            disable_web_page_preview=True,
        )


@app.on_callback_query(filters.regex(r"^close_about$"))
async def close_about_callback(client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()


@app.on_callback_query(filters.regex(r"^about_back$"))
async def about_back_callback(client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()
    await send_start_message(callback_query.message)
 
@app.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
     
    freecheck = await chk_user(message, user_id)
    if freecheck != 1:
        await message.reply("You are a premium user no need of token 😉")
        return
    if await is_user_verified(user_id):
        await message.reply("✅ Your free session is already active enjoy!")
    else:
         
        param = await generate_random_param()
        Param[user_id] = param   
 
         
        deep_link = f"https://t.me/{client.me.username}?start={param}"
 
         
        shortened_url = await get_shortened_url(deep_link)
        if not shortened_url:
            await message.reply("❌ Failed to generate the token link. Please try again.")
            return
 
         
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Verify the token now...", url=shortened_url)]]
        )
        await message.reply("Click the button below to verify your free access token: \n\n> What will you get ? \n1. No time bound upto 3 hours \n2. Batch command limit will be FreeLimit + 20 \n3. All functions unlocked", reply_markup=button)
 