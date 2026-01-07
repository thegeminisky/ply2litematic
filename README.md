# 3DGS to Minecraft Litematic Converter
### 3D 高斯泼溅转 Minecraft 投影工具 (For Apple ML-Sharp)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Minecraft](https://img.shields.io/badge/Minecraft-Litematica-green)](https://www.curseforge.com/minecraft/mc-mods/litematica)
[![Upstream](https://img.shields.io/badge/Based%20on-Apple%20ML--Sharp-black)](https://github.com/apple/ml-sharp)

这是一个 Python 工具，专为处理由 **[Apple ML-Sharp](https://github.com/apple/ml-sharp)** 项目生成的 3D Gaussian Splatting (.ply) 模型而设计。

它能读取 ML-Sharp 生成的点云数据（包括位置、球谐光照系数 SH、不透明度），将其体素化并转换为 Minecraft 的 **.litematic** 投影文件，让你在游戏中轻松复刻 AI 重建的 3D 场景。

## ✨ 主要功能

* **完美适配 ML-Sharp**：针对该项目输出的 PLY 格式（`f_dc` 色彩系数）进行了专门适配。
* **智能体素化**：将连续的高斯点云转换为离散的 Minecraft 方块网格。
* **自动色彩匹配**：内置丰富的方块调色板（混凝土、陶瓦、木材、石材等），自动计算最佳颜色。
* **色彩增强**：支持饱和度倍增，解决 AI 生成模型在 MC 中色彩发灰的问题。
* **坐标修正**：支持 Y 轴反转和 X 轴镜像，自动校正模型倒置问题。

## 🛠️ 环境依赖

在运行脚本之前，请确保已安装 Python 3.11 或更高版本，并安装以下依赖库：

```bash
pip install numpy plyfile litemapy
````

  * `numpy`: 用于矩阵运算和球谐系数(SH)到RGB的转换。
  * `plyfile`: 用于解析二进制 PLY 文件。
  * `litemapy`: 用于生成 Minecraft Litematic 格式文件。

## 🚀 工作流程与使用方法

### 第一步：生成模型

首先，请参考 **[Apple ML-Sharp](https://github.com/apple/ml-sharp)** 的官方文档，导出一个 `.ply` 格式的高斯泼溅模型文件。

### 第二步：配置转换器

1.  将导出的 `.ply` 文件复制到本脚本所在的目录。

2.  打开 `ply2litematic.py`，修改配置区域的文件名：

    ```python
    INPUT_PLY = "output_from_ml_sharp.ply"  # 修改为你的文件名
    OUTPUT_NAME = "my_mc_build"             # 输出文件名，不加后缀
    ```

### 第三步：运行转换

在终端中运行：

```bash
python ply2litematic.py
```

### 第四步：导入游戏

1.  脚本会在同目录下生成 `.litematic` 文件。
2.  将文件放入 Minecraft 的 `.minecraft/schematics/` 文件夹。
3.  在游戏中使用 Litematica Mod 加载并粘贴投影。

## ⚙️ 关键参数调整

由于 ML-Sharp 生成的模型可能在尺度和密度上有所不同，你可能需要调整以下参数（位于代码顶部）：

| 参数名 | 推荐值 | 说明 |
| :--- | :--- | :--- |
| **`SCALE_FACTOR`** | `100.0` | **缩放比例**。如果生成的建筑太小，请尝试调大此数值（如 150 或 200），反之亦然。 |
| **`INVERT_Y_AXIS`** | `True` | **Y轴反转**。解决建筑倒置问题。 |
| **`INVERT_X_AXIS`** | `True` | **X轴反转**。解决建筑左右镜像问题。 |
| **`DENSITY_THRESHOLD`** | `0.2` | **密度阈值**。如果建筑看起来像“幽灵”太透了，请调小此值（如 0.1）；如果噪点太多，请调大（如 0.3）。 |
| **`MIN_OPACITY_CUTOFF`** | `0.01` | **去除背景噪点**。忽略不透明度低于此值的点。 |
| **`SATURATION_BOOST`** | `1.5` | **色彩增强**。建议保持在 1.5 以上，以获得更鲜艳的视觉效果。 |
| **`MIN_NEIGHBORS`** | `1` | **孤立点去除**。如果一个方块周围的邻居少于此数值，则将其视为噪点删除。建议设为 1 或 2 以保持建筑整洁。 |

## 🎨 支持的方块材质

本工具会自动从以下材质中选择最接近的颜色：

  * **混凝土 (Concrete)**：用于表达鲜艳纯色。
  * **陶瓦 (Terracotta)**：用于表达自然、低饱和度的颜色。
  * **原木与木板 (Woods)**：用于表达纹理丰富的棕色、红色系。
  * **石材 (Stones)**：用于表达灰度结构。

## 📝 License

本项目采用 [GPL-3.0 协议](LICENSE) 开源。
这意味着你可以自由地运行、研究、共享和修改本软件，但如果你分发修改后的版本，必须同样基于 GPL-3.0 协议开源。
