# Copyright (c) 2026 昔音
# SPDX-License-Identifier: MIT OR MulanPSL-2.0
# 项目仓库: `https://gitee.com/liveaileen/trucert` 和 `https://github.com/LiveAlieen/trucert`

#!/usr/bin/env python3
"""
统一测试启动机制

支持分别或同时运行GUI测试套件和CLI测试套件的全部测试用例
并生成详细的测试报告
"""

import unittest
import sys
import os
import argparse
import json
from datetime import datetime
from unittest import TextTestRunner, TestLoader
from unittest.runner import TextTestResult

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入初始化依赖
from cert_manager.core.utils import initialize_dependencies


class StreamWrapper:
    """流包装器，添加writeln方法"""
    
    def __init__(self, stream):
        self.stream = stream
    
    def write(self, text):
        """写入文本"""
        self.stream.write(text)
    
    def writeln(self, text=''):
        """写入一行文本"""
        self.stream.write(text + '\n')
    
    def flush(self):
        """刷新流"""
        self.stream.flush()


class EnhancedTextTestResult(TextTestResult):
    """增强的测试结果输出"""
    
    def __init__(self, stream, descriptions, verbosity):
        # 包装流以添加writeln方法
        wrapped_stream = StreamWrapper(stream)
        super().__init__(wrapped_stream, descriptions, verbosity)
        self.test_results = []
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.test_results.append({
            'test': str(test),
            'status': 'success',
            'message': None
        })
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.test_results.append({
            'test': str(test),
            'status': 'failure',
            'message': str(err)
        })
    
    def addError(self, test, err):
        super().addError(test, err)
        self.test_results.append({
            'test': str(test),
            'status': 'error',
            'message': str(err)
        })
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.test_results.append({
            'test': str(test),
            'status': 'skipped',
            'message': reason
        })


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_suites = {
            'common': os.path.join(os.path.dirname(__file__), 'common'),
            'gui': os.path.join(os.path.dirname(__file__), 'gui'),
            'cli': os.path.join(os.path.dirname(__file__), 'cli')
        }
        self._initialized = False
    
    def _initialize(self):
        """初始化依赖注入容器"""
        if not self._initialized:
            print("Initializing dependencies for tests...")
            initialize_dependencies()
            print("Dependencies initialized successfully!")
            self._initialized = True
    
    def discover_tests(self, suite_name):
        """发现指定测试套件的测试用例"""
        if suite_name not in self.test_suites:
            print(f"错误: 未知的测试套件 '{suite_name}'")
            return None
        
        suite_path = self.test_suites[suite_name]
        if not os.path.exists(suite_path):
            print(f"错误: 测试套件目录 '{suite_path}' 不存在")
            return None
        
        # 确保src目录在Python路径中
        src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        loader = TestLoader()
        suite = loader.discover(suite_path, pattern='test_*.py')
        return suite
    
    def run_suite(self, suite_name):
        """运行指定的测试套件"""
        # 初始化依赖
        self._initialize()
        
        print(f"\n=== 运行测试套件: {suite_name} ===")
        suite = self.discover_tests(suite_name)
        if not suite:
            return None
        
        # 创建测试结果对象
        result = EnhancedTextTestResult(sys.stdout, True, 2)
        suite.run(result)
        
        # 输出测试结果摘要
        print(f"\n=== 测试套件 {suite_name} 结果摘要 ===")
        print(f"总测试数: {result.testsRun}")
        print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"失败: {len(result.failures)}")
        print(f"错误: {len(result.errors)}")
        print(f"跳过: {len(result.skipped)}")
        
        return result
    
    def run_all(self):
        """运行所有测试套件"""
        print("=== 运行所有测试套件 ===")
        all_results = {}
        
        for suite_name in self.test_suites:
            result = self.run_suite(suite_name)
            if result:
                all_results[suite_name] = result
        
        # 输出总体结果摘要
        print("\n=== 总体测试结果摘要 ===")
        total_tests = 0
        total_success = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        for suite_name, result in all_results.items():
            total_tests += result.testsRun
            total_success += result.testsRun - len(result.failures) - len(result.errors)
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            total_skipped += len(result.skipped)
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {total_success}")
        print(f"失败: {total_failures}")
        print(f"错误: {total_errors}")
        print(f"跳过: {total_skipped}")
        
        return all_results
    
    def generate_report(self, results, report_file=None):
        """生成测试报告"""
        if not report_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(os.path.dirname(__file__), f'test_report_{timestamp}.json')
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'suites': {}
        }
        
        if isinstance(results, dict):
            # 多个测试套件的结果
            for suite_name, result in results.items():
                suite_data = {
                    'total_tests': result.testsRun,
                    'success': result.testsRun - len(result.failures) - len(result.errors),
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'skipped': len(result.skipped),
                    'test_results': result.test_results
                }
                report_data['suites'][suite_name] = suite_data
        else:
            # 单个测试套件的结果
            suite_data = {
                'total_tests': results.testsRun,
                'success': results.testsRun - len(results.failures) - len(results.errors),
                'failures': len(results.failures),
                'errors': len(results.errors),
                'skipped': len(results.skipped),
                'test_results': results.test_results
            }
            report_data['suites']['single'] = suite_data
        
        # 计算总体统计
        total_tests = 0
        total_success = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        for suite_data in report_data['suites'].values():
            total_tests += suite_data['total_tests']
            total_success += suite_data['success']
            total_failures += suite_data['failures']
            total_errors += suite_data['errors']
            total_skipped += suite_data['skipped']
        
        report_data['summary'] = {
            'total_tests': total_tests,
            'success': total_success,
            'failures': total_failures,
            'errors': total_errors,
            'skipped': total_skipped,
            'success_rate': f"{((total_success / total_tests) * 100):.2f}%" if total_tests > 0 else "0.00%"
        }
        
        # 写入报告文件
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已生成: {report_file}")
        return report_file


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='统一测试启动机制')
    parser.add_argument('suite', nargs='*', default=['all'],
                        help='要运行的测试套件 (common, gui, cli, all)')
    parser.add_argument('--report', '-r', type=str,
                        help='测试报告输出文件路径')
    
    args = parser.parse_args()
    runner = TestRunner()
    
    if 'all' in args.suite:
        # 运行所有测试套件
        results = runner.run_all()
        if results:
            runner.generate_report(results, args.report)
    else:
        # 运行指定的测试套件
        all_results = {}
        for suite_name in args.suite:
            result = runner.run_suite(suite_name)
            if result:
                all_results[suite_name] = result
        
        if all_results:
            runner.generate_report(all_results, args.report)


if __name__ == '__main__':
    main()
