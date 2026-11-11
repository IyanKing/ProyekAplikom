"""Start the local Streamlit app for the Windows desktop package."""

import os
from pathlib import Path
import sys

from streamlit.web import cli as stcli


def main():
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    app_path = bundle_dir / "app.py"
    os.chdir(bundle_dir)
    user_data = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "GradasiAgregat"
    user_data.mkdir(parents=True, exist_ok=True)
    os.environ["GRADASI_DATA_DIR"] = str(user_data)

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address=127.0.0.1",
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]
    stcli.main()


if __name__ == "__main__":
    main()