# 安装 TensorBoard

本项目使用 TensorBoard 来可视化训练过程。根据 `requirements.txt`，项目指定的版本是 `tensorboard==2.16.2`。

## 安装方法

### 方法一：使用 pip 直接安装（推荐）

```bash
# 安装指定版本（推荐，与项目一致）
pip install tensorboard==2.16.2

# 或安装最新版本
pip install tensorboard
```

### 方法二：从 requirements.txt 安装

如果已激活项目的 conda 环境（如 `navsim`），可以直接从 requirements.txt 安装：

```bash
# 1. 激活conda环境（如果使用conda）
conda activate navsim

# 2. 安装tensorboard（从requirements.txt指定的版本）
pip install tensorboard==2.16.2

# 或者安装整个requirements.txt（会安装所有依赖）
pip install -r requirements.txt
```

### 方法三：在 Docker 容器中安装

如果是在 Docker 容器中：

```bash
# 1. 进入运行中的容器
docker exec -it <container_id> /bin/bash

# 2. 在容器内安装
pip install tensorboard==2.16.2

# 或者如果容器内已有requirements.txt
pip install -r requirements.txt
```

如果需要在 Dockerfile 中安装，添加：

```dockerfile
RUN pip install tensorboard==2.16.2
```

### 方法四：使用 conda 安装（不推荐）

虽然可以使用 conda 安装，但版本可能不一致：

```bash
conda install -c conda-forge tensorboard
```

建议使用 pip 安装以匹配项目要求。

## 验证安装

安装完成后，验证是否安装成功：

```bash
# 检查版本
tensorboard --version

# 应该显示: 2.16.2 (如果安装了指定版本)

# 或者使用Python验证
python -c "import tensorboard; print(tensorboard.__version__)"
```

## 如果已安装 PyTorch Lightning

PyTorch Lightning 通常会自动安装 TensorBoard 作为依赖，但可能版本不一致。

检查当前版本：
```bash
pip show tensorboard
```

如果需要升级到指定版本：
```bash
pip install --upgrade tensorboard==2.16.2
```

## 常见问题

### Q: 安装时出现依赖冲突
A: 尝试使用虚拟环境隔离：
```bash
# 创建新的虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 然后安装
pip install tensorboard==2.16.2
```

### Q: 在Docker中安装后，退出容器就丢失了
A: 需要在Dockerfile中添加安装命令，或使用docker commit保存更改：
```bash
docker commit <container_id> <new_image_name>
```

### Q: 权限错误
A: 如果使用系统Python，可能需要sudo（不推荐），或使用用户安装：
```bash
pip install --user tensorboard==2.16.2
```

## 下一步

安装完成后，可以：
1. 启动TensorBoard查看日志：`tensorboard --logdir=<log_directory>`
2. 查看详细使用说明：[view_tensorboard_in_docker.md](view_tensorboard_in_docker.md)




