# open_ksa/__init__.py
try:
    from setuptools_scm import get_version  # type: ignore
except Exception:
    get_version = None

try:
    # Attempt to get the version from the SCM metadata if available
    __version__ = get_version() if get_version is not None else "0.0.0"
except Exception:
    # Fallback to a default version if SCM metadata is not available
    __version__ = "0.0.0"

from urllib.parse import urlparse, quote
from .download_file import download_file
from open_ksa.get_dataset_resource import get_dataset_resource
from open_ksa.get_dataset_resources import get_dataset_resources
from open_ksa.get_org_resources import get_org_resources
from open_ksa.ssl_adapter import SSLAdapter, SingletonSession
from open_ksa.organizations import organizations
from . import cli as _cli_module


class _CliProxy:
    """Callable proxy that exposes CLI module attributes and is itself callable.

    Calling the proxy delegates to `download_cli` by default so `ok.cli()` works,
    while attribute access proxies to the underlying `open_ksa.cli` module.
    """
    def __call__(self, *args, **kwargs):
        return _cli_module.download_cli(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(_cli_module, name)


# Expose a callable proxy as `cli` on the package object so both `ok.cli` and
# `ok.cli()` are usable by users (module access and quick-call behavior).
cli = _CliProxy()
