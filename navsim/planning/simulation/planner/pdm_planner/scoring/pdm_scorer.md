# PDMScorer 类说明文档

## 一、类概述

`PDMScorer` 是 PDM (Planner Decision Model) 规划器中的**轨迹评分器**，用于对候选轨迹（proposals）进行综合评估。该类重新实现了 nuPlan 的闭环评估指标（closed-loop metrics），通过多个维度的指标来评估轨迹的质量。

### 核心功能
- 评估候选轨迹的安全性（碰撞检测、可行驶区域合规性）
- 评估轨迹的舒适性（加速度、转向率等）
- 评估轨迹的进度（沿中心线的行驶距离）
- 评估轨迹的交通规则合规性（行驶方向、TTC等）

---

## 二、类结构

### 2.1 初始化参数

```python
def __init__(
    self,
    proposal_sampling: TrajectorySampling,  # 轨迹采样参数
    config: PDMScorerConfig = PDMScorerConfig(),  # 评分器配置
    vehicle_parameters: VehicleParameters = get_pacifica_parameters(),  # 车辆参数
)
```

**参数说明：**
- `proposal_sampling`: 定义轨迹的时间步数和采样间隔
- `config`: 包含各项指标的权重和阈值配置
- `vehicle_parameters`: 车辆物理参数（用于计算车辆边界框）

### 2.2 配置类：PDMScorerConfig

```python
@dataclass
class PDMScorerConfig:
    # 加权指标权重
    progress_weight: float = 5.0          # 进度权重
    ttc_weight: float = 5.0               # 碰撞时间权重
    comfortable_weight: float = 2.0        # 舒适性权重
    driving_direction_weight: float = 0.0  # 行驶方向权重
    
    # 阈值参数
    driving_direction_horizon: float = 1.0                    # 行驶方向检查时间范围 [s]
    driving_direction_compliance_threshold: float = 2.0       # 行驶方向合规阈值 [m]
    driving_direction_violation_threshold: float = 6.0        # 行驶方向违规阈值 [m]
    stopped_speed_threshold: float = 5e-03                    # 停止速度阈值 [m/s]
    progress_distance_threshold: float = 5.0                  # 进度距离阈值 [m]
```

---

## 三、score_proposals 函数详解

### 3.1 函数签名

```python
def score_proposals(
    self,
    states: npt.NDArray[np.float64],
    observation: PDMObservation,
    centerline: PDMPath,
    route_lane_ids: List[str],
    drivable_area_map: PDMDrivableMap,
) -> npt.NDArray[np.float64]
```

### 3.2 输入参数详细分析

#### 1. `states: npt.NDArray[np.float64]`
**形状：** `(n_proposals, n_horizon + 1, StateIndex.size())`

**含义：** 所有候选轨迹的状态数组表示

**维度说明：**
- **第0维 (n_proposals)**: 候选轨迹的数量
- **第1维 (n_horizon + 1)**: 时间步数（包括初始状态）
  - `n_horizon = proposal_sampling.num_poses`
  - 例如：如果 `num_poses = 80`，则时间步数为 81（0 到 80）
- **第2维 (StateIndex.size() = 11)**: 每个时间步的状态向量

**状态向量包含的字段（按索引顺序）：**
```python
StateIndex._X = 0                    # X坐标 [m]
StateIndex._Y = 1                    # Y坐标 [m]
StateIndex._HEADING = 2              # 航向角 [rad]
StateIndex._VELOCITY_X = 3           # X方向速度 [m/s]
StateIndex._VELOCITY_Y = 4           # Y方向速度 [m/s]
StateIndex._ACCELERATION_X = 5       # X方向加速度 [m/s²]
StateIndex._ACCELERATION_Y = 6       # Y方向加速度 [m/s²]
StateIndex._STEERING_ANGLE = 7       # 转向角 [rad]
StateIndex._STEERING_RATE = 8        # 转向角速度 [rad/s]
StateIndex._ANGULAR_VELOCITY = 9     # 角速度 [rad/s]
StateIndex._ANGULAR_ACCELERATION = 10 # 角加速度 [rad/s²]
```

**示例：**
```python
# 假设有 100 个候选轨迹，每个轨迹有 81 个时间步
states.shape = (100, 81, 11)

# 访问第 i 个轨迹在第 t 个时间步的状态
state = states[i, t, :]
x = states[i, t, StateIndex.X]
y = states[i, t, StateIndex.Y]
heading = states[i, t, StateIndex.HEADING]
```

---

#### 2. `observation: PDMObservation`
**类型：** `PDMObservation` 对象

**含义：** PDM 的观察类，包含未来时间步的占用地图（occupancy maps）

**主要属性：**
- `_occupancy_maps`: 时间序列的占用地图列表
  - 每个时间步包含该时刻所有障碍物的占用区域
  - 通过 `observation[time_idx]` 访问特定时间步的占用地图
- `unique_objects`: 所有跟踪对象的唯一字典（token → TrackedObject）
- `collided_track_ids`: 已碰撞对象的轨迹 ID 列表
- `red_light_token`: 红色交通灯的标识符

