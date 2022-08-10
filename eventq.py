class Event_Message:
    def __init__(self):
        self.message = {
            "id": "",
            "app_author": "",
            "callback_api": ""
        }

    
class EventQ:
    def __init__(self):
        self.event_q = []
        self.latest_id = 0

    def append(self, message):
        message["id"] = self.latest_id + 1
        self.event_q.append(message)

