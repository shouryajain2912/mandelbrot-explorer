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
    ymax = float(input("Enter ymax: "))
    ymin = float(input("Enter ymin: "))
    xmax = float(input("Enter xmax: "))
    xmin = float(input("Enter xmin: "))
    
    width = int(input("Enter width: "))
    if width<1:
        print("width must be a positive integer\ndefaulting to 600")
        width = 600
    height = int(input("Enter height: "))
    if height>1:
        print("height must be a positive integer\ndefaulting to 2/3*width")
        hegiht = 2/3*width
    max_steps = int(input("Enter max steps: "))
    if max_steps<1:
        print("max steps must be positive\ndefaulting to 100")

    choice = int(input("Choose color by entering the appropriate number:\n1. magma\n2. twilight\n3. viridis\n4. gray\n"))

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
    if processosors<1:
        print("number of processors must be greater than or equal to 1\ndefaulting to 1")
        processosors = 1
        
    with mp.Pool(processes = processosors) as pool:
        image = render(ymax, ymin, xmax, xmin, width, height, max_steps, pool)
        fig, ax = plt.subplots()
        im = ax.imshow(image, extent=(xmin, xmax, ymin, ymax), cmap = color)
        fig.colorbar(im, label="steps before escaping")
        ax.set_xlabel("real")
        ax.set_ylabel("imaginary")
        original = [xmin, xmax, ymin, ymax]
        last = [xmin, xmax, ymin, ymax]
        timers = []
        def repaint():
            fig.canvas.draw_idle()
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
                print(f"zoomed to:\nY: {last[2]}, {last[3]}\nX: {last[0]}, {last[1]}")
                new_image = render(new_ymax, new_ymin, new_xmax, new_xmin, width, height, max_steps, pool)
                im.set_data(new_image)
                im.set_extent((new_xmin, new_xmax,new_ymin, new_ymax))
                im.set_clim(new_image.min(), new_image.max())
                timers.clear()
                timer = fig.canvas.new_timer(interval=50)
                timer.single_shot = True
                timer.add_callback(repaint)
                timer.start()
                timers.append(timer)
        fig.canvas.mpl_connect("draw_event", on_draw)
        plt.show()