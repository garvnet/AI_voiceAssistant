import os
from dotenv import load_dotenv
load_dotenv()

import speech_recognition as sr
import webbrowser
import datetime
import requests
import openai
from elevenlabs import text_to_speech, play

openai.api_key = os.getenv("OPENAI_API_KEY")

# Text-to-speech using ElevenLabs

def say(text):
    print(f"Gavi: {text}")
    audio = text_to_speech.text_to_speech(text=text, voice="Rachel")  # change voice as you want
    play(audio)

# Voice command recognition

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
        try:
            print("🧠 Recognizing...")
            return r.recognize_google(audio, language='en-in').lower()
        except:
            say("Sorry, I didn't catch that.")
            return ""

# Handle website commands

def handle_sites(query):
    sites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com"
    }
    for name, url in sites.items():
        if f"open {name}" in query:
            say(f"Opening {name}")
            webbrowser.open(url)
            return True
    if "youtube search" in query:
        terms = query.replace("youtube search", "").strip()
        say(f"Searching YouTube for {terms}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={terms.replace(' ','+')}")
        return True
    return False

# Handle time queries

def handle_time(query):
    if "time" in query:
        say(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
        return True
    return False

# Handle system commands

def handle_system(query):
    if "open code" in query:
        say("Opening Visual Studio Code")
        os.system("open -a 'Visual Studio Code'")
        return True
    if "close window" in query:
        say("Closing window")
        os.system("osascript -e 'tell application \"System Events\" to keystroke \"w\" using command down'")
        return True
    return False

# Handle weather queries

def handle_weather(query):
    if "weather" in query:
        city = "New Delhi,IN"
        key = os.getenv("OPENWEATHER_API_KEY")
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={key}").json()
        if "weather" not in r or "main" not in r:
            say("Sorry, I couldn't get the weather. Check your API key or network.")
            return True
        desc = r["weather"][0]["description"]
        temp = r["main"]["temp"]
        rain = r.get("rain", {}).get("1h", 0)
        say(f"It's {temp}°C with {desc}. Rain in last hour: {rain} mm.")
        if temp < 20:
            say("It's a bit chilly, take a jacket.")
        elif rain == 0:
            say("No rain right now. Good time for walk.")
        else:
            say("Might rain—carry an umbrella.")
        return True
    return False

# Handle AI chat

def handle_ai(query):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}]
    )
    say(response.choices[0].message.content)
    return True

if __name__ == "__main__":
    say("Gavi is online")
    while True:
        cmd = takeCommand()
        if not cmd:
            continue
        if any([
            handle_sites(cmd),
            handle_time(cmd),
            handle_system(cmd),
            handle_weather(cmd),
        ]):
            continue
        else:
            handle_ai(cmd)
