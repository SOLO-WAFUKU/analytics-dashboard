"""Simple data processor without pandas dependency."""

import csv
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from loguru import logger


class SimpleDataFrame:
    """Simple DataFrame-like class without pandas."""
    
    def __init__(self, data: List[Dict] = None):
        self.data = data or []
        self.columns = []
        if self.data:
            self.columns = list(self.data[0].keys())
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, key):
        if isinstance(key, str):
            return [row.get(key) for row in self.data]
        return self.data[key]
    
    def mean(self, column: str) -> float:
        """Calculate mean of a column."""
        values = [float(row.get(column, 0)) for row in self.data]
        return sum(values) / len(values) if values else 0
    
    def sum(self, column: str) -> float:
        """Calculate sum of a column."""
        return sum(float(row.get(column, 0)) for row in self.data)
    
    def max(self, column: str) -> float:
        """Get max value of a column."""
        values = [float(row.get(column, 0)) for row in self.data]
        return max(values) if values else 0
    
    def min(self, column: str) -> float:
        """Get min value of a column."""
        values = [float(row.get(column, 0)) for row in self.data]
        return min(values) if values else 0
    
    def to_csv(self, filepath: str):
        """Save to CSV file."""
        if not self.data:
            return
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(self.data)
    
    @classmethod
    def from_csv(cls, filepath: str):
        """Load from CSV file."""
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                # Convert numeric fields
                for row in data:
                    for key, value in row.items():
                        try:
                            if '.' in value:
                                row[key] = float(value)
                            else:
                                row[key] = int(value)
                        except (ValueError, AttributeError):
                            pass  # Keep as string
        except FileNotFoundError:
            logger.warning(f"File not found: {filepath}")
        
        return cls(data)
    
    def merge(self, other, on: str):
        """Simple left join implementation."""
        merged_data = []
        other_dict = {row[on]: row for row in other.data}
        
        for row in self.data:
            new_row = row.copy()
            key_value = row.get(on)
            if key_value in other_dict:
                new_row.update(other_dict[key_value])
            merged_data.append(new_row)
        
        return SimpleDataFrame(merged_data)
    
    def to_dict(self, orient='records'):
        """Convert to dictionary."""
        if orient == 'records':
            return self.data
        elif orient == 'list':
            return {col: self[col] for col in self.columns}
        return self.data


def create_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Create a list of dates between start and end."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates