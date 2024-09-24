import json
import os
from pathlib import Path
import numpy as np
import math

class Point:
    MINIMUM_PROXIMITY_DISTANCE = 0.025
    def __init__(self, x, y, id, data={}, col=(255, 0, 0),  **kwargs) -> None:
        self.__x = x
        self.__y = y
        self.__id = id
        self.__data = data
        self.__distance_v = 0
        self.__color = col
        self.__radius = 10
        self.__marker = "-1"
        self.__extras = {}
        self.__extras['det'] = self.__data

    @property
    def extras(self)->dict:
        return self.__extras
    
    @extras.setter
    def extras(self, kv:tuple)->None:
        self.__extras[kv[0]] = kv[1]

    @property
    def marker(self)->str:
        return self.__marker
    
    @marker.setter
    def marker(self, mark)->None:
        self.__marker = mark

    def copy(self):
        p = Point(self.__x, self.__y, self.__id, self.__data, self.__color)
        p.marker = self.__marker
        return  p

    @property
    def radius(self)->float:
        return self.__radius
    
    @property
    def color(self)->tuple:
        return self.__color

    @property
    def distance(self)->float:
        return self.__distance_v
    
    @property
    def x(self)->float:
        return self.__x

    @x.setter
    def x(self, d)->None:
        self.__x = d
    
    @property
    def y(self)->float:
        return self.__y
    
    @property
    def id(self)->int:
        return int(self.__id)
    
    @id.setter
    def id(self, id)->None:
        self.__id = id

    @property
    def data(self)->dict:
        return self.__data
    
    def __eq__(self, value: object) -> bool:
        # compute the euclidean distance for the object and return true if it lies within the proximity.
        x  = value.__x
        y = value.__y 
        self.__distance_v = self.__distance(x, y)
        if self.__distance_v <= Point.MINIMUM_PROXIMITY_DISTANCE:
            return True
        return False
    
    def find_closest_match(self, points:list)->int:
        # go through all the points in the list and search for a minimum
        MINIMUM_DISTANCE = math.inf
        current_index = -1
        for idx, point in enumerate(points):
            if self == point:
                dist = self.__distance_v
                if dist < MINIMUM_DISTANCE:
                    current_index = idx
                    MINIMUM_DISTANCE = dist

        return current_index

    
    def __distance(self, x, y)->float:
        return np.sqrt(np.pow(self.__x - x, 2) + np.pow(self.__y - y, 2))
    
    def set_color(self, col)->None:
        self.__color = col

    def get_distance(self)->float:
        return self.__distance_v


class JSONDirectoryReader:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        self.current_index = 0

    def next(self):
        if self.current_index >= len(self.files):
            self.current_index  = 0
            # raise StopIteration("No more files in the directory.")
        
        file_path = os.path.join(self.directory_path, self.files[self.current_index])
        self.current_index += 1
        
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        points = []
        for idx, track in enumerate(data.get('tracks', [])):
            coordinates = track['coordinates']
            tracking_id = track['tracking-id']
            points.append(Point(coordinates[0], coordinates[1], idx, track))
        
        return points

class DataLoader:
    def __init__(self, path=None):
        self.__data_path = path