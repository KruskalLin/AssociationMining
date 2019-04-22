import numpy as np
import matplotlib.pyplot as plt

y1 = [440309,486892]
y2 = [229779, 429002]
y3 = [126719, 51861]

x = ['Grocery Store', 'UNIX usage']

plt.figure()
plt.plot(x, y3, mec='b', label='FPGrowth')
plt.plot(x, y2, mec='r', label='Apriori')
plt.plot(x, y1, ms=10, label='Baseline')
plt.legend()
plt.xlabel("dataset")
plt.ylabel("time(ms)")
plt.show()