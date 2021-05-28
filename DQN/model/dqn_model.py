import torch
import torch.nn as nn
import torch.nn.functional as F

class DQN(nn.Module):

    def __init__(self, input_dimension, output_dimension):
        super(DQN, self).__init__()
        self.layer_1 = nn.Linear(
            in_features=input_dimension, out_features=64)
        self.layer_2 = nn.Linear(in_features=64, out_features=128)
        self.layer_3 = nn.Linear(in_features=128, out_features=64)

        #size = 128 * output_dimension
        input_size = 64 

        self.output_layer = nn.Linear(
            in_features=input_size, out_features=output_dimension)

    def forward(self, net_input):
        #net_input = net_input.view(net_input.size(0), -1)
        layer_1_output = F.relu(self.layer_1(net_input))
        layer_2_output = F.relu(self.layer_2(layer_1_output))
        layer_3_output = F.relu(self.layer_3(layer_2_output))

        #output = self.output_layer(layer_3_output.view(layer_3_output.size(0), -1))
        output = self.output_layer(layer_3_output)
        return output