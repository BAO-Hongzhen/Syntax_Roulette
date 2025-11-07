"""
ComfyUI Text-to-Image Workflow
将JSON工作流转换为Python脚本
"""

import json
import random


class TextToImageWorkflow:
    """文本到图像生成工作流"""
    
    def __init__(self):
        self.workflow = {}
        self.setup_workflow()
    
    def setup_workflow(self):
        """设置工作流节点"""
        
        # 节点11: 加载检查点模型
        self.workflow["11"] = {
            "inputs": {
                "ckpt_name": "majicmixRealistic_v7.safetensors"
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {
                "title": "Load Checkpoint"
            }
        }
        
        # 节点6: 正面提示词编码
        self.workflow["6"] = {
            "inputs": {
                "text": "1girl showering",
                "clip": ["11", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Prompt)"
            }
        }
        
        # 节点7: 负面提示词编码
        self.workflow["7"] = {
            "inputs": {
                "text": "embedding:easynegative,people",
                "clip": ["11", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Prompt)"
            }
        }
        
        # 节点5: 空白潜在图像
        self.workflow["5"] = {
            "inputs": {
                "width": 768,
                "height": 768,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage",
            "_meta": {
                "title": "Empty Latent Image"
            }
        }
        
        # 节点3: KSampler采样器
        self.workflow["3"] = {
            "inputs": {
                "seed": 373330229574459,
                "steps": 25,
                "cfg": 6.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1,
                "model": ["11", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler",
            "_meta": {
                "title": "KSampler"
            }
        }
        
        # 节点8: VAE解码
        self.workflow["8"] = {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["11", 2]
            },
            "class_type": "VAEDecode",
            "_meta": {
                "title": "VAE Decode"
            }
        }
        
        # 节点9: 保存图像
        self.workflow["9"] = {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage",
            "_meta": {
                "title": "Save Image"
            }
        }
    
    def update_prompt(self, positive_prompt=None, negative_prompt=None):
        """更新提示词"""
        if positive_prompt:
            self.workflow["6"]["inputs"]["text"] = positive_prompt
        if negative_prompt:
            self.workflow["7"]["inputs"]["text"] = negative_prompt
    
    def update_image_size(self, width=None, height=None):
        """更新图像尺寸"""
        if width:
            self.workflow["5"]["inputs"]["width"] = width
        if height:
            self.workflow["5"]["inputs"]["height"] = height
    
    def update_sampling_params(self, seed=None, steps=None, cfg=None, 
                              sampler_name=None, scheduler=None, denoise=None):
        """更新采样参数"""
        if seed is not None:
            self.workflow["3"]["inputs"]["seed"] = seed
        if steps is not None:
            self.workflow["3"]["inputs"]["steps"] = steps
        if cfg is not None:
            self.workflow["3"]["inputs"]["cfg"] = cfg
        if sampler_name:
            self.workflow["3"]["inputs"]["sampler_name"] = sampler_name
        if scheduler:
            self.workflow["3"]["inputs"]["scheduler"] = scheduler
        if denoise is not None:
            self.workflow["3"]["inputs"]["denoise"] = denoise
    
    def update_checkpoint(self, ckpt_name):
        """更新检查点模型"""
        self.workflow["11"]["inputs"]["ckpt_name"] = ckpt_name
    
    def update_filename_prefix(self, prefix):
        """更新输出文件名前缀"""
        self.workflow["9"]["inputs"]["filename_prefix"] = prefix
    
    def randomize_seed(self):
        """随机化种子"""
        self.workflow["3"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
    
    def get_workflow_json(self):
        """获取工作流的JSON格式"""
        return json.dumps(self.workflow, indent=2)
    
    def save_workflow(self, filename="workflow.json"):
        """保存工作流到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.workflow, f, indent=2)
        print(f"工作流已保存到 {filename}")
    
    def print_workflow_info(self):
        """打印工作流信息"""
        print("=" * 60)
        print("文本到图像生成工作流")
        print("=" * 60)
        print(f"检查点模型: {self.workflow['11']['inputs']['ckpt_name']}")
        print(f"正面提示词: {self.workflow['6']['inputs']['text']}")
        print(f"负面提示词: {self.workflow['7']['inputs']['text']}")
        print(f"图像尺寸: {self.workflow['5']['inputs']['width']}x{self.workflow['5']['inputs']['height']}")
        print(f"采样步数: {self.workflow['3']['inputs']['steps']}")
        print(f"CFG强度: {self.workflow['3']['inputs']['cfg']}")
        print(f"采样器: {self.workflow['3']['inputs']['sampler_name']}")
        print(f"调度器: {self.workflow['3']['inputs']['scheduler']}")
        print(f"种子: {self.workflow['3']['inputs']['seed']}")
        print(f"去噪强度: {self.workflow['3']['inputs']['denoise']}")
        print(f"文件名前缀: {self.workflow['9']['inputs']['filename_prefix']}")
        print("=" * 60)


# 使用示例
if __name__ == "__main__":
    # 创建工作流实例
    workflow = TextToImageWorkflow()
    
    # 打印原始工作流信息
    print("\n原始工作流配置:")
    workflow.print_workflow_info()
    
    # 示例: 自定义工作流参数
    print("\n\n修改工作流参数...")
    workflow.update_prompt(
        positive_prompt="beautiful landscape, mountains, sunset, 8k, masterpiece",
        negative_prompt="bad quality, blurry, watermark"
    )
    workflow.update_image_size(width=1024, height=768)
    workflow.update_sampling_params(steps=30, cfg=7.5)
    workflow.randomize_seed()
    workflow.update_filename_prefix("my_image")
    
    # 打印修改后的工作流信息
    print("\n修改后的工作流配置:")
    workflow.print_workflow_info()
    
    # 保存工作流
    print("\n")
    workflow.save_workflow("text_to_image_workflow.json")
    
    # 打印JSON格式
    print("\n工作流JSON格式:")
    print(workflow.get_workflow_json())
