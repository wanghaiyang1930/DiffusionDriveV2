### Mini

```
export PYTHONPATH=$PWD:$PYTHONPATH
python navsim/planning/script/run_dataset_caching.py agent=diffusiondrivev2_rl_agent experiment_name=diffusiondrivev2_cache train_test_split=mini
```

- agent: navsim/agents/diffusiondrivev2/diffusiondrivev2_rl_agent.py
- FeatureBuilder: navsim/agents/diffusiondrivev2/transfuser_features.py:TransfuserFeatureBuilder
- TargetBuilder: navsim/agents/diffusiondrivev2/transfuser_features.py:TransfuserTargetBuilder
- train_test_split: navsim/planning/script/config/common/train_test_split/mini.yaml
- scene_filter: navsim/planning/script/config/common/train_test_split/scene_filter/all_scenes.yaml

#### FeatureBuilder

- camera_feature
- lidar_feature
- status_feature: driving_command, ego_velocity, ego_acceleration

#### TargetBuilder

- trajectory
- agent_states
- agent_labels
- bev_semantic_map