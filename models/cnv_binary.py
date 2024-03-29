import torch
import torch.nn as nn
import torchvision.transforms as transforms
import logging
from torch.autograd import Function
from .binarized_modules import  BinarizeLinear,BinarizeConv2d,FCMaj3
from .majority3_cuda import * 

def make_layers(cfg, maj_cfg, padding=0, bias=False, backprop='normalConv'):
    layers = list()
    in_channels = 3
    for i,v in enumerate(cfg):
        print("layer %d:"%i)
        mp = (v[-1]=='M')
        if mp:
            filters = int(v[:-2])
        else:
            filters = int(v[:])

        maj = False if (i==0) else (maj_cfg[i-1]=="M") # first Conv always BNN, then maj_cfg
        
        if maj:
            conv2d = Maj3(in_channels, filters, kernel_size=3, backprop=backprop, padding=padding)
            print(" maj", in_channels, filters, 3, backprop, padding)
        else:
            conv2d = BinarizeConv2d(in_channels, filters, kernel_size=3, padding=padding, bias=bias)
            print(" bnn", in_channels, filters, 3, padding, bias)

        if mp:
            layers += [conv2d, nn.MaxPool2d(kernel_size=2, stride=2)]
            print(' mp', 3, 2)
        else:
            layers += [conv2d]

        layers += [nn.BatchNorm2d(filters), nn.Hardtanh(inplace=True)]
        print(" bn", filters)
        print(" htanh")
        in_channels = filters

    return nn.Sequential(*layers)


cnv_binary_cfg = ['64','64+M','128','128+M','256','256+M']
#cnv_binary_cfg = ['64','64+M','128','144+M','256','256+M']

class CNV_Binary(nn.Module):

    def __init__(self, num_classes=1000, majority="MMBBB", backprop='majority', padding=1):
        super(CNV_Binary, self).__init__()
        #self.infl_ratio=1;
        self.padding=padding
        assert len(majority)==5, "Majority configuration string must be for 5 layers only"

        self.features = make_layers(cnv_binary_cfg, majority, padding=self.padding, bias=False, backprop=backprop)

        self.out_features = 256*4*4 if self.padding==1 else 256
        
        self.classifier = nn.Sequential(
            #BinarizeLinear(self.out_features, 512, bias=False),###########################
            FCMaj3(self.out_features+2, 512),###########################
            nn.BatchNorm1d(512),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(512, 512, bias=False),
            nn.BatchNorm1d(512),
            nn.Hardtanh(inplace=True),
            #nn.Dropout(0.5),
            BinarizeLinear(512, num_classes, bias=False),
            nn.BatchNorm1d(num_classes, affine=False),
            nn.LogSoftmax()
        )

        self.regime = {
            0: {'optimizer': 'Adam', 'betas': (0.9, 0.999),'lr': 5e-3},
            40: {'lr': 1e-3},
            80: {'lr': 5e-4},
            100: {'lr': 1e-4},
            120: {'lr': 5e-5},
            140: {'lr': 1e-5}
        }

    def forward(self, x):
        x = self.features(x)
        x = x.view(-1, self.out_features)
        x = torch.nn.functional.pad(x, (1,1), "constant", -1.0) ###########################
        x = self.classifier(x)
        return x

def cnv_binary(**kwargs):
    num_classes = kwargs.get('num_classes')
    backprop = kwargs.get('backprop')
    majority = kwargs.get('majority')
    padding = kwargs.get('padding')
    return CNV_Binary(num_classes, majority, backprop, padding)
