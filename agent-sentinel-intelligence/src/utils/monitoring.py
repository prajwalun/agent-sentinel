"""
Enterprise Monitoring and Health Check System for Agent Sentinel Intelligence Layer.

Provides comprehensive monitoring, health checks, metrics collection, and alerting
for enterprise-grade observability and system reliability.
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    check_function: Callable[[], Dict[str, Any]]
    interval_seconds: int = 60
    timeout_seconds: int = 30
    critical: bool = False
    enabled: bool = True
    last_run: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    consecutive_failures: int = 0
    max_failures: int = 3


@dataclass
class Metric:
    """Metric data structure."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class Alert:
    """Alert configuration."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    message: str
    severity: str = "warning"
    enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: Optional[datetime] = None


class MetricsCollector:
    """Collects and stores system metrics."""
    
    def __init__(self, max_metrics: int = 10000):
        self.metrics: List[Metric] = []
        self.max_metrics = max_metrics
        self._lock = threading.Lock()
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None, unit: str = ""):
        """Record a metric."""
        with self._lock:
            metric = Metric(
                name=name,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
                unit=unit
            )
            self.metrics.append(metric)
            
            # Trim old metrics if we exceed the limit
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def get_metrics(self, name: str = None, since: datetime = None) -> List[Metric]:
        """Get metrics with optional filtering."""
        with self._lock:
            filtered_metrics = self.metrics
            
            if name:
                filtered_metrics = [m for m in filtered_metrics if m.name == name]
            
            if since:
                filtered_metrics = [m for m in filtered_metrics if m.timestamp >= since]
            
            return filtered_metrics.copy()
    
    def get_latest_metric(self, name: str) -> Optional[Metric]:
        """Get the latest metric by name."""
        with self._lock:
            for metric in reversed(self.metrics):
                if metric.name == name:
                    return metric
            return None
    
    def clear_metrics(self):
        """Clear all metrics."""
        with self._lock:
            self.metrics.clear()


class SystemMonitor:
    """Comprehensive system monitoring."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.monitoring_active = False
        self.monitor_thread = None
        self.monitor_interval = 30  # seconds
    
    def start_monitoring(self):
        """Start system monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_system_metrics(self):
        """Collect system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics_collector.record_metric("system.cpu.percent", cpu_percent, unit="%")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.metrics_collector.record_metric("system.memory.percent", memory.percent, unit="%")
            self.metrics_collector.record_metric("system.memory.available", memory.available, unit="bytes")
            self.metrics_collector.record_metric("system.memory.used", memory.used, unit="bytes")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics_collector.record_metric("system.disk.percent", disk_percent, unit="%")
            self.metrics_collector.record_metric("system.disk.free", disk.free, unit="bytes")
            
            # Network metrics
            net_io = psutil.net_io_counters()
            self.metrics_collector.record_metric("system.network.bytes_sent", net_io.bytes_sent, unit="bytes")
            self.metrics_collector.record_metric("system.network.bytes_recv", net_io.bytes_recv, unit="bytes")
            
            # Process metrics
            process = psutil.Process()
            self.metrics_collector.record_metric("process.cpu.percent", process.cpu_percent(), unit="%")
            self.metrics_collector.record_metric("process.memory.rss", process.memory_info().rss, unit="bytes")
            self.metrics_collector.record_metric("process.memory.vms", process.memory_info().vms, unit="bytes")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")


