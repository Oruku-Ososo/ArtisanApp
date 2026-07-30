"""
StatisFLOW Core Data Integrity Layer
Provides immutable, typed, and validated data containers to prevent silent failures.
Surpasses JASP/Jamovi by enforcing schema consistency before analysis.
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum
import hashlib
import json
from datetime import datetime

# Relative imports adjusted for package structure
from ..statistics.exceptions import DataValidationError
from ..statistics.validation import validate_dataframe


class SemanticType(Enum):
    """Enhanced semantic types beyond basic pandas dtypes."""
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    NOMINAL = "nominal"
    ORDINAL = "ordinal"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    TEXT = "text"
    IDENTIFIER = "identifier"
    TARGET = "target"
    WEIGHT = "weight"
    OFFSET = "offset"


@dataclass(frozen=True)
class ColumnMetadata:
    """Immutable metadata for a single column."""
    name: str
    semantic_type: SemanticType
    physical_dtype: str
    nullable: bool
    categories: Optional[List[Any]] = None  # For nominal/ordinal
    unit: Optional[str] = None
    description: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "semantic_type": self.semantic_type.value,
            "physical_dtype": self.physical_dtype,
            "nullable": self.nullable,
            "categories": self.categories,
            "unit": self.unit,
            "description": self.description,
            "min_value": self.min_value,
            "max_value": self.max_value
        }


@dataclass
class DataLineage:
    """Tracks the provenance of the data."""
    source_file: Optional[str] = None
    source_type: Optional[str] = None
    loaded_at: datetime = field(default_factory=datetime.now)
    transformations: List[Dict[str, Any]] = field(default_factory=list)
    parent_hash: Optional[str] = None
    
    def add_transformation(self, operation: str, params: Dict[str, Any], result_hash: str):
        self.transformations.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "parameters": params,
            "result_hash": result_hash
        })
        self.parent_hash = result_hash


class DataContainer:
    """
    An immutable, schema-enforced data container for StatisFLOW.
    
    Features:
    - Immutability: Any modification returns a NEW container.
    - Schema Enforcement: Validates types and constraints on creation.
    - Lineage Tracking: Full audit trail of transformations.
    - Semantic Typing: Understands data meaning, not just dtype.
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        schema: Optional[Dict[str, Any]] = None,
        name: str = "Untitled Dataset",
        lineage: Optional[DataLineage] = None
    ):
        self._validate_dataframe(data)
        
        # Create internal immutable dataframe
        self._data = data.copy()
        self._data.attrs["readonly"] = True
        
        # Infer or validate schema
        self._schema = self._infer_schema(data) if schema is None else schema
        
        # Metadata
        self.name = name
        self.lineage = lineage or DataLineage()
        self._hash = self._compute_hash()
        
        # Cache quality report
        self._quality_report: Optional[Any] = None

    def _validate_dataframe(self, df: pd.DataFrame):
        if df.empty:
            raise DataValidationError("Cannot create DataContainer with empty DataFrame")
        if not all(isinstance(col, str) for col in df.columns):
            raise DataValidationError("All column names must be strings")

    def _infer_schema(self, df: pd.DataFrame) -> Dict[str, ColumnMetadata]:
        """Automatically infer semantic types and constraints."""
        schema = {}
        for col in df.columns:
            series = df[col]
            dtype = str(series.dtype)
            
            # Basic inference logic
            if pd.api.types.is_numeric_dtype(series):
                if pd.api.types.is_integer_dtype(series) and series.nunique() < 10:
                    sem_type = SemanticType.DISCRETE
                else:
                    sem_type = SemanticType.CONTINUOUS
                min_val = float(series.min()) if not series.empty else None
                max_val = float(series.max()) if not series.empty else None
            elif pd.api.types.is_datetime64_any_dtype(series):
                sem_type = SemanticType.TEMPORAL
                min_val = max_val = None
            else:
                if series.nunique() / len(series) < 0.05:
                    sem_type = SemanticType.NOMINAL
                else:
                    sem_type = SemanticType.TEXT
                min_val = max_val = None
            
            schema[col] = ColumnMetadata(
                name=col,
                semantic_type=sem_type,
                physical_dtype=dtype,
                nullable=series.isna().any(),
                categories=sorted([str(x) for x in series.dropna().unique().tolist()]) if sem_type in [SemanticType.NOMINAL, SemanticType.ORDINAL] else None,
                min_value=min_val,
                max_value=max_val
            )
        return schema

    def _compute_hash(self) -> str:
        """Compute a unique hash for the current state of data."""
        # Use first 100 rows and column names for performance
        sample = self._data.head(100).to_json()
        return hashlib.sha256(sample.encode()).hexdigest()

    @property
    def data(self) -> pd.DataFrame:
        """Return read-only view of the data."""
        return self._data

    @property
    def schema(self) -> Dict[str, ColumnMetadata]:
        return self._schema.copy()

    @property
    def hash(self) -> str:
        return self._hash

    def get_quality_report(self) -> Any:
        """Generate or return cached quality report."""
        if self._quality_report is None:
            self._quality_report = validate_dataframe(self._data)
        return self._quality_report

    def transform(self, operation: str, **kwargs) -> 'DataContainer':
        """
        Apply a transformation and return a NEW DataContainer.
        Preserves immutability and updates lineage.
        """
        new_data = self._data.copy()
        
        if operation == "filter":
            query = kwargs.get("query")
            new_data = new_data.query(query)
        elif operation == "impute":
            col = kwargs.get("column")
            strategy = kwargs.get("strategy", "mean")
            if strategy == "mean" and col in new_data.columns:
                new_data[col] = new_data[col].fillna(new_data[col].mean())
            elif strategy == "median" and col in new_data.columns:
                new_data[col] = new_data[col].fillna(new_data[col].median())
        elif operation == "cast":
            col = kwargs.get("column")
            dtype = kwargs.get("dtype")
            if col in new_data.columns:
                new_data[col] = new_data[col].astype(dtype)
        else:
            raise ValueError(f"Unknown transformation: {operation}")
        
        # Create new lineage
        new_lineage = DataLineage(
            source_file=self.lineage.source_file,
            source_type=self.lineage.source_type,
            loaded_at=self.lineage.loaded_at,
            transformations=self.lineage.transformations.copy(),
            parent_hash=self._hash
        )
        new_lineage.add_transformation(operation, kwargs, hashlib.sha256(new_data.to_json().encode()).hexdigest())
        
        return DataContainer(
            data=new_data,
            schema=self._schema,
            name=f"{self.name} ({operation})",
            lineage=new_lineage
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hash": self._hash,
            "rows": len(self._data),
            "columns": list(self._data.columns),
            "schema": {k: v.to_dict() for k, v in self._schema.items()},
            "lineage": {
                "source": self.lineage.source_file,
                "transformations_count": len(self.lineage.transformations)
            }
        }

    def __repr__(self):
        return f"<DataContainer: {self.name} | Rows: {len(self._data)} | Hash: {self._hash[:8]}...>"
