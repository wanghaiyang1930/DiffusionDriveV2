"""
@brief: Visualize the BEV frame with the agent
@author: wanghaiyang
@date: 2025-12-31
"""

import os
from pathlib import Path

import hydra
from hydra.utils import instantiate
import numpy as np
import matplotlib.pyplot as plt

from navsim.common.dataloader import SceneLoader
from navsim.common.dataclasses import SceneFilter, SensorConfig

SPLIT = "mini"  # ["mini", "test", "trainval"]
FILTER = "all_scenes"

hydra.initialize(config_path="../navsim/planning/script/config/common/train_test_split/scene_filter")
cfg = hydra.compose(config_name=FILTER)
scene_filter: SceneFilter = instantiate(cfg)
openscene_data_root = Path(os.getenv("OPENSCENE_DATA_ROOT"))

scene_loader = SceneLoader(
    openscene_data_root / f"navsim_logs/{SPLIT}",
    openscene_data_root / f"sensor_blobs/{SPLIT}",
    scene_filter,
    sensor_config=SensorConfig.build_all_sensors(),
)

token = np.random.choice(scene_loader.tokens)
token = "4fb4172565965b96"
scene = scene_loader.get_scene_from_token(token)

from navsim.visualization.plots import plot_bev_with_agent
from navsim.agents.constant_velocity_agent import ConstantVelocityAgent

agent = ConstantVelocityAgent()
fig, ax = plot_bev_with_agent(scene, agent)
plt.savefig(f'bev_with_agent_{token}.png', dpi=150, bbox_inches='tight')
plt.close()