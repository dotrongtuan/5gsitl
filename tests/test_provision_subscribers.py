from tools.provision_subscribers import build_commands


def test_build_commands_for_single_slice() -> None:
    commands = build_commands(
        {
            "imsi": "001010123456780",
            "key": "00112233445566778899AABBCCDDEEFF",
            "opc": "63BFA50EE6523365FF14C1F45F88737D",
            "dnn": "internet",
            "slices": [{"sst": 1, "sd": "000001"}],
        },
        "/tmp/open5gs-dbctl",
        "mongodb://127.0.0.1/open5gs",
    )
    assert commands[0][-2:] == ["remove", "001010123456780"]
    assert "add_ue_with_slice" in commands[1]
    assert commands[1][-3:] == ["internet", "1", "000001"]


def test_build_commands_for_multi_slice() -> None:
    commands = build_commands(
        {
            "imsi": "001010123456780",
            "key": "00112233445566778899AABBCCDDEEFF",
            "opc": "63BFA50EE6523365FF14C1F45F88737D",
            "dnn": "internet",
            "slices": [{"sst": 1, "sd": "000001"}, {"sst": 1, "sd": "000002"}],
            "ipv4": "10.45.0.2",
        },
        "/tmp/open5gs-dbctl",
        "mongodb://127.0.0.1/open5gs",
    )
    joined = [" ".join(command) for command in commands]
    assert any("update_slice" in item for item in joined)
    assert any("static_ip 001010123456780 10.45.0.2" in item for item in joined)
