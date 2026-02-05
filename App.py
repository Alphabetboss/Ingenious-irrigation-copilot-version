import logging
import signal
import sys
import threading
from contextlib import contextmanager

import uvicorn

from core.app_context import AppContext
from core.config_loader import load_system_config
from core.logger import configure_root_logger
from core.system_orchestrator import SystemOrchestrator
from api.server import create_api_app
from weather.weather_service import WeatherService


@contextmanager
def application_context():
    # Load config once for logger bootstrap
    raw_config = load_system_config()
    ctx = AppContext()  # AppContext will load config again and watch for changes

    # Attach config to context before logger so logger can use it
    ctx.config = raw_config

    logger = configure_root_logger(raw_config)
    ctx.logger = logger

    logger.info("System name: %s", ctx.get("system", "name", default="Ingenious Irrigation"))
    logger.info("Environment: %s", ctx.get("system", "environment", default="unknown"))
    logger.info("Simulation mode: %s", ctx.simulation_mode)

    try:
        yield ctx
    finally:
        logger.info("Shutting down AppContext...")
        ctx.stop()


def main():
    with application_context() as ctx:
        logger: logging.Logger = ctx.logger  # type: ignore[assignment]

        # High-level orchestrator wires AI, irrigation, scheduler, health monitor
        orchestrator = SystemOrchestrator(ctx)
        orchestrator.run_startup_checks()
        orchestrator.start_background_services()

        # Weather service for API/dashboard
        weather_service = WeatherService(ctx)

        # Build API app
        app = create_api_app(
            ctx=ctx,
            ai_engine=orchestrator.ai_engine,
            irrigation_controller=orchestrator.irrigation_controller,
            weather_service=weather_service,
        )

        host = ctx.get("api", "host", default="127.0.0.1")
        port = ctx.get("api", "port", default=8000)

        logger.info("Starting Ingenious Irrigation API on %s:%s", host, port)

        shutdown_event = threading.Event()

        def handle_signal(signum, frame):
            logger.info("Received signal %s, initiating graceful shutdown...", signum)
            shutdown_event.set()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="info",
        )
        server = uvicorn.Server(config=config)

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        try:
            while not shutdown_event.is_set() and server_thread.is_alive():
                server_thread.join(timeout=0.5)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, shutting down...")
        finally:
            logger.info("Stopping orchestrator and background services...")
            orchestrator.shutdown()
            logger.info("Application shutdown complete.")
            sys.exit(0)


if __name__ == "__main__":
    main()
