def get_likeness_word(s: str, x: str, reverse: bool = False, max_value: int = 50, len_penaly: bool = True) -> int:
    if reverse:
        s = s[::-1]
        x = x[::-1]
    if s == x:
        return max_value
    res = 0
    step = 1
    for char_s, char_x in zip(s, x):
        if char_s == char_x:
            res += step
        else:
            break
    # remove score if x is greater than s
    if len_penaly:
        res -= min(
            max(
                len(x) - len(s),
                0
            ),
            max_value
        )
    return res
