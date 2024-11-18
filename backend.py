import requests
from traceback import format_exc
from openai import OpenAI
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Annotated
from dotenv import load_dotenv
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

def get_posts(place):
    city = place
    city = city.replace("+", "%2b")
    city = city.replace(" ", "+")

    url = f'https://api.weatherapi.com/v1/current.json'
    key = f"{os.getenv('WEATHER_API_KEY')}"
    try:
        response = requests.post(f'{url}?key={key}&q={city}&days=1&aqi=no&alerts=no')

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException:
        print(format_exc())
        return None

def check(place):
    posts = get_posts(place)
    if posts:
        return posts
    else:
        print('Failed')

def getWeatherReport(place):
    weather_data = check(place)

    client = OpenAI(base_url="https://jamsapi.hackclub.dev/openai/")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. You will be provided an JSON output of a weather report. Could you please make this a report, but phrase it in a passive agressive or just plain agressive tone to piss the reader off? You are required to mention the location's name. If you can insult the location with specific place details that is even better, but do not feel pressured to. Make sure to mention all temperatures in both Farenheight and Celsius. If there is no JSON data, do not make a weather report and just output \'Sorry, we broke!\'. Do not use emojis."},
            {
                "role": "user",
                "content": str(weather_data)
            }
        ]
    )
    return completion.choices[0].message

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Process the request
        response = await call_next(request)
        
         # Check if the status is 404 and the URL contains "wp-"
        if response.status_code == 404 and "wp-" in str(request.url.path):
            # Check if bomb.zstd file exists
            bomb_file_path = "bomb.zstd"
            if not os.path.exists(bomb_file_path):
                # Return a 404 if the file is not found
                return Response("File not found", status_code=404)
            
            # Serve the bomb.zstd file as is
            with open(bomb_file_path, "rb") as f:
                bomb_content = f.read()

            # Prepare custom response with bomb.zstd content and appropriate headers
            custom_response = Response(
                content=bomb_content,
                status_code=200,
                headers={
                    'Content-Encoding': 'zstd',  # Indicate the file is zstd compressed
                    'Content-Type': 'application/octet-stream',  # Generic MIME type for binary files
                }
            )
            return custom_response

        # If no conditions are met, return the original response
        return response

app = FastAPI()

origins = [
    "http://neko.hackclub.app",
    "https://neko.hackclub.app",
    "http://localhost",
    "http://localhost:41181",
    "https://api.neko.hackclub.app"
]

app.add_middleware(CustomMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get-weather")
async def weather(place: Annotated[str, Form()]):
    return getWeatherReport(place)

@app.get("/wp-example")
async def wp_example():
    return {"message": "WordPress related path"}