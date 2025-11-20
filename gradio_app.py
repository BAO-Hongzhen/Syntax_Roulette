#!/usr/bin/env python3
"""
剪纸大师 - 主启动文件
运行此文件启动 Gradio UI 界面
"""

from GUI import create_ui

if __name__ == "__main__":
    print("=" * 60)
    print("🎨 剪纸大师 (Papercraft Maestro) - 启动中...")
    print("=" * 60)
    
    # 创建并启动 UI
    demo = create_ui()
    
    print("\n✅ 界面已启动！")
    print("🌐 访问地址: http://localhost:7860")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True  # 自动打开浏览器
    )
