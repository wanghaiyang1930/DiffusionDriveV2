# DDIMScheduler 用法详解

## 一、基本概念

**DDIMScheduler** 是 Denoising Diffusion Implicit Models (DDIM) 的调度器，用于控制扩散模型的去噪过程。它相比 DDPM 的优势是可以使用更少的采样步数（如 10-50 步）生成高质量样本。

## 二、初始化参数

在你的代码中，DDIMScheduler 的初始化如下：

```python
self.diffusion_scheduler = DDIMScheduler(
    num_train_timesteps=1000,      # 训练时的总时间步数
    steps_offset=1,                 # 时间步偏移量
    beta_schedule="scaled_linear",  # β 调度方式
    prediction_type="sample",       # 模型预测类型：预测原始样本 x_0
)
```

### 参数说明：
- **num_train_timesteps**: 训练时使用的总时间步数（通常 1000）
- **steps_offset**: 时间步索引的偏移量
- **beta_schedule**: 噪声调度方式，常见有 `"linear"`, `"scaled_linear"`, `"squaredcos_cap_v2"` 等
- **prediction_type**: 
  - `"epsilon"`: 模型预测噪声 ε
  - `"sample"`: 模型预测原始样本 x_0（你的代码使用这个）
  - `"v_prediction"`: 模型预测速度 v

## 三、核心方法

### 1. `set_timesteps()` - 设置推理时间步

```python
self.diffusionrl_scheduler.set_timesteps(1000, device)
```

**作用**：设置推理时使用的时间步序列。虽然训练用 1000 步，但推理可以只用 10-50 步。

**在你的代码中**（第 811 行）：
```python
self.diffusionrl_scheduler.set_timesteps(1000, device)
step_ratio = 20 / step_num  # step_num = 10
roll_timesteps = (np.arange(0, step_num) * step_ratio).round()[::-1].copy()
# 结果：[18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
```

### 2. `add_noise()` - 添加噪声

```python
diffusion_output = self.diffusionrl_scheduler.add_noise(
    original_samples=diffusion_output,  # 原始样本
    noise=noise,                         # 要添加的噪声
    timesteps=trunc_timesteps            # 时间步（控制噪声强度）
)
```

**作用**：根据公式 `x_t = sqrt(α_t) * x_0 + sqrt(1-α_t) * ε` 添加噪声。

**在你的代码中**（第 827 行）：
```python
noise = torch.randn(diffusion_output.shape, device=device)
trunc_timesteps = torch.ones((bs,), device=device, dtype=torch.long) * 8
diffusion_output = self.diffusionrl_scheduler.add_noise(
    original_samples=diffusion_output, 
    noise=noise, 
    timesteps=trunc_timesteps
)
```
这里从时间步 8 开始，而不是从 1000 开始，这是一种"截断噪声"策略。

### 3. `step()` - 执行一步去噪

这是最核心的方法，执行一次去噪步骤：

```python
prev_sample, log_prob, prev_sample_mean = self.diffusionrl_scheduler.step(
    model_output=x_start,    # 模型预测的 x_0（因为 prediction_type="sample"）
    timestep=k,               # 当前时间步
    sample=diffusion_output,  # 当前带噪声的样本 x_t
    eta=eta,                  # DDIM 参数：0.0=确定性，1.0=随机性
)
```

**参数说明**：
- **model_output**: 模型的输出。由于 `prediction_type="sample"`，这里应该是预测的原始样本 x_0
- **timestep**: 当前时间步（如 18, 16, 14...）
- **sample**: 当前带噪声的样本 x_t
- **eta**: 
  - `eta=0.0`: 确定性采样（DDIM），生成结果可复现
  - `eta=1.0`: 随机采样（DDPM），每次结果不同

**返回值**（自定义版本）：
- `prev_sample`: 去噪后的样本 x_{t-1}
- `log_prob`: 对数概率（用于强化学习）
- `prev_sample_mean`: 去噪后的均值（确定性部分）

## 四、完整使用流程

在你的代码中，完整的扩散采样流程如下：

