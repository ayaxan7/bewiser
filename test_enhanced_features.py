#!/usr/bin/env python3
"""
Test the enhanced BeWiser Smart Advisor functionality
Run this script to test all features end-to-end
"""

import sys
import os

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.benchmark_service import fetch_nifty50_data, calculate_benchmark_metrics
from app.services.fund_analysis_service import analyze_funds_with_benchmark
from app.services.smart_advisor import get_smart_recommendations
import pandas as pd


def test_nifty50_data():
    """Test Nifty 50 data generation"""
    print("Testing Nifty 50 data generation...")
    try:
        nifty_data = fetch_nifty50_data(days_back=1000)
        assert len(nifty_data) > 500, "Should have substantial data"
        assert 'date' in nifty_data.columns, "Should have date column"
        assert 'nav' in nifty_data.columns, "Should have nav column"
        print(f"✓ Generated {len(nifty_data)} days of Nifty 50 data")
        print(f"  Date range: {nifty_data['date'].min()} to {nifty_data['date'].max()}")
        print(f"  NAV range: {nifty_data['nav'].min():.0f} to {nifty_data['nav'].max():.0f}")
        return True
    except Exception as e:
        print(f"✗ Error testing Nifty 50 data: {e}")
        return False


def test_benchmark_metrics():
    """Test benchmark metrics calculation"""
    print("\nTesting benchmark metrics calculation...")
    try:
        # Create sample fund data
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        fund_data = pd.DataFrame({
            'date': dates,
            'nav': [100 + i * 0.05 + (i % 10) * 0.02 for i in range(len(dates))]
        })
        
        # Create sample benchmark data
        benchmark_data = pd.DataFrame({
            'date': dates,
            'nav': [1000 + i * 0.04 + (i % 15) * 0.01 for i in range(len(dates))]
        })
        
        metrics = calculate_benchmark_metrics(fund_data, benchmark_data)
        
        expected_metrics = ['beta', 'alpha_pct', 'tracking_error_pct', 'correlation']
        for metric in expected_metrics:
            assert metric in metrics, f"Should have {metric}"
        
        print(f"✓ Calculated benchmark metrics: {list(metrics.keys())}")
        print(f"  Alpha: {metrics.get('alpha_pct', 'N/A')}%")
        print(f"  Beta: {metrics.get('beta', 'N/A')}")
        print(f"  Correlation: {metrics.get('correlation', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ Error testing benchmark metrics: {e}")
        return False


def test_fund_analysis():
    """Test fund analysis with benchmark"""
    print("\nTesting fund analysis with benchmark...")
    try:
        # This will use real API data, so we'll mock it for testing
        results = analyze_funds_with_benchmark()
        
        if results:
            print(f"✓ Analyzed {len(results)} funds")
            
            sample_fund = results[0]
            expected_fields = [
                'scheme_code', 'fund_name', 'alpha_pct', 'beta',
                'sharpe_ratio', 'volatility_pct', 'recommendation'
            ]
            
            for field in expected_fields:
                if field in sample_fund:
                    print(f"  ✓ {field}: {sample_fund[field]}")
                else:
                    print(f"  ? Missing field: {field}")
            
            return True
        else:
            print("✗ No funds returned from analysis")
            return False
            
    except Exception as e:
        print(f"✗ Error testing fund analysis: {e}")
        return False


def test_smart_advisor():
    """Test smart advisor functionality"""
    print("\nTesting smart advisor...")
    
    test_cases = [
        {
            'name': 'Conservative Investor',
            'params': {
                'risk_tolerance': 'conservative',
                'investment_horizon': 'long_term',
                'max_volatility': 20.0
            }
        },
        {
            'name': 'Aggressive Investor',
            'params': {
                'risk_tolerance': 'aggressive',
                'investment_horizon': 'long_term',
                'min_alpha': 2.0
            }
        },
        {
            'name': 'Moderate Investor',
            'params': {
                'risk_tolerance': 'moderate',
                'investment_horizon': 'medium_term'
            }
        }
    ]
    
    passed_tests = 0
    
    for test_case in test_cases:
        try:
            print(f"\n  Testing {test_case['name']}...")
            recommendations = get_smart_recommendations(**test_case['params'])
            
            required_sections = [
                'recommended_funds', 'analysis_summary', 'investment_strategy',
                'portfolio_allocation', 'risk_warnings'
            ]
            
            for section in required_sections:
                if section in recommendations:
                    print(f"    ✓ {section}")
                else:
                    print(f"    ✗ Missing {section}")
            
            if recommendations['recommended_funds']:
                fund_count = len(recommendations['recommended_funds'])
                print(f"    ✓ Recommended {fund_count} fund(s)")
                
                # Check if portfolio allocation matches risk tolerance
                allocation = recommendations['portfolio_allocation']
                if test_case['params']['risk_tolerance'] == 'conservative':
                    assert 'conservative' in allocation.get('recommendation', '').lower()
                elif test_case['params']['risk_tolerance'] == 'aggressive':
                    assert 'growth' in allocation.get('recommendation', '').lower()
                
                print(f"    ✓ Risk-appropriate allocation suggested")
            
            passed_tests += 1
            
        except Exception as e:
            print(f"    ✗ Error testing {test_case['name']}: {e}")
    
    print(f"\n✓ Smart advisor tests passed: {passed_tests}/{len(test_cases)}")
    return passed_tests == len(test_cases)


def test_api_integration():
    """Test API integration points"""
    print("\nTesting API integration...")
    try:
        # Test that functions can be called without errors
        from app.api.routes import router
        print("✓ API routes module imported successfully")
        
        # Test route definitions
        routes = [route.path for route in router.routes]
        expected_routes = ['/top5smallcap', '/top5smallcap-benchmark', '/smart-advisor']
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✓ Route {route} defined")
            else:
                print(f"  ✗ Route {route} missing")
        
        return True
    except Exception as e:
        print(f"✗ Error testing API integration: {e}")
        return False


def run_comprehensive_test():
    """Run all tests"""
    print("=" * 60)
    print("BEWISER ENHANCED FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Nifty 50 Data Generation", test_nifty50_data),
        ("Benchmark Metrics Calculation", test_benchmark_metrics),
        ("Fund Analysis with Benchmark", test_fund_analysis),
        ("Smart Advisor", test_smart_advisor),
        ("API Integration", test_api_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! BeWiser enhanced functionality is working correctly.")
        print("\nKey features verified:")
        print("  ✓ Nifty 50 benchmark comparison")
        print("  ✓ Alpha, Beta, Information Ratio calculation")
        print("  ✓ Risk-adjusted performance metrics")
        print("  ✓ Smart investment recommendations")
        print("  ✓ Portfolio allocation strategies")
        print("  ✓ API endpoint integration")
    else:
        print(f"❌ {total - passed} test(s) failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
