"""
Gradio文本生图界面
基于ComfyUI工作流的文本到图像生成应用
"""

import gradio as gr
import json
import requests
import io
import time
from PIL import Image
import random
import numpy as np
from text_to_image import TextToImageWorkflow


class GradioImageGenerator:
    """Gradio图像生成器"""
    
    def __init__(self):
        self.workflow = TextToImageWorkflow()
        self.history = []
    
    def generate_image_demo(self, width, height, seed):
        """
        演示模式：生成随机演示图像
        实际使用时需要连接ComfyUI API
        """
        # 创建随机渐变图像作为演示
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 根据种子生成随机颜色
        random.seed(seed)
        
        color1 = [random.randint(50, 200) for _ in range(3)]
        color2 = [random.randint(50, 200) for _ in range(3)]
        
        for i in range(height):
            ratio = i / height
            for j in range(width):
                for c in range(3):
                    img_array[i, j, c] = int(color1[c] * (1 - ratio) + color2[c] * ratio)
        
        img = Image.fromarray(img_array)
        return img
    
    def send_to_comfyui(self, comfyui_url="http://127.0.0.1:8188"):
        """
        发送工作流到ComfyUI API（实际使用版本）
        需要ComfyUI服务运行在本地或远程
        """
        try:
            # 生成客户端ID
            client_id = str(random.randint(0, 1000000))
            
            # 准备工作流数据
            prompt = {"prompt": self.workflow.workflow, "client_id": client_id}
            
            # 发送到ComfyUI
            response = requests.post(f"{comfyui_url}/prompt", json=prompt, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get('prompt_id')
                
                # 等待生成完成（最多等待60秒）
                max_wait = 60
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    history = requests.get(f"{comfyui_url}/history/{prompt_id}", timeout=5)
                    if history.status_code == 200:
                        hist_data = history.json()
                        if prompt_id in hist_data:
                            # 获取生成的图像
                            outputs = hist_data[prompt_id].get('outputs', {})
                            for node_id, node_output in outputs.items():
                                if 'images' in node_output:
                                    for img_data in node_output['images']:
                                        filename = img_data['filename']
                                        subfolder = img_data.get('subfolder', '')
                                        
                                        # 下载图像
                                        img_response = requests.get(
                                            f"{comfyui_url}/view",
                                            params={"filename": filename, "subfolder": subfolder},
                                            timeout=10
                                        )
                                        if img_response.status_code == 200:
                                            return Image.open(io.BytesIO(img_response.content))
                            break
                    time.sleep(1)
            
            return None
        except Exception as e:
            print(f"连接ComfyUI失败: {str(e)}")
            return None
    
    def generate(self, positive_prompt, negative_prompt, width, height, steps, cfg, 
                sampler, scheduler, denoise, seed, use_random_seed, use_comfyui, 
                comfyui_url, checkpoint):
        """
        生成图像的主函数
        """
        try:
            # 处理种子
            if use_random_seed:
                seed = random.randint(0, 2**32 - 1)
            
            # 验证输入
            if not positive_prompt.strip():
                return None, "⚠️ 请输入正面提示词", self.get_info_text("", "", 0, 0, 0, 0)
            
            # 更新工作流参数
            self.workflow.update_checkpoint(checkpoint)
            self.workflow.update_prompt(positive_prompt, negative_prompt)
            self.workflow.update_image_size(width, height)
            self.workflow.update_sampling_params(
                seed=seed,
                steps=steps,
                cfg=cfg,
                sampler_name=sampler,
                scheduler=scheduler,
                denoise=denoise
            )
            
            # 生成图像
            status_msg = "🎨 正在生成图像..."
            
            if use_comfyui:
                status_msg = f"🎨 正在连接ComfyUI ({comfyui_url})..."
                generated_img = self.send_to_comfyui(comfyui_url)
                
                if generated_img is None:
                    status_msg = "⚠️ ComfyUI连接失败，切换到演示模式"
                    generated_img = self.generate_image_demo(width, height, seed)
                else:
                    status_msg = "✅ 图像生成完成！"
            else:
                status_msg = "📌 演示模式：生成预览图像（非真实AI生成）"
                generated_img = self.generate_image_demo(width, height, seed)
            
            # 保存历史记录
            history_item = {
                "positive": positive_prompt,
                "negative": negative_prompt,
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "size": f"{width}x{height}",
                "image": generated_img
            }
            self.history.insert(0, history_item)
            
            # 限制历史记录数量
            if len(self.history) > 10:
                self.history = self.history[:10]
            
            # 生成信息文本
            info_text = self.get_info_text(positive_prompt, negative_prompt, width, height, steps, cfg, seed)
            
            return generated_img, status_msg, info_text
            
        except Exception as e:
            return None, f"❌ 生成失败: {str(e)}", ""
    
    def get_info_text(self, positive, negative, width, height, steps, cfg, seed=0):
        """生成参数信息文本"""
        info = f"""
### 生成参数

**正面提示词:**
{positive[:200]}{'...' if len(positive) > 200 else ''}

**负面提示词:**
{negative[:200]}{'...' if len(negative) > 200 else ''}

**图像尺寸:** {width} x {height}
**采样步数:** {steps}
**CFG Scale:** {cfg}
**随机种子:** {seed}
"""
        return info
    
    def apply_preset_landscape(self):
        """应用风景预设"""
        return "beautiful landscape, mountains, lake, sunset, dramatic sky, 8k, masterpiece, high quality"
    
    def apply_preset_portrait(self):
        """应用人物预设"""
        return "portrait, beautiful person, detailed face, professional photography, studio lighting, high quality"
    
    def apply_preset_art(self):
        """应用艺术预设"""
        return "artistic, oil painting, vibrant colors, masterpiece, highly detailed, fine art"
    
    def apply_preset_city(self):
        """应用城市预设"""
        return "city skyline, modern architecture, night scene, neon lights, urban landscape, 8k, detailed"
    
    def get_history_gallery(self):
        """获取历史记录图库"""
        if not self.history:
            return []
        return [item["image"] for item in self.history]


def create_interface():
    """创建Gradio界面"""
    
    generator = GradioImageGenerator()
    
    # 创建界面
    with gr.Blocks(title="AI文本生图工具", theme=gr.themes.Soft()) as app:
        
        gr.Markdown(
            """
            # 🎨 AI文本生图工具
            基于ComfyUI工作流的文本到图像生成应用
            """
        )
        
        with gr.Row():
            # 左侧：主要控制区域
            with gr.Column(scale=2):
                # 提示词输入
                with gr.Group():
                    gr.Markdown("### 📝 提示词")
                    
                    positive_prompt = gr.Textbox(
                        label="正面提示词 (Positive Prompt)",
                        placeholder="描述你想要生成的图像，如：beautiful landscape, mountains, sunset, 8k, masterpiece",
                        lines=4,
                        value="1girl showering"
                    )
                    
                    negative_prompt = gr.Textbox(
                        label="负面提示词 (Negative Prompt)",
                        placeholder="描述你不想在图像中出现的内容，如：bad quality, blurry, watermark",
                        lines=3,
                        value="embedding:easynegative,people"
                    )
                    
                    # 快速预设按钮
                    gr.Markdown("**快速预设:**")
                    with gr.Row():
                        btn_landscape = gr.Button("🏞️ 风景", size="sm")
                        btn_portrait = gr.Button("👤 人物", size="sm")
                        btn_art = gr.Button("🎨 艺术", size="sm")
                        btn_city = gr.Button("🌃 城市", size="sm")
                
                # 图像尺寸
                with gr.Group():
                    gr.Markdown("### 📐 图像尺寸")
                    with gr.Row():
                        width = gr.Slider(
                            minimum=256,
                            maximum=2048,
                            step=64,
                            value=768,
                            label="宽度"
                        )
                        height = gr.Slider(
                            minimum=256,
                            maximum=2048,
                            step=64,
                            value=768,
                            label="高度"
                        )
                
                # 采样参数
                with gr.Group():
                    gr.Markdown("### ⚙️ 采样参数")
                    
                    steps = gr.Slider(
                        minimum=1,
                        maximum=150,
                        step=1,
                        value=25,
                        label="采样步数",
                        info="更多步数通常产生更好的质量，但需要更长时间"
                    )
                    
                    cfg = gr.Slider(
                        minimum=1.0,
                        maximum=30.0,
                        step=0.5,
                        value=6.5,
                        label="CFG Scale",
                        info="提示词引导强度，值越高越贴近提示词"
                    )
                    
                    with gr.Row():
                        sampler = gr.Dropdown(
                            choices=[
                                "euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral",
                                "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral",
                                "dpmpp_sde", "dpmpp_2m", "dpmpp_2m_sde", "ddim", "uni_pc"
                            ],
                            value="dpmpp_2m",
                            label="采样器"
                        )
                        
                        scheduler = gr.Dropdown(
                            choices=["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"],
                            value="karras",
                            label="调度器"
                        )
                    
                    denoise = gr.Slider(
                        minimum=0.0,
                        maximum=1.0,
                        step=0.05,
                        value=1.0,
                        label="去噪强度"
                    )
                
                # 高级设置
                with gr.Accordion("🔧 高级设置", open=False):
                    checkpoint = gr.Textbox(
                        label="模型检查点",
                        value="majicmixRealistic_v7.safetensors",
                        info="输入模型文件名"
                    )
                    
                    use_random_seed = gr.Checkbox(
                        label="使用随机种子",
                        value=True
                    )
                    
                    seed = gr.Number(
                        label="种子值",
                        value=373330229574459,
                        precision=0,
                        interactive=True
                    )
                    
                    use_comfyui = gr.Checkbox(
                        label="连接ComfyUI服务",
                        value=False,
                        info="勾选后将尝试连接本地或远程ComfyUI服务"
                    )
                    
                    comfyui_url = gr.Textbox(
                        label="ComfyUI地址",
                        value="http://127.0.0.1:8188",
                        interactive=True
                    )
                
                # 生成按钮
                with gr.Row():
                    generate_btn = gr.Button("🎨 生成图像", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清除", size="lg")
            
            # 右侧：结果显示区域
            with gr.Column(scale=2):
                # 状态信息
                status_text = gr.Markdown("准备就绪，请输入提示词后点击生成")
                
                # 生成的图像
                output_image = gr.Image(
                    label="生成结果",
                    type="pil",
                    height=600
                )
                
                # 参数信息
                info_text = gr.Markdown("")
        
        # 历史记录
        with gr.Accordion("📚 历史记录", open=False):
            history_gallery = gr.Gallery(
                label="历史生成记录",
                columns=4,
                rows=2,
                height="auto"
            )
            refresh_history_btn = gr.Button("🔄 刷新历史记录")
        
        # 页脚信息
        gr.Markdown(
            """
            ---
            💡 **提示:** 勾选"连接ComfyUI服务"以使用真实的AI图像生成功能。当前为演示模式，生成的是预览图像。
            """
        )
        
        # 事件绑定
        
        # 快速预设按钮
        btn_landscape.click(
            fn=generator.apply_preset_landscape,
            inputs=[],
            outputs=positive_prompt
        )
        
        btn_portrait.click(
            fn=generator.apply_preset_portrait,
            inputs=[],
            outputs=positive_prompt
        )
        
        btn_art.click(
            fn=generator.apply_preset_art,
            inputs=[],
            outputs=positive_prompt
        )
        
        btn_city.click(
            fn=generator.apply_preset_city,
            inputs=[],
            outputs=positive_prompt
        )
        
        # 生成按钮
        generate_btn.click(
            fn=generator.generate,
            inputs=[
                positive_prompt, negative_prompt, width, height, steps, cfg,
                sampler, scheduler, denoise, seed, use_random_seed, use_comfyui,
                comfyui_url, checkpoint
            ],
            outputs=[output_image, status_text, info_text]
        )
        
        # 清除按钮
        clear_btn.click(
            fn=lambda: (None, "已清除", ""),
            inputs=[],
            outputs=[output_image, status_text, info_text]
        )
        
        # 刷新历史记录
        refresh_history_btn.click(
            fn=generator.get_history_gallery,
            inputs=[],
            outputs=history_gallery
        )
        
        # 随机种子复选框
        use_random_seed.change(
            fn=lambda x: gr.update(interactive=not x),
            inputs=use_random_seed,
            outputs=seed
        )
        
        # ComfyUI连接复选框
        use_comfyui.change(
            fn=lambda x: gr.update(interactive=x),
            inputs=use_comfyui,
            outputs=comfyui_url
        )
    
    return app


if __name__ == "__main__":
    # 创建并启动应用
    app = create_interface()
    
    # 启动服务器
    app.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,        # 端口号
        share=False,             # 不创建公共链接
        show_error=True          # 显示详细错误
    )
