import os
import vtk
import sys
import numpy as np
import SimpleITK as sitk
import shutil

from shutil import copy as copy_file
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIntValidator

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QErrorMessage, QMessageBox, QLabel
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from src.mouse_interactor_style import MouseInteractorStyle1, MouseInteractorStyle2, MouseInteractorStyle3
from src.seg import VesselSegThread, SkeletonSegThread

sys.path.append('..')
from ui.ui import Ui_MainWindow
from utils.path_design import AutoPathPlanThread, LargeAutoPathPlanThread
from utils.dcm2nii import dcm2nii
from utils.reader import vtk_nii_reader
from utils.power_time import solve_equation, solve_equation_v2
from utils.eval_tumor_efficacy import eval_tumor_efficacy
from nnunet.inference.predict import predict_from_folder

# # 将vtk报错信息输出到日志文件，避免弹出窗口
# err_out = vtk.vtkFileOutputWindow()
# err_out.SetFileName(os.path.join("log", "VTK_error.txt"))
# vtk_std_err_out = vtk.vtkOutputWindow()
# vtk_std_err_out.SetInstance(err_out)


class MainWindow(QMainWindow, Ui_MainWindow):
    """主窗口"""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)  # 初始化ui
        self._init_operate()  # 初始化操作

    def _init_operate(self):
        """初始化操作, 把QOpenGLWidget转化为vtk可视化窗口, 关联导入按钮"""

        self.cwd = os.getcwd()

        self.lung_tag = False

        self.Po_list = []
        self.info_list = ["", "", "", "", "", ""]

        os.makedirs(os.path.join(self.cwd, 'result'), exist_ok=True)
        os.makedirs(os.path.join(self.cwd, 'mid_result'), exist_ok=True)

        self.vtk_view1 = QVTKRenderWindowInteractor(self.view1)
        self.vtk_view1_layout = QtWidgets.QHBoxLayout(self.view1)  # 创建水平布局
        self.vtk_view1_layout.addWidget(self.vtk_view1)

        self.vtk_view2 = QVTKRenderWindowInteractor(self.view2)
        self.vtk_view2_layout = QtWidgets.QHBoxLayout(self.view2)
        self.vtk_view2_layout.addWidget(self.vtk_view2)

        self.vtk_view3 = QVTKRenderWindowInteractor(self.view3)
        self.vtk_view3_layout = QtWidgets.QHBoxLayout(self.view3)
        self.vtk_view3_layout.addWidget(self.vtk_view3)

        self.vtk_view4 = QVTKRenderWindowInteractor(self.view4)
        self.vtk_view4_layout = QtWidgets.QHBoxLayout(self.view4)
        self.vtk_view4_layout.addWidget(self.vtk_view4)

        # 四个窗口渲染显示
        self.vtk_view1.GetRenderWindow().Render()  
        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()
        self.vtk_view4.GetRenderWindow().Render()

        # 状态栏初始化
        self.info = QLabel(self)
        self.info.setText('')
        self.info.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.statusbar.addPermanentWidget(self.info)
        self.setStatusBar(self.statusbar)

        # 路径规划预设参数
        self.max_needle_depth_edit.setText(str(200))
        self.max_ablation_radius_edit.setText(str(25))
        # self.min_distance_edit.setText(str(5))
        self.ps_rate_edit.setText(str(0.02))
        self.pt_spacing_edit.setText(str(2))
        self.safe_distance_edit.setText(str(5))
        self.neddle_num_edit.setText(str(1))


        # 透明度slider设置
        self.lung_slider.setMinimum(0)
        self.lung_slider.setMaximum(100)
        self.lung_slider.setSingleStep(10)
        self.lung_slider.setValue(0)

        self.trachea_slider.setMinimum(0)
        self.trachea_slider.setMaximum(100)
        self.trachea_slider.setSingleStep(10)
        self.trachea_slider.setValue(0)

        self.vessel_slider.setMinimum(0)
        self.vessel_slider.setMaximum(100)
        self.vessel_slider.setSingleStep(10)
        self.vessel_slider.setValue(0)

        self.skeleton_slider.setMinimum(0)
        self.skeleton_slider.setMaximum(100)
        self.skeleton_slider.setSingleStep(10)
        self.skeleton_slider.setValue(0)

        self.tumor_slider.setMinimum(0)
        self.tumor_slider.setMaximum(100)
        self.tumor_slider.setSingleStep(10)
        self.tumor_slider.setValue(0)

        # self.dilate_tumor_slider.setMinimum(0)
        # self.dilate_tumor_slider.setMaximum(100)
        # self.dilate_tumor_slider.setSingleStep(10)
        # self.dilate_tumor_slider.setValue(0)

        # 按键关联
        self.import_btn.clicked.connect(self._import_event)
        self.lung_trachea_seg_btn.clicked.connect(self._lung_trachea_seg)  # 肺分割
        self.vessel_seg_btn.clicked.connect(self._vessel_seg)  # 血管分割
        self.skeleton_seg_btn.clicked.connect(self._skeleton_seg)  # 骨骼分割
        self.tumor_seg_btn.clicked.connect(self._tumor_seg)  # 肿瘤分割
        self.auto_path_btn.clicked.connect(self._auto_path_plan)  # 自动路径规划

        # 术后评估
        self.post_input_btn.clicked.connect(self._import_event)
        self.post_eval_btn.clicked.connect(self._post_eval)
        self.tumor_eval_btn.clicked.connect(self._tumor_eval)

        # 按键使能
        self.import_btn.setEnabled(True)
        self.lung_trachea_seg_btn.setEnabled(False)
        self.vessel_seg_btn.setEnabled(False)
        self.skeleton_seg_btn.setEnabled(False)
        self.tumor_seg_btn.setEnabled(False)
        self.auto_path_btn.setEnabled(False)

        # 身体朝向设置，默认向上
        self.body_orientation_rbtn.setChecked(True)

        self.large_checkbox.setChecked(False)
        # self.judge_rbtn.setChecked(False)

    def closeEvent(self, event):
        """槽函数:退出触发事件"""

        # # 删除生成的ct_nii
        # nii_dir = os.path.join(self.cwd, 'mid_result')
        # nii_list = os.listdir(nii_dir)
        # for f in nii_list:
        #     nii_path = os.path.join(nii_dir, f)
        #     if os.path.isfile(nii_path):
        #         os.remove(nii_path)

        self.vtk_view1.Finalize()
        self.vtk_view2.Finalize()
        self.vtk_view3.Finalize()
        self.vtk_view4.Finalize()
        QtCore.QCoreApplication.quit()

    def _clear(self):
        """删除文件, 清除view"""

        # # 删除生成的ct_nii
        # nii_dir = os.path.join(self.cwd, 'mid_result')
        # nii_list = os.listdir(nii_dir)
        # for f in nii_list:
        #     nii_path = os.path.join(nii_dir, f)
        #     if os.path.isfile(nii_path):
        #         os.remove(nii_path)

        # # 删除生成的分割掩膜
        # seg_dir = os.path.join(self.cwd, 'result')
        # seg_list = os.listdir(seg_dir)
        # for f in seg_list:
        #     seg_path = os.path.join(seg_dir, f)
        #     if os.path.isfile(seg_path):
        #         os.remove(seg_path)
        
        # 清空Po_list
        self.Po_list = []

        nii_dir = os.path.join(self.cwd, 'mid_result')
        seg_dir = os.path.join(self.cwd, 'result')
        for root, dirs, files in os.walk(nii_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                for sub_name in os.listdir(os.path.join(root, name)):
                    os.remove(os.path.join(root, name, sub_name))
                os.rmdir(os.path.join(root, name))

        for root, dirs, files in os.walk(seg_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                for sub_name in os.listdir(os.path.join(root, name)):
                    os.remove(os.path.join(root, name, sub_name))
                os.rmdir(os.path.join(root, name))

        # 清空view
        self.vtk_view1.Finalize()
        self.vtk_view2.Finalize()
        self.vtk_view3.Finalize()
        self.vtk_view4.Finalize()

    def _import_event(self):
        """槽函数:导入CT"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("请选择导入的CT格式:")
        dicom_btn = mb.addButton("DICOM", QMessageBox.AcceptRole)
        nii_btn = mb.addButton("NII", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        # 返回结果为DICOM
        if mb.clickedButton() == dicom_btn:
            self.ct_dicom_path = QFileDialog.getExistingDirectory(self, "请选择dicom文件", self.cwd)
            if self.ct_dicom_path == "":  # 没选择时返回
                return
            
            # 删除上次保留的文件
            self._clear()
            ct_nii_dir = os.path.join(self.cwd, 'mid_result')
            self.ct_nii_path = os.path.join(ct_nii_dir, "nii_0000.nii.gz")

            dcm2nii(self.ct_dicom_path, ct_nii_dir)

        elif mb.clickedButton() == nii_btn:
            self.ct_nii_path, _type = QFileDialog.getOpenFileNames(
                self, "请选择.nii.gz文件", self.cwd, "nii Files (*.nii.gz)")
            if self.ct_nii_path == []:  # 没选择时返回
                return
            
            # 删除上次保留的文件
            self._clear()
            self.ct_nii_path = self.ct_nii_path[0]  # 取路径
           
            ct_nii_dir = os.path.join(self.cwd, 'mid_result')
            copy_file(self.ct_nii_path, os.path.join(ct_nii_dir, "nii_0000.nii.gz"))  # 复制文件
            self.ct_nii_path = os.path.join(ct_nii_dir, "nii_0000.nii.gz")

        else:
            return
        
        error_tag, self.reader_output = vtk_nii_reader(self.ct_nii_path)

        # 判断是否发生错误
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(self.reader_output)
            error_message.exec_()
            return
    
        else:
            # 显示CT路径
            self.import_path_edit.setText(str(self.ct_nii_path))
            self._key_enable()

    def _key_enable(self):
        """按键使能, 如果导入dicom格式, 则接收转化后的nii路径, 如果是nii格式, 则直接接收"""

        # 按键使能
        self.lung_trachea_seg_btn.setEnabled(True)
        self.vessel_seg_btn.setEnabled(True)
        self.skeleton_seg_btn.setEnabled(True)
        self.tumor_seg_btn.setEnabled(True)
        self.auto_path_btn.setEnabled(True)


        self.lung_tag = False

        self.extent = self.reader_output.GetExtent()
        # self.extent = np.array(self.extent) + 1  # 由0开始转化为由1开始
        self.spacing = self.reader_output.GetSpacing()
        self.dim = self.reader_output.GetDimensions()
        self.origin = self.reader_output.GetOrigin()

        # 显示基本信息
        self.message_edit.setText("Origin: {}\nSpacing: {}\nDimensions: {}\n".format(str(self.origin), str(self.spacing), str(self.dim), ))  # 显示 origin, spacing, dimensions

        # 设置滚动条范围
        self.view1_scrollbar.setRange(self.extent[4], self.extent[5])  # 轴状位(z坐标变化)
        self.view2_scrollbar.setRange(self.extent[0], self.extent[1])  # 矢状位(x坐标变化)
        self.view3_scrollbar.setRange(self.extent[2], self.extent[3])  # 冠状位(y坐标变化)

        # 设置滚动条步长
        self.view1_scrollbar.setSingleStep(1)
        self.view2_scrollbar.setSingleStep(1)
        self.view3_scrollbar.setSingleStep(1)

        # 设置像素坐标显示范围
        self.x_pixel_edit.setValidator(QIntValidator(self.extent[0], self.extent[1]))
        self.y_pixel_edit.setValidator(QIntValidator(self.extent[2], self.extent[3]))
        self.z_pixel_edit.setValidator(QIntValidator(self.extent[4], self.extent[5]))
        
        # 中心点像素坐标
        self.center_pixel = [
            0.5 * self.extent[1],
            0.5 * self.extent[3],
            0.5 * self.extent[5]
        ]

        # 中心点世界坐标
        self.center_world = [
            self.spacing[0] * 0.5 * self.extent[1],
            self.spacing[1] * 0.5 * self.extent[3],
            self.spacing[2] * 0.5 * self.extent[5]
        ]

        # 设置初始位置滚动条初始位置
        self.view1_scrollbar.setValue(self.center_pixel[2])
        self.view2_scrollbar.setValue(self.center_pixel[0])
        self.view3_scrollbar.setValue(self.center_pixel[1])

        # 显示当前初始化像素坐标
        self.x_pixel_edit.setText(str(int(self.center_pixel[0])))
        self.y_pixel_edit.setText(str(int(self.center_pixel[1])))
        self.z_pixel_edit.setText(str(int(self.center_pixel[2])))

        # 显示当前初始化世界坐标
        self.x_world_edit.setText(str(round(self.center_world[0], 2)))
        self.y_world_edit.setText(str(round(self.center_world[1], 2)))
        self.z_world_edit.setText(str(round(self.center_world[2], 2)))

        # 设置初始窗宽窗位, 肺窗
        self.window_width_edit.setValidator(QIntValidator())  # 设置只能输入int类型
        self.window_width_edit.setText(str(1500))  # 窗宽
        self.window_level_edit.setValidator(QIntValidator())  # 设置只能输入int类型
        self.window_level_edit.setText(str(-450))  # 窗位

        # 透明度条归零
        self.lung_slider.setValue(0)
        self.trachea_slider.setValue(0)
        self.vessel_slider.setValue(0)
        self.skeleton_slider.setValue(0)
        self.tumor_slider.setValue(0)
        # self.dilate_tumor_slider.setValue(0)

        # 显示医学三视图
        self._mpr_show() 

        # 设置关联槽函数
        self._connect()

    def _connect(self):
        """设置关联函数"""

        # 滚动条关联
        self.view1_scrollbar.valueChanged.connect(self._view1_scrollbar_changed)
        self.view2_scrollbar.valueChanged.connect(self._view2_scrollbar_changed)
        self.view3_scrollbar.valueChanged.connect(self._view3_scrollbar_changed)

        # 像素坐标槽关联
        self.x_pixel_edit.textChanged.connect(self._x_pixel_changed)
        self.y_pixel_edit.textChanged.connect(self._y_pixel_changed)
        self.z_pixel_edit.textChanged.connect(self._z_pixel_changed)

        # 窗宽窗位槽关联
        self.window_width_edit.editingFinished.connect(self._window_width_changed)
        self.window_level_edit.editingFinished.connect(self._window_level_changed)

    def _mpr_show(self):
        """绘制医学三视图"""

        self._delete_view123()

        # 轴状矩阵
        self.axial_matrix = [
            1, 0, 0, 0,
            0, -1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]

        # 矢状矩阵
        self.sagittal_matrix = [
            0, 0, 1, 0,
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 0, 1
        ]

        # 冠状矩阵
        self.coronal_matrix = [
            1, 0, 0, 0,
            0, 0, 1, 0,
            0, 1, 0, 0,
            0, 0, 0, 1
        ]

        # view1_slicer
        self.view1_reslice_axes = vtk.vtkMatrix4x4()
        self.view1_reslice_axes.DeepCopy(self.axial_matrix)

        self.view1_slice_renderer = vtk.vtkRenderer()
        self.view1_slice_renderer.SetLayer(0)

        self.view1_reslice = vtk.vtkImageReslice()
        self.view1_reslice.SetInputData(self.reader_output)  # 设置数据输入源
        self.view1_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view1_reslice.SetResliceAxes(self.view1_reslice_axes)  # 设置矩阵
        self.view1_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                self.center_world[1],
                                                self.center_world[2])  # 设置切片中心点
        self.view1_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view1_window_mapper = vtk.vtkImageMapToWindowLevelColors()
        self.view1_window_mapper.SetInputConnection(self.view1_reslice.GetOutputPort())  # 设置图像数据
        self.view1_window_mapper.SetWindow(1500)  # 初始化窗宽
        self.view1_window_mapper.SetLevel(-450)  # 初始化窗位

        self.view1_slice_actor = vtk.vtkImageActor()
        self.view1_slice_actor.GetMapper().SetInputConnection(self.view1_window_mapper.GetOutputPort())  # 添加映射器
        self.view1_slice_renderer.AddActor(self.view1_slice_actor)  # 添加切片actor
        self.view1_slice_renderer.SetBackground(0.0, 0.0, 0.0)  # 设置背景颜色

        # view2_slicer
        self.view2_reslice_axes = vtk.vtkMatrix4x4()
        self.view2_reslice_axes.DeepCopy(self.sagittal_matrix)

        self.view2_slice_renderer = vtk.vtkRenderer()
        self.view2_slice_renderer.SetLayer(0)

        self.view2_reslice = vtk.vtkImageReslice()
        self.view2_reslice.SetInputData(self.reader_output)  # 设置数据输入源
        self.view2_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view2_reslice.SetResliceAxes(self.view2_reslice_axes)  # 设置矩阵
        self.view2_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                self.center_world[1],
                                                self.center_world[2])  # 设置切片中心点
        self.view2_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view2_window_mapper = vtk.vtkImageMapToWindowLevelColors()
        self.view2_window_mapper.SetInputConnection(self.view2_reslice.GetOutputPort())  # 设置图像数据
        self.view2_window_mapper.SetWindow(1500)  # 初始化窗宽
        self.view2_window_mapper.SetLevel(-450)  # 初始化窗位

        self.view2_slice_actor = vtk.vtkImageActor()
        self.view2_slice_actor.GetMapper().SetInputConnection(self.view2_window_mapper.GetOutputPort())  # 添加映射器
        self.view2_slice_renderer.AddActor(self.view2_slice_actor)  # 添加切片actor
        self.view2_slice_renderer.SetBackground(0.0, 0.0, 0.0)  # 设置背景颜色

        # view3_slicer
        self.view3_reslice_axes = vtk.vtkMatrix4x4()
        self.view3_reslice_axes.DeepCopy(self.coronal_matrix)

        self.view3_slice_renderer = vtk.vtkRenderer()
        self.view3_slice_renderer.SetLayer(0)

        self.view3_reslice = vtk.vtkImageReslice()
        self.view3_reslice.SetInputData(self.reader_output)  # 设置数据输入源
        self.view3_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view3_reslice.SetResliceAxes(self.view3_reslice_axes)  # 设置矩阵
        self.view3_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                self.center_world[1],
                                                self.center_world[2])  # 设置切片中心点
        self.view3_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view3_window_mapper = vtk.vtkImageMapToWindowLevelColors()
        self.view3_window_mapper.SetInputConnection(self.view3_reslice.GetOutputPort())  # 设置图像数据
        self.view3_window_mapper.SetWindow(1500)  # 初始化窗宽
        self.view3_window_mapper.SetLevel(-450)  # 初始化窗位

        self.view3_slice_actor = vtk.vtkImageActor()
        self.view3_slice_actor.GetMapper().SetInputConnection(self.view3_window_mapper.GetOutputPort())  # 添加映射器
        self.view3_slice_renderer.AddActor(self.view3_slice_actor)  # 添加切片actor
        self.view3_slice_renderer.SetBackground(0.0, 0.0, 0.0)  # 设置背景颜色

        # 十字轴定点
        self.hpoint = [
            [-self.center_world[0], 0, 0], [self.center_world[0], 0, 0],
            [-self.center_world[0], 0, 0], [self.center_world[0], 0, 0],
            [-self.center_world[0], 0, 0], [self.center_world[0], 0, 0]
        ]

        self.vpoint = [
            [0, -self.center_world[1], 0], [0, self.center_world[1], 0],
            [0, -self.center_world[2], 0], [0, self.center_world[2], 0],
            [0, -self.center_world[2], 0], [0, self.center_world[2], 0]
        ]

        # view1十字轴
        self.view1_cross_renderer = vtk.vtkRenderer()
        self.view1_cross_renderer.SetLayer(1)

        self.view1_hline_source = vtk.vtkLineSource()  # 横轴
        self.view1_hline_source.SetPoint1(self.hpoint[0])
        self.view1_hline_source.SetPoint2(self.hpoint[1])
        self.view1_hline_source.Update()

        self.view1_hline_mapper = vtk.vtkDataSetMapper()
        self.view1_hline_mapper.SetInputConnection(self.view1_hline_source.GetOutputPort())

        self.view1_hline_actor = vtk.vtkActor()
        self.view1_hline_actor.SetMapper(self.view1_hline_mapper)
        self.view1_hline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view1_cross_renderer.AddActor(self.view1_hline_actor)  # 添加横轴actor

        self.view1_vline_source = vtk.vtkLineSource()  # 竖轴
        self.view1_vline_source.SetPoint1(self.vpoint[0])
        self.view1_vline_source.SetPoint2(self.vpoint[1])
        self.view1_vline_source.Update()

        self.view1_vline_mapper = vtk.vtkDataSetMapper()
        self.view1_vline_mapper.SetInputConnection(self.view1_vline_source.GetOutputPort())

        self.view1_vline_actor = vtk.vtkActor()
        self.view1_vline_actor.SetMapper(self.view1_vline_mapper)

        self.view1_vline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view1_cross_renderer.AddActor(self.view1_vline_actor)  # 添加纵轴actor

        # view2十字轴
        self.view2_cross_renderer = vtk.vtkRenderer()
        self.view2_cross_renderer.SetLayer(1)

        self.view2_hline_source = vtk.vtkLineSource()  # 横轴
        self.view2_hline_source.SetPoint1(self.hpoint[2])
        self.view2_hline_source.SetPoint2(self.hpoint[3])
        self.view2_hline_source.Update()

        self.view2_hline_mapper = vtk.vtkDataSetMapper()
        self.view2_hline_mapper.SetInputConnection(self.view2_hline_source.GetOutputPort())

        self.view2_hline_actor = vtk.vtkActor()
        self.view2_hline_actor.SetMapper(self.view2_hline_mapper)

        self.view2_hline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view2_cross_renderer.AddActor(self.view2_hline_actor)  # 添加横轴actor

        self.view2_vline_source = vtk.vtkLineSource()  # 竖轴
        self.view2_vline_source.SetPoint1(self.vpoint[2])
        self.view2_vline_source.SetPoint2(self.vpoint[3])
        self.view2_vline_source.Update()

        self.view2_vline_mapper = vtk.vtkDataSetMapper()
        self.view2_vline_mapper.SetInputConnection(self.view2_vline_source.GetOutputPort())

        self.view2_vline_actor = vtk.vtkActor()
        self.view2_vline_actor.SetMapper(self.view2_vline_mapper)

        self.view2_vline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view2_cross_renderer.AddActor(self.view2_vline_actor)  # 添加纵轴actor

        # view3十字轴
        self.view3_cross_renderer = vtk.vtkRenderer()
        self.view3_cross_renderer.SetLayer(1)

        self.view3_hline_source = vtk.vtkLineSource()  # 横轴
        self.view3_hline_source.SetPoint1(self.hpoint[4])
        self.view3_hline_source.SetPoint2(self.hpoint[5])
        self.view3_hline_source.Update()

        self.view3_hline_mapper = vtk.vtkDataSetMapper()
        self.view3_hline_mapper.SetInputConnection(self.view3_hline_source.GetOutputPort())

        self.view3_hline_actor = vtk.vtkActor()
        self.view3_hline_actor.SetMapper(self.view3_hline_mapper)

        self.view3_hline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view3_cross_renderer.AddActor(self.view3_hline_actor)  # 添加横轴actor

        self.view3_vline_source = vtk.vtkLineSource()  # 竖轴
        self.view3_vline_source.SetPoint1(self.vpoint[4])
        self.view3_vline_source.SetPoint2(self.vpoint[5])
        self.view3_vline_source.Update()

        self.view3_vline_mapper = vtk.vtkDataSetMapper()
        self.view3_vline_mapper.SetInputConnection(self.view3_vline_source.GetOutputPort())

        self.view3_vline_actor = vtk.vtkActor()
        self.view3_vline_actor.SetMapper(self.view3_vline_mapper)

        self.view3_vline_actor.GetProperty().SetColor(1.0, 0.0, 0.0)  # 设置十字轴颜色
        self.view3_cross_renderer.AddActor(self.view3_vline_actor)  # 添加纵轴actor

        # view1

        self.vtk_view1.GetRenderWindow().SetNumberOfLayers(2)
        self.vtk_view1.GetRenderWindow().AddRenderer(self.view1_slice_renderer)  # view1渲染窗口添加渲染器
        self.vtk_view1.GetRenderWindow().AddRenderer(self.view1_cross_renderer)  # view1渲染窗口添加渲染器
        self.style1 = MouseInteractorStyle1(self.extent, self.spacing, self)
        self.style1.SetDefaultRenderer(self.view1_slice_renderer)
        # self.style1.SetRendererCollection(self.vtk_view1.GetRenderWindow().GetRenderers())
        self.iren1 = self.vtk_view1.GetRenderWindow().GetInteractor()
        self.iren1.SetInteractorStyle(self.style1)
        self.vtk_view1.GetRenderWindow().Render()  # 渲染窗口
        self.iren1.Initialize()
        self.iren1.Start()

        # view2
        self.vtk_view2.GetRenderWindow().SetNumberOfLayers(2)
        self.vtk_view2.GetRenderWindow().AddRenderer(self.view2_slice_renderer)  # view1渲染窗口添加渲染器
        self.vtk_view2.GetRenderWindow().AddRenderer(self.view2_cross_renderer)  # view1渲染窗口添加渲染器
        self.style2 = MouseInteractorStyle2(self.extent, self.spacing, self)
        self.style2.SetDefaultRenderer(self.view2_slice_renderer)
        # self.style2.SetRendererCollection(self.vtk_view2.GetRenderWindow().GetRenderers())
        self.iren2 = self.vtk_view2.GetRenderWindow().GetInteractor()
        self.iren2.SetInteractorStyle(self.style2)
        self.vtk_view2.GetRenderWindow().Render()  # 渲染窗口
        self.iren2.Initialize()
        self.iren2.Start()

        # view3

        self.vtk_view3.GetRenderWindow().SetNumberOfLayers(2)
        self.vtk_view3.GetRenderWindow().AddRenderer(self.view3_slice_renderer)  # view1渲染窗口添加渲染器
        self.vtk_view3.GetRenderWindow().AddRenderer(self.view3_cross_renderer)  # view1渲染窗口添加渲染器
        self.style3 = MouseInteractorStyle3(self.extent, self.spacing, self)
        self.style3.SetDefaultRenderer(self.view3_slice_renderer)
        # self.style3.SetRendererCollection(self.vtk_view3.GetRenderWindow().GetRenderers())
        self.iren3 = self.vtk_view3.GetRenderWindow().GetInteractor()
        self.iren3.SetInteractorStyle(self.style3)
        self.vtk_view3.GetRenderWindow().Render()  # 渲染窗口
        self.iren3.Initialize()
        self.iren3.Start()

        # 建立世界坐标系
        self.axis_actor = vtk.vtkAxesActor()
        self.axis_actor.SetPosition(0, 0, 0)
        self.axis_actor.SetTotalLength(100, 100, 100)
        self.axis_actor.SetShaftType(0)
        self.axis_actor.SetAxisLabels(0)
        self.axis_actor.SetCylinderRadius(0.02)

        self.view4_renderer = vtk.vtkRenderer()
        self.view4_renderer.AddActor(self.axis_actor)
        self.vtk_view4.GetRenderWindow().AddRenderer(self.view4_renderer)
        self.vtk_view4.GetRenderWindow().Render()  # view4开始渲染
        self.iren4 = self.vtk_view4.GetRenderWindow().GetInteractor()
        self.iren4.Initialize()
        self.iren4.Start()

    def _view1_scrollbar_changed(self):
        """槽函数:view1滚动条值改变时触发"""

        self.z_pixel_edit.setText(str(self.view1_scrollbar.value()))  # 改变坐标z

        self.center_pixel[2] = self.view1_scrollbar.value()  # 获取中心点像素坐标z
        self.view1_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                 self.center_world[1],
                                                 self.center_pixel[2] * self.spacing[2])  # 设置切片中心点
        self.vtk_view1.GetRenderWindow().Render()  # 刷新窗口

    def _view2_scrollbar_changed(self):
        """槽函数:view2滚动条值改变时触发"""
        
        self.x_pixel_edit.setText(str(self.view2_scrollbar.value()))  # 改变坐标z

        self.center_pixel[0] = self.view2_scrollbar.value()  # 获取中心点像素坐标x
        self.view2_reslice.SetResliceAxesOrigin(self.center_pixel[0] * self.spacing[0],
                                                 self.center_world[1],
                                                 self.center_world[2])  # 设置切片中心点
        self.vtk_view2.GetRenderWindow().Render()  # 刷新窗口

    def _view3_scrollbar_changed(self):
        """槽函数:view3滚动条值改变时触发"""

        self.y_pixel_edit.setText(str(self.view3_scrollbar.value()))  # 改变坐标z

        self.center_pixel[1] = self.view3_scrollbar.value()  # 获取中心点像素坐标y
        self.view3_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                 self.center_pixel[1] * self.spacing[1],
                                                 self.center_world[2])  # 设置切片中心点
        self.vtk_view3.GetRenderWindow().Render()  # 刷新窗口

    def _x_pixel_changed(self):
        """槽函数:x坐标改变时触发"""
        if self.x_pixel_edit.text() == "":
            self.x_pixel_edit.setText(str(1))

        self.x_world_edit.setText(str(round(self.spacing[0] * int(self.x_pixel_edit.text()), 2)))  # 改变世界坐标
        self.view2_scrollbar.setValue(int(self.x_pixel_edit.text()))  # 改变view2滚动条的值

        self.vpoint[0] = [
            (int(self.x_pixel_edit.text()) - 0.5 * self.extent[1]) * self.spacing[0],
            -0.5 * self.extent[3] * self.spacing[1],
            1
        ]

        self.vpoint[1] = [
            (int(self.x_pixel_edit.text()) - 0.5 * self.extent[1]) * self.spacing[0],
            0.5 * self.extent[3] * self.spacing[1],
            1
        ]

        self.vpoint[4] = [
            (int(self.x_pixel_edit.text()) - 0.5 * self.extent[1]) * self.spacing[0],
            -0.5 * self.extent[5] * self.spacing[2],
            1
        ]

        self.vpoint[5] = [
            (int(self.x_pixel_edit.text()) - 0.5 * self.extent[1]) * self.spacing[0],
            0.5 * self.extent[5] * self.spacing[2],
            1
        ]

        # 改变十字轴的位置
        self.view1_vline_source.SetPoint1(self.vpoint[0])
        self.view1_vline_source.SetPoint2(self.vpoint[1])
        self.view1_vline_source.Update()

        self.view3_vline_source.SetPoint1(self.vpoint[4])
        self.view3_vline_source.SetPoint2(self.vpoint[5])
        self.view3_vline_source.Update()

        self.vtk_view1.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()

    def _y_pixel_changed(self):
        """槽函数:y坐标改变时触发"""

        if self.y_pixel_edit.text() == '':
            self.y_pixel_edit.setText(str(1))

        self.y_world_edit.setText(str(round(self.spacing[1] * int(self.y_pixel_edit.text()), 2)))
        self.view3_scrollbar.setValue(int(self.y_pixel_edit.text()))

        self.hpoint[0] = [
            -0.5 * self.extent[1] * self.spacing[0],
            (0.5 * self.extent[3] - int(self.y_pixel_edit.text())) * self.spacing[1],
            1
        ]

        self.hpoint[1] = [
            0.5 * self.extent[1] * self.spacing[0],
            (0.5 * self.extent[3] - int(self.y_pixel_edit.text())) * self.spacing[1],
            1
        ]

        self.vpoint[2] = [
            (int(self.y_pixel_edit.text()) - 0.5 * self.extent[3]) * self.spacing[1],
            -0.5 * self.extent[5] * self.spacing[2],
            1
        ]

        self.vpoint[3] = [
            (int(self.y_pixel_edit.text()) - 0.5 * self.extent[3]) * self.spacing[1],
            0.5 * self.extent[5] * self.spacing[2],
            1
        ]

        # 改变十字轴的位置
        self.view1_hline_source.SetPoint1(self.hpoint[0])
        self.view1_hline_source.SetPoint2(self.hpoint[1])
        self.view1_hline_source.Update()

        self.view2_vline_source.SetPoint1(self.vpoint[2])
        self.view2_vline_source.SetPoint2(self.vpoint[3])
        self.view2_vline_source.Update()

        self.vtk_view1.GetRenderWindow().Render()
        self.vtk_view2.GetRenderWindow().Render()

    def _z_pixel_changed(self):
        """槽函数:z坐标改变时触发"""

        if self.z_pixel_edit.text() == '':
            self.z_pixel_edit.setText(str(1))

        self.z_world_edit.setText(str(round(self.spacing[2] * int(self.z_pixel_edit.text()), 2)))
        self.view1_scrollbar.setValue(int(self.z_pixel_edit.text()))

        self.hpoint[2] = [
            -0.5 * self.extent[3] * self.spacing[1],
            (int(self.z_pixel_edit.text()) - 0.5 * self.extent[5]) * self.spacing[2],
            1
        ]

        self.hpoint[3] = [
            0.5 * self.extent[3] * self.spacing[1],
            (int(self.z_pixel_edit.text()) - 0.5 * self.extent[5]) * self.spacing[2],
            1
        ]

        self.hpoint[4] = [
            -0.5 * self.extent[1] * self.spacing[0],
            (int(self.z_pixel_edit.text()) - 0.5 * self.extent[5]) * self.spacing[2],
            1
        ]

        self.hpoint[5] = [
            0.5 * self.extent[1] * self.spacing[0],
            (int(self.z_pixel_edit.text()) - 0.5 * self.extent[5]) * self.spacing[2],
            1
        ]

        # 改变十字轴的位置
        self.view2_hline_source.SetPoint1(self.hpoint[2])
        self.view2_hline_source.SetPoint2(self.hpoint[3])
        self.view2_hline_source.Update()

        self.view3_hline_source.SetPoint1(self.hpoint[4])
        self.view3_hline_source.SetPoint2(self.hpoint[5])
        self.view3_hline_source.Update()

        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()
        pass

    def _window_width_changed(self):
        """槽函数:改变窗宽"""

        self.view1_window_mapper.SetWindow(int(self.window_width_edit.text()))
        self.view2_window_mapper.SetWindow(int(self.window_width_edit.text()))
        self.view3_window_mapper.SetWindow(int(self.window_width_edit.text()))

        self.vtk_view1.GetRenderWindow().Render()  # 刷新窗口
        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()

    def _window_level_changed(self):
        """槽函数:改变窗位"""

        self.view1_window_mapper.SetLevel(int(self.window_level_edit.text()))
        self.view2_window_mapper.SetLevel(int(self.window_level_edit.text()))
        self.view3_window_mapper.SetLevel(int(self.window_level_edit.text()))

        self.vtk_view1.GetRenderWindow().Render()  # 刷新窗口
        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()

    def _lung_trachea_seg(self):
        """槽函数:肺分割和气管分割"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("是否导入肺和气管掩膜？")
        import_btn = mb.addButton("导入", QMessageBox.AcceptRole)
        auto_btn = mb.addButton("自动分割", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        # 判断返回结果处理相应事项
        if mb.clickedButton() == import_btn:
            self.lung_mask_path, _type = QFileDialog.getOpenFileNames(
                self, "请导入肺掩膜", self.cwd, "nii Files (*.nii.gz)")
            if self.lung_mask_path == []:  # 没选择时返回
                return
            self.lung_mask_path = self.lung_mask_path[0]  # 取路径

            self.trachea_mask_path, _type = QFileDialog.getOpenFileNames(
                self, "请导入气管掩膜", self.cwd, "nii Files (*.nii.gz)")

            if self.trachea_mask_path == []:  # 没选择时返回
                return

            self.trachea_mask_path = self.trachea_mask_path[0]

            self.lung_trachea_mask_path = os.path.join(self.cwd, 'result', 'lung_trachea_mask.nii.gz')
            lung_mask_img = sitk.ReadImage(self.lung_mask_path)
            trachea_mask_img = sitk.ReadImage(self.trachea_mask_path)
            lung_mask_img = sitk.Cast(lung_mask_img, sitk.sitkUInt8)
            trachea_mask_img = sitk.Cast(trachea_mask_img, sitk.sitkUInt8)

            if lung_mask_img.GetSize() != trachea_mask_img.GetSize():
                QtWidgets.QMessageBox.warning(self, '警告', '肺掩膜和气管掩膜不匹配', QtWidgets.QMessageBox.Yes)
                return

            merged_mask = sitk.Maximum(lung_mask_img, trachea_mask_img)
            sitk.WriteImage(merged_mask, self.lung_trachea_mask_path)

            self.lung_trachea_seg_btn.setEnabled(False)
            self.info_list[0] = "正在进行肺和气管分割..."
            self.info.setText("  ".join(self.info_list))
            self._lung_trachea_rebuild(True)  # 肺重建

        elif mb.clickedButton() == auto_btn:
            seed_mb = QMessageBox(self)
            seed_mb.setWindowTitle("消息提示")
            seed_mb.setInformativeText("请在冠状面中选择气管种子点:")
            accept_btn = seed_mb.addButton("OK", QMessageBox.AcceptRole)
            seed_mb.setStandardButtons(QMessageBox.Cancel)
            seed_mb.setDefaultButton(QMessageBox.Cancel)
            seed_mb.exec()

            if seed_mb.clickedButton() == accept_btn:
                # self.info_list[0] = "正在进行肺和气管分割..."
                # self.info.setText("  ".join(self.info_list))
                self.lung_trachea_seg_btn.setEnabled(False)
                self.style3.seed_flag = True
            else:
                return
        else:
            return

    def _lung_trachea_rebuild(self, signal):
        """槽函数:肺重建和气管重建"""

        if hasattr(self, 'lung_actor'):
            self.view4_renderer.RemoveActor(self.lung_actor)  # 重新导入时删除上一次的actor

        self.lung_actor = vtk.vtkActor()
        self.lung_polydata = self._rebuild(self.lung_mask_path, self.lung_actor, self.view4_renderer, [1, .94, .25])
        if self.lung_polydata == False:
            del self.lung_actor
            self.lung_tag = False
            self.lung_trachea_seg_btn.setEnabled(True)
            self.info_list[0] = ""
            self.info.setText("  ".join(self.info_list))
            return
        if hasattr(self, 'trachea_actor'):
            self.view4_renderer.RemoveActor(self.trachea_actor)

        self.trachea_actor = vtk.vtkActor()
        self.trachea_polydata = self._rebuild(self.trachea_mask_path, self.trachea_actor, self.view4_renderer, [0.5, 0.2, .75])
        if self.trachea_polydata == False:
            del self.trachea_actor
            self.lung_tag = False
            self.lung_trachea_seg_btn.setEnabled(True)
            self.info_list[0] = ""
            self.info.setText("  ".join(self.info_list))
            return
        self.Po_list.append(self.trachea_polydata)

        self.lung_slider.valueChanged.connect(self._set_lung_opacity)

        self.lung_slider.setValue(10)
        self.trachea_slider.setValue(100)
        self.trachea_slider.valueChanged.connect(self._set_trachea_opacity)

        self.lung_tag = True  # 标记肺分割完成，可进行血管分割

        self.lung_trachea_seg_btn.setEnabled(True)
        self.info_list[0] = "肺和气管分割完成！"
        self.info.setText("  ".join(self.info_list))

    def _set_lung_opacity(self):
        """槽函数:调整肺透明度"""
        self.lung_actor.GetProperty().SetOpacity(self.lung_slider.value() / 100)
        self.vtk_view4.GetRenderWindow().Render()

    def _set_trachea_opacity(self):
        """槽函数:调整气管透明度"""
        self.trachea_actor.GetProperty().SetOpacity(self.trachea_slider.value() / 100)
        self.vtk_view4.GetRenderWindow().Render()

    def _vessel_seg(self):
        """槽函数:血管分割"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("是否导入血管掩膜？")
        import_btn = mb.addButton("导入", QMessageBox.AcceptRole)
        auto_btn = mb.addButton("自动分割", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        # 判断返回结果处理相应事项
        if mb.clickedButton() == import_btn:
            self.vessel_mask_path, _type = QFileDialog.getOpenFileNames(
                self, "请导入血管掩膜", self.cwd, "nii Files (*.nii.gz)")
            if self.vessel_mask_path == []:  # 没选择时返回
                return
            
            self.vessel_seg_btn.setEnabled(False)
            self.info_list[1] = "正在进行血管分割..."
            self.info.setText("  ".join(self.info_list))
            self.vessel_mask_path = self.vessel_mask_path[0]
            self._vessel_rebuild(self.vessel_mask_path)

        elif mb.clickedButton() == auto_btn:
            if not self.lung_tag:
                QtWidgets.QMessageBox.warning(self, '警告', '请先进行肺部分割', QtWidgets.QMessageBox.Yes)
                return

            self.vessel_seg_btn.setEnabled(False)
            self.info_list[1] = "正在进行血管分割..."
            self.info.setText("  ".join(self.info_list))
            self.vessel_mask_path = os.path.join(self.cwd, 'result', 'vessel_mask.nii.gz')

            self.vessel_seg_thread = VesselSegThread(self.ct_nii_path, self.lung_mask_path, self.vessel_mask_path)
            self.vessel_seg_thread.finish_signal.connect(self._vessel_rebuild)
            self.vessel_seg_thread.start()

        else:
            return

    def _vessel_rebuild(self, vessel_mask_path):
        """槽函数:血管重建"""

        if hasattr(self, 'vessel_actor'):
            self.view4_renderer.RemoveActor(self.vessel_actor)

        self.vessel_actor = vtk.vtkActor()
        self.vessel_polydata = self._rebuild(self.vessel_mask_path, self.vessel_actor, self.view4_renderer, [1, 0.5, 0.5])
        if self.vessel_polydata == False:
            del self.vessel_actor
            self.vessel_seg_btn.setEnabled(True)
            self.info_list[1] = ""
            self.info.setText("  ".join(self.info_list))
            return
        self.Po_list.append(self.vessel_polydata)

        self.vessel_slider.valueChanged.connect(self._set_vessel_opacity)
        self.vessel_slider.setValue(100)

        self.vessel_seg_btn.setEnabled(True)
        self.info_list[1] = "血管分割完成！"
        self.info.setText("  ".join(self.info_list))

    def _set_vessel_opacity(self):
        """槽函数:调整血管透明度"""

        self.vessel_actor.GetProperty().SetOpacity(self.vessel_slider.value() / 100)
        self.vtk_view4.GetRenderWindow().Render()

    def _skeleton_seg(self):
        """槽函数:骨骼分割"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("是否导入骨骼掩膜？")
        import_btn = mb.addButton("导入", QMessageBox.AcceptRole)
        auto_btn = mb.addButton("自动分割", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        # 判断返回结果处理相应事项
        if mb.clickedButton() == import_btn:
            self.skeleton_mask_path, _type = QFileDialog.getOpenFileNames(
                self, "请导入骨骼掩膜", self.cwd, "nii Files (*.nii.gz)")
            if self.skeleton_mask_path == []:  # 没选择时返回
                return
            
            self.skeleton_seg_btn.setEnabled(False)
            self.info_list[2] = "正在进行骨骼分割..."
            self.info.setText("  ".join(self.info_list))
            self.skeleton_mask_path = self.skeleton_mask_path[0]
            self._skeleton_rebuild(self.skeleton_mask_path)

        elif mb.clickedButton() == auto_btn:
            self.skeleton_seg_btn.setEnabled(False)
            self.info_list[2] = "正在进行骨骼分割..."
            self.info.setText("  ".join(self.info_list))

            self.skeleton_mask_path = os.path.join(self.cwd, 'result', 'skeleton_mask.nii.gz')

            self.skeleton_seg_thread = SkeletonSegThread(self.ct_nii_path, self.skeleton_mask_path)
            self.skeleton_seg_thread.finish_signal.connect(self._skeleton_rebuild)
            self.skeleton_seg_thread.start()

        else:
            return

    def _skeleton_rebuild(self, skeleton_mask_path):
        """槽函数:骨骼重建"""
        
        if hasattr(self, 'skeleton_actor'):
            self.view4_renderer.RemoveActor(self.skeleton_actor)  # 删除上次保留的_skeleton_actor

        self.skeleton_actor = vtk.vtkActor()
        self.skeleton_polydata = self._rebuild(self.skeleton_mask_path, self.skeleton_actor, self.view4_renderer, [0.3, 0.5, 0.5])
        if self.skeleton_polydata  == False:
            del self.skeleton_actor
            self.skeleton_seg_btn.setEnabled(True)
            self.info_list[2] = ""
            self.info.setText("  ".join(self.info_list))
            return
        self.Po_list.append(self.skeleton_polydata)

        self.skeleton_slider.valueChanged.connect(self._set_skeleton_opacity)
        self.skeleton_slider.setValue(100)

        self.skeleton_seg_btn.setEnabled(True)
        self.info_list[2] = "骨骼分割完成！"
        self.info.setText("  ".join(self.info_list))

    def _set_skeleton_opacity(self):
        """槽函数:调整骨骼透明度"""

        self.skeleton_actor.GetProperty().SetOpacity(self.skeleton_slider.value() / 100)
        self.vtk_view4.GetRenderWindow().Render()

    def _tumor_seg(self):
        """槽函数:肿瘤分割"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("是否导入肿瘤掩膜？")
        import_btn = mb.addButton("导入", QMessageBox.AcceptRole)
        auto_btn = mb.addButton("自动分割", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        # 判断返回结果处理相应事项
        if mb.clickedButton() == import_btn:
            self.tumor_mask_path, _type = QFileDialog.getOpenFileNames(
                self, "请导入肿瘤掩膜", self.cwd, "nii Files (*.nii.gz)")
            if self.tumor_mask_path == []:  # 没选择时返回
                return
            
            self.tumor_seg_btn.setEnabled(False)
            self.info_list[3] = "正在进行肿瘤分割..."
            self.info.setText("  ".join(self.info_list))
            self.tumor_mask_path = self.tumor_mask_path[0]
            self._tumor_rebuild(self.tumor_mask_path)

        elif mb.clickedButton() == auto_btn:
            self.tumor_seg_btn.setEnabled(False)
            self.info_list[3] = "正在进行肿瘤分割..."
            self.info.setText("  ".join(self.info_list))
            self.tumor_mask_dir = os.path.join(self.cwd, "result", "tumor")
            os.makedirs(self.tumor_mask_dir, exist_ok=True)

            model_folder_name = os.path.join(self.cwd,"nnUNet", "nnUNet_trained_models", "nnUNet", "3d_fullres", "Task006_Lung", "nnUNetTrainerV2__nnUNetPlansv2.1")
            input_folder = os.path.join(self.cwd, "mid_result")
            # input_folder= 'mid_result'
            output_folder = self.tumor_mask_dir
            folds = 0
            save_npz = None
            num_threads_preprocessing = 6
            num_threads_nifti_save = 2
            lowres_segmentations = None
            part_id = 0
            num_parts = 1
            disable_tta = True
            overwrite_existing = False
            mode = "normal"
            all_in_gpu = False
            disable_mixed_precision = False
            step_size = 0.5
            chk = "model_final_checkpoint"

            predict_from_folder(model_folder_name, input_folder, output_folder, folds, save_npz, num_threads_preprocessing,
                    num_threads_nifti_save, lowres_segmentations, part_id, num_parts, not disable_tta,
                    overwrite_existing=overwrite_existing, mode=mode, overwrite_all_in_gpu=all_in_gpu,
                    mixed_precision=not disable_mixed_precision,
                    step_size=step_size, checkpoint_name=chk)
            
            tumor_file_name = os.listdir(self.tumor_mask_dir)[0]
            self.tumor_mask_path = os.path.join(self.tumor_mask_dir, tumor_file_name)
            self._tumor_rebuild(self.tumor_mask_path)
            # return

        else:
            return

    def _tumor_rebuild(self, tumor_mask_path):
        """槽函数:肿瘤重建"""

        if hasattr(self, 'tumor_actor'):
            self.view4_renderer.RemoveActor(self.tumor_actor)  # 删除上次保留的_tumor_actor
            self._delete_slice_mask()  # 删除上次保留的肿瘤三视图掩膜

        self.tumor_actor = vtk.vtkActor()
        self.tumor_polydata = self._rebuild(self.tumor_mask_path, self.tumor_actor, self.view4_renderer, [1.0, 0.0, 0.0])
        if self.tumor_polydata == False:
            del self.tumor_actor
            self.tumor_seg_btn.setEnabled(True)
            self.info_list[3] = ""
            self.info.setText("  ".join(self.info_list))
            return
        
        self.tumor_slider.valueChanged.connect(self._set_tumor_opacity)
        self.tumor_slider.setValue(100)

        # 三视图肿瘤掩膜
        self.tumor_reader = vtk.vtkNIFTIImageReader()
        self.tumor_reader.SetFileName(self.tumor_mask_path)
        self.tumor_reader.Update()

        color_table = vtk.vtkLookupTable()
        color_table.SetNumberOfColors(2)
        color_table.SetTableRange(0, 1)
        color_table.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)
        color_table.SetTableValue(1, 1, 0, 0, 1.0)
        color_table.Build()

        # view1_slicer
        self.view1_tumor_reslice = vtk.vtkImageReslice()
        self.view1_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view1_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view1_tumor_reslice.SetResliceAxes(self.view1_reslice_axes)  # 设置矩阵
        self.view1_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view1_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view1_tumor_mapper = vtk.vtkImageMapToColors()
        self.view1_tumor_mapper.SetLookupTable(color_table)
        self.view1_tumor_mapper.SetInputConnection(self.view1_tumor_reslice.GetOutputPort())  # 设置图像数据


        self.view1_tumor_reslice_actor = vtk.vtkImageActor()
        self.view1_tumor_reslice_actor.GetMapper().SetInputConnection(self.view1_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view1_slice_renderer.AddActor(self.view1_tumor_reslice_actor)  # 添加切片actor

        # view2_slicer
        self.view2_tumor_reslice = vtk.vtkImageReslice()
        self.view2_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view2_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view2_tumor_reslice.SetResliceAxes(self.view2_reslice_axes)  # 设置矩阵
        self.view2_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view2_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view2_tumor_mapper = vtk.vtkImageMapToColors()
        self.view2_tumor_mapper.SetLookupTable(color_table)
        self.view2_tumor_mapper.SetInputConnection(self.view2_tumor_reslice.GetOutputPort())  # 设置图像数据


        self.view2_tumor_reslice_actor = vtk.vtkImageActor()
        self.view2_tumor_reslice_actor.GetMapper().SetInputConnection(self.view2_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view2_slice_renderer.AddActor(self.view2_tumor_reslice_actor)  # 添加切片actor

        # view3_slicer
        self.view3_tumor_reslice = vtk.vtkImageReslice()
        self.view3_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view3_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view3_tumor_reslice.SetResliceAxes(self.view3_reslice_axes)  # 设置矩阵
        self.view3_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view3_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view3_tumor_mapper = vtk.vtkImageMapToColors()
        self.view3_tumor_mapper.SetLookupTable(color_table)
        self.view3_tumor_mapper.SetInputConnection(self.view3_tumor_reslice.GetOutputPort())  # 设置图像数据


        self._view3_tumor_reslice_actor = vtk.vtkImageActor()
        self._view3_tumor_reslice_actor.GetMapper().SetInputConnection(self.view3_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view3_slice_renderer.AddActor(self._view3_tumor_reslice_actor)  # 添加切片actor

        self.vtk_view1.GetRenderWindow().Render()  # 刷新窗口
        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()
        self.vtk_view4.GetRenderWindow().Render()

        self.tumor_seg_btn.setEnabled(True)
        self.info_list[3] = "肿瘤分割完成！"
        self.info.setText("  ".join(self.info_list))

    def _set_tumor_opacity(self):
        """槽函数:调整肿瘤透明度"""

        self.tumor_actor.GetProperty().SetOpacity(self.tumor_slider.value() / 100)
        self.vtk_view4.GetRenderWindow().Render()

    # def _set_dilate_tumor_opacity(self):
    #     """槽函数:调整肿瘤(+安全边界)透明度"""

    #     if hasattr(self, "dilate_tumor_actor"):
    #         self.dilate_tumor_actor.GetProperty().SetOpacity(self.dilate_tumor_slider.value() / 100)
    #         self.vtk_view4.GetRenderWindow().Render()

    def _delete_view123(self):
        """删除view1,2,3"""
        
        if hasattr(self, "view1_cross_renderer"):
             self.vtk_view1.GetRenderWindow().RemoveRenderer(self.view1_cross_renderer)
        if hasattr(self, "view2_cross_renderer"):
             self.vtk_view2.GetRenderWindow().RemoveRenderer(self.view2_cross_renderer)
        if hasattr(self, "view3_cross_renderer"):
             self.vtk_view3.GetRenderWindow().RemoveRenderer(self.view3_cross_renderer)

        if hasattr(self, "view1_slice_renderer"):
             self.vtk_view1.GetRenderWindow().RemoveRenderer(self.view1_slice_renderer)
        if hasattr(self, "view2_slice_renderer"):
             self.vtk_view2.GetRenderWindow().RemoveRenderer(self.view2_slice_renderer)
        if hasattr(self, "view3_slice_renderer"):
             self.vtk_view3.GetRenderWindow().RemoveRenderer(self.view3_slice_renderer)
        
    def _delete_slice_mask(self):
        """删除三视图中的肿瘤掩膜"""

        if hasattr(self, 'view1_tumor_reslice_actor'):
            self.view1_slice_renderer.RemoveActor(self.view1_tumor_reslice_actor)
        if hasattr(self, 'view2_tumor_reslice_actor'):
            self.view2_slice_renderer.RemoveActor(self.view2_tumor_reslice_actor)
        if hasattr(self, '_view3_tumor_reslice_actor'):
            self.view3_slice_renderer.RemoveActor(self._view3_tumor_reslice_actor)

        self.vtk_view4.GetRenderWindow().Render()

    def _rebuild(self, mask_path, actor, renderer, color):
        """模型重建"""

        error_tag, nii_reader_output = vtk_nii_reader(mask_path)
        # 判断是否发生错误
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(nii_reader_output)
            error_message.exec_()
            return False
        else:
            # 判断掩膜最大值是否为1
            accumulator = vtk.vtkImageAccumulate()
            accumulator.SetInputData(nii_reader_output)
            accumulator.Update()

            max_value = accumulator.GetMax()[0]
            if max_value != 1:
                QtWidgets.QMessageBox.warning(self, '警告', '请检查掩膜的值是否为1', QtWidgets.QMessageBox.Yes)
                return False

            # 利用封装好的MC算法抽取等值面，对应filter
            mc = vtk.vtkDiscreteMarchingCubes()
            mc.SetInputData(nii_reader_output)
            mc.SetValue(0, 1)
            mc.Update()

            # 剔除旧的或废除的数据单元，提高绘制速度，对应filter
            stripper = vtk.vtkStripper()
            stripper.SetInputConnection(mc.GetOutputPort())
            stripper.Update()

            # 对三维模型表面进行平滑,对应smoother
            smoothing_iterations = 15
            pass_band = 0.001
            feature_angle = 120.0
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            smoother.SetInputConnection(stripper.GetOutputPort())
            smoother.SetNumberOfIterations(smoothing_iterations)
            smoother.BoundarySmoothingOff()
            smoother.FeatureEdgeSmoothingOff()
            smoother.SetFeatureAngle(feature_angle)
            smoother.SetPassBand(pass_band)
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.Update()

            fillholes_filter = vtk.vtkFillHolesFilter()
            fillholes_filter.SetInputData(smoother.GetOutput())
            fillholes_filter.SetHoleSize(100.0)
            fillholes_filter.Update()

            triangle_filter = vtk.vtkTriangleFilter()
            triangle_filter.SetInputConnection(fillholes_filter.GetOutputPort())
            triangle_filter.Update()

            # Make the triangle windong order consistent
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputConnection(triangle_filter.GetOutputPort())
            normals.ConsistencyOn()
            normals.SplittingOff()
            normals.Update()

            # Set up the actor to display the transformed polydata
            transformed_mapper = vtk.vtkPolyDataMapper()
            transformed_mapper.SetInputConnection(normals.GetOutputPort())

            actor.SetMapper(transformed_mapper)

            # 角色的颜色设置
            actor.GetProperty().SetDiffuseColor(color[0], color[1], color[2])
            # 设置高光照明系数
            actor.GetProperty().SetSpecular(.1)
            # 设置高光能量
            actor.GetProperty().SetSpecularPower(100)

            renderer.AddActor(actor)
            renderer.ResetCamera()

            return mc.GetOutput()
    
    def _auto_path_plan(self):
        """自动路径规划"""

        if not hasattr(self, 'lung_actor') and not hasattr(self, 'trachea_actor') and not hasattr(self, 'vessel_actor') and not hasattr(self, 'skeleton_actor') and not hasattr(self, 'tumor_actor'):
            QtWidgets.QMessageBox.warning(self, '警告', '请先进行分割', QtWidgets.QMessageBox.Yes)
            return
        
        self.auto_path_btn.setEnabled(False)
        self.info_list[4] = "正在进行路径规划..."
        self.info.setText("  ".join(self.info_list))
        if self.large_checkbox.isChecked():
            self.auto_path_thread = LargeAutoPathPlanThread(self)
            self.auto_path_thread.finish_signal.connect(self._large_auto_path_thread_end)
        else:
            self.auto_path_thread = AutoPathPlanThread(self)
            self.auto_path_thread.finish_signal.connect(self._auto_path_thread_end)
        self.auto_path_thread.start()

    def _normalize_vector(self, v):
        length = np.linalg.norm(v)  # 计算向量的长度
        if length == 0:
            return v  # 如果向量长度为0，则返回原向量
        else:
            return v / length  # 返回单位向量

    def _auto_path_thread_end(self, signal_list):

        if not signal_list[0]:
            error_prompt = signal_list[1]
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(error_prompt)
            error_message.exec_()
            self.auto_path_btn.setEnabled(True)
            self.info_list[4] = ""
            self.info.setText("  ".join(self.info_list))
            return
        else:
            self.needles_num = signal_list[1]
            self.entry_point_list = signal_list[2]
            self.pt_centers = signal_list[3]
            self.pt_radius = signal_list[4]
            self.iou_list = signal_list[5]
            self.ac_all = signal_list[6]
            self.oa_all = signal_list[7]
            self.ablate_list = signal_list[8]
            self.dilate_tumor_mask_path = signal_list[9]

            view4_all_actors = self.view4_renderer.GetActors()
            for view4_actor in view4_all_actors:
                if view4_actor != self.lung_actor and view4_actor != self.trachea_actor and view4_actor != self.vessel_actor and view4_actor != self.tumor_actor and view4_actor != self.skeleton_actor:
                      self.view4_renderer.RemoveActor(view4_actor)

            # 可视化
            self.dilate_tumor_actor = vtk.vtkActor()
            self.dilate_tumor_mapper = vtk.vtkDataSetMapper()
            self.dilate_tumor_polydata = self._rebuild(self.dilate_tumor_mask_path, self.dilate_tumor_actor, self.view4_renderer, [0.2, 0.8, 0.0])
            self.dilate_tumor_actor.GetProperty().SetOpacity(0.5)
            # self.dilate_tumor_slider.valueChanged.connect(self._set_dilate_tumor_opacity)
            self.tumor_slider.setValue(20)

            new_center_list = []
            for i in range(self.needles_num):
                path_actor = vtk.vtkActor()
                path_source = vtk.vtkLineSource()

                vector = np.array(self.pt_centers[i]-self.entry_point_list[i])
                vertor_norm = self._normalize_vector(vector)
                new_center = np.array(self.pt_centers[i]) + vertor_norm*6
                new_center_list.append(new_center)

                path_source.SetPoint1(self.entry_point_list[i][0])
                path_source.SetPoint2(new_center[0])

                path_source.Update()

                path_mapper = vtk.vtkDataSetMapper()
                path_mapper.SetInputConnection(path_source.GetOutputPort())

                path_actor.SetMapper(path_mapper)
                path_actor.GetProperty().SetColor(1.0, 1.0, 1.0)

                ablate_actor = vtk.vtkActor()
                ablate_mapper = vtk.vtkDataSetMapper()
                ablate_mapper.SetInputData(self.ablate_list[i])
                ablate_actor.SetMapper(ablate_mapper)
                ablate_actor.GetProperty().SetColor(0.0, 1.0, 0.0)
                ablate_actor.GetProperty().SetOpacity(0.2)

                self.view4_renderer.AddActor(path_actor)
                self.view4_renderer.AddActor(ablate_actor)
                self.vtk_view4.GetRenderWindow().Render()

            # 输出结果
            result = "针数："+str(self.needles_num)+"\n\n"
            for i in range(self.needles_num):
                # self.pt_long_diameter, (self.power, self.time) = solve_equation(self.pt_radius[i]*2)
                
                # 计算进针深度
                needle_depth = np.linalg.norm(self.entry_point_list[i]-np.array(new_center_list[i]))
                result_i = "第"+str(i+1)+"针："+"\n"+\
                        "进针点："+str(self.entry_point_list[i])+"\n"+\
                        "肿瘤靶向点："+str(new_center_list[i])+"\n"+\
                        "进针深度："+str(needle_depth)+"mm\n"+\
                        "消融短径："+str(self.pt_radius[i]*2)+"\n"+\
                        "消融长径："+str(self.pt_radius[i]*2*1.2)+"\n"+\
                        "AC："+str(self.iou_list[i][0])+"\n"+\
                        "OA："+str(self.iou_list[i][1])+"\n\n"
                result += result_i
            result += "=======消融效果======="+"\n"+\
                    "AC："+str(self.ac_all)+"\n"+\
                    "OA："+str(self.oa_all)+"\n\n"

            self.auto_path_result_edit.setText(result)
            print("靶向点集：", self.pt_centers)
            print("进针点集：", self.entry_point_list)
            print("消融半径：", self.pt_radius)

            self.auto_path_btn.setEnabled(True)
            self.info_list[4] = "路径规划完成！"
            self.info.setText("  ".join(self.info_list))

    def _large_auto_path_thread_end(self, signal_list):

        if not signal_list[0]:
            error_prompt = signal_list[1]
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(error_prompt)
            error_message.exec_()
            self.auto_path_btn.setEnabled(True)
            self.info_list[4] = ""
            self.info.setText("  ".join(self.info_list))
            return
        else:
            self.needles_num = signal_list[1]
            self.entry_point_list = signal_list[2]
            self.pt_centers = signal_list[3]
            self.pt_radius = signal_list[4]
            self.iou_list = signal_list[5]
            self.ac_all = signal_list[6]
            self.oa_all = signal_list[7]
            self.ablate_list = signal_list[8]

            print("靶向点集：", self.pt_centers)
            print("进针点集：", self.entry_point_list)
            print("消融半径：", self.pt_radius)

            view4_all_actors = self.view4_renderer.GetActors()
            for view4_actor in view4_all_actors:
                if view4_actor != self.lung_actor and view4_actor != self.trachea_actor and view4_actor != self.vessel_actor and view4_actor != self.tumor_actor and view4_actor != self.skeleton_actor:
                      self.view4_renderer.RemoveActor(view4_actor)

            # 可视化
            # self.dilate_tumor_actor = vtk.vtkActor()
            # self.dilate_tumor_mapper = vtk.vtkDataSetMapper()
            # self.dilate_tumor_polydata = self._rebuild(self.dilate_tumor_mask_path, self.dilate_tumor_actor, self.view4_renderer, [0.2, 0.8, 0.0])
            # self.dilate_tumor_actor.GetProperty().SetOpacity(0.5)
            # # self.dilate_tumor_slider.valueChanged.connect(self._set_dilate_tumor_opacity)
            # self.tumor_slider.setValue(20)
            new_center_list = []
            for i in range(self.needles_num):
                path_actor = vtk.vtkActor()
                path_source = vtk.vtkLineSource()
                vector = np.array(self.pt_centers[i]-self.entry_point_list[i])
                vertor_norm = self._normalize_vector(vector)
                new_center = np.array(self.pt_centers[i]) + vertor_norm*8
                new_center_list.append(new_center)

                path_source.SetPoint1(self.entry_point_list[i][0])
                path_source.SetPoint2(new_center[0])
                path_source.Update()

                path_mapper = vtk.vtkDataSetMapper()
                path_mapper.SetInputConnection(path_source.GetOutputPort())

                path_actor.SetMapper(path_mapper)
                path_actor.GetProperty().SetColor(1.0, 1.0, 1.0)

                ablate_actor = vtk.vtkActor()
                ablate_mapper = vtk.vtkDataSetMapper()
                ablate_mapper.SetInputData(self.ablate_list[i])
                ablate_actor.SetMapper(ablate_mapper)
                ablate_actor.GetProperty().SetColor(0.0, 1.0, 0.0)
                ablate_actor.GetProperty().SetOpacity(0.2)

                self.view4_renderer.AddActor(path_actor)
                self.view4_renderer.AddActor(ablate_actor)
                self.vtk_view4.GetRenderWindow().Render()


            # 输出结果
            result = "针数："+str(self.needles_num)+"\n\n"
            for i in range(self.needles_num):
                # self.power, self.time = solve_equation_v2(self.pt_radius[i]*2, self.pt_radius[i]*2/1.5)
                
                # 计算进针深度
                needle_depth = np.linalg.norm(self.entry_point_list[i]-np.array(new_center_list[i]))
                result_i = "第"+str(i+1)+"针："+"\n"+\
                        "进针点："+str(self.entry_point_list[i])+"\n"+\
                        "肿瘤靶向点："+str(self.pt_centers[i])+"\n"+\
                        "进针深度："+str(needle_depth)+"mm\n"+\
                        "消融短径："+str(self.pt_radius[i]*2/1.2)+"\n"+\
                        "消融长径："+str(self.pt_radius[i]*2)+"\n"+\
                        "AC："+str(self.iou_list[i][0])+"\n"+\
                        "OA："+str(self.iou_list[i][1])+"\n\n"
                result += result_i
            result += "=======消融效果======="+"\n"+\
                    "AC："+str(self.ac_all)+"\n"+\
                    "OA："+str(self.oa_all)+"\n\n"

            self.auto_path_result_edit.setText(result)

            self.auto_path_btn.setEnabled(True)
            self.info_list[4] = "路径规划完成！"
            self.info.setText("  ".join(self.info_list))

    def _post_eval(self):
        """槽函数:术后评估"""

        mb = QMessageBox(self)
        mb.setWindowTitle("消息提示")
        mb.setInformativeText("是否进行术后评估？")
        accept_btn = mb.addButton("确定", QMessageBox.AcceptRole)
        mb.setStandardButtons(QMessageBox.Cancel)
        mb.setDefaultButton(QMessageBox.Cancel)
        mb.exec()

        if mb.clickedButton() == accept_btn:
            self.tumor_seg_btn.setEnabled(False)
            self.info_list[5] = "正在进行术后评估..."
            self.info.setText("  ".join(self.info_list))
            self.tumor_post_mask_dir = os.path.join(self.cwd, "result", "tumor_post")
            os.makedirs(self.tumor_post_mask_dir, exist_ok=True)

            model_folder_name = os.path.join(self.cwd,"nnUNet", "nnUNet_trained_models", "nnUNet", "3d_fullres", "Task006_Lung", "nnUNetTrainerV2__nnUNetPlansv2.1")
            input_folder = os.path.join(self.cwd, "mid_result")
            # input_folder= 'mid_result'
            output_folder = self.tumor_post_mask_dir
            folds = 0
            save_npz = None
            num_threads_preprocessing = 6
            num_threads_nifti_save = 2
            lowres_segmentations = None
            part_id = 0
            num_parts = 1
            disable_tta = True
            overwrite_existing = False
            mode = "normal"
            all_in_gpu = False
            disable_mixed_precision = False
            step_size = 0.5
            chk = "model_final_checkpoint"

            predict_from_folder(model_folder_name, input_folder, output_folder, folds, save_npz, num_threads_preprocessing,
                    num_threads_nifti_save, lowres_segmentations, part_id, num_parts, not disable_tta,
                    overwrite_existing=overwrite_existing, mode=mode, overwrite_all_in_gpu=all_in_gpu,
                    mixed_precision=not disable_mixed_precision,
                    step_size=step_size, checkpoint_name=chk)
            
            tumor_file_name = os.listdir(self.tumor_post_mask_dir)[0]
            tumor_post_mask_path = os.path.join(self.tumor_post_mask_dir, tumor_file_name)
            tumor_post_mask = sitk.ReadImage(tumor_post_mask_path)
            tumor_post_array = sitk.GetArrayFromImage(tumor_post_mask)
            if np.max(tumor_post_array) > 0:
                self.eval_result_edit.setText("有病灶残留！")
                self._tumor_post_rebuild(tumor_post_mask_path)
            else:
                self.eval_result_edit.setText("消融完全！")
            self.info_list[5] = "术后评估完成！"
            self.info.setText("  ".join(self.info_list))
            self.tumor_seg_btn.setEnabled(True)
        else:
            return

    def _tumor_post_rebuild(self, tumor_post_mask_path):
        """槽函数:肿瘤重建"""

        if hasattr(self, 'tumor_actor'):
            self.view4_renderer.RemoveActor(self.tumor_actor)  # 删除上次保留的_tumor_actor
            self._delete_slice_mask()  # 删除上次保留的肿瘤三视图掩膜

        self.tumor_actor = vtk.vtkActor()
        self.tumor_polydata = self._rebuild(tumor_post_mask_path, self.tumor_actor, self.view4_renderer, [1.0, 0.0, 0.0])
        if self.tumor_polydata == False:
            del self.tumor_actor
            self.info_list[5] = ""
            self.info.setText("  ".join(self.info_list))
            return
        
        self.tumor_slider.valueChanged.connect(self._set_tumor_opacity)
        self.tumor_slider.setValue(100)

        # 三视图肿瘤掩膜
        self.tumor_reader = vtk.vtkNIFTIImageReader()
        self.tumor_reader.SetFileName(tumor_post_mask_path)
        self.tumor_reader.Update()

        color_table = vtk.vtkLookupTable()
        color_table.SetNumberOfColors(2)
        color_table.SetTableRange(0, 1)
        color_table.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)
        color_table.SetTableValue(1, 1, 0, 0, 1.0)
        color_table.Build()

        # view1_slicer
        self.view1_tumor_reslice = vtk.vtkImageReslice()
        self.view1_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view1_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view1_tumor_reslice.SetResliceAxes(self.view1_reslice_axes)  # 设置矩阵
        self.view1_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view1_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view1_tumor_mapper = vtk.vtkImageMapToColors()
        self.view1_tumor_mapper.SetLookupTable(color_table)
        self.view1_tumor_mapper.SetInputConnection(self.view1_tumor_reslice.GetOutputPort())  # 设置图像数据


        self.view1_tumor_reslice_actor = vtk.vtkImageActor()
        self.view1_tumor_reslice_actor.GetMapper().SetInputConnection(self.view1_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view1_slice_renderer.AddActor(self.view1_tumor_reslice_actor)  # 添加切片actor

        # view2_slicer
        self.view2_tumor_reslice = vtk.vtkImageReslice()
        self.view2_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view2_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view2_tumor_reslice.SetResliceAxes(self.view2_reslice_axes)  # 设置矩阵
        self.view2_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view2_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view2_tumor_mapper = vtk.vtkImageMapToColors()
        self.view2_tumor_mapper.SetLookupTable(color_table)
        self.view2_tumor_mapper.SetInputConnection(self.view2_tumor_reslice.GetOutputPort())  # 设置图像数据


        self.view2_tumor_reslice_actor = vtk.vtkImageActor()
        self.view2_tumor_reslice_actor.GetMapper().SetInputConnection(self.view2_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view2_slice_renderer.AddActor(self.view2_tumor_reslice_actor)  # 添加切片actor

        # view3_slicer
        self.view3_tumor_reslice = vtk.vtkImageReslice()
        self.view3_tumor_reslice.SetInputConnection(self.tumor_reader.GetOutputPort())  # 设置数据输入源
        self.view3_tumor_reslice.SetOutputDimensionality(2)  # 设置输出为一个切片
        self.view3_tumor_reslice.SetResliceAxes(self.view3_reslice_axes)  # 设置矩阵
        self.view3_tumor_reslice.SetInterpolationModeToLinear()  # 设置切面算法的插值方式线性插值

        self.view3_tumor_reslice.SetResliceAxesOrigin(self.center_world[0],
                                                      self.center_world[1],
                                                      self.center_world[2])  # 设置切片中心点

        self.view3_tumor_mapper = vtk.vtkImageMapToColors()
        self.view3_tumor_mapper.SetLookupTable(color_table)
        self.view3_tumor_mapper.SetInputConnection(self.view3_tumor_reslice.GetOutputPort())  # 设置图像数据


        self._view3_tumor_reslice_actor = vtk.vtkImageActor()
        self._view3_tumor_reslice_actor.GetMapper().SetInputConnection(self.view3_tumor_mapper.GetOutputPort())  # 添加映射器
        self.view3_slice_renderer.AddActor(self._view3_tumor_reslice_actor)  # 添加切片actor

        self.vtk_view1.GetRenderWindow().Render()  # 刷新窗口
        self.vtk_view2.GetRenderWindow().Render()
        self.vtk_view3.GetRenderWindow().Render()
        self.vtk_view4.GetRenderWindow().Render()

    def _tumor_eval(self):
        label1_path, _type = QFileDialog.getOpenFileNames(
                self, "请选择术前肿瘤掩膜", self.cwd, "nii Files (*.nii.gz)")
        if label1_path == []:  # 没选择时返回
            return
        label1_path = label1_path[0]  # 取路径

        label2_path, _type = QFileDialog.getOpenFileNames(
            self, "请选择术后肿瘤掩膜", self.cwd, "nii Files (*.nii.gz)")

        if label2_path == []:  # 没选择时返回
            return

        label2_path = label2_path[0]

        tumor_eval_result = eval_tumor_efficacy(label1_path, label2_path)
        self.message_edit_2.setText(tumor_eval_result)