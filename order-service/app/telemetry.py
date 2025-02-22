"""
Telemetry configuration module.

This module sets up metrics, tracing, and logging for the application using
the OpenTelemetry libraries. It includes functions to configure:
  - Metrics (MeterProvider)
  - Tracing (TracerProvider)
  - Logging (LoggerProvider)
  - FastAPI instrumentation

All exporters are configured to send data to an OpenTelemetry Collector (OTLP)
via gRPC, with optional console exporters for debugging. Configure endpoints
in 'settings.otlp_grpc_endpoint'.
"""

import sys
import logging
from pythonjsonlogger import json  # For JSON log formatting
from app.core.config import settings

# Instrumentation for FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Resource (Service Name, etc.)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter

# Logs
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Traces
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter


def initialize_telemetry(app):
    """
    Main entry point to configure telemetry for the FastAPI application.

    1. Creates a shared Resource (with the service name).
    2. Configures metrics (MeterProvider).
    3. Configures tracing (TracerProvider).
    4. Configures logging (LoggerProvider).
    5. Instruments the FastAPI application with the above providers.

    :param app: FastAPI application instance.
    :return: None
    """
    # Create a Resource with service name (from settings)
    resource = Resource(
        attributes={
            SERVICE_NAME: settings.service_name
        }
    )

    # Flags for enabling or disabling the console exporters
    enable_console_metrics = False
    enable_console_traces = False
    enable_console_logging = True  # Always enable console logging, else you won't see anything


    # Set up metrics (returns a configured MeterProvider)
    meter_provider = initialize_metrics(resource, enable_console_metrics)

    # Set up tracing (returns a configured TracerProvider)
    tracer_provider = initialize_tracing(resource, enable_console_traces)

    # Set up logging
    initialize_logging(resource, enable_console_logging)

    # Instrument FastAPI with the configured providers
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        meter_provider=meter_provider
    )


def initialize_metrics(resource, enable_console=False):
    """
    Configure the OpenTelemetry metrics system, including:
    - An OTLP metric exporter to send metrics to the collector.
    - (Optional) A console metric exporter for local debugging.

    :param resource: An OpenTelemetry Resource for the MeterProvider.
    :return: A configured MeterProvider instance.
    """
    # OTLP metric exporter (sends data to the collector)
    otlp_metric_exporter = OTLPMetricExporter(
        endpoint=settings.otlp_grpc_endpoint,
        # Optionally configure headers, credentials, or "insecure=True" if needed
    )
    otlp_metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)

    # Add the OTLP metric reader to the list of readers
    metric_readers = [otlp_metric_reader]

    # Console metric exporter (uncomment to debug locally)
    if enable_console:
        console_metric_exporter = ConsoleMetricExporter()
        console_metric_reader = PeriodicExportingMetricReader(console_metric_exporter)
        # Add the console metric reader to the list of readers
        metric_readers.append(console_metric_reader)

    # Create the MeterProvider with the desired readers/exporters
    meter_provider = MeterProvider(
        metric_readers=metric_readers,
        resource=resource
    )
    # Set this MeterProvider as the global default
    metrics.set_meter_provider(meter_provider)

    return meter_provider


def initialize_tracing(resource, enable_console=False):
    """
    Configure the OpenTelemetry tracing system, including:
    - A TracerProvider with the given resource.
    - An OTLP span exporter to send traces to the collector.
    - (Optional) A console span exporter for local debugging.

    :param resource: An OpenTelemetry Resource for the TracerProvider.
    :return: A configured TracerProvider instance.
    """
    # Create the TracerProvider
    tracer_provider = TracerProvider(resource=resource)

    # OTLP exporter (sends trace data to the collector)
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.otlp_grpc_endpoint,
        # Optionally configure headers, credentials, or "insecure=True" if needed
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Console exporter (uncomment to debug locally)
    if enable_console:
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Set this TracerProvider as the global default
    trace.set_tracer_provider(tracer_provider)

    return tracer_provider


def initialize_logging(resource, enable_console=True):
    """
    Configure the OpenTelemetry logging system, including:
    - A LoggerProvider with the given resource.
    - An OTLP log exporter to send logs to the collector.
    - A console (stdout) handler for local debug logging.
    - A JSON formatter for structured logging in JSON format.

    :param resource: An OpenTelemetry Resource for the LoggerProvider.
    :return: None
    """
    # Standard Python logging setup
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Adjust this level as needed

    # Create the LoggerProvider
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    # OTLP log exporter (sends logs to the collector)
    otlp_exporter = OTLPLogExporter(
        endpoint=settings.otlp_grpc_endpoint,
        # Optionally configure headers, credentials, or "insecure=True" if needed
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    # OpenTelemetry logging handler (ties into the LoggerProvider)
    otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    otel_formatter = json.JsonFormatter("%(asctime)s %(levelname)s %(message)s")
    otel_handler.setFormatter(otel_formatter)
    logger.addHandler(otel_handler)

    # Standard console handler (prints logs to stdout in JSON format)
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = json.JsonFormatter("%(asctime)s %(levelname)s %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
