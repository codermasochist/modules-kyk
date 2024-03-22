

# meta developer: @i_kyk

# require httpx

import json
from typing import List

import httpx
from telethon import types

from .. import loader, utils  # type: ignore


@loader.tds
class KYKGPTMod(loader.Module):
    "KYK GPT"
    strings = {
        "name": "KYKGPT",
        "pref": "<b>[GPT4-Turbo]</b> {}",
        "prefcgpt": "<b>[GPT]</b> {}",
        "prefom": "<b>[OpenModerator]</b> {}",
        "result": (
            "<b>Запрос</b>: {prompt}\n\n<b>GPT:</b> {text}\n\n"
            "<b>Потрачено токенов:</b> {prompt_tokens}+{completion_tokens}={total_tokens}"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            *("MODEL", "azure-gpt4-turbo", "Модель GPT"),
            *(
                "COMPLETION_ENDPOINT",
                "https://cooders.veryscrappy.moe/proxy/azure/openai/v1/chat/completions",
                "Completions API endpoint",
            ),
            *("MAX_TOKENS", 128000, "Maximum tokens"),
            *("TEMPERATURE", 0.5, "Temperature"),
            *("DEBUG", False, "Debug mode for answers"),
            *(
                "CGPT_ENDPOINT",
                "https://whiterose1.hopto.org/proxy/v1/chat/completions",
                "ChatGPT API endpoint",
            ),
            *("CGPT_MODEL", "gpt-4-turbo-preview", "ChatGPT model name"),
            *("CGPT_TEMPERATURE", 0.5, "ChatGPT temperature"),
            *(
                "CGPT_SYSTEM_MSG",
                "",
                "ChatGPT system message",
            ),
            *(
                "MODERATION_ENDPOINT",
                "https://api.openai.com/v1/moderations",
                "OpenAI's moderation endpoint",
            ),
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._db_name = "KYK_GPT"
        self.messages_history_default = [
            {
                "role": "system",
                "content": self.config["CGPT_SYSTEM_MSG"],
            }
        ]
        self.messages_history = [] + self.messages_history_default

    @loader.owner
    async def setgptcmd(self, m: types.Message):
        "<token> - Нужен ключ, брать у @i_kyk"
        token: str or None = utils.get_args_raw(m)
        if not token:
            return await utils.answer(m, self.strings("pref", m).format("No token"))
        self._db.set(self._db_name, "token", token)
        await utils.answer(m, self.strings("pref", m).format("Token set"))

    @loader.owner
    async def nousagecmd(self, m: types.Message):
        "<text/reply_to_text> - generate text"
        token = self._db.get(self._db_name, "token")
        if not token:
            return await utils.answer(
                m, self.strings("pref", m).format("Нужен ключ, брать у @i_kyk .setgpt <token>")
            )
        prompt = utils.get_args_raw(m)
        reply = await m.get_reply_message()
        if reply:
            prompt = prompt or reply.raw_text

        if not prompt:
            return await utils.answer(m, self.strings("pref", m).format("Нет текста"))

        m = await utils.answer(m, self.strings("pref", m).format("Генерирую ответ..."))
        async with httpx.AsyncClient(timeout=3000) as client:
            response = await client.post(
                self.config["COMPLETION_ENDPOINT"],
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "model": self.config["MODEL"],
                    "prompt": prompt,
                    "max_tokens": self.config["MAX_TOKENS"],
                    "temperature": self.config["TEMPERATURE"],
                },
            )
            j = response.json()
            if response.status_code != 200:
                if self.config["DEBUG"]:
                    return await utils.answer(
                        m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                    )
                return await utils.answer(
                    m,
                    self.strings("pref", m).format(
                        f"<b>Error:</b> {response.status_code} {response.reason_phrase}"
                    ),
                )
            if self.config["DEBUG"]:
                return await utils.answer(
                    m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                )
            text = j["choices"][0]["text"].strip("\n").strip(" ")
            if j["choices"][0]["finish_reason"] == "length":
                text += ""
            await utils.answer(
                m,
                self.strings("pref", m).format(
                    self.strings("result", m).format(
                        prompt=prompt, text=text, **j["usage"]
                    )
                ),
            )

    @loader.owner
    async def gptcmd(self, m: types.Message):
        "<текст/ответом на сообщ> - дефолт команда, юзай ее"
        token = self._db.get(self._db_name, "token")
        if not token:
            return await utils.answer(
                m,
                self.strings("prefcgpt", m).format("Нужен ключ, брать у @i_kyk .setgpt <token>"),
            )

        prompt = utils.get_args_raw(m)
        reply = await m.get_reply_message()
        if reply:
            prompt = prompt or reply.raw_text

        if not prompt:
            return await utils.answer(m, self.strings("prefcgpt", m).format("Введи запрос!"))
        m = await utils.answer(m, self.strings("prefcgpt", m).format("Генерирую ответ..."))
        async with httpx.AsyncClient(timeout=3000) as client:
            response = await client.post(
                self.config["CGPT_ENDPOINT"],
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={
                    "model": self.config["CGPT_MODEL"],
                    "messages": self.messages_history + [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": self.config["CGPT_TEMPERATURE"],
                },
            )
            j = response.json()
            if response.status_code != 200:
                if self.config["DEBUG"]:
                    return await utils.answer(
                        m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                    )
                return await utils.answer(
                    m,
                    self.strings("prefcgpt", m).format(
                        f"<b>Error:</b> {response.status_code} {response.reason_phrase}"
                    ),
                )
            if self.config["DEBUG"]:
                return await utils.answer(
                    m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                )
            text = j["choices"][0]["message"]["content"].strip("\n").strip(" ")
            self.messages_history.append({"role": "user", "content": prompt})
            self.messages_history.append({"role": "assistant", "content": text})

            if j["choices"][0]["finish_reason"] == "length":
                text += ""

            await utils.answer(
                m,
                self.strings("prefcgpt", m).format(
                    self.strings("result", m).format(
                        prompt=prompt, text=text, **j["usage"]
                    )
                ),
            )

    @loader.owner
    async def cgptresetcmd(self, m: types.Message):
        "Reset ChatGPT history"
        self.messages_history = [] + self.messages_history_default
        await utils.answer(m, self.strings("prefcgpt", m).format("History reset"))

    @loader.owner
    async def omodercmd(self, m: types.Message):
        "turn chat text moderation with moderation endpoint (eng only)"
        token = self._db.get(self._db_name, "token")
        if not token:
            return await utils.answer(
                m,
                self.strings("prefom", m).format("No token set! Use .setgpt <token>"),
            )

        if not m.chat:
            return await utils.answer(
                m, self.strings("prefom", m).format("Only chat command")
            )

        chats: List[int] = self._db.get(self._db_name, "moderation", [])
        if m.chat.id not in chats:
            chats.append(m.chat.id)
            await utils.answer(
                m, self.strings("prefom", m).format("Moderation enabled for this chat")
            )
        else:
            chats.remove(m.chat.id)
            await utils.answer(
                m, self.strings("prefom", m).format("Moderation disabled for this chat")
            )
        self._db.set(self._db_name, "moderation", chats)

    async def watcher(self, m: types.Message):
        if not isinstance(m, types.Message):
            return
        if not m.chat:
            return
        chats: List[int] = self._db.get(self._db_name, "moderation", [])
        if m.chat.id not in chats:
            return
        token = self._db.get(self._db_name, "token")
        async with httpx.AsyncClient(timeout=3000) as client:
            response = await client.post(
                self.config["MODERATION_ENDPOINT"],
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json={"input": m.raw_text},
            )
            j = response.json()
            if response.status_code != 200:
                if self.config["DEBUG"]:
                    return await utils.answer(
                        m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                    )
                return await utils.answer(
                    m,
                    self.strings("prefcgpt", m).format(
                        f"<b>Error:</b> {response.status_code} {response.reason_phrase}"
                    ),
                )
            if self.config["DEBUG"]:
                return await utils.answer(
                    m, "<code>{}</code>".format(str(json.dumps(j, indent=1)))
                )
            if j["results"]["flagged"]:
                return await m.delete()
