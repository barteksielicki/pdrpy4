import json

import networkx as nx
import sys
from geopy.distance import distance


class Node:
    def __init__(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon

    @property
    def coords(self):
        return (self.lat, self.lon)

    def get_distance_to(self, node):
        return distance(self.coords, node.coords).kilometers


class DistanceMeter:
    RAILWAYS_FILENAME = "trakcje.json"

    def __init__(self, data_filename=RAILWAYS_FILENAME):
        """ init object with railways data extracted from file """
        with open(data_filename) as data:
            data = json.load(data)["elements"]
            ways = [x["nodes"] for x in data if x["type"] == "way"]
            self.nodes = {
                n["id"]: Node(n["id"], n["lat"], n["lon"])
                for n in data if n["type"] == "node"}
            self.graph = self.construct_graph(ways, self.nodes)

    def construct_graph(self, ways, nodes):
        """ create graph based on railways data """
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        for way in ways:
            way_nodes = [nodes[node_id] for node_id in way]
            for a, b in zip(way_nodes, way_nodes[1:]):
                graph.add_edge(a, b, weight=a.get_distance_to(b))
        return graph

    def get_closest_edge(self, node, edges):
        def get_distance(p0, p1, p2):
            x0, y0 = p0
            x1, y1 = p1
            x2, y2 = p2
            if not any([(x1 <= x0 <= x2), (x2 <= x0 <= x1), (y1 <= y0 <= y2), (y2 <= y0 <= y1)]):
                return sys.maxsize
            nom = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
            denom = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
            result = nom / denom
            return result

        return min(edges, key=lambda edge: get_distance(node.coords, edge[0].coords, edge[1].coords))

    def add_new_node(self, g, lat, lon):
        node = Node(None, lat, lon)
        edge = self.get_closest_edge(node, g.edges_iter())
        a, b = edge
        g.add_edge(a, node, weight=a.get_distance_to(node))
        g.add_edge(node, b, weight=node.get_distance_to(b))
        g.remove_edge(a, b)
        return node

    def get_distance_between(self, lat1, lon1, lat2, lon2):
        g = self.graph.copy()
        a = self.add_new_node(g, lat1, lon1)
        b = self.add_new_node(g, lat2, lon2)
        return nx.dijkstra_path_length(g, a, b)
