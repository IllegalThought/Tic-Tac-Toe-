import sys

def main():
    if sys.version_info < (3,11):
        raise SystemExit('Python 3.11 or newer is required.')
    try:
        from gui.app import App
    except ModuleNotFoundError as exc:
        raise SystemExit(f'Missing dependency: {exc.name}. Run: python -m pip install -r requirements.txt') from exc
    try:
        App().mainloop()
    except Exception as exc:
        if 'display' in str(exc).lower():
            raise SystemExit('A local desktop display is required. Run this app on Windows, macOS, or a Linux desktop.') from exc
        raise
if __name__ == '__main__': main()
