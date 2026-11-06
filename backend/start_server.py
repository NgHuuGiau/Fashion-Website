import os
import subprocess
import time

env = os.environ.copy()
env["DJANGO_SETTINGS_MODULE"] = "core.test_settings_sqlite"
env["SQLITE_TEST_DB"] = r"D:\Project\Fashion-Website\.tmp-e2e.sqlite3"
env["REDIS_URL"] = ""
env["SHOP_BANK_ACCOUNT"] = ""
env["VNPAY_TMN_CODE"] = ""

# Start server
proc = subprocess.Popen(
    [
        r"D:\Project\Fashion-Website\.venv\Scripts\python.exe",
        "backend/manage.py",
        "runserver",
        "127.0.0.1:8000",
        "--noreload",
    ],
    cwd=r"D:\Project\Fashion-Website",
    env=env,
    stdout=open(r"D:\Project\Fashion-Website\server.log", "w"),
    stderr=subprocess.STDOUT,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
)

print(f"Server started with PID: {proc.pid}")

# Wait for server
for _ in range(15):
    time.sleep(1)
    try:
        import urllib.request

        urllib.request.urlopen("http://localhost:8000/dang-nhap/", timeout=2)  # nosec B310
        print("Server is ready!")
        break
    except Exception:
        pass
else:
    print("Server did not start in time")

# Read logs
time.sleep(1)
try:
    with open(r"D:\Project\Fashion-Website\server.log", "r") as f:
        print("Server logs:")
        print(f.read())
except Exception:
    pass
