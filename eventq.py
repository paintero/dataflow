import logging
# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)

class Event_Message:
    def __init__(self, app_object, topic, api_route, params):
        self.event_message = {
            "id": "",
            "app_author": app_object,
            "topic": topic,
            "api_route": api_route,
            "params": params
        }

    def set_id(self, id):
        self.event_message['id'] = id
    
    def message(self):
        return str(self.event_message)

    def app_author(self):
        return self.event_message['app_author']

    def topic(self):
        return self.event_message['topic']

    def api_route(self):
        return self.event_message['api_route']

    def params(self):
        return self.event_message['params']


class Subscriber:
    def __init__(self, app_object, app_name, topic):
        self.subscriber = {
            "app_name": app_name,
            "app_object": app_object,
            "topic": topic
        }

    def string(self):
        return str(self.subscriber)

    def app_object(self):
        return self.subscriber['app_object']
    
    
class EventQ:
    def __init__(self):
        self.eventq = []
        self.subscriptions = []
        self.latest_id = 0

    def append(self, message):
        self.latest_id += 1
        message.set_id(self.latest_id)
        self.eventq.append(message)
        logging.debug("Event message added to eventQ: " + message.message())
        self.notify_subscribers(message)

    def subscribe(self, subscriber):
        self.subscriptions.append(subscriber)

    # run through subscribers to the topic of this message and notify them
    def notify_subscribers(self, message):
        for s in self.subscriptions:
            if s.subscriber['topic'] == message.event_message['topic']:
                s.subscriber['app_object'].notify(message)

    def print_eventq(self):
        print("Printing event queue:")
        for m in self.eventq:
            print(m.message())

