"""
VALCORE1 Performance Profiler
Track latency and performance metrics across the system
"""

import time
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from contextlib import contextmanager

try:
    import psutil
    import pynvml
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logging.warning("psutil or pynvml not available - monitoring limited")

logger = logging.getLogger(__name__)


class PerformanceProfiler:
    """Track and log performance metrics"""

    def __init__(self, log_file: str = "logs/performance.csv"):
        """
        Initialize performance profiler

        Args:
            log_file: Path to CSV log file
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Current measurements
        self.current_measurements = {}

        # Initialize CSV file if it doesn't exist
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'task', 'latency_ms', 'gpu0_util_%', 'gpu1_util_%', 'ram_mb'
                ])

        # Initialize GPU monitoring
        if MONITORING_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_monitoring = True
            except:
                self.gpu_monitoring = False
        else:
            self.gpu_monitoring = False

        logger.info(f"Performance profiler initialized (log: {log_file})")

    @contextmanager
    def measure(self, task_name: str):
        """
        Context manager for measuring task performance

        Usage:
            with profiler.measure("voice_to_text"):
                # code to measure
                pass

        Args:
            task_name: Name of task being measured
        """
        start_time = time.time()
        start_metrics = self._get_system_metrics()

        try:
            yield
        finally:
            end_time = time.time()
            end_metrics = self._get_system_metrics()

            latency_ms = (end_time - start_time) * 1000

            # Log measurement
            self.log_measurement(
                task=task_name,
                latency_ms=latency_ms,
                gpu0_util=end_metrics.get('gpu0_util'),
                gpu1_util=end_metrics.get('gpu1_util'),
                ram_mb=end_metrics.get('ram_mb')
            )

    def _get_system_metrics(self) -> Dict:
        """
        Get current system metrics

        Returns:
            Metrics dictionary
        """
        metrics = {}

        if not MONITORING_AVAILABLE:
            return metrics

        # GPU utilization
        if self.gpu_monitoring:
            try:
                for gpu_id in [0, 1]:
                    try:
                        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                        metrics[f'gpu{gpu_id}_util'] = util.gpu
                    except:
                        pass
            except:
                pass

        # RAM usage
        try:
            mem = psutil.virtual_memory()
            metrics['ram_mb'] = mem.used / (1024 ** 2)
        except:
            pass

        return metrics

    def log_measurement(
        self,
        task: str,
        latency_ms: float,
        gpu0_util: Optional[float] = None,
        gpu1_util: Optional[float] = None,
        ram_mb: Optional[float] = None
    ):
        """
        Log a performance measurement

        Args:
            task: Task name
            latency_ms: Latency in milliseconds
            gpu0_util: GPU 0 utilization percentage
            gpu1_util: GPU 1 utilization percentage
            ram_mb: RAM usage in MB
        """
        try:
            with open(self.log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    task,
                    f"{latency_ms:.2f}",
                    f"{gpu0_util:.1f}" if gpu0_util is not None else "",
                    f"{gpu1_util:.1f}" if gpu1_util is not None else "",
                    f"{ram_mb:.1f}" if ram_mb is not None else ""
                ])

            logger.debug(f"Logged: {task} - {latency_ms:.2f}ms")

        except Exception as e:
            logger.error(f"Error logging measurement: {e}")

    def get_stats(self, task_name: Optional[str] = None, last_n: int = 100) -> Dict:
        """
        Get statistics from logged measurements

        Args:
            task_name: Optional filter by task name
            last_n: Number of recent entries to analyze

        Returns:
            Statistics dictionary
        """
        try:
            # Read CSV
            measurements = []

            with open(self.log_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if task_name and row['task'] != task_name:
                        continue

                    measurements.append({
                        'task': row['task'],
                        'latency_ms': float(row['latency_ms']) if row['latency_ms'] else None
                    })

            # Get last N
            measurements = measurements[-last_n:]

            if not measurements:
                return {}

            # Calculate statistics
            latencies = [m['latency_ms'] for m in measurements if m['latency_ms'] is not None]

            if not latencies:
                return {}

            stats = {
                'count': len(latencies),
                'mean_ms': sum(latencies) / len(latencies),
                'min_ms': min(latencies),
                'max_ms': max(latencies),
                'median_ms': sorted(latencies)[len(latencies) // 2]
            }

            return stats

        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            return {}

    def save_metrics(self):
        """Save any buffered metrics (for compatibility)"""
        # Metrics are saved immediately in log_measurement
        pass

    def cleanup(self):
        """Cleanup profiler resources"""
        if self.gpu_monitoring:
            try:
                pynvml.nvmlShutdown()
            except:
                pass

        logger.info("Performance profiler cleaned up")
