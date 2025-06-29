import torch
import torch.nn as nn
import os
import json
import time
import subprocess


class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size) 
        self.l2 = nn.Linear(hidden_size, hidden_size) 
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
    
    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        return out


class FeedbackLoop:
    def __init__(self, intents_file, logs_file, model_file, retrain_script):
        self.intents_file = intents_file
        self.logs_file = logs_file
        self.model_file = model_file
        self.retrain_script = retrain_script
        self.last_retrain_time = time.time()

    def log_interaction(self, user_message, bot_response):
        """Log user interactions for future learning."""
        log_entry = {"user_message": user_message, "bot_response": bot_response}
        with open(self.logs_file, "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")

    def update_knowledge_base(self):
        """Update the intents file dynamically from interaction logs."""
        try:
            with open(self.logs_file, "r") as log_file:
                logs = [json.loads(line) for line in log_file]

            with open(self.intents_file, "r", encoding="utf-8") as f:
                intents = json.load(f)

            for log in logs:
                user_message = log["user_message"]
                bot_response = log["bot_response"]

                # Check if the user message already exists in intents
                for intent in intents["intents"]:
                    if bot_response in intent["responses"]:
                        if user_message not in intent["patterns"]:
                            intent["patterns"].append(user_message)
                        break
                else:
                    # Create a new intent if no match is found
                    new_intent = {
                        "tag": f"custom_{len(intents['intents']) + 1}",
                        "patterns": [user_message],
                        "responses": [bot_response]
                    }
                    intents["intents"].append(new_intent)

            with open(self.intents_file, "w", encoding="utf-8") as f:
                json.dump(intents, f, indent=4)

            print("Knowledge base updated from logs.")
        except FileNotFoundError:
            print("No interaction logs found. Skipping knowledge base update.")

    def retrain_model(self):
        """Retrain the model periodically."""
        current_time = time.time()
        if current_time - self.last_retrain_time > 86400:  # Retrain every 24 hours
            print("Retraining the model...")
            subprocess.run(["python", self.retrain_script], check=True)
            self.last_retrain_time = current_time
            print("Model retrained successfully.")

if __name__ == "__main__":
    feedback_loop = FeedbackLoop(
        intents_file="intents.json",
        logs_file="interaction_logs.json",
        model_file="intent_model.pth",
        retrain_script="train.py"
    )

    # Log an interaction
    feedback_loop.log_interaction()

    # Update the knowledge base
    feedback_loop.update_knowledge_base()

    # Retrain the model if needed
    feedback_loop.retrain_model()
