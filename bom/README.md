# BOM与采购状态

这里是当前机械试装版的物料清单，不是已冻结的整机电子BOM。

- [PRINT_MANIFEST.csv](PRINT_MANIFEST.csv)：10个主体打印件与独立STEP/STL路径；另有2个试片。
- [BOM_FASTENERS.csv](BOM_FASTENERS.csv)：当前名义安装量，共38颗M3与10颗M2螺钉，配套螺母和垫片；134个金属件实例。原厂透明盖6颗M2螺钉不要重复采购。
- [BOM_PURCHASED.csv](BOM_PURCHASED.csv)：推进器、舱件、相机、浮材、衬垫与绑带；穿舱件、配重等未冻结项已标记。
- [FASTENER_INSTANCES.csv](FASTENER_INSTANCES.csv)：48颗螺钉的头部基准位置。
- [KEY_HOLES.csv](KEY_HOLES.csv)：关键孔位与坐标约定。
- [component-confirmation.csv](component-confirmation.csv)：记录真实型号、外形、重量、接头、功耗及实测结果。

先买1台推进器和匹配双向电调，验证两个试片；电机螺纹孔深未测前不能按名义螺钉长度硬拧。电池、四电调、控制器与USB主机需先完成机舱空间/温升核对，之后再冻结电子BOM。
