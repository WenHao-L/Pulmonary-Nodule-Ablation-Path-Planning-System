import itk
import copy
import numpy as np
import SimpleITK as sitk
from skimage import measure
import skimage
from PyQt5.QtCore import QThread, pyqtSignal


# 窗宽窗位调整
def window_intensity(itk_image,hu_min, hu_max):
    """窗宽窗位调整 \n
    args: \n
        itk_image: simple itk 读取的图像 \n
        hu_min: 窗范围最小值 \n
        hu_max: 窗范围最大值 \n
    return: 调整窗宽窗位后的图像 \n
    """
    ww_filter = sitk.IntensityWindowingImageFilter()

    ww_filter.SetWindowMinimum(hu_min)
    ww_filter.SetWindowMaximum(hu_max)
    ww_filter.SetOutputMinimum(hu_min)
    ww_filter.SetOutputMaximum(hu_max)

    return ww_filter.Execute(itk_image)

# 去除小区域
def remove_small_region(input_img, remove_size=256):

    input_ar = sitk.GetArrayFromImage(input_img)
    output_ar = copy.deepcopy(input_ar)


    print("volarray_sum:", sum(sum(sum(input_ar))))

    label = skimage.measure.label(input_ar, connectivity=2)

    props = skimage.measure.regionprops(label)
    print(len(props))
    numPix = []
    for ia in range(len(props)):
        numPix += [props[ia].area]

    numPix_ar = np.array(numPix)
    index = np.squeeze(np.array(np.where(numPix_ar < remove_size)))

    for ind in index:
        output_ar[label==ind+1] = 0

    l = sitk.GetImageFromArray(output_ar)
    l.SetSpacing(input_img.GetSpacing())
    l.SetOrigin(input_img.GetOrigin())
    l.SetDirection(input_img.GetDirection())
    

    return l


def lung_cu_seg(img_path, remove_block=None):

    lung_img = sitk.ReadImage(img_path)

    # 获取体数据的尺寸
    size = sitk.Image(lung_img).GetSize()
    # 获取体数据direction
    direction = sitk.Image(lung_img).GetDirection()
    # 获取体数据的空间尺寸
    spacing = sitk.Image(lung_img).GetSpacing()
    # 获得体数据的oringin
    oringin = sitk.Image(lung_img).GetOrigin()
    # 将体数据转为numpy数组
    volarray = sitk.GetArrayFromImage(lung_img)

    # 根据CT值，将数据二值化（一般来说 -450 以下是空气的CT值）
    num = -450  # 根据CT图像进行微调
    volarray[volarray>=num]=1
    volarray[volarray<=num]=0

    # 生成阈值图像
    threshold = sitk.GetImageFromArray(volarray)
    threshold.SetSpacing(spacing)

    # 利用种子生成算法，填充空气
    ConnectedThresholdImageFilter = sitk.ConnectedThresholdImageFilter()
    ConnectedThresholdImageFilter.SetLower(0)
    ConnectedThresholdImageFilter.SetUpper(0)
    ConnectedThresholdImageFilter.SetSeedList([(0,0,0),(size[0]-1,size[1]-1,0)])
    
    # 得到body的mask，此时body部分是0，所以反转一下
    bodymask = ConnectedThresholdImageFilter.Execute(threshold)
    bodymask = sitk.ShiftScale(bodymask,-1,-1)
    
    # 用bodymask减去threshold，得到初步的lung的mask
    temp_array = sitk.GetArrayFromImage(bodymask)-sitk.GetArrayFromImage(threshold)
    # temp_array.dtype = np.int16 #np.int16 # # 512 -> 1024
    temp = sitk.GetImageFromArray(temp_array)
    temp = sitk.Cast(temp, sitk.sitkInt16)
    temp.SetSpacing(spacing)
    
    # 利用形态学来去掉一定的肺部的小区域
    bm = sitk.BinaryMorphologicalClosingImageFilter()
    bm.SetKernelType(sitk.sitkBall)
    bm.SetKernelRadius(4) # 微调参数可以消除未分割到的肺部小区域
    bm.SetForegroundValue(1)
    lungmask = bm.Execute(temp)
    
    # 利用measure来计算连通域
    lungmaskarray = sitk.GetArrayFromImage(lungmask)
    label = measure.label(lungmaskarray, connectivity=2)
    label1 = copy.deepcopy(label)
    props = measure.regionprops(label)

    # 计算每个连通域的体素的个数
    numPix = []
    for ia in range(len(props)):
        numPix += [props[ia].area]
    
    # 最大连通域的体素个数，也就是肺部
    # 遍历每个连通区域
    index = np.argmax(numPix)

    # if remove_block == 1:
    #     numPix[index]=0 # 去掉最大的index
    #     index = np.argmax(numPix)

    label[label!=index+1]=0
    label[label==index+1]=1
    
    label = label.astype("int16")

    rows, cols, slices = label.nonzero()
    # x = rows.mean()
    y = cols.mean()
    # z = slices.mean()

    # 自动判断是否分割成床板
    if y > label.shape[1]*0.667:
        print("need remove block")
        numPix[index]=0 # 去掉最大的index
        index = np.argmax(numPix)
        label1[label1!=index+1]=0 
        label1[label1==index+1]=1
        label = label1.astype("int16")

    l = sitk.GetImageFromArray(label)
    l.SetSpacing(spacing)
    l.SetOrigin(oringin)
    l.SetDirection(direction)

    # sitk.WriteImage(l, save_path) # 保存图像
    return l


