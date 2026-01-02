# 在Docker中查看TensorBoard日志

本文档介绍如何在Docker容器中训练时查看TensorBoard日志的几种方法。

## 方法一：日志目录已挂载到主机（推荐）

如果训练时将输出目录通过volume挂载到了主机，直接在主机的挂载目录启动TensorBoard。

### 1. 确认日志目录已挂载

```bash
# 查看Docker容器的挂载情况
docker inspect <container_id> | grep -A 10 Mounts

# 或者查看docker run命令中的 -v 参数
# 例如: -v /host/path:/container/path
```

### 2. 在主机上启动TensorBoard

```bash
# 方法1: 使用提供的脚本
chmod +x view_tensorboard.sh
./view_tensorboard.sh ${NAVSIM_EXP_ROOT}/training_diffusiondrivev2_rl_agent/xxx/lightning_logs

# 方法2: 直接运行tensorboard命令
tensorboard --logdir=/host/path/to/lightning_logs --host=0.0.0.0 --port=6006

# 然后在浏览器打开: http://localhost:6006
```

## 方法二：在Docker容器内启动TensorBoard并映射端口

如果日志只在容器内，可以在容器内启动TensorBoard，并将端口映射到主机。

### 1. 进入运行中的容器

```bash
# 进入正在运行的训练容器
docker exec -it <container_id> /bin/bash
```

### 2. 在容器内启动TensorBoard

```bash
# 在容器内
cd /path/to/output_dir
tensorboard --logdir=lightning_logs --host=0.0.0.0 --port=6006
```

### 3. 从主机访问

如果启动容器时已经映射了端口（-p 6006:6006），直接在浏览器访问：
```
http://localhost:6006
```

如果没有映射端口，需要：
```bash
# 停止当前容器（如果可能）
# 重新启动容器时添加端口映射
docker run ... -p 6006:6006 ...
```

## 方法三：使用docker exec在新容器中运行TensorBoard

创建一个新容器，共享日志目录，运行TensorBoard。

### 1. 找到日志目录在主机的位置

```bash
# 查看原始容器的挂载点
docker inspect <container_id> | grep -A 20 Mounts
```

### 2. 运行TensorBoard容器

```bash
# 如果日志在主机目录 /host/logs
docker run -it --rm \
    -v /host/logs:/logs \
    -p 6006:6006 \
    <your_image> \
    tensorboard --logdir=/logs/lightning_logs --host=0.0.0.0 --port=6006

# 或者在后台运行
docker run -d --rm \
    --name tensorboard \
    -v /host/logs:/logs \
    -p 6006:6006 \
    <your_image> \
    tensorboard --logdir=/logs/lightning_logs --host=0.0.0.0 --port=6006
```

## 方法四：复制日志文件到主机

如果无法挂载或映射，可以临时复制日志文件到主机。

### 1. 复制日志目录到主机

```bash
# 从容器复制到主机
docker cp <container_id>:/path/to/lightning_logs ./logs/

# 或者只复制特定版本
docker cp <container_id>:/path/to/lightning_logs/version_0 ./logs/version_0
```

### 2. 在主机上启动TensorBoard

```bash
tensorboard --logdir=./logs
```

## 方法五：使用docker-compose（如果使用）

如果你使用docker-compose，可以在配置中添加TensorBoard服务。

```yaml
version: '3.8'
services:
  training:
    # ... 训练服务配置
    volumes:
      - ./logs:/app/logs
  
  tensorboard:
    image: <your_image>
    ports:
      - "6006:6006"
    volumes:
      - ./logs:/logs
    command: tensorboard --logdir=/logs/lightning_logs --host=0.0.0.0 --port=6006
    depends_on:
      - training
```

然后运行：
```bash
docker-compose up tensorboard
```

## 实用技巧

### 1. 查找最新的日志目录

```bash
# 在容器内
find /path/to/output_dir -name "lightning_logs" -type d

# 查找最新的version目录
ls -t /path/to/output_dir/lightning_logs/ | head -1
```

### 2. 查看多个实验对比

```bash
# TensorBoard可以同时查看多个实验目录
tensorboard --logdir=/path/to/experiments --host=0.0.0.0 --port=6006

# 目录结构示例:
# /path/to/experiments/
#   ├── experiment1/lightning_logs/version_0
#   ├── experiment2/lightning_logs/version_0
#   └── experiment3/lightning_logs/version_0
```

### 3. 在后台运行TensorBoard

```bash
# 使用nohup
nohup tensorboard --logdir=lightning_logs --host=0.0.0.0 --port=6006 > tensorboard.log 2>&1 &

# 或者使用screen/tmux
screen -S tensorboard
tensorboard --logdir=lightning_logs --host=0.0.0.0 --port=6006
# Ctrl+A, D 分离
```

### 4. 远程服务器访问

如果Docker在远程服务器上：

```bash
# SSH端口转发
ssh -L 6006:localhost:6006 user@remote_server

# 然后在本地浏览器访问
# http://localhost:6006
```

## 常见问题

### Q: 无法访问 http://localhost:6006
A: 检查：
1. TensorBoard是否正在运行
2. 端口是否正确映射（-p 6006:6006）
3. 防火墙是否允许该端口
4. 是否使用了 --host=0.0.0.0

### Q: 找不到日志文件
A: 检查：
1. 训练是否已完成至少一个epoch（如果代码被注释则不会生成）
2. 日志目录路径是否正确
3. 容器内的路径与主机路径的映射关系

### Q: 图像不显示
A: 确认：
1. `on_validation_epoch_end` 函数中的代码是否已取消注释
2. 是否至少完成了一次validation epoch
3. TensorBoard版本是否兼容




