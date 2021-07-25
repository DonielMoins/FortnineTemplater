# Requests Template Manager

Simple Requests Manager.
Create request templates and run them easily using CSV files as input params.
Currently project is in alpha, use with caution!

## Requirements

- Python >= 3.10b3
- venv: Run ``` pip install -r Requirements.txt ``` in venv

## TODO

Listed from most to least important.

1. [x] Make a template Editor (Most Important)
2. [x] Now make the editor work!
3. [ ] Drag n' drop CSV file (Tk is very limited so this is a hard maybe)
4. [x] Finish Progress Pipes and Parse sent Data.
   1. [x] Sending and Receiving Data
   2. [x] Profile Button/Task Identifier (using profile.uuid)
   3. [x] Parse Data
5. [x] Add version migration / upgrading function.
6. [x] Disable busy Profile Buttons
7. [X] Add CSV parser
8. [x] Basic config parser
9. [x] Communication between Pool and GUI
10. [x] Prototype DataEntry window
11. [x] Prototype Profile Selector GUI
12. [x] Make a better README
13. [x] Finish Patient Thread in async.

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
  - main.py
    - [x] Add info / comments
    - [ ] Cleanup code
  - gui.py
    - [x] Add info / comments
    - [ ] Cleanup code
  - utils
    - objects.py
      - [ ] Add info / comments
      - [ ] Cleanup code
    - config.py
      - [ ] Add info / comments
      - [ ] Cleanup Code
    - requests.py
      - [ ] Add info / comments
      - [ ] Cleanup Code
    - general.py
      - [ ] Add info / comments
      - [ ] Cleanup code

## Config

For storing pre-made profiles, I chose [hjson](https://hjson.github.io) because of the following reasons:

1. It's pretty hard to mess up.
2. You can add **comments**.
3. No need for quotes.
4. Serializer-able (comes from json).
5. And most importantly, human friendly json.
