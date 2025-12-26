# Contributing to Philadelphia Trauma Deserts

Thank you for your interest in contributing to this project!

## How to Contribute

### Reporting Issues
- Use the GitHub Issues tab to report bugs or suggest enhancements
- Include as much detail as possible: steps to reproduce, expected vs actual behavior

### Pull Requests
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run validation (`make validate`)
5. Commit with clear messages
6. Push and create a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to all functions
- Keep functions focused and small

### Data Updates
If you want to refresh the data:
1. Run `make collect` to download latest data
2. Run `make process` to reprocess
3. Run `make analyze` to regenerate analysis
4. Run `make validate` to verify data quality

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/trauma-desert.git
cd trauma-desert

# Create environment
conda env create -f environment.yml
conda activate trauma-desert

# Run tests
make validate
```

## Questions?
Open an issue with the "question" label.

