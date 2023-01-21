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
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))


uart.write(b'\x57\xab\x00\x0b\x10\x00\x0ePCX-LK_Creates\x00')
uart.write(b'\x57\xab\x00\x0b\x05\x01\x03RKD\x0b')
