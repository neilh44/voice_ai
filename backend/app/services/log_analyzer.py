import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

class LogAnalyzer:
    """
    Utility for analyzing log files
    """
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
    
    def parse_log_file(self, component="app", days=1):
        """
        Parse a log file into a list of records
        """
        log_file = self.log_dir / f"{component}.log"
        
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        # Get the start date
        start_date = datetime.now() - timedelta(days=days)
        
        records = []
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    # Parse JSON log record
                    record = json.loads(line.strip())
                    
                    # Parse timestamp
                    timestamp = datetime.fromisoformat(record['timestamp'])
                    
                    # Filter by date
                    if timestamp >= start_date:
                        records.append(record)
                except json.JSONDecodeError:
                    # Skip lines that are not valid JSON
                    continue
                except KeyError:
                    # Skip records without required fields
                    continue
        
        return records
    
    def get_error_summary(self, component="app", days=1):
        """
        Get a summary of errors from the log
        """
        records = self.parse_log_file(component, days)
        
        # Filter error records
        error_records = [r for r in records if r['level'] in ('ERROR', 'CRITICAL')]
        
        # Group by error message
        error_messages = [r['message'] for r in error_records]
        error_counts = Counter(error_messages)
        
        return {
            'total_errors': len(error_records),
            'unique_errors': len(error_counts),
            'top_errors': error_counts.most_common(10)
        }
    
    def get_performance_metrics(self, component="app", days=1):
        """
        Get performance metrics from the log
        """
        records = self.parse_log_file(component, days)
        
        # Filter records with execution time
        perf_records = [r for r in records if 'execution_time' in r]
        
        # Extract function and execution time
        functions = {}
        
        for record in perf_records:
            func_name = f"{record.get('module', 'unknown')}.{record.get('function', 'unknown')}"
            execution_time = record.get('execution_time', 0)
            
            if func_name not in functions:
                functions[func_name] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            functions[func_name]['count'] += 1
            functions[func_name]['total_time'] += execution_time
            functions[func_name]['min_time'] = min(functions[func_name]['min_time'], execution_time)
            functions[func_name]['max_time'] = max(functions[func_name]['max_time'], execution_time)
        
        # Calculate average execution time
        for func_name, stats in functions.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
        
        # Sort by total execution time
        sorted_functions = sorted(
            functions.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        
        return {
            'total_functions': len(functions),
            'total_calls': sum(f['count'] for f in functions.values()),
            'top_functions': sorted_functions[:10]
        }
    
    def analyze_call_logs(self, days=1):
        """
        Analyze call logs for statistics
        """
        records = self.parse_log_file("twilio", days)
        
        # Filter records with call_sid
        call_records = [r for r in records if 'call_sid' in r]
        
        # Group by call_sid
        calls = {}
        
        for record in call_records:
            call_sid = record['call_sid']
            
            if call_sid not in calls:
                calls[call_sid] = {
                    'messages': [],
                    'start_time': None,
                    'end_time': None,
                    'error': False
                }
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(record['timestamp'])
            
            # Update start and end time
            if calls[call_sid]['start_time'] is None or timestamp < calls[call_sid]['start_time']:
                calls[call_sid]['start_time'] = timestamp
            
            if calls[call_sid]['end_time'] is None or timestamp > calls[call_sid]['end_time']:
                calls[call_sid]['end_time'] = timestamp
            
            # Check for errors
            if record['level'] in ('ERROR', 'CRITICAL'):
                calls[call_sid]['error'] = True
            
            # Add message
            calls[call_sid]['messages'].append({
                'timestamp': timestamp,
                'level': record['level'],
                'message': record['message']
            })
        
        # Calculate call duration
        for call_sid, call in calls.items():
            if call['start_time'] and call['end_time']:
                call['duration'] = (call['end_time'] - call['start_time']).total_seconds()
        
        # Summary statistics
        num_calls = len(calls)
        
