import vtk
import numpy as np
from vtkmodules.util.numpy_support import vtk_to_numpy

def extract_ps(input_data, extent, spacing, rate=0.03, face_up=True):
    """提取Ps点集, 返回各点的坐标

    Args:
        input_data: 输入vtkPolyData -> 'vtkmodules.vtkCommonDataModel.vtkPolyData'
        rate: Specify tolerance in terms of fraction of bounding box length. -> 'float'
        face_up: 判断身体朝向，默认向上 -> 'bool'

    Returns:
        ps_array: 返回皮肤点集坐标 -> 'numpy.ndarray'
    
    Raises:
        None
    """

    # 降采样
    clean_filter = vtk.vtkCleanPolyData()
    clean_filter.SetInputData(input_data)
    clean_filter.SetTolerance(rate)  # Specify tolerance in terms of fraction of bounding box length.
    clean_filter.Update()

    # 定义切割平面的法向量和原点
    normal = [0, 1, 0]
    origin = [extent[1]/2*spacing[0], extent[3]/2*spacing[1], extent[5]/2*spacing[2]]  # 修改原点

    # 创建vtkPlane对象
    plane = vtk.vtkPlane()
    plane.SetNormal(normal)
    plane.SetOrigin(origin)

    # 创建裁剪器
    clipper = vtk.vtkClipPolyData()
    clipper.SetInputData(clean_filter.GetOutput())
    clipper.SetClipFunction(plane)

    # 裁剪平面上方区域
    clipper.GenerateClipScalarsOn()
    if face_up:
        clipper.InsideOutOn()
    clipper.Update()

    # 获取裁剪后的PolyData
    clipped_polydata = clipper.GetOutput()

    ps_array = clipped_polydata.GetPoints().GetData()
    ps_array = vtk_to_numpy(ps_array)

    return ps_array


def extract_po(input_list, reduciton_rate=0.9):
    """提取Po点集, 返回各点的坐标

    Args:
        input_list: 输入重要器官vtkPolyData列表 -> 'list'
        reduciton_rate: 削减的三角形的百分比 -> 'float'

    Returns:
        po_array: 返回器官点集坐标 -> 'numpy.ndarray'
    
    Raises:
        None
    """

    # vtkPolyData合并
    append_filter = vtk.vtkAppendPolyData()
    for polydata in input_list:
        append_filter.AddInputData(polydata)
    append_filter.Update()

    # 降采样
    decimate = vtk.vtkDecimatePro()  
    decimate.SetInputData(append_filter.GetOutput())
    decimate.SetTargetReduction(reduciton_rate)
    decimate.PreserveTopologyOn()  # 是否保持原始的拓扑结构，如果on，将不会发生网格分裂和孔洞
    decimate.Update()

    po_polydata = decimate.GetOutput()

    po_array = po_polydata.GetPoints().GetData()
    po_array = vtk_to_numpy(po_array)
    
    return po_polydata, po_array


def extract_pt(input_data, sample_spacing):
    """提取Pt点集, 返回各点的坐标

    Args:
        input_data: 输入重要器官vtkPolyData -> 'vtkmodules.vtkCommonDataModel.vtkPolyData''
        sample_spacing: 肿瘤采样间距(mm) -> 'int'

    Returns:
        pt_array: 返回肿瘤点集坐标 -> 'numpy.ndarray'
    
    Raises:
        None
    """

    image_shrink3D = vtk.vtkImageShrink3D()
    image_shrink3D.SetShrinkFactors(sample_spacing, sample_spacing, sample_spacing)  # 三个维度的降采样比例
    image_shrink3D.AveragingOn()
    image_shrink3D.SetInputData(input_data)
    image_shrink3D.Update()

    pt_dims = image_shrink3D.GetOutput().GetDimensions()
    pt_spacing = image_shrink3D.GetOutput().GetSpacing()

    pt_scalars = image_shrink3D.GetOutput().GetPointData().GetScalars()  # 获取腐蚀和降采样后靶向点集掩膜的IamgeData点集的像素值
    pt_array = vtk_to_numpy(pt_scalars)  # 点集像素值转数组，被展开成一维
    pt_array = pt_array.reshape(pt_dims[2], pt_dims[1], pt_dims[0])
    pt_array = np.argwhere(pt_array == 1)  # 获取腐蚀和降采样后靶向点集所在的位置（像素值为1的点的位置）z,y,x
    pt_array = pt_array[:, [2, 1, 0]]
    
    # 把像素坐标转化为世界坐标
    pt_array = pt_array * pt_spacing

    return pt_array


if __name__ == "__main__":
    tumor_path = "./test_mask/tumor_mask.nii.gz"

    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(tumor_path)
    reader.Update()

    from mc import marching_cubes
    mc_polydata = marching_cubes(reader.GetOutput())

    ps_array = extract_ps(mc_polydata)
    print(ps_array.shape)

    po_list = [mc_polydata]
    po_polydata, po_array = extract_po(po_list)
    print(po_array.shape)

    pt_array = extract_pt(reader.GetOutput(), 3)
    print(pt_array.shape)