def regionGrowing(grayImg, seed, threshold):
    """
    :param grayImg: 灰度图像
    :param seed: 生长起始点的位置
    :param threshold: 阈值
    :return: 取值为{0, 255}的二值图像
    """

    [maxX, maxY,maxZ] = grayImg.shape[0:3]

    # 用于保存生长点的队列
    pointQueue = []
    pointQueue.append((seed[0], seed[1],seed[2])) # 保存种子点
    outImg = np.zeros_like(grayImg)
    outImg[seed[0], seed[1], seed[2]] = 1

    pointsNum = 1
    pointsMean = float(grayImg[seed[0], seed[1],seed[2]])

    # 用于计算生长点周围26个点的位置
    Next26 = [[-1, -1, -1],[-1, 0, -1],[-1, 1, -1],
                [-1, 1, 0], [-1, -1, 0], [-1, -1, 1],
                [-1, 0, 1], [-1, 0, 0],[-1, 0, -1],
                [0, -1, -1], [0, 0, -1], [0, 1, -1],
                [0, 1, 0],[-1, 0, -1],
                [0, -1, 0],[0, -1, 1],[-1, 0, -1],
                [0, 0, 1],[1, 1, 1],[1, 1, -1],
                [1, 1, 0],[1, 0, 1],[1, 0, -1],
                [1, -1, 0],[1, 0, 0],[1, -1, -1]]

    while(len(pointQueue)>0):
        # 取出队首并删除
        growSeed = pointQueue[0]
        del pointQueue[0]

        for differ in Next26:
            growPointx = growSeed[0] + differ[0]
            growPointy = growSeed[1] + differ[1]
            growPointz = growSeed[2] + differ[2]

            # 是否是边缘点
            if((growPointx < 0) or (growPointx > maxX - 1) or
               (growPointy < 0) or (growPointy > maxY - 1) or (growPointz < 0) or (growPointz > maxZ - 1)) :
                continue

            # 是否已经被生长
            if(outImg[growPointx,growPointy,growPointz] == 1):
                continue

            data = grayImg[growPointx,growPointy,growPointz]
            # 判断条件
            # 符合条件则生长，并且加入到生长点队列中
            if(abs(data - pointsMean)<threshold):
                pointsNum += 1
                pointsMean = (pointsMean * (pointsNum - 1) + data) / pointsNum
                outImg[growPointx, growPointy,growPointz] = 1
                pointQueue.append([growPointx, growPointy,growPointz])
            
            # 李文豪没改完
            # if pointsNum > 50000:
            #     break

    return outImg, pointsNum 


