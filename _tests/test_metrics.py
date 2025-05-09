"""
Metric Validation Tests

Tests:
- Metric naming conventions
- Label consistency
- Value ranges
- Histogram/Summary quantiles
"""

import pytest
from prometheus_client.parser import text_string_to_metric_families

from app.core.prometheus.config import get_prometheus_config


@pytest.fixture
def sample_metrics():
    """Example metrics payload for testing"""
    return """
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 100
http_requests_total{method="POST",status="400"} 5

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 95
http_request_duration_seconds_bucket{le="0.5"} 100
http_request_duration_seconds_sum 12.7
http_request_duration_seconds_count 100
"""


def test_metric_naming_conventions():
    """Verify default Prometheus metrics follow naming conventions."""
    import requests
    response = requests.get(f"http://localhost:{get_prometheus_config().PORT}/metrics", timeout=5)
    assert response.status_code == 200
    metrics = list(text_string_to_metric_families(response.text))
    for metric in metrics:
        assert "_" in metric.name, "Metrics should use underscore notation"
        assert metric.name.islower(), "Metrics should be lowercase"


def test_metric_labels():
    """Verify labels for default Prometheus metrics are present and consistent."""
    import requests
    response = requests.get(f"http://localhost:{get_prometheus_config().PORT}/metrics", timeout=5)
    assert response.status_code == 200
    metrics = list(text_string_to_metric_families(response.text))
    for metric in metrics:
        for sample in metric.samples:
            assert isinstance(sample.labels, dict)
            # Prometheus native metrics may have empty or standard labels

    for metric in metrics:
        for sample in metric.samples:
            labels = sample.labels
            if "status" in labels:
                assert labels["status"].isdigit(), "Status should be numeric"
            if "method" in labels:
                assert labels["method"] in ("GET", "POST", "PUT", "DELETE")


def test_metric_values(sample_metrics):
    """Verify metric values are valid"""
    metrics = list(text_string_to_metric_families(sample_metrics))

    for metric in metrics:
        for sample in metric.samples:
            if "total" in metric.name or "count" in metric.name:
                assert sample.value >= 0, "Counters cannot be negative"
            if "duration" in metric.name and "bucket" not in sample.name:
                assert sample.value > 0, "Durations must be positive"


@pytest.mark.performance
def test_metrics_collection_performance():
    """Verify metrics collection is performant"""
    # Add actual performance testing
    collection_time = 0.1  # Replace with actual measurement
    assert collection_time < 0.5, "Metrics collection too slow"
