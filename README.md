# Requests Template Manager

Simple Requests Manager.
Create request templates and run them easily using CSV files as input params.

## Requirements

- Python >= 3.9
- venv: Run ``` pip install -r Requirements.txt ``` in venv

## TODO

1. [ ] Prettify GUI
2. [ ] Fix "NULL" in postDataList multiple times
3. [ ] Possibly add arg parser support

## Config

For storing pre-made profiles, I chose [hjson](https://hjson.github.io) due the following reasons:

1. It's pretty hard to mess up.
2. You can add **comments**.
3. No need for quotes.
4. Serializable (comes from json).
5. And most importantly, human friendly json.
