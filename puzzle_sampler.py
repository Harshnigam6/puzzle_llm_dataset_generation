import string
import random
import itertools

class PuzzleSampler:

    def __init__(self) -> None:
        self.graph_size = 11
        self.puzzle_complexity = 2
        self.puzzle_distance_thr = 3
        
    def map_chunks_to_block_names(self, graphs):
        """Map chunks to blocks A, B, C D....
        """
        chunks = graphs.chunks
        block_mapping = {}
        block_list = list(string.ascii_uppercase)
        block_index = 0
        for chunk in chunks:
            block_mapping[chunk] = block_list[block_index]
            block_index = block_index + 1
        return block_mapping
    
    def sample_chunks_for_shuffle(self, graph):
        chunks = graph.chunks
        sampled_chunks = random.sample(chunks, self.puzzle_complexity)
        return sampled_chunks
    
    def filter_combination_end_indices(self, sampled_chunks: list, combinations: list):
        filtered_end_coords = []
        assert len(sampled_chunks) == len(combination)
        for combination in combination:
            flag = True
            for end_corrds_indices in range(len(combination)):
                end_coords = combination[end_corrds_indices]
                chunk = sampled_chunks[end_corrds_indices]
                distance = abs(chunk.x - end_coords[0]) + abs(chunk.y - end_coords[1])
                if distance > self.puzzle_distance_thr:
                    flag = False
            if flag is True:
                filtered_end_coords.append(combination)
        return filtered_end_coords
    
    def get_non_chunk_indices(self, graph) -> list:
        index_pairs = [(i, j) for i in range(self.graph_size) for j in range(self.graph_size)]
        index_pair_set = set(index_pairs)

        chunk_indices = [(chunk.x, chunk.y) for chunk in graph.chunks]
        chun_indices_set = set(chunk_indices)

        non_chunk_indices_pairs = index_pair_set - chun_indices_set
        return list(non_chunk_indices_pairs)

    def create_combination_end_indices(self, non_chunk_indices_pairs: list) -> list:
        combinations = list(itertools.combinations(non_chunk_indices_pairs, self.puzzle_complexity))
        return combinations
    
    @staticmethod
    def map_chunks_to_indices(chunks_to_move: list, end_coords_list: list) -> dict:
        chunk_to_end_coords_map = {}
        end_coord_index = 0
        for chunk in chunks_to_move:
            chunk_to_end_coords_map[chunk] = end_coords_list[end_coord_index]
            end_coord_index = end_coord_index + 1
        return chunk_to_end_coords_map