#!/bin/bash
echo 'starting service'
streamlit run app.py --server.port 8501 --logger.level=debug 2>&1 | tee $LOG_HOME/st_tool.log