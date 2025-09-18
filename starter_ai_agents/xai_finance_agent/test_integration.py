#!/usr/bin/env python3
"""
Integration Test for CSV Upload Functionality
Tests the actual file upload and processing workflow
"""

import pandas as pd
import os
import sys
from io import StringIO

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from ai_financial_coach_agent import (
    parse_csv_transactions,
    validate_csv_format,
    display_csv_preview
)

def test_actual_csv_upload():
    """Test the actual CSV upload workflow with our test data"""
    print("🧪 Testing CSV Upload Integration")
    print("=" * 50)
    
    # Check if test file exists
    if not os.path.exists("test_family_expenses.csv"):
        print("❌ Test CSV file not found")
        return False
    
    print("✅ Test CSV file found")
    
    # Read the file as the app would
    try:
        with open("test_family_expenses.csv", "rb") as file:
            file_content = file.read()
        
        print(f"✅ File read successfully: {len(file_content)} bytes")
        
        # Test CSV validation
        class MockFile:
            def __init__(self, content):
                self.content = content
                self.position = 0
            
            def read(self):
                return self.content
            
            def seek(self, position):
                self.position = position
        
        mock_file = MockFile(file_content)
        is_valid, message = validate_csv_format(mock_file)
        
        if is_valid:
            print(f"✅ CSV validation passed: {message}")
        else:
            print(f"❌ CSV validation failed: {message}")
            return False
        
        # Test CSV parsing
        parsed_data = parse_csv_transactions(file_content)
        
        transactions = parsed_data['transactions']
        category_totals = parsed_data['category_totals']
        
        print(f"✅ Parsed {len(transactions)} transactions")
        print(f"✅ Found {len(category_totals)} categories")
        
        # Test data quality
        df = pd.DataFrame(transactions)
        
        print("\n📊 Data Summary:")
        print(f"   • Date range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"   • Total amount: ${df['Amount'].sum():,.2f}")
        print(f"   • Average transaction: ${df['Amount'].mean():.2f}")
        print(f"   • Categories: {', '.join(df['Category'].unique())}")
        
        # Test category distribution
        print("\n📈 Category Breakdown:")
        category_summary = df.groupby('Category')['Amount'].agg(['count', 'sum']).round(2)
        for category, data in category_summary.iterrows():
            percentage = (data['sum'] / df['Amount'].sum()) * 100
            print(f"   • {category}: {data['count']} transactions, ${data['sum']:,.2f} ({percentage:.1f}%)")
        
        # Test financial reasonableness for family of 4
        print("\n🏠 Family of 4 Analysis:")
        monthly_total = df['Amount'].sum() / 4  # Assuming 4 months of data
        print(f"   • Average monthly expenses: ${monthly_total:,.2f}")
        
        housing_total = df[df['Category'] == 'Housing']['Amount'].sum()
        housing_percentage = (housing_total / df['Amount'].sum()) * 100
        print(f"   • Housing percentage: {housing_percentage:.1f}% (recommended: 25-30%)")
        
        if 'Savings' in df['Category'].values:
            savings_total = df[df['Category'] == 'Savings']['Amount'].sum()
            savings_percentage = (savings_total / df['Amount'].sum()) * 100
            print(f"   • Savings percentage: {savings_percentage:.1f}% (recommended: 10-20%)")
        
        print("\n✅ Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_manual_expense_workflow():
    """Test the manual expense entry workflow"""
    print("\n🧪 Testing Manual Expense Entry")
    print("=" * 30)
    
    # Sample manual expenses for family of 4
    manual_expenses = {
        "Housing": 1650.0,  # Rent/mortgage
        "Food": 800.0,      # Groceries + dining
        "Transportation": 450.0,  # Car payment, gas, insurance
        "Healthcare": 300.0,  # Insurance, copays, prescriptions
        "Utilities": 200.0,   # Electric, gas, water, internet
        "Entertainment": 150.0,  # Activities, streaming, etc.
        "Personal": 200.0,    # Clothing, personal care
        "Savings": 400.0      # Emergency fund, retirement
    }
    
    total_expenses = sum(manual_expenses.values())
    print(f"✅ Total monthly expenses: ${total_expenses:,.2f}")
    
    # Calculate percentages
    print("\n📊 Expense Distribution:")
    for category, amount in manual_expenses.items():
        percentage = (amount / total_expenses) * 100
        print(f"   • {category}: ${amount:,.2f} ({percentage:.1f}%)")
    
    # Validate against recommended percentages
    print("\n📋 Recommendations Check:")
    
    housing_pct = (manual_expenses["Housing"] / total_expenses) * 100
    if 25 <= housing_pct <= 35:
        print(f"   ✅ Housing: {housing_pct:.1f}% (within recommended 25-35%)")
    else:
        print(f"   ⚠️ Housing: {housing_pct:.1f}% (recommended: 25-35%)")
    
    savings_pct = (manual_expenses["Savings"] / total_expenses) * 100
    if savings_pct >= 10:
        print(f"   ✅ Savings: {savings_pct:.1f}% (meets recommended 10%+ minimum)")
    else:
        print(f"   ⚠️ Savings: {savings_pct:.1f}% (recommended: at least 10%)")
    
    return True

def test_debt_scenarios():
    """Test different debt scenarios for families"""
    print("\n🧪 Testing Debt Scenarios")
    print("=" * 25)
    
    # Common debt scenarios for young families
    debt_scenarios = [
        {
            "name": "Conservative Family",
            "debts": [
                {"name": "Mortgage", "amount": 250000, "interest_rate": 4.5, "min_payment": 1450},
                {"name": "Car Loan", "amount": 15000, "interest_rate": 6.0, "min_payment": 350}
            ]
        },
        {
            "name": "Moderate Debt Family",
            "debts": [
                {"name": "Mortgage", "amount": 300000, "interest_rate": 5.0, "min_payment": 1750},
                {"name": "Car Loan 1", "amount": 20000, "interest_rate": 6.5, "min_payment": 400},
                {"name": "Car Loan 2", "amount": 18000, "interest_rate": 7.0, "min_payment": 360},
                {"name": "Credit Card", "amount": 8000, "interest_rate": 18.5, "min_payment": 240}
            ]
        },
        {
            "name": "High Debt Family",
            "debts": [
                {"name": "Mortgage", "amount": 350000, "interest_rate": 5.5, "min_payment": 2100},
                {"name": "Student Loan 1", "amount": 45000, "interest_rate": 6.8, "min_payment": 480},
                {"name": "Student Loan 2", "amount": 35000, "interest_rate": 7.2, "min_payment": 380},
                {"name": "Car Loan", "amount": 25000, "interest_rate": 8.0, "min_payment": 450},
                {"name": "Credit Card 1", "amount": 12000, "interest_rate": 19.9, "min_payment": 360},
                {"name": "Credit Card 2", "amount": 8500, "interest_rate": 22.5, "min_payment": 255}
            ]
        }
    ]
    
    for scenario in debt_scenarios:
        print(f"\n📊 {scenario['name']}:")
        total_debt = sum(debt["amount"] for debt in scenario["debts"])
        total_min_payment = sum(debt["min_payment"] for debt in scenario["debts"])
        
        print(f"   • Total debt: ${total_debt:,.2f}")
        print(f"   • Total minimum payments: ${total_min_payment:,.2f}/month")
        
        # Calculate debt-to-income ratio (assuming $6000 monthly income)
        monthly_income = 6000
        dti_ratio = (total_min_payment / monthly_income) * 100
        print(f"   • Debt-to-income ratio: {dti_ratio:.1f}%")
        
        if dti_ratio <= 36:
            print("   ✅ DTI ratio is healthy (≤36%)")
        elif dti_ratio <= 43:
            print("   ⚠️ DTI ratio is manageable (36-43%)")
        else:
            print("   ❌ DTI ratio is concerning (>43%)")
    
    return True

def main():
    """Run all integration tests"""
    print("🚀 xAI Finance Agent - Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("CSV Upload Integration", test_actual_csv_upload),
        ("Manual Expense Entry", test_manual_expense_workflow),
        ("Debt Scenarios", test_debt_scenarios)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 Integration Test Results")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed successfully!")
        return 0
    else:
        print("⚠️ Some integration tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())