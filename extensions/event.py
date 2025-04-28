import inspect
import asyncio

class Event:
    def __init__(self):
        self.__subscribers = []

    def subscribe(self, subscriber):
        self.__subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.__subscribers.remove(subscriber)

    async def fire_async(self, *args, **kargs):
        for sub in self.__subscribers:
            signature = inspect.signature(sub)
             
            if inspect.iscoroutinefunction(sub):
                if len(signature.parameters) == 0:
                    await sub()
                    continue
                await sub(*args, **kargs)
            else:
                if len(signature.parameters) == 0:
                    sub()
                    continue
                sub(*args, **kargs)

    def fire(self, *args, **kargs):
        for sub in self.__subscribers:
            signature = inspect.signature(sub)
             
            if len(signature.parameters) == 0:
                sub()
            else:
                sub(*args, **kargs)
