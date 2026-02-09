
Metedata：由navsim_logs描述；

```
${ROOT}/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl
 ```

Pickle文件由**Frame**数组组成，设计上把所有**Scene**的**Frame**统一存在了Pickle数组中，使用时需要重排。

- 一个**pkl**包含多个**Scene**；
- 每个**Scene**由多个**Frame**组成，这些**Frame**由*scene_token*进行标识，并由*frame_idx*进行排序；