import random
import json
import torch
import openai
import requests
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from model import NeuralNet
from nltk_utils import tokenize, bag_of_words
from database_manager import update_database

openai.api_key = "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"  # Replace with actual key

# Global user context dictionary
user_context = {}

def query_openai_api(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error querying OpenAI API: {e}")
        return "Sorry, I couldn't process your request using OpenAI."

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_api():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

def create_google_calendar_event(summary, start_time, end_time, description=None):
    try:
        service = authenticate_google_api()
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'UTC'},
            'end': {'dateTime': end_time, 'timeZone': 'UTC'},
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        print(f"Error creating Google Calendar event: {e}")
        return "Sorry, I couldn't create the event in Google Calendar."

# Load intents and model data
with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

data = torch.load("data.pth")
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data["all_words"]
tags = data["tags"]

model = NeuralNet(input_size, hidden_size, output_size)
model.load_state_dict(data["model_state"])
model.eval()

def classify_intent(sentence):
    bag = bag_of_words(tokenize(sentence), all_words)
    bag = torch.from_numpy(bag).unsqueeze(0)
    output = model(bag)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    return tag if prob.item() > 0.3 else None

def generate_custom_marketing_tips(business_type, business_scale):
    # Specific cases for common business types and scales
    if "restaurant" in business_type.lower():
        if "startup" in business_scale.lower():
            return f"For a {business_scale} {business_type}, start with local SEO, Google My Business, and food influencers."
        elif "small" in business_scale.lower():
            return f"For a small {business_type}, run local social ads, add online reservations, and loyalty programs."
        else:
            return f"For a large {business_type}, launch regional campaigns, partner with delivery apps, and scale with franchises."
    elif "ecommerce" in business_type.lower():
        if "startup" in business_scale.lower():
            return f"For a {business_scale} {business_type}, use TikTok/Instagram marketing, basic SEO, and influencer giveaways."
        elif "small" in business_scale.lower():
            return f"For a small {business_type}, invest in Shopping Ads, retargeting, and email flows."
        else:
            return f"For a large {business_type}, adopt omnichannel strategies, advanced CRM, and predictive analytics."
    elif "tech" in business_type.lower() and "startup" in business_scale.lower():
        return f"For a tech startup, build thought leadership through content marketing, leverage LinkedIn, participate in industry events, and use targeted PPC campaigns."
    # Generic fallback for any business type/scale
    return (
        f"Thanks for sharing! For a {business_scale} {business_type}, "
        "focus on strong branding, a professional website, and targeted social ads. "
        "If you want more tailored tips, let me know more about your business goals!"
    )

def google_search(query):
    try:
        search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key=YOUR_API_KEY&cx=YOUR_CX_ID"
        response = requests.get(search_url)
        response.raise_for_status()
        results = response.json()

        if "items" in results and len(results["items"]) > 0:
            top_result = results["items"][0]
            title = top_result.get("title", "No title available")
            snippet = top_result.get("snippet", "No snippet available")
            link = top_result.get("link", "No link available")
            return f"{title}: {snippet}\nRead more: {link}"
        else:
            return "Sorry, I couldn't find any relevant information on Google."
    except Exception as e:
        print(f"Error during Google search: {e}")
        return "Sorry, I couldn't perform a Google search at the moment."

def get_response(msg, user_id="default"):
    global user_context

    if user_id not in user_context:
        user_context[user_id] = {"last_question": None, "business_type": None, "business_scale": None}

    ctx = user_context[user_id]

    # Handle context-based responses first
    if ctx["last_question"] == "ask_business_type":
        ctx["business_type"] = msg
        ctx["last_question"] = "ask_business_scale"
        response = "Got it! Is your business a startup, small business, medium-sized, or large enterprise?"
        update_database(msg, response)
        return response

    if ctx["last_question"] == "ask_business_scale":
        ctx["business_scale"] = msg
        ctx["last_question"] = None
        response = generate_custom_marketing_tips(ctx["business_type"], ctx["business_scale"])
        update_database(msg, response)
        return response

    # Try intent classification first
    tag = classify_intent(msg)
    if tag:
        # Handle business tips context flow
        if tag in ["business_tips", "marketing_tips_intro"]:
            ctx["last_question"] = "ask_business_type"
            response = "Sure! To give you the best marketing tips, can you tell me what type of business you have? (e.g., education, restaurant, retail, etc.)"
            update_database(msg, response)
            return response
        if tag == "business_type_response":
            ctx["business_type"] = msg
            ctx["last_question"] = "ask_business_scale"
            response = "Thanks! And what is the scale of your business? (startup, small, medium, or large)"
            update_database(msg, response)
            return response
        if tag == "business_scale_response":
            ctx["business_scale"] = msg
            ctx["last_question"] = None
            response = generate_custom_marketing_tips(ctx["business_type"], ctx["business_scale"])
            update_database(msg, response)
            return response
        # Check for matching intent
        for intent in intents['intents']:
            if tag == intent['tag']:
                response = random.choice(intent['responses'])
                update_database(msg, response)
                return response

    # Check for calendar-related queries
    if "calendar" in msg.lower():
        try:
            response = create_google_calendar_event(
                summary="Sample Event",
                start_time="2025-05-01T10:00:00Z",
                end_time="2025-05-01T11:00:00Z",
                description="This is a sample event created by the chatbot."
            )
            update_database(msg, response)
            return response
        except Exception as e:
            print(f"Calendar error: {e}")
            # Continue to fallback if calendar fails

    # Try OpenAI as first fallback
    try:
        openai_response = query_openai_api(f"Answer as a marketing assistant: {msg}")
        if openai_response and "Sorry" not in openai_response:
            update_database(msg, openai_response)
            return openai_response
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Continue to next fallback if OpenAI fails

    # Try Google search as final fallback
    try:
        search_response = google_search(msg)
        if search_response:
            update_database(msg, search_response)
            return search_response
    except Exception as e:
        print(f"Google search error: {e}")

    # If all fallbacks fail, return a default response
    default_response = "I apologize, but I'm having trouble processing your request. Could you please rephrase your question or try asking something else?"
    update_database(msg, default_response)
    return default_response

def main():
    print("Welcome to the Chatbot! How can I assist you today?")
    print("Type 'quit' to exit.")
    while True:
        msg = input("You: ")
        if msg.lower() == "quit":
            print("Goodbye!")
            break
        response = get_response(msg)
        print(f"Bot: {response}")

if __name__ == "__main__":
    main()