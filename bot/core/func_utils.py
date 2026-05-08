from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from json import loads as jloads
from re import findall
from math import floor
from os import path as ospath
from time import time, sleep
from traceback import format_exc
import asyncio
from asyncio import sleep as asleep, create_subprocess_shell
from asyncio.subprocess import PIPE
from base64 import urlsafe_b64encode, urlsafe_b64decode

from aiohttp import ClientSession
from aiofiles import open as aiopen
from aioshutil import rmtree as aiormtree
from html_telegraph_poster import TelegraphPoster
from feedparser import parse as feedparse
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton
from pyrogram.errors import MessageNotModified, FloodWait, UserNotParticipant, ReplyMarkupInvalid, MessageIdInvalid

from bot import bot, LOGS, Var
from .reporter import rep

# Shared executor to prevent resource exhaustion
executor = ThreadPoolExecutor(max_workers=cpu_count() * 4)

def handle_logs(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            await rep.report(format_exc(), "error")
    return wrapper

async def sync_to_async(func, *args, wait=True, **kwargs):
    loop = asyncio.get_running_loop()
    pfunc = partial(func, *args, **kwargs)
    future = loop.run_in_executor(executor, pfunc)
    return await future if wait else future

def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.get_running_loop().create_task(func(*args, **kwargs))
    return wrapper

async def getfeed(link, index=0):
    try:
        # Correctly offloads blocking feedparser to the executor
        feed = await sync_to_async(feedparse, link)
        return feed.entries[index]
    except IndexError:
        return None
    except Exception:
        LOGS.error(format_exc())
        return None

@handle_logs
async def aio_urldownload(link):
    async with ClientSession() as sess:
        async with sess.get(link) as data:
            image = await data.read()
    
    filename = link.split('/')[-1]
    path = f"thumbs/{filename}"
    
    # Corrected tuple check for extensions
    if not path.lower().endswith((".jpg", ".png", ".jpeg")):
        path += ".jpg"
        
    async with aiopen(path, "wb") as f:
        await f.write(image)
    return path

@handle_logs
async def get_telegraph(out):
    # This is a synchronous library, running in executor is safer
    def _poster():
        client = TelegraphPoster(use_api=True)
        client.create_api_token("Mediainfo")
        uname = Var.BRAND_UNAME.lstrip('@')
        page = client.post(
            title="Mediainfo",
            author=uname,
            author_url=f"https://t.me/{uname}",
            text=f"<pre>\n{out}\n</pre>",
        )
        return page.get("url")
    
    return await sync_to_async(_poster)

async def sendMessage(chat, text, buttons=None, get_error=False, **kwargs):
    try:
        if isinstance(chat, int):
            return await bot.send_message(chat_id=chat, text=text, disable_web_page_preview=True,
                                        disable_notification=False, reply_markup=buttons, **kwargs)
        else:
            return await chat.reply(text=text, quote=True, disable_web_page_preview=True, disable_notification=False,
                                    reply_markup=buttons, **kwargs)
    except FloodWait as f:
        await rep.report(f, "warning")
        await asleep(f.value * 1.2) # Use async sleep here!
        return await sendMessage(chat, text, buttons, get_error, **kwargs)
    except ReplyMarkupInvalid:
        return await sendMessage(chat, text, None, get_error, **kwargs)
    except Exception as e:
        await rep.report(format_exc(), "error")
        if get_error:
            raise e
        return str(e)

async def editMessage(msg, text, buttons=None, get_error=False, **kwargs):
    try:
        if not msg:
            return None
        return await msg.edit_text(text=text, disable_web_page_preview=True, 
                                        reply_markup=buttons, **kwargs)
    except FloodWait as f:
        await rep.report(f, "warning")
        await asleep(f.value * 1.2)
        return await editMessage(msg, text, buttons, get_error, **kwargs)
    except (MessageNotModified, MessageIdInvalid):
        return msg
    except Exception as e:
        await rep.report(format_exc(), "error")
        if get_error:
            raise e
        return str(e)
