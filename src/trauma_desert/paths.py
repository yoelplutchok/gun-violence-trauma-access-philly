"""
Centralized path management for the Trauma Desert project.

All paths are defined relative to the project root, ensuring consistency
across scripts regardless of where they're called from.
"""

from pathlib import Path

# Project root is two levels up from this file (src/trauma_desert/paths.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class ProjectPaths:
    """
    Centralized path definitions for the Trauma Desert project.
    
    Usage:
        from trauma_desert.paths import PATHS
        
        shootings_file = PATHS.raw / "shootings_2024-01-15.csv"
        output_map = PATHS.interactive / "trauma_desert_map.html"
    """

    def __init__(self, root: Path):
        self.root = root

        # Data directories
        self.data = root / "data"
        self.raw = self.data / "raw"
        self.processed = self.data / "processed"
        self.geo = self.data / "geo"
        self.isochrones = self.data / "isochrones"
        self.manual = self.data / "manual"

        # Script directories
        self.scripts = root / "scripts"
        self.scripts_collect = self.scripts / "collect"
        self.scripts_process = self.scripts / "process"
        self.scripts_analyze = self.scripts / "analyze"
        self.scripts_visualize = self.scripts / "visualize"

        # Source code
        self.src = root / "src"
        self.package = self.src / "trauma_desert"

        # Outputs
        self.outputs = root / "outputs"
        self.figures = self.outputs / "figures"
        self.interactive = self.outputs / "interactive"
        self.tables = self.outputs / "tables"

        # Other directories
        self.configs = root / "configs"
        self.docs = root / "docs"
        self.tests = root / "tests"
        self.logs = root / "logs"

    @property
    def params_file(self) -> Path:
        """Path to the main configuration file."""
        return self.configs / "params.yml"

    @property
    def manifest_file(self) -> Path:
        """Path to the data manifest file."""
        return self.raw / "manifest.json"

    def ensure_dirs(self) -> None:
        """Create all project directories if they don't exist."""
        dirs = [
            self.raw,
            self.processed,
            self.geo,
            self.isochrones,
            self.manual,
            self.scripts_collect,
            self.scripts_process,
            self.scripts_analyze,
            self.scripts_visualize,
            self.figures,
            self.interactive,
            self.tables,
            self.configs,
            self.docs,
            self.tests,
            self.logs,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        return f"ProjectPaths(root={self.root})"


# Singleton instance for easy importing
PATHS = ProjectPaths(PROJECT_ROOT)


if __name__ == "__main__":
    # Quick test when run directly
    print(f"Project root: {PATHS.root}")
    print(f"Raw data: {PATHS.raw}")
    print(f"Processed data: {PATHS.processed}")
    print(f"Params file: {PATHS.params_file}")
    print(f"Manifest file: {PATHS.manifest_file}")

