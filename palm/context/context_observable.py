

class ContextObservable:

    def __init__(self):
        self.observers = dict()

    def add_observer(self, observer_id, observer_callable):
        self.observers[observer_id] = observer_callable

    def remove_observer(self, observer_id):
        del self.observers[observer_id]

    def notify_observers(self):
        for key in self.observers.keys():
            self.observers[key]()
