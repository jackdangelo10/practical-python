# pcost.py
filename = r"Data/portfolio.csv"


def portfolio_cost(filename: str):
    lines = []
    cost = 0
    with open(filename, 'rt') as f:
        header = next(f)
        for line in f:
            row = line.split(',')
            value = float(row[2])
            amount = int(row[1])
            cost += value * amount

   
    return cost

print(portfolio_cost(filename))


# Exercise 1.27
