import sicc as ic
from scipy.constants import zero_Celsius

gas_sensor = ic.d0

ABS_ZERO = zero_Celsius
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
        temperature = gas_sensor.Temperature

        with ic.if_(temperature < MIN_TEMP):
            ic.devices.WallHeater().On = True
        with ic.if_(temperature <= TARGET_TEMP):
            ic.devices.WallCooler().On = False
        with ic.if_(temperature >= TARGET_TEMP):
            ic.devices.WallHeater().On = False
        with ic.if_(temperature > MAX_TEMP):
            ic.devices.WallCooler().On = True


if __name__ == "__main__":
    main.cli()
