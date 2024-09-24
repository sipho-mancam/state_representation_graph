import pprint
import numpy as np
import json
import time
from dataloader import Point

# class Point:
#     def __init__(self, x:float, y:float, typ:str, radius:int,  color:tuple=(255, 0, 0), id=0)->None:
#         self.__x = x
#         self.__y = y
#         self.__color = color
#         self.__type = typ
#         self.__radii = radius
#         self.__id = id
#         self.__extras = {}

#     @property
#     def extras(self)->dict:
#         return self.__extras
    
#     @extras.setter
#     def extras(self, kv:tuple)->None:
#         self.__extras[kv[0]] = kv[1]

#     @property
#     def id(self)->int:
#         return self.__id
    
#     @id.setter
#     def id(self, id)->None:
#         self.__id = id

#     @property
#     def x(self)->float:
#         return self.__x
    
#     @x.setter
#     def x(self, x)->float:
#         if 0 <= x <= 1:
#             self.__x = x

#     @property
#     def y(self)->float:
#         return self.__y
    
#     @y.setter
#     def y(self, y)->None:
#         if 0 <= y <= 1:
#             self.__y  = y

#     @property
#     def marker(self)->str:
#         return str(self.__type)
    
#     @marker.setter
#     def marker(self, marker)->None:
#         self.__type = marker
        
    
#     @property
#     def color(self)->tuple:
#         return self.__color
    
#     @color.setter
#     def color(self, color:tuple)->None:
#         if type(color) is tuple:
#             self.__color = color

#     @property
#     def radius(self)->int:
#         return self.__radii
    
#     @radius.setter
#     def radius(self, r:int)->None:
#         self.__radii = r
    
