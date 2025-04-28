class Event:
    def __init__(self):
        self.__subscribers = []

    def subscribe(self, subscriber):
        self.__subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.__subscribers.remove(subscriber)

    def fire(self, *args, **kargs):
        for subscriber in self.__subscribers():
            subscriber(*args, **kargs)