print("testing")
import pytest
from unittest.mock import patch
from app.utils.get_stock_daily import get_stock_daily
from app.schemas.stock_daily import StockDailyItem
from datetime import date

# 模拟 Tushare API 的返回结果
@pytest.fixture
def mock_tushare_response():
    return [
        {
            "ts_code": "000001.SZ",
            "stock_code": "000001",
            "trade_date": date(2024, 4, 10),
            "open": 10.5,
            "high": 11.0,
            "low": 10.2,
            "close": 10.8,
            "pre_close": 10.3,
            "change": 0.5,
            "pct_chg": 4.85,
            "vol": 10000,
            "amount": 200000
        },
        {
            "ts_code": "000001.SZ",
            "stock_code": "000001",
            "trade_date": date(2024, 4, 11),
            "open": 10.8,
            "high": 11.1,
            "low": 10.4,
            "close": 10.9,
            "pre_close": 10.8,
            "change": 0.1,
            "pct_chg": 0.93,
            "vol": 12000,
            "amount": 220000
        }
    ]

# 测试 get_stock_daily 函数
def test_get_stock_daily(mock_tushare_response):
    # 模拟 Tushare API 返回的结果
    with patch("app.utils.get_stock_daily.pro.daily", return_value=mock_tushare_response):
        result = get_stock_daily("000001", "20240401", "20240411")
        
        # 检查返回结果
        assert len(result) == 2
        assert isinstance(result[0], StockDailyItem)  # 确保返回的对象是 StockDailyItem 实例
        assert result[0].ts_code == "000001.SZ"
        assert result[0].stock_code == "000001"
        assert result[0].trade_date == date(2024, 4, 10)
        assert result[0].close == 10.8
        assert result[1].trade_date == date(2024, 4, 11)
        assert result[1].pct_chg == 0.93
print("test ended")