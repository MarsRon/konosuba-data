# Create a dataset to fine-tune Llama-3.2 3B model
# using the dialogues from konosuba-dialogue.txt
# 
# The data consists of:
# [
#   [user: 1st line, assistant: 2nd line],
#   [user: 2nd line, assistant: 3rd line],
#   [user: 3rd line, assistant: 4th line],
# ]
# And so on.

import csv, json, re

def clean_text(text: str) -> str:
  """
  Cleans the input text by replacing various unicode characters with their
  ASCII equivalents or common representations, and removes the trailing newline.

  Args:
      text (str): The text to be cleaned.

  Returns:
      str: The cleaned text with specific unicode characters replaced and
      trailing newline removed.
  """
  text = re.sub(r'\u201C|\u201D', '"', text)
  text = re.sub(r'\u2018|\u2019', "'", text)
  text = re.sub(r'\u2011|\u2013|\u2014|\u2500|\u30FC', '-', text)
  text = (text.replace('\u2026', '...')
              .replace('\u00e9', 'e')
              .replace('\u00ef', 'i')
              .replace('\u014d', 'o')
              .replace('\uff01', '!')
              .replace('\u00b7', '.')
              .replace('\u2020', '+')
              .replace('\u2642', 'O->')
              .replace('\u2764', '<3')
              .replace('\u00a0', ' ')
              .replace('  ', ' '))
  text = text[:-1] # Remove \n
  return text

def get_dataset(dialogue_path: str) -> list[tuple[str, str]]:
  """
  Reads the dialogue from the given text file and creates a dataset out of it.

  The dataset consists of a list of tuples, where the first element of the tuple
  is the user dialogue and the second element is the assistant dialogue.

  Args:
      dialogue_path (str): The path to the text file containing the dialogue.

  Returns:
      list[tuple[str, str]]: The dataset created from the dialogue.
  """
  with open(dialogue_path) as f:
    lines = f.readlines()

  # Create dataset
  dataset = []
  for i in range(len(lines)-2):
    # The user dialogue is the first line of the pair
    user = clean_text(lines[i])
    # The assistant dialogue is the second line of the pair
    assistant = clean_text(lines[i+1])
    # Create a tuple of the user and assistant dialogues
    data = (user, assistant)
    # Append the tuple to the dataset
    dataset.append(data)

  return dataset

def save_csv(file_path: str, dataset: list[tuple[str, str]]):
  """
  Saves the given dataset to the given CSV file path.

  The dataset is modified to include a header row with column names 'user' and
  'assistant'.

  Args:
      file_path (str): The path to the file to save the dataset to.
      dataset (list[tuple[str, str]]): The dataset to save to the file.
  """
  dataset_csv = dataset.copy()
  dataset_csv.insert(0, ('user', 'assistant'))

  with open(file_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(dataset_csv)

def save_json(file_path: str, dataset: list[tuple[str, str]], pretty_print: bool = False):
  """
  Saves the given dataset to the given JSON file path.

  Args:
      file_path (str): The path to the file to save the dataset to.
      dataset (list[tuple[str, str]]): The dataset to save to the file.
      pretty_print (bool, optional): Whether to format the JSON with indentation. Defaults to False.
  """
  dataset_json = [
    {
      'conversations': (
        { 'role': 'user', 'content': data[0] },
        { 'role': 'assistant', 'content': data[1] }
      )
    }
    for data in dataset
  ]

  if pretty_print:
    dataset_json_str = json.dumps(dataset_json, indent=2)
  else:
    dataset_json_str = json.dumps(dataset_json, separators=(',', ':'))

  with open(file_path, 'w') as f:
    f.write(dataset_json_str)


if __name__ == '__main__':
  dataset = get_dataset('./konosuba-dialogue.txt')
  print(f"Dataset size: {len(dataset)}")
  save_json('./konosuba-dataset.json', dataset)
  # save_csv('./konosuba-dataset.csv', dataset)
  # save_json('./konosuba-dataset-pretty.json', dataset, pretty_print=True)
