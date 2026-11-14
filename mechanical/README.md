# 机械工程 / V5-01

`build.py`与`parameters.json`是原始尺寸驱动源；原厂参考几何位于`supplier/`。`stl/`是已落床的10个主体打印文件；`step_parts/`是总装坐标下的10个独立可编辑实体；`fit_coupons/`包含两个电机接口试片。`assembly_meshes/`用于总装和仿真重建。

机械几何、单位mm、X前/Y左/Z上。推进器与相机/压力件为商用参考，禁止把参考电机或压力件当作本项目打印件。[完整装配说明](../docs/assembly.md)与[验收边界](../docs/acceptance.md)。

源CAD的几何哈希、0干涉与48条工具通道记录在`GEOMETRY_CHECKS.json`；这不是强度/耐压认证。`STRENGTH_SCREEN.json`只是局部理想截面估算。Onshape后端盖的曲面导入限制见`ONSHAPE_ROUNDTRIP.json`。
