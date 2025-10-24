# coffin_nap_timer.py
import datetime
import threading
import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# ---- Helper Functions ----

def get_sunset_time(lat, lon):
    """Fetch sunset time from a public API (e.g. Sunrise-Sunset.org)."""
    url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0"
    resp = requests.get(url)
    data = resp.json()
    sunset_utc = datetime.datetime.fromisoformat(data['results']['sunset'])
    return sunset_utc

def get_time_until_sunset(lat, lon, offset_minutes=10):
    """Return timedelta until (sunset - offset)."""
    sunset = get_sunset_time(lat, lon)
    now = datetime.datetime.utcnow()
    wake_time = sunset - datetime.timedelta(minutes=offset_minutes)
    delta = wake_time - now
    return delta if delta.total_seconds() > 0 else datetime.timedelta(seconds=0)

def play_alarm():
    sound = SoundLoader.load('bat_wings.wav')  # use your own spooky sound file
    if sound:
        sound.play()

def start_timer(seconds):
    """Runs a background thread that sleeps until time to wake."""
    def run():
        time.sleep(seconds)
        play_alarm()
    threading.Thread(target=run, daemon=True).start()

# ---- Kivy UI ----

class CoffinTimerLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.add_widget(Label(text="🦇 Coffin Nap Timer 🦇", font_size='24sp'))
        self.lat_input = TextInput(hint_text="Enter latitude", multiline=False)
        self.lon_input = TextInput(hint_text="Enter longitude", multiline=False)
        self.add_widget(self.lat_input)
        self.add_widget(self.lon_input)

        self.status = Label(text="Awaiting your coordinates, dark one...")
        self.add_widget(self.status)

        self.start_btn = Button(text="Set Coffin Nap", on_press=self.set_timer)
        self.add_widget(self.start_btn)

    def set_timer(self, instance):
        try:
            lat = float(self.lat_input.text)
            lon = float(self.lon_input.text)
        except ValueError:
            self.status.text = "Invalid coordinates. Even immortals need numbers."
            return

        delta = get_time_until_sunset(lat, lon)
        minutes = int(delta.total_seconds() // 60)
        self.status.text = f"Your alarm is set for {minutes} minutes from now..."
        start_timer(delta.total_seconds())

class CoffinNapTimerApp(App):
    def build(self):
        return CoffinTimerLayout()

if __name__ == '__main__':
    CoffinNapTimerApp().run()
