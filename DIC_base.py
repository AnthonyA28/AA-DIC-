import numpy as np
import cv2 as cv2
import sys
import math
import glob
from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from scipy.interpolate import griddata
from scipy.interpolate import Rbf
import scipy.interpolate
import copy
import os
import matplotlib.colors as colors


from get_positions import get_img_list
from get_positions import get_positions
from get_strains import get_strains 
from draw_strains import draw_strains
import pickle
import os 
import sys 
import numpy as np 

CHOOSE_AREA_OF_INTEREST     = True
CALC_POSITIONS              = True
CALC_STRAINS                = True
times = []
images = []


def loadAllData(pickle_path):
	areas = pickle.load(open(pickle_path + "areas", "rb"))
	pts_l = pickle.load(open(pickle_path + "pts_l", "rb"))
	times = pickle.load(open(pickle_path + "times", "rb"))
	images = pickle.load(open(pickle_path + "images", "rb"))
	num_pt_x = pickle.load(open(pickle_path + "num_pt_x", "rb"))
	num_pt_y = pickle.load(open(pickle_path + "num_pt_y", "rb"))
	strain_xx_mat_l = pickle.load(open(pickle_path + "strain_xx_mat_l", "rb"))
	strain_yy_mat_l = pickle.load(open(pickle_path + "strain_yy_mat_l", "rb"))
	strain_xy_mat_l = pickle.load(open(pickle_path + "strain_xy_mat_l", "rb"))
	pts_x_l = pickle.load(open(pickle_path + "pts_x_l", "rb"))
	pts_y_l = pickle.load(open(pickle_path + "pts_y_l", "rb"))


	return areas, pts_l, times, images, num_pt_x, num_pt_y, strain_xx_mat_l, strain_yy_mat_l, strain_xy_mat_l, pts_x_l, pts_y_l

