# Digital Image Correlation in Python

This software will measure strains on a sequence of images using the openCV image analysis library. 

Steps:

1. Speckle your specimen so locations on it can be tracked. 
2. Take images of the specimen when it is being strained. 
3. Choose an area of interest.
4. The software will determine the displacement of speckles and then the strain.

![Tutorial](Tutorial.png)


Much of the code here was adapted from https://gitlab.com/damien.andre/pydic. Pydic is recommended in most circumstances. AA-DIC- was designed to run more efficiently when very many (>10k) images are being analyzed.  

