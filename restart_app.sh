#!/bin/bash
echo 'stopping service'
ps aux | grep streamlit |grep app |awk '{print $2}' | xargs -t kill
sleep 1
echo 'starting service'
/Users/chenhao/miniconda3/envs/agi-tools/bin/streamlit run app.py --server.port 8502 --logger.level=debug 2>&1 | tee $LOG_HOME/st_tool.log