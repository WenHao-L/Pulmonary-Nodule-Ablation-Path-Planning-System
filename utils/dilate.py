import SimpleITK as sitk


def dilate(nii_path, new_nii_path, kernelsize=5):
    """
    nii_path:肿瘤掩膜的路径
    new_nii_path:放大后掩膜的路径
    kernelsize : 放大的比例，整数
    """
    nii = sitk.ReadImage(nii_path)
    kernelsize = (kernelsize, kernelsize, kernelsize)
    new_nii = sitk.BinaryDilate(nii != 0, kernelsize)
    sitk.WriteImage(new_nii, new_nii_path)