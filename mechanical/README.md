# 机械结构与可编辑源文件

`build.py`与`parameters.json`是原始尺寸驱动源；原厂参考几何位于`supplier/`。`stl/`是已落床的10个主体打印文件；`step_parts/`是总装坐标下的10个独立可编辑实体；`fit_coupons/`包含两个电机接口试片。`assembly_meshes/`用于总装和仿真重建。

机械几何、单位mm、X前/Y左/Z上。推进器与相机/压力件为商用参考，禁止把参考电机或压力件当作本项目打印件。[完整装配说明](../docs/assembly.md)与[验收边界](../docs/acceptance.md)。

源CAD的几何哈希、0干涉与48条工具通道记录在`GEOMETRY_CHECKS.json`；这不是强度/耐压认证。`STRENGTH_SCREEN.json`只是局部理想截面估算。Onshape后端盖的曲面导入限制见[历史回导报告](../validation/onshape/ONSHAPE_ROUNDTRIP.json)。

## 总装配置

默认不安装顶部浮材及绑带，外包213×210×148mm。选装浮力模块后外包213×210×184.7mm；最大尺寸不含待定线束、接头与绑带锁头。

| 配置 | 常规总装 | 含名义金属件 |
|---|---|---|
| 标准装配 | [simple-rov.step](assemblies/simple-rov.step) | [simple-rov-with-fasteners.step](assemblies/simple-rov-with-fasteners.step) |
| 加装浮力模块 | [simple-rov-with-buoyancy.step](assemblies/simple-rov-with-buoyancy.step) | [simple-rov-buoyancy-with-fasteners.step](assemblies/simple-rov-buoyancy-with-fasteners.step) |

[configurations.json](configurations.json)列出尺寸、包围盒和所含零件；[parts.json](parts.json)保留所有零件及选装标记。10个主体打印件两种配置通用，浮材不打印。历史Onshape总装含浮材，当前默认配置以本仓库为准。详见[浮力说明](../docs/buoyancy.md)和[多视角图库](../docs/gallery.md)。
