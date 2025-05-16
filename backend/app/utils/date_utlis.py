from datetime import datetime   
def check_date_format(date_str: str) -> bool:
    return isinstance(date_str, str) and len(date_str) == 8 and date_str.isdigit()

def get_today() -> str:
        """
        获取今天的日期，格式为 YYYYMMDD
        """
        return datetime.now().strftime("%Y%m%d")

def parse_date(date:str) -> datetime.date:
    """
    将 YYYYMMDD 格式的字符串转换为 datetime.date 类型
    """
    return datetime.strptime(date, "%Y%m%d").date()