import os

from src.config.config import WEBSITE_NAME, WEB_SERVER_ROOT_PATH, WEB_SERVER_STYLE_PATH, WEB_SERVER_SCRIPT_PATH
from src.libs.microdot import Microdot, Response
from src.libs.utemplate import Template

application: Microdot = Microdot()

try:
    os.remove(WEB_SERVER_ROOT_PATH + "/" + WEBSITE_NAME + ".py")
except OSError as e:
    print(e)

Template.initialize(template_dir=WEB_SERVER_ROOT_PATH)
webpage: Template = Template(WEBSITE_NAME + ".html")
Response.default_content_type = "text/html"


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
