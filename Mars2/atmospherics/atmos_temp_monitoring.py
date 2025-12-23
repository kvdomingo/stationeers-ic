import sicc as ic

gas_sensor = ic.d0
temp_display = ic.d1
pct_o2_display = ic.d2
pct_n2_display = ic.d3
pct_co2_display = ic.d4
pressure_display = ic.d5

ABS_ZERO = 273.15
MIN_TEMP_C = 18
TARGET_TEMP_C = 21
MAX_TEMP_C = 24
MIN_TEMP = ABS_ZERO + MIN_TEMP_C
TARGET_TEMP = ABS_ZERO + TARGET_TEMP_C
MAX_TEMP = ABS_ZERO + MAX_TEMP_C

DISPLAY_MODE_PERCENT = 1
DISPLAY_MODE_TEMPERATURE = 4
DISPLAY_MODE_PRESSURE = 14


@ic.program
def main():
    temp_display.Mode = DISPLAY_MODE_TEMPERATURE
    pressure_display.Mode = DISPLAY_MODE_PRESSURE
    pct_o2_display.Mode = DISPLAY_MODE_PERCENT
    pct_n2_display.Mode = DISPLAY_MODE_PERCENT
    pct_co2_display.Mode = DISPLAY_MODE_PERCENT

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

        pressure_kPa = gas_sensor.Pressure

        temp_display.Setting = gas_sensor.Temperature - ABS_ZERO
        pressure_display.Setting = pressure_kPa * 1000
        pct_o2_display.Setting = gas_sensor.RatioOxygen
        pct_n2_display.Setting = gas_sensor.RatioNitrogen
        pct_co2_display.Setting = gas_sensor.RatioCarbonDioxide


if __name__ == "__main__":
    main.cli()
