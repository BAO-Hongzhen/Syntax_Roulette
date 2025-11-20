"""
ComfyUI API调用模块 - ComfyUI API Client
负责与本地ComfyUI服务通信，生成图片
"""

import json
import requests
import websocket
import uuid
import urllib.request
import urllib.parse
import time
from io import BytesIO
from PIL import Image
from typing import Optional, Dict, List
import os


class ComfyUIClient:
    """ComfyUI API客户端"""
    
    def __init__(self, server_address: str = "127.0.0.1:8188", workflow_path: str = "ComfyUI_Workflow/Syntax_Roulette.json"):
        """
        初始化ComfyUI客户端
        
        Args:
            server_address: ComfyUI服务器地址
            workflow_path: 工作流JSON文件路径
        """
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.base_url = f"http://{server_address}"
        self.workflow_path = workflow_path
        self.workflow_template = self._load_workflow_template()
    
    def queue_prompt(self, prompt: Dict) -> Optional[str]:
        """
        将提示词加入队列
        
        Args:
            prompt: 工作流提示词
            
        Returns:
            提示词ID
        """
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        
        try:
            req = urllib.request.Request(f"{self.base_url}/prompt", data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read())
            return result.get('prompt_id')
        except Exception as e:
            print(f"❌ 提交提示词失败: {e}")
            return None
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """
        从ComfyUI获取生成的图像
        
        Args:
            filename: 文件名
            subfolder: 子文件夹
            folder_type: 文件夹类型
            
        Returns:
            图像数据
        """
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        
        try:
            with urllib.request.urlopen(f"{self.base_url}/view?{url_values}") as response:
                return response.read()
        except Exception as e:
            print(f"❌ 获取图像失败: {e}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """
        获取生成历史
        
        Args:
            prompt_id: 提示词ID
            
        Returns:
            历史记录
        """
        try:
            with urllib.request.urlopen(f"{self.base_url}/history/{prompt_id}") as response:
                return json.loads(response.read())
        except Exception as e:
            print(f"❌ 获取历史失败: {e}")
            return None
    
    def track_progress(self, prompt_id: str, timeout: int = 300) -> Optional[Dict]:
        """
        跟踪生成进度
        
        Args:
            prompt_id: 提示词ID
            timeout: 超时时间（秒）
            
        Returns:
            完成的历史记录
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                print(f"❌ 生成超时 ({timeout}秒)")
                return None
            
            history = self.get_history(prompt_id)
            if history and prompt_id in history:
                return history[prompt_id]
            
            time.sleep(1)
    
    def _load_workflow_template(self) -> Optional[Dict]:
        """
        加载工作流模板文件
        
        Returns:
            工作流模板字典
        """
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
                return workflow_data
        except FileNotFoundError:
            print(f"❌ 工作流文件未找到: {self.workflow_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 工作流文件解析失败: {e}")
            return None
    
    def _convert_workflow_to_api_format(self, workflow_data: Dict) -> Dict:
        """
        将ComfyUI GUI格式的工作流转换为API格式
        
        Args:
            workflow_data: GUI格式的工作流数据
            
        Returns:
            API格式的工作流
        """
        api_workflow = {}
        
        # 遍历所有节点
        for node in workflow_data.get('nodes', []):
            node_id = str(node['id'])
            node_type = node['type']
            
            # 构建输入连接
            inputs = {}
            
            # 处理widget值（直接输入的参数）
            if 'widgets_values' in node and node['widgets_values']:
                widget_values = node['widgets_values']
                
                # 根据节点类型设置参数
                if node_type == 'KSampler':
                    inputs['seed'] = widget_values[0] if len(widget_values) > 0 else 0
                    inputs['control_after_generate'] = widget_values[1] if len(widget_values) > 1 else 'fixed'
                    inputs['steps'] = widget_values[2] if len(widget_values) > 2 else 20
                    inputs['cfg'] = widget_values[3] if len(widget_values) > 3 else 7.0
                    inputs['sampler_name'] = widget_values[4] if len(widget_values) > 4 else 'euler'
                    inputs['scheduler'] = widget_values[5] if len(widget_values) > 5 else 'normal'
                    inputs['denoise'] = widget_values[6] if len(widget_values) > 6 else 1.0
                elif node_type == 'EmptyLatentImage':
                    inputs['width'] = widget_values[0] if len(widget_values) > 0 else 512
                    inputs['height'] = widget_values[1] if len(widget_values) > 1 else 512
                    inputs['batch_size'] = widget_values[2] if len(widget_values) > 2 else 1
                elif node_type == 'CLIPTextEncode':
                    inputs['text'] = widget_values[0] if len(widget_values) > 0 else ''
                elif node_type == 'CheckpointLoaderSimple':
                    inputs['ckpt_name'] = widget_values[0] if len(widget_values) > 0 else ''
                elif node_type == 'SaveImage':
                    inputs['filename_prefix'] = widget_values[0] if len(widget_values) > 0 else 'ComfyUI'
            
            # 处理节点间的连接
            if 'inputs' in node:
                for input_slot in node['inputs']:
                    input_name = input_slot['name']
                    if 'link' in input_slot and input_slot['link'] is not None:
                        # 查找链接的源节点
                        link_id = input_slot['link']
                        source_node_id, source_slot = self._find_link_source(workflow_data, link_id)
                        if source_node_id is not None:
                            inputs[input_name] = [str(source_node_id), source_slot]
            
            api_workflow[node_id] = {
                'class_type': node_type,
                'inputs': inputs
            }
        
        return api_workflow
    
    def _find_link_source(self, workflow_data: Dict, link_id: int) -> tuple:
        """
        查找链接的源节点和输出槽
        
        Args:
            workflow_data: 工作流数据
            link_id: 链接ID
            
        Returns:
            (源节点ID, 输出槽索引)
        """
        for link in workflow_data.get('links', []):
            if link[0] == link_id:
                return link[1], link[2]  # 源节点ID, 输出槽索引
        return None, 0
    
    def create_text2image_workflow(self, prompt: str, negative_prompt: str = "",
                                   width: int = 768, height: int = 768) -> Dict:
        """
        基于Syntax_Roulette.json创建文本到图片的工作流
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            
        Returns:
            工作流字典
        """
        if self.workflow_template is None:
            print("❌ 工作流模板未加载")
            return {}
        
        # 转换为API格式
        workflow = self._convert_workflow_to_api_format(self.workflow_template)
        
        # 更新动态参数
        # 节点6: 正面提示词
        if '6' in workflow:
            workflow['6']['inputs']['text'] = prompt
        
        # 节点7: 负面提示词（保留原有的embedding:easynegative，如果没有提供新的）
        if '7' in workflow:
            if negative_prompt:
                workflow['7']['inputs']['text'] = negative_prompt
            # 否则保持原有的 "embedding:easynegative"
        
        # 节点5: 更新尺寸
        if '5' in workflow:
            workflow['5']['inputs']['width'] = width
            workflow['5']['inputs']['height'] = height
            workflow['5']['inputs']['batch_size'] = 1  # 确保只生成一张图
        
        # 节点3: 使用随机种子
        if '3' in workflow:
            workflow['3']['inputs']['seed'] = int(time.time() * 1000)  # 使用毫秒级时间戳
            workflow['3']['inputs']['control_after_generate'] = 'randomize'
        
        return workflow
    
    def generate_image(self, prompt: str, negative_prompt: str = "",
                      width: int = 768, height: int = 768,
                      output_path: Optional[str] = None) -> Optional[str]:
        """
        生成单张图片
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            output_path: 输出路径
            
        Returns:
            生成的图片文件路径
        """
        print(f"🎨 开始生成图片...")
        print(f"   提示词: {prompt}")
        print(f"   尺寸: {width}x{height}")
        
        # 创建工作流
        workflow = self.create_text2image_workflow(
            prompt, negative_prompt, width, height
        )
        
        if not workflow:
            return None
        
        # 提交到队列
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            return None
        
        print(f"✅ 已提交到队列，ID: {prompt_id}")
        print(f"⏳ 等待生成完成...")
        
        # 跟踪进度
        history = self.track_progress(prompt_id)
        if not history:
            return None
        
        # 获取生成的图像
        outputs = history.get("outputs", {})
        image_path = None
        
        for node_id in outputs:
            node_output = outputs[node_id]
            if "images" in node_output:
                for image_data in node_output["images"]:
                    image_bytes = self.get_image(
                        image_data["filename"],
                        image_data.get("subfolder", ""),
                        image_data.get("type", "output")
                    )
                    if image_bytes:
                        # 保存图片
                        if output_path is None:
                            timestamp = int(time.time())
                            output_path = f"output/syntax_roulette_{timestamp}.png"
                        
                        # 确保输出目录存在
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        # 保存图片
                        image = Image.open(BytesIO(image_bytes))
                        image.save(output_path)
                        image_path = output_path
                        
                        print(f"✅ 图片生成成功: {output_path}")
                        return image_path
        
        print(f"❌ 未获取到图像")
        return None
    
    def test_connection(self) -> bool:
        """
        测试与ComfyUI的连接
        
        Returns:
            连接是否成功
        """
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            if response.status_code == 200:
                print(f"✅ ComfyUI连接成功: {self.base_url}")
                stats = response.json()
                print(f"   系统信息: {stats}")
                return True
            else:
                print(f"❌ ComfyUI连接失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ ComfyUI连接失败: {e}")
            print(f"   请确保ComfyUI正在运行于 {self.base_url}")
            return False


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = ComfyUIClient()
    
    # 测试连接
    print("测试ComfyUI连接...")
    if client.test_connection():
        print("\n尝试生成图片（需要ComfyUI运行）...")
        
        # 生成图片
        image_path = client.generate_image(
            prompt="a cat sitting happily in a beautiful garden",
            negative_prompt="blurry, bad quality",
            width=768,
            height=768
        )
        
        if image_path:
            print(f"\n🎉 图片已保存到: {image_path}")
    else:
        print("\n⚠️ 演示模式：请先启动ComfyUI服务")
        print("   启动命令: python main.py (在ComfyUI目录)")
