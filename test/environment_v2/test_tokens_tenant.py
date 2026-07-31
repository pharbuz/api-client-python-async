from dynatrace import DynatraceAsync


async def test_start_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.start_rotation()
    active = token_config.active
    old = token_config.old
    assert active is not None
    assert old is not None
    assert active.value == "hRCnr6Yd3BFrtxaF"
    assert old.value == "prv0bYw93v8sU9b1"


async def test_cancel_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.cancel_rotation()
    active = token_config.active
    old = token_config.old
    assert active is not None
    assert old is not None
    assert active.value == "prv0bYw93v8sU9b1"
    assert old.value is None


async def test_finish_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.finish_rotation()
    active = token_config.active
    old = token_config.old
    assert active is not None
    assert old is not None
    assert active.value == "prv0bYw93v8sU9b1"
    assert old.value is None
