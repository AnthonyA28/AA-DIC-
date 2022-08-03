import sys
import pickle
import os 
import sys 
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import scipy.ndimage

maxes = [49, 106, 161, 216, 269, 323, 373, 427, 479, 530]

mm_per_px = 4/144


#%matplotlib qt
# when you want graphs in a separate window and

# %matplotlib inline
# when you want an inline plot


log_path = "Series_specimen_images_log-ws30-gs15/pickles/"


pickle_path = log_path 
areas= pickle.load(open(pickle_path + "areas", "rb"))
pts_x_l = pickle.load(open(pickle_path + "pts_x_l", "rb"))
times = pickle.load(open(pickle_path + "times", "rb"))
strain_xx_mat_l = pickle.load(open(pickle_path + "strain_xx_mat_l", "rb"))


print("Loaded Data ")

ptsx_avgd = np.average(pts_x_l,2)
disps_avg = - (ptsx_avgd - ptsx_avgd[0]) 

ptsx_avgdX = ptsx_avgd*mm_per_px


# plot the strain distribution over every 10 images 
import seaborn as sns
strain_xx_avgdX = []
for strain in strain_xx_mat_l:
	strain_xx = sp.ndimage.filters.gaussian_filter(strain, 0.0)
	strain_xx_avgdX.append(np.average(strain_xx,1))
palette = sns.color_palette("viridis_r", len(strain_xx_avgdX)).as_hex()
for i in np.arange(0, len(strain_xx_avgdX), 10):
	t = int(i)
	lab = "t={:d}s".format(int(times[i]))
	plt.plot(ptsx_avgdX[0], strain_xx_avgdX[t], color=palette[i], label=lab)
ax = plt.gca()
plt.ylabel(" Strain (Engineering) ")
plt.xlabel("X [mm]")
#plt.legend()
plt.show()
plt.clf()

#Plot the strain distribution at the maxes 
for i in maxes:
	t = int(i)
	lab = "t={:d}s".format(int(times[i]))
	plt.plot(ptsx_avgdX[0], strain_xx_avgdX[t], color=palette[i], label=lab)
ax = plt.gca()
plt.title("Strains at max extension")
plt.ylabel(" Strain (Engineering) ")
plt.xlabel("X [mm]")
plt.legend()
plt.show()
plt.clf()



avgs = []
globAvg = []
for strain in strain_xx_mat_l:
	strain_xx = sp.ndimage.filters.gaussian_filter(strain, 0.0)
	avgs_x = np.average(strain_xx,1)
	avg1 = np.average(avgs_x[16:23])
	avg2 = np.average(avgs_x[39:46])
	avgs.append(np.average([avg2,avg2]))
	globAvg.append(np.average(strain_xx))

plt.xlabel("Time [s]")
plt.ylabel("Strain (Engineering)")
plt.plot(times, avgs, label="Hard Domain")
plt.plot(times, globAvg, label="Bulk Average")
plt.legend()
plt.show()


import pandas as pd


ptsx_avgdX[0]
for i in maxes:
	strain_xx_avgdX[t]
my_array = np.array(np.array([times, globAvg,avgs]).T)

df = pd.DataFrame(my_array, columns = ['Time [s]', 'Global Avg','Hard Domain Avg '])

df.to_csv("data.csv")