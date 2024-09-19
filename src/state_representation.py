import numpy as np


class Point:
    MINIMUM_PROXIMITY_DISTANCE = 2 #0.00015
    def __init__(self, x, y, id, data={}, **kwargs) -> None:
        self.__x = x
        self.__y = y
        self.__id = id
        self.__data = data
        self.__distance_v = 0

    @property
    def distance(self)->float:
        return self.__distance_v
    
    @property
    def x(self)->float:
        return self.__x
    
    @property
    def y(self)->float:
        return self.__y
    
    @property
    def id(self)->int:
        return int(self.__id)

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
    
    def __distance(self, x, y)->float:
        return np.sqrt(np.pow(self.__x - x, 2) + np.pow(self.__y - y, 2))
    


point1 = Point(9, 0, 2)
point2 = Point(9, 0, 3)

print(point1 == point2)

