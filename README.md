# 🎨 剪纸大师 (Papercraft Maestro)

一个由 AI 驱动的互动艺术平台，将现代文生图技术与中国传统剪纸艺术相融合。

## ✨ 项目简介

剪纸大师允许用户通过输入创意文字描述（Prompt），生成纯正的红色剪纸图案，并将其无缝贴合到场景照片中。

**示例输入**: "将玛丽莲·梦露转化为喜庆的剪纸剪影"

### 工作流程
1. 📝 文字输入 - 用户输入创意描述
2. 🎨 剪纸图生成 - AI 生成剪纸风格图案
3. 📸 结合场景照片 - 可选上传场景图片
4. 🔄 图像合成 - 智能处理与合成
5. 👀 最终预览 - 展示最终效果

## 🚀 快速开始

### 1. 环境准备

确保你已安装 Python 3.8+

```bash
# 克隆项目
cd Syntax_Roulette

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备 UI 资源

确保 `Assets/UI _Images/` 目录下包含以下文件：
- ✅ `Banner.png` - 背景图
- ✅ `Chinese Title.png` - 中文标题
- ✅ `English Title.png` - 英文标题
- ✅ `Generate Butten.png` - 生成按钮
- ✅ `Search Bar.png` - 搜索框背景
- ✅ `slogan.png` - 标语文字
- ✅ `UI_1.png` - 效果图参考

### 3. 启动应用

```bash
# 运行主程序
python main.py
```

应用将自动在浏览器中打开，默认地址：`http://localhost:7860`

## 📁 项目结构

```
Syntax_Roulette/
├── main.py                 # 主启动文件
├── GUI.py                  # Gradio UI 界面
├── ComfyUI_api.py         # ComfyUI API 接口（待实现）
├── Image_Processing.py    # 图像处理模块
├── requirements.txt       # Python 依赖
├── Assets/
│   └── UI _Images/        # UI 资源文件
│       ├── Banner.png
│       ├── Chinese Title.png
│       ├── English Title.png
│       ├── Generate Butten.png
│       ├── Search Bar.png
│       ├── slogan.png
│       └── UI_1.png
└── ComfyUI_Workflow/
    └── paper_cut.json     # ComfyUI 工作流配置
```

## 🎯 功能特性

### 当前实现
- ✅ 完整的 Gradio UI 界面
- ✅ 自定义 CSS 样式，完美还原 Figma 设计
- ✅ 所有 PNG 组件正确映射和定位
- ✅ 响应式设计，支持多种屏幕尺寸
- ✅ 图像处理模块（去饱和、增强对比、抠白、转红）

### 待实现
- ⏳ ComfyUI API 集成
- ⏳ 完整的图像生成流程
- ⏳ 场景图片合成功能
- ⏳ 结果保存与下载

## 🛠️ 技术栈

- **前端框架**: Gradio 4.0+
- **图像处理**: Pillow, NumPy
- **AI 生成**: ComfyUI (计划集成)
- **语言**: Python 3.8+

## 📖 使用指南

1. **输入创意描述**: 在搜索框中输入你想要生成的剪纸图案描述
2. **上传场景照片**（可选）: 选择一张场景照片，剪纸图案将合成到这张照片中
3. **点击生成**: 点击生成按钮或按 Enter 键开始生成
4. **查看结果**: 生成完成后，在右侧查看剪纸效果图

## 🎨 UI 设计说明

### 组件映射
- **Banner.png**: 作为整个界面的背景图，覆盖顶部区域
- **Chinese Title.png**: 中文标题"剪纸大师"，居中显示
- **English Title.png**: 英文标题"Papercraft Maestro"，位于中文标题下方
- **slogan.png**: 描述文字，位于标题区域下方
- **Search Bar.png**: 搜索框背景图，用户在此输入创意描述
- **Generate Butten.png**: 生成按钮，点击后开始生成剪纸图案

### 样式特点
- 所有组件位置与 `UI_1.png` 效果图保持一致
- 使用 base64 编码嵌入图片，提高加载速度
- 响应式布局，适配不同设备
- 悬停效果增强交互体验

## 🔧 开发说明

### 图像处理流程

`Image_Processing.py` 提供以下功能：

1. **desaturate_image()**: 将图片去饱和（转灰度）
2. **increase_contrast()**: 增强图片对比度
3. **remove_white_background()**: 移除白色背景，转为透明
4. **convert_to_red()**: 将图片转换为纯红色剪纸效果

### 扩展开发

要集成完整的生成功能，需要：

1. 在 `ComfyUI_api.py` 中实现 ComfyUI API 调用
2. 在 `GUI.py` 的 `generate_papercut()` 函数中整合各个模块
3. 处理生成流程中的异常情况
4. 添加进度显示和用户反馈

## 📝 许可证

本项目仅用于学习和研究目的。

## 👥 贡献者

SD5913 课程项目 - Group Project Master of ChinaCut

---

**享受创作剪纸艺术的乐趣！** 🎊
