import numpy as np
def random_walk(n):
    x = 0
    y = 0
    for i in range(n):
        dir = np.random.choice(["north","south","west","east"])
        if dir == "north":
            y = y + 1
        elif dir == "south":
            y = y - 1
        elif dir == "west":
            x = x - 1
        elif dir == "east":
            x = x + 1
        print("the direction is:",dir,"and the values are",x,y )
    return x, y    


print(random_walk(10))