**包含的障碍物类型：**
- **静态对象**：道路上的静态障碍物（几何形状固定）
- **动态对象**：车辆、行人等可移动对象（根据速度预测未来位置）
- **交通灯**：沿自车路线的红色交通灯（作为占用区域处理）

**用途：**
- 检测轨迹与障碍物的碰撞
- 计算时间到碰撞（TTC）指标
- 判断轨迹的安全性

---

#### 3. `centerline: PDMPath`
**类型：** `PDMPath` 对象

**含义：** 中心线路径，用于计算轨迹沿路径的进度

**主要方法：**
- `project(points)`: 将点投影到路径上，返回沿路径的距离
- `interpolate(distances)`: 根据沿路径的距离插值得到 (x, y, θ) 状态
- `length`: 路径总长度

**用途：**
- 计算轨迹沿中心线的**进度（progress）**指标
- 评估轨迹是否沿着预期路径行驶

**示例：**
```python
# 计算轨迹起点和终点在中心线上的投影距离
start_point = Point(x_start, y_start)
end_point = Point(x_end, y_end)
progress = centerline.project([start_point, end_point])
# progress[0] 是起点距离，progress[1] 是终点距离
# 进度 = progress[1] - progress[0]
```

---

#### 4. `route_lane_ids: List[str]`
**类型：** `List[str]`

**含义：** 包含在路线上的车道 ID 列表

**用途：**
- 识别哪些车道属于规划路线
- 判断轨迹是否在正确的车道上行驶
- 检测是否进入对向车道（oncoming traffic）

**示例：**
```python
route_lane_ids = ["lane_123", "lane_456", "lane_789"]
```

---

#### 5. `drivable_area_map: PDMDrivableMap`
**类型：** `PDMDrivableMap` 对象（继承自 `PDMOccupancyMap`）

**含义：** 可行驶区域多边形的占用地图

**包含的地图元素类型：**
- `SemanticMapLayer.ROADBLOCK`: 道路块
- `SemanticMapLayer.INTERSECTION`: 交叉路口
- `SemanticMapLayer.DRIVABLE_AREA`: 可行驶区域
- `SemanticMapLayer.CARPARK_AREA`: 停车场区域
- `SemanticMapLayer.LANE`: 车道
- `SemanticMapLayer.LANE_CONNECTOR`: 车道连接器

**主要方法：**
- `points_in_polygons(coords)`: 检查点是否在多边形内
- `get_indices_of_map_type(layers)`: 获取特定类型地图元素的索引
- `is_in_layer(point, layer)`: 检查点是否在特定图层中

**用途：**
- 检测轨迹是否在可行驶区域内（drivable area compliance）
- 检测轨迹是否跨越多个车道（multiple lanes）
- 检测轨迹是否进入对向车道（oncoming traffic）

---

### 3.3 输出结果详细分析

#### 返回值：`npt.NDArray[np.float64]`
**形状：** `(n_proposals,)`

**含义：** 每个候选轨迹的综合得分数组

**分数范围：** `[0.0, 1.0]`（理论上，实际可能略有超出）

**评分机制：**

1. **乘法指标（Multiplicative Metrics）**：
   - 这些指标是**硬约束**，违反则分数为 0
   - `NO_COLLISION`: 无碰撞分数（0.0, 0.5, 或 1.0）
   - `DRIVABLE_AREA`: 可行驶区域合规性（0.0 或 1.0）
   - 乘法指标得分 = `NO_COLLISION × DRIVABLE_AREA`

2. **加权指标（Weighted Metrics）**：
   - 这些指标是**软约束**，通过加权平均计算
   - `PROGRESS`: 沿中心线的进度（归一化到 [0, 1]）
   - `TTC`: 时间到碰撞（0.0 或 1.0）
   - `COMFORTABLE`: 舒适性（0.0 或 1.0）
   - `DRIVING_DIRECTION`: 行驶方向合规性（0.0, 0.5, 或 1.0）
   - 加权指标得分 = `(w1×PROGRESS + w2×TTC + w3×COMFORTABLE + w4×DRIVING_DIRECTION) / (w1+w2+w3+w4)`

3. **最终得分**：
   ```python
   final_score = 乘法指标得分 × 加权指标得分
   ```

**示例：**
```python
# 假设有 100 个候选轨迹
scores = scorer.score_proposals(states, observation, centerline, route_lane_ids, drivable_area_map)
# scores.shape = (100,)
# scores[i] 是第 i 个轨迹的得分

# 找到得分最高的轨迹
best_proposal_idx = np.argmax(scores)
best_score = scores[best_proposal_idx]
```

---

## 四、评分流程

`score_proposals` 函数的执行流程如下：

