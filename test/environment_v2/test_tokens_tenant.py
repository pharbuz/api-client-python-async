from dynatrace import DynatraceAsync


async def test_start_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.start_rotation()
    assert token_config.active.value == "hRCnr6Yd3BFrtxaF"
    assert token_config.old.value == "prv0bYw93v8sU9b1"


async def test_cancel_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.cancel_rotation()
    assert token_config.active.value == "prv0bYw93v8sU9b1"
    assert token_config.old.value is None


async def test_finish_rotation(dt: DynatraceAsync):
    token_config = await dt.tenant_tokens.finish_rotation()
    assert token_config.active.value == "prv0bYw93v8sU9b1"
    assert token_config.old.value is None
