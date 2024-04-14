import vtk

def marching_cubes(input_data):
    """MC算法抽取等值面

    Args:
        input_data: 输入vtkImageData -> 'vtkmodules.vtkCommonDataModel.vtkImageData'

    Returns:
        normals.GetOutput(): 返回表面数据 -> 'vtkmodules.vtkCommonDataModel.vtkPolyData'
    
    Raises:
        None
    """

    # 利用MC算法抽取等值面
    mc = vtk.vtkDiscreteMarchingCubes()
    mc.SetInputData(input_data)
    mc.SetValue(0, 1)
    mc.Update()

    # 剔除旧的或废除的数据单元，提高绘制速度
    stripper = vtk.vtkStripper()
    stripper.SetInputData(mc.GetOutput())
    stripper.Update()

    # 对三维模型表面进行平滑
    smoothing_iterations = 15
    pass_band = 0.001
    feature_angle = 120.0
    smoother_filter = vtk.vtkWindowedSincPolyDataFilter()
    smoother_filter.SetInputData(stripper.GetOutput())
    smoother_filter.SetNumberOfIterations(smoothing_iterations)
    smoother_filter.BoundarySmoothingOff()
    smoother_filter.FeatureEdgeSmoothingOff()
    smoother_filter.SetFeatureAngle(feature_angle)
    smoother_filter.SetPassBand(pass_band)
    smoother_filter.NonManifoldSmoothingOn()
    smoother_filter.NormalizeCoordinatesOn()
    smoother_filter.Update()

    fillholes_filter = vtk.vtkFillHolesFilter()
    fillholes_filter.SetInputData(smoother_filter.GetOutput())
    fillholes_filter.SetHoleSize(10.0)
    fillholes_filter.Update()

    triangle_filter = vtk.vtkTriangleFilter()
    triangle_filter.SetInputData(fillholes_filter.GetOutput())
    triangle_filter.Update()

    # Make the triangle windong order consistent
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(triangle_filter.GetOutput())
    normals.ConsistencyOn()
    normals.SplittingOff()
    normals.Update()

    return normals.GetOutput()


if __name__ == "__main__":
    tumor_path = "./test_mask/tumor_mask.nii.gz"
    reader = vtk.vtkNIFTIImageReader()  # 读取ct.nii文件
    reader.SetFileName(tumor_path)
    reader.Update()

    mc_polydata = marching_cubes(reader.GetOutput())

    from view import view
    actor = vtk.vtkActor()
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    iren = vtk.vtkRenderWindowInteractor()

    view(mc_polydata, actor, renderer, render_window, iren, [1.0, 0.0, 0.0], 0.5)