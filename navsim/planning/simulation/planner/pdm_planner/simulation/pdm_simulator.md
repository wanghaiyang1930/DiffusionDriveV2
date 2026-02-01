分析 `PDMSimulator` 类。查看相关依赖文件以更全面理解其功能。


[5 tools called]


## PDMSimulator 类分析

### 主要功能

`PDMSimulator` 是 nuPlan 仿真管道的重新实现，支持批量仿真。它用于模拟车辆在给定参考轨迹（proposals）上的实际运动，通过 LQR 跟踪器与运动学模型，将参考轨迹转换为考虑车辆动力学约束的实际轨迹。

### 核心组件

1. `BatchKinematicBicycleModel`：批量运动学自行车模型
   - 根据控制命令（加速度、转向率）推进车辆状态
   - 考虑车辆物理约束（如最大转向角）

2. `BatchLQRTracker`：批量 LQR 跟踪器
   - 计算跟踪参考轨迹所需的控制命令
   - 分离纵向（速度跟踪）和横向（路径跟踪）控制

### 工作流程

```
输入参考轨迹 → LQR跟踪器计算控制命令 → 运动学模型推进状态 → 输出模拟轨迹
```

具体步骤：
1. 初始化：将参考轨迹加载到跟踪器
2. 循环仿真：对每个时间步
   - 跟踪器根据当前状态和参考轨迹计算控制命令
   - 运动学模型根据控制命令推进到下一状态
3. 返回：完整的模拟状态序列

### 输入参数

#### `simulate_proposals` 方法：

1. `states: npt.NDArray[np.float64]`
   - 形状：`(batch_size, num_poses+1, state_dim)`
   - 含义：一批候选轨迹的参考状态序列
   - 内容：每个时间点的状态向量，通常包含：
     - 位置 (x, y)
     - 航向角 (heading)
     - 速度 (velocity)
     - 加速度 (acceleration)
     - 转向角 (steering_angle)
     - 等

2. `initial_ego_state: EgoState`
   - 类型：nuPlan 的 `EgoState` 对象
   - 含义：当前时刻的真实车辆状态（作为仿真的起始状态）

### 输出结果

#### `simulated_states: npt.NDArray[np.float64]`
- 形状：`(batch_size, num_poses+1, state_dim)`（与输入 `states` 相同）
- 含义：模拟后的车辆状态序列
- 特点：
  - 从真实的 `initial_ego_state` 开始
  - 通过 LQR 跟踪器跟踪参考轨迹
  - 考虑车辆动力学约束和物理限制
  - 反映实际车辆在跟踪控制下的行为

### 使用场景

从代码中可以看到，`PDMSimulator` 主要用于：
- PDM 评分系统：评估预测轨迹的质量
- 轨迹验证：检查轨迹的可行性和安全性
- 批量仿真：同时模拟多条候选轨迹

### 关键区别

- 输入 `states`：理想化的参考轨迹（可能不满足动力学约束）
- 输出 `simulated_states`：考虑实际车辆动力学和跟踪误差的模拟轨迹

这种设计可以评估轨迹的可行性和实际执行效果，是自动驾驶规划算法评估的重要工具。

---

# PDMSimulator 参数格式详解

## 一、方法签名

```python
def simulate_proposals(
    self, 
    states: npt.NDArray[np.float64], 
    initial_ego_state: EgoState
) -> npt.NDArray[np.float64]
```

---

## 二、输入参数详细格式

### 2.1 `states: npt.NDArray[np.float64]`

#### **数组形状**
```
(batch_size, num_poses + 1, StateIndex.size())
```
其中：
- `batch_size`: 候选轨迹的数量（并行仿真的轨迹条数）
- `num_poses + 1`: 时间步数（包含初始时刻 t=0）
  - `num_poses` 来自 `self.proposal_sampling.num_poses`
  - 例如：如果 `num_poses = 80`，则时间步数为 81（索引 0 到 80）
- `StateIndex.size()`: 状态向量维度，固定为 **11**

#### **数据类型**
- `dtype`: `np.float64`
- 所有元素必须是浮点数

#### **状态向量字段详解（第3维，共11个字段）**

