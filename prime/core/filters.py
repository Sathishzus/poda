from pyrogram import filters as filters_
from pyrogram.types import Message

from prime import OWNER_ID, SUDOERS
from prime.modules.trust import get_spam_data
from prime.utils.functions import get_urls_from_text


def url(_, __, message: Message) -> bool:
    # Can't use entities to check for url because
    # monospace removes url entity

    # TODO Fix undetection of those urls which
    # doesn't have schema, ex-facebook.com

    text = message.text or message.caption
    if not text:
        return False
    return bool(get_urls_from_text(text))


async def spam(_, __, message: Message) -> bool:
    text = message.text or message.caption
    if not text:
        return False
    return (await get_spam_data(message, text)).is_spam


async def admin(_, __, message: Message) -> bool:
    if message.chat.type not in ["group", "supergroup"]:
        return False
    if not message.from_user:
        if not message.sender_chat:
            return False
        return True
    # Calling iter_chat_members again and again
    # doesn't causes floodwaits, idk why, maybe it's
    # cached or something, that's why using it.
    return message.from_user.id in [
        member.user.id
        async for member in message._client.iter_chat_members(
            message.chat.id, filter="administrators"
        )
    ]


def entities(_, __, message: Message) -> bool:
    return bool(message.entities)


async def profanity(_, __, message: Message) -> bool:
    text = message.text or message.caption
    if not text:
        return False
    return (await get_spam_data(message, text)).profanity


def anonymous(_, __, message: Message) -> bool:
    return bool(message.sender_chat)


def sudoers(_, __, message: Message) -> bool:
    if not message.from_user:
        return False
    return message.from_user.id in SUDOERS


def owner(_, __, message: Message) -> bool:
    if not message.from_user:
        return False
    return message.from_user.id == OWNER_ID


class Filters:
    pass


filters = Filters
filters.url = filters_.create(url)
filters.spam = filters_.create(spam)
filters.admin = filters_.create(admin)
filters.entities = filters_.create(entities)
filters.profanity = filters_.create(profanity)
filters.anonymous = filters_.create(anonymous)
filters.sudoers = filters_.create(sudoers)
filters.owner = filters_.create(owner)
