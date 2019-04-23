#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from decimal import Decimal #使用精确浮点预算库
#############################################################################################
#   function: 产生通信测试用PRBS伪随机序列
#   author: Mark
#   version: V1.0
#   入口参数:
#           1、User_defined/PRBS_N (N=7,9,11,15,17,20,23,29,31)--使用自定义或者规定的PRBS_N序列；
#           2、seeds--产生伪随机序列的种子；
#           3、polynomial tap--规定的伪随机序列的标准tap；x^tap1+x^tap2+1 tap1>tap2
#   参数使用字典来传递
#   返回参数：
#           对应的PRBS码型
#############################################################################################
# seed and tap ref. keysight help files
prbs_dictionary={"PRBS_7":['0101010',[7,6]],
                 "PRBS_9":['010101010',[9,5]],
                 "PRBS_11":['01010101010',[11,9]],
                 "PRBS_15":['010101010101010',[15,14]],
                 "PRBS_17":['01010101010101010',[17,14]],
                 "PRBS_20":['10101010101010101010',[20,3]],
                 "PRBS_23":['01010101010101010101010',[23,18]],
                 "PRBS_29":['01010101010101010101010101010',[29,27]],
                 "PRBS_31":['0101010101010101010101010101010',[31,28]],
                 }
# if prbstype=PRBS_N, default of seed and taps are None, if prbstype=User_defined, seed and taps must be given
def prbs_Generator(prbstype, seed = None, taps = None):

    if prbstype == 'User_defined':
        prbs_sequence = prbs_create(seed,taps)
    else:
        prbs_sequence = prbs_create(prbs_dictionary.get(prbstype)[0],prbs_dictionary.get(prbstype)[1])
    return prbs_sequence

# 用xrange省空间同时提高效率
def prbs_create(seed, taps):
    #将字符串转化为列表
    sequence_list = [int(i) for i in list(seed)]
    #计算伪随机序列周期长度
    prbs_length = (2 << (len(seed) - 1))-1
    #产生规定长度的伪随机序列
    for i in range(prbs_length):
        # 对taps中的两个数进行XOR计算
        mod_two_add = sum([sequence_list[t-1] for t in taps])
        xor = mod_two_add % 2
        #将得到的值插入到队列首端
        sequence_list.insert(0, xor)
        #list 倒置
        sequence_list.reverse()
    return sequence_list

# print result_data
# print prbs_dictionary.get("PRBS_7")[0]

#############################################################################################
#   function: 通过特定的PRBS产生PWL文件
#   version: V1.0
#   入口参数:
#           1、输入PWL文件需要的Bit, V0(低电平), V1（高电平）, Bit rate, Rise time, Fall time；
#   返回参数：
#           输出符合spice仿真需要的PWL文件（.txt 文档）
#############################################################################################
def create_PWL(Bits, V0,V1,BitRate,RiseTime,FallTime):
    #从逻辑level转换成电平幅度

    waveform_list = []
    time_list = []
    volt_Bits = []
    # print len(Bits)
    # print range(len(Bits))
    for i in range(len(Bits)):
        if Bits[i] == 1:
            volt_Bits.append(V1)
        else:
            volt_Bits.append(V0)

    # 装换成含上升，下降时间的电平幅度
    for bitN in range(len(Bits)):
        waveform_list.append(volt_Bits[bitN])
        waveform_list.append(volt_Bits[bitN])
    # 获取精准的浮点运算，先将数字转换成字符使用Decimal计算后，在转回float类型
    bit_Period = round(1.0/BitRate, 3)
    for time in range(len(waveform_list)-1):
        if time%2 == 1:
            if waveform_list[time] > waveform_list[time+1]:
                time_list.append(float(Decimal(str(time+1))/Decimal('2')*Decimal(str(bit_Period))-Decimal(FallTime)))
            else:
                time_list.append(float(Decimal(str(time+1))/Decimal('2')*Decimal(str(bit_Period))-Decimal(RiseTime)))
        else:
            time_list.append(float(Decimal(str(time))/Decimal('2')*Decimal(str(bit_Period))))
    # time_list.append(float(Decimal(str(time+1))/Decimal('2')*Decimal(str(bit_Period))))
    # time_list.append(bit_Period*len(waveform_list))
    pwl_List = {"time":time_list, "Waveform":waveform_list}
    return pwl_List

#############################################################################################
# function：将生成的pwl_List按照标准格式写入text文档中，第一列为time, 第二列为voltage
# version: v1.0
# 入口：
#   1、pwl_list; 标准波形存储的字典
#   2、savePath_Name; 文件保存路径和名称
# 出口：
#   标准格式保存的text文档
#############################################################################################

def save_PWL_File(pwl_list, savePath_Name):
    DataFile = open(savePath_Name, mode = 'w+')
    for i in range(len(pwl_list.get("time"))):
        content = str(pwl_list.get("time")[i]) + ' ' + str(pwl_list.get("Waveform")[i]) + '\n'
        DataFile.writelines(content)
    DataFile.close()


result_data = prbs_Generator(prbstype = "PRBS_9")
savePath_Name = ".\pwl.txt"
pwl_file = create_PWL(result_data, 0, 5, BitRate = 10, RiseTime = 0.01, FallTime = 0.02)
save_PWL_File(pwl_file, savePath_Name)

# print pwl_file.get("time")
# print pwl_file.get("Waveform")



