class Event_Message:
    def __init__(self, app_object, topic, api_callback):
        self.event_message = {
            "id": "",
            "app_author": app_object,
            "topic": topic,
            "api_callback": api_callback
        }

    def message(self):
        return str(self.event_message)

    
class EventQ:
    def __init__(self):
        self.event_q = []
        self.subcribers = []
        self.latest_id = 0

    def append(self, message):
        self.latest_id += 1
        message["id"] = self.latest_id
        self.event_q.append(message)
        print(self.event_q)
        # self.notify_subscribers()

    def register_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def notify_subscribers(self):
        for s in subscribers:
            s.update(message)

