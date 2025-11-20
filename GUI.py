"""
剪纸大师 (Papercraft Maestro) - Gradio UI 界面
使用纯 HTML/CSS 完全自定义布局，精确还原 Figma 设计
"""

import gradio as gr
import os
from PIL import Image
import base64
from io import BytesIO
import json

# 资源文件路径
ASSETS_PATH = "Assets/UI _Images"
BANNER_PATH = os.path.join(ASSETS_PATH, "Banner.png")
CHINESE_TITLE_PATH = os.path.join(ASSETS_PATH, "Chinese Title.png")
ENGLISH_TITLE_PATH = os.path.join(ASSETS_PATH, "English Title.png")
GENERATE_BUTTON_PATH = os.path.join(ASSETS_PATH, "Generate Butten.png")
SEARCH_BAR_PATH = os.path.join(ASSETS_PATH, "Search Bar.png")
SLOGAN_PATH = os.path.join(ASSETS_PATH, "slogan.png")
UI_REFERENCE_PATH = os.path.join(ASSETS_PATH, "UI_1.png")


def image_to_base64(image_path):
    """将图片转换为 base64 编码，用于在 HTML 中使用"""
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""


def generate_papercut(prompt: str, scene_image=None):
    """
    生成剪纸图案的主函数
    
    Args:
        prompt: 用户输入的文字描述
        scene_image: 可选的场景照片
    
    Returns:
        生成的剪纸效果图和状态消息
    """
    if not prompt or not prompt.strip():
        return None, "⚠️ 请输入创意描述！"
    
    try:
        # 导入必要的模块
        from ComfyUI_api import ComfyUIClient
        from Image_Processing import desaturate_image, increase_contrast, remove_white_background, convert_to_red
        
        # 测试 ComfyUI 连接
        client = ComfyUIClient()
        if not client.test_connection():
            return None, "❌ ComfyUI 服务未连接！\n请确保 ComfyUI 正在运行于 http://127.0.0.1:8188"
        
        # 第1步：使用 ComfyUI 生成初始图像
        yield None, f"✨ 正在生成剪纸图案...\n\n📝 输入描述: {prompt}\n\n⏳ 步骤 1/4: 调用 AI 生成初始图像..."
        
        generated_image = client.generate_image(
            prompt=prompt,
            negative_prompt="blurry, bad quality, distorted",
            width=768,
            height=768
        )
        
        if generated_image is None:
            return None, "❌ 图像生成失败，请重试"
        
        # 第2步：去饱和
        yield None, f"✨ 正在处理...\n\n⏳ 步骤 2/4: 去饱和处理..."
        processed_image = desaturate_image(generated_image)
        
        # 第3步：增强对比度
        yield None, f"✨ 正在处理...\n\n⏳ 步骤 3/4: 增强对比度..."
        processed_image = increase_contrast(processed_image, factor=3.0)
        
        # 第4步：抠白色背景
        yield None, f"✨ 正在处理...\n\n⏳ 步骤 4/4: 剪纸效果处理..."
        processed_image = remove_white_background(processed_image, threshold=230)
        
        # 第5步：转为红色
        processed_image = convert_to_red(processed_image)
        
        # 保存结果
        import time
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        output_path = os.path.join(output_dir, f"papercut_{timestamp}.png")
        processed_image.save(output_path)
        
        return processed_image, f"✅ 剪纸图案生成成功！\n\n📝 提示词: {prompt}\n💾 已保存至: {output_path}"
        
    except ImportError as e:
        return None, f"❌ 模块导入失败: {e}\n请检查 ComfyUI_api.py 和 Image_Processing.py"
    except Exception as e:
        return None, f"❌ 生成失败: {str(e)}"

    return None, message


def create_custom_html(banner_b64, chinese_title_b64, english_title_b64, slogan_b64, search_bar_b64, generate_btn_b64):
    """创建完全自定义的 HTML 布局 - 严格按照 UI_1.png 精确位置"""
    # 模板匹配得到的位置: Search Bar (50%, 46.07%), Generate Button (66.92%, 47.02%)
    html = f"""
    <div id="custom-papercut-ui">
        <!-- Banner 背景区域 -->
        <div class="banner-section">
            <img src="{banner_b64}" class="banner-img" alt="Banner">
            
            <!-- 所有元素叠加层（绝对定位） -->
            <div class="overlay-container">
                <!-- 中文标题 -->
                <img src="{chinese_title_b64}" class="chinese-title" alt="剪纸大师">
                <!-- 英文标题 -->
                <img src="{english_title_b64}" class="english-title" alt="Papercraft Maestro">
                <!-- Slogan -->
                <img src="{slogan_b64}" class="slogan" alt="Slogan">

                <!-- Search Bar - 精确位置：中心 (50%, 46.074646%)，宽度 43.70% -->
                <div class="searchbar-absolute">
                    <!-- Search Bar 图片作为搜索框背景 -->
                    <img src="{search_bar_b64}" class="search-bar-bg" alt="Search Bar">
                    <!-- 输入框叠加层 -->
                    <div class="input-overlay-direct">
                        <input type="text" id="direct-input" placeholder="Describe what you want to see..." />
                    </div>
                </div>

                <!-- Generate Button - 绝对位置：中心 (66.92%, 47.02%)，在 Search Bar 右下方 -->
                <div class="generate-absolute">
                    <button class="generate-btn-custom" id="custom-generate-btn" onclick="const hiddenBtn = document.getElementById('hidden-generate-btn'); if (hiddenBtn) hiddenBtn.click();">
                        <img src="{generate_btn_b64}" alt="Generate">
                    </button>
                </div>
            </div>
        </div>
    </div>
    """
    return html


