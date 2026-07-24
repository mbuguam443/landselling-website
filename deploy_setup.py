import subprocess
import sys
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'land_selling.settings'

def run(cmd):
    print(f"\n> {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

print("=== Prime Lands Deployment Setup ===")

print("\n[1/4] Installing dependencies...")
run(f"{sys.executable} -m pip install -r requirements.txt")

print("\n[2/4] Collecting static files...")
run(f"{sys.executable} manage.py collectstatic --noinput")

print("\n[3/4] Running migrations...")
run(f"{sys.executable} manage.py migrate")

print("\n[4/4] Setup complete!")
print("Visit https://prime-lands.schones-heim-builders.co.ke/")
