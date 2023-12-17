# README

Historical data downloader from Oanda

# Features

- Handles the 5000 candles per request limit by chunking into multiple requests
- Prevents rate limit by creating a keep alive session and delaying 20ms between requests
- Provides a plan on how many candles will be obtained and how many requests it will make
- Logs the current request with start and end time to provide progress and transparency

# Limitations

- No retries. If there is an error, the entire process ends

# Usage

1. Clone this repository
2. Run the following

```sh
> python3 main.py USD_JPY 2013-01-01 2023-12-16 M1 <api_key> USD_JPY_20130101_20231216.csv

Total maximum number of candles is 5761440.0. Split into 1153 chunks to workaround the limit=5000 per request
Fetching between 2013-01-01T00:00:00Z (inc.) and 2013-01-04T11:20:00Z (exc.)
Fetching between 2013-01-04T11:20:00Z (inc.) and 2013-01-07T22:40:00Z (exc.)
Fetching between 2013-01-07T22:40:00Z (inc.) and 2013-01-11T10:00:00Z (exc.)
Fetching between 2013-01-11T10:00:00Z (inc.) and 2013-01-14T21:20:00Z (exc.)
...
```

The arugments are below, listed in the order of arguments when running the script.

| Item | Comment |
|--|--|
| Instrument | Instrument. use v3/accounts/{accountID}/instruments to get the list of available instruments. e.g. USD_JPY |
| From Time | A date and time value using either RFC3339 or UNIX time representation. e.g. 2023-11-03T00:00:00Z |
| To Time | A date and time value using either RFC3339 or UNIX time representation. e.g. 2023-12-11T00:00:00Z |
| [Granularity][1] | how granular each candle must be e.g. M1
| API Key | api key obtained from Oanda for practic environment |
| File name | output file path e.g. my_output.csv



[1]: https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickGranularity
