# Requests Template Manager

Simple Requests Manager.
Create request templates and run them easily using CSV files as input params.
Currently project is in alpha, use with caution!

## Requirements

- Python >= 3.10b3
- venv: Run ``` pip install -r Requirements.txt ``` in venv

## TODO

Listed from most to least important.

1. [ ] Make a template Editor (Most Important)
2. [ ] Drag n' drop CSV file
3. [ ] Finish Progress Pipes and Parse sent Data (1/3)
   1. [x] Sending and Receiving Data
   2. [ ] Profile Button/Task Identifier
   3. [ ] Parse Data
4. [x] Add version migration / upgrading function.
5. [x] Disable busy Profile Buttons
6. [X] Add CSV parser
7. [x] Basic config parser
8. [x] Communication between Pool and GUI
9. [x] Prototype DataEntry window
10. [x] Prototype Profile Selector GUI
11. [x] Make a better README
12. [x] Finish Patient Thread in async.

## Tests

- Tests:
   1. Request Method Tests:
        - [X] GET       (1 Test)
        - [ ] POST      (WIP)
        - [ ] HEAD      (Not Planned)
        - [ ] PATCH     (Not Planned)
        - [ ] PUT       (Not Planned)
        - [ ] DELETE    (Not Planned)
        - [ ] OPTIONS   (Not Planned)
   2. ```Request.MakeRequests()```:
        - [ ] Test Session Retention
   3. CSV Parsing Tests:
        - [x] One Line, Default             (100 x 2)
        - [x] One Line, Random Separator    (100 x 2)
        - [ ] Multiple Line, Special Characters
   4. ```Request.ParseLink()```:
      - [ ] Clean link of Illegal Chars


## Refactor Goalz

- Refactor Code:
  - [ ] Refactor Main
  - [x] Add info to Objects
  - [ ] Cleanup Objects
  - [ ] Cleanup Config
  - [ ] cleanup Requests

## Config

For storing pre-made profiles, I chose [hjson](https://hjson.github.io) because of the following reasons:

1. It's pretty hard to f*ck up.
2. You can add **comments**.
3. No need for quotes.
4. Serialize friendly (comes from json).
5. And most importantly, human friendly json.