# 完全自定义的 CSS 样式 - 按照 UI_1.png 精确位置绝对定位
custom_css = """
/* 重置 Gradio 默认样式 */
.gradio-container {
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

.main {
    padding: 0 !important;
}

#custom-papercut-ui {
    width: 100%;
    margin: 0;
    padding: 0;
}

/* Banner 区域 */
.banner-section {
    position: relative;
    width: 100%;
    margin: 0;
}

.banner-img {
    width: 100%;
    height: auto;
    display: block;
}

/* 叠加容器 */
.overlay-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
}

/* 中文标题 - 精确绝对定位 */
.chinese-title {
    position: absolute;
    width: 22.43%;
    height: auto;
    left: 49.918981%;
    top: 22.072072%;
    transform: translate(-50%, -50%);
    z-index: 20;
}

/* 英文标题 */
.english-title {
    position: absolute;
    width: 23.54%;
    height: auto;
    left: 48.4375%;
    top: 12.891463%;
    transform: translate(-50%, -50%);
    z-index: 20;
}

/* Slogan */
.slogan {
    position: absolute;
    width: 42.06%;
    height: auto;
    left: 50.104167%;
    top: 36.615187%;
    transform: translate(-50%, -50%);
    z-index: 20;
}

/* Search Bar - 绝对定位：中心 (50%, 46.07%) */
.searchbar-absolute {
    position: absolute;
    left: 50%;
    top: 46.074646%;
    transform: translate(-50%, -50%);
    width: 43.70%;
    z-index: 25;
}

.search-bar-bg {
    width: 100%;
    height: auto;
    display: block;
}

/* 输入框叠加层 - 透明覆盖在 Search Bar.png 上 */
.input-overlay-direct {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    height: 70%;
    z-index: 50;
    pointer-events: auto;
    display: flex;
    align-items: center;
}

/* 直接输入框样式 */
#direct-input {
    width: 100%;
    height: 100%;
    background: transparent;
    border: none;
    outline: none;
    padding: 0 30px;
    font-size: 15px;
    color: #ffffff;
    caret-color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    box-sizing: border-box;
    position: relative;
    z-index: 2;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Placeholder 样式 - 默认半透明白色，始终显示 */
#direct-input::placeholder {
    color: rgba(255, 255, 255, 0.7);
    opacity: 1;
}

/* 获得焦点时不影响 placeholder，保持显示 */
#direct-input:focus {
    outline: none;
}

/* Generate Button - 绝对定位：中心 (66.93%, 47.04%) */
.generate-absolute {
    position: absolute;
    left: 66.93287%;
    top: 47.0399%;
    transform: translate(-50%, -50%);
    width: 8.68%;
    z-index: 30;
}

.generate-btn-custom {
    display: block;
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
    transition: all 0.3s ease;
    width: 100%;
    height: auto;
}

.generate-btn-custom:hover {
    transform: scale(1.08);
    filter: brightness(1.15) drop-shadow(0 6px 20px rgba(211, 47, 47, 0.4));
}

.generate-btn-custom img {
    width: 100%;
    height: auto;
    display: block;
}

/* Gradio 输入框样式 - 隐藏但保持功能 */
#prompt-input {
    display: none !important;  /* 完全隐藏 Gradio 输入框 */
}

/* 输出区域样式 */
#output-section {
    margin-top: 40px;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
}

#output-image {
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

#status-message {
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.6;
}

#status-message textarea {
    background: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 6px !important;
    padding: 15px !important;
}

/* 响应式 */
@media (max-width: 1400px) {
    .chinese-title { width: 26%; top: 3%; }
    .english-title { width: 27%; top: 11%; }
    .slogan { width: 48%; top: 18%; }
    .searchbar-absolute { width: 50%; }
    .generate-btn-custom img { width: 10%; min-width: 180px; }
}

@media (max-width: 1024px) {
    .chinese-title { width: 32%; top: 2.5%; }
    .english-title { width: 33%; top: 10%; }
    .slogan { width: 55%; top: 16%; }
    .searchbar-absolute { width: 60%; }
    .generate-btn-custom img { width: 12%; min-width: 160px; }
    #prompt-input textarea { font-size: 15px !important; padding: 15px 28px !important; }
}

@media (max-width: 768px) {
    .chinese-title { width: 45%; top: 2%; }
    .english-title { width: 46%; top: 9%; }
    .slogan { width: 70%; top: 14.5%; }
    .searchbar-absolute { width: 75%; }
    .generate-btn-custom img { width: 20%; min-width: 140px; }
    #prompt-input textarea { font-size: 14px !important; padding: 12px 22px !important; }
}

@media (max-width: 480px) {
    .chinese-title { width: 60%; }
    .english-title { width: 62%; }
    .slogan { width: 82%; }
    .searchbar-absolute { width: 88%; }
    .generate-btn-custom img { width: 35%; min-width: 120px; }
    #prompt-input textarea { font-size: 13px !important; padding: 10px 18px !important; }
}
"""

