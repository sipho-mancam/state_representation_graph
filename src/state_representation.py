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
                missed_dets.append(point.copy())
        
        print(f"Missed Detections: {len(missed_dets)}")
        self.__next_state.extend(missed_dets)
        # missed_detection = []
        # temp_next_state = []
        # cleared  = False
        # for point in self.__current_state:
        #     cleared = False
        #     idx = point.find_closest_match(self.__next_state)

        #     if idx != -1:
        #         p = self.__next_state.pop(idx)
        #         # print(p)
        #         p.marker = str(point.id)
        #         temp_next_state.append(p)
        #         cleared = True
            
        #     if not cleared:
        #         p = point.copy()
        #         # p.marker = "X"
        #         # p.id = -2
        #         # p.x *= 0.95   
        #         p.set_color((0, 0, 0))
        #         # print(point.x, point.y, point.id)
        #         missed_detection.append(p)

        # # Return all the found points that had matches
        # self.__next_state.extend(temp_next_state)
        
        # print(f"Currently Found Missed Detections: {len(missed_detection)}")
        # #Append all the missed points
        # self.__next_state.extend(missed_detection)
            
                    

