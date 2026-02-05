import logging
import signal
import sys
import threading
from contextlib import contextmanager
from typing import List

import uvicorn

from core.app_context import AppContext
from ai.engine import GardenAIEngine
from api.server import create_api_app
from irrigation.controller import IrrigationController


LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"


def configure_logging(ctx: AppContext) -> logging.Logger:
    log_level_str = ctx.get("system", "log_level", default="INFO")
    level = getattr(logging, log_level_str.upper(), logging.INFO)

    logging.basicConfig(level=level, format=LOG_FORMAT)
    logger = logging.getLogger("ingenious_irrigation")

    logger.info("Logging initialized with level: %s", log_level_str.upper())
    return logger


def get_zone_ids(ctx: AppContext) -> List[int]:
    zones = ctx.get("zones", default=[])
    return [z.get("id") for z in zones if "id" in z]


@contextmanager
def application_context():
    ctx = AppContext()
    logger = configure_logging(ctx)
    ctx.logger = logger

    logger.info("System name: %s", ctx.get("system", "name", default="Ingenious Irrigation"))
    logger.info("Environment: %s", ctx.get("system", "environment", default="unknown"))
    logger.info("Simulation mode: %s", ctx.simulation_mode)

    try:
        yield ctx
    finally:
        logger.info("Shutting down AppContext...")
        ctx.stop()


def run_startup_diagnostics(logger: logging.Logger, ai_engine: GardenAIEngine, ctx: AppContext):
    zone_ids = get_zone_ids(ctx)
    if not zone_ids:
        logger.warning("No zones configured in system_config.json")
        return

    logger.info("Running startup AI evaluation for zones: %s", zone_ids)
    for zone_id in zone_ids:
        try:
            result = ai_engine.evaluate_zone(zone_id)
            logger.info(
                "Zone %s → ideal=%.1fm, health=%.2f, emergency=%s, reason=%s",
                zone_id,
                result.ideal_duration_minutes,
                result.health_score,
                result.emergency_detected,
                result.emergency_reason,
            )
        except Exception as e:
            logger.exception("Error evaluating zone %s at startup: %s", zone_id, e)


def main():
    with application_context() as ctx:
        logger: logging.Logger = ctx.logger  # type: ignore[assignment]

        ai_engine = GardenAIEngine(ctx)
        ctx.ai_engine = ai_engine

        irrigation_controller = IrrigationController(ctx)

        run_startup_diagnostics(logger, ai_engine, ctx)

        app = create_api_app(ctx, ai_engine, irrigation_controller)
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
            logger.info("Application shutdown complete.")
            sys.exit(0)


if __name__ == "__main__":
    main()
