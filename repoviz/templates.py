# -*- coding: utf-8 -*-
"""
内置海报模板定义
定义颜色方案、字体大小、布局参数等
"""


# ============================================================
# 海报尺寸定义
# ============================================================

SIZES = {
    'readme': {
        'width': 800,
        'height': 400,
        'label': 'README (800x400)',
    },
    'social': {
        'width': 1200,
        'height': 630,
        'label': '社交分享 (1200x630)',
    },
}


# ============================================================
# 模板定义
# ============================================================

TEMPLATES = {
    'minimal': {
        'name': '极简风格',
        'description': '白色背景，简洁优雅，适合README嵌入',
        # 背景颜色
        'bg_color': '#ffffff',
        'bg_secondary': '#f6f8fa',
        # 文字颜色
        'text_primary': '#24292f',
        'text_secondary': '#57606a',
        'text_tertiary': '#8b949e',
        # 强调色
        'accent_color': '#0969da',
        'accent_secondary': '#1f6feb',
        # 卡片样式
        'card_bg': '#f6f8fa',
        'card_border': '#d0d7de',
        'card_border_radius': 8,
        # 热力图颜色（从浅到深）
        'heatmap_colors': ['#ebedf0', '#9be9a8', '#40c463', '#30a14e', '#216e39'],
        # 布局参数
        'padding': 24,
        'title_font_size': 18,
        'subtitle_font_size': 12,
        'body_font_size': 11,
        'small_font_size': 9,
        'stat_number_size': 22,
        'stat_label_size': 10,
        'section_gap': 16,
        'element_gap': 8,
        # 分隔线
        'divider_color': '#d0d7de',
        # 进度条
        'bar_height': 8,
        'bar_border_radius': 4,
    },
    'gradient': {
        'name': '渐变风格',
        'description': '深紫到蓝的渐变背景，视觉冲击力强',
        # 背景颜色（渐变起止色）
        'bg_color': '#0d1117',
        'bg_gradient_start': '#1a0533',
        'bg_gradient_end': '#0a1628',
        'bg_secondary': 'rgba(255,255,255,0.05)',
        # 文字颜色
        'text_primary': '#ffffff',
        'text_secondary': '#c9d1d9',
        'text_tertiary': '#8b949e',
        # 强调色
        'accent_color': '#58a6ff',
        'accent_secondary': '#79c0ff',
        'accent_glow': '#1f6feb',
        # 卡片样式
        'card_bg': 'rgba(255,255,255,0.06)',
        'card_border': 'rgba(255,255,255,0.1)',
        'card_border_radius': 10,
        # 热力图颜色
        'heatmap_colors': ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353'],
        # 布局参数
        'padding': 28,
        'title_font_size': 20,
        'subtitle_font_size': 13,
        'body_font_size': 11,
        'small_font_size': 9,
        'stat_number_size': 24,
        'stat_label_size': 10,
        'section_gap': 18,
        'element_gap': 10,
        # 分隔线
        'divider_color': 'rgba(255,255,255,0.1)',
        # 进度条
        'bar_height': 8,
        'bar_border_radius': 4,
    },
    'dark': {
        'name': '暗黑风格',
        'description': '深灰背景，绿色/青色强调，科技感十足',
        # 背景颜色
        'bg_color': '#1e1e2e',
        'bg_secondary': '#2a2a3e',
        # 文字颜色
        'text_primary': '#e0e0e0',
        'text_secondary': '#a0a0b0',
        'text_tertiary': '#6c6c80',
        # 强调色
        'accent_color': '#00d4aa',
        'accent_secondary': '#00b894',
        # 卡片样式
        'card_bg': '#2a2a3e',
        'card_border': '#3a3a50',
        'card_border_radius': 8,
        # 热力图颜色（绿色/青色系）
        'heatmap_colors': ['#2a2a3e', '#0a4a3a', '#0d6b4e', '#10a37f', '#00d4aa'],
        # 布局参数
        'padding': 24,
        'title_font_size': 18,
        'subtitle_font_size': 12,
        'body_font_size': 11,
        'small_font_size': 9,
        'stat_number_size': 22,
        'stat_label_size': 10,
        'section_gap': 16,
        'element_gap': 8,
        # 分隔线
        'divider_color': '#3a3a50',
        # 进度条
        'bar_height': 8,
        'bar_border_radius': 4,
    },
}


def get_template(name):
    """
    获取模板配置
    :param name: 模板名称 (minimal/gradient/dark)
    :return: 模板配置字典
    """
    if name not in TEMPLATES:
        raise ValueError(f"未知模板: {name}，可选模板: {', '.join(TEMPLATES.keys())}")
    return TEMPLATES[name]


def get_size(name):
    """
    获取尺寸配置
    :param name: 尺寸名称 (readme/social)
    :return: 尺寸配置字典
    """
    if name not in SIZES:
        raise ValueError(f"未知尺寸: {name}，可选尺寸: {', '.join(SIZES.keys())}")
    return SIZES[name]


def get_heatmap_level(count, max_count):
    """
    根据提交次数获取热力图颜色等级
    :param count: 当天提交次数
    :param max_count: 最大提交次数
    :return: 颜色等级索引 (0-4)
    """
    if count == 0:
        return 0
    if max_count == 0:
        return 0
    ratio = count / max_count
    if ratio <= 0.25:
        return 1
    elif ratio <= 0.5:
        return 2
    elif ratio <= 0.75:
        return 3
    else:
        return 4


def get_activity_heatmap_color(count, max_count, template_name='gradient'):
    """
    根据提交次数和模板获取热力图颜色
    """
    template = get_template(template_name)
    level = get_heatmap_level(count, max_count)
    return template['heatmap_colors'][level]
