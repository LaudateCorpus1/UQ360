
import json
import os
import pickle

from uq360.base import Base

'''
Base class for calibrators for binary classification problems. 
Calibrators produce monotonic shifts in model confidences which preserve the order of confidence scores. 
Given as input the confidence score for class "1" in a binary classification problem, they transform
this score into an estimated probability that class "1" was a correct prediction. 
'''

class Calibrator(Base):
    def __init__(self):
        self._object_registry = {}
        self.fit_status = False
    
    def fit(self):
        raise NotImplementedError("fit method should be implemented by the calibrator")
    
    def predict(self):
        raise NotImplementedError("transform method should be implemented by the calibrator")
        
    @classmethod
    def instance(cls, subtype_name=None, **params):
        subtype_name = subtype_name
        return super(Calibrator, cls).instance(subtype_name, **params)


    @property
    def pkl_registry(self):
        pkl_list = []
        pkl_names = []
        for obj in self._object_registry.keys():
            if self._object_registry[obj]['type'] == 'pkl':
                pkl_list.append(self._object_registry[obj]['object'])
                pkl_names.append(obj)
        return pkl_list, pkl_names


    def register_pkl_object(self, obj, name):
        self._object_registry[name] = {'object': obj, 'type': 'pkl'}

    @property
    def json_registry(self):
        json_list = []
        json_names = []
        for obj in self._object_registry.keys():
            if self._object_registry[obj]['type'] == 'json':
                json_list.append(self._object_registry[obj]['object'])
                json_names.append(obj)
        return json_list, json_names

    def register_json_object(self, obj, name):
        self._object_registry[name] = {'object': obj, 'type': 'json'}

    def save(self, output_location=None):
        raise NotImplementedError("save method should be implemented by the calibrator")

    def _save(self, output_location):
        assert os.path.isdir(output_location)
        if not self.fit_status:
            raise Exception("CANNOT SAVE CALIBRATOR BEFORE CALLING FIT. ")
        # Objects in separate registries are saved with different methods
        registers = self.pkl_registry
        for obj, name in zip(registers[0], registers[1]):
            filename = self.name() + '-' + name + '.pkl'
            with open(os.path.join(output_location, filename), 'wb') as f:
                pickle.dump(obj, f)

        registers = self.json_registry
        for obj, name in zip(registers[0], registers[1]):
            filename = self.name() + '-' + name + '.json'
            with open(os.path.join(output_location, filename), 'w') as f:
                json.dump(obj, f)

    def load(self, input_location=None):
        raise NotImplementedError("load method should be implemented by the calibrator")

    def _load(self, input_location):
        assert os.path.isdir(input_location)
        archived_files = []
        for r, _, f in os.walk(input_location):
            for item in f:
                if item.startswith(self.name()):
                    archived_files.append(os.path.join(r, item))

        for obj_file in archived_files:
            if obj_file.endswith('.pkl'):
                with open(obj_file, 'rb') as f:
                    obj = pickle.load(f)
                tail = os.path.split(obj_file)[1]
                name = tail.replace('.pkl','').replace(self.name()+'-','')
                self.register_pkl_object(obj, name)
            elif obj_file.endswith('.json'):
                with open(obj_file, 'r') as f:
                    obj = json.load(f)
                tail = os.path.split(obj_file)[1]
                name = tail.replace('.json','').replace(self.name()+'-','')
                self.register_json_object(obj, name)