| 索引 | 字段名 | 访问方式 | 单位 | 物理含义 | 说明 |
|------|--------|----------|------|----------|------|
| 0 | X | `StateIndex.X` | [m] | X坐标 | 车辆后轴中心在世界坐标系中的X坐标 |
| 1 | Y | `StateIndex.Y` | [m] | Y坐标 | 车辆后轴中心在世界坐标系中的Y坐标 |
| 2 | HEADING | `StateIndex.HEADING` | [rad] | 航向角 | 车辆朝向角度（弧度制，通常范围 [-π, π]） |
| 3 | VELOCITY_X | `StateIndex.VELOCITY_X` | [m/s] | X方向速度 | 车辆后轴在X方向的纵向速度 |
| 4 | VELOCITY_Y | `StateIndex.VELOCITY_Y` | [m/s] | Y方向速度 | 车辆后轴在Y方向的横向速度（运动学模型中通常为0） |
| 5 | ACCELERATION_X | `StateIndex.ACCELERATION_X` | [m/s²] | X方向加速度 | 车辆在X方向的纵向加速度 |
| 6 | ACCELERATION_Y | `StateIndex.ACCELERATION_Y` | [m/s²] | Y方向加速度 | 车辆在Y方向的横向加速度（运动学模型中通常为0） |
| 7 | STEERING_ANGLE | `StateIndex.STEERING_ANGLE` | [rad] | 转向角 | 前轮相对于车辆纵轴的转向角 |
| 8 | STEERING_RATE | `StateIndex.STEERING_RATE` | [rad/s] | 转向角速度 | 转向角的变化率 |
| 9 | ANGULAR_VELOCITY | `StateIndex.ANGULAR_VELOCITY` | [rad/s] | 角速度 | 车辆绕垂直轴的旋转角速度 |
| 10 | ANGULAR_ACCELERATION | `StateIndex.ANGULAR_ACCELERATION` | [rad/s²] | 角加速度 | 车辆角速度的变化率 |

#### **便捷访问方式**

```python
# 访问整个状态向量
state_vector = states[i, t, :]  # 形状: (11,)

# 访问位置和姿态（SE2状态）
se2_state = states[i, t, StateIndex.STATE_SE2]  # 形状: (3,)，包含 [x, y, heading]

# 访问位置点
point = states[i, t, StateIndex.POINT]  # 形状: (2,)，包含 [x, y]

# 访问速度向量
velocity_2d = states[i, t, StateIndex.VELOCITY_2D]  # 形状: (2,)，包含 [vx, vy]

# 访问加速度向量
acceleration_2d = states[i, t, StateIndex.ACCELERATION_2D]  # 形状: (2,)，包含 [ax, ay]

# 访问单个字段
x = states[i, t, StateIndex.X]
y = states[i, t, StateIndex.Y]
heading = states[i, t, StateIndex.HEADING]
velocity_x = states[i, t, StateIndex.VELOCITY_X]
```

#### **物理含义说明**

- **输入 `states` 是参考轨迹（Reference Trajectory）**
  - 表示理想化的、期望的车辆状态序列
  - 可能不满足车辆动力学约束
  - 作为 LQR 跟踪器的跟踪目标

- **时间对应关系**
  - `states[:, 0, :]` 对应初始时刻 `initial_ego_state.time_point`
  - `states[:, t, :]` 对应时刻 `initial_ego_state.time_point + t * interval_length`
  - `interval_length` 来自 `self.proposal_sampling.interval_length`（通常为 0.1 秒）

#### **示例**

```python
# 假设有 100 个候选轨迹，每个轨迹有 81 个时间步（num_poses=80）
states.shape = (100, 81, 11)

# 访问第 5 个轨迹在第 10 个时间步的状态
trajectory_idx = 5
time_idx = 10
state = states[trajectory_idx, time_idx, :]

# 提取位置和航向
x = state[StateIndex.X]
y = state[StateIndex.Y]
heading = state[StateIndex.HEADING]

# 提取速度
velocity_x = state[StateIndex.VELOCITY_X]
velocity_y = state[StateIndex.VELOCITY_Y]
```

---

### 2.2 `initial_ego_state: EgoState`

#### **类型**
- `EgoState`: nuPlan 框架中的车辆状态对象

#### **物理含义**
- 当前时刻（t=0）的真实车辆状态
- 作为仿真的起始状态
- 包含车辆的完整状态信息（位置、速度、加速度、转向角等）

#### **关键属性**
- `initial_ego_state.time_point`: 初始时刻的时间点
- `initial_ego_state.car_footprint.vehicle_parameters`: 车辆参数（轴距、长度、宽度等）
- `initial_ego_state.rear_axle`: 后轴位置和姿态（StateSE2）
- `initial_ego_state.dynamic_car_state`: 动态状态（速度、加速度等）

#### **在仿真中的作用**
- 仿真的真实起始点（`simulated_states[:, 0]` 来自此状态）
- 提供车辆物理参数给运动学模型
- 提供时间基准点

---

## 三、输出参数详细格式

### 3.1 `simulated_states: npt.NDArray[np.float64]`

#### **数组形状**
```
(batch_size, num_poses + 1, StateIndex.size())
```
- 与输入 `states` 的形状**完全相同**
- `batch_size`: 与输入相同
- `num_poses + 1`: 与输入相同（时间步数）
- `StateIndex.size()`: 固定为 **11**

#### **数据类型**
- `dtype`: `np.float64`
- 所有元素为浮点数

#### **状态向量字段（与输入相同）**

输出数组的状态向量结构与输入完全相同，包含相同的 11 个字段：

