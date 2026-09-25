from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

client = OpenAI()

import requests

def test_weather(location):
    # Dynamically append the location variable to the URL path
    url = f"https://wttr.in/{location}"
    print(f"DEBUG: Connecting to exactly: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text  # Return the text so your print() statement can display it
        else:
            return f"Server error code: {response.status_code}"
    except Exception as e:
        return f"Network error details: {str(e)}"

def main():
    user_query = input("> ")
    response = client.chat.completions.create(
        model="gpt-5",  
        messages=[
            {"role": "user", "content": user_query}
        ]
    )

    print(f"🤖: {response.choices[0].message.content}") 


print(test_weather("goa"))
