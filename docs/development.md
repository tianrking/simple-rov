# 开发、复建与发布

所有命令从仓库根目录运行，推荐Python3.12虚拟环境。安装用途依赖：`requirements/sim.txt`、`requirements/cad.txt`、`requirements/docs.txt`。不要把虚拟环境、密钥、个人配置或运行日志提交到Git。

## 仿真

`python simulation/mujoco/run.py --viewer --manual --seconds 300`使用独立GLFW驾驶窗口；普通Python在Mac主线程上创建窗口。自动演示的原生MuJoCo查看器在Mac可通过`python simulation/mujoco/launch_macos.py --seconds 120`启动，启动器按需补齐所选虚拟环境的libpython链接。它不修改系统Python。

`--output-dir runs/demo`固定本次输出位置；省略时使用UTC时间戳目录。`verify.py`检查CAD推力映射、运动符号、定深和姿态恢复，`verify_manual.py`检查键盘目标/释放行为，`verify_driving_window.py`创建原生OpenGL窗口测试回调隔离及帧缓冲（需本地桌面）。后者不是操作系统级键盘事件注入。

## CAD

源几何位于`mechanical/build.py`，参数在`mechanical/parameters.json`。原厂STEP在`supplier/`，保持版本来源。构建命令见根目录README。几何检查涉及大量布尔运算，速度取决于平台。`export_metadata.py`重新核对打印导出，更新BOM和接口资料。

原有数字报告与源文件哈希配套；改动源参数后旧报告不再代表新几何，必须重新生成、验证和更新报告。不要为了让检查通过只改报告中的哈希。

## 文档

Markdown是阅读和编辑入口；PDF生成内容在`tools/docs/content.py`，渲染代码在同目录。文档变更时保持两者语义一致。

```bash
python tools/docs/make_figures.py
python tools/docs/build_pdf.py
python tools/docs/build_web.py
```

PDF/图示需要TrueType中文字体。Mac可自动使用系统STHeiti；Linux可安装文泉驿正黑并设置`SROV_CJK_FONT=/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`，或指定其他可读TTF/TTC。字体不随仓库分发。用`pdftoppm`渲染PDF逐页检查，不以文本抽取替代视觉检查。

## 完整性与发布

```bash
python tools/validate_repository.py
python tools/update_manifest.py
python tools/validate_repository.py --manifest
python tools/build_release.py
```

清单覆盖项目资料，排除.git、虚拟环境、缓存与runs。发布包输出在`runs/releases/`，不会自动提交；变更版本时同步更新STATUS和CHANGELOG。GitHub Actions执行仓库完整性与无窗口仿真检查，不验证实物可靠性。

`requirements/lock-macos-py312.txt`记录本机完整验证环境（含CAD与文档依赖），属于macOS/Python3.12快照；Linux CI使用requirements/sim.txt，不假设跨平台原生库完全相同。CSV统一LF换行，发布哈希以Git检出后的字节为准。
