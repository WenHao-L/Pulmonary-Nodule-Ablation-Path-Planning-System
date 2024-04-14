import os
import vtk
import numpy as np
import SimpleITK as sitk
# import vtk.util.numpy_support.vtk_to_numpy as vtk_to_numpy
from vtkmodules.util.numpy_support import vtk_to_numpy
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QErrorMessage
from utils.resample import resample_volume
from utils.dilate import dilate
from utils.reader import vtk_nii_reader
from utils.extract_point import extract_po, extract_ps, extract_pt
from utils.kmeans import get_pt_center
from src.seg import skin_seg
from utils.mc import marching_cubes
from utils.is_pareto_front import is_pareto_efficient

class AutoPathPlanThread(QThread):

    finish_signal = pyqtSignal(list)  # 使用自定义信号和主线程通讯, 参数是发送信号时附带参数的数据类型
    def __init__(self, main_class):
        super(AutoPathPlanThread, self).__init__()

        self.main_class = main_class

        # 参数初始化
        self.max_needle_depth = float(self.main_class.max_needle_depth_edit.text())  # 最大进针深度
        self.max_ablation_radius = float(self.main_class.max_ablation_radius_edit.text())  # 最大消融半径(mm)
        # self.min_distance = float(self.main_class.min_distance_edit.text())  # 与重要组织的最小间距
        self.ps_rate = float(self.main_class.ps_rate_edit.text())  # 皮肤点集采样参数
        self.pt_sample_spacing = int(self.main_class.pt_spacing_edit.text())  # 肿瘤点集采样间距(mm)
        self.safe_distance = int(self.main_class.safe_distance_edit.text())  # 安全边界距离

    def run(self):

        # 计算靶向点
        # 重采样肿瘤掩膜的spacing为(1, 1, 1)
        self.resample_tumor_mask_path = os.path.join(self.main_class.cwd, "result", "resample_tumor_mask.nii.gz")
        self.tumor_vol = sitk.Image(sitk.ReadImage(self.main_class.tumor_mask_path))
        self.resample_tumor_vol = resample_volume([1, 1, 1], self.tumor_vol)
        wriiter = sitk.ImageFileWriter()
        wriiter.SetFileName(self.resample_tumor_mask_path)
        wriiter.Execute(self.resample_tumor_vol)

        # 肿瘤安全边界膨胀
        self.dilate_tumor_mask_path = os.path.join(self.main_class.cwd, "result", "dilate_tumor_mask.nii.gz")
        dilate(self.resample_tumor_mask_path, self.dilate_tumor_mask_path, kernelsize=5)

        error_tag, self.tumor_reader_output = vtk_nii_reader(self.dilate_tumor_mask_path)

        # 判断是否发生错误
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(self.tumor_reader_output)
            error_message.exec_()
            return
        
        # 提取肿瘤点集pt
        self.pt_array = extract_pt(self.tumor_reader_output, self.pt_sample_spacing)
        print("肿瘤采样点集：", self.pt_array.shape[0])

        # 聚类算法获取消融次数, 肿瘤靶向点, 消融半径
        self.needles_num = 1  # 初始化针数为1
        self.complete_tag = False  # 消融完全标志

        while not self.complete_tag:
            self.pt_centers, self.pt_predict = get_pt_center(self.pt_array, self.needles_num)
            self.pt_radius = []
            self.radius_tag = True
            for i in range(self.needles_num):
                pt_array_i = np.array(self.pt_predict[i])
                pt_centers_i = self.pt_centers[i]
                pt_radius_i = np.max(np.sqrt(np.sum((pt_array_i-pt_centers_i)**2, axis=-1)))
                if pt_radius_i < self.max_ablation_radius:
                    self.pt_radius.append(pt_radius_i)
                else:
                    self.radius_tag = False
                    break
            if (i+1) == self.needles_num and self.radius_tag:
                self.complete_tag = True
            else:
                self.needles_num += 1

        # while not self.complete_tag:
        #     self.pt_centers, self.pt_predict = get_pt_center(self.pt_array, self.needles_num)
        #     self.pt_radius = []
        #     self.radius_tag = True
        #     for i in range(self.needles_num):
        #         pt_array_i = self.pt_array[np.where(self.pt_predict == i)]
        #         pt_centers_i = self.pt_centers[i]
        #         pt_radius_i = np.max(np.sqrt(np.sum((pt_array_i-pt_centers_i)**2, axis=-1)))
        #         if pt_radius_i < self.max_ablation_radius:
        #             self.pt_radius.append(pt_radius_i)
        #         else:
        #             self.radius_tag = False
        #             break
        #     if (i+1) == self.needles_num and self.radius_tag:
        #         self.complete_tag = True
        #     else:
        #         self.needles_num += 1

        # ps点集提取
        self._skin_mask_path = os.path.join(self.main_class.cwd, 'result', 'skin_mask.nii.gz')  # 皮肤掩膜路径
        skin_seg(self.main_class.ct_nii_path, self.main_class.lung_trachea_mask_path, self._skin_mask_path)  # 皮肤分割

        error_tag, self.ps_reader_output = vtk_nii_reader(self._skin_mask_path)
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(self.ps_reader_output)
            error_message.exec_()
            return
        
        self.ps_polydata = marching_cubes(self.ps_reader_output)

        face_up = self.main_class.body_orientation_rbtn.isChecked()
            
        self.ps_array = extract_ps(self.ps_polydata, self.main_class.extent, self.main_class.spacing, self.ps_rate, face_up)
        
        print("皮肤采样点集:", self.ps_array.shape[0])
        
        # po点集提取
        self.po_polydata, self.po_array = extract_po(self.main_class.Po_list)
        print("重要组织点集:", self.po_array.shape[0])

        # 针对每个靶向点，获取对应的进针点
        self.entry_point_list = []

        for i in range(self.needles_num):
            print("#####################")
            print("第", i, "针：")
            tag, output = self._get_needle_entry_point(self.po_polydata, self.po_array, self.pt_centers[i], self.ps_array, self.max_needle_depth)
            # tag, output = self._get_needle_entry_point(self.po_polydata, self.po_array, self.pt_centers[i], self.ps_array, self.max_needle_depth, self.min_distance)
            if tag:
                self.entry_point_list.append(output)
            else:
                self.finish_signal.emit([tag, output])
                return
        
        # 创建消融小球
        ablate_list = []
        for i in range(self.needles_num):
            ###############################################
            ellipsoid = vtk.vtkParametricEllipsoid()
            ellipsoid.SetXRadius(self.pt_radius[i]*1.2)
            ellipsoid.SetYRadius(self.pt_radius[i])
            ellipsoid.SetZRadius(self.pt_radius[i])

            ablate_ellipsoid = vtk.vtkParametricFunctionSource()
            ablate_ellipsoid.SetParametricFunction(ellipsoid)
            ablate_ellipsoid.Update()

            vector1 = np.array([1, 0, 0])
            vector2 = self.pt_centers[i] - self.entry_point_list[i]
            vector3 = np.array([vector2[0][0], vector2[0][1], 0])

            angle1 = self._angle_calculation(vector1, vector2)
            angle2 = self._angle_calculation(vector2, vector3)
            print("角度：", angle1, angle2)

            if vector2[0][1] < 0:
                angle1 = 360 - angle1
            if vector2[0][2] > 0:
                angle2 = 360 - angle2

            ellipsoid_trans = vtk.vtkTransform()
            ellipsoid_trans.PreMultiply()
            ellipsoid_trans.RotateZ(angle1)
            ellipsoid_trans.RotateY(angle2)
            ellipsoid_trans.PostMultiply()
            ellipsoid_trans.Translate(self.pt_centers[i])

            transform_filter = vtk.vtkTransformPolyDataFilter()
            transform_filter.SetInputConnection(ablate_ellipsoid.GetOutputPort())
            transform_filter.SetTransform(ellipsoid_trans)
            transform_filter.Update()

            ablate_list.append(transform_filter.GetOutput())

            ################################################
            # ablate_sphere = vtk.vtkSphereSource()
            # ablate_sphere.SetCenter(self.pt_centers[i][0], self.pt_centers[i][1], self.pt_centers[i][2])
            # ablate_sphere.SetRadius(self.pt_radius[i])
            # ablate_sphere.SetPhiResolution(30)
            # ablate_sphere.SetThetaResolution(30)
            # ablate_sphere.Update()
            # ablate_list.append(ablate_sphere.GetOutput())
        
        # 计算消融小球体积
        ablate_image_list = []
        vol_list = []
        for i in range(self.needles_num):
            ablate_image = self._polydata_to_imagedata(self.tumor_reader_output.GetSpacing(), 
                                                       self.tumor_reader_output.GetDimensions(),
                                                       self.tumor_reader_output.GetOrigin(),
                                                       ablate_list[i])
            ablate_vol = self._calculate_volume(ablate_image)
            ablate_image_list.append(ablate_image)
            vol_list.append(ablate_vol)

        # 计算肿瘤体积(+安全边界)
        tumor_image = self.tumor_reader_output
        tumor_array = vtk_to_numpy(tumor_image.GetPointData().GetScalars())
        tumor_vol = np.sum(tumor_array)
        # tumor_image = self._polydata_to_imagedata(self.tumor_reader_output.GetSpacing(), 
        #                                                self.tumor_reader_output.GetDimensions(),
        #                                                self.tumor_reader_output.GetOrigin(),
        #                                                self.main_class.tumor_polydata)
        # tumor_vol = self._calculate_volume(tumor_image)

        # 计算iou
        ablate_image_all = ablate_image_list[0]
        ablate_vol_all = vol_list[0]
        self.iou_list = []
        esp = 0.0000001

        if self.needles_num > 1:
            for i in range(1, self.needles_num):
                ablate_image_all = self._bool_or(ablate_image_all, ablate_image_list[i])
            ablate_vol_all = self._calculate_volume(ablate_image_all)

            for i in range(self.needles_num):
                and_image = self._bool_and(tumor_image, ablate_image_list[i])
                and_volume = self._calculate_volume(and_image)

                ac = round(and_volume / (tumor_vol+esp), 2)
                oa = round((vol_list[i] - and_volume) / (vol_list[i]+esp), 2)
                self.iou_list.append([ac, oa])

        and_image_all = self._bool_and(tumor_image, ablate_image_all)
        and_volume_all = self._calculate_volume(and_image_all)

        ac_all = round(and_volume_all / (tumor_vol+esp), 2)
        oa_all = round((ablate_vol_all - and_volume_all) / (ablate_vol_all+esp), 2)

        if self.needles_num == 1:
            self.iou_list.append([ac_all, oa_all])

        print("tumor_vol:", tumor_vol)
        print("ablate_image_all:", ablate_vol_all)
        print("and_volume_all:", and_volume_all)

        self.finish_signal.emit([True, self.needles_num, self.entry_point_list, self.pt_centers, self.pt_radius, self.iou_list, ac_all, oa_all, ablate_list, self.dilate_tumor_mask_path])

    def _angle_calculation(self, vector1, vector2):
        data_m = np.sqrt(np.sum(vector1 * vector1))
        data_n = np.sqrt(np.sum(vector2 * vector2))
        cos_theta = np.sum(vector1 * vector2) / (data_m * data_n)
        theta = np.degrees(np.arccos(cos_theta))
        return theta

    # def _get_needle_entry_point(self, po_polydata, po_array, pt_point, ps_array, max_needle_depth, min_distance_standard):
    def _get_needle_entry_point(self, po_polydata, po_array, pt_point, ps_array, max_needle_depth):
        """获取肿瘤靶向点对应的进针点"""

        # 约束条件一：穿刺深度
        needle_depth_array = np.sqrt(np.sum((ps_array-pt_point)**2, axis=-1))  # 计算各皮肤点到肿瘤中心点的距离
        depth_mask = needle_depth_array <= max_needle_depth
        ps_array = ps_array[depth_mask]
        needle_depth_array = needle_depth_array[depth_mask]
        print("约束1（进针深度）：", ps_array.shape[0])
        if ps_array.shape[0] < 100:
            return False, "请检查身体朝向是否设置正确，或者增大最大进针深度"

        # 约束条件二：重要器官避障
        ps_list = []
        needle_depth_list = []

        tree = vtk.vtkOBBTree()
        tree.SetDataSet(po_polydata)
        tree.BuildLocator()
        intersect_points = vtk.vtkPoints()

        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            needle_depth = needle_depth_array[i]
            tree.IntersectWithLine(coordinate, pt_point, intersect_points, None)
            if intersect_points.GetNumberOfPoints() == 0:
                ps_list.append(coordinate)
                needle_depth_list.append(needle_depth)
        if len(ps_list) < 5:
            # 删除血管约束条件
            # po点集提取
            Po_list = []
            Po_list.append(self.main_class.trachea_polydata)
            Po_list.append(self.main_class.skeleton_polydata)
            po_polydata, po_array = extract_po(Po_list)
            print("重要组织点集:", po_array.shape[0])

            ps_list = []
            needle_depth_list = []

            tree = vtk.vtkOBBTree()
            tree.SetDataSet(po_polydata)
            tree.BuildLocator()
            intersect_points = vtk.vtkPoints()

            for i in range(ps_array.shape[0]):
                coordinate = ps_array[i]
                needle_depth = needle_depth_array[i]
                tree.IntersectWithLine(coordinate, pt_point, intersect_points, None)
                if intersect_points.GetNumberOfPoints() == 0:
                    ps_list.append(coordinate)
                    needle_depth_list.append(needle_depth)

        ps_array = np.array(ps_list)
        needle_depth_array = np.array(needle_depth_list)
        print("约束2（重要组织避障）：", ps_array.shape[0])
        if ps_array.shape[0] < 1:
            return False, "无法避开重要组织，请尝试减小肿瘤点集采样间距或减小皮肤点集采样参数"

        # 目标性条件一：重要器官距离风险子目标函数
        dvo_list = []  # dvo -> 路径到重要器官的距离

        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            needle_depth = needle_depth_array[i]
            line = vtk.vtkLine()
            x = np.array([0.0, 0.0, 0.0])
            t = vtk.reference(0.0)
            min_distance = 200

            for po in po_array:
                distance = line.DistanceToLine(po, coordinate, pt_point, t, x)
                min_distance = min(distance, min_distance)

            dvo_list.append(min_distance)
        
        dvo_array = np.array(dvo_list)
        dvo_array = (dvo_array-min(dvo_array))/(max(dvo_array)-min(dvo_array))
        print("dvo_shape：", dvo_array.shape[0])

        # 约束条件四：皮肤入刺角
        # 目标性条件二：皮肤入刺角风险子目标函数

        # 目标性条件三：胸壁厚度风险子目标函数
        # 目标性条件四：肺内长度风险子目标函数
        locator = vtk.vtkCellLocator()  # Create a locator
        locator.SetDataSet(self.main_class.lung_polydata)
        locator.BuildLocator()
        tol = 1.e-6
        cwt_list = []  # cwt -> 胸壁厚度
        pll_list = []  # pll -> 肺内长度
        
        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            t = vtk.mutable(0)
            pos = np.array([0., 0., 0.])
            pcoords = np.array([0., 0., 0.])
            sub_id = vtk.mutable(0)
            cell_id = vtk.mutable(0)
            cell = vtk.vtkGenericCell()
            locator.IntersectWithLine(coordinate, pt_point, tol, t, pos, pcoords, sub_id, cell_id, cell)
            if cell_id is not None:
                cwt = np.linalg.norm(coordinate-pos)
                pll = np.linalg.norm(pos-pt_point)
                cwt_list.append(cwt)
                pll_list.append(pll)
            else:
                cwt_list.append(-1)
                pll_list.append(-1)
        cwt_array = np.array(cwt_list)
        cwt_max = max(cwt_array)
        cwt_array[cwt_array==-1] = cwt_max
        cwt_min = min(cwt_array)
        cwt_array = (cwt_array-cwt_min)/(cwt_max-cwt_min)
        print("cwt_shape：", cwt_array.shape[0])
        
        pll_array = np.array(pll_list)
        pll_max = max(pll_array)
        pll_array[pll_array==-1] = pll_max
        pll_min = min(pll_array)
        pll_array = (pll_array-pll_min)/(pll_max-pll_min)
        print("pll_shape：", pll_array.shape[0])

        # 计算帕累托前沿
        cost_array = np.stack((cwt_array, pll_array, dvo_array), axis=-1)
        is_pareto_front = is_pareto_efficient(cost_array)
        pareto_ps_array = ps_array[is_pareto_front, :]
        pareto_cost_array = cost_array[is_pareto_front, :]
        print("帕累托前沿：", pareto_ps_array.shape)

        # 计算最优穿刺路径，可自定义每个目标函数的比率，这里取平均
        pareto_score = np.mean(pareto_cost_array, axis=1)
        min_index = np.where(pareto_score==np.min(pareto_score))
        best_ps = pareto_ps_array[min_index]
        print("帕累托最优前沿:", best_ps)
        
        return True, best_ps

    def _polydata_to_imagedata(self, spacing, dim, origin, data):
        white_image = vtk.vtkImageData()
        white_image.SetSpacing(spacing)
        white_image.SetDimensions(dim)
        white_image.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)
        white_image.SetOrigin(origin)
        white_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

        pol2stenc = vtk.vtkPolyDataToImageStencil()
        pol2stenc.SetInputData(data)
        pol2stenc.SetOutputOrigin(origin)
        pol2stenc.SetOutputSpacing(spacing)
        pol2stenc.SetOutputWholeExtent(white_image.GetExtent())
        pol2stenc.Update()

        imgstenc = vtk.vtkImageStencil()
        imgstenc.SetInputData(white_image)
        imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
        imgstenc.ReverseStencilOn()
        imgstenc.SetBackgroundValue(1)
        imgstenc.Update()

        return imgstenc.GetOutput()

    def _bool_or(self, data1, data2):
        image_or = vtk.vtkImageLogic()
        image_or.SetInput1Data(data1)
        image_or.SetInput2Data(data2)
        image_or.SetOperationToOr()
        image_or.SetOutputTrueValue(1)
        image_or.Update()

        return image_or.GetOutput()

    def _bool_and(self, data1, data2):
        image_and = vtk.vtkImageLogic()
        image_and.SetInput1Data(data1)
        image_and.SetInput2Data(data2)
        image_and.SetOperationToAnd()
        image_and.SetOutputTrueValue(1)
        image_and.Update()

        return image_and.GetOutput()

    def _bool_xor(self, data1, data2):
        image_xor = vtk.vtkImageLogic()
        image_xor.SetInput1Data(data1)
        image_xor.SetInput2Data(data2)
        image_xor.SetOperationToAnd()
        image_xor.SetOutputTrueValue(1)
        image_xor.Update()

        return image_xor.GetOutput()

    def _calculate_volume(self, data):
        scalars = data.GetPointData().GetScalars()
        array = vtk_to_numpy(scalars)
        volume = sum(array)

        return volume
    

