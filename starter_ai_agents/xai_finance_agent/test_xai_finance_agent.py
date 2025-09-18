#!/usr/bin/env python3
"""
Comprehensive Test Suite for xAI Finance Agent
Tests CSV upload functionality, data processing, and financial analysis
"""

import pytest
import pandas as pd
import os
import sys
import json
import asyncio
from io import StringIO
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the current directory to the path to import the modules
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ai_financial_coach_agent import (
        FinanceAdvisorSystem,
        parse_csv_transactions,
        validate_csv_format,
        parse_json_safely,
        _run_asyncio
    )
except ImportError as e:
    print(f"Warning: Could not import all modules: {e}")
    print("Some tests may be skipped")

class TestCSVUploadFunctionality:
    """Test CSV upload and parsing functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_csv_path = "test_family_expenses.csv"
        self.sample_csv_content = """Date,Category,Amount,Description
2024-01-01,Housing,1450.00,Monthly Rent
2024-01-02,Food,89.45,Grocery Shopping
2024-01-03,Transportation,48.75,Gas Station
2024-01-04,Healthcare,125.00,Doctor Visit
2024-01-05,Entertainment,45.99,Movie Night"""
    
    def test_csv_file_exists(self):
        """Test that the test CSV file exists"""
        assert os.path.exists(self.test_csv_path), f"Test CSV file {self.test_csv_path} not found"
    
    def test_csv_file_format(self):
        """Test that the CSV file has the correct format"""
        df = pd.read_csv(self.test_csv_path)
        
        # Check required columns exist
        required_columns = ['Date', 'Category', 'Amount']
        for col in required_columns:
            assert col in df.columns, f"Required column '{col}' not found in CSV"
        
        # Check data types can be converted
        assert len(df) > 0, "CSV file is empty"
        
        # Check dates can be parsed
        try:
            pd.to_datetime(df['Date'])
        except Exception as e:
            pytest.fail(f"Date column contains invalid dates: {e}")
        
        # Check amounts are numeric
        try:
            pd.to_numeric(df['Amount'])
        except Exception as e:
            pytest.fail(f"Amount column contains non-numeric values: {e}")
    
    @pytest.mark.skipif('parse_csv_transactions' not in globals(), 
                       reason="parse_csv_transactions function not available")
    def test_parse_csv_transactions(self):
        """Test CSV parsing functionality"""
        csv_content = self.sample_csv_content.encode('utf-8')
        
        try:
            result = parse_csv_transactions(csv_content)
            
            # Check return structure
            assert 'transactions' in result
            assert 'category_totals' in result
            assert isinstance(result['transactions'], list)
            assert isinstance(result['category_totals'], list)
            
            # Check data integrity
            assert len(result['transactions']) == 5  # 5 sample transactions
            assert len(result['category_totals']) == 5  # 5 different categories
            
            # Verify transaction structure
            transaction = result['transactions'][0]
            assert 'Date' in transaction
            assert 'Category' in transaction
            assert 'Amount' in transaction
            
        except Exception as e:
            pytest.fail(f"CSV parsing failed: {e}")
    
    @pytest.mark.skipif('validate_csv_format' not in globals(), 
                       reason="validate_csv_format function not available")
    def test_validate_csv_format_valid(self):
        """Test CSV validation with valid data"""
        # Create a mock file object
        mock_file = MagicMock()
        mock_file.read.return_value = self.sample_csv_content.encode('utf-8')
        mock_file.seek.return_value = None
        
        try:
            is_valid, message = validate_csv_format(mock_file)
            assert is_valid, f"Valid CSV failed validation: {message}"
            assert "valid" in message.lower()
        except Exception as e:
            pytest.fail(f"CSV validation failed: {e}")
    
    @pytest.mark.skipif('validate_csv_format' not in globals(), 
                       reason="validate_csv_format function not available")
    def test_validate_csv_format_invalid(self):
        """Test CSV validation with invalid data"""
        invalid_csv = """Invalid,Headers
