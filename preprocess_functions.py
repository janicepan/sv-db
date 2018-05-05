import scipy.io as sio
import scipy.misc
import os
import numpy as np
from math import pi, sin, cos, sqrt, atan
from PIL import Image

def defineOutputRegions(imH,imW,carH,carW):
    output = np.zeros([imH,imW])
    m = (imH - carH) / (imW - carW)
    #top of image
    for i in range(1,int(np.floor((imH-carH)/2)+1)):
        for j in range(1,imW+1):
            if j*m-i>0 and j+i/m<imW:
                output[i-1,j-1] = 1
            elif j*m-i>0 and j+i/m>=imW:
                output[i-1,j-1] = 2
            else:
                output[i-1,j-1] = 4
    #middle of image
    for i in range(int(np.floor((imH-carH)/2)+1),int(np.floor((imH+carH)/2)+1)):
        for j in range(1,imW+1):
            if j>np.floor((imW+carW)/2):
                output[i-1,j-1] = 2
            elif j<np.floor((imW-carW)/2):
                output[i-1,j-1] = 4
    #bottom of image
    for i in range(int(np.floor((imH+carH)/2)+1),imH+1):
        for j in range(1,imW+1):
            if j*m+i>imH and j-i/m<(imW-imH/m):
                output[i-1,j-1] = 3
            elif j*m+i>imH and j-i/m>=(imW-imH/m):
                output[i-1,j-1] = 2
            else:
                output[i-1,j-1] = 4
    return output

def getProjectionMat_vc(vc_params):
    # Virtual camera projection matrix estimation, given extrinsic and intrinsic parameters
    # Virtual camera angles
    thetax = -(pi/180) * vc_params['rotx']
    thetay = -(pi/180) * vc_params['roty']
    thetaz = -(pi/180) * vc_params['rotz']

    # Rotation matrix
    Rx = [[1, 0, 0], [0, cos(thetax), -sin(thetax)], [0, sin(thetax), cos(thetax)]]
    Ry = [[cos(thetay), 0, sin(thetay)], [0, 1, 0], [-sin(thetay), 0, cos(thetay)]]
    Rz = [[cos(thetaz), -sin(thetaz), 0], [sin(thetaz), cos(thetaz), 0], [0, 0, 1]]

    R = np.dot(np.dot(Rx, Ry), Rz)

    P = [[R[0, 0], R[0, 1], R[0, 2], 0], [R[1, 0], R[1, 1], R[1, 2], 0], [R[2, 0], R[2, 1], R[2, 2], 0], [0, 0, 0, vc_params['f']]]
    return P


def intrinsic_matrix(camNum, intrinsicParams):
    distortionFocalLength = intrinsicParams['distFocalLength'][camNum]
    distortionCenterX = intrinsicParams['distCenterX'][camNum]
    distortionCenterY = intrinsicParams['distCenterY'][camNum]
    K = [[distortionFocalLength, 0, distortionCenterX], [0, distortionFocalLength, distortionCenterY], [0, 0, 1]]
    return K


def ProjectiveTrans(imgNo, intrinsicParams, extrinsicParams, xw, yw, zw):
    K = intrinsic_matrix(imgNo, intrinsicParams)
    R_w2c = extrinsicParams['R_w2c'][imgNo]
    t_w2c = extrinsicParams['t_w2c'][imgNo]
    P = [[R_w2c[0, 0], R_w2c[0, 1], R_w2c[0, 2], t_w2c[0]], [R_w2c[1, 0], R_w2c[1, 1], R_w2c[1, 2], t_w2c[1]], [R_w2c[2, 0], R_w2c[2,1], R_w2c[2, 2], t_w2c[2]], [0, 0, 0, 1]]
    img_loc = np.dot(P, [xw, yw, zw, 1])

    #Normalization
    img_x = img_loc[0]/img_loc[2]
    img_y = img_loc[1]/img_loc[2]

    img_loc = np.dot(K, [img_x, img_y, 1])

    #Quantization
    img_x = np.round(img_loc[0])
    img_y = np.round(img_loc[1])
    img_loc = [img_x, img_y]

    return img_loc


def FisheyeTrans(xin, yin, xc, yc, xd, yd, f):
    #Fisheye distortion correction function
    ru = sqrt(np.power((xin-xc), 2) + np.power((yin-yc), 2))
    rd = 2*f*sin(atan(ru/f)/2)
    xout = (xin-xc)*rd/ru + xd
    yout = (yin-yc)*rd/ru + yd
    img_loc = [xout, yout]

    return img_loc


def getTransformedSV_AutoDots(imgNo, img, vc_params, intrinsicParams, extrinsicParams, vis_params):
    # AutoDots is the method of calibration using physical spheres placed in the synthetic scene to compute
    # the perspective transforms into the world coordinate space, which is the image space. This 'AutoDots'
    # method uses image coordinates as the 'world coordinates'
    #
    # The other method uses true world coordinates of the charts, which were also manually selected,
    # to compute the perspective transforms. Then there is an additional mapping from world coordinate
    # space into image space.

    #unpack visualization parameters
    s = vis_params['scale']
    zwmesh = vis_params['zwmesh']
    imW = vis_params['imW']
    imH = vis_params['imH']
    step_size = vis_params['step_size']

    Xc_undist = vis_params['Xc_undist']
    Xc_fish = vis_params['Xc_fish']

    vc_proj_mat = getProjectionMat_vc(vc_params)  # projection matrix
    fdist = intrinsicParams['distFocalLength'][imgNo]
    xdist = intrinsicParams['distCenterX'][imgNo]
    ydist = intrinsicParams['distCenterY'][imgNo]

    pts_fisheye = []
    pts_world = []

    outputIm = np.zeros([imH, imW, img.shape[2]],'uint8')

    for iIdx in range(imH):
        i = iIdx + 1
        for jIdx in range(imW):
            j = jIdx + 1

            xw = j
            yw = i
            zw = zwmesh[iIdx,jIdx]

            loc_u = ProjectiveTrans(imgNo, intrinsicParams, extrinsicParams, xw, yw, zw) #loc in undistorted image
            xi = loc_u[0]
            yi = loc_u[1]

            loc_d = FisheyeTrans(yi, xi, Xc_undist[0], Xc_undist[1], Xc_fish[0], Xc_fish[1], fdist)
            yi_fish = loc_d[0]
            xi_fish = loc_d[1]

            xi_fish = int(np.round(xi_fish))
            yi_fish = int(np.round(yi_fish))

            if xi_fish<1:
                xi_fish = 1
            elif xi_fish>img.shape[1]:
                xi_fish = img.shape[1]

            if yi_fish<1:
                yi_fish = 1
            elif yi_fish>img.shape[0]:
                yi_fish = img.shape[0]

            outputIm[iIdx, jIdx, :] = img[yi_fish-1, xi_fish-1, :]

    return outputIm


def combine_seeds(image_dir, image_root, image_suff, num_seeds):
    images = []
    for seed in range(num_seeds):
        image_path = os.path.join(image_dir, image_root + '_s' + str(seed) + image_suff)
        images.append(np.array(Image.open(image_path)))

    return np.nanmin(np.asarray(images),0)
