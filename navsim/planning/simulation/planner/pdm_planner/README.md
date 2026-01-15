



nuplan.planning.simulation.trajectory.trajectory_sampling

TrajectorySampling:
- 可以理解为一个轨迹采样的配置参数描述的对象；
- num_pose: 点的个数；
- time_horizon: 整个事件跨度；
- interval_length: 平均每个点的运行时间；

其使用__post_init__进行后初始化，然后重新定义__hash__使其能够被哈希。

SplitState：
- linear_states: 能够进行线性插值的，比如，时间戳、位置、速度；
- angular_states: 需要进行周期插值的，比如航向角；
- fixed_state: 固定不变的数据，比如，长、宽、高等；

AbstractTrajectory:

轨迹描述：一串姿态（带有时间戳、航向角、位置）