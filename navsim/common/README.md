

## EgoStatus

- Pose
- Velocity
- Acceleration
- DrivingCommand


## AgentInput

- List[Lidar]
- List[Cameras]
- List[EgoStatus]

## Trajectory

- List[Pose]
- Sampling

## Annotations

- List[Name]
- List[Boxes]
- List[Velocity]
- List[TrackedToken]
- List[InstanceToken]


## Scene

- List[Frame]：即存储历史帧，也存储未来帧，默认当前帧存储在历史帧中；
- Metadata

## Frame

- Token
- Timestamp

- RoadIds
- Annotations
- TrafficLights

- Lidar
- Cameras
- EgoStatus


## SceneMetadata

- MapName
- LogName
- SceneToken
- InitialToken

- HistoryFrames 历史帧数；
- FutureFrames 未来帧数；