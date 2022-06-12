
'''
	tracks a matrix of positions on a series of images 
''' 



import numpy as np
import cv2 as cv2
import sys
import copy
import os
import regex as re
import DIC_base
from datetime import datetime
import time
import argparse
from glob import glob
import math 

image_path_name = r"/pos_images"
save_file_type="jpg"




# Parses when the images are in the format ( image_[Y]-[M]-[D]_[h]-[m]-[s]-[z]-N[c].png )
def parse_time_from_file(file_name):
	file_name = file_name.rsplit(r"/",1)[1]
	date = file_name.split(".",1)[0]
	date = date+"000"
	split = date.split("_")
	date_str = split[1] + "--" + split[2]
	date_str = date_str.rsplit("-",1)[0]
	split = date_str.rsplit("-",1)
	pre_millis = split[0]
	millis = split[1]
	millis = millis[0:3]+"000"
	date_str = date_str[:len(date_str)-2]
	date_str_with_microseconds = pre_millis +"-"+ millis
	date = datetime.strptime(date_str_with_microseconds, '%Y-%m-%d--%H-%M-%S-%f')
	return date

def get_grid(img_path, grid_size_px, **kwargs):

	imgFile = cv2.imread(img_path, 0)
	area_of_interest = kwargs['area_of_interest']
	points_x = np.float64(np.arange(area_of_interest[0][0], area_of_interest[1][0], grid_size_px[0]))
	points_y = np.float64(np.arange(area_of_interest[0][1], area_of_interest[1][1], grid_size_px[1]))
	points_list   = []

	for x in points_x:
		for y in points_y:
			points_list.append(np.array([np.float32(x),np.float32(y)]))

	points_list = np.array(points_list)

	return points_list, points_x, points_y

def find_nearest(array,value):
	idx = np.searchsorted(array, value, side="left")
	if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
		return idx-1
	else:
		return idx

