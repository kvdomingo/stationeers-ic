from itertools import chain

import sicc as ic

daylight_sensor = ic.d0
occupancy_sensor = ic.d1
larre_pin = ic.d2

MINUTES_IN_LIGHT = 12.5
DEGREES_PER_MINUTE = 18
DEGREES_PER_DAY = DEGREES_PER_MINUTE * MINUTES_IN_LIGHT
HALF_LIGHT_BUDGET = DEGREES_PER_DAY / 2

PLANTER_STATION_ROW_1_START = 8
PLANTER_STATION_ROW_1_END = 12
PLANTER_STATION_ROW_2_START = 1
PLANTER_STATION_ROW_2_END = 5
PLANTER_STATIONS = list(
    chain(
        range(PLANTER_STATION_ROW_1_START, PLANTER_STATION_ROW_1_END + 1),
        range(PLANTER_STATION_ROW_2_START, PLANTER_STATION_ROW_2_END + 1),
    )
)
NUM_PLANTERS = len(PLANTER_STATIONS)
HARVEST_DROP_STATION = 6
SEED_PICKUP_STATION = 7


@ic.subr
def handle_lights():
    ic.devices.GrowLight().On = daylight_sensor.SolarAngle < HALF_LIGHT_BUDGET
    ic.devices.LightLongAngled().On = occupancy_sensor.Activate
    ic.devices.LightLongWide().On = occupancy_sensor.Activate


class LarreState(ic._api.EnumEx):
    PLANTING = 0
    GROWING = 1
    HARVESTING_SEED = 2
    HARVESTING_CROP = 3


@ic.dataclasses.dataclass
class Larre:
    device: ic.Pin
    station: ic.Int = 0
    state: LarreState = LarreState.PLANTING

    @ic.subr
    def wait_until_idle(self):
        with ic.while_(lambda: ~self.device.Idle):
            handle_lights()
            ic.yield_()

    @ic.subr
    def move(self, station: ic.Int):
        self.station = station
        self.device.Setting = station
        self.wait_until_idle()

    @ic.subr
    def act(self):
        self.device.Activate = True
        self.wait_until_idle()

    @ic.subr
    def can_do_next_step(self) -> ic.Bool:
        """
        Go through all planter stations and check if all are in the same growth stage
        """
        num_stations_pending = NUM_PLANTERS

        for station in PLANTER_STATIONS:
            self.move(station)
            with ic.if_(
                (
                    (self.state == LarreState.PLANTING)
                    & (~self.device.slots[255]["Occupied"])
                )
                | (
                    (self.state == LarreState.GROWING)
                    & (~self.device.slots[255]["Seeding"])
                )
                | (
                    (self.state == LarreState.HARVESTING_SEED)
                    & (self.device.slots[255]["Mature"])
                )
                | (
                    (self.state == LarreState.HARVESTING_CROP)
                    & (self.device.slots[255]["Occupied"])
                )
            ):
                num_stations_pending -= 1

        _can_do_next_step = num_stations_pending == 0
        with ic.if_(_can_do_next_step):
            self.state = LarreState((self.state.value + 1) % len(LarreState))

        return _can_do_next_step

    @ic.subr
    def run(self):
        with ic.loop():
            _current_state = self.state

            with ic.if_(_current_state == LarreState.PLANTING):
                with ic.if_(self.can_do_next_step()):
                    self.move(SEED_PICKUP_STATION)
                    self.act()
                    for station in PLANTER_STATIONS:
                        self.move(station)
                        self.act()

            with ic.if_(_current_state == LarreState.GROWING):
                self.can_do_next_step()

            with ic.if_(_current_state == LarreState.HARVESTING_SEED):
                with ic.if_(self.can_do_next_step()):
                    for station in PLANTER_STATIONS:
                        self.move(station)
                        with ic.while_(lambda: self.device.slots[255]["Seeding"]):
                            self.act()

                    self.move(HARVEST_DROP_STATION)
                    self.act()

            with ic.if_(_current_state == LarreState.HARVESTING_CROP):
                with ic.if_(self.can_do_next_step()):
                    for station in PLANTER_STATIONS:
                        self.move(station)
                        with ic.while_(lambda: self.device.slots[255]["Occupied"]):
                            self.act()

                    self.move(HARVEST_DROP_STATION)
                    self.act()


@ic.program
def main():
    larre = Larre(larre_pin)
    larre.run()


if __name__ == "__main__":
    main.cli()
