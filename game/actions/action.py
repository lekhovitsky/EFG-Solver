import abc


class Action(abc.ABC):
    value: int

    @abc.abstractmethod
    def __str__(self):
        pass
