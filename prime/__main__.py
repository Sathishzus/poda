import asyncio
import importlib
import re

import uvloop
from pyrogram import filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from prime import (BOT_NAME, BOT_USERNAME, USERBOT_NAME, aiohttpsession,
                 app)
from prime.modules import ALL_MODULES
from prime.modules.sudoers import bot_sys_stats
from prime.utils import paginate_modules
from prime.utils.dbfunctions import clean_restart_stage

loop = asyncio.get_event_loop()

HELPABLE = {}


async def start_bot():
    restart_data = await clean_restart_stage()
    if restart_data:
        print("[INFO]: SENDING RESTART STATUS")
        try:
            await app.edit_message_text(
                restart_data["chat_id"],
                restart_data["message_id"],
                "**Restarted Successfully**",
            )
        except Exception:
            pass
    for module in ALL_MODULES:
        imported_module = importlib.import_module(
            "prime.modules." + module
        )
        if (
            hasattr(imported_module, "__MODULE__")
            and imported_module.__MODULE__
        ):
            imported_module.__MODULE__ = imported_module.__MODULE__
            if (
                hasattr(imported_module, "__HELP__")
                and imported_module.__HELP__
            ):
                HELPABLE[
                    imported_module.__MODULE__.lower()
                ] = imported_module
    bot_modules = ""
    j = 1
    for i in ALL_MODULES:
        if j == 4:
            bot_modules += "|{:<15}|\n".format(i)
            j = 0
        else:
            bot_modules += "|{:<15}".format(i)
        j += 1
    print(
        "+===============================================================+"
    )
    print(
        "|                              PRIME                              |"
    )
    print(
        "+===============+===============+===============+===============+"
    )
    print(bot_modules)
    print(
        "+===============+===============+===============+===============+"
    )
    print(f"[INFO]: BOT STARTED AS {BOT_NAME}!")
    print(f"[INFO]: USERBOT STARTED AS {USERBOT_NAME}!")
    await idle()
    print("[INFO]: STOPPING BOT AND CLOSING AIOHTTP SESSION")
    await aiohttpsession.close()





if __name__ == "__main__":
    uvloop.install()
    loop.run_until_complete(start_bot())
