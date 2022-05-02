# by t.me/yltned
from .. import loader, utils
import re


class BFGDrawingMod(loader.Module):
 """Модуль для ловли промокодов в BFG"""
 strings = {
  "name": "BFGDrawing",
  "prefix": "<b>Ловля промокодов:</b>"
 }

 async def client_ready(self, client, db):
  self.db = db
  self.db.set("BFGDrawing", "status", True)

 async def bfgdcmd(self, message):
  if self.db.get("BFGDrawing", "status"):
   await message.edit(self.strings["prefix"] + " <code>Отключена</code>")
   self.db.set("BFGDrawing", "status", False)
  else:
   await message.edit(self.strings["prefix"] + " <code>Включена</code")
   self.db.set("BFGDrawing", "status", True)

 async def watcher(self, message):
  if self.db.get("BFGDrawing", "status"):
   if message.chat_id == -1001524574130:
    if "Промо" in message.raw_text:
     promo = re.findall(r"#\S+", message.raw_text)
     await message.client.send_message("bforgame_bot", f"Промо {promo[0]}")