from abc import ABC, abstractmethod


class StorageBase(ABC):
    """
    Abstract base class for storage operations.

    This class defines the interface for saving and retrieving objects in a storage system.
    Subclasses must implement the following methods:

    Methods
    -------
    save_object(data: any) -> None
        Save a list of dictionary objects to the storage system.

    get_object() -> any
        Retrieve data from the storage system.
    """
    @abstractmethod
    def save_object(self, data: any) -> None:
        pass

    @abstractmethod
    def get_object(self) -> any:
        pass
