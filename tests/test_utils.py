# -*- coding: utf-8 -*-
"""
utils模块测试
测试工具函数（颜色转换、数字格式化等）
"""

import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repoviz.utils import (
    format_number,
    hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb,
    interpolate_color, adjust_brightness, hex_to_rgba,
    get_language_from_extension, get_language_color,
    is_excluded_dir, get_date_range_weeks, date_to_week_column,
    is_binary_file, is_image_file, is_lock_file,
    count_lines_in_file,
    EXTENSION_LANGUAGE_MAP, LANGUAGE_COLORS,
)
from repoviz.templates import (
    get_template, get_size, get_heatmap_level, get_activity_heatmap_color,
    TEMPLATES, SIZES,
)


class TestFormatNumber:
    """测试数字格式化"""

    def test_small_numbers(self):
        assert format_number(0) == "0"
        assert format_number(42) == "42"
        assert format_number(999) == "999"

    def test_thousands(self):
        assert format_number(1000) == "1k"
        assert format_number(1500) == "1.5k"
        assert format_number(999999) == "999.9k"

    def test_millions(self):
        assert format_number(1_000_000) == "1M"
        assert format_number(2_500_000) == "2.5M"

    def test_billions(self):
        assert format_number(1_000_000_000) == "1B"
        assert format_number(3_500_000_000) == "3.5B"

    def test_none_input(self):
        assert format_number(None) == "0"


class TestColorConversion:
    """测试颜色转换"""

    def test_hex_to_rgb(self):
        assert hex_to_rgb("#ff0000") == (255, 0, 0)
        assert hex_to_rgb("#00ff00") == (0, 255, 0)
        assert hex_to_rgb("#0000ff") == (0, 0, 255)
        assert hex_to_rgb("ff6600") == (255, 102, 0)

    def test_rgb_to_hex(self):
        assert rgb_to_hex(255, 0, 0) == "#ff0000"
        assert rgb_to_hex(0, 255, 0) == "#00ff00"
        assert rgb_to_hex(0, 0, 255) == "#0000ff"

    def test_hex_rgb_roundtrip(self):
        """测试十六进制和RGB之间的往返转换"""
        colors = ["#ff6600", "#3572A5", "#f1e05a", "#000000", "#ffffff"]
        for color in colors:
            r, g, b = hex_to_rgb(color)
            assert rgb_to_hex(r, g, b) == color

    def test_rgb_to_hsl(self):
        """测试RGB到HSL的转换"""
        # 红色
        h, s, l = rgb_to_hsl(255, 0, 0)
        assert h == 0.0
        assert s == 100.0
        assert l == 50.0

        # 白色
        h, s, l = rgb_to_hsl(255, 255, 255)
        assert s == 0.0
        assert l == 100.0

        # 黑色
        h, s, l = rgb_to_hsl(0, 0, 0)
        assert s == 0.0
        assert l == 0.0

    def test_hsl_to_rgb(self):
        """测试HSL到RGB的转换"""
        # 红色
        r, g, b = hsl_to_rgb(0, 100, 50)
        assert abs(r - 255) < 1
        assert abs(g) < 1
        assert abs(b) < 1

    def test_hsl_rgb_roundtrip(self):
        """测试HSL和RGB之间的往返转换"""
        test_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (128, 128, 128),
            (255, 128, 0),
        ]
        for r, g, b in test_colors:
            h, s, l = rgb_to_hsl(r, g, b)
            r2, g2, b2 = hsl_to_rgb(h, s, l)
            assert abs(r - r2) < 2
            assert abs(g - g2) < 2
            assert abs(b - b2) < 2

    def test_interpolate_color(self):
        """测试颜色插值"""
        # 从黑色到白色，中间点应该是灰色
        mid = interpolate_color("#000000", "#ffffff", 0.5)
        r, g, b = hex_to_rgb(mid)
        assert 120 <= r <= 135
        assert 120 <= g <= 135
        assert 120 <= b <= 135

        # factor=0返回第一个颜色
        assert interpolate_color("#ff0000", "#0000ff", 0.0) == "#ff0000"
        # factor=1返回第二个颜色
        assert interpolate_color("#ff0000", "#0000ff", 1.0) == "#0000ff"

    def test_adjust_brightness(self):
        """测试亮度调整"""
        # 变亮
        brighter = adjust_brightness("#808080", 2.0)
        r, g, b = hex_to_rgb(brighter)
        assert r > 128
        assert g > 128
        assert b > 128

        # 变暗
        darker = adjust_brightness("#808080", 0.5)
        r, g, b = hex_to_rgb(darker)
        assert r < 128
        assert g < 128
        assert b < 128

    def test_hex_to_rgba(self):
        """测试RGBA转换"""
        result = hex_to_rgba("#ff0000", 0.5)
        assert "rgba(255,0,0,0.5)" == result


