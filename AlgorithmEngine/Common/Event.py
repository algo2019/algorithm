
class Event(object):
    def __init__(self):
        self.__handlers = []
        self.__toSubscribe = []
        self.__toUnsubscribe = []
        self.__emitting = False

    def __applyChanges(self):
        if len(self.__toSubscribe):
            for handler in self.__toSubscribe:
                if handler not in self.__handlers:
                    self.__handlers.append(handler)
            self.__toSubscribe = []

        if len(self.__toUnsubscribe):
            for handler in self.__toUnsubscribe:
                self.__handlers.remove(handler)
            self.__toUnsubscribe = []

    def subscribe(self, handler):
        if self.__emitting:
            self.__toSubscribe.append(handler)
        elif handler not in self.__handlers:
            self.__handlers.append(handler)

    def unsubscribe(self, handler):
        if self.__emitting:
            self.__toUnsubscribe.append(handler)
        else:
            self.__handlers.remove(handler)

    def emit(self, *args, **kwargs):
        try:
            self.__emitting = True
            for handler in self.__handlers:
                handler(*args, **kwargs)
        finally:
            self.__emitting = False
            self.__applyChanges()


class MarkEvent(object):
    mark_name = 'event_mark'

    def __init__(self):
        self.__marks = {None: Event()}
        self.__null_event = Event()

    def subscribe(self, handler, mark=None):
        if self.__marks.get(mark) is None:
            self.__marks[mark] = Event()
        return self.__marks[mark].subscribe(handler)

    def unsubscribe(self, handler, mark=None):
        return self.__marks[mark].unsubscribe(handler)

    def emit(self, *args, **kwargs):
        mark = kwargs.get(self.mark_name)
        if len(args) > 0:
            mark = mark or getattr(args[0], self.mark_name, None)
        kwargs.pop(self.mark_name, None)
        self.__marks.get(mark, self.__null_event).emit(*args, **kwargs)