```
1. 初始化与数据准备 (_reset)
   ├─ 保存输入数据
   ├─ 计算车辆边界框坐标 (_ego_coords)
   └─ 生成车辆多边形 (_ego_polygons)

2. 计算车辆区域 (_calculate_ego_area)
   ├─ 检测是否在多个车道内
   ├─ 检测是否在非可行驶区域
   └─ 检测是否在对向车道

3. 计算乘法指标
   ├─ 无碰撞检测 (_calculate_no_at_fault_collision)
   └─ 可行驶区域合规性 (_calculate_drivable_area_compliance)

4. 计算加权指标
   ├─ 进度 (_calculate_progress)
   ├─ 时间到碰撞 (_calculate_ttc)
   ├─ 舒适性 (_calculate_is_comfortable)
   └─ 行驶方向合规性 (_calculate_driving_direction_compliance)

5. 聚合得分 (_aggregate_scores)
   ├─ 计算乘法指标得分
   ├─ 归一化进度指标
   ├─ 计算加权指标得分
   └─ 计算最终得分 = 乘法指标 × 加权指标
```

---

## 五、各项指标详解

### 5.1 乘法指标（硬约束）

#### NO_COLLISION（无碰撞）
- **检测方法**：检查车辆多边形是否与障碍物相交
- **碰撞分类**：
  - `ACTIVE_FRONT_COLLISION`: 主动前方碰撞
  - `STOPPED_TRACK_COLLISION`: 与静止物体碰撞
  - `ACTIVE_LATERAL_COLLISION`: 主动侧向碰撞（仅在多车道或非可行驶区域时算作责任）
- **评分规则**：
  - 无碰撞：1.0
  - 与智能体（车辆、行人等）碰撞：0.0
  - 与非智能体（静态物体）碰撞：0.5

#### DRIVABLE_AREA（可行驶区域合规性）
- **检测方法**：检查车辆边界框的四个角是否都在可行驶区域内
- **评分规则**：
  - 完全在可行驶区域内：1.0
  - 任何时刻离开可行驶区域：0.0

---

### 5.2 加权指标（软约束）

#### PROGRESS（进度）
- **计算方法**：计算轨迹起点和终点在中心线上的投影距离差
- **归一化**：除以所有轨迹中的最大进度值
- **权重**：默认 5.0

#### TTC（Time To Collision，时间到碰撞）
- **计算方法**：预测未来 1 秒内的车辆位置，检查是否与障碍物碰撞
- **评分规则**：
  - 无碰撞风险：1.0
  - 有碰撞风险：0.0
- **权重**：默认 5.0

#### COMFORTABLE（舒适性）
- **计算方法**：检查加速度、转向率等是否在舒适范围内
- **评分规则**：
  - 所有时间步都舒适：1.0
  - 任何时间步不舒适：0.0
- **权重**：默认 2.0

#### DRIVING_DIRECTION（行驶方向合规性）
- **计算方法**：计算在对向车道上的行驶距离
- **评分规则**：
  - 距离 < 2m：1.0（合规）
  - 距离 2-6m：0.5（部分违规）
  - 距离 > 6m：0.0（严重违规）
- **权重**：默认 0.0（通常不使用）

---

## 六、使用示例

```python
from navsim.planning.simulation.planner.pdm_planner.scoring.pdm_scorer import PDMScorer, PDMScorerConfig
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling

# 1. 创建评分器
proposal_sampling = TrajectorySampling(
    num_poses=80,
    interval_length=0.1  # 100ms
)
config = PDMScorerConfig(
    progress_weight=5.0,
    ttc_weight=5.0,
    comfortable_weight=2.0
)
scorer = PDMScorer(
    proposal_sampling=proposal_sampling,
    config=config
)

# 2. 准备输入数据
# states: (n_proposals, 81, 11) - 候选轨迹状态
# observation: PDMObservation - 环境观察
# centerline: PDMPath - 中心线路径
# route_lane_ids: List[str] - 路线车道ID
# drivable_area_map: PDMDrivableMap - 可行驶区域地图

# 3. 计算得分
scores = scorer.score_proposals(
    states=states,
    observation=observation,
    centerline=centerline,
    route_lane_ids=route_lane_ids,
    drivable_area_map=drivable_area_map
)

# 4. 选择最佳轨迹
best_idx = np.argmax(scores)
print(f"最佳轨迹索引: {best_idx}, 得分: {scores[best_idx]}")

# 5. 可选：查询碰撞时间
if scores[best_idx] > 0:
    collision_time = scorer.time_to_at_fault_collision(best_idx)
    ttc_time = scorer.time_to_ttc_infraction(best_idx)
    print(f"碰撞时间: {collision_time}s, TTC违规时间: {ttc_time}s")
```

---

## 七、注意事项

1. **输入数据格式**：
   - `states` 必须是 3 维数组，且第二维必须等于 `proposal_sampling.num_poses + 1`
   - 第三维必须等于 `StateIndex.size()` (即 11)

2. **性能考虑**：
   - 评分过程涉及大量的几何计算（多边形相交检测等）
   - 对于大量候选轨迹，计算可能较慢

3. **分数解释**：
   - 分数为 0 不一定意味着轨迹完全不可行，可能是某个硬约束未满足
   - 分数越高，轨迹质量越好，但需要结合具体场景判断

4. **配置调优**：
   - 可以通过调整 `PDMScorerConfig` 中的权重来平衡不同指标的重要性
   - 例如，如果更关注安全性，可以增加 `ttc_weight`
