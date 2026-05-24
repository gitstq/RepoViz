# -*- coding: utf-8 -*-
"""
PNG海报渲染器
基于matplotlib渲染PNG版本的海报
"""

import math
from .templates import get_template, get_size, get_heatmap_level
from .utils import format_number


class PNGRenderer:
    """
    PNG海报渲染器
    使用matplotlib将分析数据渲染为PNG图片
    """

    def __init__(self, template_name='gradient', size_name='readme', dpi=300):
        """
        初始化渲染器
        :param template_name: 模板名称 (minimal/gradient/dark)
        :param size_name: 尺寸名称 (readme/social)
        :param dpi: 输出DPI
        """
        self.template = get_template(template_name)
        self.size = get_size(size_name)
        self.width = self.size['width']
        self.height = self.size['height']
        self.template_name = template_name
        self.dpi = dpi

    def _hex_to_rgb_tuple(self, hex_color):
        """将十六进制颜色转换为matplotlib可用的RGB元组(0-1范围)"""
        hex_color = hex_color.lstrip('#')
        if hex_color.startswith('rgba') or hex_color.startswith('rgb'):
            # 处理rgba/rgb格式
            import re
            match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', hex_color)
            if match:
                return (int(match.group(1)) / 255,
                        int(match.group(2)) / 255,
                        int(match.group(3)) / 255)
        return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))

    def render(self, data, options=None):
        """
        渲染PNG海报
        :param data: 分析数据字典
        :param options: 渲染选项
        :return: matplotlib Figure对象
        """
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import FancyBboxPatch
        import numpy as np

        if options is None:
            options = {}

        show_heatmap = options.get('show_heatmap', True)
        show_languages = options.get('show_languages', True)
        show_contributors = options.get('show_contributors', True)
        show_activity = options.get('show_activity', True)

        t = self.template

        # 创建图形
        fig_w = self.width / 100.0  # 转换为英寸
        fig_h = self.height / 100.0
        fig, ax = plt.subplots(1, 1, figsize=(fig_w, fig_h), dpi=self.dpi)
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, self.height)
        ax.axis('off')

        # ---- 背景 ----
        if self.template_name == 'gradient':
            # 渐变背景
            gradient = np.linspace(0, 1, 256).reshape(1, -1)
            gradient = np.vstack([gradient] * 256)
            start_rgb = self._hex_to_rgb_tuple(t['bg_gradient_start'])
            end_rgb = self._hex_to_rgb_tuple(t['bg_gradient_end'])
            from matplotlib.colors import LinearSegmentedColormap
            cmap = LinearSegmentedColormap.from_list(
                'bg', [start_rgb, end_rgb]
            )
            ax.imshow(gradient, aspect='auto', cmap=cmap,
                      extent=[0, self.width, 0, self.height], zorder=0)
        else:
            bg_rgb = self._hex_to_rgb_tuple(t['bg_color'])
            fig.patch.set_facecolor(bg_rgb)
            ax.set_facecolor(bg_rgb)

        # 颜色辅助
        text_primary = self._hex_to_rgb_tuple(t['text_primary'])
        text_secondary = self._hex_to_rgb_tuple(t['text_secondary'])
        text_tertiary = self._hex_to_rgb_tuple(t['text_tertiary'])
        accent = self._hex_to_rgb_tuple(t['accent_color'])
        card_bg = self._hex_to_rgb_tuple(t['card_bg']) if not t['card_bg'].startswith('rgba') else (1, 1, 1, 0.06)
        card_border = self._hex_to_rgb_tuple(t['card_border']) if not t['card_border'].startswith('rgba') else (1, 1, 1, 0.1)

        p = t['padding']
        repo_info = data.get('repo_info', {})

        # ---- 标题 ----
        title_y = self.height - p - 20
        ax.text(p, title_y, repo_info.get('repo_name', 'Repository'),
                fontsize=t['title_font_size'], fontweight='bold',
                color=text_primary, va='top', fontfamily='sans-serif')

        # 描述
        desc_parts = []
        if repo_info.get('total_commits'):
            desc_parts.append(f"{format_number(repo_info['total_commits'])} commits")
        if repo_info.get('repo_age_days', 0) > 0:
            age_years = repo_info['repo_age_days'] / 365
            if age_years >= 1:
                desc_parts.append(f"{age_years:.1f} years")
            else:
                desc_parts.append(f"{repo_info['repo_age_days']} days")
        if repo_info.get('total_files'):
            desc_parts.append(f"{format_number(repo_info['total_files'])} files")

        if desc_parts:
            ax.text(p, title_y - 18, '  |  '.join(desc_parts),
                    fontsize=t['body_font_size'],
                    color=text_secondary, va='top', fontfamily='sans-serif')

        # ---- 语言彩色条 ----
        if show_languages and data.get('languages'):
            lang_bar_y = title_y - 36
            lang_bar_h = 6
            languages = data['languages']
            total_pct = sum(l['percentage'] for l in languages)
            if total_pct > 0:
                current_x = p
                bar_total_w = self.width - 2 * p
                for lang in languages:
                    bar_w = (lang['percentage'] / total_pct) * bar_total_w
                    if bar_w > 0.5:
                        lang_color = self._hex_to_rgb_tuple(lang['color'])
                        rect = patches.FancyBboxPatch(
                            (current_x, lang_bar_y), bar_w + 1, lang_bar_h,
                            boxstyle=f"round,pad=0,rounding_size={lang_bar_h / 2}",
                            facecolor=lang_color, edgecolor='none', zorder=2
                        )
                        ax.add_patch(rect)
                        current_x += bar_w

        # ---- 统计卡片 ----
        stats_y = title_y - 56
        heatmap_info = data.get('heatmap', {})

        stat_cards = [
            (format_number(repo_info.get('total_commits', 0)), 'Commits'),
            (format_number(repo_info.get('total_files', 0)), 'Files'),
            (format_number(repo_info.get('total_branches', 0)), 'Branches'),
            (format_number(heatmap_info.get('active_days', 0)), 'Active Days'),
        ]

        card_w = (self.width - 2 * p - (len(stat_cards) - 1) * 10) / len(stat_cards)
        card_h = 52

        for i, (number, label) in enumerate(stat_cards):
            cx = p + i * (card_w + 10)
            # 卡片背景
            if isinstance(card_bg, tuple) and len(card_bg) == 4:
                bg_color = card_bg
            else:
                bg_color = card_bg
            rect = FancyBboxPatch(
                (cx, stats_y - card_h), card_w, card_h,
                boxstyle=f"round,pad=0,rounding_size={t['card_border_radius']}",
                facecolor=bg_color if not isinstance(bg_color, tuple) or len(bg_color) == 3 else bg_color,
                edgecolor=card_border if not isinstance(card_border, tuple) or len(card_border) == 3 else card_border,
                linewidth=1, zorder=2
            )
            ax.add_patch(rect)
            # 数字
            ax.text(cx + card_w / 2, stats_y - card_h / 2 + 2, number,
                    fontsize=t['stat_number_size'], fontweight='bold',
                    color=accent, ha='center', va='center', zorder=3,
                    fontfamily='sans-serif')
            # 标签
            ax.text(cx + card_w / 2, stats_y - card_h + 10, label,
                    fontsize=t['stat_label_size'],
                    color=text_secondary, ha='center', va='bottom', zorder=3,
                    fontfamily='sans-serif')

        # ---- 左栏：语言分布 ----
        content_y = stats_y - card_h - t['section_gap']
        left_x = p
        right_x = p + (self.width - 2 * p) / 2 + 10
        col_w = (self.width - 2 * p) / 2 - 10

        if show_languages and data.get('languages'):
            lang_y = content_y
            ax.text(left_x, lang_y, "Languages",
                    fontsize=t['subtitle_font_size'], fontweight='bold',
                    color=text_primary, va='top', fontfamily='sans-serif')

            languages = data['languages'][:5]
            max_lines = languages[0]['lines'] if languages else 1
            bar_max_w = col_w - 90

            for i, lang in enumerate(languages):
                by = lang_y - 20 - i * 20
                # 语言名
                ax.text(left_x, by, lang['name'],
                        fontsize=t['small_font_size'],
                        color=text_secondary, va='top', fontfamily='sans-serif')
                # 进度条背景
                bar_x = left_x + 55
                rect = patches.FancyBboxPatch(
                    (bar_x, by - t['bar_height']), bar_max_w, t['bar_height'],
                    boxstyle=f"round,pad=0,rounding_size={t['bar_border_radius']}",
                    facecolor=card_bg if isinstance(card_bg, tuple) and len(card_bg) == 3 else (0.5, 0.5, 0.5, 0.1),
                    edgecolor='none', zorder=2
                )
                ax.add_patch(rect)
                # 进度条
                bw = max(t['bar_height'], (lang['lines'] / max_lines) * bar_max_w) if max_lines > 0 else 0
                lang_color = self._hex_to_rgb_tuple(lang['color'])
                rect2 = patches.FancyBboxPatch(
                    (bar_x, by - t['bar_height']), bw, t['bar_height'],
                    boxstyle=f"round,pad=0,rounding_size={t['bar_border_radius']}",
                    facecolor=lang_color, edgecolor='none', zorder=3
                )
                ax.add_patch(rect2)
                # 百分比
                ax.text(bar_x + bar_max_w + 8, by, f"{lang['percentage']}%",
                        fontsize=t['small_font_size'],
                        color=text_tertiary, va='top', fontfamily='sans-serif')

        # ---- 右栏：贡献者 ----
        if show_contributors and data.get('contributors'):
            contrib_y = content_y
            ax.text(right_x, contrib_y, "Contributors",
                    fontsize=t['subtitle_font_size'], fontweight='bold',
                    color=text_primary, va='top', fontfamily='sans-serif')

            contributors = data['contributors']
            max_commits = contributors[0]['commits'] if contributors else 1

            for i, c in enumerate(contributors):
                cy = contrib_y - 22 - i * 26
                name = c['name']
                if len(name) > 16:
                    name = name[:15] + '...'
                ax.text(right_x + 24, cy, name,
                        fontsize=t['body_font_size'], fontweight='600',
                        color=text_primary, va='top', fontfamily='sans-serif')
                # 提交数
                ax.text(right_x + col_w - 10, cy,
                        f"{format_number(c['commits'])} commits",
                        fontsize=t['small_font_size'],
                        color=text_tertiary, va='top', ha='right',
                        fontfamily='sans-serif')

        # ---- 底部水印 ----
        ax.text(self.width - p, p, "Generated by RepoViz",
                fontsize=8, color=text_tertiary, ha='right', va='bottom',
                alpha=0.5, fontfamily='sans-serif')

        plt.tight_layout(pad=0)
        return fig

    def render_to_file(self, data, filepath, options=None):
        """
        渲染PNG并保存到文件
        :param data: 分析数据
        :param filepath: 输出文件路径
        :param options: 渲染选项
        """
        fig = self.render(data, options)
        fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight',
                    pad_inches=0, facecolor=fig.get_facecolor())
        import matplotlib.pyplot as plt
        plt.close(fig)
