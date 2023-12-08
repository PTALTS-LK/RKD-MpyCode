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
import time

from rotary_irq_rp2 import RotaryIRQ

from tools import Tools

class Main:
    """默认的键盘行为"""
    def __init__(self,var,tools,SET_Pin_a,SET_Pin_b,SET_Pin_c):
        """初始化相关变量和设置引脚"""
        self.tools = tools
        self.SET_Pin_a = SET_Pin_a
        self.SET_Pin_b = SET_Pin_b
        self.SET_Pin_c = SET_Pin_c
        self.var = var
        
        self.l = Pin(2, Pin.OUT)#设置引脚
        self.mode = Pin(3, Pin.OUT)
        self.uart = UART(0, baudrate=57600, tx=Pin(0), rx=Pin(1))
        
        self.keys = self.tools.load_config()#加载键位配置

        self.Kms = [0,0,0,0,0,0,0]#创建变量
        self.Kold = []
        self.Knm = []
        self.Knms = []
        self.Kname = ['k1','k2','k3','k4','k5','k6','ST']
        self.KD = {}

        self.RL = 0x00
        self.RR = 0x00
        self.R1ms = 0
        self.R2ms = 0
        self.senms = 0
        self.Lon = 0

        self.sw1 = self.tools.sw1# 设置引脚
        self.sw2 = self.tools.sw2
        self.sw3 = self.tools.sw3
        self.sw4 = self.tools.sw4
        self.sw5 = self.tools.sw5
        self.sw6 = self.tools.sw6
        self.ST = self.tools.ST

