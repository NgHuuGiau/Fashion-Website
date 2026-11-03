import subprocess
import os
import sys
import time
import urllib.request

env = os.environ.copy()
env['DJANGO_SETTINGS_MODULE'] = 'core.test_settings_sqlite'
env['SQLITE_TEST_DB'] = r'D:\Project\Fashion-Website\.tmp-e2e.sqlite3'
env['REDIS_URL'] = ''
env['SHOP_BANK_ACCOUNT'] = ''
env['VNPAY_TMN_CODE'] = ''

# Start server
proc = subprocess.Popen(
    [r"D:\Project\Fashion-Website\.venv\Scripts\python.exe", "backend/manage.py", "runserver", "127.0.0.1:8000", "--noreload"],
    cwd=r"D:\Project\Fashion-Website",
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Write PID to file for later cleanup
with open(r"D:\Project\Fashion-Website\server.pid", "w") as f:
    f.write(str(proc.pid))

print(f"Server started with PID: {proc.pid}")

# Wait for server to be ready
for i in range(20):
    time.sleep(1)
    try:
        resp = urllib.request.urlopen("http://localhost:8000/dang-nhap/", timeout=2)
        print(f"Server is ready! Status: {resp.status}")
        break
    except Exception as e:
        # Print server output so far
        pass
else:
    print("Server did not start in time")

# Keep process running
proc.wait()
