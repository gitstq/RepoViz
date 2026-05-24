# -*- coding: utf-8 -*-
"""
SVG海报渲染器
纯Python字符串拼接生成SVG，零外部依赖
"""

import math
from datetime import timedelta
from .templates import get_template, get_size, get_heatmap_level
from .utils import format_number


class SVGRenderer:
    """
    SVG海报渲染器
    使用纯Python字符串拼接生成精美的SVG可视化海报
    """

    def __init__(self, template_name='gradient', size_name='readme'):
        """
        初始化渲染器
        :param template_name: 模板名称 (minimal/gradient/dark)
        :param size_name: 尺寸名称 (readme/social)
        """
        self.template = get_template(template_name)
        self.size = get_size(size_name)
        self.width = self.size['width']
        self.height = self.size['height']
        self.template_name = template_name
        self._elements = []  # 存储所有SVG元素

    def _add(self, svg_str):
        """添加SVG元素字符串"""
        self._elements.append(svg_str)

    def _escape(self, text):
        """转义XML特殊字符"""
        if text is None:
            return ''
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&apos;'))

    # ============================================================
    # 背景绘制
    # ============================================================

    def _draw_background(self):
        """绘制背景"""
        t = self.template
        if self.template_name == 'gradient':
            # 渐变背景
            self._add(f'''<defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{t['bg_gradient_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{t['bg_gradient_end']};stop-opacity:1" />
    </linearGradient>
  </defs>''')
            self._add(f'<rect width="{self.width}" height="{self.height}" fill="url(#bgGrad)" rx="12"/>')
        else:
            self._add(f'<rect width="{self.width}" height="{self.height}" fill="{t["bg_color"]}" rx="12"/>')

    # ============================================================
    # 文本绘制
    # ============================================================

    def _draw_text(self, x, y, text, size=None, color=None, anchor='start',
                   weight='normal', font_family=None, opacity=1.0):
        """绘制文本"""
        t = self.template
        size = size or t['body_font_size']
        color = color or t['text_primary']
        font_family = font_family or '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif'
        opacity_str = f' opacity="{opacity}"' if opacity < 1.0 else ''
        self._add(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{weight}" '
            f'font-family="{font_family}"{opacity_str}>{self._escape(text)}</text>'
        )

    # ============================================================
    # 统计数字卡片
    # ============================================================

    def _draw_stat_card(self, x, y, width, height, number, label):
        """绘制统计数字卡片"""
        t = self.template
        # 卡片背景
        self._add(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{t["card_border_radius"]}" '
            f'fill="{t["card_bg"]}" stroke="{t["card_border"]}" stroke-width="1"/>'
        )
        # 数字
        self._draw_text(
            x + width / 2, y + height / 2 - 2,
            format_number(number),
            size=t['stat_number_size'],
            color=t['accent_color'],
            anchor='middle',
            weight='bold'
        )
        # 标签
        self._draw_text(
            x + width / 2, y + height - 10,
            label,
            size=t['stat_label_size'],
            color=t['text_secondary'],
            anchor='middle'
        )

    # ============================================================
    # 语言分布条形图
    # ============================================================

    def _draw_language_bars(self, x, y, width, height, languages):
        """绘制语言分布条形图"""
        t = self.template
        if not languages:
            return

        # 标题
        self._draw_text(x, y, "语言分布", size=t['subtitle_font_size'],
                        color=t['text_primary'], weight='bold')

        bar_y = y + 18
        bar_height = 6
        max_bar_width = width - 80
        max_lines = languages[0]['lines'] if languages else 1

        # 显示前5种语言
        display_langs = languages[:5]
        for i, lang in enumerate(display_langs):
            current_y = bar_y + i * (bar_height + 10)

            # 语言名
            self._draw_text(x, current_y + bar_height - 1, lang['name'],
                            size=t['small_font_size'], color=t['text_secondary'])

            # 进度条背景
            bar_x = x + 55
            self._add(
                f'<rect x="{bar_x}" y="{current_y}" width="{max_bar_width}" '
                f'height="{bar_height}" rx="{t["bar_border_radius"]}" '
                f'fill="{t["card_bg"]}"/>'
            )

            # 进度条
            bar_width = max(bar_height, (lang['lines'] / max_lines) * max_bar_width) if max_lines > 0 else 0
            self._add(
                f'<rect x="{bar_x}" y="{current_y}" width="{bar_width}" '
                f'height="{bar_height}" rx="{t["bar_border_radius"]}" '
                f'fill="{lang["color"]}"/>'
            )

            # 百分比
            self._draw_text(
                bar_x + max_bar_width + 8, current_y + bar_height - 1,
                f"{lang['percentage']}%",
                size=t['small_font_size'],
                color=t['text_tertiary'],
                anchor='start'
            )

    # ============================================================
    # 语言分布彩色条
    # ============================================================

    def _draw_language_color_bar(self, x, y, width, height, languages):
        """绘制语言分布彩色条（类似GitHub的语言条）"""
        if not languages:
            return
        total_pct = sum(l['percentage'] for l in languages)
        if total_pct == 0:
            return

        # 绘制圆角矩形裁剪区域
        self._add(
            f'<defs><clipPath id="langBarClip">'
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{height / 2}"/></clipPath></defs>'
        )

        self._add(f'<g clip-path="url(#langBarClip)">')
        current_x = x
        for lang in languages:
            bar_w = (lang['percentage'] / total_pct) * width
            if bar_w > 0.5:
                self._add(
                    f'<rect x="{current_x}" y="{y}" width="{bar_w + 1}" '
                    f'height="{height}" fill="{lang["color"]}"/>'
                )
                current_x += bar_w
        self._add('</g>')

    # ============================================================
    # 提交热力图（紧凑版）
    # ============================================================

    def _draw_commit_heatmap(self, x, y, width, height, heatmap_data):
        """绘制提交热力图（紧凑版，适合海报布局）"""
        t = self.template
        heatmap = heatmap_data['heatmap']
        max_count = heatmap_data['max_count']
        weeks = heatmap_data['weeks']

        # 标题
        self._draw_text(x, y, "提交热力图", size=t['subtitle_font_size'],
                        color=t['text_primary'], weight='bold')

        # 根据可用宽度计算可显示的周数
        available_w = width - 40  # 留出左侧标签和右侧图例空间
        cell_size = 9
        cell_gap = 2
        step = cell_size + cell_gap
        display_weeks = min(weeks, available_w // step)

        heatmap_y = y + 16

        # 星期标签
        day_labels = ['', 'Mon', '', 'Wed', '', 'Fri', '']
        for d in range(7):
            if day_labels[d]:
                self._draw_text(
                    x, heatmap_y + d * step + cell_size - 2,
                    day_labels[d],
                    size=7,
                    color=t['text_tertiary'],
                    opacity=0.7
                )

        heatmap_x = x + 26

        # 绘制热力图格子（只显示最近display_weeks周）
        start_week = weeks - display_weeks
        for week_offset in range(display_weeks):
            week = start_week + week_offset
            for day in range(7):
                cx = heatmap_x + week_offset * step
                cy = heatmap_y + day * step
                count = heatmap.get((week, day), 0)
                level = get_heatmap_level(count, max_count)
                color = t['heatmap_colors'][level]
                self._add(
                    f'<rect x="{cx}" y="{cy}" width="{cell_size}" '
                    f'height="{cell_size}" rx="2" fill="{color}"/>'
                )

        # 图例（放在热力图下方）
        legend_y = heatmap_y + 7 * step + 4
        self._draw_text(heatmap_x, legend_y + cell_size - 2, "少",
                        size=7, color=t['text_tertiary'])
        for i, color in enumerate(t['heatmap_colors']):
            self._add(
                f'<rect x="{heatmap_x + 14 + i * (cell_size + 1)}" y="{legend_y}" '
                f'width="{cell_size}" height="{cell_size}" rx="2" fill="{color}"/>'
            )
        self._draw_text(heatmap_x + 14 + 5 * (cell_size + 1) + 2, legend_y + cell_size - 2, "多",
                        size=7, color=t['text_tertiary'])

        # 返回实际使用的高度
        return 7 * step + 20

    # ============================================================
    # 贡献者排行
    # ============================================================

    def _draw_contributors(self, x, y, width, height, contributors):
        """绘制贡献者排行"""
        t = self.template
        if not contributors:
            return

        # 标题
        self._draw_text(x, y, "贡献者排行", size=t['subtitle_font_size'],
                        color=t['text_primary'], weight='bold')

        item_y = y + 18
        max_commits = contributors[0]['commits'] if contributors else 1

        for i, contributor in enumerate(contributors):
            current_y = item_y + i * 24

            # 排名圆圈
            colors = [t['accent_color'], t['accent_secondary'], t['text_tertiary']]
            circle_color = colors[i] if i < 3 else t['text_tertiary']
            self._add(
                f'<circle cx="{x + 8}" cy="{current_y + 6}" r="7" '
                f'fill="{circle_color}" opacity="0.2"/>'
            )
            self._draw_text(
                x + 8, current_y + 10,
                str(i + 1),
                size=8,
                color=circle_color,
                anchor='middle',
                weight='bold'
            )

            # 贡献者名称
            name = contributor['name']
            if len(name) > 16:
                name = name[:15] + '...'
            self._draw_text(
                x + 22, current_y + 6,
                name,
                size=t['body_font_size'],
                color=t['text_primary'],
                weight='600'
            )

            # 提交数进度条
            bar_x = x + 22
            bar_y = current_y + 12
            bar_max_w = width - 100
            bar_h = 3

            self._add(
                f'<rect x="{bar_x}" y="{bar_y}" width="{bar_max_w}" '
                f'height="{bar_h}" rx="1.5" fill="{t["card_bg"]}"/>'
            )
            bar_w = (contributor['commits'] / max_commits) * bar_max_w if max_commits > 0 else 0
            self._add(
                f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
                f'height="{bar_h}" rx="1.5" fill="{t["accent_color"]}" opacity="0.7"/>'
            )

            # 提交数
            self._draw_text(
                x + width - 10, current_y + 10,
                f"{format_number(contributor['commits'])} commits",
                size=t['small_font_size'],
                color=t['text_tertiary'],
                anchor='end'
            )

    # ============================================================
    # 活跃时段分析
    # ============================================================

    def _draw_activity_patterns(self, x, y, width, height, activity_data):
        """绘制活跃时段分析"""
        t = self.template
        by_day = activity_data['by_day']
        by_hour = activity_data['by_hour']
        max_day = activity_data['max_day_count']
        max_hour = activity_data['max_hour_count']

        # 标题
        self._draw_text(x, y, "活跃时段", size=t['subtitle_font_size'],
                        color=t['text_primary'], weight='bold')

        chart_y = y + 16
        bar_h = 30
        half_w = width // 2 - 5

        # ---- 左半部分：按星期几 ----
        day_bar_w = max(4, (half_w - 10) // 7 - 3)
        for i, day_data in enumerate(by_day):
            bx = x + i * (day_bar_w + 3)
            ratio = day_data['count'] / max_day if max_day > 0 else 0
            bh = max(2, ratio * bar_h)
            by = chart_y + bar_h - bh

            self._add(
                f'<rect x="{bx}" y="{by}" width="{day_bar_w}" height="{bh}" '
                f'rx="2" fill="{t["accent_color"]}" opacity="{0.3 + ratio * 0.7}"/>'
            )
            self._draw_text(
                bx + day_bar_w / 2, chart_y + bar_h + 10,
                day_data['day_cn'][:1],
                size=7,
                color=t['text_tertiary'],
                anchor='middle'
            )

        # ---- 右半部分：按小时（每2小时一组） ----
        hour_x = x + half_w + 10
        hour_bar_w = max(2, (half_w - 10) // 12 - 2)
        for i in range(0, 24, 2):
            hour_data = by_hour[i]
            bx = hour_x + (i // 2) * (hour_bar_w + 2)
            ratio = hour_data['count'] / max_hour if max_hour > 0 else 0
            bh = max(2, ratio * bar_h)
            by = chart_y + bar_h - bh

            self._add(
                f'<rect x="{bx}" y="{by}" width="{hour_bar_w}" height="{bh}" '
                f'rx="1" fill="{t["accent_secondary"]}" opacity="{0.3 + ratio * 0.7}"/>'
            )
            self._draw_text(
                bx + hour_bar_w / 2, chart_y + bar_h + 10,
                f"{i}h",
                size=6,
                color=t['text_tertiary'],
                anchor='middle'
            )

    # ============================================================
    # 主渲染方法
    # ============================================================

    def render(self, data, options=None):
        """
        渲染完整的SVG海报
        :param data: 分析数据字典（来自RepoAnalyzer.analyze_all）
        :param options: 渲染选项字典
        :return: SVG字符串
        """
        if options is None:
            options = {}

        show_heatmap = options.get('show_heatmap', True)
        show_languages = options.get('show_languages', True)
        show_contributors = options.get('show_contributors', True)
        show_activity = options.get('show_activity', True)

        t = self.template
        p = t['padding']

        # 清空元素列表
        self._elements = []

        # 绘制背景
        self._draw_background()

        # ---- 标题区域 ----
        repo_info = data['repo_info']
        title_y = p + 18

        # 仓库名称
        self._draw_text(p, title_y, repo_info['repo_name'],
                        size=t['title_font_size'], color=t['text_primary'],
                        weight='bold')

        # 仓库描述信息
        desc_parts = []
        if repo_info.get('total_commits'):
            desc_parts.append(f"{format_number(repo_info['total_commits'])} 次提交")
        if repo_info.get('repo_age_days') and repo_info['repo_age_days'] > 0:
            age_years = repo_info['repo_age_days'] / 365
            if age_years >= 1:
                desc_parts.append(f"{age_years:.1f} 年历史")
            else:
                desc_parts.append(f"{repo_info['repo_age_days']} 天历史")
        if repo_info.get('total_files'):
            desc_parts.append(f"{format_number(repo_info['total_files'])} 个文件")

        if desc_parts:
            self._draw_text(p, title_y + 16, '  |  '.join(desc_parts),
                            size=t['body_font_size'], color=t['text_secondary'])

        # 语言彩色条
        if show_languages and data.get('languages'):
            lang_bar_y = title_y + 28
            self._draw_language_color_bar(p, lang_bar_y, self.width - 2 * p, 5,
                                          data['languages'])

        # ---- 统计数字卡片 ----
        stats_y = lang_bar_y + 14
        stats = data.get('repo_info', {})
        heatmap_info = data.get('heatmap', {})

        stat_cards = [
            (format_number(stats.get('total_commits', 0)), '总提交数'),
            (format_number(stats.get('total_files', 0)), '总文件数'),
            (format_number(stats.get('total_branches', 0)), '分支数'),
            (format_number(heatmap_info.get('active_days', 0)), '活跃天数'),
        ]

        card_width = (self.width - 2 * p - (len(stat_cards) - 1) * 8) // len(stat_cards)
        card_height = 46

        for i, (number, label) in enumerate(stat_cards):
            cx = p + i * (card_width + 8)
            self._draw_stat_card(cx, stats_y, card_width, card_height, number, label)

        # ---- 内容区域（两栏布局） ----
        content_y = stats_y + card_height + 12
        left_col_x = p
        right_col_x = p + (self.width - 2 * p) // 2 + 8
        col_width = (self.width - 2 * p) // 2 - 8

        # 左栏：语言分布 + 活跃时段
        left_y = content_y

        if show_languages and data.get('languages'):
            self._draw_language_bars(left_col_x, left_y, col_width, 100,
                                     data['languages'])
            left_y += 100

        if show_activity and data.get('activity'):
            self._draw_activity_patterns(left_col_x, left_y, col_width, 60,
                                         data['activity'])

        # 右栏：提交热力图 + 贡献者排行
        right_y = content_y

        if show_heatmap and data.get('heatmap'):
            self._draw_commit_heatmap(right_col_x, right_y, col_width, 120,
                                      data['heatmap'])
            right_y += 120

        if show_contributors and data.get('contributors'):
            self._draw_contributors(right_col_x, right_y, col_width, 120,
                                    data['contributors'])

        # ---- 底部水印 ----
        watermark_y = self.height - 12
        self._draw_text(
            self.width - p, watermark_y,
            "Generated by RepoViz",
            size=8,
            color=t['text_tertiary'],
            anchor='end',
            opacity=0.5
        )

        # 组装完整SVG
        svg_content = '\n'.join(self._elements)
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">
  {svg_content}
</svg>'''

    def render_to_file(self, data, filepath, options=None):
        """
        渲染SVG并保存到文件
        :param data: 分析数据
        :param filepath: 输出文件路径
        :param options: 渲染选项
        """
        svg_content = self.render(data, options)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
