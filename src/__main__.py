""" Here is the entry point

This module starts the application by calling the main pipeline.
"""

def start() -> None:
    """Runs the application.

    Calls the main from pipeline and handles unexpected termination
    or runtime errors.
    """
    try:
        from src.pipe import main
        main()
    except Exception as error:
        print(f"Error found: {error}")


if __name__ == "__main__":
    start()