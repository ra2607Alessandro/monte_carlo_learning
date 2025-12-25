import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


rng = np.random.default_rng(42) #to reproduce a random series of nums starting from a seed

#set the number of paths and the number of time steps
paths = 50
steps = 1000


#set mean (in standard BM is 0) and volatily which is unity
mean, sigma = 0.0 , 1.0

# use rng.normal and create a matrix 2x2 with the mean, sigma, paths and times steps as factors
Z = rng.normal(mean, sigma, (paths, steps))

# create interval in time and dt, then create the plot of the timelines with numpy linspace taking the interval and the steps
interval = [ 0.0 ,1.0 ]
dt = ( interval[1] - interval[0] ) / ( steps - 1 ) 

timeline = np.linspace(interval[0] , interval[1] , steps)

# create a new series with zeros with numpy starting from the paths and points and create a loop for the standard BM:
W = np.zeros((paths,steps))
# use [:, idx] which is the vectorized notation 
for idx in range(steps - 1):
    W[ : , idx + 1 ] = W[:,idx] + np.sqrt(dt) * Z[:,idx]

fig, ax = plt.subplots(1, 1, figsize=(12, 8)) #use the subplots componenet
#loop around the paths, plot the time plot and the series of 0 with this vectorized path W[path,:], then show
for path in range(paths):
    ax.plot(timeline,W[path,:])

#ax.set_xlabel("Time")
#ax.set_ylabel("Value")


final_values = pd.DataFrame({'final_values': W[:, -1]}) # creating a Dataframe with pandas
sns.kdeplot(data=final_values, x='final_values', fill=True, ax=ax) # using seaborn for a kernel that estimates prob distr from a finite sample data
ax.set_ylim(0.0, 0.325)
ax.set_xlabel('Final Values of Asset Paths')
plt.show()

