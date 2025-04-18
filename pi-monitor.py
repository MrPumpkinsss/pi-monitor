import os
import time
import psutil
import subprocess

from git import Repo

# 设置文件保存路径
screenshot_path = '/home/mrpumpkinsss/github_repository/pi-monitor/screenshots/screenshot.png'
status_path = '/home/mrpumpkinsss/github_repository/pi-monitor/status/status.txt'

# Git仓库路径
repo_path = '/home/mrpumpkinsss/github_repository/pi-monitor/'

# Ensure the directories exist
os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
os.makedirs(os.path.dirname(status_path), exist_ok=True)

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

def take_screenshot():
    """使用 scrot 工具截图"""
    subprocess.run(['scrot', '-o', screenshot_path])


def create_status_file():
    """创建包含系统状态信息的txt文件"""
    cpu_usage = get_cpu_usage()
    temp = get_temp()
    memory_usage = get_memory_usage()
    
    with open(status_path, 'w') as f:
        f.write(f"CPU Usage: {cpu_usage}%\n")
        f.write(f"Temperature: {temp}°C\n")
        f.write(f"Memory Usage: {memory_usage}%\n")

def git_push():
    """将截图和状态文件上传至GitHub"""
    try:
        repo = Repo(repo_path)
        repo.git.add(A=True)  # 将所有更改（新增文件、修改文件）加入到Git
        repo.index.commit(f"Added screenshot and status data")
        origin = repo.remote(name='origin')
        origin.push()
        print("Pushed to GitHub successfully.")
    except Exception as e:
        print(f"Error during git push: {e}")

def main():
    while True:
        # 截取屏幕并创建状态文件
        take_screenshot()
        create_status_file()

        # 上传截图和状态文件到GitHub
        git_push()

        print(f"Screenshot saved at {screenshot_path}")
        print(f"Status file saved at {status_path}")
        print("Screenshot and status data uploaded.")

        # 每隔7200秒执行一次
        time.sleep(7200)

if __name__ == "__main__":
    main()
