import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp

def compute_row (info):
    row, ymax, ymin, xmax, xmin, width, height, max_steps = info
    
    imag = row_to_imag(row, ymax, ymin, height)
    
    values = []
    
    for col in range(width):
        real = col_to_real(col, xmax, xmin, width)
        c = complex(real, imag)
        values.append(escape_steps(c, max_steps))
    
    return values

def escape_steps(c, max_steps):
    z = 0
    escape_step = max_steps
    for i in range(max_steps):
        z = z*z + c
        if abs(z)>2:
            escape_step = i
            break
    return escape_step

def col_to_real(col, xmax, xmin, width):
    start = xmin
    end = xmax
    x = col
    fraction = x/width
    size_of_range = end - start
    value = start + fraction * size_of_range
    return value
    

def row_to_imag(row, ymax, ymin, height):
    start = ymax
    end = ymin
    y = row
    fraction = y/height
    size_of_range = end - start
    value = start + fraction * size_of_range
    return value

def render (ymax, ymin ,xmax, xmin, width, height, max_steps, pool):
    jobs = [(row, ymax, ymin, xmax, xmin, width, height, max_steps) for row in range(height)]
    rows = pool.map(compute_row, jobs)
    image = np.array(rows)
    return image

if __name__ == "__main__":
    ymax = float(input("Enter YMAX: "))
    ymin = float(input("Enter YMIN: "))
    xmax = float(input("Enter XMAX: "))
    xmin = float(input("Enter XMIN: "))

    width = int(input("Enter Width: "))
    height = int(input("Enter Height: "))
    max_steps = int(input("Enter Max Steps: "))

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
    processosors = int(input("Enter the number of processors you want to use(1-18): "))
    with mp.Pool(processes = processosors) as pool:
        image = render(ymax, ymin, xmax, xmin, width, height, max_steps, pool)
        fig, ax = plt.subplots()
        im = ax.imshow(image, extent=(xmin, xmax, ymin, ymax), cmap = color)
        fig.colorbar(im, label="steps before escaping")
        ax.set_xlabel("real")
        ax.set_ylabel("imaginary")
        last = [xmin, xmax, ymin, ymax]
        def on_draw(event):
            new_xmin, new_xmax = ax.get_xlim()
            new_ymin, new_ymax = ax.get_ylim()
            new_limits = [new_xmin, new_xmax, new_ymin, new_ymax]
            flag = 0
            for i in range (4):
                if new_limits[i] != last[i]:
                    flag+=1
                    last[i] = new_limits[i]
            if flag:
                print(f"zoomed to:\nY: {last[0]}, {last[1]}\nX: {last[2]}, {last[3]}")
                new_image = render(new_ymax, new_ymin, new_xmax, new_xmin, width, height, max_steps, pool)
            else:
                new_image = image
            im.set_data(new_image)
            im.set_extent((new_xmin, new_xmax,new_ymin, new_ymax))
            im.set_clim(new_image.min(), new_image.max())
            fig.canvas.draw_idle()
            
        fig.canvas.mpl_connect("draw_event", on_draw)
        plt.show()