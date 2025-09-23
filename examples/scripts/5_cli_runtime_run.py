import sys
import pathlib
from pathlib import Path
import json

repo_root = pathlib.Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


def main(dataset_id: str | None = None, dest: str = "tmp_real_cli", sample_size: int = 5, demo: bool = False):
    try:
        from open_ksa import cli, downloader
    except Exception:
        # Try to ensure repo root is on sys.path and retry
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from open_ksa import cli, downloader

    Path(dest).mkdir(parents=True, exist_ok=True)

    if demo:
        # simple demo manifest without network
        manifest = {
            "timestamp": 0,
            "requested_by": "cli-demo",
            "dest_path": dest,
            "entries": [
                {
                    "resource_id": "demo-res-1",
                    "url": "https://example.com/demo.csv",
                    "local_path": f"{dest.rstrip('/')}/demo.csv",
                    "status": "demo",
                    "reason": "fallback-demo",
                }
            ],
        }
        cli_module_manifest = manifest
    else:
        # If dataset_id not supplied, pick the first dataset from the first organization
        if dataset_id is None:
            from open_ksa import organizations

            orgs = organizations(size=10)
            if not orgs.get("content"):
                raise SystemExit("No organizations found; cannot auto-select dataset")
            first_org = orgs["content"][0]
            org_id = first_org.get("publisherID") or first_org.get("id")
            from open_ksa.get_org_resources import get_org_resources

            org_res = get_org_resources(org_id=org_id)
            dataset_ids = org_res.get("dataset_ids", [])
            if not dataset_ids:
                raise SystemExit("No datasets for selected org; cannot auto-select dataset")
            dataset_id = dataset_ids[0]

        # Call the real CLI which calls downloader.fetch_and_load
        cli_module_manifest = cli.download_cli(dataset_id=dataset_id, dest=dest, sample_size=sample_size, interactive=False)

    print("Manifest returned:")
    print(json.dumps(cli_module_manifest, indent=2))
    print('\nManifest file on disk:')
    manifest_path = f"{dest.rstrip('/')}/manifest.json"
    print(manifest_path)
    if Path(manifest_path).exists():
        print(Path(manifest_path).read_text())
    else:
        print("(not written yet)")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Run a CLI download demo (real or demo)")
    p.add_argument("--dataset-id", help="UUID dataset id to download", default=None)
    p.add_argument("--dest", help="Destination dir", default="tmp_real_cli")
    p.add_argument("--sample-size", type=int, default=5)
    p.add_argument("--demo", action="store_true", help="Run demo without network")
    args = p.parse_args()
    main(dataset_id=args.dataset_id, dest=args.dest, sample_size=args.sample_size, demo=args.demo)


