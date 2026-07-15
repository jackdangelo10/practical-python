# bounce.py
#
# Exercise 1.5
starting_height = 100
factor = 3/5
i = 0
current_height = starting_height * factor
for i in range(0,10):
    print(f"{i+1} ", round(current_height, 4))
    current_height = current_height * factor
