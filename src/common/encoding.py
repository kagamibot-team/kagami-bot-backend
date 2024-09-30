DEFAULT_ENCODING = (
    "一二三四五六七八"
    "九十甲乙丙丁戊己"
    "庚辛壬癸子丑寅卯"
    "辰巳午未申酉戌亥"
    "鼠牛虎兔龙蛇马羊"
    "猴鸡狗猪坤艮坎巽"
    "震离兑乾地山水风"
    "雷火泽天月日阴阳"
)


def bytes_to_encoding(data: bytes, encoding: str = DEFAULT_ENCODING):
    """将字节数据转换为指定编码。

    Args:
        data (bytes): 要转换的字节数据。
        encoding (str, optional): 自定义编码字符串。默认为 DEFAULT_ENCODING。

    Returns:
        str: 输入字节的编码字符串表示。
    """
    result = ""
    assert len(encoding) > 1, "编码字符串必须包含至少两个字符。"
    _data = int.from_bytes(data)
    while _data > 0:
        result = encoding[_data % len(encoding)] + result
        _data //= len(encoding)
    return result if result else encoding[0]


def encoding_to_bytes(encoded_str: str, encoding: str = DEFAULT_ENCODING) -> bytes:
    """将编码字符串转换回原始字节表示。

    Args:
        encoded_str (str): 要转换回的编码字符串。
        encoding (str, optional): 自定义编码字符串。默认为 DEFAULT_ENCODING。

    Returns:
        bytes: 编码字符串的字节表示。
    """
    _data = 0
    for char in encoded_str:
        _data = _data * len(encoding) + encoding.index(char)
    return _data.to_bytes((_data.bit_length() + 7) // 8, byteorder="big")
