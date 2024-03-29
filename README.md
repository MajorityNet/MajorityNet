
## The repository is ready to do:
* Cifar10/100+svhn --> cnv_binary(BM) / vgg_binary(BM) / resnet_binary(BM)
* MNIST --> SFC / LFC


## Requirements:
```
virtualenv -p /usr/bin/python3 venv3
pip install torch torchvision numpy bokeh tensorboardX==1.6 scipy
```

Build Majority Cuda:
```
cd models/majority_cuda/ && python setup.py install
```

## Quick Start
For binarized VGG on cifar10/100, run:
```
python main_binary.py --model vgg_binary --dataset cifar10 --majority BBBBB --padding 1 --gpus=1
```

For binarized **VGG+maj3** on cifar10/100, run:
```
python main_binary.py --model vgg_binary --dataset cifar10 --majority MMMMM --padding 1 --gpus=1
```

For binarized **CNV+maj3** on cifar10/100, run:
```
python main_binary.py --model cnv_binary --dataset cifar10 --majority MMBBB --padding 0 --gpus=1
```

For binarized **CNV+maj3** on cifar10/100, run:
```
python main_binary.py --model resnet_binary --dataset cifar10 --majority BMM --gpus=0 

```

For resume
```
--resume results/cnv_binary_MMBBB_pad=0/model_best.pth.tar 
```

For MNIST
```
python main_mnist.py --gpus=1 --majority-enable --network=LFC --epochs=100
--majority-enable --> True/False flag
--network=LFC/SFC
```
