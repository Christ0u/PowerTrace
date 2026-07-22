import os
import ujson

from src.classes.AcquisitionService import AcquisitionService
from src.config.config import WEBSITE_NAME, WEB_SERVER_ROOT_PATH, WEB_SERVER_STYLE_PATH, WEB_SERVER_SCRIPT_PATH, \
    MIN_SAMPLE_PERIOD_MS, MAX_SAMPLE_PERIOD_MS, MIN_DURATION_S, MAX_DURATION_S
from src.libs.microdot import Microdot, Response
from src.libs.utemplate import Template

application: Microdot = Microdot()
acquisition_service: AcquisitionService | None = None

try:
    os.remove(WEB_SERVER_ROOT_PATH + "/" + WEBSITE_NAME + ".py")
except OSError as e:
    print(e)

Template.initialize(template_dir=WEB_SERVER_ROOT_PATH)
webpage: Template = Template(WEBSITE_NAME + ".html")
Response.default_content_type = "text/html"


def configure_acquisition_service(service: AcquisitionService) -> None:
    global acquisition_service
    acquisition_service = service


def get_response_from_json(payload: dict, status_code: int) -> Response:
    return Response(
        body=ujson.dumps(payload),
        status_code=status_code,
        headers={"Content-Type": "application/json"}
    )


def parse_sample_period_ms(request) -> int:
    raw_value = request.form.get("sample_period_ms")

    if raw_value is None:
        raise ValueError("Missing sample_period_ms")

    sample_period_ms = int(raw_value)

    if sample_period_ms < MIN_SAMPLE_PERIOD_MS:
        raise ValueError(
            "sample_period_ms is too small "
            f"(min: {MIN_SAMPLE_PERIOD_MS})"
        )

    if sample_period_ms > MAX_SAMPLE_PERIOD_MS:
        raise ValueError(
            "sample_period_ms is too large "
            f"(max: {MAX_SAMPLE_PERIOD_MS})"
        )

    return sample_period_ms


def parse_duration_ms(request) -> int | None:
    recording_mode = request.form.get("recording_mode")

    if recording_mode is None:
        raise ValueError("Missing recording_mode")

    if recording_mode == "manual":
        return None

    if recording_mode != "timed":
        raise ValueError("Invalid recording_mode")

    raw_value = request.form.get("duration_seconds")

    if raw_value is None:
        raise ValueError("Missing duration_seconds")

    duration_seconds = int(raw_value)

    if duration_seconds < MIN_DURATION_S:
        raise ValueError(
            f"duration_seconds is too small (min: {MIN_DURATION_S})")

    if duration_seconds > MAX_DURATION_S:
        raise ValueError(
            f"duration_seconds is too large (max: {MAX_DURATION_S})")

    return duration_seconds * 1000


def generate_webpage() -> str:
    """
    Render and return the main HTML page.

    :return: rendered HTML string.
    """
    parameters: dict[str, dict] = {}
    return webpage.render(parameters=parameters)


@application.route("/")
async def index(request) -> Response:
    """
    Serve the main HTML page.

    :param request: incoming HTTP request.
    :return: HTTP response containing the rendered HTML page.
    """
    return Response(generate_webpage())


@application.route("/style.css")
async def style(request) -> Response:
    """
    Serve the CSS stylesheet.

    :param request: incoming HTTP request.
    :return: HTTP response containing the CSS file.
    """
    return Response(
        open(WEB_SERVER_STYLE_PATH).read(),
        headers={"Content-Type": "text/css"},
    )


@application.route("/script.js")
async def script(request) -> Response:
    """
    Serve the JavaScript file.

    :param request: incoming HTTP request.
    :return: HTTP response containing the JavaScript file.
    """
    return Response(
        open(WEB_SERVER_SCRIPT_PATH).read(),
        headers={"Content-Type": "text/javascript"},
    )


@application.route("/api/acquisition/status")
async def acquisition_status(request) -> Response:
    if acquisition_service is None:
        return get_response_from_json(
            payload={
                "success": False,
                "message": "Acquisition service is not configured."},
            status_code=500)

    return get_response_from_json(
        payload={
            "success": True,
            "data": acquisition_service.get_status()
        },
        status_code=200
    )


@application.post("/api/acquisition/start")
async def acquisition_start(request) -> Response:
    if acquisition_service is None:
        return get_response_from_json(
            payload={
                "success": False,
                "message": "Acquisition service is not configured."},
            status_code=500)

    try:
        if acquisition_service.is_recording():
            return get_response_from_json(
                payload={
                    "success": True,
                    "message": "Acquisition is already running",
                    "data": acquisition_service.get_status()},
                status_code=409
            )

        sample_period_ms = parse_sample_period_ms(request)
        duration_ms = parse_duration_ms(request)

        acquisition_service.set_sample_period_ms(sample_period_ms)

        await acquisition_service.start(duration_ms=duration_ms, truncate=True)

        return get_response_from_json(
            payload={
                "success": True,
                "message": "Acquisition is running",
                "data": acquisition_service.get_status()
            },
            status_code=200
        )

    except Exception as error:
        return get_response_from_json(
            payload={
                "success": False,
                "message": str(error)
            },
            status_code=500
        )


@application.post("/api/acquisition/stop")
async def acquisition_stop(request) -> Response:
    if acquisition_service is None:
        return get_response_from_json(
            payload={
                "success": False,
                "message": "Acquisition service is not configured."},
            status_code=500
        )

    try:
        await acquisition_service.stop()

        return get_response_from_json(
            payload={
                "success": True,
                "message": "Acquisition is stopped",
                "data": acquisition_service.get_status()
            },
            status_code=200
        )

    except Exception as error:
        return get_response_from_json(
            payload={
                "success": False,
                "message": str(error)
            },
            status_code=500
        )
