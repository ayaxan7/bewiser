#!/usr/bin/env python3
"""
Test script to verify real Nifty 50 data fetching
"""
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.benchmark_service import fetch_nifty50_data
import pandas as pd


def test_real_nifty_data():
    """Test fetching real Nifty 50 data"""
    print("🧪 Testing Real Nifty 50 Data Fetching...")
    print("=" * 50)
    
    try:
        # Test with different time periods
        periods = [30, 90, 365, 730]
        
        for days in periods:
            print(f"\n📊 Fetching {days} days of Nifty 50 data...")
            
            df = fetch_nifty50_data(days_back=days)
            
            if not df.empty:
                print(f"✅ Success! Got {len(df)} data points")
                print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"   NAV range: {df['nav'].min():.0f} to {df['nav'].max():.0f}")
                print(f"   Latest NAV: {df['nav'].iloc[-1]:.0f}")
                
                # Calculate some basic stats
                returns = df['nav'].pct_change().dropna()
                if len(returns) > 0:
                    annual_vol = returns.std() * (252 ** 0.5) * 100
                    print(f"   Estimated Annual Volatility: {annual_vol:.1f}%")
                
            else:
                print("❌ Failed - Empty dataset returned")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Real Nifty 50 data test completed successfully!")
    return True


def test_benchmark_comparison():
    """Test a quick benchmark comparison"""
    print("\n🔄 Testing Benchmark Comparison...")
    
    try:
        from app.services.benchmark_service import calculate_benchmark_metrics
        
        # Create sample fund data
        dates = pd.date_range(start='2024-01-01', end='2024-07-26', freq='D')
        dates = dates[dates.weekday < 5]  # Business days only
        
        # Simulate a fund that outperforms the market
        fund_data = pd.DataFrame({
            'date': dates,
            'nav': [100 * (1.15/252) ** i for i in range(len(dates))]  # 15% annual growth
        })
        
        # Get real Nifty data for comparison
        nifty_data = fetch_nifty50_data(days_back=200)
        
        if not nifty_data.empty and not fund_data.empty:
            metrics = calculate_benchmark_metrics(fund_data, nifty_data)
            
            print("📈 Benchmark Comparison Metrics:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    if 'pct' in key:
                        print(f"   {key}: {value:.2f}%")
                    else:
                        print(f"   {key}: {value:.3f}")
                else:
                    print(f"   {key}: {value}")
            
            return True
        else:
            print("❌ Insufficient data for comparison")
            return False
            
    except Exception as e:
        print(f"❌ Benchmark comparison error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing BeWiser Real Nifty 50 Integration")
    print("=" * 60)
    
    success1 = test_real_nifty_data()
    success2 = test_benchmark_comparison()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Real Nifty 50 data is working.")
    else:
        print("\n⚠️  Some tests failed. Check the implementation.")
    
    print("=" * 60)
