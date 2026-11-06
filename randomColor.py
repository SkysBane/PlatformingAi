from random import random
import math

def Color() -> str:
    array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
    while True:
        randomcolor = "#"
        for i in range(6):
            randomcolor += array[math.floor(random() * len(array))]
        count = 0
        for i in range(3):
            count += array.index(randomcolor[1+(i*2)])
        if count < 26 and count > 9 and not (array.index(randomcolor[1]) - array.index(randomcolor[3])) - array.index(randomcolor[5]) > 11:
            return randomcolor


