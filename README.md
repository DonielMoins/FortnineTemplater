# Requests Templater

Simple Requests Manager/Profiler/Executer.
Make request templates and run them easily using csv files as input params.
Currently project is in alpha, use with caution!

## Requirements

- Python >= 3.10b3

## TODO

1. [ ] Make a template Editor
2. [ ] Refactor Code
3. [x] Add CSV parser
4. [ ] Drag n' drop CSV files
5. [x] Drag n' drop CSV parser
6. [ ] Add progress bar for each request button
7. [ ] Specialize requests based on method
8. [x] Make a better README
9. [x] Basic config parser
10. [x] Prototype DataEntry window
11. [x] Prototype Profile Selector GUI

## Config

For storing pre-made profiles, I chose [hjson](https://hjson.github.io) because of the following reasons:

1. It's pretty hard to f*ck up.
2. You can add **comments**.
3. No need for quotes.
4. Serialize friendly (comes from json).
5. And most importantly, human friendly json.

### Config Notes **IMPORTANT**

- Each Profile object under profiles should have a unique name/ID, E.g.

``

profiles:
    [
        {
            profID1029: {...}
            profID1023678: {...}
            profWithSpecialName: {...}
``
