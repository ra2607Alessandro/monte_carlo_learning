import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

rng = np.random.default_rng(42) # seed

paths = 50
points = 1000

interval = [0.0, 1.0]
dt = (interval[1]- interval[0])/(points- 1)
timeline = np.linspace(interval[0],interval[1],points)

mean, sigma = 0.0, 1.0
Z = rng.normal(mean,sigma,(paths,points))
W = np.zeros((paths,points))

for idx in range(points - 1):
    W[:,idx+1] = W[:,idx] + mean*(dt) + (sigma* np.sqrt(dt))*Z[:,idx]

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
for path in range (paths):
    ax.plot(timeline,W[path,:])

#ax.set_xlabel("Time")
#ax.set_ylabel("Value")
#plt.show()
d = pd.DataFrame({'d':W[:,-1]})
sns.kdeplot(data=d,x='d',fill=True,ax=ax)
ax.set_ylim(0.0, 0.325)
ax.set_xlabel("Value Assets")
plt.show()