def create_ui():
    """创建 Gradio 界面"""
    
    # 预加载所有图片的 base64 编码
    print("📦 正在加载 UI 资源...")
    banner_b64 = image_to_base64(BANNER_PATH)
    chinese_title_b64 = image_to_base64(CHINESE_TITLE_PATH)
    english_title_b64 = image_to_base64(ENGLISH_TITLE_PATH)
    generate_btn_b64 = image_to_base64(GENERATE_BUTTON_PATH)
    search_bar_b64 = image_to_base64(SEARCH_BAR_PATH)
    slogan_b64 = image_to_base64(SLOGAN_PATH)
    print("✅ UI 资源加载完成！")
    
    with gr.Blocks(css=custom_css, title="剪纸大师 - Papercraft Maestro", theme=gr.themes.Soft()) as demo:
        
        # Banner 区域 + 所有叠加元素
        gr.HTML(create_custom_html(banner_b64, chinese_title_b64, english_title_b64, slogan_b64, search_bar_b64, generate_btn_b64))
        
        # 实际的文本输入框（隐藏，仅用于后端逻辑）
        prompt_input = gr.Textbox(
            label="",
            placeholder="",
            lines=2,
            max_lines=3,
            elem_id="prompt-input",
            show_label=False,
            container=False,
            visible=False
        )
        
        # 隐藏的 Gradio 按钮用于触发生成逻辑
        generate_btn_hidden = gr.Button("Generate", visible=False, elem_id="hidden-generate-btn")
        
        # 输出区域
        with gr.Row(elem_id="output-section"):
            with gr.Column(scale=1):
                output_image = gr.Image(
                    label="🎨 生成的剪纸作品",
                    type="pil",
                    elem_id="output-image",
                    show_label=True,
                    container=True
                )
            with gr.Column(scale=1):
                status_message = gr.Textbox(
                    label="📋 状态信息",
                    lines=10,
                    max_lines=15,
                    elem_id="status-message",
                    show_label=True,
                    interactive=False,
                    container=True
                )
        
        # JavaScript 同步输入框到 Gradio 后端
        gr.HTML("""
            <script>
                function syncInputs() {
                    console.log('🔍 开始查找 DOM 元素...');
                    const directInput = document.querySelector('#direct-input');
                    const gradioTextarea = document.querySelector('#prompt-input textarea');
                    
                    console.log('directInput:', directInput);
                    console.log('gradioTextarea:', gradioTextarea);
                    
                    if (directInput) {
                        console.log('✅ 输入框找到，设置事件监听...');
                        
                        // 处理输入事件
                        const handleInput = function() {
                            const value = directInput.value || '';
                            console.log('⌨️ 输入值:', value);
                            
                            // 同步到 Gradio（如果存在）
                            if (gradioTextarea) {
                                gradioTextarea.value = value;
                                gradioTextarea.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                        };
                        
                        // 绑定输入事件
                        directInput.addEventListener('input', handleInput);
                        directInput.addEventListener('change', handleInput);
                        
                        // 按 Enter 键触发生成
                        directInput.addEventListener('keypress', function(e) {
                            if (e.key === 'Enter') {
                                if (gradioTextarea) {
                                    gradioTextarea.value = directInput.value;
                                }
                                const hiddenBtn = document.getElementById('hidden-generate-btn');
                                if (hiddenBtn) {
                                    hiddenBtn.click();
                                }
                            }
                        });
                        
                        console.log('✅ 输入框同步已设置');
                    } else {
                        console.log('⚠️ 未找到输入框，1秒后重试...');
                        setTimeout(syncInputs, 1000);
                    }
                }
                
                // 页面加载后执行
                if (document.readyState === 'loading') {
                    document.addEventListener('DOMContentLoaded', function() {
                        setTimeout(syncInputs, 500);
                    });
                } else {
                    setTimeout(syncInputs, 500);
                }
            </script>
        """)
        
        # 绑定事件
        generate_btn_hidden.click(
            fn=generate_papercut,
            inputs=[prompt_input, gr.State(None)],
            outputs=[output_image, status_message]
        )
        
        prompt_input.submit(
            fn=generate_papercut,
            inputs=[prompt_input, gr.State(None)],
            outputs=[output_image, status_message]
        )
    
    return demo


if __name__ == "__main__":
    # 启动界面
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