class TestLanguageMapping:
    """测试语言映射"""

    def test_common_languages(self):
        assert get_language_from_extension('.py') == 'Python'
        assert get_language_from_extension('.js') == 'JavaScript'
        assert get_language_from_extension('.ts') == 'TypeScript'
        assert get_language_from_extension('.java') == 'Java'
        assert get_language_from_extension('.go') == 'Go'
        assert get_language_from_extension('.rs') == 'Rust'

    def test_case_insensitive(self):
        assert get_language_from_extension('.PY') == 'Python'
        assert get_language_from_extension('.Js') == 'JavaScript'

    def test_unknown_extension(self):
        assert get_language_from_extension('.xyz123') == 'Other'

    def test_language_colors(self):
        """测试语言颜色映射"""
        assert get_language_color('Python') == '#3572A5'
        assert get_language_color('JavaScript') == '#f1e05a'
        # 未知语言返回默认颜色
        assert get_language_color('UnknownLanguage') == '#8b8b8b'


class TestExcludedDirs:
    """测试目录排除"""

    def test_common_excluded_dirs(self):
        assert is_excluded_dir('.git')
        assert is_excluded_dir('node_modules')
        assert is_excluded_dir('venv')
        assert is_excluded_dir('__pycache__')
        assert is_excluded_dir('.venv')

    def test_non_excluded_dirs(self):
        assert not is_excluded_dir('src')
        assert not is_excluded_dir('lib')
        assert not is_excluded_dir('tests')


class TestDateUtils:
    """测试日期工具"""

    def test_get_date_range_weeks(self):
        start, end = get_date_range_weeks(52)
        assert (end - start).days == 52 * 7

    def test_date_to_week_column(self):
        start = datetime(2024, 1, 1).date()
        # 第一天应该是第0周，周一(weekday=0)
        week, day = date_to_week_column(start, start)
        assert week == 0
        assert day == 0  # 2024-01-01是周一

        # 7天后应该是第1周
        next_week = start + timedelta(days=7)
        week, day = date_to_week_column(next_week, start)
        assert week == 1


class TestTemplates:
    """测试模板系统"""

    def test_get_template(self):
        for name in ['minimal', 'gradient', 'dark']:
            t = get_template(name)
            assert 'bg_color' in t
            assert 'text_primary' in t
            assert 'accent_color' in t
            assert 'heatmap_colors' in t
            assert len(t['heatmap_colors']) == 5

    def test_get_template_invalid(self):
        with pytest.raises(ValueError):
            get_template('nonexistent')

    def test_get_size(self):
        for name in ['readme', 'social']:
            s = get_size(name)
            assert 'width' in s
            assert 'height' in s

    def test_get_size_invalid(self):
        with pytest.raises(ValueError):
            get_size('invalid_size')

    def test_get_heatmap_level(self):
        assert get_heatmap_level(0, 10) == 0
        assert get_heatmap_level(1, 10) == 1
        assert get_heatmap_level(3, 10) == 2
        assert get_heatmap_level(8, 10) == 4

    def test_get_heatmap_level_zero_max(self):
        assert get_heatmap_level(0, 0) == 0
        assert get_heatmap_level(5, 0) == 0


class TestFileUtils:
    """测试文件工具函数"""

    def test_is_image_file(self, tmp_path):
        img = tmp_path / "test.png"
        img.write_text("fake")
        assert is_image_file(str(img))

        not_img = tmp_path / "test.py"
        not_img.write_text("print('hello')")
        assert not is_image_file(str(not_img))

    def test_is_lock_file(self, tmp_path):
        lock = tmp_path / "test.lock"
        lock.write_text("content")
        assert is_lock_file(str(lock))

        not_lock = tmp_path / "test.py"
        not_lock.write_text("print('hello')")
        assert not is_lock_file(str(not_lock))

    def test_count_lines_in_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3\n")
        assert count_lines_in_file(str(f)) == 3

    def test_count_lines_nonexistent(self):
        assert count_lines_in_file("/nonexistent/file.txt") == 0
