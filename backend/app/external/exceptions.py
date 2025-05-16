class StockExternalDataError(Exception):
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception

class StockExternalDataProcessingError(Exception):
    """处理股票数据时发生错误"""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception