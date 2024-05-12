'''
RKD-MpyCode
Copyright (C) 2023 PTALTS-LK
https://github.com/PTALTS-LK/RKD-MpyCode

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
import time,json

class Settings:
    """用于修改设置的类"""
    def __init__(self,var,tools,SET_Pin,f1,f2):
        """初始化"""
        self.var = var
        self.tools = tools
        self.SET_Pin = SET_Pin
        self.S_1 = f1
        self.S_2 = f2
        self.keydict = self.tools.KeyDict
        self.kindex = "m1"
    
    def main(self):
        """主函数"""
        print("设置模式，输入 `help` 以查看帮助,如退出请先关闭开关再输入 `exit` 回车或者关闭开关之后按下RUN按钮")
        while self.SET_Pin.value() == 0:
            text=input('> ')
            while len(text) == 0:
                text=input('> ')
            if text[0] == 'exit':
                break
            text=text.split()
            self.run(text)
        print('退出设置模式')

    def run(self,text):
        """分析用户输入的指令"""
        if text[0] == "help":
            self._help(text)
        elif text[0] == "key":
            self._key(text)
        elif text[0]!='exit':
            print('输入指令无效,请重新输入')
            
    def _help(self,text):
        """help子指令主函数"""
        if len(text) == 1 :
            print("命令列表: \n\n")
            print('key  键位设置')
            print("\n\n输入: `help <指令>` 获取对应指令帮助")
        else:
            if text[1] == 'key':
                print('指令: `key`')
                print('  用途: 设置键位，或获取特定键位的值')
                print('  语法: key <操作> <参数1> <参数2> ...')
                print('    \'操作\'参数说明:')
                print('      支持以下操作:')
                print('        `getKeyList`\t\t获取所有可设置的键的键名,无后续参数')
                print('        `getKeyMap`\t\t获取按键绑定表,无后续参数')
                print('        `getKeyValue`\t\t获取当前键位预设组中目标键名对应键的按键绑定. 使用F2F1来切换目标键位预设组,后续参数为目标键名,请使用 `getKeyList` 获取键名')
                print('        `getKeyGroupValue`\t获取当前键位预设组的所有按键绑定. 使用F2F1来切换修改目标键位预设组')
                print('        `setKeyValue`\t\t设置按键绑定. 使用F2F1来切换目标键位预设组,第一个后续参数为: 目标键键名,第2-N个后续参数为目标键的按键绑定表键位')
    
    def _key(self,text):
        """key指令主函数"""
        if len(text) == 1 :
            print('无操作,请输入 `help key` 查看帮助')
        elif text[1] == 'getKeyList':
            self._key_getKeyList()
        elif text[1] == 'getKeyMap':
            self._key_getKeyMap()
        elif text[1] == 'getKeyValue':
            self._key_getKeyValue(text)
        elif text[1] == 'getKeyGroupValue':
            self._key_getKeyGroupValue(text)
        elif text[1] == 'setKeyValue':
            self._key_setKeyValue(text)
        else:
            print('参数无效,请输入 `help key` 查看帮助')

    def _key_getKeyList(self):
        """key指令的getKeyList参数主函数"""
        print('当前版本可用的所有按键:')
        print('主板按键:')
        print('  `k1`  主板上从左往右第一个按键,默认`D`')
        print('  `k2`  主板上从左往右第二个按键,默认`F`')
        print('  `k3`  主板上从左往右第三个按键,默认`J`')
        print('  `k4`  主板上从左往右第四个按键mode = (not self.SET_Pin_a.value())*2**0+(not self.SET_Pin_b.value())*2**1,默认`K`')
        print('SDVX扩展板按键:')
        print('  `ST`    圆形按键,用作Start键,默认`Space`')
        print('  `k5`    圆形按键左边的按键,默认`V`')
        print('  `k6`    圆形按键右边的按键,默认`N`')
        print('  `RTLL`  左旋钮逆时针旋转,默认`W`')
        print('  `RTLR`  左旋钮顺时针旋转,默认`E`')
        print('  `RTLS`  左旋钮按下,默认`NULL`')
        print('  `RTRL`  右旋钮逆时针旋转,默认`O`')
        print('  `RTRR`  右旋钮顺时针旋转,默认`P`')
        print('  `RTRS`  右旋钮按下,默认`NULL`')
        
    def _key_getKeyMap(self):
        """key指令的getKeyMap参数主函数"""
        print('特殊键码:')
        print('  `NULL`  "空"按键,设置之后可以让按键空闲')
        print('以下是所有可用的物理按键对应键名:')
        print('''数字键区\n  对应物理按键  按键名  \n  1/!         1\n  2/@         2\n  3/#         3\n  4/$         4\n  5/%         5\n  6/^         6\n  7/&         7\n  8/*         8\n  9/(         9\n  0/)         0\n字母键区\n  对应物理按键  按键名  \n  Q           Q\n  W           W\n  E           E\n  R           R\n  T           T\n  Y           Y\n  U           U\n  I           I\n  O           O\n  P           P\n  A           A\n  S           S\n  D           D\n  F           F\n  G           G\n  H           H\n  J           J\n  K           K\n  L           L\n  Z           Z\n  X           X\n  C           C\n  V           V\n  B           B\n  N           N\n  M           M\n符号键区\n  对应物理按键  按键名   \n  `/~           `\n  -/_           -\n  =/+           =\n  \\ |           \\\n  ;/:           ;\n  '/"           '\n  ,/<           <\n  ./>           .\n  / ?           /\n  Space         Space \n功能键区\n  对应物理按键  按键名\n  ESC           ESC\n  Enter         Enter\n  BackSpace     BackSpace\n  Tab           Tab\n  CapsLock      CapsLock\n  Left Shift    ShiftL\n  Right Shift   ShiftR\n  Left Ctrl     CtrlL\n  Right Ctrl    CtrlR\n  Left Alt      AltL\n  Right Alt     AltR\n  Left Win      WinL\n  Right Win     WinR\n  Insert        Insert\n  Delete        Delete\n  Home          Home\n  End           End\n  PrintScreen   PrintScreen\n  ScrollLock    ScrollLock\n  Pause         Pause\n  PageUp        PageUp\n  PageDown      PageDown\n  Application   App\n  UpArrow       UpArrow\n  DownArrow     DownArrow\n  LeftArrow     LeftArrow\n  RightArrow    RightArrow\nFunction键区\n  对应物理按键  按键名\n  F1            F1\n  F2            F2\n  F3            F3\n  F4            F4\n  F5            F5\n  F6            F6\n  F7            F7\n  F8            F8\n  F9            F9\n  F10           F10\n  F11           F11\n  F12           F12\n小键盘区\n  对应物理按键  按键名\n  NumLock       NumLock\n  /             n/\n  *             n*\n  -             n-\n  +             n+\n  .             n.\n  Enter         nEnter\n  1             n1\n  2             n2\n  3             n3\n  4             n4\n  5             n5\n  6             n6\n  7             n7\n  8             n8\n  9             n9\n  0             n0''')

    def _key_getKeyValue(self,text):
        """key指令的getKeyValue参数主函数"""
        try:
            file=open('/config.json')
        except OSError:
            print('检测到按键配置json文件不存在,已写入默认配置,如需继续读取请再次输入同样指令')
            self.tools.write_defconf()
        else:
            
            try:
                data=json.load(file)
            except ValueError:
                print('检测到按键配置json文件损坏,已写入默认配置,如需继续读取请再次输入同样指令')
                self.tools.write_defconf()
            else:
                self._dectKIndex()
                    
                if len(text) == 2:
                    print('未输入键名,请输入 `help key` 查看帮助')
                elif text[2] not in data[self.kindex]:
                    print('键名无效,请输入 `help key` 查看帮助')
                else:
                    print('目标键绑定为:')
                    print('  '+str(data[self.kindex][text[2]]))
                file.close()
                
    def _key_getKeyGroupValue(self,text):
        """key指令的getKeyGroupValue参数主函数"""
        try:
            file=open('/config.json')
        except OSError:
            print('检测到按键配置json文件不存在,已写入默认配置,如需继续读取请再次输入同样指令')
            self.tools.write_defconf()
        else:
            
            try:
                data=json.load(file)
            except ValueError:
                print('检测到按键配置json文件损坏,已写入默认配置,如需继续读取请再次输入同样指令')
                self.tools.write_defconf()
            else:
                self._dectKIndex()
                    
                print('目标预设组绑定为:')
                print('  '+str(data[self.kindex]))
                file.close()
                
    def _key_setKeyValue(self,text):
        """key指令的setKeyValue参数主函数"""
        kmap=[]
        bk=0
        try:
            file=open('/config.json')
        except OSError:
            print('检测到按键配置json文件不存在,已写入默认配置,如需继续修改请再次输入同样指令')
            self.tools.write_defconf()
        else:
            try:
                data=json.load(file)
            except ValueError:
                print('检测到按键配置json文件损坏,已写入默认配置,如需继续修改请再次输入同样指令')
                self.tools.write_defconf()
            else:
                file.close()
                
                self._dectKIndex()
                    
                if len(text) == 2:
                    print('未输入键名,请输入 `help key` 查看帮助')
                elif text[2] not in data[self.kindex]:
                    print('键名无效,请输入 `help key` 查看帮助')
                else:
                    if len(text) == 3:
                        print('未输入修改值,请输入 `help key` 查看帮助')
                    else:
                        
                        for i in text[3:]:
                            if i not in self.keydict:
                                print('修改值无效,请输入 `help key` 查看帮助')
                                bk = 1
                                break
                            else:
                                kmap.append(i)
                        if bk == 0 :
                            file=open('/config.json',mode='w+')
                            data[self.kindex][text[2]]=kmap
                            json.dump(data,file,separators=(',', ':'))
                            file.flush()
                            file.close()
                            print('修改成功')

    def _dectKIndex(self):
        mode = (not self.S_1.value())*2**0+(not self.S_2.value())*2**1
        if mode == 0:
            self.kindex = 'm1'
            print('目标预设: 1')
        elif mode == 1:
            self.kindex = 'm2'
            print('目标预设: 2')
        elif mode == 2:
            self.kindex = 'm3'
            print('目标预设: 3')
        elif mode == 3:
            self.kindex = 'm4'
            print('目标预设: 4')
