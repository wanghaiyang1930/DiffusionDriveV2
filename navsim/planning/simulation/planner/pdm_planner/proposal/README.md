

### 路径列表（lateral_proposals）
含义：一组横向路径候选，每个路径是一个 PDMPath 对象。
作用：
表示车辆在空间中的位置和方向（x, y, θ）
每个路径是一条可插值的几何路径，包含离散的 StateSE2 点序列
代表不同的横向选择，例如：
保持在车道中心
稍微向左偏移
稍微向右偏移
变道路径等
特点：
PDMPath 提供路径插值、投影、长度计算等功能
路径是静态的空间几何形状，不包含速度信息

### 纵向策略（longitudinal_policies）
含义：BatchIDMPolicy 对象，包含多个 IDM（Intelligent Driver Model）策略。
*作用*：
控制车辆沿路径的纵向运动（速度、加速度）
每个策略有不同的参数组合：
target_velocity: 目标速度
min_gap_to_lead_agent: 与前车的最小距离
headway_time: 跟车时距
accel_max / decel_max: 最大加速度/减速度
speed_limit_fraction: 限速比例
特点：
可以批量管理多个策略（例如保守、正常、激进）
通过 propagate() 方法根据前车状态计算下一时刻的速度和位置
通过 update() 方法根据当前限速更新目标速度
组合使用
PDMProposalManager 将两者组合：
总 proposal 数 = 横向路径数 × 纵向策略数
每个 proposal 代表一个完整的候选方案：选择某条横向路径，并沿该路径应用某个纵向策略
规划器会评估这些组合，选择最优方案
举例：如果有 5 条横向路径和 3 种纵向策略，会生成 15 个 proposal，覆盖不同的路径与速度组合。

这行代码表示的是什么意思？ (v_agent * (v_agent - v_lead)) / (2 * np.sqrt(accel_max * decel_max))

解释这行代码在 IDM 模型中的含义：
这行代码是 IDM 模型中计算期望跟车距离 s_star 的第三项，表示速度差带来的额外安全距离。
公式含义
(v_agent * (v_agent - v_lead)) / (2 * np.sqrt(accel_max * decel_max))
物理意义
这一项表示：当自车速度大于前车速度时，需要额外保持的安全距离，用于在紧急情况下安全减速。
分解说明
(v_agent - v_lead)：速度差
正值：自车更快，需要更多安全距离
零或负值：自车不快于前车，该项贡献小或为负
v_agent * (v_agent - v_lead)：速度差与自车速度的乘积
反映相对速度带来的风险
2 * np.sqrt(accel_max * decel_max)：归一化因子
sqrt(accel_max * decel_max) 可视为“有效减速度能力”
除以 2 用于单位转换和模型校准
实际例子
假设：
v_agent = 20 m/s（72 km/h）
v_lead = 15 m/s（54 km/h）
accel_max = 2 m/s²
decel_max = 4 m/s²
计算：
额外距离 = (20 * (20 - 15)) / (2 * sqrt(2 * 4))         = (20 * 5) / (2 * sqrt(8))         = 100 / (2 * 2.83)         = 100 / 5.66         ≈ 17.7 米
这意味着当自车比前车快 5 m/s 时，需要额外约 17.7 米的安全距离。
在完整公式中的作用
s_star 由三部分组成：
min_gap_to_lead_agent：最小静态距离
v_agent * headway_time：基于时距的动态距离
(v_agent * (v_agent - v_lead)) / (2 * np.sqrt(accel_max * decel_max))：速度差带来的额外安全距离
设计目的
当自车更快时，增加安全距离
当自车不快于前车时，减少额外距离
根据车辆的加速/减速能力调整
这是 IDM 模型的核心安全机制之一，确保在接近前车时保持足够的安全距离。