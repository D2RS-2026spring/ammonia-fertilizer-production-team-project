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
- `data/` :存放项目原始数据文件
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
