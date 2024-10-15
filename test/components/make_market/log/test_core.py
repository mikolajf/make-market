from make_market.log import core


def test_stream_logging(caplog):
    test_logger = core.get_logger("test_logger")

    msg = "Test msg"
    test_logger.info(msg)

    assert msg in caplog.text