def regionGrowing_v2(grayImg, seed, open_grow_mode = None):
    """
    寻找最佳阈值
    :param grayImg: 灰度图像
    :param seed: 生长起始点的位置
    :param threshold: 阈值
    :param open_grow_mode: 防止一些气管分割提前停止生长，导致效果不好，可以说是放开生长模式
    :return: 取值为{0, 255}的二值图像
    """

    if open_grow_mode is not None:
        pointsnum_min = 30000
    else:
        pointsnum_min = 15000
    pointsnum_min = 20000

    threshold = 0
    Lt = 0
    old_point_num = 1
    seg_start = 0 #第一次生成模式，一般都会有超过0.9以上的增加率
    while(True): # 阈值大循环
        [maxX, maxY,maxZ] = grayImg.shape[0:3]

        # 用于保存生长点的队列
        pointQueue = []
        pointQueue.append((seed[0], seed[1],seed[2])) # 保存种子点
        outImg = np.zeros_like(grayImg)
        outImg[seed[0], seed[1],seed[2]] = 1

        pointsNum = 1
        pointsMean = float(grayImg[seed[0], seed[1],seed[2]])

        # 用于计算生长点周围26个点的位置
        Next26 = [[-1, -1, -1],[-1, 0, -1],[-1, 1, -1],
                    [-1, 1, 0], [-1, -1, 0], [-1, -1, 1],
                    [-1, 0, 1], [-1, 0, 0],[-1, 0, -1],
                    [0, -1, -1], [0, 0, -1], [0, 1, -1],
                    [0, 1, 0],[-1, 0, -1],
                    [0, -1, 0],[0, -1, 1],[-1, 0, -1],
                    [0, 0, 1],[1, 1, 1],[1, 1, -1],
                    [1, 1, 0],[1, 0, 1],[1, 0, -1],
                    [1, -1, 0],[1, 0, 0],[1, -1, -1]]

        # 给定阈值后一个生长循环
        while(len(pointQueue)>0):
            # 取出队首并删除
            growSeed = pointQueue[0]
            del pointQueue[0]

            for differ in Next26:
                growPointx = growSeed[0] + differ[0]
                growPointy = growSeed[1] + differ[1]
                growPointz = growSeed[2] + differ[2]

                # 是否是边缘点
                if((growPointx < 0) or (growPointx > maxX - 1) or
                (growPointy < 0) or (growPointy > maxY - 1) or (growPointz < 0) or (growPointz > maxZ - 1)) :
                    continue

                # 是否已经被生长
                if(outImg[growPointx,growPointy,growPointz] == 1):
                    continue

                data = grayImg[growPointx,growPointy,growPointz] # 该点的像素值
                # 判断条件
                # 符合条件则生长，并且加入到生长点队列中
                if(abs(data - pointsMean)<threshold):
                    pointsNum += 1
                    pointsMean = (pointsMean * (pointsNum - 1) + data) / pointsNum
                    outImg[growPointx, growPointy,growPointz] = 1
                    pointQueue.append([growPointx, growPointy,growPointz])
                if pointsNum > 150000:
                    break

        add_pointsNum = pointsNum - old_point_num
        Lt = add_pointsNum / pointsNum


        print("threshold:", threshold, "Lt:", Lt, 'pointsNum:', pointsNum)
        if (Lt > 0.1  and seg_start == 1 and old_point_num > pointsnum_min ) or pointsNum > 100000:
            # pointsNum > 150000 气管一般不会超过这么大的像素个数
            # 150000可以说是气管的上限。
            # 27000为气管的下限
            # print("the best threshold is :", threshold)
            break
        else:
            threshold += 1
            old_point_num = pointsNum

            # 避免第一次有效生长导致停止
            if Lt > 0.9 :
                seg_start = 1

    return threshold - 1


def airways_seg(image_path,
                output_path,
                seed = (236, 201, 252),
                threshold = 10,
                open_grow_mode = None):
    '''
    使用一个定点
    还有阈值
    '''

    lung_image = sitk.ReadImage(image_path)
    lung_arr = sitk.GetArrayFromImage(lung_image) # zyx
    lung_arr_T = lung_arr.transpose((2, 1, 0)) # zyx => xyz


    # 临近像素的阈值，微调可以减少误分割，和少分割 阈值越小，mask越小，默认50，需要动态设置阈值才好
    threshold = regionGrowing_v2(lung_arr_T, seed, open_grow_mode = open_grow_mode)
    print('select threshold:', threshold)
    trachea_img_T, pointsNum = regionGrowing(lung_arr_T, seed, threshold)
    trachea_img = trachea_img_T.transpose((2, 1, 0)) # xyz => zyx

    print('the number of pointsNum: ', pointsNum)

    pred = sitk.GetImageFromArray(trachea_img)
    pred.SetDirection(lung_image.GetDirection())
    pred.SetOrigin(lung_image.GetOrigin())
    pred.SetSpacing(lung_image.GetSpacing())

    # 闭运算填充与连接
    sitk_airways = sitk.BinaryMorphologicalClosing(pred != 0, [5,5,5])

    sitk.WriteImage(sitk_airways, output_path)

    return sitk_airways


