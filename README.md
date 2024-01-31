# Puzzle dataset
In this project we aim to synthetically generate a dataset consisting of visual puzzles along with instructions to solve the puzzles. The end goal is to provide an open sources evaluation test bench to measure performance of vision-LLMs on tasks that requires navigation and image understanding in spatial domain.

This project is inspired from how humans build spatial and visual awareness by playing puzzle as kids like jigsaw puzzles.

## V1
In the first version of the dataset, we create puzzles by simply dividing an image into chunks, and shuffling few of the chunks away from their original positions. As we move a chunk to different positions in a grid, we record the path all along. This gives us a series of operations that we can apply to this chunks to move it back to its original position.

We repeat the above step for 1000 images from COCO dataset on a variety of image classes. For each image, we create 10 puzzles by sampling different chunks to move. We also keep the number of chunks to move in the puzzle limited to one for preliminary experimentation.

In the final dataset, a data point is a dictionary with the following datastructures:
{
    "image": np.array
    (This is the snapshot of an image which has been shuffled to create a puzzle.),
    "instructions": list
    (This list contains instructions like "Move block A right")
}


