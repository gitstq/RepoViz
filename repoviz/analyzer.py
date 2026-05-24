# -*- coding: utf-8 -*-
"""
Git仓库数据分析引擎
使用subprocess调用git命令分析仓库数据，不依赖gitpython
"""

import os
import subprocess
from collections import defaultdict, Counter
from datetime import datetime, timedelta

from .utils import (
    get_language_from_extension,
    get_language_color,
    is_excluded_dir,
    is_binary_file,
    is_image_file,
    is_lock_file,
    count_lines_in_file,
    get_date_range_weeks,
    date_to_week_column,
    EXTENSION_LANGUAGE_MAP,
)


class GitCommandError(Exception):
    """Git命令执行错误"""
    pass


class NotAGitRepositoryError(Exception):
    """不是Git仓库错误"""
    pass


class RepoAnalyzer:
    """
    Git仓库数据分析器
    分析本地Git仓库的各项数据指标
    """

    def __init__(self, repo_path='.'):
        """
        初始化分析器
        :param repo_path: Git仓库路径
        """
        self.repo_path = os.path.abspath(repo_path)
        self._validate_repo()

    def _validate_repo(self):
        """验证给定路径是否为有效的Git仓库"""
        if not os.path.isdir(self.repo_path):
            raise NotAGitRepositoryError(f"路径不存在: {self.repo_path}")
        git_dir = os.path.join(self.repo_path, '.git')
        if not os.path.exists(git_dir):
            raise NotAGitRepositoryError(f"不是Git仓库: {self.repo_path}")

    def _run_git(self, *args):
        """
        执行git命令并返回输出
        :param args: git命令参数
        :return: 命令输出字符串（去除首尾空白）
        """
        cmd = ['git', '-C', self.repo_path] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode != 0:
                raise GitCommandError(f"git命令失败: {' '.join(cmd)}\n{result.stderr}")
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            raise GitCommandError(f"git命令超时: {' '.join(cmd)}")
        except FileNotFoundError:
            raise GitCommandError("未找到git命令，请确保git已安装")

    # ============================================================
    # 仓库基本信息
    # ============================================================

    def get_repo_info(self):
        """
        获取仓库基本信息
        返回包含仓库名、总提交数、总文件数、仓库年龄等信息的字典
        """
        # 获取仓库名称
        repo_name = os.path.basename(self.repo_path)

        # 获取远程仓库URL（如果有）
        remote_url = ''
        try:
            remote_url = self._run_git('remote', 'get-url', 'origin')
        except GitCommandError:
            pass

        # 获取总提交数
        total_commits = 0
        try:
            output = self._run_git('rev-list', '--count', 'HEAD')
            total_commits = int(output) if output else 0
        except (GitCommandError, ValueError):
            pass

        # 获取总分支数
        total_branches = 0
        try:
            output = self._run_git('branch', '-a')
            if output:
                total_branches = len([b for b in output.split('\n') if b.strip()])
        except GitCommandError:
            pass

        # 获取总标签数
        total_tags = 0
        try:
            output = self._run_git('tag')
            if output:
                total_tags = len([t for t in output.split('\n') if t.strip()])
        except GitCommandError:
            pass

        # 获取仓库年龄（首次提交日期）
        repo_age_days = 0
        first_commit_date = None
        try:
            output = self._run_git(
                'log', '--reverse', '--format=%ad', '--date=short', '-1'
            )
            if output:
                first_commit_date = output
                first_date = datetime.strptime(output, '%Y-%m-%d').date()
                repo_age_days = (datetime.now().date() - first_date).days
        except (GitCommandError, ValueError):
            pass

        # 获取最新提交日期
        last_commit_date = None
        try:
            output = self._run_git('log', '-1', '--format=%ad', '--date=short')
            if output:
                last_commit_date = output
        except GitCommandError:
            pass

        # 统计文件总数
        total_files = self._count_files()

        return {
            'repo_name': repo_name,
            'remote_url': remote_url,
            'total_commits': total_commits,
            'total_branches': total_branches,
            'total_tags': total_tags,
            'total_files': total_files,
            'repo_age_days': repo_age_days,
            'first_commit_date': first_commit_date,
            'last_commit_date': last_commit_date,
        }

    def _count_files(self):
        """统计仓库中被跟踪的文件总数"""
        try:
            output = self._run_git('ls-files')
            if output:
                return len([f for f in output.split('\n') if f.strip()])
            return 0
        except GitCommandError:
            # 如果git ls-files失败，尝试手动统计
            count = 0
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
                count += len(files)
            return count

    # ============================================================
    # 语言分布分析
    # ============================================================

    def analyze_languages(self):
        """
        分析仓库的语言分布
        通过文件扩展名统计各语言占比
        返回: 按文件数量排序的语言列表，每个元素包含语言名、文件数、占比、颜色
        """
        # 获取所有被跟踪的文件
        try:
            output = self._run_git('ls-files')
            if not output:
                return []
            tracked_files = [f for f in output.split('\n') if f.strip()]
        except GitCommandError:
            tracked_files = []
            for root, dirs, files in os.walk(self.repo_path):
                dirs[:] = [d for d in dirs if not is_excluded_dir(d)]
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, self.repo_path)
                    tracked_files.append(rel_path)

        # 统计各语言的文件数和行数
        lang_stats = defaultdict(lambda: {'files': 0, 'lines': 0})
        total_files = 0

        for rel_path in tracked_files:
            _, ext = os.path.splitext(rel_path)

            # 跳过无扩展名文件
            if not ext:
                continue

            # 跳过锁文件和二进制文件
            if is_lock_file(rel_path):
                continue

            full_path = os.path.join(self.repo_path, rel_path)

            # 跳过不存在的文件、二进制文件和图片
            if not os.path.exists(full_path):
                continue
            if is_binary_file(full_path) or is_image_file(full_path):
                continue

            language = get_language_from_extension(ext)
            lang_stats[language]['files'] += 1
            lang_stats[language]['lines'] += count_lines_in_file(full_path)
            total_files += 1

        # 按行数排序
        sorted_languages = sorted(
            lang_stats.items(),
            key=lambda x: x[1]['lines'],
            reverse=True
        )

        # 计算总行数
        total_lines = sum(stats['lines'] for _, stats in sorted_languages)

        # 构建结果列表
        result = []
        for lang, stats in sorted_languages:
            percentage = (stats['lines'] / total_lines * 100) if total_lines > 0 else 0
            result.append({
                'name': lang,
                'files': stats['files'],
                'lines': stats['lines'],
                'percentage': round(percentage, 1),
                'color': get_language_color(lang),
            })

        # 限制返回前10种语言
        return result[:10]

    # ============================================================
    # 提交热力图分析
    # ============================================================

    def analyze_commit_heatmap(self, weeks=52):
        """
        分析过去N周的提交热力图数据
        返回52周x7天的提交频率矩阵
        """
        start_date, end_date = get_date_range_weeks(weeks)

        # 获取过去一年的提交日期
        since_date = start_date.strftime('%Y-%m-%d')
        try:
            output = self._run_git(
                'log', f'--since={since_date}',
                '--format=%ad', '--date=short'
            )
        except GitCommandError:
            output = ''

        # 统计每天的提交次数
        daily_counts = Counter()
        if output:
            for line in output.split('\n'):
                line = line.strip()
                if line:
                    try:
                        date_obj = datetime.strptime(line, '%Y-%m-%d').date()
                        if start_date <= date_obj <= end_date:
                            daily_counts[date_obj] += 1
                    except ValueError:
                        continue

        # 构建热力图矩阵 (week_index, day_of_week) -> count
        heatmap = {}
        max_count = 0
        total_commits_in_range = 0

        for date_obj, count in daily_counts.items():
            week_idx, day_idx = date_to_week_column(date_obj, start_date)
            heatmap[(week_idx, day_idx)] = count
            max_count = max(max_count, count)
            total_commits_in_range += count

        # 计算活跃天数
        active_days = len(daily_counts)

        return {
            'heatmap': heatmap,
            'max_count': max_count,
            'total_commits': total_commits_in_range,
            'active_days': active_days,
            'weeks': weeks,
            'start_date': start_date,
            'end_date': end_date,
        }

    # ============================================================
    # 贡献者统计
    # ============================================================

    def analyze_contributors(self, top_n=5):
        """
        分析仓库贡献者统计
        返回Top N贡献者列表，包含提交数和行数变更
        """
        # 获取所有贡献者的提交数
        try:
            output = self._run_git(
                'log', '--format=%aN'
            )
        except GitCommandError:
            return []

        if not output:
            return []

        # 统计每个贡献者的提交数
        author_commits = Counter()
        for line in output.split('\n'):
            line = line.strip()
            if line:
                author_commits[line] += 1

        # 获取Top N贡献者
        top_authors = author_commits.most_common(top_n)

        # 获取每个贡献者的行数变更
        contributors = []
        for author, commits in top_authors:
            try:
                stats_output = self._run_git(
                    'log', '--author', author,
                    '--numstat', '--format=%H'
                )
                additions = 0
                deletions = 0
                if stats_output:
                    for line in stats_output.split('\n'):
                        line = line.strip()
                        if line and not line.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                            # 跳过commit hash行
                            if len(line) == 40:
                                continue
                        parts = line.split('\t')
                        if len(parts) == 3:
                            try:
                                add = int(parts[0]) if parts[0] != '-' else 0
                                delete = int(parts[1]) if parts[1] != '-' else 0
                                additions += add
                                deletions += delete
                            except ValueError:
                                continue
            except GitCommandError:
                additions = 0
                deletions = 0

            contributors.append({
                'name': author,
                'commits': commits,
                'additions': additions,
                'deletions': deletions,
                'total_changes': additions + deletions,
            })

        return contributors

    # ============================================================
    # 代码增长趋势
    # ============================================================

    def analyze_code_growth(self):
        """
        分析按月的代码行数增长趋势
        返回每月的总行数变化数据
        """
        try:
            output = self._run_git(
                'log', '--reverse', '--format=%ad', '--date=format:%Y-%m'
            )
        except GitCommandError:
            return []

        if not output:
            return []

        # 获取每月的提交数
        monthly_commits = Counter()
        for line in output.split('\n'):
            line = line.strip()
            if line:
                monthly_commits[line] += 1

        # 按月份排序
        sorted_months = sorted(monthly_commits.keys())

        # 累计提交数
        cumulative = 0
        growth_data = []
        for month in sorted_months:
            cumulative += monthly_commits[month]
            growth_data.append({
                'month': month,
                'commits': monthly_commits[month],
                'cumulative_commits': cumulative,
            })

        return growth_data

    # ============================================================
    # 活跃时段分析
    # ============================================================

    def analyze_activity_patterns(self):
        """
        分析提交的活跃时段分布
        返回按星期几和按小时的提交频率
        """
        try:
            output = self._run_git(
                'log', '--format=%ad', '--date=format:%a-%H'
            )
        except GitCommandError:
            return {'by_day': {}, 'by_hour': {}}

        if not output:
            return {'by_day': {}, 'by_hour': {}}

        # 星期几的映射（中文）
        day_names = {
            'Mon': '周一', 'Tue': '周二', 'Wed': '周三',
            'Thu': '周四', 'Fri': '周五', 'Sat': '周六', 'Sun': '周日',
        }
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        by_day = Counter()
        by_hour = Counter()

        for line in output.split('\n'):
            line = line.strip()
            if '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    day, hour = parts[0], parts[1]
                    by_day[day] += 1
                    try:
                        by_hour[int(hour)] += 1
                    except ValueError:
                        pass

        # 构建按星期几的结果（保持顺序）
        day_data = []
        for day in day_order:
            day_data.append({
                'day': day,
                'day_cn': day_names.get(day, day),
                'count': by_day.get(day, 0),
            })

        # 构建按小时的结果（0-23小时）
        hour_data = []
        for h in range(24):
            hour_data.append({
                'hour': h,
                'count': by_hour.get(h, 0),
            })

        max_day_count = max((d['count'] for d in day_data), default=0)
        max_hour_count = max((h['count'] for h in hour_data), default=0)

        return {
            'by_day': day_data,
            'by_hour': hour_data,
            'max_day_count': max_day_count,
            'max_hour_count': max_hour_count,
        }

    # ============================================================
    # 综合分析
    # ============================================================

    def analyze_all(self, top_n=5, heatmap_weeks=52):
        """
        执行全量分析，返回所有数据维度
        """
        return {
            'repo_info': self.get_repo_info(),
            'languages': self.analyze_languages(),
            'heatmap': self.analyze_commit_heatmap(heatmap_weeks),
            'contributors': self.analyze_contributors(top_n),
            'code_growth': self.analyze_code_growth(),
            'activity': self.analyze_activity_patterns(),
        }
