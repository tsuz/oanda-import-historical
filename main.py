

import os
import pandas as pd
from dateutil import parser
import datetime
import requests
import math
import time
import sys

base_url = 'https://api-fxpractice.oanda.com/v3/instruments'
api_key = sys.argv[5]
instrument = sys.argv[1]
granularity = sys.argv[4] # M1
price_component = 'M'
count = 5000
from_time = sys.argv[2] #  '2023-11-03T00:00:00Z'
to_time = sys.argv[3] # '2023-12-11T00:00:00Z'
file_name = sys.argv[6] # 'test.csv'

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + api_key
}

price_component_map = {
    'm': 'mid',
    'a': 'ask',
    'b': 'bid',
}

# get granularity and chunk it into smaller pieces
gran = granularity[0]

if gran == 'S':
    gran = int(granularity.replace('S', ''))
    gran_multiplier = gran

elif gran == 'M':
    v = int(granularity.replace('M', ''))
    gran_multiplier = v * 60

elif gran == 'H':
    v = int(granularity.replace('H', ''))
    gran_multiplier = v * 3600
    
elif gran == 'D':
    v = int(granularity.replace('D', ''))
    gran_multiplier = v * 86400

elif gran == 'W':
    v = int(granularity.replace('W', ''))
    gran_multiplier = v * 604800
    
elif gran == 'M':
    v = int(granularity.replace('M', ''))
    gran_multiplier = v * 108000


try:
    t1 = parser.parse(from_time)
except ValueError:
    print(f'Invalid from_time {from_time}')
    os.exit(1)

try:
    t2 = parser.parse(to_time)
except ValueError:
    print(f'Invalid from_time {from_time}')
    os.exit(1)


delta = t2 - t1
number_of_candles = delta.total_seconds() / gran_multiplier
chunks = math.ceil(number_of_candles / count)
print(f'Total maximum number of candles is {number_of_candles}. Split into {chunks} chunks to workaround the limit={count} per request')


for idx in range(chunks):
    start_time = t1 + datetime.timedelta(seconds=gran_multiplier * count) * idx
    end_time = t1 + datetime.timedelta(seconds=gran_multiplier * count) * (idx+1)

    # don't go over the end time
    if (end_time - t2).total_seconds() > 0:
        end_time = t2

    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    url = f'{base_url}/{instrument}/candles?price={price_component}&granularity={granularity}&from={start_time_str}&to={end_time_str}'

    is_first = idx == 0
    rows_list = []

    try:
        print(f'Fetching between {start_time_str} (inc.) and {end_time_str} (exc.)')
        s = requests.Session()
        r = s.get(url, headers=headers)
        r.raise_for_status()
        json_data = r.json()
        accessor = price_component_map[price_component.lower()]

        for c in json_data['candles']:
            v = {}
            a = c[accessor]
            v['time'] = c['time']
            v['volume'] = c['volume']
            v['complete'] = c['complete']
            v['Open'] = a['o']
            v['High'] = a['h']
            v['Low'] = a['l']
            v['Close'] = a['c']
            
            rows_list.append(v)
        
        df = pd.DataFrame(rows_list)
        df['time'] = pd.to_datetime(df['time'])
        df = df.set_index('time')
        if is_first:
            df.to_csv(file_name, header=True)
        else:
            df.to_csv(file_name, mode='a', header=False)


        # For new connections, we recommend you limit this to twice per second (2/s). 
        # Establishing a new TCP and SSL connection is expensive for both client and server. 
        # To allow a better experience, using a persistent connection will allow more requests to be performed on an established connection.
        # 0.5 = 500ms but we give some buffer
        
        # For an established connection, we recommend limiting this to one hundred per second (100/s). 
        time.sleep(0.02)

    except requests.exceptions.HTTPError as err:
        print(err.response.text)
        sys.exit()

    

