import json
import numpy as np
from typing import Dict

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
        
        
class SectionsHandler:
    def __init__(self, dict_sections: Dict[str, Dict[str, any]]= None)->None:
        
        self.data = {}
        if dict_sections:
            self.data.update(dict_sections)
    
    def add_section(self, section_name, dict_fields: Dict[str, any]):
        self.data.update({section_name: dict_fields})
    
    def save(self, path:str,filename:str)-> bool:
        path_name = f'{path}/{filename}.json'
        stored_data = self._open2write(path_name)

        #update te sections
        stored_data.update(self.data)
        was_stored = False
        
        with open(path_name, 'w') as file:
            json.dump(stored_data, file, cls= NumpyEncoder)
        
        was_stored = True

        return was_stored
    
    def _open2write(self, path_name: str) :
        try: # check if the file exist and load the sections stored to overwrite the section and not the file
            with open(path_name, 'r') as file:
                stored_data = json.load(file)
        except:
            stored_data = {} # there is no problem if no find the file
        return stored_data
    
    def open(self, path: str, filename: str) -> Dict[str, Dict[str, any]]:
        path_name = f'{path}/{filename}.json'
        with open(path_name, 'r') as file:
            stored_data = json.load(file)
        
        for section_name, dict_section in stored_data.items():
            for field_name, data in dict_section.items():
                if isinstance(data, list):
                    data = np.asanyarray(data)
                dict_section[field_name] = data
            self.data.update({section_name:dict_section})
        return self.data