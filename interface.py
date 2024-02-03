import os
from PIL import Image
import glob
from graph_embedding import ImageGraph
from puzzle_sampler import PuzzleSampler
from create_graph_dataset import Graph, PathFinder
import re
import random



def sort_key_func(file_path):
    """ Extracts the number from the file path, accounting for negative numbers, and returns it for sorting. """
    # This regex will match both positive and negative integers
    numbers = re.findall(r'-?\d+', file_path)
    # The function will return the first number found, assuming there's at least one number
    return int(numbers[0]) if numbers else 0

def create_animated_gif(image_folder: str, output_gif: str, frame_duration: int = 500, new_size: tuple = None):
    frames = []
    images = sorted(glob.glob(f"{image_folder}/*.png"), key=sort_key_func)
    for image_file in images:
        print(image_file)
        frame = Image.open(image_file)
        # if new_size:
        #     frame = frame.resize(new_size, Image.Resampling.LANCZOS)  # Updated resizing method
        frames.append(frame)

    frames[0].save(output_gif, format='GIF', append_images=frames[1:], save_all=True, duration=frame_duration, loop=0)



# num_samples_per_image = 5
# metadata = []
# directory_path = 'images'

# for filename in os.listdir(directory_path):
#     # Construct full file path
#     file_path = os.path.join(directory_path, filename)
#     print(file_path)
#     for i in range(num_samples_per_image):
#         image_graph = ImageGraph(file_path)
#         graph = image_graph.graph

#         puzzle_sampler = PuzzleSampler()
#         sampled_chunks_for_displacement = puzzle_sampler.sample_chunks_for_shuffle(graph)
#         # print(sampled_chunks_for_displacement[0].x, sampled_chunks_for_displacement[0].y)

#         chunk_block_map = puzzle_sampler.map_chunks_to_block_names(graph)

#         non_chunk_indices_pairs = puzzle_sampler.get_non_chunk_indices(graph)
#         # print(non_chunk_indices_pairs)

#         end_coords_combos = puzzle_sampler.create_combination_end_indices(non_chunk_indices_pairs)
#         # print(end_coords_combos[0], len(end_coords_combos))
#         random.shuffle(end_coords_combos)

#         chunk_to_end_coord_map = puzzle_sampler.map_chunks_to_indices(
#             sampled_chunks_for_displacement,
#             # [(10, 0), (0,10)]
#             end_coords_combos[i]
#             )
#         # print(chunk_to_end_coord_map)

#         instructions_per_chunk = image_graph.get_paths_per_chunks(sampled_chunks_for_displacement, chunk_to_end_coord_map)
#         print(instructions_per_chunk)

#         # image_graph.move_chunks(instructions_per_chunk, "output_images", chunk_block_map)
#         image_name = f"{filename.split('.')[0]}_{i}"
#         data_point = image_graph.generate_data_point(
#             instructions_per_chunk, 
#             "dataset",
#             image_name,
#             chunk_block_map,
#             metadata
#             )
#         image_graph.generate_images_for_demo(
#             chunk_instructions= data_point["instructions"],
#             output_folder="output_images",
#             chunk_block_map=chunk_block_map,
#             start_image=data_point["start_image"]
#         )
#         break
#     break
        
    

# print(dataset)
# new_width = 350  # Adjust the width as needed
# new_height = 350  # Adjust the height as needed
create_animated_gif('output_images', 'demo_solving_puzzle.gif',
                    frame_duration=700, 
                    # new_size=(new_width, new_height)
                    )
