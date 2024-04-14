import vtk
import os
from PyQt5.QtWidgets import QMessageBox

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from src.seg import LungTracheaSegThread

class MouseInteractorStyle1(vtkInteractorStyleTrackballCamera):
    """view1鼠标交互"""

    def __init__(self, extent, spacing, main_win):
        """初始化"""

        self.extent = extent
        self.spacing = spacing
        self.main_win = main_win
        self.lbtn_press_flag = False

        self.AddObserver('LeftButtonPressEvent', self._left_btn_press_event)
        self.AddObserver("MouseMoveEvent", self._mouse_move_event)
        self.AddObserver("LeftButtonReleaseEvent", self._left_btn_release_event)
        self.AddObserver("MouseWheelForwardEvent", self._mouse_wheel_forward)
        self.AddObserver("MouseWheelBackwardEvent", self._mouse_wheel_backward)

    def _left_btn_press_event(self, obj, event):
        """鼠标左键按下触发事件"""

        self.lbtn_press_flag = True
        self._mpr_change()

    def _mouse_move_event(self, obj, event):
        """鼠标移动触发事件"""

        if self.lbtn_press_flag:
            self._mpr_change()

    def _left_btn_release_event(self, obj, event):
        """鼠标左键松开触发事件"""

        self.lbtn_press_flag = False

    def _mpr_change(self):
        """view1视图改变"""

        pos = self.GetInteractor().GetEventPosition()  # Get the location of the click (in window coordinates)

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())  # Pick from this location.

        world_position = picker.GetPickPosition()

        if picker.GetCellId() != -1:
            real_position = [
                world_position[0] / self.spacing[0] + 0.5 * self.extent[1],
                0.5 * self.extent[3] - world_position[1] / self.spacing[1]
            ]
            self.main_win.view2_scrollbar.setValue(real_position[0])
            self.main_win.view3_scrollbar.setValue(real_position[1])
        else:
            if world_position[0] < -0.5 * self.spacing[0] * self.extent[1]:
                self.main_win.view2_scrollbar.setValue(0)
            if world_position[0] > 0.5 * self.spacing[0] * self.extent[1]:
                self.main_win.view2_scrollbar.setValue(self.extent[1])

            if world_position[1] < -0.5 * self.spacing[1] * self.extent[3]:
                self.main_win.view3_scrollbar.setValue(self.extent[3])
            if world_position[1] > 0.5 * self.spacing[1] * self.extent[3]:
                self.main_win.view3_scrollbar.setValue(0)

    def _mouse_wheel_forward(self, obj, event):
        self.OnLeftButtonUp()

    def _mouse_wheel_backward(self, obj, event):
        self.OnLeftButtonDown()

class MouseInteractorStyle2(vtkInteractorStyleTrackballCamera):
    """view2鼠标交互"""

    def __init__(self, extent, spacing, main_win):
        """初始化"""

        self.extent = extent
        self.spacing = spacing
        self.main_win = main_win
        self.lbtn_press_flag = False

        self.AddObserver('LeftButtonPressEvent', self._left_btn_press_event)
        self.AddObserver("MouseMoveEvent", self._mouse_move_event)
        self.AddObserver("LeftButtonReleaseEvent", self._left_btn_release_event)
        self.AddObserver("MouseWheelForwardEvent", self._mouse_wheel_forward)
        self.AddObserver("MouseWheelBackwardEvent", self._mouse_wheel_backward)

    def _left_btn_press_event(self, obj, event):
        """鼠标左键按下触发事件"""

        self.lbtn_press_flag = True
        self._mpr_change()

    def _mouse_move_event(self, obj, event):
        """鼠标移动触发事件"""

        if self.lbtn_press_flag:
            self._mpr_change()

    def _left_btn_release_event(self, obj, event):
        """鼠标左键松开触发事件"""

        self.lbtn_press_flag = False

    def _mpr_change(self):
        """view2视图改变"""

        pos = self.GetInteractor().GetEventPosition()  # Get the location of the click (in window coordinates)

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())  # Pick from this location.

        world_position = picker.GetPickPosition()

        if picker.GetCellId() != -1:
            real_position = [
                world_position[0] / self.spacing[1] + 0.5 * self.extent[3],
                world_position[1] / self.spacing[2] + 0.5 * self.extent[5]
            ]

            self.main_win.view3_scrollbar.setValue(real_position[0])
            self.main_win.view1_scrollbar.setValue(real_position[1])
        else:
            if world_position[0] < -0.5 * self.spacing[1] * self.extent[3]:
                self.main_win.view3_scrollbar.setValue(0)
            if world_position[0] > 0.5 * self.spacing[1] * self.extent[3]:
                self.main_win.view3_scrollbar.setValue(self.extent[3])

            if world_position[1] < -0.5 * self.spacing[2] * self.extent[5]:
                self.main_win.view1_scrollbar.setValue(0)
            if world_position[1] > 0.5 * self.spacing[2] * self.extent[5]:
                self.main_win.view1_scrollbar.setValue(self.extent[5])

    def _mouse_wheel_forward(self, obj, event):
        self.OnLeftButtonUp()

    def _mouse_wheel_backward(self, obj, event):
        self.OnLeftButtonDown()

