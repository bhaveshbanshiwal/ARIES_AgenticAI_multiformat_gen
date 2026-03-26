import os
import json
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

# Get the ngrok URL you saved in .env
agent_url = os.getenv("AGENT_PUBLIC_URL")

if not agent_url:
    print("Error: AGENT_PUBLIC_URL not found in .env")
    exit(1)

# Read the existing AgentCard.json
with open("AgentCard.json", "r") as file:
    card_data = json.load(file)

# Update the URL
card_data["url"] = agent_url

# Save it back to the file
with open("AgentCard.json", "w") as file:
    json.dump(card_data, file, indent=2)

print(f"Successfully updated AgentCard.json with URL: {agent_url}")