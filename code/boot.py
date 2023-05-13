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
from tools import setup
from machine import Pin
from main import main

F1 = Pin(6, Pin.IN, Pin.PULL_UP)#设置DIP开关引脚
F2 = Pin(7, Pin.IN, Pin.PULL_UP)
F3 = Pin(8, Pin.IN, Pin.PULL_UP)

#from keycos import Keycos 此处引入其他外来功能模块,在这里写import


setup()#初始化CH9329

while True :#主循环
    if F1.value() == 0 :
        #替换下面pass为外来模块的主函数，传入DIP开关引脚对象让函数知道自己由哪个开关控制
        pass
    elif F2.value() == 0 :
        #同上
        pass
    elif F3.value() == 0 :
        #同上
        pass
    else:
        main(F1,F2,F3)#没有开关打开时运行默认主函数