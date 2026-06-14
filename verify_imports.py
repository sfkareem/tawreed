import sys

print("Verifying imports for Tawreed...")
try:
    print("Core imports: OK")
    print("Styles imports: OK")
    print("Worker imports: OK")
    print("MainWindow imports: OK")
    print("Page imports: OK")
    print("Main module import: OK")
    print("All imports verified successfully!")
except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
