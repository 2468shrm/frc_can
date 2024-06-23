from msg_format import FRCCANDevice


"""This is a test wrapper to make sure the above stuff is correct.."""
if __name__ == '__main__':
    test1 = FRCCANDevice()
    expected_value = 0
    _err_str = f"test1 expected to have value 0x{expected_value:08x}," + \
        f"not 0x{test1.message_id:08x}"
    if test1.message_id != expected_value:
        raise RuntimeError(_err_str)
    _pass_str = "PASS: test1.message_id value should be " + \
        f"0x{expected_value:08x}, is 0x{test1.message_id:08x}"
    print(_pass_str)

    test2 = FRCCANDevice(device_type=FRCCANDevice.DEVICE_TYPE_MISCELLANEOUS,
                         manufacturer=FRCCANDevice.MANUF_TEAM_USE,
                         api=1,
                         device_number=1)
    expected_value = 0x0a080041
    if test2.message_id != expected_value:
        _err_str = f"test2 expected to have value 0x{expected_value:08x}," + \
            f" not 0x{test1.message_id:08x}"
        raise RuntimeError(_err_str)
    _pass_str = "PASS: test2.message_id value should be " + \
        f"0x{expected_value:08x}, is 0x{test2.message_id:08x}"
    print(_pass_str)

    # Universal heartbeat message id..
    uhb = FRCCANDevice(message_id=0x01011840)
    _pass_str = f"Universal heartbeat (message_id of {uhb.message_id})" + \
        f"\n decomposition is {uhb}"
    print(_pass_str)
