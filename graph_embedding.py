from PIL import Image, ImageOps
import typing
from create_graph_dataset import Graph, PathFinder
import os
from PIL import ImageDraw, ImageFont
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

class ImageGraph:
    def __init__(self, image_path: str, graph_size: int = 11):
        self.image_path = image_path
        self.graph_size = graph_size
        self.original_image = Image.open(image_path)
        self.resized_image = self._resize_image_to_divisible_by_three(self.original_image)
        self.chunk_size = self._calculate_chunk_size()
        self.embedded_image = self._embed_image()
        self.graph = self._create_graph()
        # print(self.graph)
        # print(self.graph.chunks[0].x)

    def _calculate_chunk_size(self) -> typing.Tuple[int, int]:
        """Calculate the size of each chunk based on the original image."""
        resized_image = self._resize_image_to_divisible_by_three(self.original_image)
        return (resized_image.width // 3, resized_image.height // 3)

    def _resize_image_to_divisible_by_three(self, image: Image.Image) -> Image.Image:
        """Resize the image to make its dimensions divisible by 3."""
        width, height = image.size
        print(f"Image dimension {width}*{height}")
        new_width = width + (-width % 3)
        new_height = height + (-height % 3)
        resized_image = ImageOps.pad(image, (new_width, new_height), method=Image.BICUBIC, color='black')
        return resized_image

    def _split_image(self, image: Image.Image) -> typing.List[Image.Image]:
        """Split the image into 9 equal-sized chunks."""
        width, height = image.size
        chunk_width, chunk_height = self.chunk_size

        chunks = []
        for i in range(0, width, chunk_width):
            for j in range(0, height, chunk_height):
                box = (i, j, i + chunk_width, j + chunk_height)
                chunks.append(image.crop(box))

        return chunks

    def _embed_image(self) -> Image.Image:
        """Embed the original image into the center of a larger image."""
        new_image_size = (self.graph_size * self.chunk_size[0], self.graph_size * self.chunk_size[1])
        new_image = Image.new('RGB', new_image_size)

        chunks = self._split_image(self._resize_image_to_divisible_by_three(self.original_image))
        start_x = (self.graph_size - 3) // 2 * self.chunk_size[0]
        start_y = (self.graph_size - 3) // 2 * self.chunk_size[1]

        for i in range(3):
            for j in range(3):
                box = (start_x + i * self.chunk_size[0], start_y + j * self.chunk_size[1])
                new_image.paste(chunks[i * 3 + j], box)

        return new_image

    def _create_graph(self) -> Graph:
        """Create a graph based on the embedded image, positioning the chunks correctly."""
        # Calculate the starting positions for the chunks in the 11x11 grid
        start_x = (self.graph_size - 3) // 2
        start_y = (self.graph_size - 3) // 2

        # Create chunk positions based on the starting coordinates
        chunk_positions = [(start_x + x, start_y + y) for x in range(3) for y in range(3)]
        return Graph(self.graph_size, self.graph_size, chunk_positions)

    def show_embedded_image(self):
        """Display the embedded image."""
        self.embedded_image.show()

    # def move_chunk_to_position(self, chunk_index: int, target_position: tuple) -> Image.Image:
    #     """Move a chunk to a specified position and return the updated image."""
    #     path_finder = PathFinder(self.graph)
    #     path_finder.find_paths()

    #     start_position = (self.graph.chunks[chunk_index].x, self.graph.chunks[chunk_index].y)
    #     print(start_position)
    #     if target_position not in path_finder.paths[start_position]:
    #         raise ValueError(f"No path found to move chunk {chunk_index} to {target_position}")

    #     # Follow the path to move the chunk
    #     for step in path_finder.paths[start_position][target_position]:
    #         self._move_chunk(self.graph.chunks[chunk_index], step)

    #     return self._generate_updated_image()
        
    def get_paths_per_chunks(self, chunks_to_move_list: list, end_coords_dict: dict) -> dict:
        """Returns the paths for the chunks provided, output is a dict with instructions mapped
        to list of instructions.

        Args:
            chunks_to_move_list (list): _description_
            end_coords_list (list): _description_
        """
        instructions_per_chunk = {}

        path_finder = PathFinder(self.graph)
        path_finder.find_paths()

        for chunk in chunks_to_move_list:
            start_coord = chunk.x, chunk.y
            end_coord = end_coords_dict[chunk]

            if end_coord not in path_finder.paths[start_coord]:
                raise ValueError(f"No path found to move chunk {start_coord} to {end_coord}")
            
            instructions = path_finder.paths[start_coord][end_coord]
            instructions_per_chunk[chunk] = instructions
        return instructions_per_chunk
    
    def generate_data_point(
            self,
            chunk_instructions: dict, 
            output_folder: str,
            image_name: str, 
            chunk_block_map: dict,
            metadata: list[dict]
            ) -> dict:
        instructions = []
        debug_instruction = {}
        step_count = 0
        max_steps = 0
        for chunk in chunk_instructions:
            max_steps = max(len(chunk_instructions[chunk]), max_steps)
            debug_instruction[chunk] = []


        for steps in range(max_steps):
            for chunk in chunk_instructions:
                try:
                    block_tag = chunk_block_map[chunk]
                    operation = chunk_instructions[chunk][steps]
                    self._move_chunk(chunk, operation)
                    operation = self.invert_operation(operation)
                    debug_instruction[chunk].append(operation)
                    operation = f"Move block {block_tag} {operation}"
                    instructions.append(operation)
                    # print(instructions)
                    step_count += 1
                except:
                    pass
    
        instructions.reverse()
        shuffledd_chunk_block_map = {}
        for chunk in chunk_instructions:
            shuffledd_chunk_block_map[chunk] = chunk_block_map[chunk]
            debug_instruction[chunk].reverse()
        img = self._generate_updated_image_with_instructions(
            instructions, 
            shuffledd_chunk_block_map,
            instruction_mode=False
            )
        metadata.append({
            "file_name": f"{image_name}.png",
            "instructions": self.convert_list_of_strings_to_string(instructions)
        })
        img.save(os.path.join(output_folder, f"{image_name}.png"))
        metadata_df = pd.DataFrame(metadata)
        metadata_df.to_csv(f"{output_folder}/metadata.csv", index=False)

        # debuggin data structrures
        data_point_for_visualization = {}
        data_point_for_visualization["instructions"] = debug_instruction
        data_point_for_visualization["graph"] = self.graph
        data_point_for_visualization["start_image"] = img
        return data_point_for_visualization
    

    def generate_images_for_demo(
            self, 
            chunk_instructions,
            output_folder,
            chunk_block_map,
            start_image
            ):
        start_image.save(os.path.join(output_folder, f"a_{-2}.png"))
        self.move_chunks(chunk_instructions, output_folder, chunk_block_map)


    def move_chunks(self, chunk_instructions: dict, output_folder: str, chunk_block_map: dict) -> None:
        """This method is to save state of the image after every operation: helps in visualizing
        the path.

        Args:
            chunk_instructions (list): _description_
            output_folder (str): _description_
            chunk_block_map (dict): _description_
        """
        instructions = []
        step_count = 0
        img = self._generate_updated_image_with_instructions(instructions)
        img.save(os.path.join(output_folder, f"a_{-1}.png"))
        max_steps = 0
        for chunk in chunk_instructions:
            max_steps = max(len(chunk_instructions[chunk]), max_steps)

        for steps in range(max_steps):
            for chunk in chunk_instructions:
                try:
                    block_tag = chunk_block_map[chunk]
                    operation = chunk_instructions[chunk][steps]
                    self._move_chunk(chunk, operation)
                    operation = f"Move block {block_tag} {operation}"
                    instructions.append(operation)
                    # print(instructions)
                    img = self._generate_updated_image_with_instructions(instructions)
                    img.save(os.path.join(output_folder, f"step_{step_count}.png"))
                    step_count += 1
                except:
                    pass

    def _generate_updated_image_with_instructions(
            self, 
            instructions: list, 
            shuffled_chunk_map: dict=None,
            instruction_mode: bool = True
            ) -> Image.Image:
        """Generate an image with the current state and a panel of instructions."""
        updated_image = self._generate_updated_image(shuffled_chunk_map)
        instruction_image = Image.new('RGB', (200, updated_image.height), color='white')
        draw = ImageDraw.Draw(instruction_image)
        font = ImageFont.load_default()  # You can use a custom font here

        font_size = 20  # You can adjust the size
        font = ImageFont.load_default()
        try:
            font = ImageFont.truetype("arial", font_size)
        except IOError:
            print("Default font not found. Using PIL's load_default() font.")

        # Add instructions to the instruction panel
        y_position = 10
        for instruction in instructions:
            draw.text((10, y_position), instruction, fill='black', font=font)
            y_position += 20
        if instruction_mode is True:
            # Concatenate instruction panel and updated image
            combined_image = Image.new('RGB', (instruction_image.width + updated_image.width, updated_image.height))
            combined_image.paste(instruction_image, (0, 0))
            combined_image.paste(updated_image, (instruction_image.width, 0))
            return combined_image
        return updated_image

    def _move_chunk(self, chunk, direction):
        """Move a chunk in a specified direction."""
        connections_vector = {
            'left': (-1, 0),
            'right': (1, 0),
            'up': (0, -1),
            'down': (0, 1)
        }
        direction_vector = connections_vector[direction]
        chunk.x, chunk.y = chunk.x + direction_vector[0], chunk.y + direction_vector[1]

    def _generate_updated_image(self, shuffled_chunk_map: dict=None) -> Image.Image:
        """Generate an image reflecting the current state of the graph.
        
        if shuffled chunk is not none, then we annotate the shuffle chunks below them as blocks.
        """
        border = 38
        new_image = Image.new(
            'RGB', 
            (self.graph_size * self.chunk_size[0], (self.graph_size * self.chunk_size[1]) + border)
            )
        chunks = self._split_image(self.resized_image)  # Use the resized image
        font = ImageFont.truetype("arial.ttf", 18)  # Load a font, with size appropriate for your chunks
        draw = ImageDraw.Draw(new_image)  # Create a drawing context
        chunk_index = 0
        for chunk in self.graph.chunks:
            # print(chunk.x, chunk.y, chunk_index)
            chunk_image = chunks[chunk_index]
            box = (chunk.x * self.chunk_size[0], chunk.y * self.chunk_size[1])
            new_image.paste(chunk_image, box)
            if shuffled_chunk_map is not None:
                if chunk not in shuffled_chunk_map.keys(): pass
                else:
                    block_tag = shuffled_chunk_map[chunk]
                    # Calculate position to place the text based on the chunk's position
                    text_position = (box[0], box[1] + self.chunk_size[1] + 10)  # Adjust as needed
                    draw.text(text_position, f"Block {block_tag}", fill='white', font=font)
            chunk_index = chunk_index + 1
        return new_image
    
    @staticmethod
    def convert_list_of_strings_to_string(instruction_list: list[str]) -> str:
        instruction_str = ""
        for i in instruction_list:
            instruction_str = instruction_str + i + ","
        return instruction_str[:-1]
    
    @staticmethod
    def invert_operation(operation: str) -> str:
        inverted_operation_map = {
            "up": "down",
            "down": "up",
            "right": "left",
            "left": "right"
        }
        return inverted_operation_map[operation]


# image_graph = ImageGraph("llama.png.")
# # Moving chunk
# final_state_image = image_graph.move_chunk_to_position(chunk_index=0, target_position=(0, 0))
# final_state_image.show()

# image_graph_rep = image_graph._create_graph()
# print(image_graph_rep)
# image_graph.show_embedded_image()