1,2,3"""
        
        mock_file = MagicMock()
        mock_file.read.return_value = invalid_csv.encode('utf-8')
        mock_file.seek.return_value = None
        
        try:
            is_valid, message = validate_csv_format(mock_file)
            assert not is_valid, "Invalid CSV passed validation"
            assert "missing" in message.lower() or "invalid" in message.lower()
        except Exception as e:
            pytest.fail(f"CSV validation error handling failed: {e}")

class TestDataProcessing:
    """Test data processing and analysis functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.sample_financial_data = {
            "monthly_income": 5000.0,
            "dependants": 2,
            "manual_expenses": {
                "Housing": 1450.0,
                "Food": 600.0,
                "Transportation": 300.0,
                "Healthcare": 200.0,
                "Entertainment": 150.0,
                "Personal": 100.0,
                "Utilities": 250.0
            },
            "debts": [
                {"name": "Credit Card", "amount": 3000.0, "interest_rate": 18.5, "min_payment": 120.0},
                {"name": "Car Loan", "amount": 15000.0, "interest_rate": 6.5, "min_payment": 350.0}
            ]
        }
    
    def test_sample_data_structure(self):
        """Test that sample data has correct structure"""
        assert "monthly_income" in self.sample_financial_data
        assert "dependants" in self.sample_financial_data
        assert "manual_expenses" in self.sample_financial_data
        assert "debts" in self.sample_financial_data
        
        # Check expenses total
        total_expenses = sum(self.sample_financial_data["manual_expenses"].values())
        assert total_expenses > 0, "Total expenses should be greater than 0"
        
        # Check debt structure
        for debt in self.sample_financial_data["debts"]:
            assert "name" in debt
            assert "amount" in debt
            assert "interest_rate" in debt
            assert "min_payment" in debt
    
    @pytest.mark.skipif('parse_json_safely' not in globals(), 
                       reason="parse_json_safely function not available")
    def test_json_parsing(self):
        """Test JSON parsing utility function"""
        # Test valid JSON
        valid_json = '{"test": "value"}'
        result = parse_json_safely(valid_json)
        assert result == {"test": "value"}
        
        # Test invalid JSON
        invalid_json = '{"test": invalid}'
        result = parse_json_safely(invalid_json, {"default": "value"})
        assert result == {"default": "value"}
        
        # Test non-string input
        dict_input = {"already": "dict"}
        result = parse_json_safely(dict_input)
        assert result == {"already": "dict"}

class TestFinanceAdvisorSystem:
    """Test the main Finance Advisor System"""
    
    def setup_method(self):
        """Setup test environment"""
        self.sample_data = {
            "monthly_income": 5000.0,
            "dependants": 2,
            "manual_expenses": {
                "Housing": 1450.0,
                "Food": 600.0,
                "Transportation": 300.0,
                "Healthcare": 200.0,
                "Entertainment": 150.0,
                "Personal": 100.0,
                "Utilities": 250.0
            },
            "debts": []
        }
    
    @pytest.mark.skipif('FinanceAdvisorSystem' not in globals(), 
                       reason="FinanceAdvisorSystem class not available")
    def test_system_initialization(self):
        """Test that the finance advisor system initializes correctly"""
        try:
            system = FinanceAdvisorSystem()
            assert system is not None
            assert hasattr(system, 'budget_analysis_agent')
            assert hasattr(system, 'savings_strategy_agent')
            assert hasattr(system, 'debt_reduction_agent')
            assert hasattr(system, 'coordinator_agent')
            assert hasattr(system, 'runner')
        except Exception as e:
            pytest.fail(f"System initialization failed: {e}")
    
    @pytest.mark.skipif('FinanceAdvisorSystem' not in globals(), 
                       reason="FinanceAdvisorSystem class not available")
    def test_default_results_creation(self):
        """Test creation of default results"""
        try:
            system = FinanceAdvisorSystem()
            default_results = system._create_default_results(self.sample_data)
            
            # Check structure
            assert "budget_analysis" in default_results
            assert "savings_strategy" in default_results
            assert "debt_reduction" in default_results
            
            # Check budget analysis
            budget_analysis = default_results["budget_analysis"]
            assert "total_expenses" in budget_analysis
            assert "spending_categories" in budget_analysis
            assert "recommendations" in budget_analysis
            
            # Check savings strategy
            savings_strategy = default_results["savings_strategy"]
            assert "emergency_fund" in savings_strategy
            assert "recommendations" in savings_strategy
            
        except Exception as e:
            pytest.fail(f"Default results creation failed: {e}")

class TestDataValidation:
    """Test data validation and error handling"""
    
    def test_csv_data_validation(self):
        """Test validation of CSV data from real file"""
        if not os.path.exists("test_family_expenses.csv"):
            pytest.skip("Test CSV file not found")
        
        df = pd.read_csv("test_family_expenses.csv")
        
        # Test data quality
        assert not df.empty, "CSV file should not be empty"
        assert len(df) >= 100, f"Expected at least 100 records, got {len(df)}"
        
        # Test for family-appropriate categories
        expected_categories = ['Housing', 'Food', 'Transportation', 'Healthcare', 
                             'Entertainment', 'Personal', 'Utilities', 'Savings']
        actual_categories = df['Category'].unique()
        
        for category in expected_categories:
            assert category in actual_categories, f"Expected category '{category}' not found"
        
        # Test amount ranges (should be reasonable for a family)
        amounts = df['Amount'].astype(float)
        assert amounts.min() > 0, "All amounts should be positive"
        assert amounts.max() < 10000, "No single expense should be unreasonably high"
        
        # Test date range
        dates = pd.to_datetime(df['Date'])
        assert (dates.max() - dates.min()).days >= 30, "Should span at least a month"
    
    def test_expense_categories_completeness(self):
        """Test that all major expense categories are represented"""
        if not os.path.exists("test_family_expenses.csv"):
            pytest.skip("Test CSV file not found")
        
        df = pd.read_csv("test_family_expenses.csv")
        category_totals = df.groupby('Category')['Amount'].sum()
        
        # Housing should be the largest expense
        assert category_totals['Housing'] > category_totals['Food'], \
            "Housing should typically be the largest expense"
        
        # Food should be a significant expense for a family of 4
        total_expenses = category_totals.sum()
        food_percentage = (category_totals['Food'] / total_expenses) * 100
        assert food_percentage >= 10, \
            f"Food should be at least 10% of expenses, got {food_percentage:.1f}%"
        
        # Should have some savings
        if 'Savings' in category_totals:
            savings_percentage = (category_totals['Savings'] / total_expenses) * 100
            assert savings_percentage >= 5, \
                f"Savings should be at least 5% of expenses, got {savings_percentage:.1f}%"

