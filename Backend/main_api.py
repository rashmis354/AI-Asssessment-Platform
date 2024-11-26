import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,HTMLResponse
from config.config import LOGS_PATH
# Create Log Folder
current_directory = os.getcwd()

try:
    if not os.path.isdir(current_directory + LOGS_PATH):
        os.makedirs(current_directory + LOGS_PATH)

except Exception as e:
    print("Log Folder Creation Failed-" + str(e))


# import routers.engine as engine
import Personas.Evaluator.routers.create_assessment as evaluator_create_assesment

from modules.utils.generate_log_file import logger

origins = ["*"]

app = FastAPI(title="AI-Assessment-Platform")

# app.include_router(engine.router)
app.include_router(evaluator_create_assesment.router)
logger.info("----------------------Service Restarted----------------")
# app.mount("/assets", StaticFiles(directory="dist/assets", html=True), name="assets")

# @app.get("/")
# @app.get("/{path:path}")
# async def serve_react_app(path: str):
#     """
#     Serve the React application.

#     This endpoint serves the React application. It handles requests to the root URL
#     ("/") and any other path, returning the appropriate HTML or static file based
#     on the request path.

#     :param path: The requested path.
#     :return: A FileResponse or HTMLResponse depending on the requested file type.
#     """
#     build_path = Path("dist")
#     index_html_path = build_path / "index.html"
#     if path == "" or path is None:
#         index_path = index_html_path
#     else:
#         index_path = build_path / path

#     if index_path.suffix == ".html":
#         return FileResponse(index_path, media_type="text/html")
#     elif index_path.suffix == "":
#         return FileResponse(index_html_path, media_type="text/html")
#     elif index_path.suffix == ".svg":
#         return FileResponse(index_path, media_type="image/svg+xml")
#     elif index_path.suffix == ".png":
#         return FileResponse(index_path, media_type="image/png")
#     elif index_path.name == "favicon.ico":
#         return FileResponse(index_path, media_type="image/x-icon")
#     elif index_path.suffix == ".js":
#         return FileResponse(index_path, media_type="application/javascript")
#     elif index_path.suffix == ".css":
#         return FileResponse(index_path, media_type="text/css")

#     return HTMLResponse(content="React App not found", status_code=404)


# @app.middleware("http")
# async def add_security_headers(request, call_next):
#     csp_policy = "frame-ancestors 'None'"
#     response = await call_next(request)
 
#     if "server" in response.headers:
#         del response.headers["server"]
#     if "Server" in response.headers:
#         del response.headers["Server"]
 
#     response.headers["Server"] = "Hidden"
 
#     response.headers["X-Content-Type-Options"] = "nosniff"
#     response.headers["Content-Security-Policy"] = csp_policy
#     response.headers["Strict-Transport-Security"] = (
#         "max-age=31536000; includeSubDomains;"
#     )
#     response.headers["X-Frame-Options"] = "SAMEORIGIN"
#     response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
#     response.headers["Permissions-Policy"] = (
#         "accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), "
#         "display-capture=(), document-domain=(), encrypted-media=(), fullscreen=*, geolocation=(), "
#         "gyroscope=(), magnetometer=(), microphone=(), midi=(), payment=(), picture-in-picture=(), "
#         "publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=()"
#     )
#     response.headers["X-XSS-Protection"] = "1; mode=block"

#     session_token = request.cookies.get("session_token")
#     if session_token:
#         response.set_cookie(
#             key="secure_cookie",             
#             value="temp",
#             httponly=True,
#             secure=True,
#             samesite='lax'
#         )
#         response.set_cookie(
#             key="session_token",             
#             value=session_token,
#             httponly=True,
#             secure=True,
#             samesite='lax'
#         )
 
#     return response
