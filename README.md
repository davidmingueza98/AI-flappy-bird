[![HitCount](http://hits.dwyl.com/davidmingueza98/flappy-bird-AI.svg)](http://hits.dwyl.com/davidmingueza98/flappy-bird-AI)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

# FLAPPY BIRD AI

## About the project

An Artificial Intelligence that plays Flappy Bird using [NEAT](https://neat-python.readthedocs.io/en/latest/).

Code extracted from the [original repository](https://github.com/techwithtim/NEAT-Flappy-Bird) from techwithtim.

This script generates an autonomous agent that achieves high scores in the game in short training time.

This implementation uses **genetic algorithms** with a Feed Forward network. The configuration is defined in `config-feedforward.txt`.

The algorithm trains itself in some iterations until the agent gets high scores. At the end, the agent generated is able to play the game indefinitely during hours.

## Installation

Create a virtual environment and run: `pip install -r requirements.txt`

## How to run

Execute *game.py* to generate the agent and see the game.
