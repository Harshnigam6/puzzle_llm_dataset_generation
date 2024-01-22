from PIL import Image
import glob
from graph_embedding import ImageGraph

def create_animated_gif(image_folder: str, output_gif: str, frame_duration: int = 500):
    frames = []
    images = glob.glob(f"{image_folder}/*.png")
    for image_file in sorted(images):
        frame = Image.open(image_file)
        frames.append(frame)

    frames[0].save(output_gif, format='GIF', append_images=frames[1:], save_all=True, duration=frame_duration, loop=0)

# Example usage
image_graph = ImageGraph("llama.png")
image_graph.move_chunk_to_position(3, (0, 0), "output_images")
create_animated_gif("output_images", "chunk_movement.gif")
