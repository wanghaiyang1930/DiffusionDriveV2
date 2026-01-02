# Ray 框架使用指南

## 1. 什么是 Ray？

Ray 是一个用于构建分布式应用的 Python 框架，支持：
- **并行计算**：在多核 CPU 上并行执行任务
- **分布式计算**：跨多台机器运行任务
- **机器学习**：分布式训练和推理
- **数据处理**：大规模数据并行处理

## 2. 安装

```bash
pip install ray
```

## 3. 核心概念

### 3.1 Remote Functions（远程函数）
使用 `@ray.remote` 装饰器将普通函数转换为可并行执行的远程函数。

### 3.2 Object References（对象引用）
Ray 使用对象引用来表示远程任务的返回值，需要调用 `.get()` 来获取实际结果。

### 3.3 Actors（执行器）
用于状态管理和更复杂的并行模式。

## 4. 基本用法

### 4.1 初始化 Ray

```python
import ray

# 方式1: 本地初始化（使用所有可用 CPU）
ray.init()

# 方式2: 指定 CPU 数量
ray.init(num_cpus=4)

# 方式3: 连接到远程集群
ray.init(address="ray://<head-node-ip>:10001")

# 方式4: 本地模式（串行执行，用于调试）
ray.init(local_mode=True)

# 检查 Ray 是否已初始化
if ray.is_initialized():
    print("Ray is running")

# 关闭 Ray
ray.shutdown()
```

### 4.2 使用 Remote Functions

#### 基本示例

```python
import ray
import time

# 初始化 Ray
ray.init(num_cpus=4)

# 定义远程函数
@ray.remote
def slow_function(x):
    """模拟耗时任务"""
    time.sleep(1)
    return x * 2

# 串行执行（不使用 Ray）
start = time.time()
results = [slow_function.remote(i) for i in range(4)]
print(f"串行执行时间: {time.time() - start:.2f}秒")  # 约 4 秒

# 并行执行（使用 Ray）
start = time.time()
futures = [slow_function.remote(i) for i in range(4)]
results = ray.get(futures)  # 等待所有任务完成并获取结果
print(f"并行执行时间: {time.time() - start:.2f}秒")  # 约 1 秒
print(results)  # [0, 2, 4, 6]

ray.shutdown()
```

#### 带参数的远程函数

```python
@ray.remote
def add(a, b):
    return a + b

@ray.remote
def multiply(x, y):
    return x * y

# 异步提交任务
future1 = add.remote(1, 2)
future2 = multiply.remote(3, 4)

# 获取结果
result1 = ray.get(future1)  # 3
result2 = ray.get(future2)  # 12

# 批量获取
results = ray.get([future1, future2])
```

#### 指定资源需求

```python
@ray.remote(num_cpus=2, num_gpus=1)
def gpu_task(data):
    # 需要 2 个 CPU 和 1 个 GPU 的任务
    import torch
    # ... GPU 计算
    return result

# 调用
future = gpu_task.remote(data)
result = ray.get(future)
```

### 4.3 使用 Ray Map（批量并行处理）

Ray 提供了类似 Python `map` 的功能，但可以并行执行：

```python
@ray.remote
def process_item(item):
    return item * 2

# 方式1: 使用 ray.util.map
items = [1, 2, 3, 4, 5]
futures = [process_item.remote(item) for item in items]
results = ray.get(futures)

# 方式2: 使用 ray.util.multiprocessing (类似于 multiprocessing.Pool)
from ray.util.multiprocessing import Pool

def process_item(item):
    return item * 2

with Pool() as pool:
    results = pool.map(process_item, items)
```

### 4.4 使用 Actors（有状态对象）

Actors 用于维护状态的并行计算：

```python
@ray.remote
class Counter:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value
    
    def get_value(self):
        return self.value

# 创建 Actor 实例
counter = Counter.remote()

# 调用 Actor 的方法（自动串行化）
future1 = counter.increment.remote()
future2 = counter.increment.remote()

print(ray.get(future1))  # 1
print(ray.get(future2))  # 2
print(ray.get(counter.get_value.remote()))  # 2
```

## 5. 高级用法

### 5.1 分布式集群设置

#### 在主节点上启动 Ray

```bash
# 在主节点上
ray start --head --port=6379 --redis-password='your-password'
```

#### 在工作节点上连接

```bash
# 在工作节点上
ray start --address=<head-node-ip>:6379 --redis-password='your-password'
```

#### 在代码中连接

```python
import ray

# 方式1: 使用环境变量（推荐用于 SLURM 集群）
# 设置环境变量: ip_head, redis_password, num_nodes
ray.init(address="auto")

# 方式2: 直接指定地址
ray.init(address="ray://<head-node-ip>:10001")
```

