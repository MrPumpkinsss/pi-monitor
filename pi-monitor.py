import os
import time
import psutil
from git import Repo

# 状态文件保存路径
status_path = '/home/mrpumpkinsss/github_repository/pi-monitor/status/status.txt'

# Git仓库路径
repo_path = '/home/mrpumpkinsss/github_repository/pi-monitor/'

# 确保目录存在
os.makedirs(os.path.dirname(status_path), exist_ok=True)

def get_cpu_usage():
    """获取CPU占用率"""
    return psutil.cpu_percent(interval=1)

def get_temp():
    """获取树莓派温度"""
    try:
        import subprocess
        result = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE)
        temp = result.stdout.decode().split('=')[1].replace("'C", '').strip()
        return temp
    except Exception:
        return "N/A"

def get_memory_usage():
    """获取内存占用率"""
    memory = psutil.virtual_memory()
    return memory.percent

def get_process_list():
    """获取所有进程的任务管理器风格信息（含真实CPU占用率）"""
    # 首先预热一次
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            proc.cpu_percent(interval=None)
            procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # 等待0.5秒
    time.sleep(0.5)
    process_info = []
    for proc in procs:
        try:
            info = proc.as_dict(attrs=['pid', 'name', 'memory_percent'])
            info['cpu_percent'] = proc.cpu_percent(interval=None)
            process_info.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # 按CPU占用排序，降序
    return sorted(process_info, key=lambda x: x['cpu_percent'], reverse=True)

def create_status_file():
    """创建包含系统状态和任务管理器进程列表的txt文件"""
    cpu_usage = get_cpu_usage()
    temp = get_temp()
    memory_usage = get_memory_usage()
    process_list = get_process_list()

    with open(status_path, 'w') as f:
        f.write(f"CPU Usage: {cpu_usage}%\n")
        f.write(f"Temperature: {temp}°C\n")
        f.write(f"Memory Usage: {memory_usage}%\n\n")
        f.write("Task Manager:\n")
        f.write(f"{'PID':>6} {'Name':<25} {'CPU%':>6} {'MEM%':>6}\n")
        f.write("="*48 + "\n")
        for proc in process_list:
            f.write(f"{proc['pid']:>6} {proc['name'][:24]:<25} {proc['cpu_percent']:>6.1f} {proc['memory_percent']:>6.1f}\n")

def git_push():
    """将状态文件上传至GitHub"""
    try:
        repo = Repo(repo_path)
        repo.git.add(A=True)
        repo.index.commit("Update status with task manager info")
        origin = repo.remote(name='origin')
        origin.push()
        print("Pushed to GitHub successfully.")
    except Exception as e:
        print(f"Error during git push: {e}")

def main():
    while True:
        create_status_file()
        git_push()
        print(f"Status file saved at {status_path}")
        print("Status data uploaded.")
        # 每隔6小时（21600秒）执行一次
        time.sleep(21600)

if __name__ == "__main__":
    main()
