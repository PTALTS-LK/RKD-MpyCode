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
import time,binascii

def ERROR_led():
    if time.ticks_diff(time.ticks_ms(), senms) >= 100 and Lon == 0 :
        senms = time.ticks_ms()
        Lon = 1
        stats.on()
    if time.ticks_diff(time.ticks_ms(), senms) >= 100 and Lon == 1 :
        senms = time.ticks_ms()
        Lon = 0
        stats.off()

senms = time.ticks_ms()
Lon = time.ticks_ms()
l = Pin(2, Pin.OUT)
mode = Pin(3, Pin.OUT)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
sw1 = Pin(9, Pin.IN, Pin.PULL_UP)
MODE = Pin(6, Pin.IN, Pin.PULL_UP)

def Keycos() :
    lt = time.ticks_ms()
    mode.on()
    try :
        file = open('keycos',mode='r')
    except OSError :
        print('keycos file not exist')
        while True :
            if MODE.value() == 1 :
                mode.off()
                break
            ERROR_led()
    else :
        while True :
            if MODE.value() == 1 :
                uart.write(b'\x57\xab\x00\x02\x08\x00\x00\x00\x00\x00\x00\x00\x00\x0c')
                mode.off()
                break
            if sw1.value() == 0 :
                Ts = time.ticks_ms()
                file.seek(0)
                l.off()
                while True :
                    data = file.readline().split()
                    for i in range(len(data)) :
                        data[i] = int(data[i])
                    if data[0] != -1 :
                        Time = Ts + data[0]
                    else:
                        uart.write(b'\x57\xab\x00\x02\x08\x00\x00\x00\x00\x00\x00\x00\x00\x0c')
                        break
                    l.on()
                    uart.write(binascii.unhexlify(b'57ab0002080000'+'{:02X}{:02X}{:02X}{:02X}{:02X}{:02X}'.format(data[1],data[2],data[3],data[4],data[5],data[6])+'{:02X}'.format((0x57+0xab+0x02+0x08+data[1]+data[2]+data[3]+data[4]+data[5]+data[6])&0xff)))
                    if time.ticks_diff(time.ticks_ms(), senms) > 10:
                        l.off()
                        lt = time.ticks_ms()
                    while True :
                        if MODE.value() == 1:
                            break
                        if time.ticks_ms() >= Time:
                            break
                    if MODE.value() == 1:
                        uart.write(b'\x57\xab\x00\x02\x08\x00\x00\x00\x00\x00\x00\x00\x00\x0c')
                        break
                    l.on()
                
    file.close()
    mode.off()
    return
