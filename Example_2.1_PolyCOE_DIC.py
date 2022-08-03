from DIC_base import perform_suite



grid_size_px 	= (15,15)
window_size_px 	= (30,30)
image_path = "Series_specimen_images/"
ref_image = "Series_specimen_images/image_2022-04-23_15-28-04-631-N0000000.tif"

perform_suite(
	image_path,
	ref_image,
	window_size_px,
	grid_size_px,
	iterative_correlation=True,
	save_every=1, # Save every image parsed
	strain_type="engineering", # Engineering strain will be calculate
	choose_aoi= [[(1143, 628), (1937, 738)]], # Choose the area of interest
	draw_strain_global_min=0, # lower limit for the strain legend
	draw_strain_global_max=5 # upper limit for the strain legend
	)