```python
# 1. 初始化调度器
self.diffusionrl_scheduler.set_timesteps(1000, device)

# 2. 准备初始样本（添加截断噪声）
plan_anchor = ...  # 形状: (bs, num_groups*20, 8, 2)
diffusion_output = self.norm_odo(plan_anchor)
noise = torch.randn(diffusion_output.shape, device=device)
trunc_timesteps = torch.ones((bs,), device=device, dtype=torch.long) * 8
diffusion_output = self.diffusionrl_scheduler.add_noise(
    original_samples=diffusion_output, 
    noise=noise, 
    timesteps=trunc_timesteps
)

# 3. 迭代去噪（10 步）
for i, k in enumerate(roll_timesteps):  # k: 18, 16, 14, ..., 0
    # 3.1 将带噪声的轨迹输入模型
    noisy_traj_points = self.denorm_odo(diffusion_output)
    traj_feature = self.plan_anchor_encoder(...)
    time_embed = self.time_mlp(k)
    
    # 3.2 模型预测 x_0
    poses_reg, poses_cls = self.diff_decoder(...)
    x_start = poses_reg[..., :2]  # 模型预测的干净轨迹
    x_start = self.norm_odo(x_start)
    
    # 3.3 调度器执行一步去噪
    prev_sample, log_prob, _ = self.diffusionrl_scheduler.step(
        model_output=x_start,
        timestep=k,
        sample=diffusion_output,
        eta=eta,
    )
    
    # 3.4 更新状态
    diffusion_output = prev_sample
    all_log_probs.append(log_prob)

# 4. 最终输出
final_trajectory = self.denorm_odo(diffusion_output)
```

## 五、自定义扩展：DDIMScheduler_with_logprob

你的代码继承并扩展了 DDIMScheduler，添加了对数概率计算：

```python
class DDIMScheduler_with_logprob(DDIMScheduler):
    def step(self, ...):
        # ... 执行标准 DDIM 去噪 ...
        
        # 计算对数概率（用于强化学习）
        log_prob = (
            -((prev_sample.detach() - prev_sample_mean) ** 2) / (2 * (std_dev_t_mul**2))
            - torch.log(std_dev_t_mul)
            - torch.log(torch.sqrt(2 * torch.as_tensor(math.pi)))
        )
        log_prob = log_prob.sum(dim=(-2, -1))
        
        return prev_sample, log_prob, prev_sample_mean
```

**关键改进**：
1. **返回 log_prob**：计算每一步的对数概率，用于强化学习的策略梯度
2. **自定义噪声**：支持乘性噪声和加性噪声（第 652-673 行）
3. **返回均值**：返回确定性部分 `prev_sample_mean`，用于分析

## 六、关键公式（DDIM）

DDIM 的去噪公式（简化版）：

```
x_{t-1} = sqrt(α_{t-1}) * x_0_pred + sqrt(1 - α_{t-1} - σ_t^2) * ε_pred + σ_t * z
```

其中：
- `x_0_pred`: 模型预测的原始样本（你的 `model_output`）
- `ε_pred`: 从 x_0_pred 推导出的噪声
- `σ_t`: 方差项（由 `eta` 控制）
- `z`: 随机噪声（eta=0 时为零）

## 七、在你的应用场景中

**用途**：轨迹规划
- **输入**：带噪声的轨迹锚点（plan_anchor）
- **过程**：通过 10 步去噪，逐步生成干净的轨迹
- **输出**：最终轨迹 + 每一步的对数概率（用于 RL 训练）

**优势**：
1. **快速采样**：10 步即可生成高质量轨迹（相比 1000 步快 100 倍）
2. **可控性**：通过 `eta` 参数控制随机性
3. **可微性**：支持梯度反向传播，适合端到端训练

## 八、常见问题

### Q1: 为什么从时间步 8 开始，而不是 1000？
**A**: 这是一种"截断噪声"策略。从较小的噪声水平开始可以：
- 加快采样速度
- 保留更多原始信息
- 适合轨迹规划这种需要保留一定结构信息的任务

### Q2: `eta` 参数如何选择？
**A**: 
- **训练时**：可以使用 `eta > 0` 增加探索性
- **推理时**：通常用 `eta=0.0` 获得确定性结果
- **你的代码**：训练时 `eta` 作为参数传入，测试时固定为 `eta=0.0`

### Q3: `prediction_type="sample"` 和 `"epsilon"` 的区别？
**A**:
- `"sample"`: 模型直接预测干净的样本 x_0（你的代码使用）
- `"epsilon"`: 模型预测噪声 ε，需要额外计算 x_0 = (x_t - sqrt(1-α_t)*ε) / sqrt(α_t)

## 九、参考代码位置

- **初始化**：第 704-715 行
- **训练流程**：第 807-946 行 (`forward_train_rl`)
- **测试流程**：第 949-1033 行 (`forward_test_rl`)
- **自定义调度器**：第 525-683 行 (`DDIMScheduler_with_logprob`)
