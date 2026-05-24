# -*- coding: utf-8 -*-
"""
工具函数模块
提供颜色转换、数字格式化、语言映射等通用工具
"""

import os
import math
from datetime import datetime, timedelta


# ============================================================
# 数字格式化
# ============================================================

def format_number(num):
    """
    将数字格式化为人类可读的短格式
    例如: 1500 -> 1.5k, 2500000 -> 2.5M
    """
    if num is None:
        return "0"
    num = int(num)
    if num < 1000:
        return str(num)
    elif num < 1_000_000:
        value = num / 1000.0
        if value == int(value):
            return f"{int(value)}k"
        return f"{value:.1f}k"
    elif num < 1_000_000_000:
        value = num / 1_000_000.0
        if value == int(value):
            return f"{int(value)}M"
        return f"{value:.1f}M"
    else:
        value = num / 1_000_000_000.0
        if value == int(value):
            return f"{int(value)}B"
        return f"{value:.1f}B"


# ============================================================
# 颜色工具
# ============================================================

def hex_to_rgb(hex_color):
    """
    将十六进制颜色转换为RGB元组
    例如: "#ff6600" -> (255, 102, 0)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """
    将RGB值转换为十六进制颜色
    例如: (255, 102, 0) -> "#ff6600"
    """
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def rgb_to_hsl(r, g, b):
    """
    将RGB转换为HSL色彩空间
    返回值范围: H(0-360), S(0-100), L(0-100)
    """
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2.0

    if max_c == min_c:
        h = s = 0.0
    else:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6.0 if g < b else 0.0)
        elif max_c == g:
            h = (b - r) / d + 2.0
        else:
            h = (r - g) / d + 4.0
        h *= 60.0

    return h, s * 100.0, l * 100.0


def hsl_to_rgb(h, s, l):
    """
    将HSL转换为RGB色彩空间
    输入范围: H(0-360), S(0-100), L(0-100)
    """
    s /= 100.0
    l /= 100.0

    c = (1.0 - abs(2.0 * l - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2 - 1.0))
    m = l - c / 2.0

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (r + m) * 255, (g + m) * 255, (b + m) * 255


def interpolate_color(color1, color2, factor):
    """
    在两个颜色之间进行线性插值
    factor: 0.0返回color1, 1.0返回color2
    """
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = r1 + (r2 - r1) * factor
    g = g1 + (g2 - g1) * factor
    b = b1 + (b2 - b1) * factor
    return rgb_to_hex(r, g, b)


def adjust_brightness(hex_color, factor):
    """
    调整颜色亮度
    factor > 1.0 变亮, factor < 1.0 变暗
    """
    r, g, b = hex_to_rgb(hex_color)
    r = min(255, max(0, r * factor))
    g = min(255, max(0, g * factor))
    b = min(255, max(0, b * factor))
    return rgb_to_hex(r, g, b)


def hex_to_rgba(hex_color, alpha=1.0):
    """
    将十六进制颜色转换为带透明度的RGBA字符串
    """
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({int(r)},{int(g)},{int(b)},{alpha})"


# ============================================================
# 文件扩展名到编程语言的映射
# ============================================================

EXTENSION_LANGUAGE_MAP = {
    # Python
    '.py': 'Python',
    '.pyw': 'Python',
    '.pyx': 'Python',
    '.pyd': 'Python',
    # JavaScript
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.mjs': 'JavaScript',
    '.cjs': 'JavaScript',
    # TypeScript
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    # Java
    '.java': 'Java',
    '.jar': 'Java',
    # C
    '.c': 'C',
    '.h': 'C',
    # C++
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.hpp': 'C++',
    '.hxx': 'C++',
    # C#
    '.cs': 'C#',
    # Go
    '.go': 'Go',
    # Rust
    '.rs': 'Rust',
    # Ruby
    '.rb': 'Ruby',
    '.erb': 'Ruby',
    # PHP
    '.php': 'PHP',
    # Swift
    '.swift': 'Swift',
    # Kotlin
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    # Dart
    '.dart': 'Dart',
    # Scala
    '.scala': 'Scala',
    # R
    '.r': 'R',
    '.R': 'R',
    # Shell
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.fish': 'Shell',
    # HTML/CSS
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SCSS',
    '.less': 'Less',
    # Web相关
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    # 配置文件
    '.json': 'JSON',
    '.yaml': 'YAML',
    '.yml': 'YAML',
    '.toml': 'TOML',
    '.xml': 'XML',
    '.ini': 'INI',
    '.cfg': 'INI',
    '.conf': 'Config',
    # Markdown/文档
    '.md': 'Markdown',
    '.rst': 'reStructuredText',
    '.txt': 'Text',
    '.pdf': 'PDF',
    # SQL
    '.sql': 'SQL',
    # Lua
    '.lua': 'Lua',
    # Perl
    '.pl': 'Perl',
    '.pm': 'Perl',
    # Haskell
    '.hs': 'Haskell',
    # Elixir
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    # Clojure
    '.clj': 'Clojure',
    '.cljs': 'Clojure',
    # Docker
    '.dockerfile': 'Dockerfile',
    # Makefile
    '.mk': 'Makefile',
    # TeX
    '.tex': 'TeX',
    '.latex': 'TeX',
    # Jupyter
    '.ipynb': 'Jupyter Notebook',
    # 图形
    '.svg': 'SVG',
    '.png': 'PNG',
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.ico': 'ICO',
    # 其他
    '.lock': 'Lock',
    '.log': 'Log',
    '.map': 'Source Map',
    '.wasm': 'WebAssembly',
}


# GitHub官方语言颜色
LANGUAGE_COLORS = {
    'Python': '#3572A5',
    'JavaScript': '#f1e05a',
    'TypeScript': '#3178c6',
    'Java': '#b07219',
    'C': '#555555',
    'C++': '#f34b7d',
    'C#': '#178600',
    'Go': '#00ADD8',
    'Rust': '#dea584',
    'Ruby': '#701516',
    'PHP': '#4F5D95',
    'Swift': '#F05138',
    'Kotlin': '#A97BFF',
    'Dart': '#00B4AB',
    'Scala': '#c22d40',
    'R': '#198CE7',
    'Shell': '#89e051',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'SCSS': '#c6538c',
    'Less': '#1e40af',
    'Vue': '#41b883',
    'Svelte': '#ff3e00',
    'JSON': '#292929',
    'YAML': '#cb171e',
    'Markdown': '#083fa1',
    'SQL': '#e38c00',
    'Lua': '#000080',
    'Perl': '#0298c3',
    'Haskell': '#5e5086',
    'Elixir': '#6e4a7e',
    'Clojure': '#db5855',
    'Dockerfile': '#384d54',
    'Makefile': '#427819',
    'TeX': '#3D6117',
    'Jupyter Notebook': '#DA5B0B',
    'SVG': '#ff9900',
    'Text': '#999999',
    'Other': '#8b8b8b',
}

# 默认颜色（当语言不在映射中时使用）
DEFAULT_LANGUAGE_COLOR = '#8b8b8b'


def get_language_color(language):
    """获取语言对应的颜色"""
    return LANGUAGE_COLORS.get(language, DEFAULT_LANGUAGE_COLOR)


def get_language_from_extension(ext):
    """根据文件扩展名获取编程语言名称"""
    # 统一转小写处理
    ext_lower = ext.lower()
    return EXTENSION_LANGUAGE_MAP.get(ext_lower, 'Other')


# ============================================================
# 日期处理工具
# ============================================================

def get_date_range_weeks(weeks=52):
    """
    获取过去N周的日期范围
    返回从(weeks*7)天前到今天的日期列表
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=weeks * 7)
    return start_date, end_date


