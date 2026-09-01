"""
SubFlow AI - Unified Entry Point for Desktop GUI, CLI, and Web Interfaces.
"""

from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    args = sys.argv[1:]

    # Web Mode
    if "--web" in args or "-w" in args:
        from src.web.server import start_web_server
        port = 8080
        host = "127.0.0.1"
        for i, a in enumerate(args):
            if a in ("-p", "--port") and i + 1 < len(args):
                try:
                    port = int(args[i + 1])
                except ValueError:
                    pass
            elif a in ("-h", "--host") and i + 1 < len(args):
                host = args[i + 1]

        start_web_server(host=host, port=port)
        return

    # CLI Mode
    if len(args) > 0 and "--gui" not in args and "-g" not in args:
        from src.cli.cli_runner import run_cli
        sys.exit(run_cli(args))

    # GUI Mode (Default)
    try:
        from PyQt6.QtWidgets import QApplication
        from src.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("SubFlow AI")
        app.setOrganizationName("Antigravity")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except ImportError as e:
        print(f"[Error] PyQt6 is required for GUI mode: {e}", file=sys.stderr)
        print("You can run the web studio instead:\n  python main.py --web", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
