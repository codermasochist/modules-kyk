from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import loader, utils
from datetime import datetime


def register(cb):
 cb(KykPingerMod())


class KykPingerMod(loader.Module):
 """Классический пинг"""

 strings = {'name': 'PingKyK'}

 def init(self):
  self.name = self.strings['name']
  self._me = None
  self._ratelimit = []

 async def client_ready(self, client, db):
  self._db = db
  self._client = client
  self.me = await client.get_me()

 async def pinkcmd(self, message):
  """Узнать свой пинг"""
  a = 10
  r = utils.get_args(message)
  if r and r[0].isdigit():
   a = int(r[0])
  ping_msg = []
  ping_data = []
  for _ in range(a):
   start = datetime.now()
   msg = await message.client.send_message("me", "ping")
   end = datetime.now()
   duration = (end - start).microseconds / 1000
   ping_data.append(duration)
   ping_msg.append(msg)
  ping = sum(ping_data) / len(ping_data)
  await message.edit(f"[<3] {str(ping)[0:10]}наносекунд")
  for i in ping_msg:
   await i.delete()