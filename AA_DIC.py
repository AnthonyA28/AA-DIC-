from get_area_of_interest import get_area_of_interest
from get_positions import get_positions
from get_strains import get_strains 
from draw_strains import draw_strains
import pickle
import os 
import sys 
import numpy as np 

CHOOSE_AREA_OF_INTEREST 	= True
CALC_POSITIONS 				= True
CALC_STRAINS 				= True
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
	choose_area_of_interest=CHOOSE_AREA_OF_INTEREST,\
	calc_positions=CALC_POSITIONS,\
	calc_strains=CALC_STRAINS,\
	first_imgs=1,\
	last_imgs=1,\
	save_every=1,\
	skip_img_interval=0,\
	start_index=0,\
	stop_index=100000000000,\
	pickle_path="",\
	log_path="",
	ranges=[], 
	freqs=[0.001],
	log_path_prefix=""
	):

	if log_path == "":
		log_path = image_path[:-1] + log_path_prefix+ "_log-ws"+str(window_size_px[0]) + "-gs" + str(grid_size_px[0]) + "/"
	if pickle_path == "":
		pickle_path = log_path + "/"+"pickles/"
	os.makedirs(pickle_path, exist_ok = True)
	os.makedirs(log_path, exist_ok = True)

	if CHOOSE_AREA_OF_INTEREST and not CALC_POSITIONS:
		print("ERROR: CALC_POSITIONS==False and CHOOSE_AREA_OF_INTEREST==True ")
		areas = get_area_of_interest(log_path, ref_image)
		pickle.dump(areas, open(pickle_path + "areas", "wb"))
		# sys.exit()
		return 
		

	if(calc_positions):
		if(choose_area_of_interest):
			areas = get_area_of_interest(log_path, ref_image)
			pickle.dump(areas, open(pickle_path + "areas", "wb"))
		else:
			areas = pickle.load(open(pickle_path + "areas", "rb"))
		global times
		global images 
		pts_l, times, images, num_pt_x, num_pt_y 	= get_positions(areas, image_path, log_path, grid_size_px, window_size_px, save_every=save_every,  start_index=start_index, stop_index=stop_index, ranges=ranges, freqs=freqs)
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



if __name__ == "__main__":
	print("This is not meant to be run as main.")


