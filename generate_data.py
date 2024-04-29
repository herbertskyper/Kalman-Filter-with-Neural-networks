def synthetise_image(background_image,front_image,scale=0.1,degree=10,borderValue=(114,114,114)):
    background_image_cp=copy.deepcopy(background_image)
    bg_h, bg_w = background_image_cp.shape[0:2]
    qr_h, qr_w = front_image.shape[0:2]
    roate_image, rotate_label = random_perspective(front_image, np.array([0, 0, 0, qr_w, qr_h]).reshape((-1, 5)),
                                                       translate=0, scale=scale,degrees=degree, shear=0, border=(qr_w//2,qr_w//2),borderValue=borderValue)
 
    crop_rotate = roate_image[rotate_label[0][2]:rotate_label[0][4], rotate_label[0][1]:rotate_label[0][3]]
 
    if bg_w<crop_rotate.shape[1] or bg_h<crop_rotate.shape[0]:
        return None,None
 
    random_x = random.randint(0, bg_w - crop_rotate.shape[1])
    random_y = random.randint(0, bg_h - crop_rotate.shape[0])
 
    if random_y + crop_rotate.shape[0]>bg_h or random_x + crop_rotate.shape[1]>bg_w:
        return None,None
 
    mask = (crop_rotate != np.array(list(borderValue)))
    mask = (mask[:, :, 0] | mask[:, :, 1] | mask[:, :, 2])
    mask_inv=(~mask)
 
    roi = background_image_cp[random_y:random_y + crop_rotate.shape[0], random_x:random_x + crop_rotate.shape[1]]
    roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv.astype(np.uint8))
 
    roi_fg = cv2.bitwise_and(crop_rotate, crop_rotate, mask=mask.astype(np.uint8))
 
    dst = cv2.add(roi_bg, roi_fg)
    roi[:, :] = dst[:, :]
 
    return background_image_cp,[random_x,random_y,crop_rotate.shape[1],crop_rotate.shape[0]]
    
...    
 
background_image=cv2.imread(os.path.join(background_dir,background_lst[index]))
background_h,background_w=background_image.shape[0:2]
 
mixup_image,box=synthetise_image(background_image,qr_image,scale=0.2,degree=45)
 
if mixup_image is None or (box[2]<60 or box[3]<60):
    continue
 
cnt+=1
 
center_x=box[0]+box[2]/2
center_y=box[1]+box[3]/2
label=[0,center_x/background_w,center_y/background_h,box[2]/background_w,box[3]/background_h]
 
#save image
cv2.imwrite(os.path.join(save_dir,"{:0>8d}_sync_{}.jpg".format(thread_start_cnt,sub_dir)),mixup_image)
#save label
with open(os.path.join(save_label,"{:0>8d}_sync_{}.txt".format(thread_start_cnt,sub_dir)),'w') as f:
    f.write("{0} {1} {2} {3} {4}\n".format(label[0],label[1],label[2],label[3],label[4]))