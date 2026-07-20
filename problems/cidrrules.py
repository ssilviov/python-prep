def parse_addr(addr: str) -> int:
    bytes = addr.split(".")
    if len(bytes) != 4:
        raise ValueError(f"cannot parse f{addr}")
    res = 0
    for b in bytes:
        res = res << 8
        res += int(b)
    return res


def match(rule: str, addr: int):
    components = rule.split("/")

    if len(components) > 2:
        raise ValueError(f"cannot parse rule: {rule}")

    network = parse_addr(components[0])
    bits = 32
    if len(components) > 1:
        bits = int(components[1])

    if bits == 0:
        return True

    netmask = ((1 << bits) - 1) << (32 - bits)
    return (addr & netmask) == (network & netmask)


def access_ok(rules: list[tuple[str, bool]], addr: str):
    """Check IP addr against rules.

    Returns approved or not and rule index.
    """

    parsed_addr = parse_addr(addr)
    for idx, (rule, action) in enumerate(rules):
        if match(rule, parsed_addr):
            return action, idx

    return False, -1
