"""
Syntax Roulette - AI文本生图主程序
只需运行此文件即可启动Web界面

使用方法:
    python main.py

然后在浏览器中打开显示的地址（通常是 http://localhost:7860）
"""

import gradio as gr
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import time


class SyntaxRouletteApp:
    """Syntax Roulette应用主类"""
    
    def __init__(self):
        self.generation_history = []
        self.current_seed = random.randint(0, 2**32 - 1)
    
    def generate_demo_image(self, prompt, width, height, seed):
        """
        生成演示图像
        实际项目中可以接入ComfyUI或其他AI图像生成服务
        """
        # 创建画布
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 根据种子生成随机渐变背景
        random.seed(seed)
        color1 = tuple([random.randint(100, 255) for _ in range(3)])
        color2 = tuple([random.randint(50, 200) for _ in range(3)])
        
        # 绘制渐变背景
        for y in range(height):
            ratio = y / height
            color = tuple([
                int(color1[i] * (1 - ratio) + color2[i] * ratio)
                for i in range(3)
            ])
            draw.line([(0, y), (width, y)], fill=color)
        
        # 添加装饰性元素
        num_circles = random.randint(3, 8)
        for _ in range(num_circles):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(20, 100)
            circle_color = tuple([random.randint(100, 255) for _ in range(3)])
            draw.ellipse([x-r, y-r, x+r, y+r], fill=circle_color, outline=None)
        
        # 添加提示词文字（如果图像足够大）
        if width >= 400 and height >= 300:
            try:
                # 在图像上绘制提示词
                text = prompt[:50] + "..." if len(prompt) > 50 else prompt
                
                # 创建文字背景
                text_bbox = draw.textbbox((0, 0), text)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                padding = 20
                text_x = (width - text_width) // 2
                text_y = height - text_height - 30
                
                # 半透明背景
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle(
                    [text_x - padding, text_y - padding, 
                     text_x + text_width + padding, text_y + text_height + padding],
                    fill=(0, 0, 0, 180)
                )
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                
                # 绘制文字
                draw.text((text_x, text_y), text, fill='white')
            except:
                pass  # 如果字体不可用，跳过文字绘制
        
        return img
    
    def generate_image(self, prompt, negative_prompt, width, height, 
                      quality, style, use_random_seed, seed_value, progress=gr.Progress()):
        """
        主图像生成函数
        """
        try:
            # 验证输入
            if not prompt or prompt.strip() == "":
                return None, "❌ 错误：请输入描述文本！", ""
            
            # 处理种子
            if use_random_seed:
                seed = random.randint(0, 2**32 - 1)
            else:
                seed = int(seed_value)
            
            self.current_seed = seed
            
            # 根据质量和风格调整提示词
            enhanced_prompt = self.enhance_prompt(prompt, quality, style)
            
            # 显示进度
            progress(0, desc="开始生成...")
            time.sleep(0.2)
            
            progress(0.3, desc="处理提示词...")
            time.sleep(0.2)
            
            progress(0.6, desc="生成图像中...")
            # 生成图像
            generated_image = self.generate_demo_image(enhanced_prompt, width, height, seed)
            
            progress(0.9, desc="完成...")
            time.sleep(0.1)
            
            # 保存到历史
            self.generation_history.insert(0, {
                "image": generated_image,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "negative": negative_prompt,
                "seed": seed,
                "size": f"{width}x{height}",
                "quality": quality,
                "style": style
            })
            
            # 限制历史数量
            if len(self.generation_history) > 20:
                self.generation_history = self.generation_history[:20]
            
            # 生成信息文本
            info_text = self.create_info_text(prompt, enhanced_prompt, negative_prompt, 
                                              width, height, seed, quality, style)
            
            status = f"✅ 生成成功！种子值: {seed}"
            
            return generated_image, status, info_text
            
        except Exception as e:
            return None, f"❌ 生成失败: {str(e)}", ""
    
    def enhance_prompt(self, prompt, quality, style):
        """根据质量和风格增强提示词"""
        enhanced = prompt
        
        # 添加质量关键词
        quality_keywords = {
            "低": "",
            "中": "good quality",
            "高": "high quality, detailed",
            "超高": "masterpiece, best quality, highly detailed, 8k"
        }
        
        # 添加风格关键词
        style_keywords = {
            "默认": "",
            "写实": "realistic, photorealistic, professional photography",
            "动漫": "anime style, manga, illustration",
            "油画": "oil painting, artistic, fine art",
            "水彩": "watercolor, soft colors, artistic",
            "素描": "sketch, pencil drawing, black and white",
            "赛博朋克": "cyberpunk, neon lights, futuristic, sci-fi"
        }
        
        quality_text = quality_keywords.get(quality, "")
        style_text = style_keywords.get(style, "")
        
        parts = [enhanced, style_text, quality_text]
        enhanced = ", ".join([p for p in parts if p])
        
        return enhanced
    
    def create_info_text(self, original_prompt, enhanced_prompt, negative_prompt, 
                        width, height, seed, quality, style):
        """创建信息文本"""
        info = f"""### 📋 生成信息

**原始描述:**
{original_prompt}

**增强提示词:**
{enhanced_prompt}

**负面提示词:**
{negative_prompt if negative_prompt else "无"}

---

**参数设置:**
- 📐 图像尺寸: {width} × {height}
- 🎨 质量等级: {quality}
- 🖼️ 风格: {style}
- 🎲 随机种子: {seed}
"""
        return info
    
    def get_preset_prompt(self, preset_type):
        """获取预设提示词"""
        presets = {
            "风景": "beautiful natural landscape, mountains, lake, blue sky, sunset, scenic view",
            "人物": "portrait of a person, detailed face, professional photography, studio lighting",
            "动物": "cute animal, detailed fur, natural environment, wildlife photography",
            "建筑": "modern architecture, building exterior, urban landscape, city view",
            "抽象": "abstract art, colorful patterns, geometric shapes, modern art",
            "科幻": "science fiction scene, futuristic, space, technology, cyberpunk",
            "幻想": "fantasy world, magical, mystical creatures, epic scene"
        }
        return presets.get(preset_type, "")
    
    def get_history_gallery(self):
        """获取历史记录图库"""
        if not self.generation_history:
            return []
        return [(item["image"], f"种子: {item['seed']}") for item in self.generation_history]
    
    def clear_history(self):
        """清除历史记录"""
        self.generation_history = []
        return [], "📝 历史记录已清除"


