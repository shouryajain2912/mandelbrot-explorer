import numpy as np
import matplotlib.pyplot as plt

def escape_steps(c, max_steps):
    z = 0
    escape_step = max_steps
    for i in range(max_steps):
        z = z*z + c
        if abs(z)>2:
            escape_step = i
            break
    return escape_step

def col_to_real(col, xmax, xmin):
    start = xmin
    end = xmax
    x = col
    fraction = x/WIDTH
    size_of_range = end - start
    value = start + fraction * size_of_range
    return value
    

def row_to_imag(row, ymax, ymin):
    start = ymax
    end = ymin
    y = row
    fraction = y/HEIGHT
    size_of_range = end - start
    value = start + fraction * size_of_range
    return value

ymax = float(input("Enter YMAX: "))
ymin = float(input("Enter YMIN: "))
xmax = float(input("Enter XMAX: "))
xmin = float(input("Enter XMIN: "))

WIDTH = int(input("Enter Width: "))
HEIGHT = int(input("Enter Height: "))
MAX_STEPS = int(input("Enter Max Steps: "))

choice = int(input("Choose color by entering the appropiate number:\n1. magma\n2. twilight\n3. viridis\n4. gray\n"))

if choice == 1:
    color = "magma"
elif choice == 2:
    color = "twilight"
elif choice == 3:
    color = "viridis"
elif choice == 4:
    color = "gray"
else:
    print("Incorrect input, defaulting to magma:")
    color = "magma"
    
image = np.zeros((HEIGHT, WIDTH))

for row in range(HEIGHT):
    imag = row_to_imag(row, ymax, ymin)
    for col in range(WIDTH):
        real = col_to_real(col, xmax, xmin)
        
        c = complex(real, imag)
        image[row, col] = escape_steps(c, MAX_STEPS)
        
plt.imshow(image, extent = (xmin, xmax, ymin, ymax), cmap=color)
plt.colorbar(label="steps before escaping")
plt.xlabel("real")
plt.ylabel("imaginary")
plt.show()