hi
this is my first upload for my upcoming solution for the:
Vinícius da Silva, Tiago Novello, Hélio Lopes and Luiz Velho. 2021.
*Real-time rendering of complex fractals.* arXiv:2102.01747.
https://arxiv.org/abs/2102.01747


About the code:
Inputs:
 - takes in input of initial dimensional limits
 - takes in input of width and height (these give number of pixels that will be calculated)
 - can take in input of 1-4 to select from 4 different colour schemes
 - max steps help set the limit to max number of times the for loop runs to see if the coordinate (pixel) goes out of the loop
 - you can enter number of processors you can use. Code says 1-18 because my laptop has that many, you can enter as many as your computer has

Processing:
 - it takes the number and for every pixel (every coordinate using the width and height)
 - every pixel's coordinate value is calculated by using the x and y limits
 - then every pixel is put thru the loop of z = z*z + c whre the pixel coordinates is c and z = 0 in the start to find the number of steps before it escapes (modulus of z becomes 2 or greater)
 - when the image opens you can zoom in and the zoomed in coordinates are used to recalculate, you get the same resolution (width and height and max steps and number of processors used)

my current findings from doing this and using different parameters:
 - using more cores doesnt give linearly more speed in calculations but it does increase
 - the number of max steps help to differentiate between the pixels more as you increase the number of them (you can keep it one and then 5 and then 10 to see what i mean easily)
 - using higher numbers in width and height also means higher compute times (obviously but it grows fast), a 600x400 vs a 1200x800 is a 4x increase in compute since the number of pixels quadrubles with height and width both doubling

about the project:
i found this paper randomly while going to ideas for a hackathon, couldnt attend the hackathon but this idea intrigued me. so this project is me learning everything i need to know about this background of fractals with coding and 3d graphics to solve any problems in the paper (still havent read it just the title intrigued me so i started this lol)
i have not used ai in the code at all, all made by me as ive learnt
i only used ai to generate the script i ran to find timings for when the code is run with differnt parameters (bench_live.py)

will keep updating this
