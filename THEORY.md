## Theory
If you are like me... coming into Computer Vision with no coding experience or knowledge,  
this repository is meant to serve as an introductory guide to the basic **Theory** of Computer Vision  
& uses LeNet-5 Architecture to demonstrate how to **Implement** it in code.

## Computer Vision Theory Basics

1. Testing & Training
2. Perceptron
3. Back propagation
4. Gradient Descent

## Convulational Neural Network (CNN) terms to know:

**Key Terms to Know**
- Kernal
- Stride
- Padding
- Pooling:
  - Max Pooling
  - Average Pooling
- Flattening

## LeNet5-Implementation

![Image of LeNet-5 Architecture](https://miro.medium.com/max/4348/1*PXworfAP2IombUzBsDMg7Q.png)

Progress:
- [x] Setup
- [ ] Coding Base Structure
- [ ] Training
- [ ] Testing
- [ ] Iteration


Setup (Language and Virtual Environment Setup & Libraries & Dependencies Installation):

1. I created a project folder in my Desktop named 'ComputerVision' by typing `mkdir Desktop/ComputerVision` into my terminal command line
2. I created a **Virtual Environment** to separate my system libraries from my project libraries using the built-in 'venv' library that comes with python 3 versions. Python 3.7.7 was already downloaded within my system directory. In terminal I entered  
`python3 -m venv Desktop/ComputerVision/CV_Venv`
3. In order to activate my **Virtual Environment** in the command line I entered  
`source Desktop/ComputerVision/CV_Venv/bin/activate`
4. From here I installed *numpy, torch, torchvision* with
    pip install numpy
    pip install torch torchvision
5. I am using VS code for my text editor
