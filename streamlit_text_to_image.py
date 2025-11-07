"""
Streamlit文本生图界面
基于ComfyUI工作流的文本到图像生成应用
"""

import streamlit as st
import json
import requests
import io
import time
from PIL import Image
import random
from text_to_image import TextToImageWorkflow


# 页面配置
st.set_page_config(
    page_title="AI文本生图工具",
    page_icon="🎨",
    layout="wide"
)

# 初始化session state
if 'workflow' not in st.session_state:
    st.session_state.workflow = TextToImageWorkflow()
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'history' not in st.session_state:
    st.session_state.history = []


def generate_image_demo(workflow):
    """
    演示模式：生成随机演示图像
    实际使用时需要连接ComfyUI API
    """
    # 这里创建一个演示图像
    import numpy as np
    
    # 获取配置参数
    width = workflow.workflow["5"]["inputs"]["width"]
    height = workflow.workflow["5"]["inputs"]["height"]
    
    # 创建随机渐变图像作为演示
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 根据种子生成随机颜色
    seed = workflow.workflow["3"]["inputs"]["seed"]
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


def send_to_comfyui(workflow, comfyui_url="http://127.0.0.1:8188"):
    """
    发送工作流到ComfyUI API（实际使用版本）
    需要ComfyUI服务运行在本地或远程
    """
    try:
        # 生成客户端ID
        client_id = str(random.randint(0, 1000000))
        
        # 准备工作流数据
        prompt = {"prompt": workflow.workflow, "client_id": client_id}
        
        # 发送到ComfyUI
        response = requests.post(f"{comfyui_url}/prompt", json=prompt)
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result.get('prompt_id')
            
            # 等待生成完成
            while True:
                history = requests.get(f"{comfyui_url}/history/{prompt_id}")
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
                                        params={"filename": filename, "subfolder": subfolder}
                                    )
                                    if img_response.status_code == 200:
                                        return Image.open(io.BytesIO(img_response.content))
                        break
                time.sleep(1)
        
        return None
    except Exception as e:
        st.error(f"连接ComfyUI失败: {str(e)}")
        return None


# 标题和说明
st.title("🎨 AI文本生图工具")
st.markdown("基于ComfyUI工作流的文本到图像生成应用")

# 侧边栏 - 工作流配置
st.sidebar.header("⚙️ 生成参数")

# 模型选择
checkpoint = st.sidebar.text_input(
    "模型检查点",
    value=st.session_state.workflow.workflow["11"]["inputs"]["ckpt_name"],
    help="输入模型文件名，如 majicmixRealistic_v7.safetensors"
)

# 图像尺寸
st.sidebar.subheader("图像尺寸")
col1, col2 = st.sidebar.columns(2)
with col1:
    width = st.number_input(
        "宽度",
        min_value=256,
        max_value=2048,
        value=st.session_state.workflow.workflow["5"]["inputs"]["width"],
        step=64
    )
with col2:
    height = st.number_input(
        "高度",
        min_value=256,
        max_value=2048,
        value=st.session_state.workflow.workflow["5"]["inputs"]["height"],
        step=64
    )

# 采样参数
st.sidebar.subheader("采样参数")
steps = st.sidebar.slider(
    "采样步数",
    min_value=1,
    max_value=150,
    value=st.session_state.workflow.workflow["3"]["inputs"]["steps"],
    help="更多步数通常产生更好的质量，但需要更长时间"
)

cfg = st.sidebar.slider(
    "CFG Scale",
    min_value=1.0,
    max_value=30.0,
    value=float(st.session_state.workflow.workflow["3"]["inputs"]["cfg"]),
    step=0.5,
    help="提示词引导强度，值越高越贴近提示词"
)

