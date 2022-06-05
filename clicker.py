# KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
# YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
# KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
#              © Copyright 2022
#
#          https://t.me/i_kyk
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @i_kyk

from .. import loader, utils
from telethon.tl.types import Message
import logging
import asyncio

from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.errors.rpcerrorlist import BotResponseTimeoutError

logger = logging.getLogger(__name__)


@loader.tds
class KyKClickerMod(loader.Module):
    """Clicker"""

    strings = {"name": "KyKClicker"}
    _chat = 1543388590
    _request_timeout = 3

    async def client_ready(self, client, db) -> None:
        self._db = db
        self._client = client
        self._tg_id = (await client.get_me()).id

    async def startkykcmd(self, message: Message) -> None:
        """Start clicking"""
        await message.edit("🔎 <b>Ищу сообщения...</b>")
        messages = {}

        async for msg in self._client.iter_messages(self._chat, limit=50):
            if not getattr(msg, "reply_markup", False):
                continue

            try:
                data = msg.reply_markup.rows[0].buttons[1].data
            except (AttributeError, IndexError):
                continue

            logger.info(data)

            if data == b"payTaxesGenerator":
                messages["generator"] = msg
            elif data == b"payTaxesGarden":
                messages["garden"] = msg
            elif data == b"payTaxesFarm":
                messages["farm"] = msg
            elif data == b"payTaxes":
                messages["business"] = msg

            found_all = True

            for i in {"farm", "garden", "business", "generator"}:
                if i not in messages:
                    found_all = False
                    break

            if found_all:
                break

        for i in {"farm", "garden", "business", "generator"}:
            if i not in messages:
                await message.edit("🚫 <b>Не могу найти сообщения</b>")
                return

        messages_formatted = (
            f"<b>Генератор</b>: <a href=\"https://t.me/c/{self._chat}/{messages['generator'].id}\">#{messages['generator'].id}</a>\n"
            f"<b>Сад</b>: <a href=\"https://t.me/c/{self._chat}/{messages['garden'].id}\">#{messages['garden'].id}</a>\n"
            f"<b>Ферма</b>: <a href=\"https://t.me/c/{self._chat}/{messages['farm'].id}\">#{messages['farm'].id}</a>\n"
            f"<b>Бизнес</b>: <a href=\"https://t.me/c/{self._chat}/{messages['business'].id}\">#{messages['business'].id}</a>\n\n"
        )

        await message.edit("✅ <b>Сообщения найдены!</b>\n" "<i>Запускаю кликер...</i>")

        await self.inline.form(
            message=utils.get_chat_id(message),
            text=f"🍏 <b>Работаю...</b>\n\n{messages_formatted}",
            reply_markup=[[{"text": "🚨 Остановить", "data": "kykfarmstop"}]],
        )

        self._db.set(self.strings["name"], "state", True)

        async def click(message_id: int, data: bytes):
            try:
                await self._client(
                    GetBotCallbackAnswerRequest(
                        self._chat,
                        message_id,
                        data=data,
                    )
                )
            except BotResponseTimeoutError:
                pass  # Ignore error bc bot doesn't answer callback query

            return True

        while self._db.get(self.strings["name"], "state", False):
            for message_id, data in [
                (messages["generator"].id, b"payTaxesGenerator"),
                (messages["business"].id, b"payTaxes"),
                (messages["farm"].id, b"payTaxesFarm"),
                (messages["garden"].id, b"pourGarden"),
                (messages["garden"].id, b"payTaxesGarden"),
            ]:
                if not await click(message_id, data):
                    return

                await asyncio.sleep(self._request_timeout)

            await asyncio.sleep(60 * 60)

    async def kyk_callback_handler(self, call: "InlineCall"):  # noqa: F821
        if call.data != "kykfarmstop" or call.from_user.id not in [self._tg_id]:
            return

        self._db.set(self.strings["name"], "state", False)
        await call.answer("Остановлено!")
        await getattr(self.inline, "bot", self.inline._bot).edit_message_text(
            inline_message_id=call.inline_message_id,
            text="🚨 <b>Остановлено</b>",
            parse_mode="HTML",
        )
