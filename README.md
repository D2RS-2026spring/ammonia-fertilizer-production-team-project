# ammonia-fertilizer-production-team-project
分散式氨肥生产小组作业
## 小组成员
- 刘  慧2025303120075
- 李亚茹2025303120104
- 王焱栋2025303120131
- 高  彬2025303120156
- 倪  龙2025303110088
## 项目信息
- 论文标题：Cost-competitive decentralized ammonia fertilizer production can increase food security
- 发表期刊/时间：Nature Food，16 May 2024
- 论文链接：https://doi.org/10.1038/s43016-024-00979-y
- 代码和数据集链接：https://doi.org/10.5281/zenodo.815514
## 复现目标与核心内容
本项目完整复现了原研究的计算逻辑与可视化结果，核心目标包括：
1.  完成 **`grid`（电网供电）** 与 **`agrivolt`（农光互补供电）** 两种系统的氨肥成本（LCOA）计算
2.  生成与文献一致的成本密度分布曲线、供需平衡曲线
3.  验证不同年份（2020/2030/2050）、不同技术路线的成本趋势差异
## 项目结构说明
- `input_data/` :数据预处理脚本
- `calculation/`:核心计算脚本（需求聚合、成本计算、直方图、敏感性分析等）
- `plot/`:可视化脚本，输出成本分解、累计供需等图表
- `figure/`:复现出的图表内容
## 环境配置与依赖安装
### 1. 创建独立虚拟环境
```bash
conda create -n ammonia_repro python=3.9.12 -y
conda activate ammonia_repro
```
### 2. 安装核心依赖
```bash
pip install numpy pandas matplotlib geopandas rasterio scipy seaborn
conda install -c conda-forge rioxarray -y
conda install -c conda-forge numba -y
conda install -c conda-forge openpyxl -y
conda install -c conda-forge pyDOE -y
conda install -c conda-forge salib -y
```
### 3. 关键环境配置（解决投影错误）
```bash
import os
# 替换为你本地 Conda 环境的 proj 路径
os.environ['PROJ_LIB'] = r'F:\anaconda3\envs\ammonia_repro\Library\share\proj'

# 配置完成后再导入 geopandas
import geopandas as gpd
```
### ⚠️ 大文件说明
> 由于 GitHub 对单文件大小限制为 100MB，项目中部分数据文件（.csv/.geojson/.tif等）体积超过限制，未上传至仓库。

- **获取方式**：从论文原始数据链接下载：[https://doi.org/10.5281/zenodo.815514](https://doi.org/10.5281/zenodo.8155141)
- **使用方法**：将下载后的文件夹整体替换项目中的同名文件夹，即可完整运行所有代码。
