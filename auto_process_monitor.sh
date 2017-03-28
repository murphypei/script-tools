#!/bin/bash

# @author: peic
# 监控程序，若程序被kill，则自动拉起程序


# 脚本的名字，用以在查找进程时过滤掉当前脚本的进程
script_name="auto_process_monitor.sh"


# 检查文件是否存在
# @param $1:要监控的程序的目录
function check_file()
{
    if [ $# -ne 1 ]; then
        echo "参数错误，正确使用方法： check_file /dir/file"
        return 1;
    fi

    if [ ! -f $1 ];then
        echo "文件 $1 不存在"
        return 1
    fi
}


# return 0:进程没有运行 1:进程已运行
# @param $1:要监控的程序的目录
function monitor_process()
{
    if [ $# -ne 1 ]; then
        echo "参数错误，正确使用方法：monitor_process /dir/file"
        return 1
    fi

    process_exists=$(ps -ef | grep $1 | grep -v grep | grep -v $script_name | wc -l)
    
    if [ $process_exists -eq 0 ]; then
        return 0
    else
        return 1
    fi
}


# 启动监控程序
# @param $1:要监控的程序的目录function start_monitor()
{
    if [ $# -ne 1 ]; then
        echo "参数错误，正确使用方法：start_monitor /dir/file"
        return 1
    fi

    process_path=$1
    process_name=$(echo $process_path | awk -F / '{print $NF}')
    
    monitor_process $process_name
    if [ $? -eq 0 ]; then
        echo "该进程没有运行：$process_path"
        echo "现将启动进程"

        $process_path &
        #sh $process_path &
        
        monitor_process $process_name
        if [ $? -eq 1 ]; then
            echo "重启进程成功"
        else
            echo "重启进程失败"
        fi
     else
        echo "进程已经启动"
     fi   
}


# 主程序
# @param $1:要监控的程序的目录
if [ $# -ne 1 ]; then
    echo "参数错误，正确使用方法：ecdata_auto_process_monitor /dir/file"
    exit 1
fi

check_file $1
if [ $? -ne 0 ]; then
    exit 1
fi

start_monitor $1
