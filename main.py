import os
import json
import time
import requests
from datetime import datetime, timedelta
import pyttsx3
import speech_recognition as sr
from plyer import notification

# API Keys (replace with your own keys)
WEATHER_API_KEY = "your_openweathermap_api_key"
NEWS_API_KEY = "your_newsapi_api_key"

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Speed of speech
engine.setProperty("volume", 0.9)  # Volume (0.0 to 1.0)

# Reminder storage
REMINDERS_FILE = "reminders.json"


def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()


def listen():
    """Capture audio input from the user."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            return command
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand that.")
            return ""
        except sr.WaitTimeoutError:
            speak("You didn't say anything. Please try again.")
            return ""


def set_reminder():
    """Set a new reminder."""
    speak("What should I remind you about?")
    reminder_text = listen()
    if reminder_text:
        speak("When should I remind you? Please say the time in minutes.")
        try:
            minutes = int(listen())
            reminder_time = datetime.now() + timedelta(minutes=minutes)
            reminder = {"text": reminder_text, "time": reminder_time.strftime("%Y-%m-%d %H:%M:%S")}
            save_reminder(reminder)
            speak(f"Reminder set for {minutes} minutes from now.")
        except ValueError:
            speak("I couldn't understand the time. Please try again.")
    else:
        speak("No reminder text provided.")


def save_reminder(reminder):
    """Save reminders to a file."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as file:
            reminders = json.load(file)
    else:
        reminders = []
    reminders.append(reminder)
    with open(REMINDERS_FILE, "w") as file:
        json.dump(reminders, file)


def check_reminders():
    """Check and notify reminders."""
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "r") as file:
            reminders = json.load(file)
        now = datetime.now()
        remaining_reminders = []
        for reminder in reminders:
            reminder_time = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")
            if reminder_time <= now:
                notification.notify(
                    title="Reminder",
                    message=reminder["text"],
                    timeout=10
                )
                speak(f"Reminder: {reminder['text']}")
            else:
                remaining_reminders.append(reminder)
        with open(REMINDERS_FILE, "w") as file:
            json.dump(remaining_reminders, file)


def get_weather():
    """Fetch and announce the weather."""
    speak("Which city's weather would you like to know?")
    city = listen()
    if city:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()
        if response.get("cod") == 200:
            weather = response["weather"][0]["description"]
            temp = response["main"]["temp"]
            speak(f"The weather in {city} is {weather} with a temperature of {temp} degrees Celsius.")
        else:
            speak("I couldn't fetch the weather for that city. Please try again.")
    else:
        speak("No city provided.")


def get_news():
    """Fetch and announce the news headlines."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get("status") == "ok":
        articles = response.get("articles", [])[:5]
        speak("Here are the top 5 news headlines.")
        for i, article in enumerate(articles, 1):
            speak(f"Headline {i}: {article['title']}")
    else:
        speak("I couldn't fetch the news at the moment.")


def main():
    """Main function to run the assistant."""
    while True:
        speak("How can I help you? You can ask me to set a reminder, check the weather, or read the news.")
        command = listen()
        if "reminder" in command:
            set_reminder()
        elif "weather" in command:
            get_weather()
        elif "news" in command:
            get_news()
        elif "exit" in command or "quit" in command:
            speak("Goodbye!")
            break
        else:
            speak("I didn't understand that. Please try again.")
        check_reminders()
        time.sleep(1)


if __name__ == "__main__":
    main()
