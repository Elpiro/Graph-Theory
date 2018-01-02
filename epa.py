# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys

def read_inp(inp_path):
    junctions = []
    pipes = []
    valves = []
    reservoirs = []
    pumps = []
    with open(inp_path, 'r') as network:
        datas = network.read()
        datas = datas.split('\n')
        for line in range(len(datas)):
            if datas[line] == '[JUNCTIONS]':
                line = line + 2
                i = 0
                while datas[line]:
                    temp_data = datas[line].replace(' ', '').split('\t')
                    del temp_data[-1]
                    temp_data.insert(0, i)
                    junctions.append(temp_data)
                    i += 1
                    line += 1
            elif datas[line] == '[RESERVOIRS]':
                line = line+2
                while datas[line]:
                    temp_data = datas[line].replace(' ', '').split('\t')
                    del temp_data[-1]
                    temp_data.insert(0,i)
                    reservoirs.append(temp_data)
                    i+=1
                    line+=1
            elif datas[line] == '[PIPES]':
                line = line + 2
                i = 0
                while datas[line]:
                    temp_data = datas[line].replace(' ', '').split('\t')
                    del temp_data[-1]
                    temp_data.insert(0, i)
                    pipes.append(temp_data)
                    i += 1
                    line += 1
            elif datas[line] == '[VALVES]':
                line = line + 2
                while datas[line]:
                    temp_data = datas[line].replace(' ', '').split('\t')
                    del temp_data[-1]
                    temp_data.insert(0, i)
                    valves.append(temp_data)
                    i += 1
                    line += 1
            elif datas[line] == '[PUMPS]':
                use_pumps = input('use pumps as pipes ?(y/n)')
                if use_pumps == 'y' or use_pumps == 'yes':
                    line = line + 2
                    while datas[line]:
                        temp_data = datas[line].replace(' ', '').split('\t')
                        temp_data = temp_data[0:3]
                        temp_data.insert(0, i)
                        pumps.append(temp_data)
                        i += 1
                        line += 1

        junctions = pd.DataFrame(junctions, columns=['ID', 'Name', 'Elev', 'Demand', 'Pattern'])
        reservoirs = pd.DataFrame(reservoirs, columns = ['ID', 'Name', 'Head', 'Pattern'])
        pipes = pd.DataFrame(pipes, columns=['Edge_ID', 'Name', 'Node1', 'Node2', 'Length', 'Diameter', 'Roughness',
                                             'MinorLoss', 'Status'])
        valves = pd.DataFrame(valves, columns=['Edge_ID', 'Name', 'Node1', 'Node2', 'Diameter', 'Type', 'Settings',
                                               'MinorLoss'])
        pumps = pd.DataFrame(pumps, columns = ['Edge_ID', 'Name', 'Node1', 'Node2'])
        
        del junctions['Elev']
        del junctions['Demand']
        del junctions['Pattern']
        junctions['Reservoir'] = pd.DataFrame([False]*len(junctions))
        
        del reservoirs['Head']
        del reservoirs['Pattern']
        reservoirs['Reservoir'] = pd.DataFrame([True]*len(reservoirs))

        del pipes['Length']
        del pipes['Diameter']
        del pipes['Roughness']
        del pipes['MinorLoss']
        del pipes['Status']
        pipes['Node1_ID'] = pd.DataFrame([0] * len(pipes))
        pipes['Node2_ID'] = pd.DataFrame([0] * len(pipes))
        pipes['Valve'] = pd.DataFrame([False] * len(pipes))
        pipes['Pump'] = pd.DataFrame([False] * len(pipes))

        del valves['Diameter']
        del valves['Type']
        del valves['Settings']
        del valves['MinorLoss']
        valves['Node1_ID'] = pd.DataFrame([0] * len(valves))
        valves['Node2_ID'] = pd.DataFrame([0] * len(valves))
        valves['Valve'] = pd.DataFrame([True] * len(valves))
        valves['Pump'] = pd.DataFrame([False] * len(valves))
        
        pumps['Node1_ID'] = pd.DataFrame([0] * len(pumps))
        pumps['Node2_ID'] = pd.DataFrame([0] * len(pumps))
        pumps['Valve'] = pd.DataFrame([False] * len(pumps))
        pumps['Pump'] = pd.DataFrame([True] * len(pumps))
        
        junctions = junctions.append(reservoirs, ignore_index = True)
        
        pipes = pipes.append(valves, ignore_index = True)
        pipes = pipes.append(pumps, ignore_index = True)
    

        for j in range(len(pipes)):
            node1 = pipes.Node1[j]
            node2 = pipes.Node2[j]
            try:
                node1_ID = int(junctions[junctions.Name == node1].ID)
            except:
                node1_ID = len(junctions)
                new_node = pd.DataFrame([[node1_ID, node1, True]], columns=['ID', 'Name', 'Reservoir'])
                junctions = junctions.append(new_node, ignore_index=True)
                
            try:
                node2_ID = int(junctions[junctions.Name == node2].ID)
            except:
                node2_ID = len(junctions)
                new_node = pd.DataFrame([[node2_ID, node2, True]], columns=['ID', 'Name', 'Reservoir'])
                junctions = junctions.append(new_node, ignore_index=True)

            pipes = pipes.set_value(j, 'Node1_ID', node1_ID)
            pipes = pipes.set_value(j, 'Node2_ID', node2_ID)

        return junctions, pipes


