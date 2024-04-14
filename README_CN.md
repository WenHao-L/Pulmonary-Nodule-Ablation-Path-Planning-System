# 肺结节消融路径规划系统

中文 | [英文](README.md) 

该仓库提供了一个基于 Python、VTK 的实现的 CT 影像肺结节消融路径规划系统，包括肺部器官（肺、骨骼、气管、血管）和肺结节的分割和三维重建（面绘制）；微波消融进针路线规划算法；微波消融温度场模拟算法；消融术后评估。

#### ⚠️ 该项目现已暂停维护，项目还比较初级，存在许多不足之处，欢迎提issue，后续看情况继续改进（大概也许可能有空的话应该会吧。。。）

<div align="center">
  <img src="doc/img/seg.png" alt="seg" />
</div>
<div align="center">
  <img src="doc/img/path_planing.png" alt="path_planing" />
</div>
<div align="center">
  <img src="doc/img/3d.png" alt="3d" />
</div>
<div align="center">
  <img src="doc/img/range.png" alt="range" />
</div>

# 项目结构
- doc
    - img: `项目图片`
- src
    - main_window.py `主窗口功能实现`
    - mouse_interactor_style.py `鼠标交互事件`
    - seg.py `分割算法`
- ui
    - path_planning.ui `界面文件`
    - ui.py `界面代码`
- utils
    - dcm2nii.py `DICON转NIFTI`
    - dilate.py `形态学操作`
    - eval_tumor_efficacy.py `术后评估`
    - extract_point.py `提取点集`
    - is_pareto_front.py `判断帕累托前言`
    - kmeans.py `聚类算法`
    - mc.py `面绘算法`
    - path_design.py `路径规划算法`
    - power_time.py `消融时间功率算法`
    - reader.py `文件读取`
    - resample.py `重采样`
- main.py `主函数入口`
- main.spec `打包用`
- README.md `自述文件`
- requirements.txt `依赖包`

# 开始使用
1、确保您已安装所需的库：

```
pip install -r requirements.txt
```

2、nnUNet 配置：

参考[官方仓库](https://github.com/MIC-DKFZ/nnUNet)，配置nnUNet环境，并将 nnUNet 代码仓放在主目录下

3、运行：

```
python main.py
```

# 友情链接
[Lung Organ Segmentation: A Comprehensive Python Project](https://github.com/skyous779/Lung-Organ-Segmentation)

# 免责声明：
- **仅供学习和研究使用：** 本项目仅用于学习和研究目的。对于任何非法使用造成的后果，开发者概不负责。

- **不提供医疗建议：** 本项目中的任何信息都不应被视为医疗建议。在做出任何医疗决定之前，请咨询专业医生。