def perform_suite(image_path, \
	ref_image, \
	window_size_px,\
	grid_size_px,\
	strain_type="engineering", \
	iterative_correlation=False, \
	log_path_prefix="", \
	save_every=1,\
	start_index=0,\
	stop_index=100000000000,\
	pickle_path="",\
	log_path="", \
	ranges=[],\
	freqs=[0.001], \
	choose_aoi=CHOOSE_AREA_OF_INTEREST,\
	calc_positions=CALC_POSITIONS,\
	calc_strains=CALC_STRAINS
	):

	if log_path == "":
		log_path = image_path[:-1] + log_path_prefix+ "_log-ws"+str(window_size_px[0]) + "-gs" + str(grid_size_px[0]) + "/"
	if pickle_path == "":
		pickle_path = log_path + "/"+"pickles/"
	os.makedirs(pickle_path, exist_ok = True)
	os.makedirs(log_path, exist_ok = True)

	if choose_aoi==True:
		areas = get_area_of_interest(ref_image, grid_size_px, window_size_px)

		pickle.dump(areas, open(pickle_path + "areas", "wb"))
	elif choose_aoi == False:
		print("Using previous area of interest")
		areas = pickle.load(open(pickle_path + "areas", "rb"))
	else:
		areas = choose_aoi
		pickle.dump(areas, open(pickle_path + "areas", "wb"))
		
	images, times = get_img_list(image_path, freqs, ranges, start_index, stop_index,time_between_images=0)
	pickle.dump(images, open(pickle_path + "images", "wb"))
	pickle.dump(times, open(pickle_path + "times", "wb"))

	if(calc_positions):
		pts_l, num_pt_x, num_pt_y   = get_positions(areas, log_path, images, times, grid_size_px, window_size_px,iterative_correlation=iterative_correlation, save_every=save_every)

		pickle.dump(grid_size_px,open(pickle_path + "grid_size_px", "wb"))
		pickle.dump(window_size_px,open(pickle_path + "window_size_px", "wb"))
		pickle.dump(pts_l,open(pickle_path + "pts_l", "wb"))
		pickle.dump(times,open(pickle_path + "times", "wb"))
		pickle.dump(images,open(pickle_path + "images", "wb"))
		pickle.dump(num_pt_x,open(pickle_path + "num_pt_x", "wb"))
		pickle.dump(num_pt_y,open(pickle_path + "num_pt_y", "wb"))

		pts_x_l = []
		pts_y_l = []
		for i in range(0, len(times)):
			ptsy = np.array([p[1] for p in pts_l[i]]).reshape((num_pt_x, num_pt_y))
			ptsx = np.array([p[0] for p in pts_l[i]]).reshape((num_pt_x, num_pt_y))
			pts_x_l.append(ptsx)
			pts_y_l.append(ptsy)

		pickle.dump(pts_x_l,open(pickle_path + "pts_x_l", "wb"))
		pickle.dump(pts_y_l,open(pickle_path + "pts_y_l", "wb"))

	else:
		pts_l = pickle.load(open(pickle_path + "pts_l", "rb"))
		times = pickle.load(open(pickle_path + "times", "rb"))
		images = pickle.load(open(pickle_path + "images", "rb"))
		num_pt_x = pickle.load(open(pickle_path + "num_pt_x", "rb"))
		num_pt_y = pickle.load(open(pickle_path + "num_pt_y", "rb"))        
		pts_x_l = pickle.load(open(pickle_path + "pts_x_l", "rb"))
		pts_y_l = pickle.load(open(pickle_path + "pts_y_l", "rb"))


	if(calc_strains):
		strain_xx_mat_l, strain_yy_mat_l, strain_xy_mat_l = get_strains(strain_type, pts_l, images, times, num_pt_x, num_pt_y)
		pickle.dump(strain_xx_mat_l, open(pickle_path + "strain_xx_mat_l", "wb"))
		pickle.dump(strain_yy_mat_l, open(pickle_path + "strain_yy_mat_l", "wb"))
		pickle.dump(strain_xy_mat_l, open(pickle_path + "strain_xy_mat_l", "wb"))
	else:
		strain_xx_mat_l = pickle.load(open(pickle_path + "strain_xx_mat_l", "rb"))
		strain_yy_mat_l = pickle.load(open(pickle_path + "strain_yy_mat_l", "rb"))
		strain_xy_mat_l = pickle.load(open(pickle_path + "strain_xy_mat_l", "rb"))


	draw_strains(strain_xx_mat_l,pts_x_l, pts_y_l, log_path+"/Strain_xx", images, save_every=save_every, gausFilt=0.5)

	return times, strain_xx_mat_l, strain_yy_mat_l, strain_xy_mat_l, images


