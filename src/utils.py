"""
ArcLatePaymentUpdate Utilities
共通ユーティリティ・ヘルパー関数
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional


def print_banner(title: str, width: int = 60) -> None:
    """
    バナー表示
    
    Args:
        title (str): タイトル
        width (int): バナー幅
    """
    border = "=" * width
    padding = (width - len(title) - 2) // 2
    formatted_title = " " * padding + title + " " * padding
    if len(formatted_title) < width - 2:
        formatted_title += " "
    
    print(border)
    print(f"={formatted_title}=")
    print(border)


def print_section(title: str, width: int = 50) -> None:
    """
    セクション表示
    
    Args:
        title (str): セクションタイトル
        width (int): 幅
    """
    border = "-" * width
    print(f"\n{border}")
    print(f" {title}")
    print(f"{border}")


def format_number(number: float, decimal_places: int = 0) -> str:
    """
    数値フォーマット（カンマ区切り）
    
    Args:
        number (float): 数値
        decimal_places (int): 小数点以下桁数
        
    Returns:
        str: フォーマット済み数値文字列
    """
    try:
        if decimal_places == 0:
            return f"{number:,.0f}"
        else:
            return f"{number:,.{decimal_places}f}"
    except (ValueError, TypeError):
        return str(number)


def format_percentage(ratio: float, decimal_places: int = 1) -> str:
    """
    パーセンテージフォーマット
    
    Args:
        ratio (float): 比率（0-1）
        decimal_places (int): 小数点以下桁数
        
    Returns:
        str: パーセンテージ文字列
    """
    try:
        return f"{ratio * 100:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return "0.0%"


def format_file_size(bytes_size: int) -> str:
    """
    ファイルサイズフォーマット
    
    Args:
        bytes_size (int): バイト数
        
    Returns:
        str: フォーマット済みファイルサイズ
    """
    try:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    except (ValueError, TypeError):
        return "Unknown"


def get_timestamp(format_string: str = "%Y%m%d_%H%M%S") -> str:
    """
    タイムスタンプ生成
    
    Args:
        format_string (str): 日時フォーマット
        
    Returns:
        str: フォーマット済みタイムスタンプ
    """
    return datetime.now().strftime(format_string)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全な除算（ゼロ除算回避）
    
    Args:
        numerator (float): 分子
        denominator (float): 分母
        default (float): デフォルト値（ゼロ除算時）
        
    Returns:
        float: 除算結果またはデフォルト値
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (ValueError, TypeError):
        return default


def print_data_summary(df, title: str = "データ概要") -> None:
    """
    データフレーム概要表示
    
    Args:
        df: pandas DataFrame
        title (str): タイトル
    """
    try:
        print_section(title)
        print(f"行数: {len(df):,}")
        print(f"列数: {len(df.columns)}")
        print(f"列名: {list(df.columns)}")
        
        if len(df) > 0:
            print("\n先頭5行:")
            print(df.head().to_string(index=False))
            
            # 数値列の統計
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                print(f"\n数値列統計:")
                for col in numeric_columns:
                    print(f"  {col}: 合計={format_number(df[col].sum())}, "
                          f"平均={format_number(df[col].mean())}, "
                          f"最大={format_number(df[col].max())}, "
                          f"最小={format_number(df[col].min())}")
        
    except Exception as e:
        print(f"データ概要表示エラー: {e}")


def handle_exception(e: Exception, context: str = "") -> None:
    """
    例外処理ハンドラー
    
    Args:
        e (Exception): 例外オブジェクト
        context (str): コンテキスト情報
    """
    print(f"\n{'='*60}")
    print("エラーが発生しました")
    print(f"{'='*60}")
    
    if context:
        print(f"コンテキスト: {context}")
    
    print(f"エラータイプ: {type(e).__name__}")
    print(f"エラーメッセージ: {str(e)}")
    
    # デバッグ情報（詳細なトレースバック）
    print(f"\n詳細情報:")
    traceback.print_exc()
    
    print(f"{'='*60}")


def validate_file_path(file_path: str, check_exists: bool = True) -> bool:
    """
    ファイルパス検証
    
    Args:
        file_path (str): ファイルパス
        check_exists (bool): 存在チェック実行有無
        
    Returns:
        bool: 有効な場合True
    """
    try:
        if not file_path or not isinstance(file_path, str):
            return False
        
        # パス形式チェック
        normalized_path = os.path.normpath(file_path)
        
        if check_exists and not os.path.exists(normalized_path):
            return False
        
        return True
        
    except Exception:
        return False


def create_directory_if_not_exists(dir_path: str) -> bool:
    """
    ディレクトリ作成（存在しない場合）
    
    Args:
        dir_path (str): ディレクトリパス
        
    Returns:
        bool: 成功した場合True
    """
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            return True
        return True
        
    except Exception as e:
        print(f"ディレクトリ作成エラー: {e}")
        return False


def print_processing_summary(stats: Dict[str, Any]) -> None:
    """
    処理サマリー表示
    
    Args:
        stats (Dict[str, Any]): 処理統計情報
    """
    try:
        print_banner("処理サマリー", 60)
        
        # 入力情報
        print("【入力】")
        print(f"  アーク残債: {format_number(stats.get('original_arc_count', 0))}件")
        print(f"  ContractList: {format_number(stats.get('original_contract_count', 0))}件")
        
        # 処理結果
        print("\n【処理結果】")
        match_count = stats.get('merged_count', 0)
        unmatch_count = stats.get('unmatch_count', 0)
        match_ratio = stats.get('match_ratio', 0)
        
        print(f"  紐付け成功: {format_number(match_count)}件 ({format_percentage(match_ratio)})")
        print(f"  紐付け失敗: {format_number(unmatch_count)}件")
        print(f"  最終出力: {format_number(stats.get('output_count', 0))}件")
        
        # 金額情報
        if 'total_amount' in stats:
            print("\n【金額情報】")
            print(f"  合計滞納額: {format_number(stats['total_amount'])}円")
            print(f"  平均滞納額: {format_number(stats.get('avg_amount', 0))}円")
        
        # 品質評価
        print("\n【品質評価】")
        if match_ratio >= 0.95:
            quality = "優秀"
            emoji = "[OK]"
        elif match_ratio >= 0.90:
            quality = "良好"
            emoji = "[OK]"
        elif match_ratio >= 0.80:
            quality = "普通"
            emoji = "[WARN]"
        else:
            quality = "要確認"
            emoji = "[ERROR]"
        
        print(f"  データ品質: {emoji} {quality}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"処理サマリー表示エラー: {e}")


def get_system_info() -> Dict[str, str]:
    """
    システム情報取得
    
    Returns:
        Dict[str, str]: システム情報
    """
    try:
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'current_directory': os.getcwd(),
            'timestamp': get_timestamp("%Y/%m/%d %H:%M:%S")
        }
    except Exception:
        return {'error': 'システム情報取得失敗'}