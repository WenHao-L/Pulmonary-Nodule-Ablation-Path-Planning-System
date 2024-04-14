import SimpleITK as sitk


def resample_volume(out_spacing, vol):
    """
    将体数据重采样的指定的spacing大小

    Args:
        out_spacing: 指定的spacing, 例如[1, 1, 1]
        vol: sitk读取的image信息, 这里是体数据

    Return:
        new_vol: 重采样后的数据
    
    Raises:
        None
    """

    out_size = [0, 0, 0]

    # 读取文件的size和spacing信息
    input_size = vol.GetSize()
    input_spacing = vol.GetSpacing()

    # 计算改变spacing后的size，用物理尺寸/体素的大小
    out_size[0] = int(input_size[0] * input_spacing[0] / out_spacing[0] + 0.5)
    out_size[1] = int(input_size[1] * input_spacing[1] / out_spacing[1] + 0.5)
    out_size[2] = int(input_size[2] * input_spacing[2] / out_spacing[2] + 0.5)

    # 设定重采样的一些参数
    transform = sitk.Transform()
    transform.SetIdentity()
    resampler = sitk.ResampleImageFilter()
    resampler.SetTransform(transform)
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetOutputOrigin(vol.GetOrigin())
    resampler.SetOutputSpacing(out_spacing)
    resampler.SetOutputDirection(vol.GetDirection())
    resampler.SetSize(out_size)
    new_vol = resampler.Execute(vol)
    return new_vol    

if __name__ == "__main__":
    # 读文件
    vol = sitk.Image(sitk.ReadImage("input.mha"))

    # 重采样
    new_vol = resample_volume([1, 1, 1], vol)

    # 写文件
    wriiter = sitk.ImageFileWriter()
    wriiter.SetFileName("output.nii.gz")
    wriiter.Execute(new_vol)