def date_to_week_column(date_obj, start_date):
    """
    将日期转换为热力图中的(周, 列)坐标
    返回 (week_index, day_of_week)
    day_of_week: 0=周一, 6=周日
    """
    delta = (date_obj - start_date).days
    week_index = delta // 7
    day_of_week = date_obj.weekday()  # 0=周一, 6=周日
    return week_index, day_of_week


# ============================================================
# 文件系统工具
# ============================================================

# 需要排除的目录名
EXCLUDED_DIRS = {
    '.git', '.svn', '.hg',          # 版本控制
    'node_modules',                 # Node.js依赖
    'venv', 'virtualenv', '.venv',  # Python虚拟环境
    '__pycache__', '.pytest_cache', # Python缓存
    '.tox',                         # tox测试环境
    'dist', 'build',                # 构建目录
    '.eggs', '*.egg-info',          # Python打包
    '.mypy_cache',                  # mypy缓存
    '.idea', '.vscode',             # IDE配置
    'vendor', 'third_party',        # 第三方代码
    '.next', '.nuxt',               # 框架构建目录
    'coverage', '.coverage',        # 测试覆盖率
    '.nyc_output',                  # nyc覆盖率
    'bower_components',             # Bower依赖
    '.terraform',                   # Terraform
    '.serverless',                  # Serverless框架
    'env', '.env',                  # 环境目录
    'site-packages',                # Python包
    'target', 'out',                # 编译输出
    'bin', 'obj',                   # 编译中间文件
    '.gradle', '.mvn',              # 构建工具
    'cmake-build-debug',            # CMake
    'Pods',                         # CocoaPods
    '.bundle',                      # Ruby Bundler
}


def is_excluded_dir(dir_name):
    """检查目录是否在排除列表中"""
    return dir_name in EXCLUDED_DIRS


def count_lines_in_file(filepath):
    """
    统计文件行数
    如果文件是二进制文件或读取失败，返回0
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (IOError, OSError):
        return 0


def is_binary_file(filepath):
    """简单判断文件是否为二进制文件"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                return True
        return False
    except (IOError, OSError):
        return True


def is_image_file(filepath):
    """判断文件是否为图片文件"""
    image_exts = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp'}
    _, ext = os.path.splitext(filepath)
    return ext.lower() in image_exts


def is_lock_file(filepath):
    """判断是否为锁文件"""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in {'.lock', '.pyc', '.pyo', '.class', '.o', '.so', '.dylib', '.dll'}
