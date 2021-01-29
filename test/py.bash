#!/bin/bash
procnum1=` ps -ef |grep "python -u send_queue.py"|grep -v grep|wc -l`
procnum2=`ps -ef |grep "python -u receipt_set_mq.py"|grep -v grep|wc -l`
procnum3=` ps -ef |grep "python pre_api.py"|grep -v grep|wc -l`
procnum4=` ps -ef |grep "get_sms_order.py"|grep -v grep|wc -l`
procnum5=` ps -ef |grep "test.py"|grep -v grep|wc -l`
if [ $procnum1 -eq 0 ]; then
cd /set_preceipt/receipt
 nohup python -u send_queue.py  >send_queue.txt 2>&1 &
fi
if [ $procnum2 -eq 0 ]; then
 cd /set_preceipt/receipt
 nohup python -u receipt_set_mq.py  >receipt_set_mq.txt 2>&1 &
fi
if [ $procnum3 -eq 0 ]; then
 cd /api_preceipt/api
 nohup python pre_api.py   >temp2.txt 2>&1 &
fi
if [ $procnum4 -eq 0 ]; then
 cd /api_preceipt/api
 nohup python -u get_sms_order.py > sms.log 2>&1 &
fi
if [ $procnum5 -eq 0 ]; then
 cd /api_preceipt
 nohup python -u test.py >test.log 2>&1 &
fi