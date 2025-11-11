"""
Gradio网页界面模块 - Web UI Module
负责创建用户交互界面
"""

import gradio as gr
from typing import Optional, Tuple, List
import os
import time
from PIL import Image


class GradioInterface:
    """Gradio界面管理类"""
    
    def __init__(self, word_bank, comfyui_client):
        """
        初始化Gradio界面
        
        Args:
            word_bank: 词库实例
            comfyui_client: ComfyUI客户端实例
        """
        self.word_bank = word_bank
        self.comfyui_client = comfyui_client
        self.generation_history = []
    
    def generate_sentence_handler(self, pattern_type: str) -> Tuple[str, str]:
        """
        生成句子的处理函数
        
        Args:
            pattern_type: 句子模式类型
            
        Returns:
            (句子, 详细信息)
        """
        try:
            if pattern_type == "简单句式":
                result = self.word_bank.generate_simple_sentence()
            elif pattern_type == "详细句式":
                result = self.word_bank.generate_detailed_sentence()
            else:
                result = self.word_bank.generate_simple_sentence()
            
            sentence = result["sentence"]
            
            # 构建详细信息
            details = f"""### 🎯 生成的句子
**{sentence}**

### 📋 句子结构
**模式**: {result['pattern']}

### 🔤 各部分详情
"""
            for key, value in result.items():
                if key not in ["sentence", "pattern"]:
                    details += f"- **{key}**: {value}\n"
            
            return sentence, details
            
        except Exception as e:
            return "", f"❌ 生成失败: {str(e)}"
    
    def generate_gif_handler(self, sentence: str, negative_prompt: str,
                           width: int, height: int, num_frames: int, fps: int,
                           progress=gr.Progress()) -> Tuple[Optional[str], str]:
        """
        生成GIF的处理函数
        
        Args:
            sentence: 句子（提示词）
            negative_prompt: 负面提示词
            width: 宽度
            height: 高度
            num_frames: 帧数
            fps: 帧率
            progress: 进度条
            
        Returns:
            (GIF路径, 状态信息)
        """
        try:
            if not sentence or sentence.strip() == "":
                return None, "❌ 请先生成或输入句子"
            
            progress(0, desc="准备生成...")
            
            # 使用ComfyUI生成
            progress(0.1, desc="连接ComfyUI...")
            
            if not self.comfyui_client.test_connection():
                return None, "❌ 无法连接到ComfyUI，请确保ComfyUI正在运行"
            
            progress(0.3, desc="提交到生成队列...")
            
            gif_path = self.comfyui_client.generate_gif(
                prompt=sentence,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_frames=num_frames,
                fps=fps
            )
            
            if gif_path:
                progress(1.0, desc="完成！")
                
                # 添加到历史记录
                self.generation_history.insert(0, {
                    "sentence": sentence,
                    "path": gif_path,
                    "timestamp": time.time()
                })
                
                status = f"""✅ **GIF生成成功！**

📝 **提示词**: {sentence}
🚫 **负面提示词**: {negative_prompt}
📐 **尺寸**: {width} x {height}
🎞️ **帧数**: {num_frames}
⚡ **帧率**: {fps} FPS
💾 **保存路径**: {gif_path}
"""
                return gif_path, status
            else:
                return None, "❌ GIF生成失败，请查看终端日志"
                
        except Exception as e:
            return None, f"❌ 生成失败: {str(e)}"
    
    def get_history_gallery(self) -> List[Tuple[str, str]]:
        """获取历史记录"""
        return [(item["path"], item["sentence"]) for item in self.generation_history[:20]]
    
    def create_interface(self) -> gr.Blocks:
        """
        创建Gradio界面
        
        Returns:
            Gradio Blocks应用
        """
        with gr.Blocks(title="Syntax Roulette - 句子转GIF动图", theme=gr.themes.Soft()) as app:
            
            gr.Markdown(
                """
                # 🎲 Syntax Roulette - 语法轮盘
                ## 随机生成句子，AI创作GIF动图
                
                **玩法**: 从词库随机抽取单词 → 组成句子 → AI生成动态GIF
                """
            )
            
            with gr.Row():
                # 左侧：句子生成
                with gr.Column(scale=1):
                    gr.Markdown("## 🎯 步骤1: 生成句子")
                    
                    with gr.Group():
                        pattern_selector = gr.Radio(
                            choices=["简单句式", "详细句式"],
                            value="简单句式",
                            label="选择句式模板",
                            info="简单: 主+谓+宾 | 详细: 完整修饰"
                        )
                        
                        generate_sentence_btn = gr.Button(
                            "🎲 随机生成句子",
                            variant="primary",
                            size="lg"
                        )
                        
                        sentence_output = gr.Textbox(
                            label="生成的句子",
                            placeholder="点击上方按钮生成句子...",
                            lines=3
                        )
                        
                        sentence_details = gr.Markdown("")
                    
                    # 词库管理
                    with gr.Accordion("📚 词库管理", open=False):
                        gr.Markdown("### 当前词库统计")
                        stats = self.word_bank.get_statistics()
                        stats_text = "\n".join([f"- **{k}**: {v}个" for k, v in stats.items()])
                        gr.Markdown(stats_text)
                
                # 右侧：GIF生成
                with gr.Column(scale=1):
                    gr.Markdown("## 🎨 步骤2: 生成GIF动图")
                    
                    with gr.Group():
                        gr.Markdown("### 生成参数")
                        
                        negative_prompt = gr.Textbox(
                            label="负面提示词（可选）",
                            placeholder="blurry, bad quality, distorted",
                            lines=2,
                            value="blurry, bad quality, low quality, distorted"
                        )
                        
                        with gr.Row():
                            width = gr.Slider(256, 1024, 512, step=64, label="宽度")
                            height = gr.Slider(256, 1024, 512, step=64, label="高度")
                        
                        with gr.Row():
                            num_frames = gr.Slider(4, 32, 16, step=4, label="帧数", info="更多帧更流畅")
                            fps = gr.Slider(4, 24, 8, step=2, label="帧率 (FPS)")
                        
                        generate_gif_btn = gr.Button(
                            "🎬 生成GIF动图",
                            variant="primary",
                            size="lg"
                        )
                    
                    status_output = gr.Markdown("⏳ 等待生成...")
                    
                    gif_output = gr.Image(
                        label="生成的GIF",
                        type="filepath",
                        height=400
                    )
            
            # 历史记录
            with gr.Accordion("📚 生成历史", open=False):
                with gr.Row():
                    refresh_history_btn = gr.Button("🔄 刷新历史", size="sm")
                
                history_gallery = gr.Gallery(
                    label="历史GIF",
                    columns=4,
                    rows=2,
                    height=400
                )
            
            # 使用说明
            with gr.Accordion("❓ 使用说明", open=False):
                gr.Markdown(
                    """
                    ## 📖 如何使用
                    
                    ### 基本流程:
                    1. **选择句式**: 选择简单或详细句式模板
                    2. **生成句子**: 点击"随机生成句子"按钮
                    3. **调整参数**: 设置GIF尺寸、帧数等参数
                    4. **生成GIF**: 点击"生成GIF动图"按钮
                    5. **查看结果**: 等待生成完成，GIF会显示在右侧
                    
                    ### 前置要求:
                    - 需要本地ComfyUI正在运行（127.0.0.1:8188）
                    - 真实AI生成高质量动图
                    
                    ### 启动ComfyUI:
                    ```bash
                    # 在ComfyUI目录下运行
                    python main.py
                    ```
                    
                    ### 提示:
                    - 🎲 每次点击生成不同的句子
                    - 📐 建议尺寸: 512x512
                    - 🎞️ 建议帧数: 16帧
                    - ⚡ 建议帧率: 8 FPS
                    """
                )
            
            # 事件绑定
            generate_sentence_btn.click(
                fn=self.generate_sentence_handler,
                inputs=[pattern_selector],
                outputs=[sentence_output, sentence_details]
            )
            
            generate_gif_btn.click(
                fn=self.generate_gif_handler,
                inputs=[
                    sentence_output, negative_prompt,
                    width, height, num_frames, fps
                ],
                outputs=[gif_output, status_output]
            )
            
            refresh_history_btn.click(
                fn=self.get_history_gallery,
                inputs=[],
                outputs=[history_gallery]
            )
        
        return app


# 使用示例
if __name__ == "__main__":
    from word_bank import WordBank
    from comfyui_api import ComfyUIClient
    
    # 创建实例
    word_bank = WordBank()
    comfyui_client = ComfyUIClient()
    
    # 创建界面
    interface = GradioInterface(word_bank, comfyui_client)
    app = interface.create_interface()
    
    # 启动
    app.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)
