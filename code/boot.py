'''
RKD-MpyCode
Copyright (C) 2023 PCX-LK
https://github.com/PCX-LK/RKD-MpyCode

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
from machine import Pin
from keycos import Keycos
from main import main

F1 = Pin(6, Pin.IN, Pin.PULL_UP)
F2 = Pin(7, Pin.IN, Pin.PULL_UP)
F3 = Pin(8, Pin.IN, Pin.PULL_UP)

while True :
    if F1.value() == 0 :
        Keycos()
#     elif F2.value() == 0 :
#         
#     elif F3.value() == 0 :
#         
    else:
        main()