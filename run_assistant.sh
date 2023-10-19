#!/bin/bash
echo 'stopping service'
ps aux | grep streamlit |grep assistant |awk '{print $2}' | xargs -t kill
sleep 1
echo 'starting service'
streamlit run assistant_web.py --server.port 8502 2>&1 | tee $LOG_HOME/assistant.log