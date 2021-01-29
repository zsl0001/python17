#!/bin/bash
cd /api_preceipt/dzhd_use_info
nohup python -u tcp.py  >tcp.txt 2>&1 &

