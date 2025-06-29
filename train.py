import numpy as np
import random
import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from nltk_utils import bag_of_words, tokenize, stem
from model import NeuralNet
from database_manager import update_database  

# --- Update intents from interaction logs (if any) ---
def update_training_data_from_logs():
    try:
        with open("interaction_logs.json", "r") as log_file:
            logs = []
            for line in log_file:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        with open("intents.json", "r", encoding="utf-8") as f:
            intents = json.load(f)

        for log in logs:
            user_message = log.get("user_message")
            bot_response = log.get("bot_response")

            if not user_message or not bot_response:
                continue

            for intent in intents["intents"]:
                if bot_response in intent["responses"]:
                    if user_message not in intent["patterns"]:
                        intent["patterns"].append(user_message)
                    break
            else:
                new_intent = {
                    "tag": f"custom_{len(intents['intents']) + 1}",
                    "patterns": [user_message],
                    "responses": [bot_response]
                }
                intents["intents"].append(new_intent)

        with open("intents.json", "w", encoding="utf-8") as f:
            json.dump(intents, f, indent=4)

        print("Intents updated from logs.")
    except FileNotFoundError:
        print("No interaction logs found. Skipping update.")

# --- Load intents data ---
with open('intents.json', 'r', encoding='utf-8') as f:
    intents = json.load(f)

all_words = []
tags = []
xy = []

for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    for pattern in intent['patterns']:
        w = tokenize(pattern)
        all_words.extend(w)
        xy.append((w, tag))

ignore_words = ['?', '.', '!']
all_words = [stem(w) for w in all_words if w not in ignore_words]
all_words = sorted(set(all_words))
tags = sorted(set(tags))

print(len(xy), "patterns")
print(len(tags), "tags:", tags)
print(len(all_words), "unique stemmed words:", all_words)

# Optional: dynamically update intents from log file
update_training_data_from_logs()

# --- Training data ---
X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    label = tags.index(tag)
    y_train.append(label)

X_train = np.array(X_train)
y_train = np.array(y_train)

# --- Hyperparameters ---
num_epochs = 1000
batch_size = 8
learning_rate = 0.001
input_size = len(X_train[0])
hidden_size = 8
output_size = len(tags)
print(input_size, output_size)

# --- Dataset Class ---
class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    def __len__(self):
        return self.n_samples

# --- Data Loader ---
dataset = ChatDataset()
train_loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

# --- Model, Loss, Optimizer ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = NeuralNet(input_size, hidden_size, output_size).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# --- Train the Model ---
for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.to(dtype=torch.long).to(device)

        outputs = model(words)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

print(f"Final loss: {loss.item():.4f}")

# --- Save Trained Data ---
data = {
    "model_state": model.state_dict(),
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags
}

FILE = "data.pth"
torch.save(data, FILE)

print(f"Training complete. Model saved to {FILE}")