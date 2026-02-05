from core.app_context import AppContext
from ai.engine import GardenAIEngine
from api.server import create_api_app
import uvicorn


def main():
    ctx = AppContext()
    ai_engine = GardenAIEngine(ctx)

    # Quick CLI test: evaluate both zones and print
    for zone_id in [1, 2]:
        result = ai_engine.evaluate_zone(zone_id)
        print(
            f"[Zone {zone_id}] ideal={result.ideal_duration_minutes:.1f}m "
            f"health={result.health_score:.2f} "
            f"emergency={result.emergency_detected} "
            f"reason={result.emergency_reason}"
        )

    # Start API
    app = create_api_app(ctx, ai_engine)
    host = ctx.get("api", "host", default="127.0.0.1")
    port = ctx.get("api", "port", default=8000)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
