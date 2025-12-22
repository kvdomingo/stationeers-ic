from typing import cast

import sicc as ic

sensor = cast(ic.devices.DaylightSensor, ic.d0)

panels = ic.devices.SolarPanelDualReinforced()


@ic.program
def main():
    with ic.loop():
        ic.yield_()
        sensor.Mode = 1

        raw_vertical = sensor.Vertical
        raw_horizontal = sensor.Horizontal

        panels.Vertical = (90 - raw_vertical) % 360
        panels.Horizontal = (raw_horizontal - 90) % 360


if __name__ == "__main__":
    main.cli()
