import os
import ujson

from src.classes.AcquisitionService import AcquisitionService
from src.config.config import WEBSITE_NAME, WEB_SERVER_ROOT_PATH, WEB_SERVER_STYLE_PATH, WEB_SERVER_SCRIPT_PATH
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

        await acquisition_service.start(duration_ms=None, truncate=True)

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
