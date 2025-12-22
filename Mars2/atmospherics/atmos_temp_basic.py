import sicc as ic

gas_sensor = ic.d0

ABS_ZERO = 273.15
MIN_TEMP_C = 18
TARGET_TEMP_C = 21
MAX_TEMP_C = 24
MIN_TEMP = ABS_ZERO + MIN_TEMP_C
TARGET_TEMP = ABS_ZERO + TARGET_TEMP_C
MAX_TEMP = ABS_ZERO + MAX_TEMP_C


@ic.program
def main():
    with ic.loop():
        ic.yield_()

        with ic.if_(gas_sensor.Temperature < MIN_TEMP):
            ic.devices.WallHeater().On = True
        with ic.if_(gas_sensor.Temperature <= TARGET_TEMP):
            ic.devices.WallCooler().On = False
        with ic.if_(gas_sensor.Temperature >= TARGET_TEMP):
            ic.devices.WallHeater().On = True
        with ic.if_(gas_sensor.Temperature > MAX_TEMP):
            ic.devices.WallCooler().On = False


if __name__ == "__main__":
    main.cli()
