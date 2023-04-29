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

from machine import Pin,UART
from rotary_irq_rp2 import RotaryIRQ
from tools import load_config
import time

l = Pin(2, Pin.OUT)#设置引脚
mode = Pin(3, Pin.OUT)
uart = UART(0, baudrate=57600, tx=Pin(0), rx=Pin(1))

keys = load_config()#加载键位配置

Kms = [0,0,0,0,0,0,0]#创建变量
Kold = []
Knm = []
Knms = []
Kname = ['k1','k2','k3','k4','k5','k6','ST']

RL = 0x00
RR = 0x00
R1ms = 0
R2ms = 0
senms = 0
Lon = 0

def main(a,b,c):
    global l
    global mode
    global uart
    global keys
    global Kms
    global Kold
    global Knm
    global Knms
    global Kname
    global RL
    global RR
    global R1ms
    global R2ms
    global senms
    global Lon
    
    sw1 = Pin(9, Pin.IN, Pin.PULL_UP)# 覆盖设置引脚
    sw2 = Pin(10, Pin.IN, Pin.PULL_UP)
    sw3 = Pin(11, Pin.IN, Pin.PULL_UP)
    sw4 = Pin(12, Pin.IN, Pin.PULL_UP)
    sw5 = Pin(14, Pin.IN, Pin.PULL_UP)
    sw6 = Pin(15, Pin.IN, Pin.PULL_UP)
    ST = Pin(13, Pin.IN, Pin.PULL_UP)

    SR1 = RotaryIRQ(#设置旋转编码器
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
    SR1.set(value=1)#设置编码器初始值
    SR2.set(value=1)
    KD = {'k1':keys['k1'],'k2':keys['k2'],'k3':keys['k3'],'k4':keys['k4'],'k5':keys['k5'],'k6':keys['k6'],'ST':keys['ST']}#初步处理键位设置

    while a.value()+b.value()+c.value() == 3:
        
        RTv = [SR1.value(),SR2.value()]#读取编码器状态
        KV = [sw1.value(),sw2.value(),sw3.value(),sw4.value(),sw5.value(),sw6.value(),ST.value()]#读取按键状态

        for q in range(len(KV)) :#按键输入处理
            if KV[q] == 0 :
                if not KD[Kname[q]] in Knm :
                    Knm.append(KD[Kname[q]])
                    Kms[q] = time.ticks_ms()
            elif not time.ticks_diff(time.ticks_ms(), Kms[q]) >= 5 :#5ms消抖
                if KD[Kname[q]] not in Knm :
                    Knm.append(KD[Kname[q]])

        if RTv[0] != 1 :#编码器输入处理
            if RTv[0] == 0 :
                RL = keys['SR1L']
                R1ms = time.ticks_ms()
                SR1.set(value=1)
            elif RTv[0] == 2 :
                RL = keys['SR1R']
                R1ms = time.ticks_ms()
                SR1.set(value=1)
            Knm.append(RL)
        elif not time.ticks_diff(time.ticks_ms(), R1ms) >= 75 :#延迟75ms释放按键
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
        
        for i in Knm :#处理按键数据 去除重复键值
            for s in i:
                if s not in Knms:
                    Knms.append(s)
        
        while len(Knms) < 6 :#补足按键数据6位长度
            Knms.append(0)

        if Knms != Kold :#发送按键数据到CH9329
            uart.write(b'\x57\xab\x00\x02\x08\x00\x00'+bytes([Knms[0],Knms[1],Knms[2],Knms[3],Knms[4],Knms[5],(0x57+0xab+0x02+0x08+Knms[0]+Knms[1]+Knms[2]+Knms[3]+Knms[4]+Knms[5])&0xff]))
            Kold = Knms

        if Knms != [0,0,0,0,0,0] :#按键提示灯
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

        Knms = []#重置按键数据
        Knm = []