# import pprint
class ProximityCalculator:
    def __init__(self, x_list:list, o_list:list)->None:
        self.__x_list = x_list
        self.__o_list = o_list
        self.__selected_vertices = []
        self.__selected_indices = []

        self.__graph = [
            # {'id':'X', 'edges':{'1':0.3,  '3':0.5,  '2':0.55, '4':0.7}},
            # {'id':'Y', 'edges':{'2':0.20, '3':0.25, '1':0.56, '4':0.8}},
            # {'id':'Z', 'edges':{'4':0.02, '2':0.15, '3':0.2,  '1':0.7}},
            # {'id':'A', 'edges':{'4':0.01, '2':0.16, '3':0.25, '1':0.8}}
        ]

    
    def __associate_points(self)->None:
        # Associates nodes from state 1 to nodes on state 2
        for node in self.__graph:
            id = node.get('id')
            for point in self.__x_list:
                if point.id == id:
                    point.extras = ('vertex', node.get('vertex'))
                    point.extras = ('distance', node.get('edges', {}).get(node.get('vertex')))
                    # print(point.extras)
                    break
        
        for point in self.__x_list:
            extras = point.extras
            id = extras.get('vertex')
            if extras.get('distance') is not None and extras.get('distance') > Point.MINIMUM_PROXIMITY_DISTANCE:
                continue
            if id is not None:
                for o_point in self.__o_list:
                    if o_point.id == id:
                        o_point.marker = str(point.id)
                        point.extras = ('found_det', o_point.extras['det'])
                        # print(point.extras)
                        break

    def get_associated_points(self)->tuple:
        return self.__x_list, self.__o_list
    

    def __build_point_vector(self, point:Point, size)->np.ndarray:
        return np.array([
                                [point.x for _ in range(size)],
                                [point.y for _ in range(size)]
                            ], dtype=np.float64)

    def __build_o_vector(self, o_list=None)->np.ndarray:
        if o_list is None:
            return np.array([[point.x for point in self.__o_list],
                             [point.y for point in self.__o_list]],
                               dtype=np.float64)
        return np.array([
                            [point.x for point in o_list],
                            [point.y for point in o_list]
                        ], dtype=np.float64)

    def write_to_json(self)->None:
        path = "debug.json"
        with open(path, 'w') as fp:
            json.dump(self.__graph, fp)
        
    
    def test(self)->None:
        start_time = time.time()
        self.build_distances_graph()
        self.run()
        self.__associate_points()
        end_time = time.time()
        self.write_to_json()
        proc_time = round((end_time - start_time)*1000, 2)
        print(f"Testing Time ProximityCalculation is: {proc_time} ms")

    def compute(self)->None:
        self.build_distances_graph()
        self.run()
        self.__associate_points()
        self.write_to_json()
      

    def __calculate_distances(self, point)->np.ndarray:
        xy_vector = self.__build_point_vector(point, len(self.__o_list))
        xy_o_list = self.__build_o_vector()
        return np.sqrt(np.power(xy_vector[0]-xy_o_list[0], 2)+np.power(xy_vector[1]-xy_o_list[1], 2))


    def build_distances_graph(self)->None:
        # This method needs to construct a similar graph to the one at the top
        # From a list of nodes and a list of vertices
        # Vertices in this context will mean the O points
        # and Nodes will refer to the X points        
        for x_point in self.__x_list:
            node = {'id':x_point.id, 'edges':{}}
            edges = {}
            point_distances = self.__calculate_distances(x_point) # n^2
            for idx, edget_distance in enumerate(point_distances):
               o_point = self.__o_list[idx]
               edges[o_point.id] = float(edget_distance)

            intem = sorted(edges.items(), key=lambda kv : kv[1])
            edges = dict(intem)
            node['edges'] = edges
            self.__graph.append(node)
        
    
    def __build_stack(self, vertex, dist,  current_index)->list:
        res = [(dist, current_index)]
        for idx, elem in enumerate(self.__graph):
            if not elem.get('selected'):
                d2 = elem['edges'][vertex]
                if d2 < dist:
                    res.append((d2, idx))  
        return sorted(res, key=lambda a : a[0])
    
    def __proximity_calculator(self, index, ck=0, lkt={})->list[tuple]: # this returns a tuple of (ID, Vertex) of all assigned IDs
        if index >= len(self.__graph):
            return []

        current_node = self.__graph[index]
        current_key = ck
        keys = list(current_node['edges'].keys())
        lookup = lkt

        if ck >= len(keys):
            return []
        
        # Try and find an unused key to start from
        vertex = keys[current_key]
        while True:
            if lookup.get(vertex) is not None: # The Vertex has been used
                current_key += 1
                if current_key >= len(keys):
                    return []
            else:
                vertex = keys[current_key]
                break     
            vertex = keys[current_key]

        dist = current_node['edges'][keys[current_key]]
        stack = self.__build_stack(vertex, dist, index)

        # Check, if I'm at the top of the stack, cause, if that's the case then I'm the closest
        if stack[0][1] == index:
            self.__graph[index]['selected'] = True
            lookup[vertex] = True
            return [(index, vertex)]
        
        # At this point we are doubting that I'm the closest, we want to know if I'm the best candidate
        dist , ind = stack[0]
        res = self.__proximity_calculator(ind, lkt=lookup)
        if  lookup.get(vertex):
            r1 =  self.__proximity_calculator(index, current_key+1, lookup)
            res.extend(r1)
            return res
        else:
            self.__graph[index]['selected'] = True
            res.append((index, vertex))
            lookup[vertex]=True
            return res
          
    def run(self)->None:
        current_index = 0
        lookup = {}
        while current_index < len(self.__graph):
            results = self.__proximity_calculator(current_index, 0, lookup)
            for res in results:
                index, vertex = res
                self.__selected_indices.append(index)
                self.__selected_vertices.append(vertex)
                self.__graph[index]['vertex'] = vertex
            
            current_index += 1
            while current_index in self.__selected_indices:
                current_index += 1



if __name__ == "__main__":        
    res = ProximityCalculator(None, None)
    res.run()