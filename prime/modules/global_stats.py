import asyncio
import os
import subprocess
import time

import psutil

from pyrogram import filters

from prime.utils import formatter
from prime import BOT_ID, BOT_NAME, SUDOERS, app ,bot_start_time
from prime.core.decorators.errors import capture_err
from prime.modules import ALL_MODULES
from prime.utils.dbfunctions import (get_blacklist_filters_count,
                                   get_filters_count, get_gbans_count,
                                   get_karmas_count, get_notes_count,
                                   get_served_chats, get_served_users,
                                   get_warns_count,
                                   remove_served_chat)
from prime.utils.http import get
from prime.utils.inlinefuncs import keywords_list

""" CHAT WATCHER IS IN filters.py"""


@app.on_message(
    filters.command("stats")
    & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def global_stats(_, message):
    m = await app.send_message(
        message.chat.id,
        text="__**Analysing Stats**__",
        disable_web_page_preview=True,
    )

    # For bot served chat and users count
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    await m.edit(
        f"""🌐 __**Generating Statistics Report**__ 🌐

🖥 __**Database Name:Mongo DB**__

⏳ __**Should Take {len(served_chats)*2}+ Seconds.**__""",
        disable_web_page_preview=True,
    )
    for served_chat in served_chats:
        try:
            await app.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(2)
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
            pass
    served_users = await get_served_users()
    # Gbans count
    gbans = await get_gbans_count()
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Blacklisted filters count across chats
    _filters = await get_blacklist_filters_count()
    blacklist_filters_count = _filters["filters_count"]
    blacklist_filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # System stats
    bot_uptime = int(time.time() - bot_start_time)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    process = psutil.Process(os.getpid())
    

    msg = f""" 🌐 Second DataBase 🌐
**Global Stats of {BOT_NAME}**:

🔇 **{gbans}** Globally banned users.

🔞 **{blacklist_filters_count}** Blacklist Filters, Across **{blacklist_filters_chats_count}** chats.

♻️ **{filters_count}** Filters, Across **{filters_chats_count}** chats.

⛔️ **{warns_count}** Warns, Across **{warns_chats_count}** chats.

👍 **{karmas_count}** Karma, Across **{karmas_chats_count}** chats.

🧍‍♂️ **{len(served_users)}** Users, Across **{len(served_chats)}** chats.

UPTIME: {formatter.get_readable_time((bot_uptime))}
BOT: {round(process.memory_info()[0] / 1024 ** 2)} MB
CPU: {cpu}%
RAM: {mem}%
DISK: {disk}%

"""
    await m.edit(msg, disable_web_page_preview=True)
