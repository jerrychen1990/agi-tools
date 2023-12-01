#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/11/27 15:16:50
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import time
import random
import concurrent
from flask import Flask, jsonify, request

    
def run(job_id):
    rs = random.random()*10
    print(f"job {job_id} starts" )
    time.sleep(rs)
    jobs[job_id] = (rs, "done")
    print(f"job {job_id} ends")


jobs = dict()
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
app = Flask(__name__)


def get_job_status(job_id):
    return jobs[job_id]

@app.route('/create_job', methods=['POST'])
def create_job():
    job_id = str(time.time())
    jobs[job_id] = (None,"pending")    
    executor.submit(run, job_id)
    rs, status = get_job_status(job_id)
    
    return jsonify(dict(job_id=job_id, status=status, rs=rs))
    
    
@app.route('/get_job_result', methods=['POST'])
def get_job_result():
    job_id = request.get_json()['job_id']
    rs, status = get_job_status(job_id)
    return jsonify(dict(job_id=job_id, status=status, rs=rs))
    
    

if __name__ == '__main__':
    app.run(debug=True)

    
    


