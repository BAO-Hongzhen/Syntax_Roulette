# Gradio文本生图界面使用指南

## 简介

这是一个基于Gradio框架的AI文本生图Web界面，提供友好的图形界面来使用ComfyUI工作流生成图像。

## 安装步骤

### 1. 安装依赖

```bash
pip install gradio Pillow numpy requests
```

或使用requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python gradio_text_to_image.py
```

启动后会显示：

```
Running on local URL:  http://127.0.0.1:7860
```

在浏览器中打开该地址即可使用。

## 功能特点

### ✅ Gradio界面优势

- 🎨 **现代化UI设计**: 美观、直观的用户界面
- 📱 **响应式布局**: 适配不同屏幕尺寸
- 🔄 **实时交互**: 即时反馈和更新
- 🌐 **易于分享**: 可生成公共链接供他人访问
- 🚀 **快速部署**: 无需复杂配置即可上线
- 📚 **历史记录**: 自动保存生成历史

### 主要功能模块

#### 1. 提示词编辑
- **正面提示词**: 描述想要生成的内容
- **负面提示词**: 描述不想出现的内容
- **快速预设**: 一键应用预设提示词（风景、人物、艺术、城市）

#### 2. 图像参数
- **尺寸设置**: 256-2048像素，支持自定义宽高
- **采样步数**: 1-150步，控制生成质量
- **CFG Scale**: 1.0-30.0，控制提示词引导强度
- **采样器**: 多种采样算法可选
- **调度器**: 多种调度策略可选

#### 3. 高级设置
- **模型选择**: 指定ComfyUI模型文件
- **随机种子**: 控制生成的随机性
- **ComfyUI连接**: 连接到真实的AI服务

## 使用方法

### 演示模式（默认）

1. 启动应用后直接使用，无需额外配置
2. 生成的是预览图像（彩色渐变），非真实AI生成
3. 适合测试界面和参数调整

### 连接ComfyUI服务

1. **启动ComfyUI服务**
   - 确保ComfyUI已安装并运行
   - 默认地址：`http://127.0.0.1:8188`

2. **在界面中配置**
   - 展开"高级设置"
   - 勾选"连接ComfyUI服务"
   - 确认ComfyUI地址正确
   - 输入提示词后点击"生成图像"

3. **等待生成**
   - 系统会连接ComfyUI并发送请求
   - 如果连接失败，自动切换到演示模式

## 界面操作指南

### 基本操作流程

```
1. 输入正面提示词（必填）
   ↓
2. 输入负面提示词（可选）
   ↓
3. 调整图像参数（可选）
   ↓
4. 点击"生成图像"按钮
   ↓
5. 查看生成结果
```

### 快速预设按钮

| 按钮 | 预设内容 | 适用场景 |
|------|---------|---------|
| 🏞️ 风景 | 山川湖泊、自然风光 | 生成风景照片 |
| 👤 人物 | 人物肖像、专业摄影 | 生成人物照片 |
| 🎨 艺术 | 艺术风格、油画效果 | 生成艺术作品 |
| 🌃 城市 | 城市景观、现代建筑 | 生成城市场景 |

### 参数调整建议

#### 图像质量优先
- 采样步数: 30-50
- CFG Scale: 7-10
- 采样器: dpmpp_2m
- 调度器: karras

#### 速度优先
- 采样步数: 15-25
- CFG Scale: 6-8
- 采样器: euler
- 调度器: normal

#### 创意探索
- 使用随机种子
- CFG Scale: 5-7
- 尝试不同采样器

## 示例提示词

### 风景类
```
正面: beautiful mountain landscape, clear blue sky, crystal lake, 
      golden sunset, dramatic clouds, 8k, masterpiece, highly detailed

负面: bad quality, blurry, watermark, people, buildings
```

### 人物类
```
正面: professional portrait photo, beautiful woman, detailed face, 
      studio lighting, bokeh background, high quality

负面: bad anatomy, deformed, blurry, low quality, worst quality
```

### 艺术类
```
正面: oil painting, vibrant colors, impressionist style, 
      beautiful flowers in vase, masterpiece, fine art

负面: photography, realistic, 3d render, bad quality
```

## 高级功能

### 历史记录
- 自动保存最近10次生成结果
- 点击"刷新历史记录"查看
- 可查看每次的参数设置

### 种子控制
- **随机种子**: 每次生成不同结果
- **固定种子**: 使用相同种子可复现结果

### 批量生成
- 固定其他参数
- 只改变种子值
- 多次点击生成按钮

## 常见问题

### Q: 为什么生成的是彩色渐变图？
A: 这是演示模式，需要连接ComfyUI服务才能生成真实AI图像。

### Q: 如何连接ComfyUI？
A: 在高级设置中勾选"连接ComfyUI服务"，确保ComfyUI在运行。

### Q: 生成速度慢怎么办？
A: 减少采样步数、降低图像分辨率、使用更快的采样器。

### Q: 如何提高图像质量？
A: 增加采样步数、使用更好的模型、优化提示词描述。

### Q: 可以部署到服务器吗？
A: 可以，修改启动参数：
```python
app.launch(
    server_name="0.0.0.0",  # 允许外部访问
    server_port=7860,
    share=True              # 生成公共链接
)
```

## 技术架构

```
gradio_text_to_image.py
├── GradioImageGenerator类
│   ├── generate_image_demo()  # 演示模式
│   ├── send_to_comfyui()      # ComfyUI连接
│   ├── generate()              # 主生成函数
│   └── apply_preset_*()       # 预设函数
│
└── create_interface()         # 界面创建
    ├── 提示词输入区
    ├── 参数调整区
    ├── 高级设置区
    └── 结果显示区
```

## 与Streamlit版本对比

| 特性 | Gradio | Streamlit |
|-----|--------|-----------|
| UI设计 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 交互体验 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 部署难度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 分享功能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 组件丰富度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 扩展开发

### 添加新的预设

```python
def apply_preset_custom(self):
    """自定义预设"""
    return "your custom prompt here"
```

### 修改界面主题

```python
app = gr.Blocks(theme=gr.themes.Monochrome())  # 黑白主题
# 或
app = gr.Blocks(theme=gr.themes.Glass())       # 玻璃主题
```

### 添加图像后处理

```python
def post_process_image(img):
    # 在这里添加滤镜、水印等
    return processed_img
```

## 总结

Gradio文本生图界面提供了：
- ✅ 简单易用的图形界面
- ✅ 完整的参数控制
- ✅ 快速预设功能
- ✅ 历史记录管理
- ✅ 演示和实际模式切换
- ✅ 易于部署和分享

适合快速搭建AI图像生成应用原型或部署生产环境！
