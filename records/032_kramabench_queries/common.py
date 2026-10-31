from pathlib import Path
import json, sys, socket
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data/kramabench/data'
def block_network(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.bind','socket.sendto'):
        raise RuntimeError('Network is disabled for local queries')
sys.addaudithook(block_network)
pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.precision',15)
def finish(result):
    print('\nRESULT_JSON')
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    return result
