


PDMObservation 的用途和内容。
查看相关类以更好地理解整体结构：
PDMObservation 的用途
PDMObservation 是 PDM（Planner Decision Model）规划器的观察类，用于管理预测的占用地图（forecasted occupancy maps）。它整合当前环境信息并生成未来时间步的占用地图，供路径规划使用。
描述的主要内容
该类封装以下信息：
1. 时间序列占用地图 (_occupancy_maps)
存储未来多个时间步的 PDMOccupancyMap
每个时间步包含该时刻所有障碍物的占用区域
通过 __getitem__ 方法访问特定时间步的占用地图
2. 三类障碍物信息
静态对象 (Static Objects):
道路上的静态障碍物
几何形状固定不变
动态对象 (Dynamic Objects):
车辆、行人等可移动对象
根据速度预测未来位置（使用 dynamic_object_dxy 计算）
交通灯 (Traffic Lights):
沿自车路线的红色交通灯
作为占用区域处理，用于约束规划
3. 关键属性
unique_objects: 所有跟踪对象的唯一字典（token → TrackedObject）
collided_track_ids: 已碰撞对象的轨迹 ID 列表（避免重复处理）
red_light_token: 红色交通灯的标识符
4. 核心功能
更新方法 (update):
从观测数据中提取对象
过滤超出范围或已碰撞的对象
预测动态对象未来位置
生成时间序列占用地图
检测当前时刻的碰撞
三种更新模式:
update(): 标准模式，基于观测数据预测未来
update_replay(): 回放模式，使用场景的真实未来数据
update_detections_tracks(): 基于检测轨迹的更新
5. 时间分辨率处理
支持不同的采样分辨率 (observation_sample_res)
自动适配轨迹采样和提案采样的时间间隔
通过 _global_to_local_idcs 映射全局时间索引到本地索引
该类为 PDM 规划器提供结构化环境表示，支持安全、高效的路径规划。