class MouseInteractorStyle3(vtkInteractorStyleTrackballCamera):
    """view3鼠标交互"""

    def __init__(self, extent, spacing, main_win):
        """初始化"""

        self.extent = extent
        self.spacing = spacing
        self.main_win = main_win
        self.lbtn_press_flag = False
        self.seed_flag = False

        self.AddObserver('LeftButtonPressEvent', self._left_btn_press_event)
        self.AddObserver("MouseMoveEvent", self._mouse_move_event)
        self.AddObserver("LeftButtonReleaseEvent", self._left_btn_release_event)
        self.AddObserver("MouseWheelForwardEvent", self._mouse_wheel_forward)
        self.AddObserver("MouseWheelBackwardEvent", self._mouse_wheel_backward)

    def _left_btn_press_event(self, obj, event):
        """鼠标左键按下触发事件"""

        if not self.seed_flag:
            self.lbtn_press_flag = True
            self._mpr_change()
        else:
            self._lung_trachea_seg()

    def _mouse_move_event(self, obj, event):
        """鼠标移动触发事件"""

        if self.lbtn_press_flag:
            self._mpr_change()

    def _left_btn_release_event(self, obj, event):
        """鼠标左键松开触发事件"""

        self.lbtn_press_flag = False

    def _mpr_change(self):
        """view3视图改变"""

        pos = self.GetInteractor().GetEventPosition()  # Get the location of the click (in window coordinates)

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())  # Pick from this location.

        world_position = picker.GetPickPosition()

        if picker.GetCellId() != -1:
            real_position = [
                world_position[0] / self.spacing[0] + 0.5 * self.extent[1],
                world_position[1] / self.spacing[2] + 0.5 * self.extent[5]
            ]

            self.main_win.view2_scrollbar.setValue(real_position[0])
            self.main_win.view1_scrollbar.setValue(real_position[1])
        else:
            if world_position[0] < -0.5 * self.spacing[0] * self.extent[1]:
                self.main_win.view2_scrollbar.setValue(0)
            if world_position[0] > 0.5 * self.spacing[0] * self.extent[1]:
                self.main_win.view2_scrollbar.setValue(self.extent[3])

            if world_position[1] < -0.5 * self.spacing[2] * self.extent[5]:
                self.main_win.view1_scrollbar.setValue(0)
            if world_position[1] > 0.5 * self.spacing[2] * self.extent[5]:
                self.main_win.view1_scrollbar.setValue(self.extent[5])

    def _lung_trachea_seg(self):
        pos = self.GetInteractor().GetEventPosition()  # Get the location of the click (in window coordinates)

        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())  # Pick from this location.

        world_position = picker.GetPickPosition()

        if picker.GetCellId() != -1:
            real_position = [
                world_position[0] / self.spacing[0] + 0.5 * self.extent[1],
                world_position[1] / self.spacing[2] + 0.5 * self.extent[5]
            ]

            self.main_win.view2_scrollbar.setValue(real_position[0])
            self.main_win.view1_scrollbar.setValue(real_position[1])
            
            mb = QMessageBox(self.main_win)
            mb.setWindowTitle("消息提示")
            mb.setInformativeText("确定选择当前种子点？")
            accept_btn = mb.addButton("确定", QMessageBox.AcceptRole)
            mb.setStandardButtons(QMessageBox.Cancel)
            mb.setDefaultButton(QMessageBox.Cancel)
            mb.exec()

            if mb.clickedButton() == accept_btn:
                self.main_win.info_list[0] = "正在进行肺和气管分割..."
                self.main_win.info.setText("  ".join(self.main_win.info_list))

                self.seed_flag = False

                self.lung_trachea_seed = [int(self.main_win.x_pixel_edit.text()), int(self.main_win.y_pixel_edit.text()), int(self.main_win.z_pixel_edit.text())]
                # print(self.lung_trachea_seed)
                self.main_win.lung_mask_path = os.path.join(self.main_win.cwd, 'result', 'lung_mask.nii.gz')
                self.main_win.trachea_mask_path = os.path.join(self.main_win.cwd, 'result', 'trachea_mask.nii.gz')
                self.main_win.lung_trachea_mask_path = os.path.join(self.main_win.cwd, 'result', 'lung_trachea_mask.nii.gz')
                self.lung_trachea_seg_thread = LungTracheaSegThread(self.lung_trachea_seed, self.main_win.ct_nii_path, self.main_win.lung_mask_path, self.main_win.trachea_mask_path, self.main_win.lung_trachea_mask_path)  # 实例化肺分割线程, 可传参数
                self.lung_trachea_seg_thread.finish_signal.connect(self.main_win._lung_trachea_rebuild)  # 将线程_lung_seg_thread的信号finish_signal和主线程中的槽函数_lung_trachea_rebuild进行连接
                self.lung_trachea_seg_thread.start()  # 启动肺分割线程，执行线程类中run函数
            else:
                return
        else:
            QMessageBox.warning(self.main_win, '警告', '请选择正确的点', QMessageBox.Yes)
            return
        
    def _mouse_wheel_forward(self, obj, event):
        self.OnLeftButtonUp()

    def _mouse_wheel_backward(self, obj, event):
        self.OnLeftButtonDown()