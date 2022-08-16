import logging
# this will ensure that logger writes to the same file
# defined in the main module
log = logging.getLogger(__name__)

class Event_Message:
    def __init__(self, app_object, topic, api_route, params):
        
        self.id = ""
        self.app_author = app_object
        self.topic = topic
        self.api_route = api_route
        self.params = params

    def display(self):
        s = "ID: " + str(self.id) + " "
        s += " App: " + str(self.app_author.app_name)
        s += " Topic: " + str(self.topic)
        s += " API route: " + str(self.api_route)
        s += " Params: " + str(self.params)
        return s
    


class Subscriber:
    def __init__(self, app_object, app_name, topic):    
        self.app_name = app_name
        self.app_object = app_object
        self.topic = topic
    
    
    
class EventQ:
    def __init__(self):
        self.eventq = []
        self.subscriptions = []
        self.latest_id = 0

    def append(self, message):
        self.latest_id += 1
        self.id = self.latest_id
        self.eventq.append(message)
        logging.debug("Event message added to eventQ: " + message.display())
        self.notify_subscribers(message)

    def subscribe(self, subscriber):
        self.subscriptions.append(subscriber)

    # run through subscribers to the topic of this message and notify them
    def notify_subscribers(self, message):
        for s in self.subscriptions:
            if s.topic == message.topic:
                s.app_object.notify(message)

    def print_eventq(self):
        print("Printing event queue:")
        for m in self.eventq:
            m.display()