def MorphologicalOperation(sitk_maskimg, kernelsize, name='open'):
    """
    morphological operation
    :param sitk_maskimg:input binary image
    :param kernelsize:kernel size
    :param name:operation name
    :return:binary image
    """
    if name == 'open':
        morphoimage = sitk.BinaryMorphologicalOpening(sitk_maskimg != 0)
        return morphoimage
    if name == 'close':
        morphoimage = sitk.BinaryMorphologicalClosing(sitk_maskimg != 0)
        return morphoimage
    if name == 'dilate':
        morphoimage = sitk.BinaryDilate(sitk_maskimg != 0, kernelsize)
        return morphoimage
    if name == 'erode':
        morphoimage = sitk.BinaryErode(sitk_maskimg != 0, kernelsize)
        return morphoimage


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


class LungTracheaSegThread(QThread):
    """肺分割线程"""

    finish_signal = pyqtSignal(bool)  # 使用自定义信号和主线程通讯, 参数是发送信号时附带参数的数据类型
    def __init__(self, seed, ct_nii_path, lung_mask_path, trachea_mask_path, lung_trachea_mask_path, remove_block=None):
        super(LungTracheaSegThread, self).__init__()

        self.seed = seed
        self.ct_nii_path = ct_nii_path
        self.lung_mask_path = lung_mask_path
        self.trachea_mask_path = trachea_mask_path
        self.lung_trachea_mask_path = lung_trachea_mask_path
        # self.remove_block = remove_block

    def run(self):
        """线程执行函数"""

        airways_image = airways_seg(image_path=self.ct_nii_path,
                                    output_path=self.trachea_mask_path,
                                    seed=self.seed)
        
        lung_image = lung_cu_seg(img_path=self.ct_nii_path, remove_block=0)

        lung_arr = sitk.GetArrayFromImage(lung_image)
        airways_arr = sitk.GetArrayFromImage(airways_image)

        # print(lung_arr.shape, airways_arr.shape)
        lung_arr[airways_arr==1] = 0

        lung_mask_image = sitk.GetImageFromArray(lung_arr)
        lung_mask_image.SetSpacing(lung_image.GetSpacing())
        lung_mask_image.SetDirection(lung_image.GetDirection())
        lung_mask_image.SetOrigin(lung_image.GetOrigin())

        # 开运算去毛刺
        lung_mask_image = sitk.BinaryMorphologicalOpening(lung_mask_image != 0, [5,5,5])

        sitk.WriteImage(lung_image, self.lung_trachea_mask_path) # 保存分割的(肺+气管)
        sitk.WriteImage(lung_mask_image, self.lung_mask_path) # 保存分割的肺

        self.finish_signal.emit(True)  # 向主线程传递自动分割信号


