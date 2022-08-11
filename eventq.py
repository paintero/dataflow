import logging
# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)

class Event_Message:
    def __init__(self, app_object, topic, api_callback):
        self.event_message = {
            "id": "",
            "app_author": app_object,
            "topic": topic,
            "api_callback": api_callback
        }

    def set_id(self, id):
        self.event_message['id'] = id
    
    def message(self):
        return str(self.event_message)

    
class EventQ:
    def __init__(self):
        self.eventq = []
        self.subcribers = []
        self.latest_id = 0

    def append(self, message):
        self.latest_id += 1
        message.set_id(self.latest_id)
        self.eventq.append(message)
        logging.debug("Event message added to eventQ: " + message.message())
        # self.notify_subscribers()

    def register_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def notify_subscribers(self):
        for s in subscribers:
            s.update(message)

    def print_eventq(self):
        print("Printing event queue:")
        for m in self.eventq:
            print(m.message())

