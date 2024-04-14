import numpy as np
from scipy.spatial import ConvexHull
import SimpleITK as sitk

# 得到最大连通域
def GetLargestConnectedCompont(binarysitk_image):
    """
    save largest object
    :param sitk_maskimg:binary itk image
    :return: largest region binary image
    """
    cc = sitk.ConnectedComponent(binarysitk_image)
    stats = sitk.LabelIntensityStatisticsImageFilter()
    stats.SetGlobalDefaultNumberOfThreads(8)
    stats.Execute(cc, binarysitk_image)
    maxlabel = 0
    maxsize = 0
    size_list = []
    for l in stats.GetLabels():
        size = stats.GetPhysicalSize(l)
        size_list.append(size)
        if maxsize < size:
            maxlabel = l
            maxsize = size
    labelmaskimage = sitk.GetArrayFromImage(cc) # 带label不同值的mask


    outmask = labelmaskimage.copy()
    outmask[labelmaskimage == maxlabel] = 1
    outmask[labelmaskimage != maxlabel] = 0


    outmask_sitk = sitk.GetImageFromArray(outmask)
    outmask_sitk.SetDirection(binarysitk_image.GetDirection())
    outmask_sitk.SetSpacing(binarysitk_image.GetSpacing())
    outmask_sitk.SetOrigin(binarysitk_image.GetOrigin())
    return outmask_sitk


def Minimum_envelope_ball(mask_data):
    '''
    mask_data: 需要计算的掩膜数组
    '''
# 找到非零点的坐标
    nonzero_points = np.argwhere(mask_data > 0)

    # 使用ConvexHull来计算最小外包围球
    hull = ConvexHull(nonzero_points)
    diameter = 2 * np.max(np.linalg.norm(nonzero_points[hull.vertices] - np.mean(nonzero_points, axis=0), axis=1))

    return diameter

def eval_tumor_efficacy(label1_path, label2_path):
    '''
    肿瘤疗效评估标准
    Criteria for evaluation of tumor efficacy
    :param label1_path 术前肿瘤掩膜路径
    :param label2_path 术前肿瘤掩膜路径
    '''
    tumor1_image = sitk.ReadImage(label1_path)
    tumor2_image = sitk.ReadImage(label2_path)

    tumor1_image = GetLargestConnectedCompont(tumor1_image)
    tumor2_image = GetLargestConnectedCompont(tumor2_image)

    tumor1_arr = sitk.GetArrayFromImage(tumor1_image)
    tumor2_arr = sitk.GetArrayFromImage(tumor2_image)

    tumor1_diameter = Minimum_envelope_ball(tumor1_arr)
    tumor2_diameter = Minimum_envelope_ball(tumor2_arr)
    print('tumor1_diameter:', tumor1_diameter)
    print('tumor2_diameter:', tumor2_diameter)

    result_rate =  (tumor2_diameter-tumor1_diameter)/tumor1_diameter
    if tumor2_diameter == 0:
        output_result =  "完全缓解(CR): 术后肿瘤病灶消失"
    elif (-0.3 <= result_rate) and (result_rate <= -0.15):
        output_result = "部分缓解(PR): 肿瘤直径缩小15%~30%, 有少量病灶残留"
    elif (-0.15 <= result_rate) and (result_rate <= 0.15):
        output_result = "稳定(SD): 有病灶残留, 肿瘤直径增加、缩小在15%以下"
    elif (result_rate > 0.15):
        output_result = "进展(PD): 肿瘤直径增加15%以上。"

    return output_result
    

# output_result = eval_tumor_efficacy('result copy\\label1.nii.gz', 'result copy\\label3_multi.nii.gz')
# print(output_result)



# # 读取NIfTI文件
# nii_file = "result\\tumor_post\\nii.nii.gz"
# img = nib.load(nii_file)
# mask_data = img.get_fdata()

# print(type(mask_data)) # <class 'numpy.ndarray'>
# print('mask_data.shape:', mask_data.shape)
# # 找到非零点的坐标
# nonzero_points = np.argwhere(mask_data > 0)

# # 使用ConvexHull来计算最小外包围球
# hull = ConvexHull(nonzero_points)
# diameter = 2 * np.max(np.linalg.norm(nonzero_points[hull.vertices] - np.mean(nonzero_points, axis=0), axis=1))

# print("掩膜直径：", diameter)






# lung_image = sitk.ReadImage(nii_file)

# lung_image2 = GetLargestConnectedCompont(lung_image)

# lung_arr = sitk.GetArrayFromImage(lung_image2) 

# print(lung_arr.shape)

# print(Minimum_envelope_ball(lung_arr))




# print(data.shape[-1])
# # 遍历每个掩膜
# for mask_index in range(data.shape[-1]):
#     mask_data = data[..., mask_index]
    
#     # 找到非零点的坐标
#     nonzero_points = np.argwhere(mask_data > 0)

#     # 使用ConvexHull来计算最小外包围球
#     hull = ConvexHull(nonzero_points)
#     diameter = 2 * np.max(np.linalg.norm(nonzero_points[hull.vertices] - np.mean(nonzero_points, axis=0), axis=1))

#     print(f"掩膜 {mask_index + 1} 的直径：{diameter}")
