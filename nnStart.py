from main import Main
import numpy as np
import pickle
import os

def formNextGeneration(results, candidatesPercent, mutatePercent):
    futureBrains = []
    results.sort(key=lambda result: result[1], reverse=True)

    population = len(results)

    # I wanna keep the best one around
    futureBrains.append(results[0][0].clone())
    futureBrains.append(results[1][0].clone())
    futureBrains.append(results[2][0].clone())
    population -= 3

    for i in range(population):
        if i < population*mutatePercent:
            futureBrains.append(results[i % int(candidatesPercent*population)][0].clone().mutate(0.1, 0.1))
        else:
            if (i % int(candidatesPercent*population) == i % 3):
                futureBrains.append(results[i % int(candidatesPercent*population)][0].createOffspring(results[(i+1) % 3][0], 0.5))
            else:
                futureBrains.append(results[i % int(candidatesPercent*population)][0].createOffspring(results[i % 3][0], 0.5))

    #for i in range(population):
    #    if i < population / 2:
    #        futureBrains.append(results[0 + int(i/(population/4))][0].mutate(0.4, 0.1).clone())
    #    else:
    #       futureBrains.append(results[int((i-int(population/2))/4)][0].createOffspring(results[i+1-int(population/2)][0], 0.5))
    
    return futureBrains

def save(results, filename):
    model_folder_path = f'./nn_models'
    if not os.path.exists(model_folder_path):
        os.makedirs(model_folder_path)
    filename = os.path.join(model_folder_path, filename)

    with open(filename+".pkl", "wb") as f: pickle.dump(results, f)

def load(filename):
    model_folder_path = f'./nn_models'
    filename = os.path.join(model_folder_path, filename)
    with open(filename+".pkl", "rb") as f: return pickle.load(f)

game = Main(7, controlledByNN=True, populationSize=25, display=True, timedDeath=False, nnTimeTick=False)

#below is to load in old brains, skipping it generates default ones

brains = []
old_results = load("21 21 3/level7")
for n in range(len(old_results)):
   brains.append(old_results[n][0])
game.resetAndRestartNNBrains(brains)


for generation in range(200):
    results = game.run()
    if not results:
        exit()
    bestFitness = max(r[1] for r in results)
    completed = sum(r[2] for r in results)

    #to train until completed:
    if completed:
        save(results, "21 21 3/level7")
        break
    
    print(
            f"Generation {generation + 1}: "
            f"Amount of them = {len(results) }, "
            f"Best fitness = {bestFitness:.2f}, "
            f"Completed = {completed}"
        )

    newBrains = formNextGeneration(results, 0.21, 0.9)
    game.resetAndRestartNNBrains(newBrains)

results.sort(key=lambda result: result[1], reverse=True)
if input("Would you like to save progress?\n") == "y":
    save(results, "21 21 3/level7")
    print("saved!")
game.resetAndRestartNNBrains([results[0][0]])
game.display = True
game.nnTimeTick = True

print("Best fitness:", results[0][1])
print("Completed:", sum(r[2] for r in results))
if input("Would you like to see the winning brain?\n") == "y":
    #results[0][0].printLayerData()
    print(results[0][1])
    while True:
        results = game.run()
        if not results:
            break
        game.resetAndRestartNNBrains([results[0][0]])

game.quitPygame()

#results.sort(key=lambda result: result[1], reverse=True)



