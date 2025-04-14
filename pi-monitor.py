import os
import time
import psutil
import pyautogui
import subprocess
from datetime import datetime
from git import Repo

# 设置文件保存路径
screenshot_dir = '/home/mrpumpkinsss/github_repository/pi-monitor/'
status_dir = '/home/mrpumpkinsss/github_repository/pi-monitor/'

# Git仓库路径
repo_path = '/home/mrpumpkinsss/github_repository/pi-monitor/'

# 创建文件夹（如果不存在）
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs(status_dir, exist_ok=True)

def get_cpu_usage():
    """获取CPU占用率"""
    return psutil.cpu_percent(interval=1)

def get_temp():
    """获取树莓派温度"""
    result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    temp = result.stdout.decode().split('=')[1].replace("’C", '')
    return temp

def get_memory_usage():
    """获取内存占用率"""
    memory = psutil.virtual_memory()
    return memory.percent

def take_screenshot(timestamp):
    """截取屏幕截图"""
    screenshot_path = os.path.join(screenshot_dir, f'screenshot_{timestamp}.png')
    pyautogui.screenshot(screenshot_path)
    return screenshot_path

def create_status_file(timestamp):
    """创建包含系统状态信息的txt文件"""
    cpu_usage = get_cpu_usage()
    temp = get_temp()
    memory_usage = get_memory_usage()
    
    status_file_path = os.path.join(status_dir, f'{timestamp}.txt')
    
    with open(status_file_path, 'w') as f:
        f.write(f"CPU Usage: {cpu_usage}%\n")
        f.write(f"Temperature: {temp}°C\n")
        f.write(f"Memory Usage: {memory_usage}%\n")
    
    return status_file_path

def git_push():
    """将截图和状态文件上传至GitHub"""
    repo = Repo(repo_path)
    repo.git.add(A=True)  # 将所有更改（新增文件、修改文件）加入到Git
    repo.index.commit(f"Added screenshot and status data for {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    origin = repo.remote(name='origin')
    origin.push()

def main():
    while True:
        # 获取当前时间戳
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # 截取屏幕并创建状态文件
        screenshot_path = take_screenshot(timestamp)
        status_file_path = create_status_file(timestamp)

        # 上传截图和状态文件到GitHub
        git_push()

        print(f"Screenshot and status data for {timestamp} uploaded.")

        # 每隔60秒执行一次
        time.sleep(60)

if __name__ == "__main__":
    main()
