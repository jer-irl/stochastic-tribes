# stochastic-tribes

## Background

I started this as my first real non-script python project.  After learning in biology about Hardy-Weinberg equillibria, I was interested in exploring the circumstances in which these ideal conditions aren't met.

## Description

The board is initialized with a random set of entities (referred to as hamsters in the code).  Each entity has an age (visually size), a position, a bearing, and a single genetic constant (float between 0 and 1, visually color).  For fun, I also gave them names popular in the early 20th century.

For each tick, each hamster moves, with components of movement determined by the bearing, nearby neighbors, and a random factor.  Currently, all members are of the subclass "RacistHam," which are influenced more by neighbors of similar color.  This produces rudimentary flocking.

Hamsters can also breed with nearby hamsters with a cooldown period, preferring those similar to their own color.  The offspring will be the average color of the two parents.  There is a local carrying capacity though, and if there are too many neighbors, or a parent is too old, it won't breed.

Over time, you can see "tribes" of one color form, and if two tribes collide, if their colors are close, they may mix, or if they are far, they may just cohabitate.

## Status

The simulation isn't well balanced, and eventually the hamsters usually die out.  Also, unlike more developed flocking algorithms, hamsters don't mind being highly compact.

The simulation is also very innefficient, and when a lot of hamsters are on the board, it will visibly slow down.  The first thing to try to improve performance is to change the python lists holding the objects to sets.  Because of the iterative nature, this should improve performance.  There are also several places in the code where I'm sure there are unnecessary reads and searches made (object-orientation is dangerous for the unwary).  I was considering reimplementing in C, and still may do so in the future.

## Requirements

- tkinter
- Python 3 standard library
