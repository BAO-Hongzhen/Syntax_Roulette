import streamlit as st
import os
import time
import random
from PIL import Image
import numpy as np
from comfy_api import ComfyUIManager
from Image_Processing import process_image_for_papercut

# --- 配置 ---
st.set_page_config(
    page_title="Papercraft Maestro",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 路径设置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
UI_IMAGES_DIR = os.path.join(ASSETS_DIR, "UI _Images")
SCENE_IMAGES_DIR = os.path.join(ASSETS_DIR, "Prototype_Images")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCENE_OUTPUT_DIR = os.path.join(BASE_DIR, "image_in_scene")
WORKFLOW_PATH = os.path.join(BASE_DIR, "ComfyUI_Workflow", "paper_cut.json")

# --- 初始化 ComfyUI ---
@st.cache_resource
def get_manager():
    return ComfyUIManager(WORKFLOW_PATH)

manager = get_manager()

# --- 辅助函数 ---

def _apply_color_and_opacity(image: Image.Image, color: tuple = (152, 0, 21), opacity: float = 0.75) -> Image.Image:
    """应用指定颜色和透明度到图片"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    img_array = np.array(image)
    a = img_array[:, :, 3]
    
    # 将所有非透明像素设为指定颜色
    non_transparent = a > 0
    
    img_array[:, :, 0] = np.where(non_transparent, color[0], 0)  # R
    img_array[:, :, 1] = np.where(non_transparent, color[1], 0)  # G
    img_array[:, :, 2] = np.where(non_transparent, color[2], 0)  # B
    
    # 调整透明度
    img_array[:, :, 3] = np.where(non_transparent, (a * opacity).astype(np.uint8), 0)
    
    return Image.fromarray(img_array, 'RGBA')

def composite_scene(papercut_path, scene_path):
    """合成剪纸到场景"""
    try:
        papercut = Image.open(papercut_path).convert('RGBA')
        scene = Image.open(scene_path).convert('RGB')
        
        # 调整剪纸尺寸为 1736x1736
        papercut = papercut.resize((1736, 1736), Image.Resampling.LANCZOS)
        
        # 应用颜色 (#980015) 和透明度 (75%)
        papercut = _apply_color_and_opacity(papercut, color=(152, 0, 21), opacity=0.75)
        
        # 坐标设置 (Window)
        x = 2870
        y = 137
        
        scene_rgba = scene.convert('RGBA')
        composite = Image.new('RGBA', scene_rgba.size, (255, 255, 255, 0))
        composite.paste(scene_rgba, (0, 0))
        composite.paste(papercut, (x, y), papercut)
        
        final_image = composite.convert('RGB')
        
        timestamp = int(time.time())
        output_filename = f"scene_render_{timestamp}.png"
        output_path = os.path.join(SCENE_OUTPUT_DIR, output_filename)
        final_image.save(output_path, 'PNG')
        
        return output_path
    except Exception as e:
        st.error(f"合成失败: {e}")
        return None

# --- 自定义 CSS ---
st.markdown("""
<style>
    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 全局背景色 */
    .stApp {
        background-color: #fdfbf7; /* 浅米色背景，类似纸张 */
    }
    
    /* 按钮样式 */
    .stButton > button {
        background-color: #980015;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #b30019;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #980015;
        padding: 10px;
        background-color: rgba(255, 255, 255, 0.9);
    }
    
    /* 图片容器 */
    .image-container {
        display: flex;
        justify_content: center;
        align_items: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 状态管理 ---
if 'step' not in st.session_state:
    st.session_state.step = 0 # 0: Input, 1: Result, 2: Scene
if 'generated_image_path' not in st.session_state:
    st.session_state.generated_image_path = None
if 'scene_image_path' not in st.session_state:
    st.session_state.scene_image_path = None
if 'prompt' not in st.session_state:
    st.session_state.prompt = ""

# --- UI 布局 ---

# 1. Banner
banner_path = os.path.join(UI_IMAGES_DIR, "Banner.png")
if os.path.exists(banner_path):
    st.image(banner_path, use_container_width=True)
else:
    st.title("Papercraft Maestro")

# 2. 主逻辑区域
container = st.container()

with container:
    # --- 步骤 0: 输入与生成 ---
    if st.session_state.step == 0:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # 显示 Search Bar 图片作为装饰
            search_bar_img = os.path.join(UI_IMAGES_DIR, "Search Bar.png")
            if os.path.exists(search_bar_img):
                st.image(search_bar_img, use_container_width=True)
            
            # 输入框
            prompt = st.text_input("Enter your prompt here:", value=st.session_state.prompt, placeholder="Describe the papercut pattern...", label_visibility="collapsed")
            st.session_state.prompt = prompt
            
            # 生成按钮
            generate_btn_img = os.path.join(UI_IMAGES_DIR, "Generate Butten.png")
            
            # 使用列来居中按钮
            b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
            with b_col2:
                if st.button("GENERATE", use_container_width=True):
                    if not prompt:
                        st.warning("Please enter a prompt first.")
                    else:
                        with st.spinner("Generating papercut art... This may take a moment."):
                            try:
                                # 1. ComfyUI 生成 (使用 comfy_api)
                                raw_image_path = manager.generate_image(prompt, OUTPUT_DIR)
                                
                                if raw_image_path:
                                    # 2. 图像处理 (转红, 抠图)
                                    processed_path = process_image_for_papercut(raw_image_path)
                                    
                                    if processed_path:
                                        st.session_state.generated_image_path = processed_path
                                        st.session_state.step = 1
                                        st.rerun()
                                    else:
                                        st.error("Image processing failed.")
                                else:
                                    st.error("Generation failed: No images returned from ComfyUI.")
                                    
                            except Exception as e:
                                st.error(f"An error occurred: {e}")

    # --- 步骤 1: 结果展示 ---
    elif st.session_state.step == 1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Generated Papercut")
            if st.session_state.generated_image_path:
                st.image(st.session_state.generated_image_path, use_container_width=True)
            
            # 按钮组
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Try Again"):
                    st.session_state.step = 0
                    st.rerun()
            with btn_col2:
                # 下载按钮
                if st.session_state.generated_image_path:
                    with open(st.session_state.generated_image_path, "rb") as file:
                        st.download_button(
                            label="Download PNG",
                            data=file,
                            file_name="papercut.png",
                            mime="image/png"
                        )

        with col2:
            st.subheader("Visualize in Scene")
            st.write("See how it looks in a real environment.")
            
            # 场景选择 (目前主要支持 Window)
            scene_type = st.selectbox("Select Scene", ["Window", "Wall", "Door"])
            
            render_btn_img = os.path.join(UI_IMAGES_DIR, "Render in Sence Butten.png")
            
            if st.button("RENDER IN SCENE", use_container_width=True):
                with st.spinner("Rendering scene..."):
                    # 确定场景图片路径
                    scene_filename = "Prototype_Window.jpg" # 默认 Window
                    if scene_type == "Wall":
                        scene_filename = "Prototype_Wall.jpg" # 假设文件名
                    elif scene_type == "Door":
                        scene_filename = "Prototype_Door.jpg" # 假设文件名
                        
                    scene_path = os.path.join(SCENE_IMAGES_DIR, scene_filename)
                    
                    # 如果找不到特定场景，回退到 Window
                    if not os.path.exists(scene_path):
                        scene_path = os.path.join(SCENE_IMAGES_DIR, "Prototype_Window.jpg")
                    
                    if os.path.exists(scene_path) and st.session_state.generated_image_path:
                        final_scene_path = composite_scene(st.session_state.generated_image_path, scene_path)
                        if final_scene_path:
                            st.session_state.scene_image_path = final_scene_path
                            st.session_state.step = 2
                            st.rerun()
                    else:
                        st.error(f"Scene image not found: {scene_path}")

    # --- 步骤 2: 场景展示 ---
    elif st.session_state.step == 2:
        st.subheader("Scene Visualization")
        
        if st.session_state.scene_image_path:
            st.image(st.session_state.scene_image_path, use_container_width=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Back to Edit"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.button("Start Over"):
                    st.session_state.step = 0
                    st.session_state.prompt = ""
                    st.rerun()
            with col3:
                with open(st.session_state.scene_image_path, "rb") as file:
                    st.download_button(
                        label="Download Scene",
                        data=file,
                        file_name="scene_render.png",
                        mime="image/png"
                    )

# 底部装饰
ui_1_path = os.path.join(UI_IMAGES_DIR, "UI_1.png")
if os.path.exists(ui_1_path):
    st.image(ui_1_path, use_container_width=True)
