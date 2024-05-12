'''
RKD-MpyCode
Copyright (C) 2024 PCX-LK
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
        self.SR1 = RotaryIRQ(#设置旋转编码器
            pin_num_clk=17, 
            pin_num_dt=16, 
            min_val=0, 
            max_val=2,
            pull_up=True,
            half_step=False,
            range_mode=RotaryIRQ.RANGE_BOUNDED)
        self.SR2 = RotaryIRQ(
            pin_num_clk=20, 
            pin_num_dt=19, 
            min_val=0, 
            max_val=2,
            pull_up=True,
            half_step=False,
            range_mode=RotaryIRQ.RANGE_BOUNDED)
        
        self.keys = self.tools.load_config()#加载键位配置
        # 创建变量
        self.Kms = [0,0,0,0,0,0,0,0,0]# 上次触发时间
        self.Kstatus = [False,False,False,False,False,False,False,False,False] # 按键状态
        self.nowtime = 0
        self.Knm = [0,0,0,0,0,0] # 要发送的按键包
        self.Knmm = []
        self.Knmold = []
        self.KD = [] # 键值
        self.RT = [[self.SR1,[0x00],'RTLL','RTLR',False],[self.SR2,[0x00],'RTRL','RTRR',False]]
        self.Rms = [0,0]

        self.senms = 0
        self.Lon = 0

        self.sw1 = self.tools.sw1# 设置引脚
        self.sw2 = self.tools.sw2
        self.sw3 = self.tools.sw3
        self.sw4 = self.tools.sw4
        self.sw5 = self.tools.sw5
        self.sw6 = self.tools.sw6
        self.ST = self.tools.ST
        self.RTSL = self.tools.RTSL
        self.RTSR = self.tools.RTSR

        self.SR1.set(value=1)#设置编码器初始值
        self.SR2.set(value=1)
        
        if self.var.boot_mode == 1:#在boot mode 1时加载预设组1
            self.KD = [self.keys['m1']['k1'],self.keys['m1']['k2'],
                       self.keys['m1']['k3'],self.keys['m1']['k4'],
                       self.keys['m1']['k5'],self.keys['m1']['k6'],
                       self.keys['m1']['ST'],self.keys['m1']['RTLS'],
                       self.keys['m1']['RTRS']]#初步处理键位设置
            

    def main(self):
        """主循环"""
        while self._mode_dect():
            self.nowtime = time.ticks_ms()
            
            self._kmap_dect()    
                
            self._read_status()
            
            self._key_processing()
            self._rotary_processing()
            
            #self._raw_data_processing()
            #self._debugoutput()

            self._press_status_show()
            self._send_data()

            #重置按键数据
            self.Knmm = self.Knm[:]
            self.Knm = [0,0,0,0,0,0]
            
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
                self.var.kmap_index = 'm1'
                self.KD = [self.keys['m1']['k1'],self.keys['m1']['k2'],
                           self.keys['m1']['k3'],self.keys['m1']['k4'],
                           self.keys['m1']['k5'],self.keys['m1']['k6'],
                           self.keys['m1']['ST'],self.keys['m1']['RTLS'],
                           self.keys['m1']['RTRS']]#加载键位预设1
            elif mode == 1:
                self.var.kmap_index = 'm2'
                self.KD = [self.keys['m2']['k1'],self.keys['m2']['k2'],
                           self.keys['m2']['k3'],self.keys['m2']['k4'],
                           self.keys['m2']['k5'],self.keys['m2']['k6'],
                           self.keys['m2']['ST'],self.keys['m1']['RTLS'],
                           self.keys['m2']['RTRS']]#加载键位预设2
            elif mode == 2:
                self.var.kmap_index = 'm3'
                self.KD = [self.keys['m3']['k1'],self.keys['m3']['k2'],
                           self.keys['m3']['k3'],self.keys['m3']['k4'],
                           self.keys['m3']['k5'],self.keys['m3']['k6'],
                           self.keys['m3']['ST'],self.keys['m1']['RTLS'],
                           self.keys['m3']['RTRS']]#加载键位预设3
            elif mode == 3:
                self.var.kmap_index = 'm4'
                self.KD = [self.keys['m4']['k1'],self.keys['m4']['k2'],
                           self.keys['m4']['k3'],self.keys['m4']['k4'],
                           self.keys['m4']['k5'],self.keys['m4']['k6'],
                           self.keys['m4']['ST'],self.keys['m1']['RTLS'],
                           self.keys['m4']['RTRS']]#加载键位预设4
        
    def _read_status(self):
        """读取按键/编码器状态"""
        self.RTv = [self.RT[0][0].value(),self.RT[1][0].value()]#读取编码器状态
        self.KV = [self.sw1.value(),self.sw2.value(),self.sw3.value(),
                   self.sw4.value(),self.sw5.value(),self.sw6.value(),
                   self.ST.value(),self.RTSL.value(),self.RTSR.value()]#读取按键状态
    
    def _key_processing(self):
        """处理按键状态"""
        for i in range(len(self.KV)) :
            if time.ticks_diff(self.nowtime, self.Kms[i]) > 5:
                if (not self.KV[i]) != self.Kstatus[i]:
                    self.Kstatus[i] = not self.KV[i]
                    self.Kms[i] = self.nowtime
    
    def _rotary_processing(self):
        """处理编码器状态"""
        for i in range(2):
            if self.RTv[i] == 0 :
                self.RT[i][1] = self.keys[self.var.kmap_index][self.RT[i][2][:]]
                self.Rms[i] = self.nowtime
                self.RT[i][4] = True
                self.RT[i][0].set(value=1)
            elif self.RTv[i] == 1 :
                self.RT[i][4] = False
            elif self.RTv[i] == 2 :
                self.RT[i][1] = self.keys[self.var.kmap_index][self.RT[i][3][:]]
                self.Rms[i] = self.nowtime
                self.RT[i][4] = True 
                self.RT[i][0].set(value=1)
    
#     def _raw_data_processing(self):
#         """处理原始按键数据"""
#         pass

    def _press_status_show(self):
        """按键提示灯"""
        if self.Knmm != [0,0,0,0,0,0] :
            if time.ticks_diff(self.nowtime, self.senms) >= 25 and self.Lon == 0 :
                self.senms = time.ticks_ms()
                self.Lon = 1
                self.l.on()
            if time.ticks_diff(self.nowtime, self.senms) >= 25 and self.Lon == 1 :
                self.senms = time.ticks_ms()
                self.Lon = 0
                self.l.off()
        else:
            self.l.off()

    def _send_data(self):
        """发送数据到CH9329"""
        for i in range(len(self.Kstatus)):
            if self.Kstatus[i]:
                for a in range(len(self.KD[i])):
                    if self.KD[i]:
                        for q in range(len(self.Knm)):
                            if self.Knm[q] == 0 :
                                self.Knm[q] = self.KD[i][a]
                                break
                            
        for s in range(2):
            if self.RT[s][4] or self.nowtime - self.Rms[s] <= 75:
                for i in range(len(self.RT[s][1])):
                    if self.RT[s][1][i]:
                        for a in range(len(self.Knm)):
                            if not self.Knm[a]:
                                self.Knm[a] = self.RT[s][1][a]
                                break
                
                
        
        if self.Knm != self.Knmold:
            #self._debugoutput()
            self.uart.write(b'\x57\xab\x00\x02\x08\x00\x00'+bytes([self.Knm[0],self.Knm[1],self.Knm[2],self.Knm[3],self.Knm[4],self.Knm[5],(0x57+0xab+0x02+0x08+self.Knm[0]+self.Knm[1]+self.Knm[2]+self.Knm[3]+self.Knm[4]+self.Knm[5])&0xff]))
            self.Knmold = self.Knm[:]
        

    def _debugoutput(self):
        print('debug output:')
        print("Kstatus:"+str(self.Kstatus))
        #print("Ks:"+str(self.Ks))
        print("Kms:"+str(self.Kms))
        print("Knm:"+str(self.Knm))
        print("Knmm:"+str(self.Knmm))
        print("RT:"+str(self.RT))
        print("RTv:"+str(self.RTv))
        #print("RTvo:"+str(self.RTvo))
        print("Rms:"+str(self.Rms))
        print("nowtime:"+str(self.nowtime))
        time.sleep_ms(50)