| 索引 | 字段名 | 单位 | 物理含义 |
|------|--------|------|----------|
| 0 | X | [m] | X坐标 |
| 1 | Y | [m] | Y坐标 |
| 2 | HEADING | [rad] | 航向角 |
| 3 | VELOCITY_X | [m/s] | X方向速度 |
| 4 | VELOCITY_Y | [m/s] | Y方向速度 |
| 5 | ACCELERATION_X | [m/s²] | X方向加速度 |
| 6 | ACCELERATION_Y | [m/s²] | Y方向加速度 |
| 7 | STEERING_ANGLE | [rad] | 转向角 |
| 8 | STEERING_RATE | [rad/s] | 转向角速度 |
| 9 | ANGULAR_VELOCITY | [rad/s] | 角速度 |
| 10 | ANGULAR_ACCELERATION | [rad/s²] | 角加速度 |

#### **物理含义说明**

- **输出 `simulated_states` 是模拟轨迹（Simulated Trajectory）**
  - 从真实的 `initial_ego_state` 开始
  - 通过 LQR 跟踪器跟踪输入参考轨迹 `states`
  - 考虑车辆动力学约束和物理限制
  - 反映实际车辆在跟踪控制下的行为

- **关键区别**
  - **输入 `states`**: 理想化的参考轨迹（可能不可行）
  - **输出 `simulated_states`**: 考虑实际动力学的可行轨迹

- **初始状态**
  - `simulated_states[:, 0, :]` = `ego_state_to_state_array(initial_ego_state)`
  - 即输出的第一个时间步来自真实的初始状态，而不是输入的 `states[:, 0, :]`

- **后续状态**
  - `simulated_states[:, t, :]` 是通过运动学模型从 `simulated_states[:, t-1, :]` 推进得到的
  - 每一步都通过 LQR 跟踪器计算控制命令，然后由运动学模型执行

#### **访问方式（与输入相同）**

```python
# 访问整个状态向量
simulated_state = simulated_states[i, t, :]

# 访问位置和姿态
simulated_se2 = simulated_states[i, t, StateIndex.STATE_SE2]

# 访问单个字段
simulated_x = simulated_states[i, t, StateIndex.X]
simulated_y = simulated_states[i, t, StateIndex.Y]
simulated_heading = simulated_states[i, t, StateIndex.HEADING]
```

#### **示例**

```python
# 输入和输出形状相同
assert states.shape == simulated_states.shape  # (100, 81, 11)

# 比较参考轨迹和模拟轨迹
reference_x = states[0, 10, StateIndex.X]
simulated_x = simulated_states[0, 10, StateIndex.X]

# 计算跟踪误差
position_error = np.linalg.norm(
    states[0, 10, StateIndex.POINT] - simulated_states[0, 10, StateIndex.POINT]
)
```

---

## 四、完整示例

```python
import numpy as np
from navsim.planning.simulation.planner.pdm_planner.simulation.pdm_simulator import PDMSimulator
from navsim.planning.simulation.planner.pdm_planner.utils.pdm_enums import StateIndex
from nuplan.common.actor_state.ego_state import EgoState
from nuplan.planning.simulation.trajectory.trajectory_sampling import TrajectorySampling

# 创建仿真器
proposal_sampling = TrajectorySampling(
    num_poses=80,  # 80个未来时间步
    interval_length=0.1  # 每个时间步0.1秒
)
simulator = PDMSimulator(proposal_sampling)

# 准备输入数据
batch_size = 100  # 100个候选轨迹
num_poses = 80
state_dim = StateIndex.size()  # 11

# 创建参考轨迹数组（示例：随机生成，实际应从规划器获取）
states = np.random.randn(batch_size, num_poses + 1, state_dim).astype(np.float64)

# 设置初始状态（示例）
initial_ego_state = ...  # 从场景中获取真实的初始状态

# 执行仿真
simulated_states = simulator.simulate_proposals(states, initial_ego_state)

# 验证输出形状
assert simulated_states.shape == (batch_size, num_poses + 1, state_dim)
assert simulated_states.dtype == np.float64

# 访问结果
for i in range(batch_size):
    for t in range(num_poses + 1):
        # 获取模拟状态
        x = simulated_states[i, t, StateIndex.X]
        y = simulated_states[i, t, StateIndex.Y]
        heading = simulated_states[i, t, StateIndex.HEADING]
        velocity = simulated_states[i, t, StateIndex.VELOCITY_X]
        
        # 处理结果...
```

---

## 五、注意事项

1. **时间步数要求**
   - 输入 `states` 的第1维必须至少为 `num_poses + 1`
   - 如果输入的第1维大于 `num_poses + 1`，只会使用前 `num_poses + 1` 个时间步

2. **状态向量维度**
   - 第3维必须严格等于 `StateIndex.size()` (11)
   - 不能多也不能少

3. **坐标系**
   - 所有位置和角度都在世界坐标系中
   - 航向角使用弧度制
   - 位置以米为单位

4. **初始状态**
   - 输出的第一个时间步来自 `initial_ego_state`，而不是输入的 `states[:, 0, :]`
   - 这确保了仿真从真实状态开始

5. **批量处理**
   - 所有轨迹并行处理，提高效率
   - 每个轨迹的仿真相互独立