class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_csv_to_analysis_workflow(self):
        """Test the complete workflow from CSV upload to analysis"""
        if not os.path.exists("test_family_expenses.csv"):
            pytest.skip("Test CSV file not found")
        
        # Read the CSV file
        df = pd.read_csv("test_family_expenses.csv")
        
        # Convert to the expected format
        transactions = df.to_dict('records')
        
        # Create financial data structure
        financial_data = {
            "monthly_income": 6000.0,  # Reasonable income for family of 4
            "dependants": 2,  # 2 children
            "transactions": transactions,
            "manual_expenses": None,
            "debts": [
                {"name": "Mortgage", "amount": 200000.0, "interest_rate": 4.5, "min_payment": 1200.0},
                {"name": "Car Loan", "amount": 25000.0, "interest_rate": 6.0, "min_payment": 450.0}
            ]
        }
        
        # Validate the structure
        assert len(financial_data["transactions"]) >= 100
        assert financial_data["monthly_income"] > 0
        assert financial_data["dependants"] == 2
        assert len(financial_data["debts"]) > 0

def run_performance_tests():
    """Run performance tests for the system"""
    print("\n=== Performance Tests ===")
    
    if not os.path.exists("test_family_expenses.csv"):
        print("❌ Test CSV file not found - skipping performance tests")
        return
    
    # Test CSV loading performance
    start_time = datetime.now()
    df = pd.read_csv("test_family_expenses.csv")
    load_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ CSV loading time: {load_time:.3f} seconds")
    print(f"✅ Records processed: {len(df)}")
    print(f"✅ Processing rate: {len(df)/load_time:.0f} records/second")
    
    # Test data aggregation performance
    start_time = datetime.now()
    category_totals = df.groupby('Category')['Amount'].sum()
    monthly_totals = df.groupby(pd.to_datetime(df['Date']).dt.to_period('M'))['Amount'].sum()
    agg_time = (datetime.now() - start_time).total_seconds()
    
    print(f"✅ Data aggregation time: {agg_time:.3f} seconds")
    print(f"✅ Categories found: {len(category_totals)}")
    print(f"✅ Months covered: {len(monthly_totals)}")

def run_data_quality_tests():
    """Run data quality tests"""
    print("\n=== Data Quality Tests ===")
    
    if not os.path.exists("test_family_expenses.csv"):
        print("❌ Test CSV file not found - skipping data quality tests")
        return
    
    df = pd.read_csv("test_family_expenses.csv")
    
    # Basic quality checks
    print(f"✅ Total records: {len(df)}")
    print(f"✅ Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"✅ Total amount: ${df['Amount'].sum():,.2f}")
    print(f"✅ Average transaction: ${df['Amount'].mean():.2f}")
    
    # Category distribution
    category_dist = df['Category'].value_counts()
    print(f"✅ Categories: {len(category_dist)}")
    for category, count in category_dist.items():
        percentage = (count / len(df)) * 100
        total_amount = df[df['Category'] == category]['Amount'].sum()
        print(f"   - {category}: {count} transactions ({percentage:.1f}%), ${total_amount:,.2f}")
    
    # Data validation
    errors = []
    
    # Check for missing values
    if df.isnull().any().any():
        errors.append("Contains missing values")
    
    # Check for negative amounts
    if (df['Amount'] < 0).any():
        errors.append("Contains negative amounts")
    
    # Check date format
    try:
        pd.to_datetime(df['Date'])
    except:
        errors.append("Invalid date format")
    
    if errors:
        print(f"❌ Data quality issues found: {', '.join(errors)}")
    else:
        print("✅ All data quality checks passed")

def main():
    """Main test runner"""
    print("🧪 xAI Finance Agent Test Suite")
    print("=" * 50)
    
    # Check environment
    print("\n=== Environment Check ===")
    print(f"✅ Python version: {sys.version.split()[0]}")
    print(f"✅ Current directory: {os.getcwd()}")
    print(f"✅ Test CSV exists: {os.path.exists('test_family_expenses.csv')}")
    
    # Check dependencies
    dependencies = ['pandas', 'streamlit', 'plotly', 'google-adk']
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Missing")
    
    # Run tests
    print("\n=== Running Tests ===")
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-x"  # Stop on first failure
    ]
    
    try:
        exit_code = pytest.main(pytest_args)
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {exit_code})")
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
    
    # Run additional tests
    run_performance_tests()
    run_data_quality_tests()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed")

if __name__ == "__main__":
    main()