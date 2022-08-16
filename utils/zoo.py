from sparsezoo import Model
from functools import wraps


def is_valid_stub(stub: str) -> bool:
    return stub and stub.startswith('zoo:')


def check_stub_before_invoke(func):
    @wraps(func)
    def wrapper(stub: str, *args, **kwargs):
        if is_valid_stub(stub):
            return func(stub, *args, **kwargs)
        raise ValueError(f"Invalid Stub: {stub}")

    return wrapper


@check_stub_before_invoke
def get_model_onnx_from_stub(stub: str):
    """
    Downloads model from stub and returns its onnx filepath

    :param stub: SparseZoo stub for the model
    :return: path to model.onnx for the specified stub
    """
    try:
        return Model(stub).onnx_model.path
    except Exception as e:
        raise ValueError(
            f"Could not find a valid onnx file for {stub}. Error:\n{e}"
        )


@check_stub_before_invoke
def get_checkpoint_from_stub(stub: str) -> str:
    """
    Helper to download a model checkpoint from SparseZoo Stub

    :param stub: A valid SparseZoo Stub
    :raises: ValueError if invalid stub given
    :return: path to model checkpoint (after downloading from SparseZoo)
    """

    try:
        return Model(stub).get_file("model.pth").path
    except Exception as e:
        raise ValueError(
            f"Could not find a valid framework file for {stub}. Error:\n{e}"
        )
