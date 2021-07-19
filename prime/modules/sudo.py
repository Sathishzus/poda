import os

from pyrogram import filters
from pyrogram.types import Message

from prime import BOT_ID, SUDOERS, USERBOT_PREFIX, app2
from prime.core.decorators.errors import capture_err
from prime.modules.userbot import edit_or_reply
from prime.utils.dbfunctions import add_sudo, get_sudoers, remove_sudo

__MODULE__ = "Sudo"
__HELP__ = """
**THIS MODULE IS ONLY FOR DEVS**

.useradd - To Add A User In Sudoers.
.userdel - To Remove A User From Sudoers.
.sudoers - To List Sudo Users.

**NOTE:**

Never add anyone to sudoers unless you trust them,
sudo users can do anything with your account, they
can even delete your account.
"""

@app2.on_message(
    filters.command("smartaddsudo")
    & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def useradd(_, message: Message):
    if not message.reply_to_message:
        return await edit_or_reply(
            message,
            text="Reply to someone's message to add him to sudoers.",
        )
    user_id = message.reply_to_message.from_user.id
    sudoers = await get_sudoers()
    if user_id in sudoers:
        return await edit_or_reply(
            message, text="User is already in sudoers."
        )
    if user_id == BOT_ID:
        return await edit_or_reply(
            message, text="You can't add assistant bot in sudoers."
        )
    added = await add_sudo(user_id)
    if added:
        await edit_or_reply(
            message,
            text="Successfully added user in sudoers, Bot will be restarted now.",
        )
        return os.execvp("python3", ["python3", "-m", "wbb"])
    await edit_or_reply(
        message, text="Something wrong happened, check logs."
    )


@app2.on_message(
    filters.command("smartdelsudo")
    & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def userdel(_, message: Message):
    if not message.reply_to_message:
        return await edit_or_reply(
            message,
            text="Reply to someone's message to remove him to sudoers.",
        )
    user_id = message.reply_to_message.from_user.id
    if user_id not in await get_sudoers():
        return await edit_or_reply(
            message, text="User is not in sudoers."
        )
    removed = await remove_sudo(user_id)
    if removed:
        await edit_or_reply(
            message,
            text="Successfully removed user from sudoers, Bot will be restarted now.",
        )
        return os.execvp("python3", ["python3", "-m", "prime"])
    await edit_or_reply(
        message, text="Something wrong happened, check logs."
    )


@app2.on_message(
    filters.command("smartsudolist")
    & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = ""
    for count, user_id in enumerate(sudoers, 1):
        user = await app2.get_users(user_id)
        user = user.first_name if not user.mention else user.mention
        text += f"{count}. {user}\n"
    await edit_or_reply(message, text=text)
