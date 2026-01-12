import uvicorn

from cnm_bookhub_be.settings import settings


def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "cnm_bookhub_be.web.application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.value.lower(),
        factory=True,
    )


if __name__ == "__main__":
    # uvicorn.run(
    #     "cnm_bookhub_be.main:app",
    #     host="localhost",  # <--- Sửa chỗ này từ "127.0.0.1" thành "localhost"
    #     port=8000,
    #     reload=True
    # )
    main()
