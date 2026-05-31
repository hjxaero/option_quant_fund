"""Verify key project directories and files exist."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_root_files_exist():
    for name in ("README.md", "pyproject.toml"):
        assert (ROOT / name).is_file(), f"missing {name}"


def test_config_exists():
    assert (ROOT / "configs" / "default.yaml").is_file()


def test_data_directories_exist():
    for sub in ("raw", "processed", "sample"):
        assert (ROOT / "data" / sub).is_dir()


def test_docs_exist():
    for name in ("architecture.md", "data_dictionary.md", "roadmap.md"):
        assert (ROOT / "docs" / name).is_file(), f"missing docs/{name}"


def test_fast_lane_readmes_exist():
    assert (ROOT / "experiments" / "README.md").is_file()
    assert (ROOT / "notebooks" / "README.md").is_file()


def test_package_layout_exists():
    pkg = ROOT / "src" / "option_quant_fund"
    assert pkg.is_dir()
    for module in ("data", "option_chain", "greeks", "backtest", "risk", "utils"):
        assert (pkg / module / "__init__.py").is_file(), f"missing {module}/__init__.py"
