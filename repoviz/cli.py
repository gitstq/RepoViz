# -*- coding: utf-8 -*-
"""
CLI入口模块
使用argparse构建命令行接口
"""

import argparse
import os
import sys

from . import __version__
from .analyzer import RepoAnalyzer, NotAGitRepositoryError, GitCommandError
from .renderer_svg import SVGRenderer
from .renderer_png import PNGRenderer


def build_parser():
    """
    构建命令行参数解析器
    """
    parser = argparse.ArgumentParser(
        prog='repoviz',
        description='RepoViz - 轻量级Git仓库数据可视化海报生成工具',
        epilog='示例: repoviz /path/to/repo -f svg -t gradient -s readme',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Git仓库路径（默认当前目录）'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出文件路径（默认: repoviz.<格式>）'
    )

    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['svg', 'png', 'both'],
        default='svg',
        help='输出格式：svg / png / both（默认svg）'
    )

    parser.add_argument(
        '-t', '--template',
        type=str,
        choices=['minimal', 'gradient', 'dark'],
        default='gradient',
        help='模板名称：minimal / gradient / dark（默认gradient）'
    )

    parser.add_argument(
        '-s', '--size',
        type=str,
        choices=['readme', 'social'],
        default='readme',
        help='海报尺寸：readme / social（默认readme）'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=5,
        help='Top N贡献者（默认5）'
    )

    parser.add_argument(
        '--no-heatmap',
        action='store_true',
        default=False,
        help='不包含提交热力图'
    )

    parser.add_argument(
        '--no-languages',
        action='store_true',
        default=False,
        help='不包含语言分布'
    )

    parser.add_argument(
        '--no-contributors',
        action='store_true',
        default=False,
        help='不包含贡献者统计'
    )

    parser.add_argument(
        '--no-activity',
        action='store_true',
        default=False,
        help='不包含活跃时段'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    return parser


def main(args=None):
    """
    CLI主入口函数
    """
    parser = build_parser()
    opts = parser.parse_args(args)

    # 解析仓库路径
    repo_path = os.path.abspath(opts.path)

    # 确定输出路径
    output_path = opts.output
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    else:
        output_path = os.path.join(os.getcwd(), 'repoviz')

    # 步骤1：分析仓库
    print(f"正在分析仓库: {repo_path}")
    try:
        analyzer = RepoAnalyzer(repo_path)
    except NotAGitRepositoryError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 执行全量分析
    try:
        data = analyzer.analyze_all(top_n=opts.top)
    except GitCommandError as e:
        print(f"Git命令执行失败: {e}", file=sys.stderr)
        sys.exit(1)

    repo_info = data['repo_info']
    print(f"  仓库: {repo_info['repo_name']}")
    print(f"  提交数: {repo_info['total_commits']}")
    print(f"  文件数: {repo_info['total_files']}")

    # 渲染选项
    render_options = {
        'show_heatmap': not opts.no_heatmap,
        'show_languages': not opts.no_languages,
        'show_contributors': not opts.no_contributors,
        'show_activity': not opts.no_activity,
    }

    # 步骤2：渲染海报
    fmt = opts.format

    if fmt in ('svg', 'both'):
        svg_path = output_path if output_path.endswith('.svg') else f"{output_path}.svg"
        print(f"正在生成SVG海报: {svg_path}")
        renderer = SVGRenderer(
            template_name=opts.template,
            size_name=opts.size
        )
        renderer.render_to_file(data, svg_path, render_options)
        print(f"  SVG已保存: {svg_path}")

    if fmt in ('png', 'both'):
        png_path = output_path if output_path.endswith('.png') else f"{output_path}.png"
        print(f"正在生成PNG海报: {png_path}")
        renderer = PNGRenderer(
            template_name=opts.template,
            size_name=opts.size
        )
        renderer.render_to_file(data, png_path, render_options)
        print(f"  PNG已保存: {png_path}")

    print("完成!")


if __name__ == '__main__':
    main()
