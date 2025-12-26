# Trauma Desert Project Makefile
# Run `make help` for available commands

.PHONY: help setup collect isochrones process analyze visualize test clean all

# Default target
help:
	@echo "Trauma Desert Project - Available Commands"
	@echo "==========================================="
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - Create virtual environment and install dependencies"
	@echo "  make setup-conda - Create conda environment from environment.yml"
	@echo ""
	@echo "Data Pipeline:"
	@echo "  make collect     - Run all data collection scripts"
	@echo "  make isochrones  - Generate drive-time isochrones for trauma centers"
	@echo "  make process     - Run all data processing scripts"
	@echo "  make analyze     - Run statistical analysis"
	@echo "  make visualize   - Generate all maps and figures"
	@echo ""
	@echo "Quality:"
	@echo "  make test        - Run validation checks"
	@echo "  make lint        - Run code formatting (black)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean       - Remove processed files (preserve raw data)"
	@echo "  make clean-all   - Remove all generated files (including raw)"
	@echo "  make all         - Full pipeline execution"
	@echo ""

# Environment setup
setup:
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install -e .
	@echo ""
	@echo "Environment created! Activate with: source .venv/bin/activate"

setup-conda:
	conda env create -f environment.yml
	@echo ""
	@echo "Conda environment created! Activate with: conda activate trauma-desert"

# Data collection
collect:
	@echo "Running data collection scripts..."
	python scripts/collect/download_shootings.py
	python scripts/collect/compile_trauma_centers.py
	python scripts/collect/geocode_trauma_centers.py
	python scripts/collect/download_census_tracts.py
	python scripts/collect/download_demographics.py
	@echo "Data collection complete."

# Isochrone generation (expensive, run separately)
isochrones:
	@echo "Generating isochrones for trauma centers..."
	@echo "Note: This uses API calls. Ensure .env is configured."
	python scripts/collect/generate_isochrones.py
	@echo "Isochrone generation complete."

# Data processing
process:
	@echo "Running data processing scripts..."
	python scripts/process/clean_shootings.py
	python scripts/process/assign_shootings_to_tracts.py
	python scripts/process/calculate_tract_density.py
	python scripts/process/calculate_transport_times.py
	python scripts/process/create_master_dataset.py
	@echo "Data processing complete."

# Analysis
analyze:
	@echo "Running analysis scripts..."
	python scripts/analyze/bivariate_classification.py
	python scripts/analyze/identify_trauma_deserts.py
	python scripts/analyze/demographic_disparity.py
	python scripts/analyze/golden_hour_analysis.py
	python scripts/analyze/temporal_trends.py
	@echo "Analysis complete."

# Visualization
visualize:
	@echo "Generating visualizations..."
	python scripts/visualize/create_interactive_map.py
	python scripts/visualize/create_static_maps.py
	python scripts/visualize/create_charts.py
	@echo "Visualization complete."

# Testing and validation
test:
	@echo "Running validation checks..."
	python -m pytest tests/ -v
	@echo "Validation complete."

lint:
	@echo "Formatting code with black..."
	black src/ scripts/ tests/
	@echo "Formatting complete."

# Cleanup
clean:
	@echo "Removing processed data files..."
	rm -f data/processed/*.csv
	rm -f data/processed/*.geojson
	rm -f outputs/figures/*.png
	rm -f outputs/figures/*.pdf
	rm -f outputs/interactive/*.html
	rm -f outputs/tables/*.csv
	@echo "Clean complete. Raw data preserved."

clean-all: clean
	@echo "Removing raw data files..."
	rm -f data/raw/*.csv
	rm -f data/raw/*.json
	rm -f data/geo/*.geojson
	rm -f data/geo/*.shp
	rm -f data/geo/*.dbf
	rm -f data/geo/*.shx
	rm -f data/geo/*.prj
	rm -f data/isochrones/*.geojson
	@echo "Full clean complete."

# Full pipeline
all: collect isochrones process analyze visualize test
	@echo ""
	@echo "=========================================="
	@echo "Full pipeline complete!"
	@echo "Interactive map: outputs/interactive/trauma_desert_map.html"
	@echo "=========================================="

