"""
Ingenious Irrigation — Application Entrypoint
---------------------------------------------
Bootstraps:
- Configuration
- Logging
- System Orchestrator (AI, irrigation, scheduler, health monitor)
- Weather service
- FastAPI application
- Graceful shutdown handling

This file is the authoritative runtime entrypoint for the entire system.
"""

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


# ---------------------------------------------------------
# Terminal Color Overrides (Chrome-Green Hacker Style)
# ---------------------------------------------------------
logging.addLevelName(logging.INFO, "\033[92mINFO\033[0m")
logging.addLevelName(logging.WARNING, "\033[93mWARN\033[0m")
logging.addLevelName(logging.ERROR, "\033[91mERROR\033[0m")


# ---------------------------------------------------------
# Application Context Manager
# ---------------------------------------------------------
@contextmanager
def application_context():
    """
    Creates and manages the lifecycle of the AppContext.
    Ensures config + logging are initialized before anything else.
    """

    # Load config early so logger can use it
    raw_config = load_system_config()

    ctx = AppContext()
    ctx.config = raw_config  # Attach config before logger initialization

    logger = configure_root_logger(raw_config)
    ctx.logger = logger

    # -----------------------------------------------------
    # Futuristic chrome-green boot banner
    # -----------------------------------------------------
    banner = r"""
   ███████╗██╗███╗   ██╗ ██████╗ ███████╗██╗   ██╗██╗███████╗
   ██╔════╝██║████╗  ██║██╔════╝ ██╔════╝██║   ██║██║██╔════╝
   █████╗  ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██║███████╗
   ██╔══╝  ██║██║╚██╗██║██║   ██║██╔══╝  ╚██╗ ██╔╝██║╚════██║
   ██║     ██║██║ ╚████║╚██████╔╝███████╗ ╚████╔╝ ██║███████║
   ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝╚══════╝

                I N G E N I O U S   I R R I G A T I O N   O S
--------------------------------------------------------------------------------
"""
    logger.info("\n%s", banner)

    logger.info(">> Initializing quantum hydration matrix...")
    logger.info(">> Spinning up AI inference core...")
    logger.info(">> Activating irrigation control relays...")
    logger.info(">> Linking weather intelligence network...")
    logger.info(">> Establishing secure uplink to dashboard...")
    logger.info(">> System integrity: STABLE")
    logger.info(">> Boot sequence: COMPLETE\n")

    logger.info("System Name: %s", ctx.get("system", "name", default="Ingenious Irrigation"))
    logger.info("Environment: %s", ctx.get("system", "environment", default="unknown"))
    logger.info("Simulation Mode: %s", ctx.simulation_mode)

    try:
        yield ctx
    finally:
        logger.info("Shutting down AppContext...")
        ctx.stop()
        logger.info("AppContext shutdown complete.")


# ---------------------------------------------------------
# Main Application Runtime
# ---------------------------------------------------------
def main():
    with application_context() as ctx:
        logger: logging.Logger = ctx.logger  # type: ignore

        # -------------------------------------------------
        # Initialize Orchestrator (AI, irrigation, scheduler)
        # -------------------------------------------------
        orchestrator = SystemOrchestrator(ctx)

        logger.info("Running startup checks...")
        orchestrator.run_startup_checks()

        logger.info("Starting background services...")
        orchestrator.start_background_services()

        # -------------------------------------------------
        # Weather Service
        # -------------------------------------------------
        weather_service = WeatherService(ctx)

        # -------------------------------------------------
        # Build FastAPI App
        # -------------------------------------------------
        app = create_api_app(
            ctx=ctx,
            ai_engine=orchestrator.ai_engine,
            irrigation_controller=orchestrator.irrigation_controller,
            weather_service=weather_service,
        )

        host = ctx.get("api", "host", default="127.0.0.1")
        port = ctx.get("api", "port", default=8000)

        logger.info("Starting Ingenious Irrigation API at http://%s:%s", host, port)

        # -------------------------------------------------
        # Graceful Shutdown Handling
        # -------------------------------------------------
        shutdown_event = threading.Event()

        def handle_signal(signum, frame):
            logger.warning("Received signal %s — initiating graceful shutdown...", signum)
            shutdown_event.set()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        # -------------------------------------------------
        # Start Uvicorn Server
        # -------------------------------------------------
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            reload=False,  # safer for production
        )
        server = uvicorn.Server(config=config)

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        # -------------------------------------------------
        # Main Loop — Wait for Shutdown
        # -------------------------------------------------
        try:
            while not shutdown_event.is_set() and server_thread.is_alive():
                server_thread.join(timeout=0.5)

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt received — shutting down...")

        finally:
            # Futuristic shutdown banner
            shutdown_banner = r"""
──────────────────────────────────────────────────────────────
   S Y S T E M   S H U T D O W N   I N I T I A T E D
──────────────────────────────────────────────────────────────
"""
            logger.info("\n%s", shutdown_banner)
            logger.info(">> Releasing AI cores...")
            logger.info(">> Powering down irrigation relays...")
            logger.info(">> Saving state to memory vault...")
            logger.info(">> Disconnecting weather uplink...")
            logger.info(">> Shutdown complete.")

            orchestrator.shutdown()
            sys.exit(0)


# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
