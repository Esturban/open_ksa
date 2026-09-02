"""CLI entrypoints for open_ksa."""

import argparse
from typing import List, Optional

from . import downloader
from . import manifest as manifest_module
from . import notebook
from .models import DownloadManifest


def browse_cli(query: Optional[str] = None, dest: str = ".") -> Optional[DownloadManifest]:
    """Search organizations, pick a dataset, and download it -- no prior org ID needed.

    Prompts interactively at each step (organization, then dataset) using the
    existing notebook browse helpers, then downloads the pick via `download_cli`.
    Returns the resulting manifest, or None if the user quits at either step.
    """
    try:
        organization_id = notebook.browse_organizations(query=query, interactive=True)
        if not organization_id:
            return None
        dataset_id = notebook.browse_datasets(organization_id, interactive=True)
        if not dataset_id:
            return None
    except ValueError as exc:
        print(f"Invalid selection: {exc}")
        return None

    return download_cli(dataset_id=dataset_id, organization_id=organization_id, dest=dest)


def download_cli(dataset_id: Optional[str] = None, organization_id: Optional[str] = None, dest: str = '.', sample_size: int = 0, formats: Optional[list] = None, interactive: bool = False):
    """Execute a download via the canonical downloader and write a manifest to disk."""
    manifest, _ = downloader.fetch_and_load(
        organization_id=organization_id,
        dataset_id=dataset_id,
        dest=dest,
        sample_size=sample_size,
        formats=formats,
        interactive=interactive,
    )

    manifest_path = f"{dest.rstrip('/')}/manifest.json"
    manifest_module.write_manifest(manifest, manifest_path)
    return manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="open-ksa",
        description="Browse and download datasets from the KSA Open Data portal.",
    )
    subparsers = parser.add_subparsers(dest="command")

    browse_parser = subparsers.add_parser(
        "browse", help="Search organizations, pick a dataset, and download it. Default command."
    )
    browse_parser.add_argument("--query", default=None, help="Search term for organizations.")
    browse_parser.add_argument("--dest", default=".", help="Directory to download into.")

    download_parser = subparsers.add_parser(
        "download", help="Download a dataset or organization directly, given a known ID."
    )
    download_parser.add_argument("--dataset-id", default=None)
    download_parser.add_argument("--organization-id", default=None)
    download_parser.add_argument("--dest", default=".")
    download_parser.add_argument("--sample-size", type=int, default=0)
    download_parser.add_argument("--formats", nargs="*", default=None, help="Restrict to these formats, e.g. csv json.")

    # `browse` is the default when no subcommand is given, so give the top-level
    # parser the same defaults as the browse subparser (argparse only populates
    # subparser-only args when that subcommand is actually selected).
    parser.set_defaults(command="browse", query=None, dest=".")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Console-script entry point for `open-ksa`. Browses by default; `download` for a known ID."""
    args = _build_parser().parse_args(argv)

    try:
        if args.command == "download":
            manifest = download_cli(
                dataset_id=args.dataset_id,
                organization_id=args.organization_id,
                dest=args.dest,
                sample_size=args.sample_size,
                formats=args.formats,
            )
            print(f"Downloaded {len(manifest.entries)} resource(s) to {args.dest}")
            return 0

        # No subcommand, or explicit `browse`, both land here.
        manifest = browse_cli(query=args.query, dest=args.dest)
        if manifest is None:
            print("No dataset selected.")
            return 1
        print(f"Downloaded {len(manifest.entries)} resource(s) to {args.dest}")
        return 0
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1
