# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'path_planninggBbupx.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1047, 845)
        self.import_action = QAction(MainWindow)
        self.import_action.setObjectName(u"import_action")
        self.exit_actiont = QAction(MainWindow)
        self.exit_actiont.setObjectName(u"exit_actiont")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.seg_tab = QWidget()
        self.seg_tab.setObjectName(u"seg_tab")
        self.verticalLayout_2 = QVBoxLayout(self.seg_tab)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(30, 20, 30, 20)
        self.import_layout = QHBoxLayout()
        self.import_layout.setSpacing(3)
        self.import_layout.setObjectName(u"import_layout")
        self.import_btn = QPushButton(self.seg_tab)
        self.import_btn.setObjectName(u"import_btn")

        self.import_layout.addWidget(self.import_btn)

        self.import_path_edit = QLineEdit(self.seg_tab)
        self.import_path_edit.setObjectName(u"import_path_edit")
        self.import_path_edit.setReadOnly(True)

        self.import_layout.addWidget(self.import_path_edit)

        self.import_layout.setStretch(0, 1)
        self.import_layout.setStretch(1, 5)

        self.verticalLayout_2.addLayout(self.import_layout)

        self.seg_line_1 = QFrame(self.seg_tab)
        self.seg_line_1.setObjectName(u"seg_line_1")
        self.seg_line_1.setFrameShape(QFrame.HLine)
        self.seg_line_1.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.seg_line_1)

        self.window_layout = QHBoxLayout()
        self.window_layout.setSpacing(3)
        self.window_layout.setObjectName(u"window_layout")
        self.window_width_layout = QVBoxLayout()
        self.window_width_layout.setSpacing(3)
        self.window_width_layout.setObjectName(u"window_width_layout")
        self.window_width_label = QLabel(self.seg_tab)
        self.window_width_label.setObjectName(u"window_width_label")
        self.window_width_label.setAlignment(Qt.AlignCenter)

        self.window_width_layout.addWidget(self.window_width_label)

        self.window_width_edit = QLineEdit(self.seg_tab)
        self.window_width_edit.setObjectName(u"window_width_edit")
        self.window_width_edit.setAlignment(Qt.AlignCenter)

        self.window_width_layout.addWidget(self.window_width_edit)


        self.window_layout.addLayout(self.window_width_layout)

        self.window_level_layout = QVBoxLayout()
        self.window_level_layout.setSpacing(3)
        self.window_level_layout.setObjectName(u"window_level_layout")
        self.window_level_label = QLabel(self.seg_tab)
        self.window_level_label.setObjectName(u"window_level_label")
        self.window_level_label.setAlignment(Qt.AlignCenter)

        self.window_level_layout.addWidget(self.window_level_label)

        self.window_level_edit = QLineEdit(self.seg_tab)
        self.window_level_edit.setObjectName(u"window_level_edit")
        self.window_level_edit.setAlignment(Qt.AlignCenter)

        self.window_level_layout.addWidget(self.window_level_edit)


        self.window_layout.addLayout(self.window_level_layout)


        self.verticalLayout_2.addLayout(self.window_layout)

        self.seg_line_2 = QFrame(self.seg_tab)
        self.seg_line_2.setObjectName(u"seg_line_2")
        self.seg_line_2.setFrameShape(QFrame.HLine)
        self.seg_line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.seg_line_2)

        self.seg_layout = QGridLayout()
        self.seg_layout.setSpacing(2)
        self.seg_layout.setObjectName(u"seg_layout")
        self.seg_layout.setContentsMargins(2, 2, 2, 2)
        self.tumor_seg_btn = QPushButton(self.seg_tab)
        self.tumor_seg_btn.setObjectName(u"tumor_seg_btn")

        self.seg_layout.addWidget(self.tumor_seg_btn, 4, 0, 1, 1)

        self.skeleton_slider = QSlider(self.seg_tab)
        self.skeleton_slider.setObjectName(u"skeleton_slider")
        self.skeleton_slider.setOrientation(Qt.Horizontal)

        self.seg_layout.addWidget(self.skeleton_slider, 3, 1, 1, 1)

        self.lung_slider = QSlider(self.seg_tab)
        self.lung_slider.setObjectName(u"lung_slider")
        self.lung_slider.setOrientation(Qt.Horizontal)

        self.seg_layout.addWidget(self.lung_slider, 0, 1, 1, 1)

        self.tumor_slider = QSlider(self.seg_tab)
        self.tumor_slider.setObjectName(u"tumor_slider")
        self.tumor_slider.setOrientation(Qt.Horizontal)

        self.seg_layout.addWidget(self.tumor_slider, 4, 1, 1, 1)

        self.lung_trachea_seg_btn = QPushButton(self.seg_tab)
        self.lung_trachea_seg_btn.setObjectName(u"lung_trachea_seg_btn")

        self.seg_layout.addWidget(self.lung_trachea_seg_btn, 0, 0, 1, 1)

        self.skeleton_seg_btn = QPushButton(self.seg_tab)
        self.skeleton_seg_btn.setObjectName(u"skeleton_seg_btn")

        self.seg_layout.addWidget(self.skeleton_seg_btn, 3, 0, 1, 1)

        self.vessel_slider = QSlider(self.seg_tab)
        self.vessel_slider.setObjectName(u"vessel_slider")
        self.vessel_slider.setOrientation(Qt.Horizontal)

        self.seg_layout.addWidget(self.vessel_slider, 2, 1, 1, 1)

        self.vessel_seg_btn = QPushButton(self.seg_tab)
        self.vessel_seg_btn.setObjectName(u"vessel_seg_btn")

        self.seg_layout.addWidget(self.vessel_seg_btn, 2, 0, 1, 1)

        self.trachea_slider = QSlider(self.seg_tab)
        self.trachea_slider.setObjectName(u"trachea_slider")
        self.trachea_slider.setOrientation(Qt.Horizontal)

        self.seg_layout.addWidget(self.trachea_slider, 1, 1, 1, 1)

        self.seg_layout.setRowStretch(0, 1)
        self.seg_layout.setRowStretch(1, 1)
        self.seg_layout.setRowStretch(2, 1)
        self.seg_layout.setRowStretch(3, 1)
        self.seg_layout.setRowStretch(4, 1)
        self.seg_layout.setColumnStretch(0, 1)
        self.seg_layout.setColumnStretch(1, 1)
        self.seg_layout.setColumnMinimumWidth(0, 1)
        self.seg_layout.setColumnMinimumWidth(1, 1)
        self.seg_layout.setRowMinimumHeight(0, 1)
        self.seg_layout.setRowMinimumHeight(1, 1)
        self.seg_layout.setRowMinimumHeight(2, 1)
        self.seg_layout.setRowMinimumHeight(3, 1)
        self.seg_layout.setRowMinimumHeight(4, 1)

        self.verticalLayout_2.addLayout(self.seg_layout)

        self.seg_line_3 = QFrame(self.seg_tab)
        self.seg_line_3.setObjectName(u"seg_line_3")
        self.seg_line_3.setFrameShape(QFrame.HLine)
        self.seg_line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_2.addWidget(self.seg_line_3)

        self.message_edit = QTextEdit(self.seg_tab)
        self.message_edit.setObjectName(u"message_edit")
        self.message_edit.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.message_edit)

        self.tabWidget.addTab(self.seg_tab, "")
        self.path_planning_tab = QWidget()
        self.path_planning_tab.setObjectName(u"path_planning_tab")
        self.verticalLayout_3 = QVBoxLayout(self.path_planning_tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pixel_label = QLabel(self.path_planning_tab)
        self.pixel_label.setObjectName(u"pixel_label")
        self.pixel_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.pixel_label)

        self.pixel_layout = QHBoxLayout()
        self.pixel_layout.setSpacing(2)
        self.pixel_layout.setObjectName(u"pixel_layout")
        self.x_pixel_edit = QLineEdit(self.path_planning_tab)
        self.x_pixel_edit.setObjectName(u"x_pixel_edit")
        self.x_pixel_edit.setAlignment(Qt.AlignCenter)

        self.pixel_layout.addWidget(self.x_pixel_edit)

        self.y_pixel_edit = QLineEdit(self.path_planning_tab)
        self.y_pixel_edit.setObjectName(u"y_pixel_edit")
        self.y_pixel_edit.setAlignment(Qt.AlignCenter)

        self.pixel_layout.addWidget(self.y_pixel_edit)

        self.z_pixel_edit = QLineEdit(self.path_planning_tab)
        self.z_pixel_edit.setObjectName(u"z_pixel_edit")
        self.z_pixel_edit.setAlignment(Qt.AlignCenter)

        self.pixel_layout.addWidget(self.z_pixel_edit)


        self.verticalLayout_3.addLayout(self.pixel_layout)

        self.world_label = QLabel(self.path_planning_tab)
        self.world_label.setObjectName(u"world_label")
        self.world_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.world_label)

        self.world_layout = QHBoxLayout()
        self.world_layout.setSpacing(2)
        self.world_layout.setObjectName(u"world_layout")
        self.x_world_edit = QLineEdit(self.path_planning_tab)
        self.x_world_edit.setObjectName(u"x_world_edit")
        self.x_world_edit.setAlignment(Qt.AlignCenter)
        self.x_world_edit.setReadOnly(True)

        self.world_layout.addWidget(self.x_world_edit)

        self.y_world_edit = QLineEdit(self.path_planning_tab)
        self.y_world_edit.setObjectName(u"y_world_edit")
        self.y_world_edit.setAlignment(Qt.AlignCenter)
        self.y_world_edit.setReadOnly(True)

        self.world_layout.addWidget(self.y_world_edit)

        self.z_world_edit = QLineEdit(self.path_planning_tab)
        self.z_world_edit.setObjectName(u"z_world_edit")
        self.z_world_edit.setAlignment(Qt.AlignCenter)
        self.z_world_edit.setReadOnly(True)

        self.world_layout.addWidget(self.z_world_edit)


        self.verticalLayout_3.addLayout(self.world_layout)

        self.path_line_1 = QFrame(self.path_planning_tab)
        self.path_line_1.setObjectName(u"path_line_1")
        self.path_line_1.setFrameShape(QFrame.HLine)
        self.path_line_1.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.path_line_1)

        self.parameter_label = QLabel(self.path_planning_tab)
        self.parameter_label.setObjectName(u"parameter_label")
        self.parameter_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.parameter_label)

        self.safe_distance_layout = QHBoxLayout()
        self.safe_distance_layout.setObjectName(u"safe_distance_layout")
        self.safe_distance_label = QLabel(self.path_planning_tab)
        self.safe_distance_label.setObjectName(u"safe_distance_label")
        self.safe_distance_label.setAlignment(Qt.AlignCenter)

        self.safe_distance_layout.addWidget(self.safe_distance_label)

        self.safe_distance_edit = QLineEdit(self.path_planning_tab)
        self.safe_distance_edit.setObjectName(u"safe_distance_edit")
        self.safe_distance_edit.setAlignment(Qt.AlignCenter)

        self.safe_distance_layout.addWidget(self.safe_distance_edit)

        self.safe_distance_layout.setStretch(0, 1)
        self.safe_distance_layout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.safe_distance_layout)

        self.max_needle_depth_layout = QHBoxLayout()
        self.max_needle_depth_layout.setObjectName(u"max_needle_depth_layout")
        self.max_needle_depth_label = QLabel(self.path_planning_tab)
        self.max_needle_depth_label.setObjectName(u"max_needle_depth_label")
        self.max_needle_depth_label.setAlignment(Qt.AlignCenter)

        self.max_needle_depth_layout.addWidget(self.max_needle_depth_label)

        self.max_needle_depth_edit = QLineEdit(self.path_planning_tab)
        self.max_needle_depth_edit.setObjectName(u"max_needle_depth_edit")
        self.max_needle_depth_edit.setAlignment(Qt.AlignCenter)

        self.max_needle_depth_layout.addWidget(self.max_needle_depth_edit)

        self.max_needle_depth_layout.setStretch(0, 1)
        self.max_needle_depth_layout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.max_needle_depth_layout)

        self.max_ablation_radius_layout = QHBoxLayout()
        self.max_ablation_radius_layout.setObjectName(u"max_ablation_radius_layout")
        self.max_ablation_radius_label = QLabel(self.path_planning_tab)
        self.max_ablation_radius_label.setObjectName(u"max_ablation_radius_label")
        self.max_ablation_radius_label.setAlignment(Qt.AlignCenter)

        self.max_ablation_radius_layout.addWidget(self.max_ablation_radius_label)

        self.max_ablation_radius_edit = QLineEdit(self.path_planning_tab)
        self.max_ablation_radius_edit.setObjectName(u"max_ablation_radius_edit")
        self.max_ablation_radius_edit.setAlignment(Qt.AlignCenter)

        self.max_ablation_radius_layout.addWidget(self.max_ablation_radius_edit)

        self.max_ablation_radius_layout.setStretch(0, 1)
        self.max_ablation_radius_layout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.max_ablation_radius_layout)

        self.max_ablation_radius_layout_2 = QHBoxLayout()
        self.max_ablation_radius_layout_2.setObjectName(u"max_ablation_radius_layout_2")
        self.min_distance_label = QLabel(self.path_planning_tab)
        self.min_distance_label.setObjectName(u"min_distance_label")
        self.min_distance_label.setAlignment(Qt.AlignCenter)

        self.max_ablation_radius_layout_2.addWidget(self.min_distance_label)

        self.min_distance_edit = QLineEdit(self.path_planning_tab)
        self.min_distance_edit.setObjectName(u"min_distance_edit")
        self.min_distance_edit.setAlignment(Qt.AlignCenter)

        self.max_ablation_radius_layout_2.addWidget(self.min_distance_edit)

        self.max_ablation_radius_layout_2.setStretch(0, 1)
        self.max_ablation_radius_layout_2.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.max_ablation_radius_layout_2)

        self.pt_spacing_layout = QHBoxLayout()
        self.pt_spacing_layout.setObjectName(u"pt_spacing_layout")
        self.pt_spacing_label = QLabel(self.path_planning_tab)
        self.pt_spacing_label.setObjectName(u"pt_spacing_label")
        self.pt_spacing_label.setAlignment(Qt.AlignCenter)

        self.pt_spacing_layout.addWidget(self.pt_spacing_label)

        self.pt_spacing_edit = QLineEdit(self.path_planning_tab)
        self.pt_spacing_edit.setObjectName(u"pt_spacing_edit")
        self.pt_spacing_edit.setAlignment(Qt.AlignCenter)

        self.pt_spacing_layout.addWidget(self.pt_spacing_edit)

        self.pt_spacing_layout.setStretch(0, 1)
        self.pt_spacing_layout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.pt_spacing_layout)

        self.ps_rate_layout = QHBoxLayout()
        self.ps_rate_layout.setObjectName(u"ps_rate_layout")
        self.ps_rate_label = QLabel(self.path_planning_tab)
        self.ps_rate_label.setObjectName(u"ps_rate_label")
        self.ps_rate_label.setAlignment(Qt.AlignCenter)

        self.ps_rate_layout.addWidget(self.ps_rate_label)

        self.ps_rate_edit = QLineEdit(self.path_planning_tab)
        self.ps_rate_edit.setObjectName(u"ps_rate_edit")
        self.ps_rate_edit.setAlignment(Qt.AlignCenter)

        self.ps_rate_layout.addWidget(self.ps_rate_edit)

        self.ps_rate_layout.setStretch(0, 1)
        self.ps_rate_layout.setStretch(1, 1)

        self.verticalLayout_3.addLayout(self.ps_rate_layout)

        self.path_line_2 = QFrame(self.path_planning_tab)
        self.path_line_2.setObjectName(u"path_line_2")
        self.path_line_2.setFrameShape(QFrame.HLine)
        self.path_line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.path_line_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.body_orientation_rbtn = QRadioButton(self.path_planning_tab)
        self.body_orientation_rbtn.setObjectName(u"body_orientation_rbtn")

        self.horizontalLayout_2.addWidget(self.body_orientation_rbtn)

        self.auto_path_btn = QPushButton(self.path_planning_tab)
        self.auto_path_btn.setObjectName(u"auto_path_btn")

        self.horizontalLayout_2.addWidget(self.auto_path_btn)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.path_line_3 = QFrame(self.path_planning_tab)
        self.path_line_3.setObjectName(u"path_line_3")
        self.path_line_3.setFrameShape(QFrame.HLine)
        self.path_line_3.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_3.addWidget(self.path_line_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.large_checkbox = QCheckBox(self.path_planning_tab)
        self.large_checkbox.setObjectName(u"large_checkbox")

        self.horizontalLayout_4.addWidget(self.large_checkbox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.label_2 = QLabel(self.path_planning_tab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.neddle_num_edit = QLineEdit(self.path_planning_tab)
        self.neddle_num_edit.setObjectName(u"neddle_num_edit")
        self.neddle_num_edit.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.neddle_num_edit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.auto_path_result_edit = QTextEdit(self.path_planning_tab)
        self.auto_path_result_edit.setObjectName(u"auto_path_result_edit")
        self.auto_path_result_edit.setFocusPolicy(Qt.StrongFocus)
        self.auto_path_result_edit.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.auto_path_result_edit)

        self.tabWidget.addTab(self.path_planning_tab, "")
        self.post_eval_tab = QWidget()
        self.post_eval_tab.setObjectName(u"post_eval_tab")
        self.gridLayout_2 = QGridLayout(self.post_eval_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.post_input_btn = QPushButton(self.post_eval_tab)
        self.post_input_btn.setObjectName(u"post_input_btn")

        self.gridLayout_2.addWidget(self.post_input_btn, 0, 0, 1, 1)

        self.post_eval_btn = QPushButton(self.post_eval_tab)
        self.post_eval_btn.setObjectName(u"post_eval_btn")

        self.gridLayout_2.addWidget(self.post_eval_btn, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.post_eval_tab)
        self.label.setObjectName(u"label")

        self.horizontalLayout_3.addWidget(self.label)

        self.eval_result_edit = QLineEdit(self.post_eval_tab)
        self.eval_result_edit.setObjectName(u"eval_result_edit")

        self.horizontalLayout_3.addWidget(self.eval_result_edit)


        self.gridLayout_2.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        self.tumor_eval_btn = QPushButton(self.post_eval_tab)
        self.tumor_eval_btn.setObjectName(u"tumor_eval_btn")

        self.gridLayout_2.addWidget(self.tumor_eval_btn, 3, 0, 1, 1)

        self.message_edit_2 = QTextEdit(self.post_eval_tab)
        self.message_edit_2.setObjectName(u"message_edit_2")
        self.message_edit_2.setReadOnly(True)

        self.gridLayout_2.addWidget(self.message_edit_2, 4, 0, 1, 1)

        self.tabWidget.addTab(self.post_eval_tab, "")

        self.horizontalLayout.addWidget(self.tabWidget)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.view1_layout = QHBoxLayout()
        self.view1_layout.setSpacing(1)
        self.view1_layout.setObjectName(u"view1_layout")
        self.view1 = QOpenGLWidget(self.centralwidget)
        self.view1.setObjectName(u"view1")

        self.view1_layout.addWidget(self.view1)

        self.view1_scrollbar = QScrollBar(self.centralwidget)
        self.view1_scrollbar.setObjectName(u"view1_scrollbar")
        self.view1_scrollbar.setOrientation(Qt.Vertical)

        self.view1_layout.addWidget(self.view1_scrollbar)

        self.view1_layout.setStretch(0, 1)

        self.gridLayout.addLayout(self.view1_layout, 0, 0, 1, 1)

        self.view2_layout = QHBoxLayout()
        self.view2_layout.setSpacing(1)
        self.view2_layout.setObjectName(u"view2_layout")
        self.view2 = QOpenGLWidget(self.centralwidget)
        self.view2.setObjectName(u"view2")

        self.view2_layout.addWidget(self.view2)

        self.view2_scrollbar = QScrollBar(self.centralwidget)
        self.view2_scrollbar.setObjectName(u"view2_scrollbar")
        self.view2_scrollbar.setOrientation(Qt.Vertical)

        self.view2_layout.addWidget(self.view2_scrollbar)

        self.view2_layout.setStretch(0, 1)

        self.gridLayout.addLayout(self.view2_layout, 0, 1, 1, 1)

        self.view3_layout = QHBoxLayout()
        self.view3_layout.setSpacing(1)
        self.view3_layout.setObjectName(u"view3_layout")
        self.view3 = QOpenGLWidget(self.centralwidget)
        self.view3.setObjectName(u"view3")

        self.view3_layout.addWidget(self.view3)

        self.view3_scrollbar = QScrollBar(self.centralwidget)
        self.view3_scrollbar.setObjectName(u"view3_scrollbar")
        self.view3_scrollbar.setOrientation(Qt.Vertical)

        self.view3_layout.addWidget(self.view3_scrollbar)

        self.view3_layout.setStretch(0, 1)

        self.gridLayout.addLayout(self.view3_layout, 1, 0, 1, 1)

        self.view4 = QOpenGLWidget(self.centralwidget)
        self.view4.setObjectName(u"view4")

        self.gridLayout.addWidget(self.view4, 1, 1, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)

        self.horizontalLayout.setStretch(1, 7)

        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1047, 23))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setLayoutDirection(Qt.RightToLeft)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu.menuAction())
        self.menu.addAction(self.import_action)
        self.menu.addAction(self.exit_actiont)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.import_action.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165", None))
        self.exit_actiont.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.import_btn.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165", None))
        self.window_width_label.setText(QCoreApplication.translate("MainWindow", u" \u7a97\u5bbd", None))
        self.window_width_edit.setText("")
        self.window_level_label.setText(QCoreApplication.translate("MainWindow", u" \u7a97\u4f4d", None))
        self.tumor_seg_btn.setText(QCoreApplication.translate("MainWindow", u"\u80bf\u7624\u5206\u5272", None))
        self.lung_trachea_seg_btn.setText(QCoreApplication.translate("MainWindow", u"\u80ba\u3001\u6c14\u7ba1\u5206\u5272", None))
        self.skeleton_seg_btn.setText(QCoreApplication.translate("MainWindow", u"\u9aa8\u9abc\u5206\u5272", None))
        self.vessel_seg_btn.setText(QCoreApplication.translate("MainWindow", u"\u8840\u7ba1\u5206\u5272", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.seg_tab), QCoreApplication.translate("MainWindow", u"\u5206\u5272", None))
        self.pixel_label.setText(QCoreApplication.translate("MainWindow", u"\u56fe\u50cf\u5750\u6807\uff1ax, y, z", None))
        self.world_label.setText(QCoreApplication.translate("MainWindow", u"\u4e16\u754c\u5750\u6807\uff1ax, y, z", None))
        self.parameter_label.setText(QCoreApplication.translate("MainWindow", u"\u9884\u8bbe\u53c2\u6570", None))
        self.safe_distance_label.setText(QCoreApplication.translate("MainWindow", u"\u5b89\u5168\u8fb9\u754c\u8ddd\u79bb\uff08mm\uff09\uff1a", None))
        self.max_needle_depth_label.setText(QCoreApplication.translate("MainWindow", u"\u6700\u5927\u8fdb\u9488\u6df1\u5ea6\uff08mm\uff09\uff1a", None))
        self.max_ablation_radius_label.setText(QCoreApplication.translate("MainWindow", u"\u6700\u5927\u6d88\u878d\u534a\u5f84(mm)\uff1a", None))
        self.min_distance_label.setText(QCoreApplication.translate("MainWindow", u"\u4e0e\u91cd\u8981\u7ec4\u7ec7\u6700\u77ed\u95f4\u8ddd\uff08mm\uff09\uff1a", None))
        self.pt_spacing_label.setText(QCoreApplication.translate("MainWindow", u"\u80bf\u7624\u70b9\u96c6\u91c7\u6837\u95f4\u8ddd\uff08mm\uff09\uff1a", None))
        self.ps_rate_label.setText(QCoreApplication.translate("MainWindow", u"\u76ae\u80a4\u70b9\u96c6\u91c7\u6837\u53c2\u6570\uff1a", None))
        self.body_orientation_rbtn.setText(QCoreApplication.translate("MainWindow", u"\u4ef0\u5367\u4f4d", None))
        self.auto_path_btn.setText(QCoreApplication.translate("MainWindow", u"\u81ea\u52a8\u8def\u5f84\u89c4\u5212", None))
        self.large_checkbox.setText(QCoreApplication.translate("MainWindow", u"\u59d1\u606f\u6027\u6d88\u878d", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\u9488\u6570\uff1a", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.path_planning_tab), QCoreApplication.translate("MainWindow", u"\u8def\u5f84\u89c4\u5212", None))
        self.post_input_btn.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u5165", None))
        self.post_eval_btn.setText(QCoreApplication.translate("MainWindow", u"\u8bc4\u4f30", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u7ed3\u679c\uff1a", None))
        self.tumor_eval_btn.setText(QCoreApplication.translate("MainWindow", u"\u80bf\u7624\u7597\u6548\u8bc4\u4f30", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.post_eval_tab), QCoreApplication.translate("MainWindow", u"\u672f\u540e\u8bc4\u4f30", None))
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
    # retranslateUi

