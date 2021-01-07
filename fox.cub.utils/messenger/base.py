from abc import ABCMeta, abstractmethod

class BaseMessenger(metaclass=ABCMeta):

    @abstractmethod
    def send_message(self, message):
        raise NotImplementedError

