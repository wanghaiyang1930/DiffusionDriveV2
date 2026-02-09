"""
解析 navsim log pickle 文件的工具脚本

用法:
    python navsim_log_pkl.py [--pkl_path PATH] [--frame_idx IDX] [--summary]

    # 显示摘要信息
    python tools/navsim_log_pkl.py --pkl_path /home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl --summary

    # 查看指定帧的详细信息
    python tools/navsim_log_pkl.py --frame_idx 0

    # 指定不同的 pickle 文件
    python tools/navsim_log_pkl.py --pkl_path /path/to/file.pkl --summary

    # 导出到 JSON
    python tools/navsim_log_pkl.py --export_json output.json
    python tools/navsim_log_pkl.py --export_json output.json:5  # 只导出第5帧

    # 查看指定帧的详细信息
    python tools/navsim_log_pkl.py --pkl_path /home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl --frame_idx 0
"""

import pickle
import argparse
from pathlib import Path
from typing import Dict, List, Any
import json


def load_pickle(pkl_path: str) -> List[Dict[str, Any]]:
    """
    加载 pickle 文件
    
    Args:
        pkl_path: pickle 文件路径
        
    Returns:
        scene_dict_list: 场景字典列表
    """
    pkl_path = Path(pkl_path)
    if not pkl_path.exists():
        raise FileNotFoundError(f"Pickle file not found: {pkl_path}")
    
    with open(pkl_path, 'rb') as f:
        scene_dict_list = pickle.load(f)
    
    return scene_dict_list


def print_summary(scene_dict_list: List[Dict[str, Any]]) -> None:
    """
    打印 pickle 文件的摘要信息
    
    Args:
        scene_dict_list: 场景字典列表
    """
    print("=" * 80)
    print("NAVSIM LOG PICKLE SUMMARY")
    print("=" * 80)
    
    if len(scene_dict_list) == 0:
        print("Empty pickle file!")
        return
    
    # 基本信息
    print(f"\n总帧数: {len(scene_dict_list)}")
    
    # 第一帧的信息
    first_frame = scene_dict_list[0]
    print(f"\n日志名称: {first_frame.get('log_name', 'N/A')}")
    print(f"地图位置: {first_frame.get('map_location', 'N/A')}")
    
    # 所有帧的键
    print(f"\n帧字典包含的键: {list(first_frame.keys())}")
    
    # 统计信息
    frame_indices = [frame.get('frame_idx', -1) for frame in scene_dict_list]
    if frame_indices:
        print(f"\n帧索引范围: {min(frame_indices)} - {max(frame_indices)}")
    
    # 驾驶命令统计
    driving_commands = []
    for frame in scene_dict_list:
        cmd = frame.get('driving_command', 'N/A')
        # 如果是 numpy 数组或其他不可哈希类型，转换为元组或字符串
        if hasattr(cmd, 'tolist'):
            cmd = tuple(cmd.tolist()) if isinstance(cmd.tolist(), list) else str(cmd)
        elif not isinstance(cmd, (str, int, float, tuple)):
            cmd = str(cmd)
        driving_commands.append(cmd)
    
    unique_commands = set(driving_commands)
    print(f"\n驾驶命令类型: {unique_commands}")
    print(f"驾驶命令统计:")
    for cmd in unique_commands:
        count = driving_commands.count(cmd)
        print(f"  {cmd}: {count} 帧")
    
    # 路线信息
    frames_with_route = sum(1 for frame in scene_dict_list if len(frame.get('roadblock_ids', [])) > 0)
    print(f"\n包含路线的帧数: {frames_with_route} / {len(scene_dict_list)}")
    
    # 传感器信息
    if 'cams' in first_frame:
        cam_keys = list(first_frame['cams'].keys()) if isinstance(first_frame['cams'], dict) else []
        print(f"\n相机传感器: {cam_keys}")
    
    if 'lidar_path' in first_frame:
        print(f"\nLiDAR路径示例: {first_frame.get('lidar_path', 'N/A')}")
    
    print("\n" + "=" * 80)


