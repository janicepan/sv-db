The files needed to capture the SV data include:

sv_city.blend: Blender file with city and all external models packed. Requires Blender 2.77.
	Email janicepan@utexas.edu for the link to download the .blend file;  ~640MB
sv_city_capture.py: Python script to capture scenes within sv_city.blend.
	Three customizable lines: 	line 174: savePath_SV; specifies directory to which to save image data
								line 175: camAnglesDeg_SV; specifies rotation of the 4 cameras;
								default [0] only captures with the traditional SV configuration
								line 195: pathname; specifies path to external .csv files
test4_captureLocations_all.csv: manually-specified capture locations within the city in sv_city.blend
SunColors.csv: manually-specified ambient lighting conditions

Sample call:
<path-to-blender>/blender <path-to-sv_city>/sv-city.blend --background --python <path-to-python-script>/sv_city_capture.py -- <arg1> <arg2> <arg3> <arg4> <arg5>
where the arguments are:
<arg1> = starting index of scene to capture; indices are w.r.t. test4_captureLocations_all.csv; 0-indexed
<arg2> = number of scenes to capture, beginning with <arg1>
<arg3> = total number of scene augmentations *in addition to* the initial capture; we used 20 for a total of 21 augmentations
<arg4> = start index of augmentations to capture in this call to sv_city_capture.py (e.g., 0 to start at the beginning)			
<arg5> = number of augmentations starting with <arg4> to capture in this call to sv_city_capture.py
	*<arg4> and <arg5> allow for breaking up data collection into multiple jobs
	
The files needed to process the captured data:
preprocess_scenes_multiangle.py: combine rendered seeds and create a stitched (i.e., distorted) SV image
preprocess_functions.py: used in preprocess_scenes_multiangle.py
preprocess_depth_multiangle.m: combine depth maps of different seeds to reduces firefly effect
Data/calibration/*: all the calibration data used to generate stitched images