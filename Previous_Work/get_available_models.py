"""
获取 ComfyUI 中可用的模型列表
"""

import requests
import json

def get_available_models():
    """获取可用模型"""
    try:
        print("🔍 正在获取 ComfyUI 可用模型...\n")
        
        # 获取对象信息
        response = requests.get('http://127.0.0.1:8000/object_info', timeout=5)
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return
        
        data = response.json()
        
        # 获取checkpoint列表
        checkpoint_info = data.get('CheckpointLoaderSimple', {})
        input_info = checkpoint_info.get('input', {})
        required_info = input_info.get('required', {})
        ckpt_name_info = required_info.get('ckpt_name', [[]])
        checkpoints = ckpt_name_info[0] if ckpt_name_info else []
        
        if not checkpoints:
            print("❌ 没有找到任何模型文件！")
            print("\n💡 解决方法:")
            print("   1. 下载 Stable Diffusion 模型（.safetensors 或 .ckpt 文件）")
            print("   2. 将模型放到 ComfyUI 的 models/checkpoints 目录")
            print("   3. 重启 ComfyUI")
            print("\n推荐模型:")
            print("   - SD 1.5: https://huggingface.co/runwayml/stable-diffusion-v1-5")
            print("   - SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")
            return None
        
        print(f"✅ 找到 {len(checkpoints)} 个可用模型:\n")
        
        for i, model in enumerate(checkpoints, 1):
            print(f"  {i}. {model}")
        
        print(f"\n💡 建议使用第一个模型: {checkpoints[0]}")
        print(f"\n📝 请修改 comfyui_api.py 中的模型名称:")
        print(f'   "ckpt_name": "{checkpoints[0]}"')
        
        return checkpoints
        
    except Exception as e:
        print(f"❌ 获取模型失败: {e}")
        return None


if __name__ == "__main__":
    models = get_available_models()
