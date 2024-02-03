from datasets import load_dataset

dataset = load_dataset("imagefolder", data_dir="dataset", split="train")
dataset.push_to_hub("Harshnigm/puzzles-for-vision-llm")
# print(dataset[0]["instructions"])