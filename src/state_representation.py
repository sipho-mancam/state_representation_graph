import numpy as np
from dataloader import Point, JSONDirectoryReader
from proximity_calculator import ProximityCalculator

class State:
    """
    1. A state object is an object with a collection of points
    2. It manages the objects and exposes points, while also exposing an indexing method for the points
    """
    def __init__(self) -> None:
        self.__current_state = []
        self.__data_dir = r"C:\Users\sipho-mancam\Documents\Programming\python\state_representation_graph\src\tracking_data_files"
        self.__data_loader = JSONDirectoryReader(self.__data_dir)
        self.__next_state = self.__data_loader.next()

    def get_next_state(self)->tuple[list[Point], list[Point]]:
        self.__current_state = self.__next_state
        for point in self.__current_state:
            point.extras.clear()
            point.extras = ('det', point.data)

        self.__next_state = self.__data_loader.next()
        print(f"Before Match:\nPrevious State Count: {len(self.__current_state)}  Next State Count: {len(self.__next_state)}")
        # if len(self.__current_state) > len(self.__next_state):
        self.__match_states()
        print(f"After Match:\nPrevious State Count: {len(self.__current_state)}  Next State Count: {len(self.__next_state)}")
        return self.__current_state, self.__next_state
    

    def __match_states(self)->None:
        """
        1. Take State 0 and Compare it with State 1
        2. Find the holes in state one from all the points that didn't match state 0
        3. Update State 1 with the left over points from State 0
        """
        prox_calc = ProximityCalculator(self.__current_state, self.__next_state)
        prox_calc.compute()
        # X list -- > O list
        self.__current_state, self.__next_state = prox_calc.get_associated_points()

        missed_dets = []
        for point in self.__current_state:
            if 'found_det' not in point.extras:
                p = point.copy()
                missed_dets.append(p)
        
        print(f"Missed Detections: {len(missed_dets)}")
        for p in missed_dets:
            print(p.id)
        self.__next_state.extend(missed_dets)            

