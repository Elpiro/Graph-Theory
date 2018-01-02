# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
import random
import sys


def read_metro(metro_path):
    metro_stations = []
    lines = []
    with open(metro_path, 'r') as metro:
        datas = metro.read()
        datas = datas.split('\n')
        for line in range(len(datas)):
            if datas[line] == '[Vertices]':
                line += 1
                i = 0
                stations_id_to_name = dict()
                while datas[line]:
                    temp_data = datas[line]
                    node_ID = i
                    node_name = temp_data[5:]
                    metro_stations.append([node_ID, node_name])
                    stations_id_to_name[i] = node_name
                    i += 1
                    line += 1
                    if datas[line] == '[Edges]':
                        line += 1
                        i = 0
                        while datas[line]:
                            temp_data = datas[line].split(' ')
                            try:
                                temp_data[2] = int(temp_data[2])
                                temp_data.append(False)
                            except:
                                temp_data[2] = float(temp_data[2])
                                temp_data.append(True)
                            temp_data.insert(0, i)
                            lines.append(temp_data)
                            i += 1
                            line += 1

        stations_df = pd.DataFrame(metro_stations, columns=['Vertex_ID', 'Station_name'])

        lines_df = pd.DataFrame(lines, columns=['Edge_ID', 'Node_source', 'Node_dest', 'Weight', 'Walk'])

    return stations_df, lines_df, stations_id_to_name


