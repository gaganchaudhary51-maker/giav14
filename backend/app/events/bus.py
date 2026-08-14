from collections import deque
from threading import Lock
from app.events.store import event_store

class EventBus:
    def __init__(self, limit=500):
        self._events=deque(maxlen=limit); self._lock=Lock()
    def publish(self,event_type,payload):
        event={"type":event_type,"payload":payload}
        with self._lock: self._events.append(event)
        event_store.publish(event_type,payload)
        return event
    def recent(self,limit=50):
        with self._lock: return list(self._events)[-min(max(limit,1),200):]
event_bus=EventBus()
