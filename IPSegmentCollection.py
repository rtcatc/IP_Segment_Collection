#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import sys,os
import sqlite3
from socket import gethostbyname

"""
    企业IP段信息搜集工具 V1.0
    Auteur:Poc Sir E-mail:cool-guy@c-est.cool
    Mon site Internet:https://www.hackinn.com
    Weibo:@Poc-Sir Twitter:@rtcatc GitHub:@rtcatc
"""

def Get_IPSegment(IP_Original):
    IP_Final =  IP_Original.split('.')[0] + "." + IP_Original.split('.')[1] +  "." + IP_Original.split('.')[2] + ".0/24"  #将获取到的IP转化为网段
    Add_SegmentInfo(IP_Final)

def Get_HostIP(Host_Name):
    try:
        Host_IP = gethostbyname(Host_Name) #获取域名对应的IP地址
        Get_IPSegment(Host_IP)
    except:
        return 0

def Get_File(File_In): #一行一行读取文件
    file = open(File_In)
    Host_Name = file.readline()
    while Host_Name:
        Host_Name = file.readline()
        Host_Name = Host_Name.strip() #删除空格，换行符 //但这里我没有删去空白行，可能会出现错误，下次修正
        Host_Name = Host_Name.strip('\n')
        Get_HostIP(Host_Name)
    file.close()

def Get_MiddleStr(content,startStr,endStr): #获取中间字符串的一个通用函数
    startIndex = content.index(startStr)
    if startIndex>=0:
        startIndex += len(startStr)
    endIndex = content.index(endStr)
    return content[startIndex:endIndex]

def Add_SegmentInfo(IP_Final):
    conn = sqlite3.connect('SegmentInfo.db')
    c = conn.cursor()
    Select_SQL = "SELECT Weight from DATA where Segment=\"" + IP_Final + "\""
    Add_SQL = "INSERT into DATA (Segment,Weight) VALUES (\"" + IP_Final + "\",1)" #初次添加IP段，权重为1
    Update_SQL = "UPDATE DATA SET Weight = Weight + 1 WHERE Segment=\"" + IP_Final + "\""
    c.execute(Select_SQL)
    IP_res = c.fetchall()
    if len(IP_res) > 0 : #判断IP段是否存在，没有则添加权重为1的记录，有则升级权重
        c.execute(Update_SQL)
    else:
        c.execute(Add_SQL)
    conn.commit()
    conn.close()

def Print_Long(string, length=0): #通用函数，固定字符串长度
	if length == 0:
		return string
	slen = len(string)
	re = string
	if isinstance(string, str):
		placeholder = ' '
	else:
		placeholder = u'　'
	while slen < length:
		re += placeholder
		slen += 1
	return re

def Print_SegmentInfo(File_Out,Weight_Value):
    conn = sqlite3.connect('SegmentInfo.db')
    c = conn.cursor()
    Print_SQL = "SELECT Segment,Weight from DATA where Weight > " + str(Weight_Value) #查询符合权重的IP段
    Info_results = c.execute(Print_SQL)
    All_results = Info_results.fetchall()
    file = open(File_Out,"w")
    print "+------------------+-----+\n| IP段             | 权重|\n+------------------+-----+"
    file.write("+------------------+-----+\n| IP段             | 权重 |\n+------------------+-----+\n")
    for results in All_results: #遍历符合要求的IP段，将其输出
        results = str(results)
        results_part1 = Get_MiddleStr(results,"(u\'","\', ")
        results_part2 = Get_MiddleStr(results,"\', ",")")
        file.write("| " + Print_Long(results_part1, 17) + "| " + Print_Long(results_part2, 4) + "|\n")
        print "| " + Print_Long(results_part1, 17) + "| " + Print_Long(results_part2, 4) + "|"
    print "+------------------+-----+"
    file.write("+------------------+-----+")
    file.close()
    conn.commit()
    conn.close()

def Create_Database():
    conn = sqlite3.connect('SegmentInfo.db') #创建一个SQLite数据库，方便统计IP段和权重
    c = conn.cursor()
    c.execute('''CREATE TABLE DATA
       (Segment  TEXT  PRIMARY KEY  NOT NULL,
        Weight   INT                NOT NULL);''')
    conn.commit()
    conn.close()

def Delete_Database(): #删除用于临时储存和分析的数据库
    DB_path = os.getcwd() + os.sep + "SegmentInfo.db"
    try:
        os.remove(DB_path)
    except:
        return 0

if __name__ == '__main__':
    Delete_Database()
    Create_Database()
    Weight_Value = 2 #设置权重值为2，则权重值小于等于2的IP段将不会被输出，提高准确性,可在此修改参数
    File_In = raw_input("输入域名信息文件路径和名称:")
    File_Out = raw_input("输入输出结果文件路径和名称:")
    File_In = unicode(File_In, "utf8") #支持中文路径
    File_Out = unicode(File_Out, "utf8")
    File_In = File_In.strip()  #去除两边空格
    File_Out = File_Out.strip()
    Get_File(File_In)
    Print_SegmentInfo(File_Out,Weight_Value)
    Delete_Database()
