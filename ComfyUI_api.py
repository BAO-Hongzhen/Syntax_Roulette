"""
ComfyUI API调用模块 - ComfyUI API Client
负责与本地ComfyUI服务通信，生成图片
"""

import json
import requests
import uuid
import urllib.request
import urllib.parse
import time
from io import BytesIO
from PIL import Image
from typing import Optional, Dict
import os


class ComfyUIClient:
    """ComfyUI API客户端"""
    
    def __init__(self, server_address: str = "127.0.0.1:8188", workflow_path: str = "ComfyUI_Workflow/paper_cut.json"):
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
        """将提示词加入队列"""
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        
        try:
            req = urllib.request.Request(f"{self.base_url}/prompt", data=data)
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read())
            return result.get('prompt_id')
        except Exception as e:
            print(f"❌ 提交提示词失败: {e}")
            return None
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """从ComfyUI获取生成的图像"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        
        try:
            with urllib.request.urlopen(f"{self.base_url}/view?{url_values}", timeout=30) as response:
                return response.read()
        except Exception as e:
            print(f"❌ 获取图像失败: {e}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """获取生成历史"""
        try:
            with urllib.request.urlopen(f"{self.base_url}/history/{prompt_id}", timeout=10) as response:
                return json.loads(response.read())
        except Exception as e:
            return None
    
    def track_progress(self, prompt_id: str, timeout: int = 300) -> Optional[Dict]:
        """跟踪生成进度"""
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
        """加载工作流模板文件"""
        try:
            with open(self.workflow_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ 工作流文件加载失败: {e}")
            return None
    
    def _convert_workflow_to_api_format(self, workflow_data: Dict) -> Dict:
        """将ComfyUI GUI格式的工作流转换为API格式"""
        api_workflow = {}
        
        for node in workflow_data.get('nodes', []):
            node_id = str(node['id'])
            node_type = node['type']
            inputs = {}
            
            if 'widgets_values' in node and node['widgets_values']:
                widget_values = node['widgets_values']
                
                if node_type == 'KSampler':
                    inputs['seed'] = widget_values[0] if len(widget_values) > 0 else 0
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
            
            if 'inputs' in node:
                for input_slot in node['inputs']:
                    input_name = input_slot['name']
                    if 'link' in input_slot and input_slot['link'] is not None:
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
        """查找链接的源节点"""
        for link in workflow_data.get('links', []):
            if link[0] == link_id:
                return link[1], link[2]
        return None, 0
    
    def generate_image(self, prompt: str, negative_prompt: str = "",
                      width: int = 768, height: int = 768) -> Optional[Image.Image]:
        """
        生成图片
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            
        Returns:
            PIL Image对象
        """
        print(f"🎨 开始生成图片...")
        print(f"   提示词: {prompt}")
        
        if self.workflow_template is None:
            print("❌ 工作流模板未加载")
            return None
        
        workflow = self._convert_workflow_to_api_format(self.workflow_template)
        
        # 更新提示词参数（根据实际工作流节点ID调整）
        for node_id, node_data in workflow.items():
            if node_data['class_type'] == 'CLIPTextEncode':
                if 'text' in node_data['inputs']:
                    if negative_prompt and 'negative' in str(node_data['inputs'].get('text', '')).lower():
                        node_data['inputs']['text'] = negative_prompt
                    else:
                        node_data['inputs']['text'] = prompt
            elif node_data['class_type'] == 'EmptyLatentImage':
                node_data['inputs']['width'] = width
                node_data['inputs']['height'] = height
            elif node_data['class_type'] == 'KSampler':
                node_data['inputs']['seed'] = int(time.time() * 1000)
        
        prompt_id = self.queue_prompt(workflow)
        if not prompt_id:
            return None
        
        print(f"✅ 已提交到队列，ID: {prompt_id}")
        
        history = self.track_progress(prompt_id, timeout=300)
        if not history:
            return None
        
        outputs = history.get("outputs", {})
        
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
                        print(f"✅ 图片生成成功")
                        return Image.open(BytesIO(image_bytes))
        
        print(f"❌ 未获取到图像")
        return None
    
    def test_connection(self) -> bool:
        """测试与ComfyUI的连接"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
