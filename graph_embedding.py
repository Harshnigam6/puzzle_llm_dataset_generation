from PIL import Image, ImageOps
import typing
from create_graph_dataset import Graph, PathFinder
import os
from PIL import ImageDraw, ImageFont

class ImageGraph:
    def __init__(self, image_path: str, graph_size: int = 11):
        self.image_path = image_path
        self.graph_size = graph_size
        self.original_image = Image.open(image_path)
        self.resized_image = self._resize_image_to_divisible_by_three(self.original_image)
        self.chunk_size = self._calculate_chunk_size()
        self.embedded_image = self._embed_image()
        self.graph = self._create_graph()
        print(self.graph)
        print(self.graph.chunks[0].x)

    def _calculate_chunk_size(self) -> typing.Tuple[int, int]:
        """Calculate the size of each chunk based on the original image."""
        resized_image = self._resize_image_to_divisible_by_three(self.original_image)
        return (resized_image.width // 3, resized_image.height // 3)

    def _resize_image_to_divisible_by_three(self, image: Image.Image) -> Image.Image:
        """Resize the image to make its dimensions divisible by 3."""
        width, height = image.size
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
        
    def move_chunk_to_position(self, chunk_index: int, target_position: tuple, output_folder: str):
        """Move a chunk to a specified position and save each step as an image with instructions."""
        path_finder = PathFinder(self.graph)
        path_finder.find_paths()

        start_position = (self.graph.chunks[chunk_index].x, self.graph.chunks[chunk_index].y)
        if target_position not in path_finder.paths[start_position]:
            raise ValueError(f"No path found to move chunk {chunk_index} to {target_position}")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        instructions = []
        step_count = 0
        img = self._generate_updated_image_with_instructions(instructions)
        img.save(os.path.join(output_folder, f"a_{-1}.png"))
        for step in path_finder.paths[start_position][target_position]:
            self._move_chunk(self.graph.chunks[chunk_index], step)
            instructions.append(step)
            img = self._generate_updated_image_with_instructions(instructions)
            img.save(os.path.join(output_folder, f"step_{step_count}.png"))
            step_count += 1

    def _generate_updated_image_with_instructions(self, instructions: list) -> Image.Image:
        """Generate an image with the current state and a panel of instructions."""


        updated_image = self._generate_updated_image()
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
            instruction = f"Move block A {instruction}."
            draw.text((10, y_position), instruction, fill='black', font=font)
            y_position += 20

        # Concatenate instruction panel and updated image
        combined_image = Image.new('RGB', (instruction_image.width + updated_image.width, updated_image.height))
        combined_image.paste(instruction_image, (0, 0))
        combined_image.paste(updated_image, (instruction_image.width, 0))

        return combined_image

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

    def _generate_updated_image(self) -> Image.Image:
        """Generate an image reflecting the current state of the graph."""
        new_image = Image.new('RGB', (self.graph_size * self.chunk_size[0], self.graph_size * self.chunk_size[1]))
        chunks = self._split_image(self.resized_image)  # Use the resized image
        chunk_index = 0
        for chunk in self.graph.chunks:
            print(chunk.x, chunk.y, chunk_index)
            chunk_image = chunks[chunk_index]
            box = (chunk.x * self.chunk_size[0], chunk.y * self.chunk_size[1])
            new_image.paste(chunk_image, box)
            chunk_index = chunk_index + 1
        return new_image

# image_graph = ImageGraph("llama.png.")
# # Moving chunk
# final_state_image = image_graph.move_chunk_to_position(chunk_index=0, target_position=(0, 0))
# final_state_image.show()

# image_graph_rep = image_graph._create_graph()
# print(image_graph_rep)
# image_graph.show_embedded_image()

