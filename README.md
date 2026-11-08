hi

# Mandelbrot Explorer

this is my first upload for my upcoming solution for:
Vinícius da Silva, Tiago Novello, Hélio Lopes and Luiz Velho. 2021.

*Real-time rendering of complex fractals.* arXiv:2102.01747.

https://arxiv.org/abs/2102.01747

(might not be a solution might just be an implementation of what they did, im not sure yet dont know enough to understand the paper)

### about the code:

#### how to run:
 - install `numpy` and `matplotlib` (`pip install numpy matplotlib`)
 - run `python mandelbrot-final.py` to run the project
 - run `bench_live.py` to run the benchmark **THIS DOES TAKE HOURS SO BE PREPARED**

#### inputs:
 - takes in input of initial dimensional limits
 - takes in input of width and height (these give number of pixels that will be calculated)
 - can take in input of 1-4 to select from 4 different colour schemes (magma, twilight, virdis, gray)
 - max steps help set the limit to max number of times the for loop runs to see if the coordinate (pixel) giving a point of escape
 - you can enter number of processors you can use. Code says 1-18 because my laptop has that many, you can enter as many as your computer has

#### processing:
 - it takes the number and for every pixel (every coordinate using the width and height)
 - every pixel's coordinate value is calculated by using the x and y limits
 - then every pixel is put thru the loop of z = z*z + c where the pixel coordinates is c and z = 0 in the start to find the number of steps before it escapes (modulus of z becomes greater than 2)
 - when the image opens you can zoom in and the zoomed in coordinates are used to recalculate, you get the same resolution (width and height and max steps and number of processors used)
 - pressing home resets back to the original limits

#### my current findings from doing this and using different parameters:
 - using more cores doesnt give linearly more speed in calculations but it does increase (16 cores give 8.8x the speedup compared to 1 for 9600x6400 200 steps)
 - the number of max steps help to differentiate between the pixels more as you increase the number of them (you can keep it one and then 5 and then 10 to see what i mean easily)
 - using higher numbers in width and height also means higher compute times (obviously but it grows fast), a 600x400 vs a 1200x800 is a 4x increase in compute since the number of pixels quadruples with height and width both doubling

### TRY THIS:
whole set:
 - YMAX 1, YMIN -1, XMAX 1, XMIN -2, 200 steps
seahorse valley:
 - YMAX 0.13333, YMIN 0.06667, XMAX -0.7, XMIN -0.8, 200 steps
elephant valley:
 - YMAX 0.4, YMIN -0.04, XMAX -0.34, XMIN 0.22, 300 steps
mini mandelbrot on the needle:
 - YMAX 0.03333, YMIN -0.03333, XMAX -1.7, XMIN -1.8, 300 steps
triple spiral valley:
 - YMAX 0.674, YMIN 0.634, XMAX -0.058, XMIN -0.118, 300 steps
sehouse spiral (deep): (this is quite deep so you can only zoom a few times)
 - YMAX 0.11603, YMIN 0.10937, XMAX -0.7403, XMIN -0.7503, 500 steps 

### Bugs and Limitations:
 - no bugs indentified for now, let me know if you find them
 - float64 runs out at rougly 1e-13 per pixel

### about the project:
i found this paper randomly while going through ideas for a hackathon, couldnt attend the hackathon but this idea intrigued me. so this project is me learning everything i need to know about this background of fractals with coding and 3d graphics to solve any problems in the paper (still havent read it just the title intrigued me so i started this lol)
wrote the code myself (0 ai generated code in the actual project)
claude was used as tutor and code reviewer tho
bench_live.py was only AI-generated upload

#### Upcoming Roadmap
 - implemetn error handling (negative numbers, fractions getting to small, etc)
 - numpy speedup
 - julia sets
 - distance functions and ray marching

will keep updating this
