# -*- coding: utf-8 -*-
"""
analyzer模块测试
测试Git命令解析、数据统计逻辑
"""

import os
import sys
import tempfile
import subprocess
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest

# 确保可以导入被测模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repoviz.analyzer import (
    RepoAnalyzer, NotAGitRepositoryError, GitCommandError
)
from repoviz.utils import (
    format_number, hex_to_rgb, rgb_to_hex, rgb_to_hsl, hsl_to_rgb,
    interpolate_color, adjust_brightness, hex_to_rgba,
    get_language_from_extension, get_language_color,
    is_excluded_dir, get_date_range_weeks, date_to_week_column,
)


class TestRepoAnalyzerValidation:
    """测试仓库验证逻辑"""

    def test_nonexistent_path_raises_error(self):
        """测试不存在的路径抛出异常"""
        with pytest.raises(NotAGitRepositoryError):
            RepoAnalyzer('/nonexistent/path/that/does/not/exist')

    def test_non_git_dir_raises_error(self, tmp_path):
        """测试非Git目录抛出异常"""
        with pytest.raises(NotAGitRepositoryError):
            RepoAnalyzer(str(tmp_path))

    def test_valid_git_repo(self, tmp_path):
        """测试有效的Git仓库初始化"""
        # 创建一个临时Git仓库
        subprocess.run(['git', 'init'], cwd=str(tmp_path),
                       capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'],
                       cwd=str(tmp_path), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'],
                       cwd=str(tmp_path), capture_output=True)

        analyzer = RepoAnalyzer(str(tmp_path))
        assert analyzer.repo_path == str(tmp_path)


class TestRepoAnalyzerInfo:
    """测试仓库信息获取"""

    def _create_test_repo(self, tmp_path):
        """创建测试用Git仓库"""
        subprocess.run(['git', 'init'], cwd=str(tmp_path),
                       capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'],
                       cwd=str(tmp_path), capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'],
                       cwd=str(tmp_path), capture_output=True)

        # 创建一些文件并提交
        for i in range(3):
            f = tmp_path / f"file{i}.py"
            f.write_text(f"# File {i}\nprint('hello')\n")
            subprocess.run(['git', 'add', str(f)],
                           cwd=str(tmp_path), capture_output=True, check=True)
            subprocess.run(['git', 'commit', '-m', f'Commit {i}'],
                           cwd=str(tmp_path), capture_output=True, check=True)

        return tmp_path

    def test_get_repo_info(self, tmp_path):
        """测试获取仓库基本信息"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        info = analyzer.get_repo_info()

        assert 'repo_name' in info
        assert 'total_commits' in info
        assert 'total_files' in info
        assert info['total_commits'] == 3
        assert info['total_files'] >= 3

    def test_analyze_languages(self, tmp_path):
        """测试语言分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        languages = analyzer.analyze_languages()

        assert isinstance(languages, list)
        # 应该有Python语言
        lang_names = [l['name'] for l in languages]
        assert 'Python' in lang_names

        # 每种语言应有正确的字段
        for lang in languages:
            assert 'name' in lang
            assert 'files' in lang
            assert 'lines' in lang
            assert 'percentage' in lang
            assert 'color' in lang

    def test_analyze_contributors(self, tmp_path):
        """测试贡献者分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        contributors = analyzer.analyze_contributors(top_n=5)

        assert isinstance(contributors, list)
        assert len(contributors) >= 1
        assert contributors[0]['name'] == 'Test User'
        assert contributors[0]['commits'] == 3

    def test_analyze_commit_heatmap(self, tmp_path):
        """测试提交热力图分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        heatmap_data = analyzer.analyze_commit_heatmap(weeks=52)

        assert 'heatmap' in heatmap_data
        assert 'max_count' in heatmap_data
        assert 'total_commits' in heatmap_data
        assert 'active_days' in heatmap_data
        assert isinstance(heatmap_data['heatmap'], dict)

    def test_analyze_activity_patterns(self, tmp_path):
        """测试活跃时段分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        activity = analyzer.analyze_activity_patterns()

        assert 'by_day' in activity
        assert 'by_hour' in activity
        assert isinstance(activity['by_day'], list)
        assert isinstance(activity['by_hour'], list)
        assert len(activity['by_day']) == 7
        assert len(activity['by_hour']) == 24

    def test_analyze_code_growth(self, tmp_path):
        """测试代码增长趋势分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        growth = analyzer.analyze_code_growth()

        assert isinstance(growth, list)
        assert len(growth) >= 1
        for item in growth:
            assert 'month' in item
            assert 'commits' in item
            assert 'cumulative_commits' in item

    def test_analyze_all(self, tmp_path):
        """测试全量分析"""
        repo = self._create_test_repo(tmp_path)
        analyzer = RepoAnalyzer(str(repo))
        data = analyzer.analyze_all()

        assert 'repo_info' in data
        assert 'languages' in data
        assert 'heatmap' in data
        assert 'contributors' in data
        assert 'code_growth' in data
        assert 'activity' in data
