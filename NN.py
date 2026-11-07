import numpy as np
import copy
rng = np.random.default_rng()


class NNLayer():
    def __init__(self, inputSize, outputSize, *, generator=None):
        generator = rng if generator is None else generator
        self.w = generator.normal(0, 0.5, (inputSize, outputSize))
        self.b = np.zeros(outputSize)

    def forward(self, inputs):
        return np.tanh(np.asarray(inputs) @ self.w + self.b)

    def getWeights(self):
        return self.w

    def printInfo(self):
        print("Biases: " + str(self.b))
        print("Weights: ")
        print(self.w)
        print("Shape: " + str(self.w.shape))

    

class NeuralNetwork():
    def __init__(self, inputSize, outputSize, hiddenLayers = 0, hiddenLayerSize = None, *, generator=None):
        self.layers = []
        if hiddenLayerSize is None:
            hiddenLayerSize = int((inputSize + outputSize)/2)
        for i in range(hiddenLayers+1):
            if i == 0:
                front = inputSize
            else: 
                front = hiddenLayerSize
            if i == hiddenLayers:
                back = outputSize
            else:
                back = hiddenLayerSize
            self.layers.append(NNLayer(front, back, generator=generator))

        self.inputSize = inputSize
        self.outputSize = outputSize
        self.hiddenLayers = hiddenLayers
        self.hiddenLayerSize = hiddenLayerSize

    def printLayerData(self):
        for i in range(len(self.layers)):
            print("------------------------\nLayer",i+1)
            self.layers[i].printInfo()
            print()

    def forward(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs

    def mutate(self, strength=0.05, prob=0.05, *, generator=None):
        generator = rng if generator is None else generator
        for layer in self.layers:
            mask = generator.random(layer.w.shape) < prob
            mutations = generator.normal(0, strength, layer.w.shape)

            layer.w += mask * mutations

            biasMask = generator.random(layer.b.shape) < prob
            biasMutations = generator.normal(0, strength, layer.b.shape)

            layer.b += biasMask * biasMutations
        return self

    def createOffspring(self, other, takeOverPercent=0.5, *, generator=None):
        generator = rng if generator is None else generator
        if len(self.layers) != len(other.layers):
            raise ValueError("Networks have different amounts of layers")

        for a, b in zip(self.layers, other.layers):
            if a.w.shape != b.w.shape or a.b.shape != b.b.shape:
                raise ValueError("Networks have different layer sizes")

        offspring = self.clone()

        for childLayer, a, b in zip(offspring.layers, self.layers, other.layers):
            weightMask = generator.random(a.w.shape) < takeOverPercent
            biasMask = generator.random(a.b.shape) < takeOverPercent

            childLayer.w = np.where(weightMask, b.w, a.w)
            childLayer.b = np.where(biasMask, b.b, a.b)

        return offspring

    def clone(self):
        return copy.deepcopy(self)
