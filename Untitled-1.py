import math
print(math.pi)
colors = [0,170*math.pi, 340 * math.pi]
for x in range(int(85*math.pi/2)):
    for i in range(len(colors)):
        colors[i] = (math.sin((x + 255*i)/255)*255+255)/2
    print(colors)

colors = [0, 0, 0]  # Initialize the colors list with the desired starting values

for x in range(int(85 * int(math.pi)/2)):
    for i in range(len(colors)):
        if i == 0:
            colors[i] = (math.sin((x/255)*255) +255)/2
        elif i == 1:
            colors[i] = (math.sin((x / 255) + 2 * math.pi * (2 / 3)) * 255 + 255) / 2
        elif i == 2:
            colors[i] = (math.sin((x / 255) + 2 * math.pi * (1 / 3)) * 255 + 255) / 2
    print(colors)