class VesselSegThread(QThread):
    """血管分割线程"""

    finish_signal = pyqtSignal(str)  # 使用自定义信号和主线程通讯, 参数是发送信号时附带参数的数据类型
    def __init__(self, ct_nii_path, lung_mask_path, vessel_mask_path):
        super(VesselSegThread, self).__init__()

        self.ct_nii_path = ct_nii_path
        self.lung_mask_path = lung_mask_path
        self.vessel_mask_path = vessel_mask_path

    def run(self):
        """线程执行函数"""

        self.vessle_segment(self.ct_nii_path, self.vessel_mask_path)

        sitk_mask = sitk.ReadImage(self.lung_mask_path)
        kernel_size = 4
        new_sitk_mask = sitk.BinaryErode(sitk_mask != 0, [kernel_size, kernel_size, kernel_size])

        vessel = sitk.ReadImage(self.vessel_mask_path)
        # vessel = MorphologicalOperation(vessel, kernelsize=2, name='close') # 等价以下函数
        vessel = sitk.BinaryMorphologicalClosing(vessel != 0)
        new_vessel_mask = self.get_mask_image(vessel, new_sitk_mask, 0)
        new_vessel_mask = remove_small_region(new_vessel_mask, 256)
        sitk.WriteImage(new_vessel_mask, self.vessel_mask_path)

        self.finish_signal.emit(self.vessel_mask_path)

    def get_mask_image(self, sitk_src, sitk_mask, replace_value=0):
        """
        get mask image
        :param sitk_src:input image
        :param sitk_mask:input mask
        :param replace_value:replace_value of maks value equal 0
        :return:mask image
        """
        array_src = sitk.GetArrayFromImage(sitk_src)
        array_mask = sitk.GetArrayFromImage(sitk_mask)
        array_out = array_src.copy()
        array_out[array_mask == 0] = replace_value
        outmask_sitk = sitk.GetImageFromArray(array_out)
        outmask_sitk.SetDirection(sitk_src.GetDirection())
        outmask_sitk.SetSpacing(sitk_src.GetSpacing())
        outmask_sitk.SetOrigin(sitk_src.GetOrigin())
        return outmask_sitk

    def vessle_segment(self, real_lung_path, vessel_mask_path):
        '''
        分割血管
        :param real_lung_path:实质肺nii.gz
        :param vessel_mask_path:血管掩膜保存路径名
        '''

        sigma_minimum = 2.
        sigma_maximum = 2.
        number_sigma_steps = 8
        lower_threshold = 40

        input_image = itk.imread(real_lung_path, itk.F)
        image_type = type(input_image)
        dimension = input_image.GetImageDimension()
        hessian_pixel_type = itk.SymmetricSecondRankTensor[itk.D, dimension]
        hessian_image_type = itk.Image[hessian_pixel_type, dimension]
        objectness_filter = itk.HessianToObjectnessMeasureImageFilter[hessian_image_type, image_type].New()
        objectness_filter.SetBrightObject(True)
        objectness_filter.SetScaleObjectnessMeasure(True)
        objectness_filter.SetAlpha(0.5)
        objectness_filter.SetBeta(1.0)
        objectness_filter.SetGamma(5.0)
        multi_scale_filter = itk.MultiScaleHessianBasedMeasureImageFilter[image_type, hessian_image_type, image_type].New()
        multi_scale_filter.SetInput(input_image)
        multi_scale_filter.SetHessianToMeasureFilter(objectness_filter)
        multi_scale_filter.SetSigmaStepMethodToLogarithmic()
        multi_scale_filter.SetSigmaMinimum(sigma_minimum)
        multi_scale_filter.SetSigmaMaximum(sigma_maximum)
        multi_scale_filter.SetNumberOfSigmaSteps(number_sigma_steps)

        output_pixel_type = itk.UC
        output_image_type = itk.Image[output_pixel_type, dimension]

        rescale_filter = itk.RescaleIntensityImageFilter[image_type, output_image_type].New()
        rescale_filter.SetInput(multi_scale_filter)

        threshold_filter = itk.BinaryThresholdImageFilter[output_image_type, output_image_type].New()
        threshold_filter.SetInput(rescale_filter.GetOutput())
        threshold_filter.SetLowerThreshold(lower_threshold)
        threshold_filter.SetUpperThreshold(255)
        threshold_filter.SetOutsideValue(0)
        threshold_filter.SetInsideValue(1)

        itk.imwrite(threshold_filter.GetOutput(), vessel_mask_path)


class SkeletonSegThread(QThread):
    """骨骼分割线程"""

    finish_signal = pyqtSignal(str)  # 使用自定义信号和主线程通讯, 参数是发送信号时附带参数的数据类型
    def __init__(self, ct_nii_path, skeleton_mask_path, lowerThreshold=129, parent=None):
        super(SkeletonSegThread, self).__init__(parent)

        self.ct_nii_path = ct_nii_path
        self._skeleton_mask_path = skeleton_mask_path
        self.lowerThreshold = lowerThreshold

    def run(self):
        """线程执行函数"""

        sitk_src = sitk.ReadImage(self.ct_nii_path)
        sitk_seg = sitk.BinaryThreshold(sitk_src, lowerThreshold=self.lowerThreshold, upperThreshold=3000, insideValue=255,
                            outsideValue=0)

        # 主要分割包括肺的骨头
        sitk_open = MorphologicalOperation(sitk_seg, kernelsize=2, name='open')

        array_open = sitk.GetArrayFromImage(sitk_open)
        array_seg = sitk.GetArrayFromImage(sitk_seg)

        # 相减
        array_mask = array_seg - array_open
        sitk_mask = sitk.GetImageFromArray(array_mask)
        sitk_mask.SetDirection(sitk_seg.GetDirection())
        sitk_mask.SetSpacing(sitk_seg.GetSpacing())
        sitk_mask.SetOrigin(sitk_seg.GetOrigin())

        # 最大连通域提取，去除小连接
        skeleton_mask = GetLargestConnectedCompont(sitk_mask)

        # 加上一个闭运算，减少断层
        skeleton_mask = MorphologicalOperation(skeleton_mask, kernelsize=2, name='close')

        sitk.WriteImage(skeleton_mask, self._skeleton_mask_path)

        self.finish_signal.emit(self._skeleton_mask_path)