class LargeAutoPathPlanThread(QThread):

    finish_signal = pyqtSignal(list)  # 使用自定义信号和主线程通讯, 参数是发送信号时附带参数的数据类型
    def __init__(self, main_class):
        super(LargeAutoPathPlanThread, self).__init__()

        self.main_class = main_class

        # 参数初始化
        self.max_needle_depth = float(self.main_class.max_needle_depth_edit.text())  # 最大进针深度
        # self.max_ablation_radius = float(self.main_class.max_ablation_radius_edit.text())  # 最大消融半径(mm)
        # self.min_distance = float(self.main_class.min_distance_edit.text())  # 与重要组织的最小间距
        self.ps_rate = float(self.main_class.ps_rate_edit.text())  # 皮肤点集采样参数
        self.pt_sample_spacing = int(self.main_class.pt_spacing_edit.text())  # 肿瘤点集采样间距(mm)
        # self.safe_distance = int(self.main_class.safe_distance_edit.text())  # 安全边界距离
        self.needles_num = int(self.main_class.neddle_num_edit.text())  # 初始化针数

    def run(self):

        # 计算靶向点
        # 重采样肿瘤掩膜的spacing为(1, 1, 1)
        self.resample_tumor_mask_path = os.path.join(self.main_class.cwd, "result", "resample_tumor_mask.nii.gz")
        self.tumor_vol = sitk.Image(sitk.ReadImage(self.main_class.tumor_mask_path))
        self.resample_tumor_vol = resample_volume([1, 1, 1], self.tumor_vol)
        wriiter = sitk.ImageFileWriter()
        wriiter.SetFileName(self.resample_tumor_mask_path)
        wriiter.Execute(self.resample_tumor_vol)

        # 肿瘤安全边界膨胀
        # self.dilate_tumor_mask_path = os.path.join(self.main_class.cwd, "result", "dilate_tumor_mask.nii.gz")
        # dilate(self.resample_tumor_mask_path, self.dilate_tumor_mask_path, kernelsize=5)

        error_tag, self.tumor_reader_output = vtk_nii_reader(self.resample_tumor_mask_path)

        # 判断是否发生错误
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(self.tumor_reader_output)
            error_message.exec_()
            return
        
        # 提取肿瘤点集pt
        self.pt_array = extract_pt(self.tumor_reader_output, self.pt_sample_spacing)
        print("肿瘤采样点集：", self.pt_array.shape[0])

        # 聚类算法获取消融次数, 肿瘤靶向点, 消融半径
        
        self.pt_centers, self.pt_predict = get_pt_center(self.pt_array, self.needles_num)
        self.pt_radius = []
        for i in range(self.needles_num):
            pt_array_i = np.array(self.pt_predict[i])
            pt_centers_i = self.pt_centers[i]
            pt_radius_i = np.max(np.sqrt(np.sum((pt_array_i-pt_centers_i)**2, axis=-1))) / 1.5
            self.pt_radius.append(pt_radius_i)

        # self.needles_num = 1
        # self.complete_tag = False  # 消融完全标志

        # while not self.complete_tag:
        #     self.pt_centers, self.pt_predict = get_pt_center(self.pt_array, self.needles_num)
        #     self.pt_radius = []
        #     self.radius_tag = True
        #     for i in range(self.needles_num):
        #         pt_array_i = np.array(self.pt_predict[i])
        #         pt_centers_i = self.pt_centers[i]
        #         pt_radius_i = np.max(np.sqrt(np.sum((pt_array_i-pt_centers_i)**2, axis=-1)))
        #         if pt_radius_i < self.max_ablation_radius:
        #             self.pt_radius.append(pt_radius_i)
        #         else:
        #             self.radius_tag = False
        #             break
        #     if (i+1) == self.needles_num and self.radius_tag:
        #         self.complete_tag = True
        #     else:
        #         self.needles_num += 1

        # while not self.complete_tag:
        #     self.pt_centers, self.pt_predict = get_pt_center(self.pt_array, self.needles_num)
        #     self.pt_radius = []
        #     self.radius_tag = True
        #     for i in range(self.needles_num):
        #         pt_array_i = self.pt_array[np.where(self.pt_predict == i)]
        #         pt_centers_i = self.pt_centers[i]
        #         pt_radius_i = np.max(np.sqrt(np.sum((pt_array_i-pt_centers_i)**2, axis=-1)))
        #         if pt_radius_i < self.max_ablation_radius:
        #             self.pt_radius.append(pt_radius_i)
        #         else:
        #             self.radius_tag = False
        #             break
        #     if (i+1) == self.needles_num and self.radius_tag:
        #         self.complete_tag = True
        #     else:
        #         self.needles_num += 1

        # ps点集提取
        self._skin_mask_path = os.path.join(self.main_class.cwd, 'result', 'skin_mask.nii.gz')  # 皮肤掩膜路径
        skin_seg(self.main_class.ct_nii_path, self.main_class.lung_trachea_mask_path, self._skin_mask_path)  # 皮肤分割

        error_tag, self.ps_reader_output = vtk_nii_reader(self._skin_mask_path)
        if error_tag:
            error_message = QErrorMessage(self)
            error_message.setWindowTitle("错误提示")
            error_message.showMessage(self.ps_reader_output)
            error_message.exec_()
            return
        
        self.ps_polydata = marching_cubes(self.ps_reader_output)

        face_up = self.main_class.body_orientation_rbtn.isChecked()
            
        self.ps_array = extract_ps(self.ps_polydata, self.main_class.extent, self.main_class.spacing, self.ps_rate, face_up)
        
        print("皮肤采样点集:", self.ps_array.shape[0])
        
        # po点集提取
        self.po_polydata, self.po_array = extract_po(self.main_class.Po_list)
        print("重要组织点集:", self.po_array.shape[0])

        # 针对每个靶向点，获取对应的进针点
        self.entry_point_list = []

        for i in range(self.needles_num):
            print("#####################")
            print("第", i, "针：")
            tag, output = self._get_needle_entry_point(self.po_polydata, self.po_array, self.pt_centers[i], self.ps_array, self.max_needle_depth)
            # tag, output = self._get_needle_entry_point(self.po_polydata, self.po_array, self.pt_centers[i], self.ps_array, self.max_needle_depth, self.min_distance)
            if tag:
                self.entry_point_list.append(output)
            else:
                self.finish_signal.emit([tag, output])
                return
        
        # 创建消融小球
        ablate_list = []
        for i in range(self.needles_num):
            ###############################################
            ellipsoid = vtk.vtkParametricEllipsoid()
            ellipsoid.SetXRadius(self.pt_radius[i])
            ellipsoid.SetYRadius(self.pt_radius[i]/1.2)
            ellipsoid.SetZRadius(self.pt_radius[i]/1.2)

            ablate_ellipsoid = vtk.vtkParametricFunctionSource()
            ablate_ellipsoid.SetParametricFunction(ellipsoid)
            ablate_ellipsoid.Update()

            vector1 = np.array([1, 0, 0])
            vector2 = self.pt_centers[i] - self.entry_point_list[i]
            vector3 = np.array([vector2[0][0], vector2[0][1], 0])

            angle1 = self._angle_calculation(vector1, vector2)
            angle2 = self._angle_calculation(vector2, vector3)
            print("角度：", angle1, angle2)

            if vector2[0][1] < 0:
                angle1 = 360 - angle1
            if vector2[0][2] > 0:
                angle2 = 360 - angle2

            ellipsoid_trans = vtk.vtkTransform()
            ellipsoid_trans.PreMultiply()
            ellipsoid_trans.RotateZ(angle1)
            ellipsoid_trans.RotateY(angle2)
            ellipsoid_trans.PostMultiply()
            ellipsoid_trans.Translate(self.pt_centers[i])

            transform_filter = vtk.vtkTransformPolyDataFilter()
            transform_filter.SetInputConnection(ablate_ellipsoid.GetOutputPort())
            transform_filter.SetTransform(ellipsoid_trans)
            transform_filter.Update()

            ablate_list.append(transform_filter.GetOutput())

            ################################################
            # ablate_sphere = vtk.vtkSphereSource()
            # ablate_sphere.SetCenter(self.pt_centers[i][0], self.pt_centers[i][1], self.pt_centers[i][2])
            # ablate_sphere.SetRadius(self.pt_radius[i])
            # ablate_sphere.SetPhiResolution(30)
            # ablate_sphere.SetThetaResolution(30)
            # ablate_sphere.Update()
            # ablate_list.append(ablate_sphere.GetOutput())
        
        # 计算消融小球体积
        ablate_image_list = []
        vol_list = []
        for i in range(self.needles_num):
            ablate_image = self._polydata_to_imagedata(self.tumor_reader_output.GetSpacing(), 
                                                       self.tumor_reader_output.GetDimensions(),
                                                       self.tumor_reader_output.GetOrigin(),
                                                       ablate_list[i])
            ablate_vol = self._calculate_volume(ablate_image)
            ablate_image_list.append(ablate_image)
            vol_list.append(ablate_vol)

        # 计算肿瘤体积
        tumor_image = self.tumor_reader_output
        tumor_array = vtk_to_numpy(tumor_image.GetPointData().GetScalars())
        tumor_vol = np.sum(tumor_array)
        # tumor_image = self._polydata_to_imagedata(self.tumor_reader_output.GetSpacing(), 
        #                                                self.tumor_reader_output.GetDimensions(),
        #                                                self.tumor_reader_output.GetOrigin(),
        #                                                self.main_class.tumor_polydata)
        # tumor_vol = self._calculate_volume(tumor_image)

        # 计算iou
        ablate_image_all = ablate_image_list[0]
        ablate_vol_all = vol_list[0]
        self.iou_list = []
        esp = 0.0000001

        if self.needles_num > 1:
            for i in range(1, self.needles_num):
                ablate_image_all = self._bool_or(ablate_image_all, ablate_image_list[i])
            ablate_vol_all = self._calculate_volume(ablate_image_all)

            for i in range(self.needles_num):
                and_image = self._bool_and(tumor_image, ablate_image_list[i])
                and_volume = self._calculate_volume(and_image)

                ac = round(and_volume / (tumor_vol+esp), 2)
                oa = round((vol_list[i] - and_volume) / (vol_list[i]+esp), 2)
                self.iou_list.append([ac, oa])

        and_image_all = self._bool_and(tumor_image, ablate_image_all)
        and_volume_all = self._calculate_volume(and_image_all)

        ac_all = round(and_volume_all / (tumor_vol+esp), 2)
        oa_all = round((ablate_vol_all - and_volume_all) / (ablate_vol_all+esp), 2)

        if self.needles_num == 1:
            self.iou_list.append([ac_all, oa_all])

        print("tumor_vol:", tumor_vol)
        print("ablate_image_all:", ablate_vol_all)
        print("and_volume_all:", and_volume_all)

        self.finish_signal.emit([True, self.needles_num, self.entry_point_list, self.pt_centers, self.pt_radius, self.iou_list, ac_all, oa_all, ablate_list])

    def _angle_calculation(self, vector1, vector2):
        data_m = np.sqrt(np.sum(vector1 * vector1))
        data_n = np.sqrt(np.sum(vector2 * vector2))
        cos_theta = np.sum(vector1 * vector2) / (data_m * data_n)
        theta = np.degrees(np.arccos(cos_theta))
        return theta

    # def _get_needle_entry_point(self, po_polydata, po_array, pt_point, ps_array, max_needle_depth, min_distance_standard):
    def _get_needle_entry_point(self, po_polydata, po_array, pt_point, ps_array, max_needle_depth):
        """获取肿瘤靶向点对应的进针点"""

        # 约束条件一：穿刺深度
        needle_depth_array = np.sqrt(np.sum((ps_array-pt_point)**2, axis=-1))  # 计算各皮肤点到肿瘤中心点的距离
        depth_mask = needle_depth_array <= max_needle_depth
        ps_array = ps_array[depth_mask]
        needle_depth_array = needle_depth_array[depth_mask]
        print("约束1（进针深度）：", ps_array.shape[0])
        if ps_array.shape[0] < 100:
            return False, "请检查身体朝向是否设置正确，或者增大最大进针深度"

        # 约束条件二：重要器官避障
        ps_list = []
        needle_depth_list = []

        tree = vtk.vtkOBBTree()
        tree.SetDataSet(po_polydata)
        tree.BuildLocator()
        intersect_points = vtk.vtkPoints()

        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            needle_depth = needle_depth_array[i]
            tree.IntersectWithLine(coordinate, pt_point, intersect_points, None)
            if intersect_points.GetNumberOfPoints() == 0:
                ps_list.append(coordinate)
                needle_depth_list.append(needle_depth)
        if len(ps_list) < 5:
            # 删除血管约束条件
            # po点集提取
            Po_list = []
            Po_list.append(self.main_class.trachea_polydata)
            Po_list.append(self.main_class.skeleton_polydata)
            po_polydata, po_array = extract_po(Po_list)
            print("重要组织点集:", po_array.shape[0])

            ps_list = []
            needle_depth_list = []

            tree = vtk.vtkOBBTree()
            tree.SetDataSet(po_polydata)
            tree.BuildLocator()
            intersect_points = vtk.vtkPoints()

            for i in range(ps_array.shape[0]):
                coordinate = ps_array[i]
                needle_depth = needle_depth_array[i]
                tree.IntersectWithLine(coordinate, pt_point, intersect_points, None)
                if intersect_points.GetNumberOfPoints() == 0:
                    ps_list.append(coordinate)
                    needle_depth_list.append(needle_depth)

        ps_array = np.array(ps_list)
        needle_depth_array = np.array(needle_depth_list)
        print("约束2（重要组织避障）：", ps_array.shape[0])
        if ps_array.shape[0] < 1:
            return False, "无法避开重要组织，请尝试减小肿瘤点集采样间距或减小皮肤点集采样参数"

        # 目标性条件一：重要器官距离风险子目标函数
        dvo_list = []  # dvo -> 路径到重要器官的距离

        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            needle_depth = needle_depth_array[i]
            line = vtk.vtkLine()
            x = np.array([0.0, 0.0, 0.0])
            t = vtk.reference(0.0)
            min_distance = 200

            for po in po_array:
                distance = line.DistanceToLine(po, coordinate, pt_point, t, x)
                min_distance = min(distance, min_distance)

            dvo_list.append(min_distance)
        
        dvo_array = np.array(dvo_list)
        dvo_array = (dvo_array-min(dvo_array))/(max(dvo_array)-min(dvo_array))
        print("dvo_shape：", dvo_array.shape[0])

        # 约束条件四：皮肤入刺角
        # 目标性条件二：皮肤入刺角风险子目标函数

        # 目标性条件三：胸壁厚度风险子目标函数
        # 目标性条件四：肺内长度风险子目标函数
        locator = vtk.vtkCellLocator()  # Create a locator
        locator.SetDataSet(self.main_class.lung_polydata)
        locator.BuildLocator()
        tol = 1.e-6
        cwt_list = []  # cwt -> 胸壁厚度
        pll_list = []  # pll -> 肺内长度
        
        for i in range(ps_array.shape[0]):
            coordinate = ps_array[i]
            t = vtk.mutable(0)
            pos = np.array([0., 0., 0.])
            pcoords = np.array([0., 0., 0.])
            sub_id = vtk.mutable(0)
            cell_id = vtk.mutable(0)
            cell = vtk.vtkGenericCell()
            locator.IntersectWithLine(coordinate, pt_point, tol, t, pos, pcoords, sub_id, cell_id, cell)
            if cell_id is not None:
                cwt = np.linalg.norm(coordinate-pos)
                pll = np.linalg.norm(pos-pt_point)
                cwt_list.append(cwt)
                pll_list.append(pll)
            else:
                cwt_list.append(-1)
                pll_list.append(-1)
        cwt_array = np.array(cwt_list)
        cwt_max = max(cwt_array)
        cwt_array[cwt_array==-1] = cwt_max
        cwt_min = min(cwt_array)
        cwt_array = (cwt_array-cwt_min)/(cwt_max-cwt_min)
        print("cwt_shape：", cwt_array.shape[0])
        
        pll_array = np.array(pll_list)
        pll_max = max(pll_array)
        pll_array[pll_array==-1] = pll_max
        pll_min = min(pll_array)
        pll_array = (pll_array-pll_min)/(pll_max-pll_min)
        print("pll_shape：", pll_array.shape[0])

        # 计算帕累托前沿
        cost_array = np.stack((cwt_array, pll_array, dvo_array), axis=-1)
        is_pareto_front = is_pareto_efficient(cost_array)
        pareto_ps_array = ps_array[is_pareto_front, :]
        pareto_cost_array = cost_array[is_pareto_front, :]
        print("帕累托前沿：", pareto_ps_array.shape)

        # 计算最优穿刺路径，可自定义每个目标函数的比率，这里取平均
        pareto_score = np.mean(pareto_cost_array, axis=1)
        min_index = np.where(pareto_score==np.min(pareto_score))
        best_ps = pareto_ps_array[min_index]
        print("帕累托最优前沿:", best_ps)
        
        return True, best_ps

    def _polydata_to_imagedata(self, spacing, dim, origin, data):
        white_image = vtk.vtkImageData()
        white_image.SetSpacing(spacing)
        white_image.SetDimensions(dim)
        white_image.SetExtent(0, dim[0] - 1, 0, dim[1] - 1, 0, dim[2] - 1)
        white_image.SetOrigin(origin)
        white_image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)

        pol2stenc = vtk.vtkPolyDataToImageStencil()
        pol2stenc.SetInputData(data)
        pol2stenc.SetOutputOrigin(origin)
        pol2stenc.SetOutputSpacing(spacing)
        pol2stenc.SetOutputWholeExtent(white_image.GetExtent())
        pol2stenc.Update()

        imgstenc = vtk.vtkImageStencil()
        imgstenc.SetInputData(white_image)
        imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
        imgstenc.ReverseStencilOn()
        imgstenc.SetBackgroundValue(1)
        imgstenc.Update()

        return imgstenc.GetOutput()

    def _bool_or(self, data1, data2):
        image_or = vtk.vtkImageLogic()
        image_or.SetInput1Data(data1)
        image_or.SetInput2Data(data2)
        image_or.SetOperationToOr()
        image_or.SetOutputTrueValue(1)
        image_or.Update()

        return image_or.GetOutput()

    def _bool_and(self, data1, data2):
        image_and = vtk.vtkImageLogic()
        image_and.SetInput1Data(data1)
        image_and.SetInput2Data(data2)
        image_and.SetOperationToAnd()
        image_and.SetOutputTrueValue(1)
        image_and.Update()

        return image_and.GetOutput()

    def _bool_xor(self, data1, data2):
        image_xor = vtk.vtkImageLogic()
        image_xor.SetInput1Data(data1)
        image_xor.SetInput2Data(data2)
        image_xor.SetOperationToAnd()
        image_xor.SetOutputTrueValue(1)
        image_xor.Update()

        return image_xor.GetOutput()

    def _calculate_volume(self, data):
        scalars = data.GetPointData().GetScalars()
        array = vtk_to_numpy(scalars)
        volume = sum(array)

        return volume