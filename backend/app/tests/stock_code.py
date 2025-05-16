import sys
print(sys.path)

from app.utils.stock_utlis import is_index_code,format_stock_code

import unittest



class TestStockCode(unittest.TestCase):
    def test_format_stock_code_ashare(self):
        """测试A股代码格式化"""
        test_cases = {
            '600000': '600000.SH',  # 上交所
            '000001': '000001.SZ',  # 深交所主板
            '002001': '002001.SZ',  # 深交所中小板
            '300750': '300750.SZ',  # 创业板
            '688001': '688001.SH',  # 科创板
            '830999': '830999.BJ',  # 北交所
        }
        for input_code, expected in test_cases.items():
            with self.subTest(input_code=input_code):
                self.assertEqual(format_stock_code(input_code), expected)

    def test_format_stock_code_hk(self):
        """测试港股代码格式化"""
        test_cases = {
            '00700': '00700.HK',  # 腾讯控股
            '09988': '09988.HK',  # 阿里巴巴
        }
        for input_code, expected in test_cases.items():
            with self.subTest(input_code=input_code):
                self.assertEqual(format_stock_code(input_code), expected)

    def test_format_stock_code_invalid(self):
        """测试无效股票代码"""
        invalid_codes = [
            'abc123',     # 非数字
            '12345678',   # 长度过长
            '1234',       # 长度过短
            '123456',     # 无效前缀
        ]
        for code in invalid_codes:
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    format_stock_code(code)

    def test_is_index_code_ashare(self):
        """测试A股指数代码判断"""
        index_codes = {
            '000001': True,   # 上证指数
            '399001': True,   # 深证成指
            '399006': True,   # 创业板指
            '000300': True,   # 沪深300
            '600000': False,  # 浦发银行
            '000002': True,   # 上证A股指数
            '899001': True,   # 北交所指数
        }
        for code, expected in index_codes.items():
            with self.subTest(code=code):
                self.assertEqual(is_index_code(code), expected)

    def test_is_index_code_hk(self):
        """测试港股指数代码判断"""
        index_codes = {
            '00001': True,   # 恒生指数
            '00002': True,   # 恒生中国企业指数
            '00700': False,  # 腾讯控股（股票）
        }
        for code, expected in index_codes.items():
            with self.subTest(code=code):
                self.assertEqual(is_index_code(code), expected)

    def test_is_index_code_invalid(self):
        """测试无效指数代码"""
        invalid_codes = [
            'HSI',        # 非数字
            '1234567',    # 长度过长
            '1234',       # 长度过短
        ]
        for code in invalid_codes:
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    is_index_code(code)

if __name__ == '__main__':
    unittest.main()