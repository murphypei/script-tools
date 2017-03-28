# -*- coding:utf-8 -*-

# @author: peic
# 监视CPU和GPU的资源利用率并统计平均资源使用率

import os
import time
import re


# 配置需要监控的业务进程名称
process_name = ["engine_laucher","sensestruct_engine"]

# 获取统计
def get_statistics_info():
 
    # CPU占用率 
    cpu_rate = 0
    # 内存占用
    memory_size = 0
    # gpu信息
    gpu_rate = 0
    gpu_memory = 0

    number = 0
    statistics_number = 2000

    # 统计200次
    while (number < statistics_number):
        time.sleep(5)
        print '-' * 8 + " {} ".format(number) + '-'*8
        
        for i in range(len(process_name)):
            # cpu信息, 对于engine_laucher，有两个
            rates = os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $3}'" % process_name[i],'r').read()
            rates = rates.strip().split('\n')
            rate = sum([float(r) for r in rates])
            cpu_rate += rate

            # 内存信息
            # 获取使用物理内存大小（单位kb)
            sizes = os.popen("ps aux | grep %s |grep -v 'grep'|awk '{print $6}'" %process_name[i],'r').read()
            sizes = sizes.strip().split('\n')
            size = sum([long(r) for r in sizes]) / 1024.0 / 1024.0
            memory_size += size

            # gpu使用信息
            gpu_info = os.popen("nvidia-smi").read()
            # 从nvidia-smi中进行字符串匹配来提取使用率信息
            volatile_pattern = r'(\d+)W(\s+\/\s+)(\d+)W(\s+\|\s+)(\d+)MiB(\s+\/\s+)(\d+)MiB(\s+\|\s+)(\s+)(\d+)%'
            gpu_mem_pattern = r'{}(\s+)(\d+)MiB'.format(process_name[i])
            
            gpu_volatile = 0
            search_result = re.search(volatile_pattern, gpu_info)
            if search_result:
                gpu_volatile =  search_result.group(10)
            gpu_rate += float(gpu_volatile)
            
            gpu_mem = 0
            search_result = re.search(gpu_mem_pattern, gpu_info)
            if search_result:
                gpu_mem = search_result.group(2)
            gpu_memory += float(gpu_mem)
            
        print "process: {}, cpu_rate: {}, memory size : {} GB\n， gpu_volatile: {}, gpu_mem size {}".format(
            process_name[i], rate, size, gpu_volatile, gpu_mem)
        
        number += 1

    if (number != 0) :
        cpu_rate /= number
        memory_size /= number
        gpu_rate /=  number
        gpu_memory /=  number

    print "*" * 5 + "statistics info: " + "*" * 5
    
    print "cpu rate: {}        memory size: {}GB\ngpu_volatile: {}    gpu_mem size {}MB".format(
        cpu_rate, memory_size, gpu_rate, gpu_memory)


if __name__ == '__main__':
    
    get_statistics_info()
