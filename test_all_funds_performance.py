#!/usr/bin/env python3
"""
Quick test to see how long it takes to analyze all funds
"""
import sys
import time

sys.path.insert(0, '/Users/ayaan/development/bewiser')

def time_analysis():
    print("⏱️  Testing analysis time for all small cap funds...")
    
    start_time = time.time()
    
    try:
        from app.services.fund_analysis_service import analyze_funds
        results = analyze_funds()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Analysis completed!")
        print(f"   📊 Analyzed {len(results)} funds")
        print(f"   ⏱️  Time taken: {duration:.2f} seconds")
        print(f"   🏆 Top 5 funds by Sharpe ratio:")
        
        for i, fund in enumerate(results[:5], 1):
            print(f"   {i}. {fund['fund_name'][:50]}... (Sharpe: {fund['sharpe_ratio']})")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    time_analysis()
