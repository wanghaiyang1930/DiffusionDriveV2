

## Ego Query

## Agent Query

## BEV Feature

## Status Encoding

## Status Feature

## Camera Feature

## Feature

## Target

## Metric Cache

在模型设计的 metric_cache 一直是 MetricCache 的文件地址；

MetricCache 应该是一个数据，起大小与BatchSize一直，在使用过程中传递，按照BatchSize的大小对 **metric_cache** 进行加载。
每一个 metric_cache 在**pdm_score_par**中被应用，每一个pickle文件，就是一个 MetricCache 对象，可以参考：
```
/home/workspace/e2e/diffusion/DiffusionDriveV2/navsim/planning/metric_caching/metric_cache.py
```


```
/home/data/navsim/exp/metric_cache/2021.10.11.08.31.07_veh-50_01750_01948/unknown/e9203f0ea48f5b71/metric_cache.pkl
```

2021.10.11.08.31.07_veh-50_01750_01948：表示一个场景（Scene），也可以理解为一个Clip；
e9203f0ea48f5b71：表示一帧（Frame）；

