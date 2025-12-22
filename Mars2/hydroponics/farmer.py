import sys

sys.path.append(".")

import sicc as ic
from hydroponics.constants import (
    HARVEST_DROP_STATION,
    NUM_PLANTERS,
    PLANTER_STATIONS,
    SEED_PICKUP_STATION,
)

daylight_sensor = ic.d0
occupancy_sensor = ic.d1
larre_pin = ic.d2

MINUTES_IN_LIGHT = 12.5
DEGREES_PER_MINUTE = 18
DEGREES_PER_DAY = DEGREES_PER_MINUTE * MINUTES_IN_LIGHT
HALF_LIGHT_BUDGET = DEGREES_PER_DAY / 2


@ic.subr
def handle_lights():
    ic.devices.GrowLight().On = daylight_sensor.SolarAngle < HALF_LIGHT_BUDGET
    ic.devices.LightLongAngled().On = occupancy_sensor.Activate
    ic.devices.LightLongWide().On = occupancy_sensor.Activate


class LarreState(ic._api.EnumEx):
    PLANTING = 0
    HARVESTING_SEED = 1
    HARVESTING_CROP = 2


@ic.dataclasses.dataclass
class Larre:
    device: ic.Pin
    control: ic.devices.LarreDockHydroponics
    state: ic.Int = LarreState.PLANTING.value

    @ic.subr
    def wait_until_idle(self):
        with ic.while_(lambda: ~self.device.Idle):
            handle_lights()
            ic.yield_()

    @ic.subr
    def move(self, station: ic.Int):
        self.control.Setting = station
        self.wait_until_idle()

    @ic.subr
    def act(self):
        self.control.Activate = True
        self.wait_until_idle()

    @ic.subr
    def can_do_action(self) -> ic.Bool:
        """
        Go through all planter stations and check if all are in the same growth stage
        """
        num_stations_pending = NUM_PLANTERS

        for station in PLANTER_STATIONS:
            self.move(station)
            with ic.if_(
                (
                    (self.state == LarreState.PLANTING.value)
                    & ~self.control.slots[255]["Occupied"]
                )
                | (
                    (self.state == LarreState.HARVESTING_SEED.value)
                    & self.control.slots[255]["Occupied"]
                    & self.control.slots[255]["Seeding"]
                )
                | (
                    (self.state == LarreState.HARVESTING_CROP.value)
                    & self.control.slots[255]["Occupied"]
                    & self.control.slots[255]["Mature"]
                    & ~self.control.slots[255]["Seeding"]
                )
            ):
                num_stations_pending -= 1

        return num_stations_pending == 0

    @ic.subr
    def run(self):
        with ic.loop():
            with ic.if_(~self.can_do_action()):
                ic.continue_()

            with ic.if_(self.state == LarreState.PLANTING.value):
                self.move(SEED_PICKUP_STATION)
                self.act()
                for station in PLANTER_STATIONS:
                    self.move(station)
                    self.act()

            with ic.if_(self.state == LarreState.HARVESTING_SEED.value):
                for station in PLANTER_STATIONS:
                    self.move(station)
                    with ic.while_(lambda: self.control.slots[255]["Seeding"]):
                        self.act()
                self.move(HARVEST_DROP_STATION)
                self.act()

            with ic.if_(self.state == LarreState.HARVESTING_CROP.value):
                for station in PLANTER_STATIONS:
                    self.move(station)
                    with ic.while_(lambda: self.control.slots[255]["Occupied"]):
                        self.act()
                self.move(HARVEST_DROP_STATION)
                self.act()

            self.state = (self.state + 1) % 3


@ic.program
def main():
    larre = Larre(larre_pin, ic.devices.LarreDockHydroponics())
    larre.run()


if __name__ == "__main__":
    main.cli()
