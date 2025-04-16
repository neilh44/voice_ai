# /Users/nileshhanotia/Desktop/Voice AI/backend/test_imports.py

import sys
import os

# Print the current working directory
print(f"Current directory: {os.getcwd()}")

# Print Python's import path
print(f"Python path: {sys.path}")

# Try to import the packages
try:
    import app
    print("✅ Successfully imported 'app' package")
except ImportError as e:
    print(f"❌ Failed to import 'app' package: {e}")

try:
    import app.api
    print("✅ Successfully imported 'app.api' package")
except ImportError as e:
    print(f"❌ Failed to import 'app.api' package: {e}")

try:
    import app.core
    print("✅ Successfully imported 'app.core' package")
except ImportError as e:
    print(f"❌ Failed to import 'app.core' package: {e}")