class Graph():
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges

        self.nb_nodes = len(vertices)
        self.nb_edges = len(edges)

        self.adjacency_matrix = self.create_adjacency_matrix(self.edges)

        self.walking_lines = list(self.edges.Edge_ID[self.edges.Walk == True])
        sys.setrecursionlimit(self.nb_nodes * self.nb_nodes)

    def create_adjacency_matrix(self, edges):
        adj_matrix = np.array([[np.inf] * self.nb_nodes] * self.nb_nodes)
        for i in range(self.nb_edges):
            node1 = int(edges.Node_source[i])
            node2 = int(edges.Node_dest[i])

            adj_matrix[node1, node2] = edges.Weight[i]

        return adj_matrix

    def shortest_path_between_stations(self, station_source, station_dest, no_weights=False):
        try:
            if type(station_source) == str:
                station_source = int(self.vertices[self.vertices.Station_name == station_source].Vertex_ID)
            if type(station_dest) == str:
                station_dest = int(self.vertices[self.vertices.Station_name == station_dest].Vertex_ID)
        except:
            return 'station not found'

        if no_weights:
            adjacency_matrix = np.array([[np.inf] * self.nb_nodes] * self.nb_nodes)
            for i in range(self.nb_nodes):
                for j in range(self.nb_nodes):
                    if self.adjacency_matrix[i, j] != np.inf:
                        adjacency_matrix[i, j] = 1
        else:
            adjacency_matrix = self.adjacency_matrix

        vertex = self.vertices.Vertex_ID
        vertex = pd.DataFrame([vertex], columns=['Vertex'])

        visited = [False] * self.nb_nodes
        visited = pd.DataFrame(visited, columns=['Visited'])

        dijkstra_table = pd.concat([vertex, visited], axis=1)

        dijkstra_table = dijkstra_table.drop(['Vertex_ID'])

        distance = [np.inf] * self.nb_nodes
        distance[station_source] = 0
        distance = pd.DataFrame(distance, columns=['Distance'])

        dijkstra_table = pd.concat([dijkstra_table, distance], axis=1)

        previous = [None] * self.nb_nodes
        previous = pd.DataFrame(previous, columns=['Previous'])

        dijkstra_table = pd.concat([dijkstra_table, previous], axis=1)

        all_shortest_path = self.dijkstra(node_source=station_source,
                                          dijkstra_table=dijkstra_table,
                                          adjacency_matrix=adjacency_matrix)

        time = all_shortest_path.loc[station_dest, 'Distance']
        shortest_path = [station_dest]
        while True:
            next_node = all_shortest_path.loc[station_dest, 'Previous']
            shortest_path.append(next_node)
            station_dest = next_node
            if station_dest == station_source:
                break
        shortest_path.reverse()

        return shortest_path, time

    def dijkstra(self, node_source, dijkstra_table, adjacency_matrix):
        while True:
            unvisited_nodes_distances = dijkstra_table.Distance[dijkstra_table.Visited == False]
            try:
                node_source = unvisited_nodes_distances.idxmin()
            except:
                node_source = random.choice(node_source)
            dijkstra_table.at[node_source, 'Visited'] = True
            neighbours = np.where(adjacency_matrix[node_source, :] != np.inf)[0]
            for i in range(len(neighbours)):
                neighbour_node = neighbours[i]
                if dijkstra_table.Visited[neighbour_node] == False:
                    neighbour_node_weight = adjacency_matrix[node_source, neighbour_node]
                    old_distance = dijkstra_table.Distance[neighbour_node]
                    new_distance = float(dijkstra_table.Distance[node_source]) + neighbour_node_weight
                    if np.greater(old_distance, new_distance):
                        dijkstra_table.at[neighbour_node, 'Distance'] = new_distance
                        dijkstra_table.at[neighbour_node, 'Previous'] = node_source

            if dijkstra_table.Visited.all():
                break

        return dijkstra_table

    """ Tentative de BFS avec suivi des layers
    def shortest_path_by_nodes(self, node_source, node_dest):
        visited = np.array([False] * self.nb_nodes)
        queue = [node_source]
        layers = {node_source: 0}
        back_in_time = dict()
        time_forward = dict()
        while not visited.all():
            next_node = queue.pop(0)
            visited[next_node] = True
            node_layer = layers[next_node]
            temp_adj_matrix = self.adjacency_matrix[next_node, :]
            candidates_nodes = np.where(temp_adj_matrix != np.inf)[0]
            for node in candidates_nodes:
                if visited[node] == False:
                    queue.append(node)
                    layers[node] = node_layer + 1
                    back_in_time[next_node] = node
                    time_forward[node] = next_node

        dest_layer = layers[node_dest]
        path = [node_dest]
        for i in range(dest_layer-1):
            previous_node = time_forward[node_dest]
            path.append(previous_node)
            node_dest = previous_node

        path.reverse()
        path.insert(0,node_source)


        return path
    """
    """
    def floyd_warshall(self):
        floyd_warshall_matrix = self.adjacency_matrix
        floyd_warshall_matrix[floyd_warshall_matrix == np.inf] = 0
        for i in range(self.nb_nodes):
            floyd_warshall_matrix[i,i] = np.inf

        for k in range(self.nb_nodes):
            for i in range(self.nb_nodes):
                for j in range(self.nb_nodes):
                    if i!=j and i!=k and j!=k:
                        if floyd_warshall_matrix[i,j] > (floyd_warshall_matrix[i,k] +floyd_warshall_matrix[k,j]):
                            floyd_warshall_matrix[i,j] = floyd_warshall_matrix[i,k] +floyd_warshall_matrix[k,j]
        return floyd_warshall_matrix
    """

    def longest_path_in_x_hours(self, x):
        time_length = x * 3600
        not_visited = [True] * self.nb_edges
        zeros_adj_matrix = np.array([[0] * self.nb_nodes] * self.nb_nodes)

        median = self.edges.Weight.describe()[5]  # --> minimum weight to choose before breaking the loop
        test = 0
        while True:
            print(test)
            test += 1
            connected_subgraph = False
            candidates_edges = self.edges[not_visited]

            big_weight = np.max(candidates_edges.Weight)
            selected_edge = candidates_edges[candidates_edges.Weight == big_weight]

            if len(candidates_edges) > 1:
                selected_edge_index = random.choice(selected_edge.index)
                selected_edge = selected_edge[selected_edge.index == selected_edge_index]

            node_source = int(selected_edge.Node_source.values[0])
            node_dest = int(selected_edge.Node_dest.values[0])

            zeros_adj_matrix[node_source, node_dest] = big_weight
            zeros_adj_matrix[node_dest, node_source] = big_weight

            not_visited[int(selected_edge.Edge_ID.values[0])] = False

            try:
                mirror_edge = self.edges[self.edges.Node_source == str(node_dest)]
                mirror_edge = mirror_edge[mirror_edge.Node_dest == str(node_source)]
                not_visited[int(mirror_edge.Edge_ID.values[0])] = False
            except:
                None

            extremes_nodes = dict()
            good_nodes = dict()
            critical_nodes = dict()
            nodes_count = 0
            for i in range(self.nb_nodes):
                connected_nodes = np.where(zeros_adj_matrix[i, :] != 0)[0].tolist()
                if len(connected_nodes) > 0:
                    nodes_count += len(connected_nodes)
                if len(connected_nodes) == 1:
                    extremes_nodes[i] = connected_nodes
                if len(connected_nodes) == 2:
                    good_nodes[i] = connected_nodes
                if len(connected_nodes) == 3:
                    critical_nodes[i] = connected_nodes

            # prune branch
            if len(critical_nodes) >= 1:
                zeros_adj_matrix[node_source, node_dest] = 0
                zeros_adj_matrix[node_dest, node_source] = 0
                nodes_count -= 2

            # check if single line
            if (len(good_nodes) == (nodes_count - 2)) and (len(extremes_nodes) == 2):
                connected_subgraph = True

            # cycle created
            if len(good_nodes) == nodes_count:
                zeros_adj_matrix[node_source, node_dest] = 0
                zeros_adj_matrix[node_dest, node_source] = 0
                nodes_count -= 2

            """Si subgraph_connected = False"""
            """Trouver comment eliminer les edges qui correspondent aux noeuds extremes"""
            """relancer la boucle sans utiliser les edges"""

            total_time = np.sum(zeros_adj_matrix) / 3600

            if total_time > x and connected_subgraph == True:
                for key, item in extremes_nodes:
                    not_visited[key] = True

            if (total_time > time_length and connected_subgraph == False) or ((np.array(not_visited) == False).all()):
                zeros_adj_matrix[node_source, node_dest] = 0
                zeros_adj_matrix[node_dest, node_source] = 0
                total_time = np.sum(zeros_adj_matrix) / 3600
                break
        print(good_nodes)
        print(critical_nodes)
        print(extremes_nodes)
        print(total_time)
        return total_time


