# Puzzle dataset
In this project we aim to synthetically generate a dataset consisting of visual puzzles along with instructions to solve the puzzles. The end goal is to provide an open sources evaluation test bench to measure performance of vision-LLMs on tasks that requires navigation and image understanding in spatial domain.

This project is inspired from how humans build spatial and visual awareness by playing puzzle as kids like jigsaw puzzles.

## V1
In the first version of the dataset, we create puzzles by simply dividing an image into chunks, and shuffling few of the chunks away from their original positions. As we move a chunk to different positions in a grid, we record the path all along. This gives us a series of operations that we can apply to this chunks to move it back to its original position.

We repeat the above step for 200 images from COCO dataset on a variety of image classes. For each image, we create 5 puzzles by sampling different chunks to move. We also keep the number of chunks to move in the puzzle limited to one for preliminary experimentation.

In the final dataset, a data point is a dictionary with the following datastructures:
{
    "image": .png
    (This is the snapshot of an image which has been shuffled to create a puzzle.),
    "instructions": string containing text instructions seperated by commas.
    (An instruction is an operation containing block tag and optimal move like "Move block A right")
}

### Dataset
1. Public dataset for v1 has been pushed to hugging face: [puzzles-for-vision-llm ](https://huggingface.co/datasets/Harshnigm/puzzles-for-vision-llm)
2. The dataset contains about 1000 puzzles. 
3. Currently all the data is stored under train split.



![Example GIF](https://github.com/Harshnigam6/puzzle_llm_dataset_generation/blob/main/artifacts/demo_solving_puzzle.gif)


