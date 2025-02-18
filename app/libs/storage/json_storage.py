import os
import json

from app.libs.storage.base import StorageBase

class JsonStorage(StorageBase):
    """
        A class to handle storage of data in JSON format.

        Attributes:
            file_path (str): The path to the JSON file where data will be stored.

        Methods:
            save_object(data: any) -> any:
                Saves the given data object to the JSON file.

            get_object() -> any:
                Retrieves and returns the data object from the JSON file. 
                Returns an empty list if the file does not exist.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path

    def save_object(self, data: any) -> any:
        """
        Fetches the existing object and updates in db if proce is changed
        Else appends the new one in db
        param: data: data to be stored in db
        """
        new_objects_maps = {row['product_title']: row for row in data}
        data = self.get_object()

        # check if price need to be updated for existing data
        for obj in data:
            if obj['product_title'] in new_objects_maps:
                obj['product_price'] = new_objects_maps[obj['product_title']]['product_price']
                del new_objects_maps[obj['product_title']]

        # add new items
        data.extend(list(new_objects_maps.values()))
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return new_objects_maps

    def get_object(self) -> any:
        """
        Returns the db object data
        """
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, 'r') as f:
            return json.load(f)
