import scipy.io as sio
import scipy.misc
import os
import numpy as np
import sys
from math import pi, sin, cos, sqrt, atan
from PIL import Image
from preprocess_functions import combine_seeds
from preprocess_functions import defineOutputRegions, getProjectionMat_vc, getTransformedSV_AutoDots

# FOR CITY SCENES
# usage: python preprocess_scenes_multiangle.py -- <sceneStartIdx> <num_scenes_to_process>
#	where sceneStartIdx is the index of the scene from which to begin processing and
#	num_scenes_to_process is the number of scenes beginning with sceneStartIdx to process
#		- allows for breaking up the data processing into multiple parallel jobs
# Used Python 2.7.9

def main():

	sceneStartIdx = int(sys.argv[-2])
	num_scenes_to_process = int(sys.argv[-1])
	print('Processing scenes ' + str(sceneStartIdx) + ' - ' + str(sceneStartIdx+num_scenes_to_process-1))
	projdir = '<path-to-captured-stereo-data>/Stereo'
	savedir = projdir + '_preprocessed'
	calibDataDir = os.path.join('Data','calibration')

	#if not os.path.exists(savedir):
	#	os.makedirs(savedir)

	# database parameters
	num_seeds = 3
	num_versions = 21 #1 (original) + 20 (number of augmentations)
	num_scenes = 200 #index starts at 0

	#virtual camera parameters
	vc_height = 15
	vc_f = 0.5      #check if this is even used
	vc_rotx = 0     #virtual camera rotation in x [degrees]
	vc_roty = 0     #rotation in y [degrees]
	vc_rotz = 0     #rotation in z [degrees]

	#load chart points
	mat_contents = sio.loadmat(os.path.join(calibDataDir,'chartPoints.mat'))
	distorted = mat_contents['distorted']
	undistorted = mat_contents['undistorted']
	world = mat_contents['world']

	distorted_xs = []
	distorted_ys = []
	undistorted_xs = []
	undistorted_ys = []
	world_xs = []
	world_ys = []
	for camNum in range(4):
		distorted_xs_cam = []
		distorted_ys_cam = []
		undistorted_xs_cam = []
		undistorted_ys_cam = []
		world_xs_cam = []
		world_ys_cam = []
		for ptNum in range(8):
			distorted_xs_cam.append(distorted['xs'][0][0][camNum][0][ptNum][0])
			distorted_ys_cam.append(distorted['xs'][0][0][camNum][0][ptNum][0])
			undistorted_xs_cam.append(undistorted['xs'][0][0][camNum][0][ptNum][0])
			undistorted_ys_cam.append(undistorted['xs'][0][0][camNum][0][ptNum][0])
			world_xs_cam.append(world['xs'][0][0][camNum][0][ptNum][0])
			world_ys_cam.append(world['ys'][0][0][camNum][0][ptNum][0])
		distorted_xs.append(distorted_xs_cam)
		distorted_ys.append(distorted_ys_cam)
		undistorted_xs.append(undistorted_xs_cam)
		undistorted_ys.append(undistorted_ys_cam)
		world_xs.append(world_xs_cam)
		world_ys.append(world_ys_cam)

	#load intrinisic parameters
	mat_contents = sio.loadmat(os.path.join(calibDataDir,'intrinsicParams.mat'))
	intrinsicParams = mat_contents['intrinsicParams']
	distCenterX = []
	distCenterY = []
	distFocalLength = []
	for camNum in range(4):
		distCenterX.append(intrinsicParams['distCenterX'][0][0][camNum][0])
		distCenterY.append(intrinsicParams['distCenterY'][0][0][camNum][0])
		distFocalLength.append(intrinsicParams['distFocalLength'][0][0][camNum][0])

	intrinsicParams = {'distCenterX': distCenterX, 'distCenterY': distCenterY, 'distFocalLength': distFocalLength}

	#load extrinsic parameters
	mat_contents = sio.loadmat(os.path.join(calibDataDir,'extrinsicParams.mat'))
	extrinsicParams = mat_contents['extrinsicParams']

	R_w2c = []
	t_w2c = []
	R_c2w = []
	t_c2w = []
	for camNum in range(4):
		R_w2c_cam = []
		t_w2c_cam = []
		R_c2w_cam = []
		t_c2w_cam = []
		for row in range(3):
			t_w2c_cam.append(extrinsicParams['t_w2c'][0][0][0][camNum][row][0])
			t_c2w_cam.append(extrinsicParams['t_c2w'][0][0][0][camNum][row][0])
			for col in range(3):
				R_w2c_cam.append(extrinsicParams['R_w2c'][0][0][0][camNum][row][col])
				R_c2w_cam.append(extrinsicParams['R_c2w'][0][0][0][camNum][row][col])
		R_w2c.append(np.reshape(R_w2c_cam,[3,3]))
		t_w2c.append(t_w2c_cam)
		R_c2w.append(np.reshape(R_c2w_cam,[3,3]))
		t_c2w.append(t_c2w_cam)

	extrinsicParams = {'R_w2c': R_w2c, 't_w2c': t_w2c, 'R_c2w': R_c2w, 't_c2w': t_c2w}

	R1_w2c = R_w2c[0]
	R2_w2c = R_w2c[1]
	R3_w2c = R_w2c[2]
	R4_w2c = R_w2c[3]

	t1_w2c = t_w2c[0]
	t2_w2c = t_w2c[1]
	t3_w2c = t_w2c[2]
	t4_w2c = t_w2c[3]

	t1_c2w = np.dot(np.transpose(-R1_w2c),t1_w2c)
	t2_c2w = np.dot(np.transpose(-R2_w2c),t2_w2c)
	t3_c2w = np.dot(np.transpose(-R3_w2c),t3_w2c)
	t4_c2w = np.dot(np.transpose(-R4_w2c),t4_w2c)

	outputDim = [720, 720]
	imW = outputDim[0]
	imH = outputDim[1]
	s = 1 #scale
	imW = int(imW/s)
	imH = int(imH/s)

	camLabels = defineOutputRegions(imH, imW, 0, 0)

	# ASSIGN VIRTUAL CAMERA PARAMETERS
	cc = (t1_c2w + t2_c2w + t3_c2w + t4_c2w)/4
	cc = cc[0:2]

	vc_params = {'tx': 0, 'ty': 0,'tz': 0, 'rotx': 0, 'roty': 0, 'rotz':0, 'f': 0}

	#rotation
	vc_params['rotx'] = 0
	vc_params['roty'] = 0
	vc_params['rotz'] = 0

	vc_params['tx'] = cc[0] #translation; in world coordinates
	vc_params['ty'] = cc[1]
	vc_params['tz'] = vc_height*100 #height in cm

	vc_params['f'] = vc_f

	vc_proj_mat = getProjectionMat_vc(vc_params) #projection matrix

	# Perspective image dimensions (undistorted fisheye)
	wpersp = 1920
	hpersp = 1080

	# Compute camera centers
	inputDim = [1280, 720]
	Xc_undist = [hpersp/2, wpersp/2]
	Xc_fish = [inputDim[1]/2, inputDim[0]/2]

	# Visualization parameters
	step_size = 1
	maxZ = 500 #maximum visualization height; [m]

	X = np.linspace(-imW/2, imW/2, imW/s)
	Y = np.linspace(-imH/2, imH/2, imH/s)
	xwmesh, ywmesh = np.meshgrid(X,Y)
	zwmesh = np.zeros(xwmesh.shape)

	vis_params = {'step_size': step_size, 'maxZ': maxZ, 'xwmesh': xwmesh, 'ywmesh': ywmesh, 'zwmesh': zwmesh, 'imW': imW, 'imH': imH, 'scale': s, 'Xc_undist': Xc_undist, 'Xc_fish': Xc_fish}

	cam_names = ['0sv_PERSP', '1front_PANO', '2right_PANO', '3rear_PANO', '4left_PANO']
	image_suff = '.png'

	for sceneIdx in range(sceneStartIdx,sceneStartIdx+num_scenes_to_process):
		for versionIdx in range(num_versions):
			for seedIdx in range(num_seeds):
				for camIdx in range(len(cam_names)):
					image_root = cam_names[camIdx] + '_PNG_' + str(sceneIdx) + '_v' + str(versionIdx)
					if camIdx == 0:
						image_filtered = combine_seeds(projdir, image_root, image_suff, num_seeds)
						scipy.misc.imsave(os.path.join(savedir,image_root + image_suff), image_filtered)
					else:
						for angle_idx in range(7):
							image_filtered = combine_seeds(projdir+str(angle_idx), image_root+'_a'+str(angle_idx), image_suff, num_seeds)
							scipy.misc.imsave(os.path.join(savedir,image_root+'_a'+str(angle_idx)+image_suff), image_filtered)

			img1 = scipy.misc.imread(os.path.join(savedir,'1front_PANO_PNG_' + str(sceneIdx) + '_v' + str(versionIdx) + '_a3' + image_suff))
			img2 = scipy.misc.imread(os.path.join(savedir,'2right_PANO_PNG_' + str(sceneIdx) + '_v' + str(versionIdx) + '_a3' + image_suff))
			img3 = scipy.misc.imread(os.path.join(savedir,'3rear_PANO_PNG_' + str(sceneIdx) + '_v' + str(versionIdx) + '_a3' + image_suff))
			img4 = scipy.misc.imread(os.path.join(savedir,'4left_PANO_PNG_' + str(sceneIdx) + '_v' + str(versionIdx) + '_a3' + image_suff))

			imgs = [img1, img2, img3, img4]

			trImgs = []
			for imgNo in range(4):
				img = imgs[imgNo]
				trImg = getTransformedSV_AutoDots(imgNo, img, vc_params, intrinsicParams, extrinsicParams, vis_params)
				#scipy.misc.imsave(os.path.join(projdir, 'transformed' + str(sceneIdx) + '_' + str(imgNo+1) + '_python.png'), trImg)
				trImgs.append(trImg)

			outputIm = np.zeros(trImg.shape,'uint8')
			for iIdx in range(imH):
				for jIdx in range(imW):
					camNum = int(camLabels[iIdx,jIdx])
					trImg = trImgs[camNum-1]
					outputIm[iIdx, jIdx, :] = trImg[iIdx, jIdx, :]

			scipy.misc.imsave(os.path.join(savedir,'stitchedSV_' + str(sceneIdx) + '_' + str(versionIdx) + image_suff), outputIm)

if __name__ == "__main__":
	main()