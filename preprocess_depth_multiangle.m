function preprocess_depth_multiangle(start_scene,end_scene)
% start_scene and end_scene are the lower and upper bounds of the scene indices to process
% 	allows for breaking up the data processing into multiple parallel jobs

depth_dir = '<path-to-captured-depth-data>/Depth';
save_dir = '<path-to-save-directory>'; %e.g., '<path-to-captured-depth-data>/Depth_preprocessed'

% if ~exist(save_dir)
%     mkdir(save_dir)
% end

cam_names = {'0sv_PERSP','1front_PANO','2right_PANO','3rear_PANO','4left_PANO'};

num_versions = 20; %# additional augmentations; 1 original + 20 additional versions = 21 total

sv_h = 720;
sv_w = 720;

im_h = 720;
im_w = 1280;

for scene_num = start_scene:end_scene
    for version_num = 0:num_versions
        for cam_num = 1:numel(cam_names)
            if cam_num==1
                s0_name = sprintf('%s_HDR_%d_v%d_s0.hdr',cam_names{cam_num},scene_num,version_num);
                s1_name = sprintf('%s_HDR_%d_v%d_s1.hdr',cam_names{cam_num},scene_num,version_num);
                s2_name = sprintf('%s_HDR_%d_v%d_s2.hdr',cam_names{cam_num},scene_num,version_num);

                s0 = hdrread(fullfile(depth_dir,s0_name));
                s1 = hdrread(fullfile(depth_dir,s1_name));
                s2 = hdrread(fullfile(depth_dir,s2_name));
                
                depth_ch1 = min(cat(3,s0(:,:,1), s1(:,:,1), s2(:,:,1)),[],3);
                depth_ch2 = min(cat(3,s0(:,:,2), s1(:,:,2), s2(:,:,2)),[],3);
                depth_ch3 = min(cat(3,s0(:,:,3), s1(:,:,3), s2(:,:,3)),[],3);
                
                depth_im = cat(3, depth_ch1, depth_ch2, depth_ch3);
                
                depth_name = sprintf('%s_HDR_%d_v%d.hdr',cam_names{cam_num},scene_num,version_num);
                hdrwrite(depth_im,fullfile(save_dir,depth_name));
            else
                for angle_idx = 0:6
                    depth_dir_angle = sprintf('%s%d',depth_dir,angle_idx);
                    s0_name = sprintf('%s_HDR_%d_v%d_a%d_s0.hdr',cam_names{cam_num},scene_num,version_num,angle_idx);
                    s1_name = sprintf('%s_HDR_%d_v%d_a%d_s1.hdr',cam_names{cam_num},scene_num,version_num,angle_idx);
                    s2_name = sprintf('%s_HDR_%d_v%d_a%d_s2.hdr',cam_names{cam_num},scene_num,version_num,angle_idx);
                    
                    s0 = hdrread(fullfile(depth_dir_angle,s0_name));
                    s1 = hdrread(fullfile(depth_dir_angle,s1_name));
                    s2 = hdrread(fullfile(depth_dir_angle,s2_name));
                    
                    depth_ch1 = min(cat(3,s0(:,:,1), s1(:,:,1), s2(:,:,1)),[],3);
                    depth_ch2 = min(cat(3,s0(:,:,2), s1(:,:,2), s2(:,:,2)),[],3);
                    depth_ch3 = min(cat(3,s0(:,:,3), s1(:,:,3), s2(:,:,3)),[],3);
                    
                    depth_im = cat(3, depth_ch1, depth_ch2, depth_ch3);
                    
                    depth_name = sprintf('%s_HDR_%d_v%d_a%d.hdr',cam_names{cam_num},scene_num,version_num,angle_idx);
                    hdrwrite(depth_im,fullfile(save_dir,depth_name));
                end
            end
        end
    end
end