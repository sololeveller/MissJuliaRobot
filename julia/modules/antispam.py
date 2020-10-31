import time
from julia.events import register
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import (EditChatDefaultBannedRightsRequest,
                                            UpdatePinnedMessageRequest)
from telethon.tl.types import (ChannelParticipantsAdmins, ChatAdminRights,
                               ChatBannedRights, MessageEntityMentionName,
                               MessageMediaPhoto)


def max_seconds(max_seconds, *, interval=1):
    interval = int(interval)
    start_time = time.time()
    end_time = start_time + max_seconds
    yield 0
    while time.time() < end_time:
        if interval > 0:
            next_time = start_time
            while next_time < time.time():
                next_time += interval
            time.sleep(int(round(next_time - time.time())))
        yield int(round(time.time() - start_time))
        if int(round(time.time() + interval)) > int(round(end_time)): 
            return

from pymongo import MongoClient
from julia import MONGO_DB_URI, tbot
from julia.events import register
from telethon import types
from telethon.tl import functions

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["leccher"]
leechers = db.leecher

@register(pattern="")      
async def (event):
  if event.fwd_from:
    return  
  if event.is_private:  	
   return
  sender = await event.from_id()
  let = sender.username
  USERSPAM = []
  check = sender 
  if len(USERSPAM) >= 1:
       if event.from_id == USERSPAM[0]:
           pass
       else:
           USERSPAM = []
           USERSPAM.append(check) # lock the user id
  else:     
       USERSPAM.append(check) # lock the user id
  for sec in max_seconds(5):
   if len(event) > 5 and event.from_id == USERSPAM[0]:
      VALID = True
      if sender.username == None:
           st = sender.first_name
           hh = sender.id
           final = f"[{st}](tg://user?id={hh}) you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !"
      else:
           final = f'@{let} you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !'
   else:
     VALID = False
   if VALID == True:  
     users = leechers.find({})
     for c in users:
       if event.from_id == c["id"]:
          return  
       dev = await event.respond(final)                 
       leechers.insert_one({"id": event.from_id, "time": timerr})
       try:
          MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
          await event.client(EditBannedRequest(event.chat_id, event.from_id, MUTE_RIGHTS))
          await dev.edit("\nYou are now muted !")
       except Exception:
           pass
