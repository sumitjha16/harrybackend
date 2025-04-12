import time
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_fastapi_instrumentator.metrics import Info

# Define custom metrics
REQUESTS_TOTAL = Counter(
    "storybook_requests_total",
    "Total number of requests",
    ["endpoint", "method", "status_code"]
)

RESPONSE_TIME = Histogram(
    "storybook_response_time_seconds",
    "Response time in seconds",
    ["endpoint", "method"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

TOKEN_COUNT = Counter(
    "storybook_token_count_total",
    "Total number of tokens processed",
    ["operation"]
)

MEMORY_USAGE = Gauge(
    "storybook_memory_usage_bytes",
    "Memory usage in bytes"
)

ACTIVE_REQUESTS = Gauge(
    "storybook_active_requests",
    "Number of active requests"
)


# Custom metrics
def response_time(metric_name: str = "http_response_time_seconds"):
    """Response time metrics"""

    def instrumentation(info: Info):
        # Store the start time when the request begins
        request_start_time = time.time()

        def observe_duration():
            if info.response:
                endpoint = info.request.url.path
                method = info.request.method
                duration = time.time() - request_start_time
                RESPONSE_TIME.labels(endpoint=endpoint, method=method).observe(duration)

        # This will be called after the response is generated
        info.response_hook = observe_duration

    return instrumentation


def active_requests_count():
    """Active requests metrics"""

    def instrumentation(info: Info):
        ACTIVE_REQUESTS.inc()

        def on_response():
            ACTIVE_REQUESTS.dec()

        info.response_hook = on_response

    return instrumentation


def register_metrics(app):
    """Register all metrics with the application"""
    instrumentator = Instrumentator()

    # Add default metrics
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    instrumentator.add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )

    # Add custom metrics
    instrumentator.add(response_time())
    instrumentator.add(active_requests_count())

    # Instrument app
    instrumentator.instrument(app).expose(app)

    return instrumentator