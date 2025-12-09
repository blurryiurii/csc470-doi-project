# Test Suite

## Getting Started

1. Install Dependencies

   ```console
   cd src
   pip install -r requirements.txt
   pip install -r test_requirements.txt
   ```

2. Run All Tests

   ```console
   pytest tests/ -v
   ```

   Or Run Specific Test Files:

   ```console
   pytest tests/test_api.py -v
   pytest tests/test_properties.py -v
