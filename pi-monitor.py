import os
import time
import psutil
import pyautogui
import subprocess
from git import Repo

# 设置文件保存路径
screenshot_path = '/home/mrpumpkinsss/github_repository/pi-monitor/screenshots/screenshot.png'
status_path = '/home/mrpumpkinsss/github_repository/pi-monitor/status/status.txt'
tasks_path = '/home/mrpumpkinsss/github_repository/pi-monitor/status/tasks.txt'

# Git仓库路径
repo_path = '/home/mrpumpkinsss/github_repository/pi-monitor/'

# Ensure the directories exist
os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
os.makedirs(os.path.dirname(status_path), exist_ok=True)

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
    temp = result.stdout.decode().split('=')[1].replace("’C", '')
    return temp

def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent

def take_screenshot():
    pyautogui.screenshot(screenshot_path)

def create_status_file():
    cpu_usage = get_cpu_usage()
    temp = get_temp()
    memory_usage = get_memory_usage()
    
    with open(status_path, 'w') as f:
        f.write(f"CPU Usage: {cpu_usage}%\n")
        f.write(f"Temperature: {temp}°C\n")
        f.write(f"Memory Usage: {memory_usage}%\n")

def create_task_file():
    """生成任务列表文件"""
    with open(tasks_path, 'w') as f:
        f.write(f"{'PID':>6} {'Name':<25} {'CPU%':>6} {'Memory%':>8}\n")
        f.write("-" * 50 + "\n")
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pid = proc.info['pid']
                name = proc.info['name'][:25]
                cpu = proc.info['cpu_percent']
                memory = proc.info['memory_percent']
                f.write(f"{pid:>6} {name:<25} {cpu:>6.1f} {memory:>8.1f}\n")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

def git_push():
    try:
        repo = Repo(repo_path)
        repo.git.add(A=True)
        repo.index.commit("Added screenshot, status, and task data")
        origin = repo.remote(name='origin')
        origin.push()
        print("Pushed to GitHub successfully.")
    except Exception as e:
        print(f"Error during git push: {e}")

def main():
    while True:
        take_screenshot()
        create_status_file()
        create_task_file()
        git_push()

        print(f"Screenshot saved at {screenshot_path}")
        print(f"Status file saved at {status_path}")
        print(f"Tasks file saved at {tasks_path}")
        print("All data uploaded.\n")

        time.sleep(600)

if __name__ == "__main__":
    main()