metro_stations, metro_lines, stations_id_to_name = read_metro('metro_complet.txt')

g = Graph(metro_stations, metro_lines)
"""user inputs"""
while True:
    print('----------------------------------------------------------------')
    print('1 -> shortest path between stations')
    print('2 -> --- not ready yet ---vcompute longest path in the network, each node visited once')
    print('----------------------------------------------------------------')

    choice = input('Choose an option: ')

    if choice == '1':
        while True:
            print('\n----------------------------------------------------------------')
            print('1 -> compute shortest path between stations counting time')
            print('2 -> compute shortest path counting nodes')
            print('3 -> show list of stations')
            print('any key -> go back')
            print('----------------------------------------------------------------')
            choice2 = input('choose an option: ')

            if choice2 == '1':
                station_source = int(input('enter station source ID: '))
                station_dest = int(input('enter destintation source ID: '))
                shortest_path, time = g.shortest_path_between_stations(station_source=station_source,
                                                                       station_dest=station_dest, no_weights=False)
                for i in range(len(shortest_path)):
                    shortest_path[i] = stations_id_to_name[shortest_path[i]]
                print('***********************************************************')
                print('path length:')
                print(len(shortest_path))
                print('path:')
                print(shortest_path)
                print(' ')
                print('time of travel = ' + str(np.ceil(time / 60)) + ' minutes')
                print('***********************************************************')
                input('press enter to continue')

            elif choice2 == '2':
                station_source = int(input('enter station source ID: '))
                station_dest = int(input('enter destintation source ID: '))
                shortest_path , time= g.shortest_path_between_stations(station_source=station_source,
                                                                 station_dest=station_dest, no_weights=True)

                for i in range(len(shortest_path)):
                    shortest_path[i] = stations_id_to_name[shortest_path[i]]
                print('***********************************************************')
                print('path length:')
                print(len(shortest_path))
                print('path:')
                print(shortest_path)
                print('***********************************************************')
                input('press enter to continue')

            elif choice2 == '3':
                for key, value in stations_id_to_name.items():
                    if ((int(key) + 1) % 5) == 0:
                        sys.stdout.write(str(key) + value + '\n')
                    else:
                        sys.stdout.write(str(key) + value + '\t')
            else:
                break
    if choice == '2':
        print('How long do you want to stay away from light ?')
        x = input('enter the desired time in hours. Enter "q" to go back')
        time = g.longest_path_in_x_hours(x)
        print(time)


