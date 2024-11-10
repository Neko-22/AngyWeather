import requests
from traceback import format_exc
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

def get_posts(place):
    city = place
    city = city.replace("+", "%2b")
    city = city.replace(" ", "+")

    url = f'https://api.weatherapi.com/v1/current.json'
    key = f"{os.environ.get('WEATHER_API_KEY')}"
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

app = FastAPI()

origins = [
    "http://neko.hackclub.app/AngyWeather/site.html",
    "https://neko.hackclub.app/AngyWeather/site.html",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-weather")
def weather(place: str):
    return getWeatherReport(place)