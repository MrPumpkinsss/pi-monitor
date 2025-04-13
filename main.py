import time
import psutil
import subprocess
import os

def take_screenshot():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"/home/mrpumpkinsss/github_repository/pi-monitor/screenshots/screenshot_{timestamp}.png"
    subprocess.run(['scrot', filename])
    return filename

def get_cpu_info():
    cpu_usage = psutil.cpu_percent(interval=1)
    try:
        cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
    except KeyError:
        cpu_temp = "N/A"
    return cpu_usage, cpu_temp

def upload_to_github(file_path):
    repo_dir = '/home/mrpumpkinsss/github_repository/pi-monitor'
    os.chdir(repo_dir)
    subprocess.run(['cp', file_path, './screenshots/'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'Add screenshot {file_path}'])
    subprocess.run(['git', 'push'])

# 每5秒截图并上传
while True:
    screenshot = take_screenshot()
    cpu_usage, cpu_temp = get_cpu_info()
    print(f"CPU Usage: {cpu_usage}%, CPU Temperature: {cpu_temp}°C")
    upload_to_github(screenshot)
    time.sleep(5)
