# -*- coding: utf-8 -*-'''

"""
Sean Sanpietro
CPS 310 Midterm
"""
"""
Created on Wed Oct 14 09:50:47 2026

@author: Ssanp
"""

import json
import math
import random
import time


WIDTH = 18
HEIGHT = 8
MAX_HUMANS = WIDTH * HEIGHT
STARTING_HUMANS = 13
STARTING_ZOMBIES = 2
MAX_ROUNDS = 100
HUMAN_REPRODUCTION_CHANCE = 0.08
ZOMBIE_DEATH_CHANCE = 0.02
ROUND_DELAY = 0.5


class GameState:
    def __init__(self, round_number, humans, zombies):
        self.round_number = round_number
        self.humans = humans
        self.zombies = zombies


class MemoryStorage:
    def __init__(self):
        self.state = None

    def load(self):
        return self.state

    def save(self, state):
        self.state = state


class FileStorage:
    def __init__(self, file_name):
        self.file_name = file_name

    def load(self):
        try:
            with open(self.file_name, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            return None

        return GameState(data["round_number"], data["humans"], data["zombies"])

    def save(self, state):
        data = {
            "round_number": state.round_number,
            "humans": state.humans,
            "zombies": state.zombies
        }

        with open(self.file_name, "w") as file:
            json.dump(data, file)


class ZombieSimulation:
    def __init__(self, storage):
        self.storage = storage

    def random_position(self):
        return [
            random.randint(0, WIDTH - 1),
            random.randint(0, HEIGHT - 1)
        ]

    def create_state(self):
        humans = []
        zombies = []

        for i in range(min(STARTING_HUMANS, MAX_HUMANS)):
            humans.append(self.random_position())

        for i in range(STARTING_ZOMBIES):
            zombies.append(self.random_position())

        return GameState(0, humans, zombies)

    def run(self):
        state = self.storage.load()

        if state is None:
            state = self.create_state()

        print("ZOMBIE SIMULATOR")

        while state.round_number < MAX_ROUNDS:
            state.round_number += 1

            self.move_humans(state)
            self.move_zombies(state)
            self.infect_humans(state)
            self.reproduce_humans(state)
            self.kill_zombies(state)

            self.storage.save(state)
            self.display_map(state)

            if len(state.humans) == 0:
                print("All humans have been infected!")
                print("The zombies win!")
                return

            if len(state.zombies) == 0:
                print("There are no zombies left!")
                print("The humans survive!")
                return

            time.sleep(ROUND_DELAY)

        print("The simulation reached the maximum number of rounds.")

    def move_humans(self, state):
        for human in state.humans:
            move = random.choice([[1, 0], [-1, 0], [0, 1], [0, -1]])
            human[0] = max(0, min(WIDTH - 1, human[0] + move[0]))
            human[1] = max(0, min(HEIGHT - 1, human[1] + move[1]))

    def move_zombies(self, state):
        for zombie in state.zombies:
            if len(state.humans) == 0:
                return

            closest_human = min(
                state.humans,
                key=lambda human: math.dist(zombie, human)
            )

            if zombie[0] < closest_human[0]:
                zombie[0] += 1
            elif zombie[0] > closest_human[0]:
                zombie[0] -= 1

            if zombie[1] < closest_human[1]:
                zombie[1] += 1
            elif zombie[1] > closest_human[1]:
                zombie[1] -= 1

    def infect_humans(self, state):
        infected = []

        for human in state.humans[:]:
            if human in state.zombies:
                state.humans.remove(human)
                infected.append(human)

        state.zombies.extend(infected)

    def reproduce_humans(self, state):
        new_humans = []
        open_spaces = MAX_HUMANS - len(state.humans)

        if len(state.humans) < 2 or open_spaces <= 0:
            return

        for i in range(len(state.humans)):
            for j in range(i + 1, len(state.humans)):
                if len(new_humans) >= open_spaces:
                    break

                human1 = state.humans[i]
                human2 = state.humans[j]

                if math.dist(human1, human2) <= 2:
                    if random.random() < HUMAN_REPRODUCTION_CHANCE:
                        x = (human1[0] + human2[0]) // 2
                        y = (human1[1] + human2[1]) // 2
                        new_humans.append([x, y])

        state.humans.extend(new_humans)

    def kill_zombies(self, state):
        remaining_zombies = []

        for zombie in state.zombies:
            if random.random() > ZOMBIE_DEATH_CHANCE:
                remaining_zombies.append(zombie)

        state.zombies = remaining_zombies

    def display_map(self, state):
        grid = []

        for y in range(HEIGHT):
            row = []

            for x in range(WIDTH):
                row.append(".")

            grid.append(row)

        for x, y in state.humans:
            grid[y][x] = "H"

        for x, y in state.zombies:
            grid[y][x] = "Z"

        print("\nROUND", state.round_number)

        for row in grid:
            print("".join(row))

        print("Humans:", len(state.humans), "/", MAX_HUMANS)
        print("Zombies:", len(state.zombies))


def main():
    storage = MemoryStorage()
    # storage = FileStorage("zombie_state.json")

    game = ZombieSimulation(storage)
    game.run()


if __name__ == "__main__":
    main()