def get_positions(areas_of_interest,\
					image_path,\
					log_path,\
					grid_size_px,\
					window_size_px ,\
					save_every=0,\
					time_between_images=0,\
					start_index=0,\
					stop_index=100000000,\
					ranges=[],\
					freqs=[0.001]):
	'''
		areas_of_interest: The area of interest in pixel coordinates 
		image_path: The path to the images to perform DIC on 
		log_path: TJhe path to where the result images will be saved 
		grid_size_px: The space between each consecutive point to be tracked 
		window_size_px : The size of the tracking winodw on each point 
		save_every: The frequency of images to be saved (save_every=1 will save each image analyzed)
		time_between_images: The time between each consecutive image in seconds, useful for when the image names do not tell the time. 
		stop_index: The first image to be tracked 
		ranges: A list of ranges 
		freqs: A list time deltas in which the corresponding range will analyze images, useful for when images need to be skipped  
			Setting freqs[0.1] will parse images 10 every second
	'''


	use_ref_pos = False  #TODO: #p3 If there is an efficient way to integrate a reference (to account for backgorund moevement that would be nice. )
	ref_points_list = []
	if len(areas_of_interest)==2:
		use_ref_pos = True 
		ref_area = areas_of_interest[1]
		x = int((ref_area[0][0] + ref_area[1][0])/2.0)
		y = int((ref_area[0][1] + ref_area[1][1])/2.0)
		ref_points_list = np.array([np.array([np.float32(x),np.float32(y)])])

	area_of_interest = areas_of_interest[0]

	print("image_path ", image_path)

	times = []
	images = []
	images = [y for x in os.walk(image_path) for y in glob(os.path.join(x[0], '*.tif')) + glob(os.path.join(x[0], '*.tiff')) + glob(os.path.join(x[0], '*.png')) + glob(os.path.join(x[0], '*.jpg'))]

	# Sort the images by the first number in the filename
	images.sort(key=lambda f: int(re.sub('\D', '', f)))
	images = images[start_index:stop_index]

	print("Reference Image: ", str(images[0]))

	# Get the list of points within the area_of_interest 
	points_list, points_x, points_y = get_grid(images[0], grid_size_px, area_of_interest=area_of_interest)

	out_img_dir = log_path+image_path_name
	if not os.path.exists(out_img_dir):
		os.makedirs(out_img_dir)

	t = 0 
	init_time = t
	if time_between_images == 0:
		init_time = parse_time_from_file(images[0])
	else:
		init_time = t
		t += time_between_images/1000000

	img_mat_prev = cv2.imread(images[0], 1)
	current_points_list = points_list
	total_len_images = len(images)
	mat_l = []
	print("total_len_images: ", total_len_images)

	#get a list of images and times 
	i = 0
	images_to_parse = []
	while i < total_len_images: #and i >= start_index and i < stop_index:
		images_to_parse.append(images[i])
		if time_between_images == 0:
			cur_time = parse_time_from_file(images[i])
		else:
			cur_time = t 
			t += time_between_images/1000000
		try:
			delta_time = (cur_time-init_time).total_seconds()
		except Exception as err:
			delta_time = (cur_time-init_time)
		times.append(delta_time)
		i += 1
	images = images_to_parse

	print(len(images))

	assert len(ranges)+1 == len(freqs)

	freq = freqs[0]
	_range = times[-1]
	if len(ranges) > 0 :
		_range = ranges[0]

	print("Creating list of images to correlate: ")
	
	times_to_parse = []
	images_to_parse = []
	t = 0 
	i = -1
	prev_index = -1
	count = 0 
	while True:
		index = find_nearest(times,t)
		if index != prev_index:
			prev_index = index
			times_to_parse.append(times[index])
			images_to_parse.append(images[index])
			count += 1 
			print( "(",str(count),"/",str(total_len_images),") Adding file: " , "/".join(images[index].split("/")[-2:]), end=" | ")
			print("time : {:.2f}".format(times[index]), " of {:.2f}".format(times[-1]),  " , {:.2f}".format(t/times[-1]*100), " %") 
		t += freq
		if t > _range:
			i += 1
			print(i)
			if i == len(ranges)-1:
				freq = freqs[i+1]
				_range = times[-1]
			elif i < len(ranges):
				freq = freqs[i+1]
				_range = ranges[i]
			else:
				break
	times = times_to_parse
	images = images_to_parse


	print(len(times))
	print(len(images))

	i = 0
	save_every_i = 0
	len_images = len(images)
	while i < len_images: #and i >= start_index and i < stop_index:
		
		print("Computing positions on image " + str(i) +  " of " + str(len_images) + ", image=(" + images[i].split("/")[-1], end=")")

		img_mat_cur = cv2.imread(images[i])
		lk_params = dict( winSize  = window_size_px, maxLevel = 50,
						criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 500, 0.0003))
		
		if (use_ref_pos):
			ref_points_list, st, err = cv2.calcOpticalFlowPyrLK(img_mat_prev, img_mat_cur, ref_points_list, None, **lk_params)
			print(ref_points_list)
			import time  
			time.sleep(10)

		
		current_points_list, st, err = cv2.calcOpticalFlowPyrLK(img_mat_prev, img_mat_cur, current_points_list, None, **lk_params)
		img_mat_prev = img_mat_cur
		st = np.array(st) 
		err = np.array(err) 

		mat_l.append(np.array(current_points_list))

		save_every_i  += 1
		if save_every > 0 and save_every_i >= save_every:
			save_every_i = 0 
			save_name = out_img_dir + r"/"+images[i].split(r"/")[-1].split(".")[0]+"."+save_file_type
			print(".. Saving image to " , save_name  , end="\n")
			p_size = int(grid_size_px[0]/2)
			DIC_base.draw_opencv(images[i], point=current_points_list, pointf=points_list, p_color=(255,0,0), filename=save_name, p_size=p_size)
		else:
			print()
		i += 1

	num_pt_x = len(points_x)
	num_pt_y = len(points_y)
	return mat_l, times, images, num_pt_x, num_pt_y







if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Get Displacements in a sequence of DIC images .')
	parser.add_argument('--image_path', required=True, metavar='<path>', type=str, help='The path to the images to be parsed')
	parser.add_argument('--log_path', required=True, metavar='<path>', type=str, help='The path to the log directory (where the data Area_of_interes.md is stored) and the results will be saved. ')
	parser.add_argument('--grid_size_px', metavar='<int>', type=int)
	parser.add_argument('--window_size_px', metavar='<int>', type=int)
	parser.add_argument('--save_every', metavar='<int>', type=int, help='Frequency of images to save.   ')
	parser.add_argument('--time_between_images', required=False, metavar='<int>', type=int, help='Time between consecutive images [microseconds] if the date is not in the filename in format ')


	args = parser.parse_args()

	log_path = args.log_path
	image_path = args.image_path

	# Input default arguments
	time_between_images = 0
	save_every = 0 
	if args.save_every != None:
		save_every = args.save_every
	if args.time_between_images != None:
		time_between_images = args.time_between_images
	if args.grid_size_px != None:
		grid_size_px = (args.grid_size_px,args.grid_size_px)
	if args.window_size_px != None:
		window_size_px = (args.window_size_px, args.window_size_px)
