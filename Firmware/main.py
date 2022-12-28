# Control for instant/tankless water heater

# GP0: Triac1
# GP1: (Triac2)
# GP2: ZCD1
# GP3: (ZCD2)
# GP6: A rotary encode
# GP7: B rotary encode
# GP8: Push rotary encode
# GP20/21: I²C
# GP22: Flow 0..13
# GP26: Temperature out
# GP27: Temperature in
# Vref = external

from machine import Pin
from machine import ADC
from time import sleep

patterns = [0b00000000000000000000000000000000,  #  0
            0b10000000000000000000000000000000,  #  1
            0b10000000000000001000000000000000,  #  2
            0b10000000000100000000001000000000,  #  3
            0b10000000100000001000000010000000,  #  4
            0b10000010000010000001000001000000,  #  5
            0b10000100001000001000010000010000,  #  6
            0b10001000010001000010001000010000,  #  7
            0b10001000100010001000100010001000,  #  8
            0b10001001000100100010010001001000,  #  9
            0b10010010001001001001001000100100,  # 10
            0b10010010010010100100100100100100,  # 11
            0b10010100100100101001001010010010,  # 12
            0b10100101001010100101001010010100,  # 13
            0b10010101010010101001010100101010,  # 14
            0b10100101010101010101010010101010,  # 15
            0b10101010101010101010101010101010,  # 16
            0b01011010101010101010101101010101,  # 17
            0b01101010101101010110101011010101,  # 18
            0b01011010110101011010110101101011,  # 19
            0b01101011011011010110110101101101,  # 20
            0b01101101101101011011011011011011,  # 21
            0b01101101110110110110110111011011,  # 22
            0b01110110111011011101101110110111,  # 23
            0b01110111011101110111011101110111,  # 24
            0b01110111101110111101110111101111,  # 25
            0b01111011110111110111101111101111,  # 26
            0b01111101111101111110111110111111,  # 27
            0b01111111011111110111111101111111,  # 28
            0b01111111111011111111110111111111,  # 29
            0b01111111111111110111111111111111,  # 30
            0b01111111111111111111111111111111,  # 31
            0b11111111111111111111111111111111]  # 32

_gate = Pin(0, Pin.OUT)       # gate of power triac: 0 = on
_zerocross = Pin(2, Pin.IN)   # 0 = mains zero crossing right now
_flow = Pin(22, Pin.IN)       # water flow pulses 660 pulses/l
temp_out = ADC(26)            # optional ADC for output temperature (not used for control reasons)
temp_in = ADC(27)             # ADC for input temperature

Ttarget = 41                  # Target temperature
BoostTime = 1000              # Time for boost (100%) when water starts flowing to heat up the pipe quickly

_gate.value(1)  # inactive
cycle = 1       # pattern bit counter
power = 0       # values from 0 oo32 (no heat) to 32 oo32 (full power)
TinLP = 0       # temperature LP filter (32 values)
ToutLP = 0
Wflow = 0       # Water flow counter
flowcnt = 0
standbycnt = 990  # idle time up counter; counts time of no water consumption in 32/f (f=50Hz in Europe) steps till 1000
boost = 0       # boost time down counter

def callback(_flow):
    global flowcnt
    flowcnt += 1

_flow.irq(trigger=Pin.IRQ_FALLING, handler=callback)

while True:
    cycle -= 1
    if cycle == 0:  # every 0.64s (50Hz mains) or 0.5s (60Hz mains)
        cycle = 32  # bit pattern has 32 bits
        
        # calculate temperature [°C]
        temp = 0x10000 - (ToutLP >> 5)                          # >> 5: temperature LP filter (32 values)
        Tout = 16.6 + temp / 1390 + temp * temp / 116000000     # formular evaluated by LibreOffice Calc
        temp = 0x10000 - (TinLP >> 5)                           # >> 5: temperature LP filter (32 values)
        Tin  = 16.6 + temp / 1390 + temp * temp / 116000000     # formular evaluated by LibreOffice Calc

        TinLP = 0       # reinit LP filter and water flow counter
        ToutLP = 0
        Wflow = flowcnt
        flowcnt = 0

        if Wflow == 0:  # no water consumption
            boost = 0
            if standbycnt < BoostTime:
                standbycnt += 1
        else:  # water is flowing
            if boost > 0:
                boost -= 1
            if standbycnt != 0:  # water just started to flow
                boost = int((Ttarget - Tin) * standbycnt / 300)  # calculate boost time
                standbycnt = 0

        power = int(Wflow * (Ttarget - Tin) / 7)  # water heating formula
        if power < 0:
            power = 0
        if power > 32:  # limit must be 64 for 3-phase heater with 2 triacs!
            power = 32

        print (Tout, Tin, Wflow, power, standbycnt, boost)

    while _zerocross.value() == 1:    # wait for mains voltage zero crossing
        pass

    if (patterns[power & 0x1f] & (1 << (cycle - 1))) != 0 or boost > 0:
        _gate.value(0)   # trigger triac for the next half wave (10ms)
#    if power > 32:  # only for 3-phase heater with 2 triacs!
#        _gate2.value(0)   # trigger triac for the next half wave (10ms)

    ToutLP += temp_out.read_u16()  # blue/green wires
    TinLP += temp_in.read_u16()    # white/gray wires

    sleep(.003)          # trigger for 3ms

    _gate.value(1)       # release trigger
#    _gate2.value(1)      # release trigger only for 3-phase heater with 2 triacs!





