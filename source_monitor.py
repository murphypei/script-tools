# This Python file uses the following encoding: utf-8
import os
import time
import stat
import pexpect
import ConfigParser
from socket import *
#time.sleep(60)
#配置需要监控的业务进程名称
Process_Name=["/guard","/aps","/sa","/zyguard"]

#读配置文件获取告警阀值(物理及虚拟内存/CPU)
def ReadConf(alarmtype,sername,value):
    config=ConfigParser.ConfigParser()
    config.read('/usr/local/lxb/alarm.conf')
    threshold=config.getint(alarmtype,sername)
    if ((alarmtype!="cpu") and (alarmtype!="Physical_Machine_Threshold")):
        threshold=threshold*0.01*value
    return threshold

#写日志及拷贝日志文件函数
def WriteCopyLog(name,num,typename,threshold):
     timenow=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
     opentxt = open('/usr/local/lxb/log/alarmlog/%s_alarm.log' %ip,'a')
     if typename == "Rss_Memory" or typename=="Vsz_Memory":
         opentxt.writelines('%s\t%s\t%s\t\tAt present the use value:%.2fMb\t\tThreshold:%sMb\n' %(timenow,name,typename,num,threshold))
     else:
         opentxt.writelines('%s\t%s\t%s\t\tAt present the use value:%.2f%%\t\tThreshold:%s%%\n' %(timenow,name,typename,num,threshold))
     opentxt.close()
     copyfile=pexpect.spawn("scp -P 22 /usr/local/lxb/log/alarmlog/%s_alarm.log root@172.16.185.109:/usr/local/lxb/log/alarmlog/" %ip)
     time.sleep(30)
     copyfile.expect("root@172.16.185.109's password")
     copyfile.sendline("kedatest1")
     copyfile.expect(pexpect.EOF)

#x=os.popen('ps aux |grep guard|awk \'{print $11}\'').read()
#获取系统IP地址
ip = os.popen("/sbin/ifconfig | grep 'inet addr' | awk '{print $2}'").read()
ip = ip[ip.find(':')+1:ip.find('\n')]
'''
proce=os.popen("ps aux |grep guard|grep -v 'grep'|awk '{print $11}'").read()
proce=proce.strip().split('\n')
lens=len(proce)
for i in range(lens):
    #得到以‘/’打头的进程
    if proce[i][0] in '/':
        pname[i]=proce[i][9:]
    elif proce[i][0] in '.':
        pname[i]=proce[i][2:]
keys=pname.keys()
'''
Process_Number=len(Process_Name)
#服务器虚拟内存大小
swptotal=os.popen("free | grep Swap | awk '{print $2}'").read()
swptotal=int(swptotal)/1024

#服务器物理内存大小
memtotal=os.popen("free | grep Mem | awk '{print $2}'").read()
memtotal=int(memtotal)/1024

#CPU核数
cpunumber=os.popen("cat /proc/cpuinfo |grep 'processor'|wc -l").read()
cpunumber=int(cpunumber)

#系统CPU使用率
def System_Cpu():
    Sys_Cpu_Use=os.popen("vmstat|grep -v procs|grep -v swpd|awk '{print $13}'").read()
    Sys_Cpu_Use=int(Sys_Cpu_Use)
    return Sys_Cpu_Use

#系统内存使用率
def System_Memory():
    Sys_Mem_Use=os.popen("free | grep Mem | awk '{print $3}'").read()
    Sys_Mem_Use=int(Sys_Mem_Use)/1024
    return Sys_Mem_Use
#获取业务进程号
First_Process_Number={}
for x in range(Process_Number):
    if Process_Name[x]=="/guard":
        First_Process=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $2}'" %Process_Name[x],'r').read()
    else:
        First_Process=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $2}'" %Process_Name[x],'r').read()
    First_Process_Number[x]=First_Process.strip().split('\n')
    
print First_Process_Number

