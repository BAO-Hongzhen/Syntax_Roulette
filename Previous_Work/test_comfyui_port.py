"""
测试 ComfyUI 端口
检测桌面版 ComfyUI 实际使用的端口
"""

import requests
import socket

def test_port(port):
    """测试端口是否可访问"""
    try:
        # 测试 TCP 连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 开放")
            
            # 尝试访问 API
            try:
                response = requests.get(f"http://127.0.0.1:{port}/system_stats", timeout=3)
                print(f"   HTTP 状态码: {response.status_code}")
                if response.status_code == 200:
                    print(f"   ✅ ComfyUI API 响应成功")
                    print(f"   系统信息: {response.json()}")
                    return True
            except requests.exceptions.RequestException as e:
                print(f"   ⚠️ HTTP 请求失败: {e}")
                
                # 尝试访问根路径
                try:
                    response = requests.get(f"http://127.0.0.1:{port}/", timeout=3)
                    print(f"   根路径状态码: {response.status_code}")
                    if response.status_code == 200:
                        print(f"   ✅ 端口 {port} 有 HTTP 服务运行")
                        return True
                except:
                    pass
        else:
            print(f"❌ 端口 {port} 关闭")
    except Exception as e:
        print(f"❌ 测试端口 {port} 失败: {e}")
    
    return False


def main():
    print("🔍 扫描 ComfyUI 可能使用的端口...\n")
    
    # 常见端口列表
    common_ports = [
        8188,  # ComfyUI 默认端口
        8000,  # 常用端口
        8080,  # 常用端口
        3000,  # 常用端口
        5000,  # 常用端口
        7860,  # Gradio 默认
        8888,  # Jupyter 常用
        3001,  # 备用端口
        8001,  # 备用端口
    ]
    
    found_ports = []
    
    for port in common_ports:
        print(f"\n测试端口 {port}:")
        if test_port(port):
            found_ports.append(port)
    
    print("\n" + "="*60)
    if found_ports:
        print(f"✅ 找到可用端口: {found_ports}")
        print(f"\n💡 建议使用端口: {found_ports[0]}")
        print(f"   请在 main_ComfyUIDesktop.py 中修改为:")
        print(f'   comfyui_client = ComfyUIClient(server_address="127.0.0.1:{found_ports[0]}")')
    else:
        print("❌ 未找到运行中的 ComfyUI 服务")
        print("\n💡 请确认:")
        print("   1. ComfyUI Desktop 是否已启动")
        print("   2. 检查 ComfyUI 的启动日志，查看实际使用的端口")
        print("   3. 可能需要在 ComfyUI 设置中查看端口配置")
    print("="*60)


if __name__ == "__main__":
    main()