#         self.sw1 = Pin(9, Pin.IN, Pin.PULL_UP)# 覆盖设置引脚
#         self.sw2 = Pin(10, Pin.IN, Pin.PULL_UP)
#         self.sw3 = Pin(11, Pin.IN, Pin.PULL_UP)
#         self.sw4 = Pin(12, Pin.IN, Pin.PULL_UP)
#         self.sw5 = Pin(14, Pin.IN, Pin.PULL_UP)
#         self.sw6 = Pin(15, Pin.IN, Pin.PULL_UP)
#         self.ST = Pin(13, Pin.IN, Pin.PULL_UP)

        self.SR1 = RotaryIRQ(#设置旋转编码器
            pin_num_clk=17, 
            pin_num_dt=16, 
            min_val=0, 
            max_val=2,
            pull_up=True,
            half_step=True,
            range_mode=RotaryIRQ.RANGE_BOUNDED)
        self.SR2 = RotaryIRQ(
            pin_num_clk=20, 
            pin_num_dt=19, 
            min_val=0, 
            max_val=2,
            pull_up=True,
            half_step=True,
            range_mode=RotaryIRQ.RANGE_BOUNDED)
        self.SR1.set(value=1)#设置编码器初始值
        self.SR2.set(value=1)
        
        if self.var.boot_mode == 1:#在boot mode 1时加载预设组1
            self.KD = {'k1':self.keys['m1']['k1'],'k2':self.keys['m1']['k2'],
                       'k3':self.keys['m1']['k3'],'k4':self.keys['m1']['k4'],
                       'k5':self.keys['m1']['k5'],'k6':self.keys['m1']['k6'],
                       'ST':self.keys['m1']['ST']}#初步处理键位设置
            

    def main(self):
        """主循环"""
        while self._mode_dect():
            
            self._kmap_dect()    
                
            self._read_status()
            
            self._key_processing()
            self._rotary_processing()
            
            self._raw_data_processing()

            self._send_data()

            if self.Knms != [0,0,0,0,0,0] :#按键提示灯
                if time.ticks_diff(time.ticks_ms(), self.senms) >= 25 and self.Lon == 0 :
                    self.senms = time.ticks_ms()
                    self.Lon = 1
                    self.l.on()
                if time.ticks_diff(time.ticks_ms(), self.senms) >= 25 and self.Lon == 1 :
                    self.senms = time.ticks_ms()
                    self.Lon = 0
                    self.l.off()
            else:
                self.l.off()

            self.Knms = []#重置按键数据
            self.Knm = []

    def _mode_dect(self):
        """检查处于哪个boot循环"""
        if self.var.boot_mode == 0:
            return self.SET_Pin_c.value()
        else:
            return (self.SET_Pin_a.value()+self.SET_Pin_b.value()+self.SET_Pin_c.value() == 3)
    
    def _kmap_dect(self):
        """在boot mode 0下检测选择了哪个键位预设"""
        if self.var.boot_mode == 0:
            mode = (not self.SET_Pin_a.value())*2**0+(not self.SET_Pin_b.value())*2**1
            if mode == 0:
                self.var.kamp_index = 'm1'
                self.KD = {'k1':self.keys['m1']['k1'],'k2':self.keys['m1']['k2'],
                           'k3':self.keys['m1']['k3'],'k4':self.keys['m1']['k4'],
                           'k5':self.keys['m1']['k5'],'k6':self.keys['m1']['k6'],
                           'ST':self.keys['m1']['ST']}#加载键位预设1
            elif mode == 1:
                self.var.kamp_index = 'm2'
                self.KD = {'k1':self.keys['m2']['k1'],'k2':self.keys['m2']['k2'],
                           'k3':self.keys['m2']['k3'],'k4':self.keys['m2']['k4'],
                           'k5':self.keys['m2']['k5'],'k6':self.keys['m2']['k6'],
                           'ST':self.keys['m2']['ST']}#加载键位预设2
            elif mode == 2:
                self.var.kamp_index = 'm3'
                self.KD = {'k1':self.keys['m3']['k1'],'k2':self.keys['m3']['k2'],
                           'k3':self.keys['m3']['k3'],'k4':self.keys['m3']['k4'],
                           'k5':self.keys['m3']['k5'],'k6':self.keys['m3']['k6'],
                           'ST':self.keys['m3']['ST']}#加载键位预设3
            elif mode == 3:
                self.var.kamp_index = 'm4'
                self.KD = {'k1':self.keys['m4']['k1'],'k2':self.keys['m4']['k2'],
                           'k3':self.keys['m4']['k3'],'k4':self.keys['m4']['k4'],
                           'k5':self.keys['m4']['k5'],'k6':self.keys['m4']['k6'],
                           'ST':self.keys['m4']['ST']}#加载键位预设4
        
    def _read_status(self):
        """读取按键/编码器状态"""
        self.RTv = [self.SR1.value(),self.SR2.value()]#读取编码器状态
        self.KV = [self.sw1.value(),self.sw2.value(),self.sw3.value(),
                   self.sw4.value(),self.sw5.value(),self.sw6.value(),
                   self.ST.value()]#读取按键状态
    
    def _key_processing(self):
        """处理按键状态"""
        for q in range(len(self.KV)) :#按键输入处理
            if self.KV[q] == 0 :
                if not self.KD[self.Kname[q]] in self.Knm :
                    self.Knm.append(self.KD[self.Kname[q]])
                    self.Kms[q] = time.ticks_ms()
            elif not time.ticks_diff(time.ticks_ms(), self.Kms[q]) >= 5 :#5ms消抖
                if self.KD[self.Kname[q]] not in self.Knm :
                    self.Knm.append(self.KD[self.Kname[q]])
    
    def _rotary_processing(self):
        """处理编码器状态"""
        if self.RTv[0] != 1 :#编码器输入处理
            if self.RTv[0] == 0 :
                self.RL = self.keys[self.var.kamp_index]['SR1L']
                self.R1ms = time.ticks_ms()
                self.SR1.set(value=1)
            elif self.RTv[0] == 2 :
                self.RL = self.keys[self.var.kamp_index]['SR1R']
                self.R1ms = time.ticks_ms()
                self.SR1.set(value=1)
            self.Knm.append(self.RL)
            
        elif not time.ticks_diff(time.ticks_ms(), self.R1ms) >= 75 :#延迟75ms释放编码器按键
            if not self.RL in self.Knm :
                self.Knm.append(self.RL)
                
        if self.RTv[1] != 1 :
            if self.RTv[1] == 0 :
                self.RR = self.keys[self.var.kamp_index]['SR2L']
                self.R2ms = time.ticks_ms()
                self.SR2.set(value=1)
            elif self.RTv[1] == 2 :
                self.RR = self.keys[self.var.kamp_index]['SR2R']
                self.R2ms = time.ticks_ms()
                self.SR2.set(value=1)
            self.Knm.append(self.RR)
                
        elif not time.ticks_diff(time.ticks_ms(), self.R2ms) >= 75 :
            if not self.RR in self.Knm :
                self.Knm.append(self.RR)
    def _raw_data_processing(self):
        """处理原始按键数据"""
        for i in self.Knm :#处理按键数据 去除重复键值
            for s in i:
                if s not in self.Knms:
                    self.Knms.append(s)
        
        while len(self.Knms) < 6 :#补足按键数据6位长度
            self.Knms.append(0)
    
    def _send_data(self):
        """发送数据到CH9329"""
        if self.Knms != self.Kold :#发送按键数据到CH9329
            self.uart.write(b'\x57\xab\x00\x02\x08\x00\x00'+bytes([self.Knms[0],self.Knms[1],self.Knms[2],self.Knms[3],self.Knms[4],self.Knms[5],(0x57+0xab+0x02+0x08+self.Knms[0]+self.Knms[1]+self.Knms[2]+self.Knms[3]+self.Knms[4]+self.Knms[5])&0xff]))
            self.Kold = self.Knms
