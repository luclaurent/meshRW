import pytest
from meshRW.various import convert_size, timeit
from loguru import logger
import time

def test_convert_size():
    # Test for 0 bytes
    assert convert_size(0) == '0B'

    # Test for exact powers of 1024
    assert convert_size(1024) == '1 KB'
    assert convert_size(1048576) == '1 MB'
    assert convert_size(1073741824) == '1 GB'

    # Test for non-exact values
    assert convert_size(1536) == '1.5 KB'
    assert convert_size(1572864) == '1.5 MB'

    # Test for very large values
    assert convert_size(1099511627776) == '1 TB'

    # Test for negative input
    with pytest.raises(ValueError):
        convert_size(-1024)


# def test_timeit_decorator(caplog):
#     @timeit("Test Function")
#     def sample_function():
#         time.sleep(0.1)  # Simulate a function that takes time

#     with caplog.at_level("DEBUG"):
#         sample_function()

#     # Check if the log contains the expected message
#     assert any("Test Function" in message for message in caplog.text)
#     assert any("s" in message for message in caplog.text)