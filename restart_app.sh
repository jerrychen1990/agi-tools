#!/bin/bash
echo 'stopping service'
ps aux | grep streamlit |grep app |awk '{print $2}' | xargs -t kill
sleep 1
echo 'starting service'
streamlit run app.py --server.port 8501 2>&1 | tee $LOG_HOME/st_tool.log