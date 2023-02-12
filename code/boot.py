'''
RKD-MpyCode
Copyright (C) 2023 PCX-LK

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from machine import Pin,UART
from rotary_irq_rp2 import RotaryIRQ
from tools import load_config
from keycos import Keycos
import time,binascii

l = Pin(2, Pin.OUT)
mode = Pin(3, Pin.OUT)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

bk = Pin(8, Pin.IN, Pin.PULL_UP)
sw1 = Pin(9, Pin.IN, Pin.PULL_UP)# 初始化引脚
sw2 = Pin(10, Pin.IN, Pin.PULL_UP)
sw3 = Pin(11, Pin.IN, Pin.PULL_UP)
sw4 = Pin(12, Pin.IN, Pin.PULL_UP)
sw5 = Pin(14, Pin.IN, Pin.PULL_UP)
sw6 = Pin(15, Pin.IN, Pin.PULL_UP)
ST = Pin(13, Pin.IN, Pin.PULL_UP)
MODE = Pin(6, Pin.IN, Pin.PULL_UP)

SR1 = RotaryIRQ(
   pin_num_clk=17, 
   pin_num_dt=16, 
   min_val=0, 
   max_val=2,
   pull_up=True,
   half_step=True,
   range_mode=RotaryIRQ.RANGE_BOUNDED)
SR2 = RotaryIRQ(
   pin_num_clk=20, 
   pin_num_dt=19, 
   min_val=0, 
   max_val=2,
   pull_up=True,
   half_step=True,
   range_mode=RotaryIRQ.RANGE_BOUNDED)
SR1.set(value=1)
SR2.set(value=1)

# k1def = 0x07
# k2def = 0x09
# k3def = 0x0d
# k4def = 0x0e
# k5def = 0x19
# k6def = 0x11
# STdef = 0x2c
# SR1defL = 0x1a
# SR1defR = 0x08
# SR2defL = 0x12
# SR2defR = 0x13

keys = load_config()

Kms = [0,0,0,0,0,0,0]
Kold = []
Knm = []

RL = 0x00
RR = 0x00
R1ms = 0
R2ms = 0
senms = 0
Lon = 0

while True :
    if MODE.value() == 0 :
        Keycos()
    if bk.value() == 0 :
        break
    KD = [keys['k1'],keys['k2'],keys['k3'],keys['k4'],keys['k5'],keys['k6'],keys['ST']]
    RTv = [SR1.value(),SR2.value()]
    KV = [sw1.value(),sw2.value(),sw3.value(),sw4.value(),sw5.value(),sw6.value(),ST.value()]
    
    for q in range(len(KV)) :
        if KV[q] == 0 :
            if not KD[q] in Knm :
                Knm.append(KD[q])
                Kms[q] = time.ticks_ms()
        elif not time.ticks_diff(time.ticks_ms(), Kms[q]) >= 5 :
            if not KD[q] in Knm :
                Knm.append(KD[q])

    if RTv[0] != 1 :
        if RTv[0] == 0 :
            RL = keys['SR1L']
            R1ms = time.ticks_ms()
            SR1.set(value=1)
        elif RTv[0] == 2 :
            RL = keys['SR1R']
            R1ms = time.ticks_ms()
            SR1.set(value=1)
        Knm.append(RL)
    elif not time.ticks_diff(time.ticks_ms(), R1ms) >= 75 :
        if not RL in Knm :
            Knm.append(RL)
        
    if RTv[1] != 1 :
        if RTv[1] == 0 :
            RR = keys['SR2L']
            R2ms = time.ticks_ms()
            SR2.set(value=1)
        elif RTv[1] == 2 :
            RR = keys['SR2R']
            R2ms = time.ticks_ms()
            SR2.set(value=1)
        Knm.append(RR)
    elif not time.ticks_diff(time.ticks_ms(), R2ms) >= 75 :
        if not RR in Knm :
            Knm.append(RR)

    while len(Knm) < 6 :
        Knm.append(0)


    if Knm != Kold :
        uart.write(binascii.unhexlify(b'57ab0002080000'+'{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}'.format(Knm[0],Knm[1],Knm[2],Knm[3],Knm[4],Knm[5])+'{:02X}'.format((0x57+0xab+0x02+0x08+Knm[0]+Knm[1]+Knm[2]+Knm[3]+Knm[4]+Knm[5])&0xff)))
        Kold = Knm

    if Knm != [0,0,0,0,0,0] :
        if time.ticks_diff(time.ticks_ms(), senms) >= 25 and Lon == 0 :
            senms = time.ticks_ms()
            Lon = 1
            l.on()
        if time.ticks_diff(time.ticks_ms(), senms) >= 25 and Lon == 1 :
            senms = time.ticks_ms()
            Lon = 0
            l.off()
    else:
        l.off()
    
    Knm = []