class Graph:
    def __init__(self, junctions, pipes):
        self.edges = pipes
        self.vertices = junctions

        self.nb_edges = len(pipes)
        self.nb_nodes = len(junctions)

        self.adjacency_matrix = self.create_symetric_adjacency_matrix(self.edges)
        sys.setrecursionlimit(self.nb_nodes)

    def create_symetric_adjacency_matrix(self, edges):
        adj_matrix = np.array([[np.inf] * self.nb_nodes] * self.nb_nodes)
        for i in range(self.nb_edges):
            node1 = edges.Node1_ID[i]
            node2 = edges.Node2_ID[i]
            if edges.Valve[i] == False:
                adj_matrix[node1, node2] = 1
                adj_matrix[node2, node1] = 1
            else:
                adj_matrix[node1, node2] = 2
                adj_matrix[node2, node1] = 2

        return adj_matrix

    def find_all_valves_to_close(self, pipe_name):
        
        node_1_id = self.edges.Node1_ID[self.edges.Name == pipe_name].tolist()[0]
        node_2_id = self.edges.Node2_ID[self.edges.Name == pipe_name].tolist()[0]

        visited_pipes = []
        valves_to_close = []
        
        #look left
        valves_to_close, visited_pipes, isolated = self.find_valves_to_close_one_side(previous_pipe=pipe_name,
                                                                            node_source=node_1_id,
                                                                            visited_pipes=visited_pipes,
                                                                            valves_to_close=valves_to_close,
                                                                            isolated = True)
        #look right
        valves_to_close, visited_pipes, isolated = self.find_valves_to_close_one_side(previous_pipe=pipe_name,
                                                                            node_source=node_2_id,
                                                                            visited_pipes=visited_pipes,
                                                                            valves_to_close=valves_to_close, 
                                                                            isolated = isolated)
        visited_pipes = list(set(visited_pipes))
        return valves_to_close, visited_pipes, isolated

    def find_valves_to_close_one_side(self, previous_pipe, node_source, visited_pipes, valves_to_close, isolated):
        visited_pipes.append(previous_pipe)

        node = self.adjacency_matrix[node_source, :]
        next_nodes = np.where(node != np.inf)[0].tolist()
        
        if len(next_nodes) > 0:
            for i in range(len(next_nodes)):
                node_dest = next_nodes[i]
                if self.vertices.Reservoir[node_dest] == True:
                    isolated = False
                edge_value = self.adjacency_matrix[node_source, node_dest]

                # find the edge
                try:
                    pipes_infos = self.edges
                    pipes_infos = pipes_infos[pipes_infos.Node1_ID == node_source]
                    pipes_infos = pipes_infos[pipes_infos.Node2_ID == node_dest]
                    next_edge_name = pipes_infos.Name.tolist()[0]
                except:
                    pipes_infos = self.edges
                    pipes_infos = pipes_infos[pipes_infos.Node1_ID == node_dest]
                    pipes_infos = pipes_infos[pipes_infos.Node2_ID == node_source]
                    next_edge_name = pipes_infos.Name.tolist()[0]


                pipe_name = next_edge_name
                if (pipe_name not in visited_pipes):
                    if (pipe_name not in valves_to_close):
                        if edge_value == 1:
                            valves_to_close, visited_pipes, isolated = self.find_valves_to_close_one_side( previous_pipe=pipe_name,
                                                                                                           node_source=node_dest,
                                                                                                           visited_pipes=visited_pipes,
                                                                                                           valves_to_close=valves_to_close,
                                                                                                           isolated = isolated)
                        elif edge_value == 2:
                            valves_to_close.append(pipe_name)

        return valves_to_close, visited_pipes, isolated
    
    
''' --------------------------------Display----------------------------------- '''




while True:
    print('------------ Choose a network to study ------------')
    print(' 1 -> 1st network')
    print(' 2 -> chinese network')
    print('---------------------------------------------------')
    network_choice = input('Choice: ')
    
    if network_choice == '1':
        print('loading the network...')
        junctions, pipes = read_inp('network.inp')
        g = Graph(junctions, pipes)
        break
    elif network_choice == '2':
        print('loading the network...')
        junctions, pipes = read_inp('network_china.inp')
        g = Graph(junctions, pipes)
        break


while True:
    pipe_name = input('enter the name of a pipe: ')
    
    if pipe_name in list(pipes.Name):
        print('starting analysis')
        valves_to_close, visited_pipes, is_isolated = g.find_all_valves_to_close(pipe_name)
        print(str(len(visited_pipes))+ ' pipes in this area')
        print(str(len(valves_to_close))+ ' valves to close')
        if is_isolated == True:
            print('this area is surrounded by valves')
        else:
            print('There are tanks/reservoirs that bound this area')
            
            
        show = input('show list of valves to close ?(y/n)')
        if show == 'y':
            print(valves_to_close)
        show1 = input('show list of visited_pipes ?(y/n)')
        if show1 == 'y':
            print(visited_pipes)

            
    else:
        print('pipe not in the network')
        


    



#
#df = pd.DataFrame(columns=['pipes', 'valves'])
#pipes = pipes[['Name', 'Valve']]
#pipes = pipes[pipes.Valve == False]
#i=0
#for pipe_name in pipes.Name:
#   if (pipe_name not in df.pipes):
#       print(pipe_name)
#       valves_to_close, visited_pipes = g.find_all_valves_to_close(pipe_name)
#       for i in range(len(visited_pipes)):
#           temp_df = pd.DataFrame([[visited_pipes[i],valves_to_close]], columns = ['pipes', 'valves']) #MUST CHECK IF ALL PIPES ARE WRITTEN IN df
#           df = df.append(temp_df, ignore_index=True)#MUST CHECK IF ALL PIPES ARE WRITTEN IN df

