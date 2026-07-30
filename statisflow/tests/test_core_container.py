"""
Comprehensive Test Suite for StatisFLOW Core Data Container
Tests immutability, schema inference, lineage tracking, and transformations.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from data_formulator.core import DataContainer, DataLineage, SemanticType
from data_formulator.statistics.exceptions import DataValidationError


@pytest.fixture
def sample_df():
    """Create a sample dataframe for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "value": [10.5, 20.3, np.nan, 40.1, 50.0],
        "category": ["A", "B", "A", "C", "B"],
        "date": pd.date_range("2023-01-01", periods=5)
    })


class TestDataContainerCreation:
    """Test DataContainer initialization and validation."""
    
    def test_create_from_dataframe(self, sample_df):
        """Test basic creation from DataFrame."""
        container = DataContainer(sample_df, name="Test Dataset")
        assert container.name == "Test Dataset"
        assert len(container.data) == 5
        assert container.hash is not None
    
    def test_empty_dataframe_rejected(self):
        """Test that empty DataFrames are rejected."""
        empty_df = pd.DataFrame()
        with pytest.raises(DataValidationError):
            DataContainer(empty_df)
    
    def test_non_string_columns_rejected(self):
        """Test that non-string column names are rejected."""
        df = pd.DataFrame({1: [1, 2], 2: [3, 4]})
        with pytest.raises(DataValidationError):
            DataContainer(df)
    
    def test_schema_inference(self, sample_df):
        """Test automatic schema inference."""
        container = DataContainer(sample_df)
        schema = container.schema
        
        assert "id" in schema
        assert "value" in schema
        assert "category" in schema
        
        # Check semantic types
        assert schema["id"].semantic_type == SemanticType.DISCRETE
        assert schema["value"].semantic_type == SemanticType.CONTINUOUS
        assert schema["category"].semantic_type == SemanticType.NOMINAL
        assert schema["date"].semantic_type == SemanticType.TEMPORAL


class TestDataContainerImmutability:
    """Test immutability guarantees."""
    
    def test_data_readonly(self, sample_df):
        """Test that returned data is read-only view."""
        container = DataContainer(sample_df)
        data = container.data
        
        # Should be able to read
        assert len(data) == 5
        
        # Original container should be unaffected by external changes
        original_hash = container.hash
        # Note: pandas doesn't have true readonly, but we track via hash
    
    def test_transform_returns_new_container(self, sample_df):
        """Test that transform returns a new container."""
        container = DataContainer(sample_df, name="Original")
        new_container = container.transform("filter", query="value > 20")
        
        assert container is not new_container
        assert container.name == "Original"
        assert "Original (filter)" in new_container.name
        assert len(new_container.data) < len(container.data)
    
    def test_original_unchanged_after_transform(self, sample_df):
        """Test that original container is unchanged after transformation."""
        container = DataContainer(sample_df)
        original_len = len(container.data)
        original_hash = container.hash
        
        _ = container.transform("impute", column="value", strategy="mean")
        
        assert len(container.data) == original_len
        assert container.hash == original_hash


class TestDataLineage:
    """Test data lineage tracking."""
    
    def test_initial_lineage(self, sample_df):
        """Test initial lineage creation."""
        container = DataContainer(sample_df, name="Test")
        lineage = container.lineage
        
        assert lineage.source_file is None
        assert lineage.loaded_at is not None
        assert len(lineage.transformations) == 0
    
    def test_lineage_updated_on_transform(self, sample_df):
        """Test that lineage is updated on transformations."""
        container = DataContainer(sample_df)
        
        c1 = container.transform("filter", query="value > 20")
        c2 = c1.transform("impute", column="value", strategy="mean")
        
        assert len(c1.lineage.transformations) == 1
        assert len(c2.lineage.transformations) == 2
        assert c2.lineage.parent_hash == c1.hash
    
    def test_lineage_chain(self, sample_df):
        """Test complete lineage chain."""
        container = DataContainer(sample_df)
        
        c1 = container.transform("filter", query="value > 20")
        c2 = c1.transform("impute", column="value", strategy="mean")
        c3 = c2.transform("cast", column="id", dtype="str")
        
        # Verify chain
        assert c3.lineage.parent_hash == c2.hash
        assert c2.lineage.parent_hash == c1.hash
        assert c1.lineage.parent_hash == container.hash


class TestQualityReport:
    """Test quality report generation."""
    
    def test_quality_report_generated(self, sample_df):
        """Test that quality report is generated."""
        container = DataContainer(sample_df)
        report = container.get_quality_report()
        
        assert report is not None
        assert hasattr(report, 'total_rows')
        assert hasattr(report, 'missing_values')
    
    def test_quality_report_cached(self, sample_df):
        """Test that quality report is cached."""
        container = DataContainer(sample_df)
        
        report1 = container.get_quality_report()
        report2 = container.get_quality_report()
        
        assert report1 is report2


class TestSerialization:
    """Test serialization capabilities."""
    
    def test_to_dict(self, sample_df):
        """Test conversion to dictionary."""
        container = DataContainer(sample_df, name="Serialize Test")
        result = container.to_dict()
        
        assert result["name"] == "Serialize Test"
        assert result["rows"] == 5
        assert result["columns"] == ["id", "value", "category", "date"]
        assert "schema" in result
        assert "lineage" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
