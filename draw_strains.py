import sys
import numpy as np
import cv2 as cv2
import seaborn as sns
import argparse
import json 
import os 
import scipy as sp
import scipy.ndimage
from PIL import Image

use_init_pos = False

def get_rgb(hex):
	hex = hex[1:]
	return tuple(int(hex[i:i+2], 16) for i in (4, 2, 0))



def draw_strains(strain_mat_l, pt_mat_x_list, pt_mat_y_list,log_path, file_names, use_init_pos=False, use_global= True, global_max=None, global_min=None, save_every=1, binarize=False, threshold=0.1, gausFilt=0, rotation=0):


	strain_min_maxes = []
	image_names = []

	os.makedirs(log_path, exist_ok = True)
	strain_min_l = np.min(np.min(strain_mat_l, 1),1)
	strain_max_l = np.max(np.max(strain_mat_l, 1),1)

	strain_global_max = np.amax(strain_max_l)
	strain_global_avg = np.average(strain_max_l)

	print("Drawing strains to images")
	# f = open(log_path + r"/strains_xx_AVG.csv", "w")
	save_every_i = 0 
	if global_max is None:
		global_max = np.max(strain_mat_l)
	if global_min is None:
		global_min = np.min(strain_mat_l)
	for q in range(1, len(strain_mat_l), save_every):
		img_name = file_names[q]
		image_names.append(img_name)
		
		print("Plotting Image " +str(q) + " of " + str(len(strain_mat_l)) + ", " + str(img_name))

		strain      = strain_mat_l[q]
		if gausFilt > 0:
			strain = sp.ndimage.filters.gaussian_filter(strain, gausFilt)
		strain_max  = strain_max_l[q]
		strain_min  = strain_min_l[q]
		if binarize:
			upper = 1
			lower = 0 
			strain = np.where(strain>threshold, upper, lower)
			strain_max = 1
			strain_min = 0

		locs_arr_x = pt_mat_x_list[q]
		locs_arr_y = pt_mat_y_list[q]

		if use_init_pos:
			locs_arr_x = pt_mat_x_list[0]
			locs_arr_y = pt_mat_y_list[0]
			img_name = file_names[0]

		image = cv2.imread(img_name, 1)
		img_name = file_names[q] # This has to be reset otherwise when using initial position, all will save to initial

		palette = sns.color_palette("rocket_r", 100).as_hex()

		strain_range = strain_max - strain_min
		strain_min_maxes.append((strain_min, strain_max))

		strain_avgYs = []
		for i in range(len(locs_arr_x)):
			strain_avgYs.append(np.average(strain[i]))
		strain_avgYs_MAX = np.amax(strain_avgYs)


		Tstrain = np.transpose(strain)
		strain_avgXs = []
		for i in range(len(locs_arr_x[0])):
			strain_avgXs.append(np.average(Tstrain[i]))
		strain_avgXs_MAX = np.amax(strain_avgXs)


		dx = locs_arr_x[1][0] - locs_arr_x[0][0] # the pixel length between each point in the x direction
		dy = locs_arr_y[0][1] - locs_arr_y[0][0] # and in the y direction


		baseline = int(locs_arr_y[0][0] - dy)

		for x_i in range(2, len(locs_arr_x)):
			for y_i in range(len(locs_arr_x[0])):
				x = int(locs_arr_x[x_i][y_i])
				y = int(locs_arr_y[x_i][y_i])
			
				if use_global:
					color_int = int((strain[x_i][y_i]-global_min)/(global_max-global_min)*99)
				else:
					color_int = int((strain[x_i][y_i]-strain_min)/strain_range*99)
				color = palette[color_int]
				thickness = -1 # -1 will fill
				wid = dx
				heig = dy
				image = cv2.rectangle(image, (x,y),(int(x+wid), int(y+heig)), get_rgb(color), thickness)

		y , x, = image.shape[0], image.shape[1]
		image = Image.fromarray(image)
		image  = image.transpose(rotation)
		image = np.asarray(image)
		
	
		wid = 100
		heig = 25
		x -= int(wid*1.1)
		y -= int(heig *1.1 )
		font = cv2.FONT_HERSHEY_SIMPLEX
		fontScale = 1

		print("global_max", global_max)
		print("global_min", global_min)

		for i in np.linspace(global_min, global_max, 10):
			color_int = int((i - global_min)/(global_max-global_min)*99)
				
			color = palette[color_int]
			
			pos = (int(x-100), int(y-50) )
			image = cv2.rectangle(image, pos,(int(x+wid), int(y+heig)), get_rgb(color), thickness)
			
			pos = (x, y)
			cv2.putText(image, "{:.2f}".format(i), pos, font, fontScale, get_rgb("#FFFFFF"), 4 , cv2.LINE_AA)
			
			y -= heig*3
			
		thickness = 2
		pos = (40, 80)
		
		save_name = log_path + r"/" + img_name.split(r"/")[-1].split(".")[0] + ".jpg"
		cv2.imwrite( save_name, image)
		print("saving " + str(save_name))
		
		
		
	return image_names, strain_min_maxes, palette



# for i in range(0, len(strain_xx_mat_l), save_every):
#     strain_xx = strain_xx_mat_l[i]
#     xmin = 0 
#     xmax = (np.max(pts_x_l[0]) - np.min(pts_x_l[0]))*mm_per_px
#     ymin = 0
#     ymax = (np.max(pts_y_l[0]) - np.min(pts_y_l[0]))*mm_per_px
	
#     c = plt.imshow(strain_xx, cmap='rocket_r', extent=( ymin, ymax, xmin, xmax))
#     plt.colorbar(c)


#     # colours = im.cmap(im.norm(np.unique(c))
	
#     plt.show()
#     plt.clf()
