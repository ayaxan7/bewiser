import sys
import os
sys.path.append('/Users/ayaan/development/bewiser')

print("Testing benchmark service...")

# Test 1: Import test
try:
    from app.services.benchmark_service import fetch_nifty50_data
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Basic data fetch
try:
    df = fetch_nifty50_data(30)  # 30 days
    print(f"✅ Data fetch successful - Shape: {df.shape}")
    print(f"✅ Columns: {list(df.columns)}")
    print(f"✅ Current Nifty value: {df['nav'].iloc[-1]:.2f}")
except Exception as e:
    print(f"❌ Data fetch failed: {e}")
    exit(1)

print("🎉 Basic benchmark service test PASSED!")
