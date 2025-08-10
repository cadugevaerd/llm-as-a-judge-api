"""Test script to validate pyproject.toml configuration."""

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python versions

from pathlib import Path
import pytest


def test_pyproject_toml_exists():
    """Test that pyproject.toml exists in project root."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml not found"


def test_pyproject_toml_valid_syntax():
    """Test that pyproject.toml has valid TOML syntax."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    assert isinstance(config, dict), "pyproject.toml should parse to a dictionary"


def test_pyproject_has_required_sections():
    """Test that pyproject.toml has all required sections."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    # Required sections
    assert "build-system" in config, "Missing [build-system] section"
    assert "project" in config, "Missing [project] section"
    
    # Project metadata
    project = config["project"]
    assert "name" in project, "Missing project name"
    assert "version" in project, "Missing project version"
    assert "dependencies" in project, "Missing dependencies"


def test_pyproject_has_dev_dependencies():
    """Test that development dependencies are configured."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    assert "project" in config
    assert "optional-dependencies" in config["project"]
    assert "dev" in config["project"]["optional-dependencies"]
    
    dev_deps = config["project"]["optional-dependencies"]["dev"]
    dev_dep_names = [dep.split(">=")[0].split("==")[0] for dep in dev_deps]
    
    assert "black" in dev_dep_names, "black not in dev dependencies"
    assert "pytest" in dev_dep_names, "pytest not in dev dependencies"
    assert "ruff" in dev_dep_names, "ruff not in dev dependencies"


def test_black_configuration():
    """Test that Black is properly configured."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    assert "tool" in config, "Missing [tool] section"
    assert "black" in config["tool"], "Missing [tool.black] section"
    
    black_config = config["tool"]["black"]
    assert "line-length" in black_config, "Missing line-length in Black config"
    assert "target-version" in black_config, "Missing target-version in Black config"


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])