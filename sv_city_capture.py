import os
import bpy
from bpy import context
from math import sin, cos, radians, pi, sqrt
import random as rand
import pickle
import pdb
import csv
import sys

def capture_multiangle(cam, newType, newTypeInfo, angleOffsets, renderFormat, savePath, saveType, sceneIdx, camName, cyclesSeed, augIdx):
    # saveType can be 'Depth' or 'Stereo'
    # renderFormat can be HDR, PNG
    print('Scene ' + str(sceneIdx) + ": " + camName + ": " + newType + ", capturing...")
    # print(newType)
    if renderFormat == 'HDR':
        suff = '.hdr'
    if renderFormat == 'PNG':
        suff = '.png'
    oldType = cam.data.type
    if (oldType == 'PANO') & (newType == 'PERSP'):
        # newTypeInfo contains sensor width, sensor height, sensor fit,
        #   focal length, and units
        cam.data.type = newType
        cam.data.sensor_width = float(newTypeInfo[0])
        cam.data.sensor_fit = newTypeInfo[1]
        cam.data.lens = float(newTypeInfo[2])
        cam.data.lens_unit = newTypeInfo[3]
    elif (oldType == 'PERSP') & (newType == 'PANO'):
        # newTypeInfo contains sensor width, sensor fit, focal length, and fov
        cam.data.type = 'PANO'
        cam.data.sensor_width = float(newTypeInfo[0])
        cam.data.sensor_fit = newTypeInfo[1]
        cam.data.cycles.fisheye_lens = float(newTypeInfo[2])
        cam.data.cycles.fisheye_fov = float(newTypeInfo[3])
    currRot = cam.rotation_euler
    for angleIdx in range(len(angleOffsets)):
        oldAngle = currRot[2]
        newAngle = currRot[2] + angleOffsets[angleIdx]
        cam.rotation_euler = (currRot[0], currRot[1], newAngle)
        bpy.context.scene.render.image_settings.file_format = renderFormat
        bpy.context.scene.camera = cam
        print('Angle %d:' % angleIdx)
        print(cam.rotation_euler)
        bpy.context.scene.render.filepath = os.path.join(savePath, saveType + str(angleIdx), camName + '_' + newType + '_' + renderFormat + '_' + str(sceneIdx) + '_v' + str(augIdx) + '_a' + str(angleIdx) + '_s' + str(cyclesSeed) + suff)
        bpy.ops.render.render(use_viewport=True, write_still=True)
        cam.rotation_euler = (currRot[0], currRot[1], oldAngle)
    return cam

def capture_simple(cam, newType, newTypeInfo, renderFormat, savePath, saveType, sceneIdx, camName, cyclesSeed, augIdx):
    # saveType can be 'Depth' or 'Stereo'
    # renderFormat can be HDR, PNG
    print('Scene ' + str(sceneIdx) + ": " + camName + ": " + newType + ", capturing...")
    # print(newType)
    if renderFormat == 'HDR':
        suff = '.hdr'
    if renderFormat == 'PNG':
        suff = '.png'
    oldType = cam.data.type
    if (oldType == 'PANO') & (newType == 'PERSP'):
        # newTypeInfo contains sensor width, sensor height, sensor fit,
        #   focal length, and units
        cam.data.type = newType
        cam.data.sensor_width = float(newTypeInfo[0])
        cam.data.sensor_fit = newTypeInfo[1]
        cam.data.lens = float(newTypeInfo[2])
        cam.data.lens_unit = newTypeInfo[3]
    elif (oldType == 'PERSP') & (newType == 'PANO'):
        # newTypeInfo contains sensor width, sensor fit, focal length, and fov
        cam.data.type = 'PANO'
        cam.data.sensor_width = float(newTypeInfo[0])
        cam.data.sensor_fit = newTypeInfo[1]
        cam.data.cycles.fisheye_lens = float(newTypeInfo[2])
        cam.data.cycles.fisheye_fov = float(newTypeInfo[3])
    currRot = cam.rotation_euler
    bpy.context.scene.render.image_settings.file_format = renderFormat
    bpy.context.scene.camera = cam
    bpy.context.scene.render.filepath = os.path.join(savePath, saveType, camName + '_' + newType + '_' + renderFormat + '_' + str(sceneIdx) + '_v' + str(augIdx) + '_s' + str(cyclesSeed) + suff)
    bpy.ops.render.render(use_viewport=True, write_still=True)
    cam.rotation_euler = (currRot[0], currRot[1], currRot[2])
    return cam