sampler_options = [
    "euler", "euler_ancestral", "heun", "dpm_2", "dpm_2_ancestral",
    "lms", "dpm_fast", "dpm_adaptive", "dpmpp_2s_ancestral",
    "dpmpp_sde", "dpmpp_2m", "dpmpp_2m_sde", "ddim", "uni_pc"
]
sampler = st.sidebar.selectbox(
    "采样器",
    options=sampler_options,
    index=sampler_options.index(st.session_state.workflow.workflow["3"]["inputs"]["sampler_name"])
    if st.session_state.workflow.workflow["3"]["inputs"]["sampler_name"] in sampler_options else 0
)

scheduler_options = ["normal", "karras", "exponential", "sgm_uniform", "simple", "ddim_uniform"]
scheduler = st.sidebar.selectbox(
    "调度器",
    options=scheduler_options,
    index=scheduler_options.index(st.session_state.workflow.workflow["3"]["inputs"]["scheduler"])
    if st.session_state.workflow.workflow["3"]["inputs"]["scheduler"] in scheduler_options else 0
)

denoise = st.sidebar.slider(
    "去噪强度",
    min_value=0.0,
    max_value=1.0,
    value=float(st.session_state.workflow.workflow["3"]["inputs"]["denoise"]),
    step=0.05
)

# 种子设置
st.sidebar.subheader("随机种子")
use_random_seed = st.sidebar.checkbox("使用随机种子", value=True)
if use_random_seed:
    seed = random.randint(0, 2**32 - 1)
else:
    seed = st.sidebar.number_input(
        "种子值",
        min_value=0,
        max_value=2**32 - 1,
        value=st.session_state.workflow.workflow["3"]["inputs"]["seed"]
    )

# ComfyUI连接设置
st.sidebar.subheader("连接设置")
use_comfyui = st.sidebar.checkbox(
    "连接ComfyUI服务",
    value=False,
    help="勾选后将尝试连接本地或远程ComfyUI服务"
)
comfyui_url = st.sidebar.text_input(
    "ComfyUI地址",
    value="http://127.0.0.1:8188",
    disabled=not use_comfyui
)

# 主界面 - 提示词输入
st.header("📝 提示词")
col_left, col_right = st.columns([3, 1])

with col_left:
    positive_prompt = st.text_area(
        "正面提示词 (Positive Prompt)",
        value=st.session_state.workflow.workflow["6"]["inputs"]["text"],
        height=100,
        placeholder="描述你想要生成的图像，如：beautiful landscape, mountains, sunset, 8k, masterpiece",
        help="描述你想在图像中看到的内容"
    )
    
    negative_prompt = st.text_area(
        "负面提示词 (Negative Prompt)",
        value=st.session_state.workflow.workflow["7"]["inputs"]["text"],
        height=100,
        placeholder="描述你不想在图像中出现的内容，如：bad quality, blurry, watermark",
        help="描述你不想在图像中看到的内容"
    )

with col_right:
    st.markdown("### 快速提示词")
    if st.button("🏞️ 风景", use_container_width=True):
        positive_prompt = "beautiful landscape, mountains, lake, sunset, dramatic sky, 8k, masterpiece"
    if st.button("👤 人物", use_container_width=True):
        positive_prompt = "portrait, beautiful person, detailed face, professional photography, studio lighting"
    if st.button("🎨 艺术", use_container_width=True):
        positive_prompt = "artistic, oil painting, vibrant colors, masterpiece, highly detailed"
    if st.button("🌃 城市", use_container_width=True):
        positive_prompt = "city skyline, modern architecture, night scene, neon lights, urban landscape"

# 生成按钮
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
with col_btn1:
    generate_btn = st.button("🎨 生成图像", type="primary", use_container_width=True)
with col_btn2:
    save_workflow_btn = st.button("💾 保存配置", use_container_width=True)