def window_transform(ct_array, windowWidth, windowCenter, normal=False):
    """
    return: trucated image according to window center and window width
    and normalized to [0,1]
    """
    minWindow = float(windowCenter) - 0.5 * float(windowWidth)
    newimg = (ct_array - minWindow) / float(windowWidth)
    newimg[newimg < 0] = 0
    newimg[newimg > 1] = 1
    if not normal:
        newimg = (newimg * 255).astype('float32')
    return newimg


def skin_seg(ct_nii_path, lung_mask_path, skin_mask_path):

    image = sitk.ReadImage(ct_nii_path, sitk.sitkFloat32)

    origin = image.GetOrigin()
    spacing = image.GetSpacing()
    direction = image.GetDirection()

    # 肺窗/二值处理
    array = sitk.GetArrayFromImage(image)
    array[array > 0] = 255
    array = window_transform(array, 400, -200, False)
    array[array > 0] = 255
    image1 = sitk.GetImageFromArray(array)

    # 提取最大连通量
    image1 = sitk.Cast(image1, sitk.sitkInt16)
    cc = sitk.ConnectedComponent(image1)  # 只支持16位
    stats = sitk.LabelIntensityStatisticsImageFilter()
    stats.SetGlobalDefaultNumberOfThreads(8)
    stats.Execute(cc, image1)
    maxlabel = 0
    maxsize = 0
    for i in stats.GetLabels():
        size = stats.GetPhysicalSize(i)
        if maxsize < size:
            maxlabel = i
            maxsize = size
    labelmaskimage = sitk.GetArrayFromImage(cc)
    outmask = labelmaskimage.copy()
    outmask[labelmaskimage == maxlabel] = 1
    outmask[labelmaskimage != maxlabel] = 0

    outmasksitk = sitk.GetImageFromArray(outmask)

    # 开运算，去掉小白点
    kernelsize = (5, 5, 5)
    image1 = sitk.BinaryMorphologicalOpening(outmasksitk != 0, kernelsize)

    # 使用肺部掩膜和闭运算，填充孔洞
    # 使用到粗分割肺的掩膜
    lung_mask_sitk = sitk.ReadImage(lung_mask_path)

    # 对肺掩膜做一个闭运算,然后填充
    lung_mask_sitk_1 = sitk.BinaryDilate(lung_mask_sitk != 0, (5, 5, 5))
    mask = sitk.GetArrayFromImage(lung_mask_sitk_1)

    image4_array = sitk.GetArrayFromImage(image1)
    image4_array[mask == 1] = 1

    image1 = sitk.GetImageFromArray(image4_array)
    image1 = sitk.BinaryDilate(image1 != 0, (5, 5, 5))

    ## sobel 算子提取边界
    # change data type before edge detection
    image1 = sitk.Cast(image1, sitk.sitkFloat32)

    sobel_op = sitk.SobelEdgeDetectionImageFilter()
    image1 = sobel_op.Execute(image1)
    image1 = sitk.Cast(image1, sitk.sitkInt16)

    # 二值化皮肤mask
    sobel_array = sitk.GetArrayFromImage(image1)
    outmask = sobel_array.copy()
    outmask[sobel_array != 0] = 1

    image1 = sitk.GetImageFromArray(outmask)

    image1.SetOrigin(origin)
    image1.SetSpacing(spacing)
    image1.SetDirection(direction)
    sitk.WriteImage(image1, skin_mask_path)

if __name__ == '__main__':
    pass