def main():
    sceneStartIdx = int(sys.argv[-5])
    total_scene_number = int(sys.argv[-4])
    num_augment = int(sys.argv[-3])
    start_augment = int(sys.argv[-2])
    X = int(sys.argv[-1]) #number of augmentations to save
    print('Starting scene = ' + str(sceneStartIdx) + ', capturing ' + str(total_scene_number) + ' scenes\n')

    ### DEFINE PARAMETERS ###
    rand.seed(sceneStartIdx+start_augment)

    # RESOLUTION
    outResX = 1280 #640  # 2560
    outResY = 720  #360  # 1440 #outResX/2

    outResX_sv = 720  # 1760
    outResY_sv = 720  # 2160

    # CAMERA PARAMETERS
    sceneScale = 0.01
    camHeight = 1.5
    camBaseline = 1
    downTilt = 20
    downTiltRad = downTilt * pi / 180

    roadHeightOffsetZ = 0.1

    # cam1_rotx_deg = 90 - downTilt
    cam1_rotx_deg = 90
    cam1_roty_deg = 0
    cam1_rotz_deg = 270
    cam1_rotx = pi / 180 * cam1_rotx_deg
    cam1_roty = pi / 180 * cam1_roty_deg
    cam1_rotz = pi / 180 * cam1_rotz_deg

    # cam2_rotx_deg = 90 - downTilt
    cam2_rotx_deg = 90
    cam2_roty_deg = 0
    cam2_rotz_deg = 0
    cam2_rotx = pi / 180 * cam2_rotx_deg
    cam2_roty = pi / 180 * cam2_roty_deg
    cam2_rotz = pi / 180 * cam2_rotz_deg

    # cam3_rotx_deg = 90 - downTilt
    cam3_rotx_deg = 90
    cam3_roty_deg = 0
    cam3_rotz_deg = 90
    cam3_rotx = pi / 180 * cam3_rotx_deg
    cam3_roty = pi / 180 * cam3_roty_deg
    cam3_rotz = pi / 180 * cam3_rotz_deg

    # cam4_rotx_deg = 90 - downTilt
    cam4_rotx_deg = 90
    cam4_roty_deg = 0
    cam4_rotz_deg = 180
    cam4_rotx = pi / 180 * cam4_rotx_deg
    cam4_roty = pi / 180 * cam4_roty_deg
    cam4_rotz = pi / 180 * cam4_rotz_deg

    camSV_rotx_deg = 0
    camSV_roty_deg = 0
    camSV_rotz_deg = 0
    camSV_rotx = pi / 180 * camSV_rotx_deg
    camSV_roty = pi / 180 * camSV_roty_deg
    camSV_rotz = pi / 180 * camSV_rotz_deg

    cam1_x = sceneScale * sqrt(camBaseline)
    cam1_y = sceneScale * 0
    cam1_z = sceneScale * (camHeight + roadHeightOffsetZ)
    cam2_x = sceneScale * 0
    cam2_y = sceneScale * sqrt(camBaseline)
    cam2_z = sceneScale * (camHeight + roadHeightOffsetZ)
    cam3_x = sceneScale * (-sqrt(camBaseline))
    cam3_y = sceneScale * 0
    cam3_z = sceneScale * (camHeight + roadHeightOffsetZ)
    cam4_x = sceneScale * 0
    cam4_y = sceneScale * (-sqrt(camBaseline))
    cam4_z = sceneScale * (camHeight + roadHeightOffsetZ)

    camSV_x = sceneScale * 0
    camSV_y = sceneScale * 0
    camSV_z = sceneScale * (camHeight + 13.5 + roadHeightOffsetZ)

    camOrigLocs = [[cam1_x, cam1_y, cam1_z], [cam2_x, cam2_y, cam2_z], [cam3_x, cam3_y, cam3_z], [cam4_x, cam4_y, cam4_z], [camSV_x, camSV_y, camSV_z]]

    # RENDER SETTINGS
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.render.resolution_x = outResX
    bpy.context.scene.render.resolution_y = outResY
    bpy.context.scene.render.resolution_percentage = 100
    savePath_SV = #SPECIFY PATH TO SAVE DATA
    camAnglesDeg_SV = [0] #TO SAVE MULTIANGLE DATA, USE: [60, 45, 30, 0, -30, -45, -60]
    camAnglesRad_SV = []

    for i in range(len(camAnglesDeg_SV)):
        camAnglesRad_SV.append(camAnglesDeg_SV[i] * pi / 180)

    # Activate all scene layers to remove any objects still present
    for i in range(len(bpy.context.scene.layers)):
        bpy.context.scene.layers[i] = True

    # First delete cameras in the scene
    bpy.context.scene.objects.active = None
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete(use_global=True)

    #load the roads and locations for capture
    captureRoads = []
    captureXoffsets = []
    captureYoffsets = []
    captureSeqNumbers = []
    pathname = #SPECIFY PATH TO CSV FILES: test4_captureLocations_all.csv, SunColors.csv
    f = open(os.path.join(pathname,'test4_captureLocations_all.csv'), 'r')
    csvreader =csv.reader(f,delimiter=',')
    for row in csvreader:
        captureRoads.append(row[0])
        captureXoffsets.append(float(row[1]))
        captureYoffsets.append(float(row[2]))
        captureSeqNumbers.append(int(row[3]))

    suncolors = []
    suncolors.append([1, 0.858, 0.622])  # original color
    f = open(os.path.join(pathname, 'SunColors.csv'), 'r')
    csvreader = csv.reader(f, delimiter=',')
    for row in csvreader:
        suncolors.append([float(row[0]), float(row[1]), float(row[2])])  # other sun color options

    # add cameras to layer 4
    sceneLayer = 4
    bpy.context.scene.layers[sceneLayer] = True
    for i in range(len(bpy.context.scene.layers)):
        if (i != sceneLayer):
            bpy.context.scene.layers[i] = False

    bpy.ops.object.camera_add(location=(cam1_x, cam1_y, cam1_z), rotation=(cam1_rotx, cam1_roty, cam1_rotz))
    cam1 = bpy.context.scene.objects.active
    bpy.ops.object.camera_add(location=(cam2_x, cam2_y, cam2_z), rotation=(cam2_rotx, cam2_roty, cam2_rotz))
    cam2 = bpy.context.scene.objects.active
    bpy.ops.object.camera_add(location=(cam3_x, cam3_y, cam3_z), rotation=(cam3_rotx, cam3_roty, cam3_rotz))
    cam3 = bpy.context.scene.objects.active
    bpy.ops.object.camera_add(location=(cam4_x, cam4_y, cam4_z), rotation=(cam4_rotx, cam4_roty, cam4_rotz))
    cam4 = bpy.context.scene.objects.active

    bpy.ops.object.camera_add(location=(camSV_x, camSV_y, camSV_z), rotation=(camSV_rotx, camSV_roty, camSV_rotz))
    camSV = bpy.context.scene.objects.active

    cameras = [cam1, cam2, cam3, cam4, camSV]
    camNames = ['2right','1front','4left','3rear','0sv']

    # Set the parameters of each camera
    for camIdx in range(4):
        cam = cameras[camIdx]
        cam.data.type = 'PANO'
        cam.data.cycles.fisheye_lens = 1.8
        cam.data.cycles.fisheye_fov = 3.14159
        cam.data.sensor_width = 5.2
        cam.scale = (sceneScale * 0.05, sceneScale * 0.05, sceneScale * 0.05)

    camSV.data.type = 'PERSP'
    camSV.data.sensor_width = float(5.2)
    camSV.data.sensor_fit = 'AUTO'
    camSV.data.lens = 3.5
    camSV.data.lens_unit = 'MILLIMETERS'
    camSV.scale = (sceneScale * 0.05, sceneScale * 0.05, sceneScale * 0.05)

    # Render the scene
    renderLayers = [2, 3, 4, 5]
    for i in range(len(renderLayers)):
        bpy.context.scene.layers[renderLayers[i]] = True

    panoInfo = ['5.2', 'AUTO', '1.8', '3.14159']
    perspInfo = ['5.2', 'AUTO', '3.5', 'MILLIMETERS']
    svInfo = ['5.2', 'AUTO', '3.5', 'MILLIMETERS']

    numCaptures = len(captureRoads)
    prevSeqIdx = -1
    roadWidth = 10  # meters
    for i in range(sceneStartIdx,sceneStartIdx+total_scene_number):
        sceneIdx = i
        seqIdx = captureSeqNumbers[i]
        if(seqIdx!=prevSeqIdx):
            print(seqIdx)
            prevSeqIdx = seqIdx

        roadLoc = bpy.data.objects[captureRoads[i]].location

        xOff = captureXoffsets[i]
        yOff = captureYoffsets[i]

        xAug = []
        yAug = []
        zRandRot = []

        xAug.append(0)
        yAug.append(0)
        zRandRot.append(0)

        for augIdx in range(num_augment):
            xAug.append(0.5-rand.random())
            yAug.append(0.5-rand.random())
            zRandRot.append(pi / 2 * rand.random())

        for augIdx in range(start_augment,start_augment + X): # can only capture 7 augmentations in 24 hours #len(xAug)):
            newLoc_x = roadLoc[0] + xOff + xAug[augIdx]
            newLoc_y = roadLoc[1] + yOff + yAug[augIdx]
            camOrigLocs_rotate = []
            for camNum in range(len(cameras)):
                camOrigLoc_x = camOrigLocs[camNum][0]
                camOrigLoc_y = camOrigLocs[camNum][1]
                camOrigLoc_z = camOrigLocs[camNum][2]
                x_rotated = camOrigLoc_x * cos(zRandRot[augIdx]) - camOrigLoc_y * sin(zRandRot[augIdx])
                y_rotated = camOrigLoc_x * sin(zRandRot[augIdx]) + camOrigLoc_y * cos(zRandRot[augIdx])
                camOrigLocs_rotate.append([x_rotated, y_rotated, camOrigLoc_z])

            for camNum in range(len(cameras)):
                currCam = cameras[camNum]
                currCam.location[0] = camOrigLocs_rotate[camNum][0] + sceneScale * (newLoc_x)
                currCam.location[1] = camOrigLocs_rotate[camNum][1] + sceneScale * (newLoc_y)
                currCam.location[2] = camOrigLocs_rotate[camNum][2] + sceneScale * (roadLoc[2])
                print(currCam.location)
                print(roadLoc)

            # Change the ambient lighting
            if augIdx == 0:
                suncolor = suncolors[0]
            else:
                suncolor = suncolors[rand.randint(0, len(suncolors) - 1)]

            sun_nodes = bpy.data.lamps["Sun"].node_tree
            sun_nodes.nodes["Emission"].inputs[0].default_value[0] = suncolor[0]
            sun_nodes.nodes["Emission"].inputs[0].default_value[1] = suncolor[1]
            sun_nodes.nodes["Emission"].inputs[0].default_value[2] = suncolor[2]

            ### PREPARE SCENE FOR RENDERING ###
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            links = tree.links

            # first clear the node tree to prepare for new scene
            for n in tree.nodes:
                tree.nodes.remove(n)

            # Scene render settings for fisheye

            scene = bpy.context.scene
            print(scene.render.use_multiview)
            print(scene.render.views_format)
            rl = tree.nodes.new(type="CompositorNodeRLayers")
            composite = tree.nodes.new(type="CompositorNodeComposite")
            composite.location = 400, 0
            normalize = tree.nodes.new(type="CompositorNodeNormalize")
            normalize.location = 200, 0

            for cyclesSeed in range(3):
                bpy.data.scenes["Scene"].cycles.seed = cyclesSeed

                links.new(rl.outputs['Image'], composite.inputs['Image'])
                scene.render.use_multiview = False
                bpy.context.scene.render.image_settings.file_format = 'PNG'

                ## 8-bit color depth; RGB image
                bpy.context.scene.render.image_settings.color_depth = '8'
                bpy.context.scene.render.image_settings.color_mode = 'RGB'

                for camIdx in range(4):
                    cam = cameras[camIdx]
                    xrot = cam.rotation_euler[0]
                    yrot = cam.rotation_euler[1]
                    zrot = cam.rotation_euler[2]
                    cam.rotation_euler = (xrot - downTiltRad, yrot, zrot + zRandRot[augIdx])
                    capture_multiangle(cam, 'PANO', panoInfo, camAnglesRad_SV, 'PNG', savePath_SV, 'Stereo', sceneIdx, camNames[camIdx], cyclesSeed, augIdx)
                    cam.rotation_euler = (xrot, yrot, zrot)

                cam = cameras[4]  # sv
                xrot = cam.rotation_euler[0]
                yrot = cam.rotation_euler[1]
                zrot = cam.rotation_euler[2]
                cam.rotation_euler = (xrot, yrot, zrot + zRandRot[augIdx])
                bpy.context.scene.render.resolution_x = outResX_sv
                bpy.context.scene.render.resolution_y = outResY_sv
                capture_simple(camSV, 'PERSP', svInfo, 'PNG', savePath_SV, 'Stereo', sceneIdx, camNames[-1], cyclesSeed, augIdx)
                bpy.context.scene.render.resolution_x = outResX
                bpy.context.scene.render.resolution_y = outResY
                cam.rotation_euler = (xrot, yrot, zrot)

                ## 8-bit color depth; RGB image
                links.new(rl.outputs['Z'], composite.inputs['Image'])

                for camIdx in range(4):
                    cam = cameras[camIdx]
                    xrot = cam.rotation_euler[0]
                    yrot = cam.rotation_euler[1]
                    zrot = cam.rotation_euler[2]
                    cam.rotation_euler = (xrot - downTiltRad, yrot, zrot + zRandRot[augIdx])
                    capture_multiangle(cam,'PANO', panoInfo, camAnglesRad_SV, 'HDR', savePath_SV, 'Depth', sceneIdx, camNames[camIdx], cyclesSeed, augIdx)
                    cam.rotation_euler = (xrot, yrot, zrot)

                cam = cameras[4]  # sv
                xrot = cam.rotation_euler[0]
                yrot = cam.rotation_euler[1]
                zrot = cam.rotation_euler[2]
                cam.rotation_euler = (xrot, yrot, zrot + zRandRot[augIdx])
                bpy.context.scene.render.resolution_x = outResX_sv
                bpy.context.scene.render.resolution_y = outResY_sv
                capture_simple(camSV, 'PERSP', svInfo, 'HDR', savePath_SV, 'Depth', sceneIdx, camNames[-1], cyclesSeed, augIdx)
                bpy.context.scene.render.resolution_x = outResX
                bpy.context.scene.render.resolution_y = outResY
                cam.rotation_euler = (xrot, yrot, zrot)

if __name__ == "__main__":
    main()