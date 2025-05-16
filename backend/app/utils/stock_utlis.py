def get_stock_exchange_code(code: str) -> str:
    """
    根据股票代码格式判断所属交易所，并返回相应的市场标识符（适用于 AkShare）。
    
    Args:
        code (str): 股票代码，纯数字，例如：'600000', '000001', '300750'
    
    Returns:
        str: 股票代码对应的股票交易所后缀后缀（例如 'SH'、'SZ'）
    
    Raises:
        ValueError: 当股票代码格式不正确或无法识别时抛出
    """
    code = str(code).strip()

    # 验证是否为纯数字
    if not code.isdigit():
        raise ValueError("股票代码必须为纯数字")
    
    if len(code) != 6:
        raise ValueError("股票代码长度应为6位")
    
    # 根据股票代码前缀判断所属交易所
    if code.startswith(('6', '5', '900')):
        return "SH"  # 上海证券交易所
    elif code.startswith(('000', '001', '002', '003', '300')):
        return "SZ"  # 深圳证券交易所
    elif code.startswith(('920')):
        return "BJ"
    else:
        raise ValueError(f"无法识别的股票代码前缀: {code}")
    

def get_exchange_name_by_code(exchange_code: str) -> str:
    """
    根据交易所代码标识符（如 'SH', 'SZ', 'BJ'）返回交易所的全称。
    
    Args:
        exchange_code (str): 交易所代码标识符，例如 'SH'、'SZ'、'BJ'
    
    Returns:
        str: 交易所的全称，例如 '上海证券交易所'、'深圳证券交易所'、'北京证券交易所'
    
    Raises:
        ValueError: 如果输入的交易所代码不合法或无法识别时抛出
    """
    exchange_code = exchange_code.strip().upper()

    # 判断交易所代码并返回全称
    if exchange_code == "SH":
        return "上海证券交易所"
    elif exchange_code == "SZ":
        return "深圳证券交易所"
    elif exchange_code == "BJ":
        return "北京证券交易所"
    else:
        raise ValueError(f"无法识别的交易所代码: {exchange_code}")


def format_stock_code_for_xueqiu(code: str) -> str:
    """
    格式化股票代码，返回带有市场后缀的标准格式（适用于Akshare的雪球接口）。
    
    Args:
        code (str): 股票代码，纯数字，例如：'600000', '000001', '300750'
    
    Returns:
        str: 带有市场前缀的股票代码，例如 'SZ600000' 或 'SZ000001'
    
    Raises:
        ValueError: 如果股票代码格式不正确或无法识别时抛出
    """
    code = str(code).strip()
    
    # 调用 get_stock_exchange 获取市场后缀
    exchange = get_stock_exchange_code(code)
    
    return f"{exchange}{code}"  

def check_stock_format(code: str) -> bool:
    """
    检查股票代码格式是否正确。
    
    Args:
        code (str): 股票代码，纯数字，例如：'600000', '000001', '300750'
    
    Returns:
        bool: 如果格式正确返回 True，否则返回 False
    """
    try:
        get_stock_exchange_code(code)
        return True
    except ValueError:
        return False