def print_frame_info(scene_dict_list: List[Dict[str, Any]], frame_idx: int) -> None:
    """
    打印指定帧的详细信息
    
    Args:
        scene_dict_list: 场景字典列表
        frame_idx: 帧索引
    """
    if frame_idx < 0 or frame_idx >= len(scene_dict_list):
        print(f"错误: 帧索引 {frame_idx} 超出范围 [0, {len(scene_dict_list)-1}]")
        return
    
    frame = scene_dict_list[frame_idx]
    
    print("=" * 80)
    print(f"FRAME {frame_idx} DETAILS")
    print("=" * 80)
    
    # 基本信息
    print(f"\n帧索引: {frame.get('frame_idx', 'N/A')}")
    print(f"Token: {frame.get('token', 'N/A')}")
    print(f"场景Token: {frame.get('scene_token', 'N/A')}")
    print(f"时间戳: {frame.get('timestamp', 'N/A')}")
    print(f"日志名称: {frame.get('log_name', 'N/A')}")
    print(f"地图位置: {frame.get('map_location', 'N/A')}")
    
    # 驾驶命令
    print(f"\n驾驶命令: {frame.get('driving_command', 'N/A')}")
    
    # Ego 状态
    if 'ego2global_translation' in frame:
        translation = frame['ego2global_translation']
        print(f"\nEgo全局位置: x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}")
    
    if 'ego2global_rotation' in frame:
        rotation = frame['ego2global_rotation']
        print(f"Ego全局旋转 (quaternion): {rotation}")
    
    if 'ego_dynamic_state' in frame:
        dynamic_state = frame['ego_dynamic_state']
        if len(dynamic_state) >= 2:
            print(f"Ego速度: vx={dynamic_state[0]:.2f}, vy={dynamic_state[1]:.2f}")
        if len(dynamic_state) >= 4:
            print(f"Ego加速度: ax={dynamic_state[2]:.2f}, ay={dynamic_state[3]:.2f}")
    
    # 路线信息
    roadblock_ids = frame.get('roadblock_ids', [])
    print(f"\n路线Roadblock IDs: {roadblock_ids}")
    print(f"路线长度: {len(roadblock_ids)}")
    
    # 交通灯信息
    traffic_lights = frame.get('traffic_lights', [])
    print(f"\n交通灯数量: {len(traffic_lights)}")
    if traffic_lights:
        print(f"交通灯信息: {traffic_lights[:3]}...")  # 只显示前3个
    
    # 传感器信息
    if 'cams' in frame:
        cams = frame['cams']
        if isinstance(cams, dict):
            print(f"\n相机数量: {len(cams)}")
            for cam_name, cam_info in list(cams.items())[:3]:  # 只显示前3个
                print(f"  {cam_name}: {cam_info}")
    
    if 'lidar_path' in frame:
        print(f"\nLiDAR路径: {frame['lidar_path']}")
    
    # 注释信息（如果有）
    if 'annotations' in frame:
        annotations = frame['annotations']
        print(f"\n注释信息:")
        if isinstance(annotations, dict):
            for key, value in annotations.items():
                if isinstance(value, (list, tuple)):
                    print(f"  {key}: {len(value)} 个对象")
                else:
                    print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)


def export_to_json(scene_dict_list: List[Dict[str, Any]], output_path: str, frame_idx: int = None) -> None:
    """
    导出数据到 JSON 文件
    
    Args:
        scene_dict_list: 场景字典列表
        output_path: 输出 JSON 文件路径
        frame_idx: 如果指定，只导出该帧；否则导出所有帧
    """
    output_path = Path(output_path)
    
    if frame_idx is not None:
        if frame_idx < 0 or frame_idx >= len(scene_dict_list):
            print(f"错误: 帧索引 {frame_idx} 超出范围")
            return
        data = scene_dict_list[frame_idx]
    else:
        data = scene_dict_list
    
    # 转换 numpy 数组等不可序列化的对象
    def convert_to_serializable(obj):
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        elif isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_to_serializable(value) for key, value in obj.items()}
        else:
            return obj
    
    serializable_data = convert_to_serializable(data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    
    print(f"数据已导出到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='解析 navsim log pickle 文件')
    parser.add_argument(
        '--pkl_path',
        type=str,
        default='/home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl',
        help='Pickle 文件路径'
    )
    parser.add_argument(
        '--frame_idx',
        type=int,
        default=None,
        help='要查看的帧索引（如果不指定，则显示摘要）'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='显示摘要信息'
    )
    parser.add_argument(
        '--export_json',
        type=str,
        default=None,
        help='导出到 JSON 文件（可选：指定帧索引，如 "output.json:5"）'
    )
    
    args = parser.parse_args()
    
    # 加载 pickle 文件
    try:
        scene_dict_list = load_pickle(args.pkl_path)
        print(f"成功加载 pickle 文件: {args.pkl_path}")
    except Exception as e:
        print(f"加载 pickle 文件失败: {e}")
        return
    
    # 显示摘要
    if args.summary or args.frame_idx is None:
        print_summary(scene_dict_list)
    
    # 显示指定帧的信息
    if args.frame_idx is not None:
        print_frame_info(scene_dict_list, args.frame_idx)
    
    # 导出到 JSON
    if args.export_json:
        export_parts = args.export_json.split(':')
        output_path = export_parts[0]
        frame_idx = int(export_parts[1]) if len(export_parts) > 1 else None
        export_to_json(scene_dict_list, output_path, frame_idx)


if __name__ == '__main__':
    main()
