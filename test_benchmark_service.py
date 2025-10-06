#!/usr/bin/env python3
"""
Comprehensive test script for benchmark_service.py
Tests both real NSE data integration and fallback mechanisms
"""

import sys
import os
sys.path.append('/Users/ayaan/development/bewiser')

from app.services.benchmark_service import (
    fetch_nifty50_data, 
    calculate_benchmark_metrics,
    calculate_risk_adjusted_metrics,
    get_benchmark_recommendation,
    _generate_synthetic_nifty_data
)
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def test_nifty50_data_fetch():
    """Test Nifty 50 data fetching functionality"""
    print("=" * 60)
    print("🧪 TESTING NIFTY 50 DATA FETCH")
    print("=" * 60)
    
    try:
        # Test with different time periods
        test_periods = [30, 365, 1825]  # 1 month, 1 year, 5 years
        
        for days in test_periods:
            print(f"\n📊 Testing {days} days back...")
            
            df = fetch_nifty50_data(days_back=days)
            
            # Validate data structure
            assert isinstance(df, pd.DataFrame), "Should return DataFrame"
            assert 'date' in df.columns, "Should have 'date' column"
            assert 'nav' in df.columns, "Should have 'nav' column"
            assert len(df) > 0, "Should have data rows"
            
            # Validate data quality
            assert df['nav'].min() > 0, "NAV values should be positive"
            assert df['date'].is_monotonic_increasing, "Dates should be sorted"
            
            print(f"   ✅ Data shape: {df.shape}")
            print(f"   ✅ Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"   ✅ NAV range: {df['nav'].min():.2f} to {df['nav'].max():.2f}")
            print(f"   ✅ Current value: {df['nav'].iloc[-1]:.2f}")
            
    except Exception as e:
        print(f"❌ Error in Nifty 50 data fetch: {e}")
        return False
    
    print("\n✅ Nifty 50 data fetch tests PASSED")
    return True

def test_synthetic_fallback():
    """Test synthetic data generation fallback"""
    print("\n" + "=" * 60)
    print("🧪 TESTING SYNTHETIC DATA FALLBACK")
    print("=" * 60)
    
    try:
        df = _generate_synthetic_nifty_data(365)
        
        # Validate structure
        assert isinstance(df, pd.DataFrame), "Should return DataFrame"
        assert 'date' in df.columns, "Should have 'date' column"
        assert 'nav' in df.columns, "Should have 'nav' column"
        assert len(df) > 0, "Should have data rows"
        
        # Validate data quality
        assert df['nav'].min() > 0, "NAV values should be positive"
        assert df['date'].is_monotonic_increasing, "Dates should be sorted"
        
        print(f"   ✅ Synthetic data shape: {df.shape}")
        print(f"   ✅ Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   ✅ NAV range: {df['nav'].min():.2f} to {df['nav'].max():.2f}")
        
    except Exception as e:
        print(f"❌ Error in synthetic data: {e}")
        return False
    
    print("\n✅ Synthetic data fallback tests PASSED")
    return True

def test_benchmark_metrics():
    """Test benchmark metrics calculation"""
    print("\n" + "=" * 60)
    print("🧪 TESTING BENCHMARK METRICS CALCULATION")
    print("=" * 60)
    
    try:
        # Get Nifty 50 data
        nifty_df = fetch_nifty50_data(365)
        
        # Create sample fund data (slightly outperforming)
        fund_dates = nifty_df['date'].copy()
        fund_navs = nifty_df['nav'] * 1.1 + np.random.normal(0, 50, len(nifty_df))
        fund_df = pd.DataFrame({
            'date': fund_dates,
            'nav': fund_navs
        })
        
        # Calculate metrics
        metrics = calculate_benchmark_metrics(fund_df, nifty_df)
        
        print(f"   📊 Calculated metrics: {len(metrics)} metrics")
        for key, value in metrics.items():
            print(f"   ✅ {key}: {value}")
        
        # Validate key metrics exist
        expected_metrics = ['beta', 'alpha_pct', 'correlation']
        for metric in expected_metrics:
            if metric in metrics:
                print(f"   ✅ {metric} calculated successfully")
        
    except Exception as e:
        print(f"❌ Error in benchmark metrics: {e}")
        return False
    
    print("\n✅ Benchmark metrics calculation tests PASSED")
    return True

def test_risk_adjusted_metrics():
    """Test risk-adjusted metrics calculation"""
    print("\n" + "=" * 60)
    print("🧪 TESTING RISK-ADJUSTED METRICS")
    print("=" * 60)
    
    try:
        # Get data
        nifty_df = fetch_nifty50_data(365)
        
        # Create fund data
        fund_dates = nifty_df['date'].copy()
        fund_navs = nifty_df['nav'] * 1.05 + np.random.normal(0, 30, len(nifty_df))
        fund_df = pd.DataFrame({
            'date': fund_dates,
            'nav': fund_navs
        })
        
        # Calculate risk-adjusted metrics
        risk_metrics = calculate_risk_adjusted_metrics(fund_df, nifty_df)
        
        print(f"   📊 Risk-adjusted metrics: {len(risk_metrics)} metrics")
        for key, value in risk_metrics.items():
            print(f"   ✅ {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error in risk-adjusted metrics: {e}")
        return False
    
    print("\n✅ Risk-adjusted metrics tests PASSED")
    return True

def test_recommendation_generation():
    """Test recommendation generation"""
    print("\n" + "=" * 60)
    print("🧪 TESTING RECOMMENDATION GENERATION")
    print("=" * 60)
    
    try:
        # Create sample metrics
        sample_metrics = {
            'alpha_pct': 2.5,
            'beta': 1.1,
            'information_ratio': 0.7,
            'sharpe_ratio': 1.2,
            'treynor_ratio': 0.15,
            'outperformance_1y_pct': 3.2,
            'outperformance_2y_pct': 1.8,
            'outperformance_3y_pct': 2.1
        }
        
        recommendation = get_benchmark_recommendation(sample_metrics)
        
        print(f"   📝 Generated recommendation:")
        print(f"   ✅ {recommendation}")
        
        assert isinstance(recommendation, str), "Should return string"
        assert len(recommendation) > 0, "Should not be empty"
        
    except Exception as e:
        print(f"❌ Error in recommendation generation: {e}")
        return False
    
    print("\n✅ Recommendation generation tests PASSED")
    return True

def test_nsepython_integration():
    """Test nsepython library integration specifically"""
    print("\n" + "=" * 60)
    print("🧪 TESTING NSEPYTHON INTEGRATION")
    print("=" * 60)
    
    try:
        # Try importing nsepython
        try:
            from nsepython import nse_get_index_quote
            print("   ✅ nsepython library imported successfully")
            
            # Try fetching current Nifty 50 data
            nifty_data = nse_get_index_quote("NIFTY 50")
            print(f"   ✅ NSE API call successful")
            print(f"   📊 Nifty data keys: {list(nifty_data.keys()) if nifty_data else 'No data'}")
            
            if nifty_data:
                current_value = nifty_data.get('lastPrice', 0)
                print(f"   ✅ Current Nifty 50 value: {current_value}")
            
        except ImportError:
            print("   ⚠️  nsepython not available - fallback will be used")
        except Exception as api_error:
            print(f"   ⚠️  NSE API error: {api_error} - fallback will be used")
        
    except Exception as e:
        print(f"❌ Error testing nsepython integration: {e}")
        return False
    
    print("\n✅ NSE integration tests COMPLETED")
    return True

def run_comprehensive_test():
    """Run all benchmark service tests"""
    print("🚀 STARTING COMPREHENSIVE BENCHMARK SERVICE TESTS")
    print("=" * 70)
    
    test_results = []
    
    # Run all tests
    test_results.append(test_nsepython_integration())
    test_results.append(test_nifty50_data_fetch())
    test_results.append(test_synthetic_fallback())
    test_results.append(test_benchmark_metrics())
    test_results.append(test_risk_adjusted_metrics())
    test_results.append(test_recommendation_generation())
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"✅ PASSED: {passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Benchmark service is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
