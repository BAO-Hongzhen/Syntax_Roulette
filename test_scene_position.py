"""
快速测试场景合成位置的脚本
使用指定的剪纸图片和坐标测试合成效果
"""

from PIL import Image
import numpy as np
import os
import sys

def apply_color_and_opacity(image, color=(152, 0, 21), opacity=0.75):
    """应用颜色和透明度"""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    img_array = np.array(image)
    a = img_array[:, :, 3]
    
    non_transparent = a > 0
    
    img_array[:, :, 0] = np.where(non_transparent, color[0], 0)
    img_array[:, :, 1] = np.where(non_transparent, color[1], 0)
    img_array[:, :, 2] = np.where(non_transparent, color[2], 0)
    img_array[:, :, 3] = np.where(non_transparent, (a * opacity).astype(np.uint8), 0)
    
    return Image.fromarray(img_array, 'RGBA')

def test_composite(papercut_filename, x, y):
    """
    测试场景合成
    
    Args:
        papercut_filename: 剪纸文件名 (在output文件夹中)
        x: X坐标
        y: Y坐标
    """
    print("\n" + "="*60)
    print("🧪 场景合成位置测试")
    print("="*60)
    
    # 文件路径
    papercut_path = os.path.join('output', papercut_filename)
    scene_path = 'Assets/Prototype_Images/Prototype_Window.jpg'
    output_path = 'test_scene_output.png'
    
    # 检查文件
    if not os.path.exists(papercut_path):
        print(f"❌ 剪纸文件不存在: {papercut_path}")
        return
    
    if not os.path.exists(scene_path):
        print(f"❌ 场景文件不存在: {scene_path}")
        return
    
    print(f"📂 剪纸文件: {papercut_path}")
    print(f"📂 场景文件: {scene_path}")
    print(f"📍 位置: X={x}, Y={y}")
    print()
    
    # 加载图片
    print("📥 加载图片...")
    papercut = Image.open(papercut_path).convert('RGBA')
    scene = Image.open(scene_path).convert('RGB')
    
    print(f"   原始剪纸尺寸: {papercut.size}")
    print(f"   场景尺寸: {scene.size}")
    
    # 调整剪纸尺寸
    print("🔄 调整剪纸尺寸到 1736x1736...")
    papercut = papercut.resize((1736, 1736), Image.Resampling.LANCZOS)
    
    # 应用颜色和透明度
    print("🎨 应用颜色 #980015 和 75% 透明度...")
    papercut = apply_color_and_opacity(papercut, color=(152, 0, 21), opacity=0.75)
    
    # 合成
    print(f"✨ 合成到位置 ({x}, {y})...")
    scene_rgba = scene.convert('RGBA')
    composite = Image.new('RGBA', scene_rgba.size, (255, 255, 255, 0))
    composite.paste(scene_rgba, (0, 0))
    composite.paste(papercut, (x, y), papercut)
    
    # 保存
    final_image = composite.convert('RGB')
    final_image.save(output_path, 'PNG')
    
    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n✅ 合成完成！")
    print(f"📁 输出文件: {output_path}")
    print(f"📊 文件大小: {file_size:.2f} MB")
    print(f"📐 输出尺寸: {final_image.size}")
    print("\n💡 提示: 使用图片查看器打开 test_scene_output.png 查看效果")
    print("="*60)

if __name__ == "__main__":
    # 默认参数
    papercut_file = "papercut_1763997762.png"
    x_pos = 3916
    y_pos = 137
    
    # 命令行参数
    if len(sys.argv) > 1:
        papercut_file = sys.argv[1]
    if len(sys.argv) > 2:
        x_pos = int(sys.argv[2])
    if len(sys.argv) > 3:
        y_pos = int(sys.argv[3])
    
    # 运行测试
    test_composite(papercut_file, x_pos, y_pos)
    
    print("\n📝 使用方法:")
    print(f"   python test_scene_position.py [剪纸文件名] [X坐标] [Y坐标]")
    print(f"   例如: python test_scene_position.py papercut_1763997762.png 3916 137")