### 5.2 错误处理和重试

```python
@ray.remote(max_retries=3)
def unreliable_task():
    import random
    if random.random() < 0.5:
        raise ValueError("随机失败")
    return "成功"

# Ray 会自动重试失败的任务（最多3次）
result = ray.get(unreliable_task.remote())
```

### 5.3 资源管理

```python
# 检查可用资源
resources = ray.available_resources()
print(f"可用 CPU: {resources.get('CPU', 0)}")
print(f"可用 GPU: {resources.get('GPU', 0)}")

# 等待资源可用
@ray.remote(num_gpus=1)
def gpu_task():
    pass

# 如果 GPU 不可用，任务会排队等待
```

## 6. 项目中的实际应用

### 6.1 项目中的 Ray 初始化

查看 `worker_ray_no_torch.py`，可以看到项目中的 Ray 初始化方式：

```python
def initialize_ray(
    master_node_ip: Optional[str] = None,
    threads_per_node: Optional[int] = None,
    local_mode: bool = False,
    log_to_driver: bool = True,
    use_distributed: bool = False,
):
    # 本地模式
    if not use_distributed:
        ray.init(
            num_cpus=threads_per_node,
            dashboard_host="0.0.0.0",
            local_mode=local_mode,
            log_to_driver=log_to_driver,
        )
    # 分布式模式
    elif master_node_ip and use_distributed:
        ray.init(
            address=f"ray://{master_node_ip}:10001",
            local_mode=local_mode,
            log_to_driver=log_to_driver
        )
    # 通过环境变量连接集群（SLURM）
    elif env_var_master_node_ip in os.environ and use_distributed:
        ray.init(
            address="auto",
            _node_ip_address=master_node_ip,
            _redis_password=redis_password,
            log_to_driver=log_to_driver,
        )
```

### 6.2 在项目中使用 Ray 执行任务

```python
# 项目中使用 ray_map 来并行执行任务
from nuplan.planning.utils.multithreading.ray_execution import ray_map

def cache_scenarios(args):
    # 处理场景的逻辑
    pass

# 并行执行多个任务
results = ray_map(worker, cache_scenarios, data_points)
```

### 6.3 直接使用 Ray Remote

```python
# 项目中也直接使用 ray.remote
remote_fn = ray.remote(task.fn).options(
    num_gpus=task.num_gpus,
    num_cpus=task.num_cpus
)
object_id = remote_fn.remote(*args, **kwargs)
result = ray.get(object_id)
```

## 7. 最佳实践

### 7.1 性能优化

1. **避免频繁的小任务**：批量处理更高效
2. **合理设置资源需求**：不要过度分配资源
3. **使用对象存储**：避免重复传输大对象

```python
# 将大对象存入 Ray 对象存储
large_data = ray.put(large_array)

@ray.remote
def process(data_ref):
    data = ray.get(data_ref)  # 从对象存储获取
    return process_data(data)

# 多个任务可以共享同一个对象引用
results = [process.remote(large_data) for _ in range(10)]
```

### 7.2 调试技巧

```python
# 1. 使用 local_mode 进行调试（串行执行，便于调试）
ray.init(local_mode=True)

# 2. 查看任务状态
ray.util.pdb.set_trace()  # 在远程函数中设置断点

# 3. 查看 Ray Dashboard
# 启动后访问 http://localhost:8265
```

### 7.3 错误处理

```python
# 捕获远程任务中的异常
@ray.remote
def might_fail():
    if condition:
        raise ValueError("错误")
    return "成功"

try:
    result = ray.get(might_fail.remote())
except ValueError as e:
    print(f"任务失败: {e}")
```

## 8. 与其他并行框架的对比

| 特性 | Ray | multiprocessing | threading | asyncio |
|------|-----|----------------|-----------|---------|
| 跨机器 | ✅ | ❌ | ❌ | ❌ |
| GIL 限制 | ✅ | ✅ | ❌ | ✅ |
| GPU 支持 | ✅ | ❌ | ❌ | ❌ |
| 动态调度 | ✅ | ❌ | ❌ | ✅ |
| 学习曲线 | 中等 | 简单 | 简单 | 中等 |

## 9. 总结

Ray 是一个强大的分布式计算框架，特别适合：
- 需要跨多台机器并行执行的任务
- 需要灵活资源调度的场景
- 大规模数据处理和机器学习任务
- 需要动态任务调度的应用

在项目中，Ray 主要用于并行执行 metric caching 等计算密集型任务，可以显著提升处理速度。









