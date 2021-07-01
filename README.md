# Requests Template Manager

Simple Requests Manager/Profiler/Executer.
Make request templates and run them easily using csv files as input params.
Currently project is in alpha, use with caution!

## Requirements

- Python >= 3.10b3
- venv: Run ``` pip install -r Requirements.txt ``` in venv

## TODO

Listed from most to least important.

1. [ ] Make a template Editor (Most Important)
2. [ ] Fix Config Profile Bug (WIP)
3. [ ] Refactor Code (3/10)
4. [ ] Drag n' drop CSV file
5. [x] Disable busy Profile Buttons
6. [ ] Finish Progress Pipes and Parse sent Data (2/5)
7. [ ] Specialize requests based on method
8. [ ] Make tests:
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
9. [x] Add version migration / upgrading function.
10. [X] Add CSV parser
11. [x] Communication between Pool and GUI
12. [x] Make a better README
13. [x] Basic config parser
14. [x] Prototype DataEntry window
15. [x] Prototype Profile Selector GUI
16. [x] Finish Patient Thread in async.

## Config

For storing pre-made profiles, I chose [hjson](https://hjson.github.io) because of the following reasons:

1. It's pretty hard to f*ck up.
2. You can add **comments**.
3. No need for quotes.
4. Serialize friendly (comes from json).
5. And most importantly, human friendly json.

### Config Notes **IMPORTANT**

- Each Profile object under profiles should have a unique name/ID, E.g.

```hjson

profiles:
    [
        {
            profID1029: {...}
            profID1023678: {...}
            profWithSpecialName: {...}
```
