import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import time

# 创建图表布局
fig = make_subplots(rows=1, cols=1)

# 初始化数据
x = np.linspace(0, 2 * np.pi, 100)
y = np.sin(x)
trace = go.Scatter(x=x, y=y, mode='lines', line=dict(color='royalblue'))

# 添加数据到图表
fig.add_trace(trace)

# 更新数据
for _ in range(30):
    y = np.sin(x + _ * 0.1)
    with fig.batch_update():
        fig.data[0].y = y
    time.sleep(0.1)

# 显示图表
fig.show()
