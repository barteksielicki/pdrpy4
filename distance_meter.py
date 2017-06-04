import json
import os
import sys

import networkx as nx
from geopy.distance import distance


class Node:
    """
    Simple class representing single node in tram route graph.
    """

    def __init__(self, id, lat, lon):
        self.id = id
        self.lat = lat
        self.lon = lon

    @property
    def coords(self):
        return (self.lat, self.lon)

    def get_distance_to(self, node):
        return distance(self.coords, node.coords).kilometers


class TemporaryNode:
    """
    To find distance between two points using route graph, these points must be
    inserted into graph as new nodes. We don't want them to remain in graph
    as it will be reused to calculate another distance, and making deep copy
    of graph is slow. That context manager will be helpful in adding temporary
    nodes.
    """

    def __init__(self, graph, node, tolerance):
        self.graph = graph
        self.node = node
        self.tolerance = tolerance
        self.left = None
        self.right = None

    def __enter__(self):
        """ add node to graph """
        g = self.graph
        node = self.node

        edge, distance = DistanceMeter.get_closest_edge(node, g.edges_iter())
        if distance < self.tolerance:
            self.left, self.right = edge
            g.add_edge(
                self.left, node, weight=node.get_distance_to(self.left))
            g.add_edge(
                node, self.right, weight=node.get_distance_to(self.right))
            g.remove_edge(self.left, self.right)
            return node

    def __exit__(self, *args):
        """ remove node from graph and add preiously deleted edge """
        if self.left and self.right:
            self.graph.remove_node(self.node)
            self.graph.add_edge(
                self.left, self.right,
                weight=self.left.get_distance_to(self.right))


class DistanceMeter:
    ROUTES_DATA_DIRECTORY = "routes"
    POSITION_TOLERANCE = 0.01  # km

    def __init__(self, data_directory=ROUTES_DATA_DIRECTORY):
        """ init graphs (one graph per route) """
        self.graphs = {}
        for filename in os.listdir(data_directory):
            route, _ = os.path.splitext(filename)
            self.graphs[route] = self.construct_graph(
                os.path.join(data_directory, filename))

    def construct_graph(self, file):
        """ create graph based on tram route data """
        ways, nodes = self.extract_route_data(file)
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        for way in ways:
            way_nodes = [nodes[node_id] for node_id in way]
            for a, b in zip(way_nodes, way_nodes[1:]):
                graph.add_edge(a, b, weight=a.get_distance_to(b))
        return self.clean_graph(graph)

    def clean_graph(self, graph):
        """
        return biggest connected subgraph;
        graph created from route data contains many redundant components,
        like depot tracks or single vertices representing tram stops
        """
        return max(nx.connected_component_subgraphs(graph),
                   key=lambda g: g.number_of_nodes())

    def extract_route_data(self, file):
        """ return nodes and ways (segments creating route) from json file """
        with open(file) as data:
            data = json.load(data)["elements"]
        ways = [x["nodes"] for x in data if x["type"] == "way"]
        raw_nodes = (n for n in data if n["type"] == "node")
        nodes = {n["id"]: Node(n["id"], n["lat"], n["lon"]) for n in raw_nodes}

        return ways, nodes

    @staticmethod
    def get_distance_to_segment(p0, p1, p2):
        """ get distance between point p0 and line segment <p1, p2> """
        x0, y0 = p0
        x1, y1 = p1
        x2, y2 = p2
        if not any([(x1 <= x0 <= x2), (x2 <= x0 <= x1),
                    (y1 <= y0 <= y2), (y2 <= y0 <= y1)]):
            return sys.maxsize

        nom = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        denom = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
        result = nom / denom
        return result

    @staticmethod
    def get_closest_edge(node, edges):
        annotated_edges = (
            (e, DistanceMeter.get_distance_to_segment(
                node.coords, e[0].coords, e[1].coords)) for e in edges)
        return min(annotated_edges, key=lambda pair: pair[1])

    def get_distance_between_nodes(self, node1, node2, route):
        """ calculate distance between node1 and node2 along given route """
        graph = self.graphs.get(route)
        if not graph:
            return None
        with TemporaryNode(graph, node1, self.POSITION_TOLERANCE) as a:
            with TemporaryNode(graph, node2, self.POSITION_TOLERANCE) as b:
                if not a or not b:
                    distance = None
                else:
                    distance = nx.dijkstra_path_length(graph, a, b)
        return distance

    def get_distance_between_coords(self, lat1, lon1, lat2, lon2, route):
        """ calculate distance between two points along given route """
        node1 = Node(None, lat1, lon1)
        node2 = Node(None, lat2, lon2)
        return self.get_distance_between_nodes(node1, node2, route)
