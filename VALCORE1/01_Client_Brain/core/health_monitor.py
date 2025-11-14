"""
VALCORE1 Health Monitor
Monitors GPU temperature, RAM, disk space, and network latency
"""

import logging
import threading
import time
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import json

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    logging.warning("pynvml not available - GPU monitoring disabled")

import psutil
import requests

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors system health metrics"""

    def __init__(self, config_path: str = "config/settings.json"):
        """Initialize health monitor"""
        self.config = self._load_config(config_path)
        self.running = False
        self.thread = None
        self.metrics_file = Path("logs/health_metrics.csv")

        # Initialize NVML for GPU monitoring
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.nvml_initialized = True
                logger.info("NVML initialized for GPU monitoring")
            except Exception as e:
                logger.error(f"Failed to initialize NVML: {e}")
                self.nvml_initialized = False
        else:
            self.nvml_initialized = False

        # Create logs directory
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize CSV file
        if not self.metrics_file.exists():
            with open(self.metrics_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'gpu0_temp', 'gpu0_util', 'gpu1_temp', 'gpu1_util',
                    'ram_percent', 'disk_free_gb', 'network_latency_ms'
                ])

        logger.info("Health monitor initialized")

    def _load_config(self, path: str) -> dict:
        """Load configuration"""
        with open(path, 'r') as f:
            config = json.load(f)
        return config.get('health_monitoring', {})

    def get_gpu_temp(self, device_id: int) -> Optional[float]:
        """
        Get GPU temperature

        Args:
            device_id: GPU device ID (0 or 1)

        Returns:
            Temperature in Celsius or None if unavailable
        """
        if not self.nvml_initialized:
            return None

        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            return float(temp)
        except Exception as e:
            logger.error(f"Error getting GPU {device_id} temperature: {e}")
            return None

    def get_gpu_utilization(self, device_id: int) -> Optional[float]:
        """
        Get GPU utilization percentage

        Args:
            device_id: GPU device ID

        Returns:
            Utilization percentage or None
        """
        if not self.nvml_initialized:
            return None

        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return float(util.gpu)
        except Exception as e:
            logger.error(f"Error getting GPU {device_id} utilization: {e}")
            return None

    def get_ram_usage(self) -> float:
        """
        Get RAM usage percentage

        Returns:
            RAM usage percentage
        """
        return psutil.virtual_memory().percent

    def get_disk_space(self, drive: str = "A:\\") -> float:
        """
        Get free disk space

        Args:
            drive: Drive letter (default: A:\)

        Returns:
            Free space in GB
        """
        try:
            usage = psutil.disk_usage(drive)
            return usage.free / (1024 ** 3)  # Convert to GB
        except Exception as e:
            logger.error(f"Error getting disk space for {drive}: {e}")
            return 0.0

    def ping_server(self, server_url: str = "http://192.168.1.121:11434") -> Optional[float]:
        """
        Ping ATOM server and measure latency

        Args:
            server_url: Server URL

        Returns:
            Latency in milliseconds or None if unreachable
        """
        try:
            start = time.time()
            response = requests.get(f"{server_url}/api/tags", timeout=5)
            latency = (time.time() - start) * 1000  # Convert to ms

            if response.status_code == 200:
                return latency
            else:
                return None

        except requests.exceptions.RequestException:
            return None

    def check_thresholds(self, metrics: Dict) -> list:
        """
        Check if any metrics exceed thresholds

        Args:
            metrics: Dictionary of current metrics

        Returns:
            List of warning messages
        """
        warnings = []

        # GPU temperature warnings
        gpu_temp_warning = self.config.get('gpu_temp_warning_threshold', 85)
        gpu_temp_critical = self.config.get('gpu_temp_critical_threshold', 90)

        for gpu_id in [0, 1]:
            temp = metrics.get(f'gpu{gpu_id}_temp')
            if temp:
                if temp >= gpu_temp_critical:
                    warnings.append(f"CRITICAL: GPU {gpu_id} temperature {temp}°C (threshold: {gpu_temp_critical}°C)")
                elif temp >= gpu_temp_warning:
                    warnings.append(f"WARNING: GPU {gpu_id} temperature {temp}°C (threshold: {gpu_temp_warning}°C)")

        # RAM warning
        ram_warning = self.config.get('ram_warning_threshold_percent', 85)
        if metrics['ram_percent'] >= ram_warning:
            warnings.append(f"WARNING: RAM usage {metrics['ram_percent']}% (threshold: {ram_warning}%)")

        # Disk space warning
        disk_warning = self.config.get('disk_warning_threshold_gb', 10)
        if metrics['disk_free_gb'] < disk_warning:
            warnings.append(f"WARNING: Low disk space {metrics['disk_free_gb']:.1f}GB (threshold: {disk_warning}GB)")

        return warnings

    def collect_metrics(self) -> Dict:
        """
        Collect all health metrics

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'gpu0_temp': self.get_gpu_temp(0),
            'gpu0_util': self.get_gpu_utilization(0),
            'gpu1_temp': self.get_gpu_temp(1),
            'gpu1_util': self.get_gpu_utilization(1),
            'ram_percent': self.get_ram_usage(),
            'disk_free_gb': self.get_disk_space(),
            'network_latency_ms': self.ping_server()
        }

        return metrics

    def log_metrics(self, metrics: Dict):
        """
        Log metrics to CSV file

        Args:
            metrics: Metrics dictionary
        """
        try:
            with open(self.metrics_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    metrics['timestamp'],
                    metrics['gpu0_temp'],
                    metrics['gpu0_util'],
                    metrics['gpu1_temp'],
                    metrics['gpu1_util'],
                    metrics['ram_percent'],
                    metrics['disk_free_gb'],
                    metrics['network_latency_ms']
                ])
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")

    def _monitor_loop(self):
        """Background monitoring loop"""
        check_interval = self.config.get('check_interval_seconds', 30)

        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_metrics()

                # Log to CSV
                self.log_metrics(metrics)

                # Check thresholds
                warnings = self.check_thresholds(metrics)
                for warning in warnings:
                    logger.warning(warning)

                # Sleep until next check
                time.sleep(check_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(check_interval)

    def start_monitoring(self):
        """Start background monitoring thread"""
        if not self.config.get('enabled', True):
            logger.info("Health monitoring disabled in config")
            return

        if self.thread and self.thread.is_alive():
            logger.warning("Health monitor already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Health monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Health monitoring stopped")

    def get_status(self) -> Dict:
        """
        Get current health status

        Returns:
            Status dictionary
        """
        metrics = self.collect_metrics()
        warnings = self.check_thresholds(metrics)

        return {
            **metrics,
            'warnings': warnings,
            'status': 'critical' if any('CRITICAL' in w for w in warnings) else 'warning' if warnings else 'ok'
        }

    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()

        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except:
                pass

        logger.info("Health monitor cleaned up")
