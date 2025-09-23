try:
    # package import when installed or running from project root
    from open_ksa import organizations
except Exception:
    # fallback: local import path
    import importlib.util
    import sys
    import pathlib

    repo_root = pathlib.Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))
    from open_ksa import organizations


if __name__ == "__main__":
    orgs = organizations()
    print("Found", len(orgs.get("content", [])), "organizations (sample)")
