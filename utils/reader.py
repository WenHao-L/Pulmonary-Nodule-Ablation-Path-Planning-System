import vtk


class ErrorObserver:
    """错误观察者
    """

    def __init__(self):

        self.__ErrorOccurred = False
        self.__ErrorMessage = None
        self.CallDataType = "string0"

    def __call__(self, obj, event, message):

        self.__ErrorOccurred = True
        self.__ErrorMessage = message

    def ErrorOccurred(self):

        occ = self.__ErrorOccurred
        self.__ErrorOccurred = False
        return occ

    def ErrorMessage(self):

        return self.__ErrorMessage


def vtk_nii_reader(path):
    """读取nii文件

    Args:
        path: 文件路径 -> 'str'

    Returns:
        error_tag: False
        reader.GetOutput(): 返回vtkImageData -> 'vtkmodules.vtkCommonDataModel.vtkImageData'
    
    Raises:
        error_tag: True
        当读取出错时返回报错信息
    
    """

    error_tag = False
    error_observer = ErrorObserver()
    reader = vtk.vtkNIFTIImageReader()
    reader.AddObserver('ErrorEvent', error_observer)
    reader.SetFileName(path)
    reader.Update()

    if error_observer.ErrorOccurred():
        error_tag = True
        return error_tag, str(error_observer.ErrorMessage())
    else:
        return error_tag, reader.GetOutput()


def vtk_dicom_reader(path):
    """读取dicom文件
    Args:
        path: 文件路径 -> 'str'

    Returns:
        error_tag: False
        reader.GetOutput(): 返回vtkImageData -> 'vtkmodules.vtkCommonDataModel.vtkImageData'
    
    Raises:
        error_tag: True
        当读取出错时返回报错信息
    """

    error_tag = False
    error_observer = ErrorObserver()
    reader = vtk.vtkDICOMImageReader()
    reader.AddObserver('ErrorEvent', error_observer)
    reader.SetDirectoryName(path)
    reader.Update()

    if error_observer.ErrorOccurred():
        error_tag = True
        return error_tag, str(error_observer.ErrorMessage())
    else:
        return error_tag, reader.GetOutput()


if __name__ == "__main__":
    nii_path = "./test_mask/tumor_mask.nii.gz"
    nii_data = vtk_nii_reader(nii_path)

    dicom_path = ""
    dicom_data = vtk_dicom_reader(dicom_path)