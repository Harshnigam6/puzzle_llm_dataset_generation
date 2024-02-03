from collections import deque

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.connections = {'up': None, 'down': None, 'left': None, 'right': None}

class Graph:
    def __init__(self, width, height, chunk_positions):
        self.nodes = [[Node(x, y) for y in range(height)] for x in range(width)]
        self._connect_nodes()
        self.chunks = [self._create_chunk(x, y) for x, y in chunk_positions]

    def __str__(self):
        graph_str = ""
        for y in range(len(self.nodes[0])):
            for x in range(len(self.nodes)):
                if any(chunk.x == x and chunk.y == y for chunk in self.chunks):
                    graph_str += "* "
                else:
                    graph_str += ". "
            graph_str += "\n"
        return graph_str

    def _connect_nodes(self):
        for x in range(len(self.nodes)):
            for y in range(len(self.nodes[x])):
                node = self.nodes[x][y]
                if x > 0:
                    node.connections['left'] = self.nodes[x - 1][y]
                if x < len(self.nodes) - 1:
                    node.connections['right'] = self.nodes[x + 1][y]
                if y > 0:
                    node.connections['up'] = self.nodes[x][y - 1]
                if y < len(self.nodes[x]) - 1:
                    node.connections['down'] = self.nodes[x][y + 1]

    def _create_chunk(self, x, y):
        chunk = Chunk(x, y)
        chunk.connections = self.nodes[x][y].connections.copy()
        return chunk

class Chunk(Node):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.is_chunk = True

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
        self.paths = {}

    def find_paths(self):
        for chunk in self.graph.chunks:
            self.paths[(chunk.x, chunk.y)] = self._find_paths_from_chunk(chunk)
            # break

    def _find_paths_from_chunk(self, chunk):
        queue = deque([(chunk, [])])
        paths = {}
        visited = set()

        while queue:
            current_chunk, current_path = queue.popleft()
            current_key = (current_chunk.x, current_chunk.y)

            if current_key in visited:
                continue

            visited.add(current_key)

            for direction, next_node in current_chunk.connections.items():
                if next_node is None:
                    continue

                next_key = (next_node.x, next_node.y)
                new_path = current_path + [direction]

                if next_key not in paths or len(new_path) < len(paths[next_key]):
                    paths[next_key] = new_path
                    queue.append((next_node, new_path))

        return paths

    # def _find_paths_from_chunk(self, chunk, path, visited):
    #     visited.add((chunk.x, chunk.y))
    #     # print(visited)
    #     paths = {}

    #     for direction, next_node in chunk.connections.items():
    #         if next_node is None or (next_node.x, next_node.y) in visited:
    #             continue

    #         new_path = path + [direction]
    #         # print(new_path)
    #         node_key = (next_node.x, next_node.y)

    #         if not any(c.x == next_node.x and c.y == next_node.y for c in self.graph.chunks):
    #             if node_key not in paths or len(new_path) < len(paths[node_key]):
    #                 paths[node_key] = new_path

    #         deeper_paths = self._find_paths_from_chunk(next_node, new_path, visited)
    #         for key, value in deeper_paths.items():
    #             if key not in paths or len(value) < len(paths[key]):
    #                 paths[key] = value

    #     return paths

# Example usage
# graph = Graph(11, 11, [(0, 0), (1, 1), (2, 2)])
# print(graph)  # Visualize the graph

# path_finder = PathFinder(graph)
# path_finder.find_paths()  # Find all paths

# print(path_finder.paths)

# Print some paths for demonstration
# for start, paths in path_finder.paths.items():
#     print(f"Paths from chunk at {start}:")
#     for node, node_paths in paths.items():
#         print(f"  To node {node}:")
#         for path in node_paths[:3]:  # Print first 3 paths for brevity
#             print("    " + " -> ".join(path))
