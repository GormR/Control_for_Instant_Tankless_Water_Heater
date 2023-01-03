#  Test code for instant/tankless water heater
#
#
#  copyright 2022 by Gorm Rose
#
#  This example code is licensed under GNU PL V3.0
#

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

patterns = [0b00000000000000000000000000000000,  #  0 first phase
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

#### µC pin definitions ####

_gate = Pin(0, Pin.OUT)       # gate of power triac: 0 = on
_gate2 = Pin(1, Pin.OUT)      # gate of power triac: 0 = on
_zerocross = Pin(2, Pin.IN)   # 0 = mains zero crossing right now
_flow = Pin(22, Pin.IN)       # water flow pulses 660 pulses/l
temp_out = ADC(26)
temp_in = ADC(27)

#### user constants ####

Ttarget = 41                  # TARGET TEMPERATURE
BoostTime = 500               # Boost time in 1/64/freq, so about 0.8 per second for 50Hz
p = 1 / 14                    # constant for heating curve: power = p * delta_temperature * waterflow  (higher = steeper)
k0 = 16.6                     # constants for tranforming ADC value to temperature in °C
k1 = 1 / 1390
k2 = 1 / 116000000

#### variables ####

cycle = 1       # pattern bit counter
lowhigh = 0     # always two identical bits
power = 0       # values from 0 (off) to 64 (full power on both phases)
TinLP = 0       # temperature LP filter (64 values)
ToutLP = 0
Wflow = 0       # water flow counter
flowcnt = 0
standbycnt = 0  # counts time of no water consumption in 64/f (f=50Hz in Europe) steps till BoostTime
boost = 0

_gate.value(1)      # init as inactive
_gate2.value(1)     # init as inactive

#### water counter interrupt ####

def callback(_flow):
    global flowcnt
    flowcnt += 1

_flow.irq(trigger=Pin.IRQ_FALLING, handler=callback)

#### control loop ####

while True:
    if lowhigh != 0:  # this 'if' ensures, that always two half waves are either on or off (avoids DC on AC net)
        cycle -= 1
        lowhigh = 0
    else:
        lowhigh = 1

    if cycle == 0:  # once every 1.28s @ 50 Hz (1.02s @ 60 Hz)
        cycle = 32
        temp = 0x10000 - (ToutLP >> 6)  # >> 6: temperature LP filter (64 values)
        Tout = k0 + k1 * temp + k2 * temp * temp  # calculate temperature in °C from ADC values
        temp = 0x10000 - (TinLP >> 6)
        Tin  = k0 + k1 * temp + k2 * temp * temp

        TinLP = 0  # reinit counters
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
            if standbycnt != 0:
                boost = int((Ttarget - Tin) * standbycnt / 150)
                standbycnt = 0

        power = int(p * Wflow * (Ttarget - Tin))
        if power < 0:
            power = 0
        if power > 64 or boost > 0:
            power = 64

        print(Tout, Tin, Wflow, power, standbycnt, boost)

    while _zerocross.value() == 1:    # wait for mains voltage zero crossing
        pass

    if power > 32:
        _gate.value(0)          # trigger triac for the next half wave (10ms)
    else:
        if (patterns[power] & (1 << (cycle - 1))) != 0:
            _gate.value(0)      # trigger triac for the next half wave (10ms)
    sleep(.003)                 # trigger for 3ms
    _gate.value(1)              # then release trigger

#    if power > 32:  # enable these lines for 2-phase setups
#        while _zerocross.value() == 1:  # wait for mains voltage zero crossing (2nd phase must be 120° delayed)
#            pass
#        if (patterns[power - 32] & (1 << (cycle - 1))) != 0 or boost > 0:
#            _gate2.value(0)     # trigger 2nd triac for the next half wave (10ms)
#    sleep(.003)                 # trigger for 3ms
#    _gate2.value(1)             # then release trigger2

    ToutLP += temp_out.read_u16()  # blue/green wires in my case
    TinLP += temp_in.read_u16()    # white/gray wires in my case






