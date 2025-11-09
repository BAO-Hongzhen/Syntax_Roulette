"""
环境检测脚本
运行此脚本检查所有依赖是否正确安装
"""

import sys

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    print("✅ Python版本符合要求")
    return True

def check_package(package_name, import_name=None):
    """检查单个包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', '未知')
        print(f"✅ {package_name}: {version}")
        return True
    except ImportError:
        print(f"❌ {package_name}: 未安装")
        return False

def main():
    print("=" * 60)
    print("🔍 Syntax Roulette - 环境检测")
    print("=" * 60)
    print()
    
    # 检查Python版本
    print("【1】检查Python版本")
    python_ok = check_python_version()
    print()
    
    # 检查必需的包
    print("【2】检查必需依赖")
    packages = {
        'gradio': 'gradio',
        'Pillow': 'PIL',
        'numpy': 'numpy',
    }
    
    all_installed = True
    for package_name, import_name in packages.items():
        if not check_package(package_name, import_name):
            all_installed = False
    
    print()
    
    # 检查可选的包
    print("【3】检查可选依赖")
    optional_packages = {
        'requests': 'requests',
        'streamlit': 'streamlit',
    }
    
    for package_name, import_name in optional_packages.items():
        check_package(package_name, import_name)
    
    print()
    print("=" * 60)
    
    # 总结
    if python_ok and all_installed:
        print("🎉 恭喜！所有必需依赖已正确安装")
        print("你可以运行以下命令启动应用：")
        print()
        print("    python main.py")
        print()
        print("或者双击运行 启动应用.bat (Windows)")
    else:
        print("⚠️  部分依赖缺失，请运行以下命令安装：")
        print()
        print("    pip install gradio pillow numpy")
        print()
        if not python_ok:
            print("❌ Python版本不符合要求")
            print("请升级到Python 3.8或更高版本")
            print("下载地址: https://www.python.org/downloads/")
    
    print("=" * 60)
    print()

if __name__ == "__main__":
    main()
    input("按回车键退出...")