class HealthChecker:
    """Health check manager."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.metrics_collector = metrics_collector
        self.checking_active = False
        self.check_thread = None
    
    def register_health_check(self, health_check: HealthCheck):
        """Register a health check."""
        self.health_checks[health_check.name] = health_check
        logger.info(f"Registered health check: {health_check.name}")
    
    def start_health_checking(self):
        """Start health checking."""
        if self.checking_active:
            return
        
        self.checking_active = True
        self.check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.check_thread.start()
        logger.info("Health checking started")
    
    def stop_health_checking(self):
        """Stop health checking."""
        self.checking_active = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        logger.info("Health checking stopped")
    
    def _health_check_loop(self):
        """Main health checking loop."""
        while self.checking_active:
            try:
                self._run_health_checks()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                time.sleep(10)
    
    def _run_health_checks(self):
        """Run all health checks."""
        for name, check in self.health_checks.items():
            if not check.enabled:
                continue
            
            now = datetime.utcnow()
            
            # Check if it's time to run this health check
            if check.last_run and (now - check.last_run).total_seconds() < check.interval_seconds:
                continue
            
            try:
                # Run the health check with timeout
                result = self._run_single_health_check(check)
                check.last_run = now
                check.last_result = result
                
                # Record metrics
                status_value = 1 if result.get('healthy', False) else 0
                self.metrics_collector.record_metric(
                    f"health.{name}.status",
                    status_value,
                    tags={"check": name}
                )
                
                # Handle success/failure
                if result.get('healthy', False):
                    check.consecutive_failures = 0
                else:
                    check.consecutive_failures += 1
                    logger.warning(f"Health check failed: {name} - {result.get('message', 'Unknown error')}")
                
            except Exception as e:
                check.consecutive_failures += 1
                check.last_result = {
                    'healthy': False,
                    'message': f"Health check exception: {e}",
                    'timestamp': now.isoformat()
                }
                logger.error(f"Health check exception for {name}: {e}")
    
    def _run_single_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Run a single health check with timeout."""
        try:
            # Simple timeout implementation
            start_time = time.time()
            result = check.check_function()
            duration = time.time() - start_time
            
            if duration > check.timeout_seconds:
                return {
                    'healthy': False,
                    'message': f"Health check timeout ({duration:.2f}s > {check.timeout_seconds}s)",
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {'healthy': bool(result), 'message': str(result)}
            
            if 'healthy' not in result:
                result['healthy'] = True
            
            result['timestamp'] = datetime.utcnow().isoformat()
            result['duration'] = duration
            
            return result
            
        except Exception as e:
            return {
                'healthy': False,
                'message': f"Health check error: {e}",
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        overall_status = HealthStatus.HEALTHY
        failed_checks = []
        degraded_checks = []
        
        for name, check in self.health_checks.items():
            if not check.enabled:
                continue
            
            if check.last_result is None:
                overall_status = HealthStatus.UNKNOWN
                continue
            
            if not check.last_result.get('healthy', False):
                if check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                    failed_checks.append(name)
                else:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
                    degraded_checks.append(name)
        
        return {
            'status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {name: check.last_result for name, check in self.health_checks.items() if check.enabled},
            'failed_checks': failed_checks,
            'degraded_checks': degraded_checks
        }


class AlertManager:
    """Alert management system."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.alerts: Dict[str, Alert] = {}
        self.metrics_collector = metrics_collector
        self.alert_handlers: List[Callable[[Alert, Dict[str, Any]], None]] = []
    
    def register_alert(self, alert: Alert):
        """Register an alert."""
        self.alerts[alert.name] = alert
        logger.info(f"Registered alert: {alert.name}")
    
    def add_alert_handler(self, handler: Callable[[Alert, Dict[str, Any]], None]):
        """Add an alert handler."""
        self.alert_handlers.append(handler)
    
    def check_alerts(self, context: Dict[str, Any]):
        """Check all alerts against current context."""
        for name, alert in self.alerts.items():
            if not alert.enabled:
                continue
            
            # Check cooldown
            if alert.last_triggered:
                time_since_last = (datetime.utcnow() - alert.last_triggered).total_seconds()
                if time_since_last < alert.cooldown_seconds:
                    continue
            
            try:
                if alert.condition(context):
                    self._trigger_alert(alert, context)
            except Exception as e:
                logger.error(f"Error checking alert {name}: {e}")
    
    def _trigger_alert(self, alert: Alert, context: Dict[str, Any]):
        """Trigger an alert."""
        alert.last_triggered = datetime.utcnow()
        
        logger.warning(f"Alert triggered: {alert.name} - {alert.message}")
        
        # Record alert metric
        self.metrics_collector.record_metric(
            f"alert.{alert.name}.triggered",
            1,
            tags={"alert": alert.name, "severity": alert.severity}
        )
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert, context)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")


class MonitoringSystem:
    """Main monitoring system coordinator."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.system_monitor = SystemMonitor(self.metrics_collector)
        self.health_checker = HealthChecker(self.metrics_collector)
        self.alert_manager = AlertManager(self.metrics_collector)
        
        # Setup default health checks
        self._setup_default_health_checks()
        
        # Setup default alerts
        self._setup_default_alerts()
    
    def start(self):
        """Start all monitoring components."""
        self.system_monitor.start_monitoring()
        self.health_checker.start_health_checking()
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop all monitoring components."""
        self.system_monitor.stop_monitoring()
        self.health_checker.stop_health_checking()
        logger.info("Monitoring system stopped")
    
    def _setup_default_health_checks(self):
        """Setup default health checks."""
        # System resource health check
        def check_system_resources():
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            
            issues = []
            if cpu_percent > 90:
                issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            if memory_percent > 85:
                issues.append(f"High memory usage: {memory_percent:.1f}%")
            if disk_percent > 90:
                issues.append(f"High disk usage: {disk_percent:.1f}%")
            
            return {
                'healthy': len(issues) == 0,
                'message': '; '.join(issues) if issues else 'System resources OK',
                'details': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_percent,
                    'disk_percent': disk_percent
                }
            }
        
        self.health_checker.register_health_check(HealthCheck(
            name="system_resources",
            check_function=check_system_resources,
            interval_seconds=60,
            critical=True
        ))
        
        # Process health check
        def check_process_health():
            try:
                process = psutil.Process()
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                issues = []
                if cpu_percent > 50:
                    issues.append(f"High process CPU: {cpu_percent:.1f}%")
                if memory_mb > 1000:  # 1GB
                    issues.append(f"High process memory: {memory_mb:.1f}MB")
                
                return {
                    'healthy': len(issues) == 0,
                    'message': '; '.join(issues) if issues else 'Process health OK',
                    'details': {
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_mb
                    }
                }
            except Exception as e:
                return {
                    'healthy': False,
                    'message': f"Process health check failed: {e}"
                }
        
        self.health_checker.register_health_check(HealthCheck(
            name="process_health",
            check_function=check_process_health,
            interval_seconds=30,
            critical=False
        ))
    
    def _setup_default_alerts(self):
        """Setup default alerts."""
        # High CPU alert
        def high_cpu_condition(context):
            cpu_metric = self.metrics_collector.get_latest_metric("system.cpu.percent")
            return cpu_metric and cpu_metric.value > 80
        
        self.alert_manager.register_alert(Alert(
            name="high_cpu",
            condition=high_cpu_condition,
            message="High CPU usage detected",
            severity="warning",
            cooldown_seconds=300
        ))
        
        # High memory alert
        def high_memory_condition(context):
            memory_metric = self.metrics_collector.get_latest_metric("system.memory.percent")
            return memory_metric and memory_metric.value > 85
        
        self.alert_manager.register_alert(Alert(
            name="high_memory",
            condition=high_memory_condition,
            message="High memory usage detected",
            severity="warning",
            cooldown_seconds=300
        ))
        
        # Health check failure alert
        def health_check_failure_condition(context):
            health_status = self.health_checker.get_health_status()
            return health_status['status'] in ['unhealthy', 'degraded']
        
        self.alert_manager.register_alert(Alert(
            name="health_check_failure",
            condition=health_check_failure_condition,
            message="Health check failures detected",
            severity="critical",
            cooldown_seconds=600
        ))
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'health': self.health_checker.get_health_status(),
            'metrics_count': len(self.metrics_collector.metrics),
            'alerts': {name: alert.last_triggered.isoformat() if alert.last_triggered else None 
                      for name, alert in self.alert_manager.alerts.items()},
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics to file."""
        metrics_data = []
        for metric in self.metrics_collector.metrics:
            metrics_data.append({
                'name': metric.name,
                'value': metric.value,
                'timestamp': metric.timestamp.isoformat(),
                'tags': metric.tags,
                'unit': metric.unit
            })
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Exported {len(metrics_data)} metrics to {filepath}")


# Global monitoring instance
_monitoring_system = None


def get_monitoring_system() -> MonitoringSystem:
    """Get the global monitoring system instance."""
    global _monitoring_system
    if _monitoring_system is None:
        _monitoring_system = MonitoringSystem()
    return _monitoring_system


def record_metric(name: str, value: float, tags: Dict[str, str] = None, unit: str = ""):
    """Record a metric to the global monitoring system."""
    monitoring = get_monitoring_system()
    monitoring.metrics_collector.record_metric(name, value, tags, unit)


def get_health_status() -> Dict[str, Any]:
    """Get health status from the global monitoring system."""
    monitoring = get_monitoring_system()
    return monitoring.get_status() 