# 生成图像
if generate_btn:
    if not positive_prompt.strip():
        st.warning("⚠️ 请输入正面提示词")
    else:
        # 更新工作流参数
        st.session_state.workflow.update_checkpoint(checkpoint)
        st.session_state.workflow.update_prompt(positive_prompt, negative_prompt)
        st.session_state.workflow.update_image_size(width, height)
        st.session_state.workflow.update_sampling_params(
            seed=seed,
            steps=steps,
            cfg=cfg,
            sampler_name=sampler,
            scheduler=scheduler,
            denoise=denoise
        )
        
        # 显示生成状态
        with st.spinner("🎨 正在生成图像，请稍候..."):
            progress_bar = st.progress(0)
            
            if use_comfyui:
                # 尝试连接ComfyUI
                st.info(f"连接到ComfyUI服务: {comfyui_url}")
                generated_img = send_to_comfyui(st.session_state.workflow, comfyui_url)
                
                if generated_img is None:
                    st.warning("⚠️ ComfyUI连接失败，切换到演示模式")
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    generated_img = generate_image_demo(st.session_state.workflow)
            else:
                # 演示模式
                st.info("📌 演示模式：生成预览图像（非真实AI生成）")
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                generated_img = generate_image_demo(st.session_state.workflow)
            
            progress_bar.empty()
        
        if generated_img:
            st.success("✅ 图像生成完成！")
            
            # 保存到历史记录
            st.session_state.generated_images.insert(0, generated_img)
            st.session_state.history.insert(0, {
                "positive": positive_prompt,
                "negative": negative_prompt,
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "size": f"{width}x{height}"
            })
            
            # 限制历史记录数量
            if len(st.session_state.generated_images) > 10:
                st.session_state.generated_images = st.session_state.generated_images[:10]
                st.session_state.history = st.session_state.history[:10]

# 保存配置
if save_workflow_btn:
    filename = f"workflow_{int(time.time())}.json"
    st.session_state.workflow.save_workflow(filename)
    st.success(f"✅ 工作流已保存到 {filename}")

# 显示生成的图像
if st.session_state.generated_images:
    st.markdown("---")
    st.header("🖼️ 生成结果")
    
    # 最新图像
    tab1, tab2 = st.tabs(["当前图像", "历史记录"])
    
    with tab1:
        col_img, col_info = st.columns([2, 1])
        
        with col_img:
            st.image(
                st.session_state.generated_images[0],
                caption="最新生成的图像",
                use_container_width=True
            )
            
            # 下载按钮
            buf = io.BytesIO()
            st.session_state.generated_images[0].save(buf, format="PNG")
            st.download_button(
                label="📥 下载图像",
                data=buf.getvalue(),
                file_name=f"generated_image_{int(time.time())}.png",
                mime="image/png",
                use_container_width=True
            )
        
        with col_info:
            st.markdown("### 生成参数")
            latest = st.session_state.history[0]
            st.markdown(f"**正面提示词:**\n{latest['positive']}")
            st.markdown(f"**负面提示词:**\n{latest['negative']}")
            st.markdown(f"**尺寸:** {latest['size']}")
            st.markdown(f"**步数:** {latest['steps']}")
            st.markdown(f"**CFG:** {latest['cfg']}")
            st.markdown(f"**种子:** {latest['seed']}")
    
    with tab2:
        if len(st.session_state.generated_images) > 1:
            st.markdown("### 历史生成记录")
            
            # 以网格形式显示历史图像
            cols_per_row = 3
            for idx in range(1, len(st.session_state.generated_images)):
                if (idx - 1) % cols_per_row == 0:
                    cols = st.columns(cols_per_row)
                
                col_idx = (idx - 1) % cols_per_row
                with cols[col_idx]:
                    st.image(
                        st.session_state.generated_images[idx],
                        caption=f"历史 #{idx}",
                        use_container_width=True
                    )
                    with st.expander("查看参数"):
                        hist = st.session_state.history[idx]
                        st.text(f"提示词: {hist['positive'][:50]}...")
                        st.text(f"尺寸: {hist['size']}")
                        st.text(f"种子: {hist['seed']}")
        else:
            st.info("暂无历史记录")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>💡 提示：勾选"连接ComfyUI服务"以使用真实的AI图像生成功能</p>
    <p>当前为演示模式，生成的是预览图像</p>
    </div>
    """,
    unsafe_allow_html=True
)
