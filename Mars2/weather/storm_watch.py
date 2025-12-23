import sys

sys.path.append(".")

from enum import Enum

import sicc as ic
from common.string import to_ascii

WeatherStation = ic.d0
Display = ic.d1
Speaker = ic.d2


class WeatherStationMode(Enum):
    NO_STORM = 0
    STORM_INCOMING = 1
    IN_STORM = 2


class SpeakerMode(Enum):
    ALERT = 17
    STORM_INCOMING = 18


class LEDMode(Enum):
    SECONDS = 7
    MINUTES = 8
    DAYS = 9
    STRING = 10


@ic.subr
def handle_lights():
    ic.devices.LightLongWide().On = ic.devices.OccupancySensor().Activate.max


@ic.program
def main():
    Display.On = True
    Speaker.Volume = 100

    with ic.loop():
        ic.yield_()
        handle_lights()

        with ic.if_(WeatherStation.Mode == WeatherStationMode.NO_STORM.value):
            Speaker.On = False
            Display.Setting = to_ascii("CLEAR")
            Display.Color = ic.Color.Green
            Display.Mode = LEDMode.STRING.value

        with ic.if_(WeatherStation.Mode == WeatherStationMode.STORM_INCOMING.value):
            eta = WeatherStation.NextWeatherEventTime
            Speaker.On = True
            Speaker.Mode = SpeakerMode.STORM_INCOMING.value
            Speaker.SoundAlert = SpeakerMode.STORM_INCOMING.value
            Display.Setting = eta
            Display.Color = ic.Color.Yellow

            with ic.if_(eta < 60):
                Display.Mode = LEDMode.SECONDS.value

            with ic.if_((eta >= 60) & (eta < 1440)):
                Display.Setting = eta / 60
                Display.Mode = LEDMode.MINUTES.value

            with ic.if_(eta >= 1440):
                Display.Setting = eta / 60 / 24
                Display.Mode = LEDMode.DAYS.value

        with ic.if_(WeatherStation.Mode == WeatherStationMode.IN_STORM.value):
            Speaker.On = True
            Speaker.Mode = SpeakerMode.ALERT.value
            Speaker.SoundAlert = SpeakerMode.ALERT.value
            Display.Setting = to_ascii("STORM")
            Display.Color = ic.Color.Red
            Display.Mode = LEDMode.STRING.value
