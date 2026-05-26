from .app import create_app
from .config import MODEL_PATH
from .hardware import Hardware
from . import pose_engine


def main() -> None:
    hw = Hardware()
    engine = pose_engine.PoseEngine(MODEL_PATH)

    input_shape = engine.get_input_tensor_shape()
    input_height = input_shape[1]
    input_width = input_shape[2]

    app = create_app(engine=engine, hw=hw, input_width=input_width, input_height=input_height)

    try:
        app.run(host="0.0.0.0", port=5000, threaded=True)
    finally:
        hw.close()


if __name__ == "__main__":
    main()

