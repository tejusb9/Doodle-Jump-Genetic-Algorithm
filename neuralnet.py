import numpy as np
import random


class NeuralNetwork():

    def __init__(self, in_nodes, hid_nodes, out_nodes):
        
        self.input_nodes = in_nodes
        self.hidden_nodes = hid_nodes
        self.output_nodes = out_nodes
        self.weights1 = 2* np.random.random((self.input_nodes, self.hidden_nodes)) -1
        self.weights2 = 2* np.random.random((self.hidden_nodes,self.output_nodes)) -1
        self.bias1 = 2* np.random.random((self.hidden_nodes)) -1
        self.bias2 = 2* np.random.random((self.output_nodes)) -1

    # Activation functions
    def sigmoid(self, x):
        #applying the sigmoid function
        return 1 / (1 + np.exp(-x))
    
    def tanh(self,x):
        return (2 / (1 + np.exp(-2*x))) - 1
    
    def feedForward(self, inputs):
        inputs = np.asarray(inputs)
        #print("inputs ", inputs)
        #print("weights ", self.weights1)
        #print("bias ", self.bias1)
        hidden = self.sigmoid(np.dot(inputs, self.weights1)+ self.bias1)
        #print ("hidden ", hidden)
        output = self.sigmoid(np.dot(hidden, self.weights2)+ self.bias2)
        #print("output ",output)
        return output
        
    def mutate(self, rate):   
        def mutation (val):
            if (np.random.random(1) < rate):
                rand = random.gauss(0, 0.1) + val
                if (rand > 1):
                    rand = 1
                elif (rand < -1):
                    rand =-1

                return rand
            else:
                return val
        vmutate = np.vectorize(mutation)
        self.weights1 = vmutate(self.weights1)
        self.weights2 = vmutate(self.weights2)
        self.bias1 = vmutate(self.bias1)
        self.bias2 = vmutate(self.bias2)
    
    def clone(self):
        cloneBrain = NeuralNetwork(self.input_nodes, self.hidden_nodes, self.output_nodes)
        cloneBrain.weights1 = self.weights1
        cloneBrain.weights2 = self.weights2
        cloneBrain.bias1 = self.bias1
        cloneBrain.bias2 = self.bias2
        
        return cloneBrain
    