def get_area_of_interest(ref_image, grid_size_px, window_size_px):

	def handle_input(PreliminaryImage, grid_size_px, window_size_px):
		image = PreliminaryImage
		global areas
		areas = []
		area = [(), ()]

		def click_and_crop(event, x, y, flags, area):
			if event == cv2.EVENT_LBUTTONDOWN:
				print("Cursor: " , str(x)+", ",  str(y))
				area[0] = (x, y)
			elif event == cv2.EVENT_LBUTTONUP:
				area[1] = (x, y)
				points_list,points_x,points_y  = get_grid(image, grid_size_px, area_of_interest=area)
				Newimage = draw_opencv(image, point=points_list,p_color=(0,255,0), square_width=window_size_px[0], p_size=1)
				Newimage = draw_opencv(Newimage, point=points_list,p_color=(0,0,255), p_size=1)
				x1 = int((area[0][0] + area[1][0])/2.0)
				y1 = int((area[0][1] + area[1][1])/2.0)
				cv2.circle(Newimage, (x1, y1), 1, (255,0,0), -1)
				cv2.putText(Newimage, str(len(areas) + 1), area[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255))
				cv2.imshow('image', Newimage)
				areas.append(copy.copy(area))
		clone = image.copy()
		cv2.namedWindow('image', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('image', image.shape[1], image.shape[0])
		cv2.setMouseCallback("image", click_and_crop, area)
		# keep looping until the 'c' key is pressed
		while True:
			# display the image and wait for a keypress
			cv2.imshow("image", image)
			key = cv2.waitKey(1) & 0xFF
			# if the 'r' key is pressed, reset the cropping region
			if key == ord("r"):
				image = clone.copy()
				areas = []
				# if the 'c' key is pressed, break from the loop
			elif key == ord("c"):
				cv2.destroyWindow('image')
				break
		return areas
	image_mat = cv2.imread(ref_image)
	areas = handle_input(image_mat, grid_size_px, window_size_px)
	return areas

def draw_opencv(image, *args, **kwargs):
	"""A function with a lot of named argument to draw opencv image
 - 'point' arg must be an array of (x,y) point
 - 'p_color' arg to choose the color of point in (r,g,b) format
 - 'pointf' to draw lines between point and pointf, pointf 
   must be an array of same lenght than the point array
 - 'l_color' to choose the color of lines
 - 'grid' to display a grid, the grid must be a grid object
 - 'gr_color' to choose the grid color
 - 'p_size' to choose pixel size of the poiints  """

	p_size = 8
	l_size=1
	if 'p_size' in kwargs: 
	  p_size = kwargs['p_size']
	if type(image) == str :
		image = cv2.imread(image, 0)
		image = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)

	if 'text' in kwargs:
		 text = kwargs['text']
		 image = cv2.putText(image, text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),4)
	
	frame = image

	scale = 1. if not 'scale' in kwargs else kwargs['scale']
	if 'pointf' in kwargs and 'point' in kwargs:
		assert len(kwargs['point']) == len(kwargs['pointf']), 'bad size'
		l_color = (0, 255, 0) if not 'l_color' in kwargs else kwargs['l_color']
		for i, pt0 in enumerate(kwargs['point']):
			pt1 = kwargs['pointf'][i]
			if np.isnan(pt0[0])==False and np.isnan(pt0[1])==False and np.isnan(pt1[0])==False and np.isnan(pt1[1])==False :
				 disp_x = (pt1[0]-pt0[0])*scale
				 disp_y = (pt1[1]-pt0[1])*scale
				 frame = cv2.line(frame, (int(pt0[0]), int(pt0[1])), (int(pt0[0]+disp_x), int(pt0[1]+disp_y)), l_color, l_size)
	
	if  'point' in kwargs:
		p_color = (0, 255, 255) if not 'p_color' in kwargs else kwargs['p_color']
		for pt in kwargs['point']:
			if not np.isnan(pt[0]) and not np.isnan(pt[1]):
				x = int(pt[0])
				y = int(pt[1])
				# p_color = (255,0,0)
				if 'square_width' in kwargs:
					start_point = (int(x-kwargs['square_width']/2), int(y-kwargs['square_width']/2))
					end_point = (int(x+kwargs['square_width']/2), int(y+kwargs['square_width']/2))
					frame = cv2.rectangle(frame, start_point, end_point, p_color, p_size)
				else:
					frame = cv2.circle(frame, (x, y), p_size, p_color, -1)

	if 'filename' in kwargs:
		 cv2.imwrite( kwargs['filename'], frame)
		 return

	if 'show' in kwargs:
		cv2.namedWindow('image', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('image', frame.shape[1], frame.shape[0])
		cv2.moveWindow('image', 40,30)  # Move it to (40,30)
		cv2.imshow('image',frame)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		return 
	return frame 

def get_grid(img_File, grid_size_px, **kwargs):

	# imgFile = cv2.imread(img_path, 0)
	area_of_interest = kwargs['area_of_interest']
	points_x = np.float64(np.arange(area_of_interest[0][0], area_of_interest[1][0], grid_size_px[0]))
	points_y = np.float64(np.arange(area_of_interest[0][1], area_of_interest[1][1], grid_size_px[1]))
	points_list   = []

	for x in points_x:
		for y in points_y:
			points_list.append(np.array([np.float32(x),np.float32(y)]))

	points_list = np.array(points_list)

	return points_list, points_x, points_y


if __name__ == "__main__":
	print("This is not meant to be run as main.")

