

## SensorConfig

在代码中，该类用于按帧决定加载哪些传感器，通过配置转换为实际加载做定制化决策。

设计目的
- 内存管理：避免加载不需要的传感器数据
- 灵活性：可按帧精确控制传感器加载
- 性能优化：减少 I/O 和内存占用

- cam_f0: Union[bool, List[int]]
- cam_l0: Union[bool, List[int]]
- cam_l1: Union[bool, List[int]]
- cam_l2: Union[bool, List[int]]
- cam_r0: Union[bool, List[int]]
- cam_r1: Union[bool, List[int]]
- cam_r2: Union[bool, List[int]]
- cam_b0: Union[bool, List[int]]
- lidar_pc: Union[bool, List[int]]

## 架构设计：build_all_sensors

`build_all_sensors` 中 `include` 的工作原理：

## 工作原理

`include` 参数可以是两种类型，用于控制所有传感器的加载方式：

### 1. **布尔值模式** (`bool`)
- `include=True`：所有传感器在所有历史帧都加载
- `include=False`：所有传感器都不加载

### 2. **列表模式** (`List[int]`)
- `include=[0, 1, 2]`：所有传感器仅在指定的历史帧索引（0、1、2）加载

## 实际使用示例

```python
# 方式1: 加载所有传感器的所有历史帧
config1 = SensorConfig.build_all_sensors(include=True)
# 结果: 所有传感器在所有迭代都加载

# 方式2: 不加载任何传感器
config2 = SensorConfig.build_all_sensors(include=False)
# 结果: 所有传感器都不加载

# 方式3: 只在特定历史帧加载所有传感器
config3 = SensorConfig.build_all_sensors(include=[0, 1])  # 只加载前两帧
# 结果: 所有传感器只在 iteration=0 和 iteration=1 时加载
```

## 与 `get_sensors_at_iteration` 的配合

在 `get_sensors_at_iteration(iteration)` 中：
- 如果传感器配置是 `bool=True`，该传感器会被包含
- 如果传感器配置是 `List[int]` 且 `iteration` 在列表中，该传感器会被包含

这样可以在不同历史帧中灵活控制哪些传感器需要加载，用于内存管理。

## 架构设计：get_sensors_at_iteration

1. 遍历所有传感器配置（通过 asdict(self) 转换为字典）；
2. 对每个传感器，检查其配置值：
- 布尔值：True 时，该传感器被包含
- 列表：iteration 在列表中时，该传感器被包含
3. 返回符合条件的传感器名称列表；

```
config = SensorConfig(
    cam_f0=[0, 1],      # 只在第0和第1帧加载
    cam_l0=True,        # 所有帧都加载
    cam_l1=[2],         # 只在第2帧加载
    lidar_pc=False,     # 不加载
    # ... 其他传感器
)

# 调用
sensors = config.get_sensors_at_iteration(0)
# 返回: ['cam_f0', 'cam_l0']  # cam_f0在列表[0,1]中，cam_l0是True

sensors = config.get_sensors_at_iteration(1)
# 返回: ['cam_f0', 'cam_l0']  # cam_f0在列表[0,1]中，cam_l0是True

sensors = config.get_sensors_at_iteration(2)
# 返回: ['cam_l0', 'cam_l1']  # cam_l1在列表[2]中，cam_l0是True

sensors = config.get_sensors_at_iteration(3)
# 返回: ['cam_l0']  # 只有cam_l0是True
```