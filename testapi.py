"""
ComfyUI API调用模块 - ComfyUI API Client
负责与本地ComfyUI服务通信，生成图片
使用 comfy_api_simplified 库简化调用流程
"""

import random
import asyncio
import os
from pathlib import Path
from typing import Optional
from PIL import Image
from io import BytesIO

try:
    from comfy_api_simplified import ComfyApiWrapper, ComfyWorkflowWrapper
    COMFY_API_AVAILABLE = True
except ImportError:
    COMFY_API_AVAILABLE = False
    print("⚠️ comfy-api-simplified 未安装，请运行: pip install comfy-api-simplified")


class ComfyUIClient:
    """ComfyUI API客户端 - 使用 comfy_api_simplified 简化版本"""
    
    # 内置的剪纸风格提示词模板
    PAPERCUT_STYLE_PROMPTS = [
        "A vibrant red Chinese paper cut art, featuring {subject}, intricate Chinese traditional patterns, "
        "complex geometric designs, swirling clouds and stylized patterns. The background is pure white, "
        "emphasizing a bold traditional design. High contrast, sharp edges, symmetrical composition.",
        
        "Traditional Chinese paper cutting style, {subject} depicted in elegant red silhouette, "
        "with delicate decorative borders and auspicious cloud motifs. Pure white background, "
        "folk art style, festive and cultural atmosphere.",
        
        "Chinese New Year paper cut design, {subject} surrounded by prosperity symbols, "
        "red paper cutting art with fine details, traditional Chinese aesthetics, "
        "white background, celebration theme, intricate linework.",
        
        "Chinese zodiac paper cut style, {subject} with traditional Chinese elements, "
        "red color dominant, white negative space, symmetrical design, "
        "cultural patterns, festive decoration art.",
        
        "Modern Chinese paper cutting art, {subject} in contemporary interpretation, "
        "bold red silhouette, minimalist white background, clean lines, "
        "fusion of traditional and modern aesthetics."
    ]
    
    def __init__(self, server_address: str = "127.0.0.1:8188", 
                 workflow_path: str = "ComfyUI_Workflow/paper_cut.json"):
        """
        初始化ComfyUI客户端
        
        Args:
            server_address: ComfyUI服务器地址
            workflow_path: 工作流JSON文件路径
        """
        if not COMFY_API_AVAILABLE:
            raise ImportError("comfy-api-simplified 未安装，无法使用 ComfyUI 功能")
        
        self.server_address = server_address
        self.base_url = f"http://{server_address}/"
        self.workflow_path = Path(workflow_path)
        
        # 初始化 API 包装器
        self.api = ComfyApiWrapper(self.base_url)
        self.workflow = None
        
        # 加载工作流
        if self.workflow_path.exists():
            try:
                self.workflow = ComfyWorkflowWrapper(str(self.workflow_path))
                print(f"✅ 工作流加载成功: {self.workflow_path}")
            except Exception as e:
                print(f"⚠️ 工作流加载失败: {e}")
        else:
            print(f"⚠️ 工作流文件不存在: {self.workflow_path}")
    
    def _build_full_prompt(self, user_prompt: str, style_index: int = 0) -> str:
        """
        构建完整的提示词，将用户输入嵌入到风格模板中
        
        Args:
            user_prompt: 用户输入的描述
            style_index: 风格模板索引（0-4）
            
        Returns:
            完整的提示词
        """
        # 确保索引在有效范围内
        style_index = max(0, min(style_index, len(self.PAPERCUT_STYLE_PROMPTS) - 1))
        
        # 从模板中生成完整提示词
        template = self.PAPERCUT_STYLE_PROMPTS[style_index]
        full_prompt = template.format(subject=user_prompt)
        
        return full_prompt
    
    def generate_image(self, prompt: str, negative_prompt: str = "",
                      width: int = 1024, height: int = 1024,
                      style_index: int = 0) -> Optional[Image.Image]:
        """
        生成图片 - 核心方法
        
        Args:
            prompt: 用户输入的正面提示词（会被嵌入到风格模板中）
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            style_index: 风格模板索引（0-4，对应不同的剪纸风格）
            
        Returns:
            PIL Image对象
        """
        if self.workflow is None:
            print("❌ 工作流未加载，无法生成图片")
            return None
        
        print(f"🎨 开始生成剪纸图片...")
        print(f"   用户输入: {prompt}")
        print(f"   图片尺寸: {width}x{height}")
        
        try:
            # 构建完整的提示词（嵌入风格模板）
            full_prompt = self._build_full_prompt(prompt, style_index)
            print(f"   完整提示词: {full_prompt[:100]}...")
            
            # 设置随机种子
            random_seed = random.randint(1, 2**32 - 1)
            self.workflow.set_node_param("KSampler", "seed", random_seed)
            print(f"   随机种子: {random_seed}")
            
            # 设置图片尺寸（查找正确的节点名称）
            # 根据 paper_cut.json，节点名称可能是 "EmptySD3LatentImage"
            try:
                self.workflow.set_node_param("EmptySD3LatentImage", "width", width)
                self.workflow.set_node_param("EmptySD3LatentImage", "height", height)
                self.workflow.set_node_param("EmptySD3LatentImage", "batch_size", 1)
            except:
                # 备用方案：尝试其他可能的节点名称
                try:
                    self.workflow.set_node_param("Empty Latent Image", "width", width)
                    self.workflow.set_node_param("Empty Latent Image", "height", height)
                    self.workflow.set_node_param("Empty Latent Image", "batch_size", 1)
                except:
                    print("⚠️ 无法设置图片尺寸，使用默认值")
            
            # 设置提示词（正面）
            # CLIPTextEncodeFlux 有 3 个参数：[clip_l, t5xxl, guidance]
            # 我们需要修改前两个文本参数
            try:
                # 注意：comfy_api_simplified 使用 widgets_values 数组索引
                # 参数名应该是实际的输入参数名，查看 ComfyUI 节点定义
                self.workflow.set_node_param("CLIPTextEncodeFlux", "clip_l", full_prompt)
                self.workflow.set_node_param("CLIPTextEncodeFlux", "t5xxl", full_prompt)
                print("✅ 提示词设置成功")
            except Exception as e:
                print(f"⚠️ 无法设置提示词: {e}")
            
            # 设置负面提示词（如果有）
            if negative_prompt:
                try:
                    self.workflow.set_node_param("negative", "text", negative_prompt)
                except:
                    pass
            
            # 提交工作流并等待结果
            print("⏳ 提交到 ComfyUI 队列，等待生成...")
            
            # 使用 asyncio 运行异步任务
            results = asyncio.run(
                self.api.queue_and_wait_images(self.workflow, "Save Image")
            )
            
            # 获取生成的图片
            if results:
                for filename, image_data in results.items():
                    print(f"✅ 图片生成成功: {filename}")
                    
                    # 将字节数据转换为 PIL Image
                    if isinstance(image_data, bytes):
                        return Image.open(BytesIO(image_data))
                    elif isinstance(image_data, Image.Image):
                        return image_data
                    else:
                        print(f"⚠️ 未知的图片数据类型: {type(image_data)}")
            
            print("❌ 未获取到图像数据")
            return None
            
        except Exception as e:
            print(f"❌ 图片生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_connection(self) -> bool:
        """
        测试与ComfyUI的连接
        
        Returns:
            连接是否成功
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}system_stats", timeout=5)
            if response.status_code == 200:
                print(f"✅ ComfyUI连接成功: {self.base_url}")
                return True
            else:
                print(f"❌ ComfyUI连接失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ComfyUI连接失败: {e}")
            print(f"   请确保ComfyUI正在运行于 {self.base_url}")
            return False
