import os
from pathlib import Path

Import("env")


def load_dotenv(path):
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        values[key] = value

    return values


project_dir = Path(env.subst("$PROJECT_DIR"))
dotenv = load_dotenv(project_dir / ".env")

def inject(env_var, macro_name):
    value = os.environ.get(env_var) or dotenv.get(env_var)
    if value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        env.Append(BUILD_FLAGS=[f'-D{macro_name}=\\"{escaped}\\"'])


inject("OWM_API_KEY", "PIXELPULSE_OWM_API_KEY")
inject("WIFI_SSID", "PIXELPULSE_WIFI_SSID")
inject("WIFI_PASS", "PIXELPULSE_WIFI_PASS")
