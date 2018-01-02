# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 11:36:33 2017

@author: GALLICE
"""
import pandas as pd
import numpy as np
import random

class Graph:
    def __init__(self, vertices_list, edges_list):
        self.edges = edges_list
        self.vertices = vertices_list
        self.nb_nodes = len(vertices_list)
        self.nb_edges = len(edges_list)
        
        self.adjacency_matrix = self.create_adjacency_matrix(vertices_list, edges_list)

    
    def create_adjacency_matrix(self, vertices_list, edges_list):
        nb_nodes = len(vertices_list)
        nb_edges = len(edges_list)
        adj_matrix= np.array([[np.inf]*nb_nodes]*nb_nodes)
        for i in range(nb_edges):
            this_node = edges_list[i]
            adj_matrix[this_node[0], this_node[1]] = this_node[2]
            
        return adj_matrix    
    
    def is_strongly_connected(self):
        i = 0
        for node in self.vertices:
            connected_nodes = self.depth_transervsal_search(start_node = node)
            if i == 0:
                reference_set = set(connected_nodes)
            if i>0:
                if set(connected_nodes) != reference_set:
                    return False
        return True
    
    #TODO
    def contains_cycles(self):
        for i in range(self.nb_nodes):
            start_node = random.choice(self.vertices)
            visited = [start_node]
            cycle = False
            for j in range(self.nb_nodes):
                 cycle = self.look_for_cycle(start_node, visited, cycle)  
                 if cycle == True:
                     return True
        return False
    
    def look_for_cycle(self, node, visited, cycle):
        candidates_nodes = np.where(self.adjacency_matrix[node, :] != np.inf)[0].tolist()
              
        for next_node in candidates_nodes:
            if next_node in visited:
                cycle = True
            else:
                visited.append(next_node)
                self.look_for_cycle(next_node, visited, cycle)
                
        return cycle
    
    def in_out_degrees(self, node):
        node_in_degree = self.nb_nodes - np.sum(np.isinf(self.adjacency_matrix[:,node]))
        node_out_degree = self.nb_nodes - np.sum(np.isinf(self.adjacency_matrix[node,:]))

        return [node_in_degree, node_out_degree]
    
    #TODO
    def first_transversal_search(self):
        stuff = []
        
        return stuff

    def depth_transervsal_search(self, start_node, stack = [], visited = []): 
        visited.append(start_node)
        node = self.adjacency_matrix[start_node,:]
        
        candidates_nodes = np.where(node != np.inf)[0].tolist() #get edges
        
        for i in range(len(candidates_nodes)):
            if candidates_nodes[i] not in visited:
                self.depth_transervsal_search(start_node = candidates_nodes[i], stack = stack,visited = visited)

        return visited
        
        
    def do_bfs_traversal(self):
    
        visited = []
        queue = []
    
        # push first vertex
        queue.append(self.vertices[0])
    
        while len(queue) != 0:
    
            vertex = queue[0]
            # add to visited
            visited.append(int(vertex))
            # remove first entry of queue
            queue.pop(0)
    
            for i in range(0, self.nb_nodes):
    
                # check if adjacent (weigth not inf)
                edge_weight = self.adjacency_matrix[int(vertex), i]
    
                if edge_weight != np.inf and i not in visited:
                    if i not in queue:
                        queue.append(i)
    
        return visited
    
    #TODO
    def is_bipartite(self):
        stuff = []
        
        return stuff
        
    #TODO
    def topological_sort(self):
        sort = []
        
        return sort
    
    def mst_prim(self):
        prim_table = pd.DataFrame(columns = ['vertices', 'visited', 'weight', 'parent'])
        
        for i in range(self.nb_nodes):
            prim_table.loc[i] = [self.vertices[i], False, np.inf, 0]
            
        
        mst = []
        while prim_table.visited.all() != True:
            visiting_node = random.choice(prim_table.vertices)  
            prim_table.set_value(visiting_node, 'visited', True)
            mst.append(visiting_node)
            
            
            prim_table.set_value(visiting_node, 1, True)
            node = self.adjacency_matrix[visiting_node,:]
            
            neighbours_nodes = np.where(node != np.inf)[0].tolist()
            for j in range(len(neighbours_nodes)):
                neighbour_weight = node[neighbours_nodes[j]]
                if neighbour_weight < prim_table.weight[neighbours_nodes[j]]:
                    prim_table.set_value(neighbours_nodes[j], 'weight', neighbour_weight)
            
            
            #TROUVER COMMENT INVERSER LES VALEURS BOOLEENNES DE prim_table POUR ENSUITE UTILISER CETTE ARRAY DE BOOL POUR SELECTIONNER LES BONS NOEUDS DANS pirm_table
            nodes_of_choice = prim_table['visited']
            random.choice(prim_table.loc[nodes_of_choice])
            
        return mst

    def find_simple_path(self, node_source, node_dest, visited = [], path = [], path_found = False):
        nodes = self.adjacency_matrix[node_source,:]
        next_nodes = np.where(nodes != np.inf)[0]
        for i in range(len(next_nodes)):
            node_source = next_nodes[i]
            if node_source not in visited:
                if path_found == False:
                    visited.append(node_source)
                    if node_source == node_dest:
                        path_found = True
                        path.append(node_source)
                    else:
                        if node_source == visited[0]:
                            break
                        visited.append(node_source)
                        self.find_simple_path(self,
                                        node_source = node_source,
                                        node_dest = node_dest,
                                        visited = visited,
                                        path_found = path_found)
                        if path_found == True:
                            path.append(node_source)
                            
        return path
            
            
            
        

#    def max_flow_Ford_Fulkerson(self, node_source, node_dest):
#        residual_graph = self.adjacency_matrix
#        path = self.find_simple_path(node_source,node_dest)
        
            
        

            
    
    
#user inputs
#vertices_list = []
#edges_list = []
#
#while True:
#    try:
#        vertex = int(input("enter a new vertex, press q when finished\n"))
#        vertices_list.append(vertex)
#    except:
#        break
#
#
#while True:
#    try:
#        source_edge = int(input("enter the source edge, q to quit\n"))
#    except:
#        break
#    dest_edge = int(input("enter the dest edge\n"))
#    weight = 1
#    
#    edges_list.append([source_edge, dest_edge, weight])

#Test graph
vertices_list = [0,1,2,3,4,5]
edges_list = [[0,1,1],[1,2,1],[2,3,1],[3,0,1], [1,5,1],[5,3,1],[4,0,1],[4,3,1]]

graph = Graph(vertices_list, edges_list)
print(graph.find_simple_path(node_source = 1,node_dest = 3))
#
#while True:
#    print("\n--------------------------------")
#    print("1 -> check if strongly connected")
#    print("2 -> check if contains cycle")
#    print("3 -> check in-degrees of a node")
#    print("4 -> check out-degrees of a node")
#    print("5 -> print the adjacency matrix")
#    print("q -> quit")
#    print("--------------------------------\n")
#    
#    choice = input("choose a function\n")
#    
#    if choice =="1":
#        answer = graph.is_strongly_connected()
#        if answer == True:
#            print("strongly connected\n")
#        else:
#            print("weakly connected\n")
#    elif choice == "2":
#        answer = graph.contains_cycle()
#        if answer == True:
#            print("at least one cycle exists\n")
#        else:
#            print("no cycle exists\n")
#    elif choice =="3":
#        node = int(input("enter the id of a vertex\n"))
#        if node not in graph.vertices:
#            print("this vertex doesn't exist\n")
#        else:
#            answer = graph.in_degrees(node)
#            print('in degrees:')
#            print(answer[0])
#            print('out_degrees:')
#            print(answer[1])
#    elif choice =="5":
#        print(graph.adjacency_matrix)
#    elif choice == "q":
#        break
