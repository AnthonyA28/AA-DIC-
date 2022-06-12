from DIC_base import perform_suite



grid_size_px 				= (10,10)
window_size_px 				= (20,20)
image_path = "Examples_images/triangle_specimen/"
ref_image = "Examples_images/triangle_specimen/image_2022-04-08_17-40-24-091-N0000000.jpg"

perform_suite(
	image_path,
	ref_image,
	window_size_px,
	grid_size_px,
	save_every=3, # Save every 2nd image parsed
	strain_type="engineering", # Engineering strain will be calculate 
	choose_area_of_interest=False, # Choose the area of interest 
	calc_positions=False, # Calculate Positions 
	calc_strains=False, # Calulate strains 
	freqs = [1] # skip images until images are 1 second apart 
	)