def create_app():
    """创建Gradio应用界面"""
    
    app_instance = SyntaxRouletteApp()
    
    # 创建主题
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="cyan",
    )
    
    with gr.Blocks(title="Syntax Roulette - AI文本生图", theme=theme) as app:
        
        # 标题区域
        gr.Markdown(
            """
            # 🎨 Syntax Roulette - AI文本生图
            ### 用文字描述你的想象，让AI为你创作图像
            
            💡 **使用提示**: 输入描述文字，选择风格和质量，点击生成按钮即可创作图像
            """
        )
        
        with gr.Row():
            # 左侧控制面板
            with gr.Column(scale=1):
                gr.Markdown("## 📝 创作面板")
                
                # 提示词输入
                with gr.Group():
                    prompt_input = gr.Textbox(
                        label="🖊️ 描述你想要的图像",
                        placeholder="例如：一只可爱的猫咪坐在窗台上，阳光洒在它身上...",
                        lines=4,
                        value="a beautiful landscape with mountains and lake at sunset"
                    )
                    
                    negative_prompt = gr.Textbox(
                        label="🚫 不想要的元素（可选）",
                        placeholder="例如：模糊、低质量、变形...",
                        lines=2,
                        value="blurry, bad quality, distorted"
                    )
                
                # 快速预设
                with gr.Group():
                    gr.Markdown("### 🎯 快速预设")
                    with gr.Row():
                        preset1 = gr.Button("🏞️ 风景", size="sm")
                        preset2 = gr.Button("👤 人物", size="sm")
                        preset3 = gr.Button("🐾 动物", size="sm")
                        preset4 = gr.Button("🏛️ 建筑", size="sm")
                    with gr.Row():
                        preset5 = gr.Button("🎨 抽象", size="sm")
                        preset6 = gr.Button("🚀 科幻", size="sm")
                        preset7 = gr.Button("✨ 幻想", size="sm")
                
                # 参数设置
                with gr.Group():
                    gr.Markdown("### ⚙️ 参数设置")
                    
                    with gr.Row():
                        width = gr.Slider(
                            minimum=256,
                            maximum=1024,
                            step=64,
                            value=512,
                            label="宽度"
                        )
                        height = gr.Slider(
                            minimum=256,
                            maximum=1024,
                            step=64,
                            value=512,
                            label="高度"
                        )
                    
                    quality = gr.Radio(
                        choices=["低", "中", "高", "超高"],
                        value="高",
                        label="质量等级",
                        info="质量越高，生成图像越精细"
                    )
                    
                    style = gr.Dropdown(
                        choices=["默认", "写实", "动漫", "油画", "水彩", "素描", "赛博朋克"],
                        value="默认",
                        label="艺术风格",
                        info="选择生成图像的艺术风格"
                    )
                
                # 高级选项
                with gr.Accordion("🔧 高级选项", open=False):
                    use_random_seed = gr.Checkbox(
                        label="使用随机种子",
                        value=True,
                        info="每次生成不同的结果"
                    )
                    
                    seed_input = gr.Number(
                        label="固定种子值",
                        value=42,
                        precision=0,
                        info="使用相同种子可以重现结果",
                        interactive=False
                    )
                
                # 操作按钮
                with gr.Row():
                    generate_btn = gr.Button("🎨 生成图像", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清空", size="lg")
            
            # 右侧展示区域
            with gr.Column(scale=1):
                gr.Markdown("## 🖼️ 生成结果")
                
                # 状态显示
                status_text = gr.Markdown("⏳ 等待生成...")
                
                # 图像显示
                output_image = gr.Image(
                    label="生成的图像",
                    type="pil",
                    height=400,
                    show_label=False
                )
                
                # 下载按钮
                with gr.Row():
                    download_btn = gr.Button("📥 下载图像", size="sm")
                
                # 详细信息
                with gr.Accordion("📊 详细信息", open=True):
                    info_display = gr.Markdown("")
        
        # 历史记录区域
        with gr.Accordion("📚 生成历史", open=False):
            with gr.Row():
                refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
                clear_history_btn = gr.Button("🗑️ 清空历史", size="sm")
            
            history_gallery = gr.Gallery(
                label="历史记录",
                columns=4,
                rows=2,
                height=400,
                object_fit="contain"
            )
            history_status = gr.Markdown("")
        
        # 使用说明
        with gr.Accordion("❓ 使用说明", open=False):
            gr.Markdown(
                """
                ## 📖 如何使用
                
                ### 基本步骤:
                1. **输入描述**: 在"描述你想要的图像"框中输入你的想法
                2. **选择风格**: 选择你喜欢的艺术风格（可选）
                3. **调整参数**: 设置图像尺寸和质量（可选）
                4. **点击生成**: 点击"生成图像"按钮
                5. **查看结果**: 等待几秒，图像就会显示在右侧
                
                ### 快速预设:
                - 点击预设按钮可以快速填入常用场景描述
                - 你可以在预设的基础上继续编辑
                
                ### 提示词技巧:
                - 📝 **具体明确**: 详细描述你想要的内容
                - 🎨 **添加细节**: 如"阳光明媚"、"细节丰富"等
                - 🚫 **负面提示**: 描述不想要的元素，如"模糊"、"低质量"
                - 🔢 **使用关键词**: 如"8k"、"高清"、"专业摄影"等
                
                ### 示例描述:
                ```
                一只橘色的小猫坐在窗台上，阳光透过窗户照在它身上，
                温暖的光线，毛发清晰可见，专业摄影，高质量
                ```
                
                ### 高级功能:
                - **随机种子**: 每次生成不同结果
                - **固定种子**: 可以重现之前的生成结果
                - **历史记录**: 自动保存最近20次生成
                
                ---
                
                ⚠️ **注意**: 当前为演示模式，生成的是艺术风格的预览图像。
                如需真实AI生成，请连接ComfyUI服务。
                """
            )
        
        # 页脚
        gr.Markdown(
            """
            ---
            <div style="text-align: center; color: #666;">
                <p>🎨 Syntax Roulette | 让创意触手可及</p>
                <p style="font-size: 0.9em;">提示：当前为演示模式 | 建议使用Chrome或Firefox浏览器</p>
            </div>
            """,
            elem_id="footer"
        )
        
        # ===== 事件绑定 =====
        
        # 快速预设按钮
        preset1.click(lambda: app_instance.get_preset_prompt("风景"), None, prompt_input)
        preset2.click(lambda: app_instance.get_preset_prompt("人物"), None, prompt_input)
        preset3.click(lambda: app_instance.get_preset_prompt("动物"), None, prompt_input)
        preset4.click(lambda: app_instance.get_preset_prompt("建筑"), None, prompt_input)
        preset5.click(lambda: app_instance.get_preset_prompt("抽象"), None, prompt_input)
        preset6.click(lambda: app_instance.get_preset_prompt("科幻"), None, prompt_input)
        preset7.click(lambda: app_instance.get_preset_prompt("幻想"), None, prompt_input)
        
        # 生成按钮
        generate_btn.click(
            fn=app_instance.generate_image,
            inputs=[
                prompt_input, negative_prompt, width, height,
                quality, style, use_random_seed, seed_input
            ],
            outputs=[output_image, status_text, info_display]
        )
        
        # 清空按钮
        clear_btn.click(
            fn=lambda: ("", "", None, "⏳ 已清空，等待生成...", ""),
            inputs=[],
            outputs=[prompt_input, negative_prompt, output_image, status_text, info_display]
        )
        
        # 种子复选框
        use_random_seed.change(
            fn=lambda x: gr.update(interactive=not x),
            inputs=use_random_seed,
            outputs=seed_input
        )
        
        # 历史记录按钮
        refresh_history_btn.click(
            fn=app_instance.get_history_gallery,
            inputs=[],
            outputs=history_gallery
        )
        
        clear_history_btn.click(
            fn=app_instance.clear_history,
            inputs=[],
            outputs=[history_gallery, history_status]
        )
    
    return app


if __name__ == "__main__":
    print("=" * 60)
    print("🎨 Syntax Roulette - AI文本生图")
    print("=" * 60)
    print("正在启动Web界面...")
    print("请稍候，首次启动可能需要几秒钟...")
    print("=" * 60)
    
    # 创建并启动应用
    app = create_app()
    
    # 启动服务器
    app.launch(
        server_name="127.0.0.1",  # 本地访问
        server_port=7860,          # 端口号
        share=False,               # 不创建公共链接
        show_error=True,           # 显示错误信息
        quiet=False,               # 显示启动信息
        inbrowser=True            # 自动打开浏览器
    )