Second_Process_Number={}
Vsz_Memory={}
Rss_Memory={}
Cpu_Use_Value={}
while True:
    time.sleep(3)
    #获取业务进程号
    for y in range(Process_Number):
        if Process_Name[y]=="/guard":
            Second_Process=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $2}'" %Process_Name[y],'r').read()
        else:
            Second_Process=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $2}'" %Process_Name[y],'r').read()
        Second_Process_Number[y]=Second_Process.strip().split('\n')
    #print "second"
    #print Second_Process_Number
    #判断业务进程是否有变化，有变化写入日志文件
    for j in range(Process_Number):
        if First_Process_Number[j]!=Second_Process_Number[j]:
            Time_Now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            opencpu = open('/usr/local/lxb/log/collapselog/%s_collapse.log' %ip,'a')
            opencpu.writelines('%s\t%s\tCollapse\tThe new process:%s\tThe old process:%s\n' %(Time_Now,Process_Name[j],Second_Process_Number[j],First_Process_Number[j]))
            opencpu.close()
            copyfile=pexpect.spawn("scp -P 22 /usr/local/lxb/log/collapselog/%s_collapse.log root@172.16.185.109:/usr/local/lxb/log/collapselog" %ip)
            time.sleep(30)
            copyfile.expect("root@172.16.185.109's password")
            copyfile.sendline("kedatest1")
            copyfile.expect(pexpect.EOF)
    #获取业务进程号
    for x in range(Process_Number):
        if Process_Name[x]=="/guard":
            First_Process=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $2}'" %Process_Name[x],'r').read()
        else:
            First_Process=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $2}'" %Process_Name[x],'r').read()
        First_Process_Number[x]=First_Process.strip().split('\n')
    #print "first"
    #print First_Process_Number

    #虚拟内存使用值判断
    #print "RSSMEM---------------"
    for m1 in range(Process_Number):
        alarmtype="vszmem"
        typename="Vsz_Memory"
        #print pname[keys[m1]]
        if Process_Name[m1]=="/guard":
            Vsz_Mems=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $5}'" %Process_Name[m1],'r').read()
        else:
            Vsz_Mems=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $5}'" %Process_Name[m1],'r').read()
        Vsz_Memory[m1]=float(Vsz_Mems)/1024
        Vsz_Memory_Threshold=ReadConf(alarmtype,Process_Name[m1],swptotal)
        #print "1使用:%s" %Vsz_Memory[m1]
        #print "1阀值:%s" %Vsz_Memory_Threshold
        if Vsz_Memory[m1]>=Vsz_Memory_Threshold:
            WriteCopyLog(Process_Name[m1],Vsz_Memory[m1],typename,Vsz_Memory_Threshold)

    #物理内存使用值判断
    #print "RSSMEM---------------"
    for m2 in range(Process_Number):
        alarmtype="rssmem"
        typename="Rss_Memory"
        #print pname[keys[m2]]
        if Process_Name[m2]=="/guard":
            Rss_Mems=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $6}'" %Process_Name[m2],'r').read()
        else:
            Rss_Mems=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $6}'" %Process_Name[m2],'r').read()
            
        #print "xxxxxxxxx:%s" %Rss_Mems
        #print "yyyyyyyyy:%.2f" %float(Rss_Mems)
        Rss_Memory[m2]=float(Rss_Mems)/1024
        Rss_Memory_Threshold=ReadConf(alarmtype,Process_Name[m2],memtotal)
        #print "1使用:%.2f" %Rss_Memory[m2]
        #print "1阀值:%.2f" %Rss_Memory_Threshold
        if Rss_Memory[m2]>=Rss_Memory_Threshold:
            WriteCopyLog(Process_Name[m2],Rss_Memory[m2],typename,Rss_Memory_Threshold)        

    #CPU使用值判断
    #print "CPU---------------"
    for c in range(Process_Number):
        alarmtype="cpu"
        typename="Cpu Use   "
        cpuvalue=0
        #print pname[keys[c]]
        if Process_Name[c]=="/guard":
            Cpu_Uses=os.popen("ps aux | grep %s |grep -v 'grep'|grep -v '/bin/bash'|awk '{print $3}'" %Process_Name[c],'r').read()
            Cpu_Uses=Cpu_Uses.strip().split('\n')
        else:
            Cpu_Uses=os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $3}'" %Process_Name[c],'r').read()
            Cpu_Uses=Cpu_Uses.strip().split('\n')
        Cpu_Use_Value[c]=float(Cpu_Uses[0])
        Cpu_Use_Threshold=ReadConf(alarmtype,Process_Name[c],cpuvalue)
        #print "1使用:%s" %Cpu_Use_Value[c]
        #print "1阀值:%s" %Cpu_Use_Threshold
        if Cpu_Use_Value[c]>=Cpu_Use_Threshold:
            WriteCopyLog(Process_Name[c],Cpu_Use_Value[c],typename,Cpu_Use_Threshold)
            
    #系统CPU使用告警
    Sys_Cpu_Threshold=ReadConf("Physical_Machine_Threshold","cpu_use",0)
    System_Cpu()
    if System_Cpu()>=Sys_Cpu_Threshold:
        WriteCopyLog("System",System_Cpu(),"System Cpu Use",Sys_Cpu_Threshold)
        
    #系统内存使用告警
    Sys_Mem_Threshold=ReadConf("Physical_Machine_Threshold","memory_use",0)
    Sys_Mem=System_Memory()/memtotal
    if Sys_Mem>=Sys_Mem_Threshold:
        WriteCopyLog("System",Sys_Mem,"System Mem Use",Sys_Mem_Threshold)