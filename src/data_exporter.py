"""
ArkLatePaymentUpdate Data Exporter
出力ファイル生成・フォーマット処理
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any
from config import (
    OUTPUT_ENCODING,
    OUTPUTS_DIR,
    generate_output_filename
)


def ensure_output_directory() -> str:
    """
    出力ディレクトリの確認・作成
    
    Returns:
        str: 出力ディレクトリパス
    """
    try:
        if not os.path.exists(OUTPUTS_DIR):
            os.makedirs(OUTPUTS_DIR)
            print(f"出力ディレクトリを作成しました: {OUTPUTS_DIR}")
        
        return OUTPUTS_DIR
        
    except Exception as e:
        print(f"出力ディレクトリ作成エラー: {e}")
        # フォールバック: カレントディレクトリ
        return "."


def format_output_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    出力データのフォーマット調整
    
    Args:
        df (pd.DataFrame): 出力対象データフレーム
        
    Returns:
        pd.DataFrame: フォーマット済みデータフレーム
    """
    try:
        print("出力データフォーマット調整...")
        
        formatted_df = df.copy()
        
        # 管理番号の形式統一（文字列、ゼロパディングなし）
        formatted_df.iloc[:, 0] = formatted_df.iloc[:, 0].astype(str).str.strip()
        
        # 管理前滞納額の形式統一（整数）
        formatted_df.iloc[:, 1] = formatted_df.iloc[:, 1].round(0).astype(int)
        
        # ソート（管理番号順）
        formatted_df = formatted_df.sort_values(by=formatted_df.columns[0])
        
        # インデックスリセット
        formatted_df = formatted_df.reset_index(drop=True)
        
        print(f"フォーマット調整完了: {len(formatted_df):,}行")
        
        return formatted_df
        
    except Exception as e:
        print(f"データフォーマット調整エラー: {e}")
        return df


def export_to_csv(df: pd.DataFrame, custom_filename: str = None) -> str:
    """
    CSV出力（CP932エンコーディング）
    
    Args:
        df (pd.DataFrame): 出力データフレーム
        custom_filename (str, optional): カスタムファイル名
        
    Returns:
        str: 出力ファイルパス
        
    Raises:
        Exception: 出力処理失敗時
    """
    try:
        print("=" * 50)
        print("CSV出力開始")
        print("=" * 50)
        
        # 出力ディレクトリ確認
        output_dir = ensure_output_directory()
        
        # ファイル名生成
        if custom_filename:
            filename = custom_filename
        else:
            filename = generate_output_filename()
        
        output_path = os.path.join(output_dir, filename)
        
        print(f"出力ファイル: {output_path}")
        print(f"エンコーディング: {OUTPUT_ENCODING}")
        
        # データフォーマット調整
        formatted_df = format_output_data(df)
        
        # CSV出力
        formatted_df.to_csv(
            output_path,
            index=False,
            encoding=OUTPUT_ENCODING,
            lineterminator='\n'  # Windows改行コード統一
        )
        
        # 出力確認
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"出力完了:")
            print(f"  ファイルパス: {output_path}")
            print(f"  ファイルサイズ: {file_size:,} bytes")
            print(f"  レコード数: {len(formatted_df):,}行")
            
            # 出力内容サンプル表示
            print(f"出力内容サンプル（先頭5行）:")
            print(formatted_df.head().to_string(index=False))
            
        else:
            raise Exception("出力ファイルが作成されませんでした")
        
        print("=" * 50)
        print("CSV出力完了")
        print("=" * 50)
        
        return output_path
        
    except Exception as e:
        print(f"CSV出力エラー: {e}")
        raise


def generate_processing_report(stats: Dict[str, Any], output_path: str) -> str:
    """
    処理レポート生成
    
    Args:
        stats (Dict[str, Any]): 処理統計情報
        output_path (str): 出力ファイルパス
        
    Returns:
        str: レポートファイルパス
    """
    try:
        # レポートファイル名生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"processing_report_{timestamp}.txt"
        report_path = os.path.join(ensure_output_directory(), report_filename)
        
        # レポート内容生成
        report_content = []
        report_content.append("=" * 60)
        report_content.append("ArkLatePaymentUpdate 処理レポート")
        report_content.append("=" * 60)
        report_content.append(f"実行日時: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}")
        report_content.append("")
        
        # 入力ファイル情報
        report_content.append("【入力ファイル情報】")
        report_content.append(f"アーク残債レコード数: {stats.get('original_arc_count', 0):,}件")
        report_content.append(f"ContractListレコード数: {stats.get('original_contract_count', 0):,}件")
        report_content.append("")
        
        # 処理結果
        report_content.append("【処理結果統計】")
        report_content.append(f"紐付け成功: {stats.get('merged_count', 0):,}件 ({stats.get('match_ratio', 0):.1%})")
        report_content.append(f"紐付け失敗: {stats.get('unmatch_count', 0):,}件 ({stats.get('unmatch_ratio', 0):.1%})")
        report_content.append(f"最終出力: {stats.get('output_count', 0):,}件")
        report_content.append("")
        
        # 金額統計
        if 'total_amount' in stats and 'avg_amount' in stats:
            report_content.append("【金額統計】")
            report_content.append(f"管理前滞納額合計: {stats['total_amount']:,.0f}円")
            report_content.append(f"管理前滞納額平均: {stats['avg_amount']:,.0f}円")
            report_content.append("")
        
        # 出力ファイル情報
        report_content.append("【出力ファイル情報】")
        report_content.append(f"出力ファイル: {os.path.basename(output_path)}")
        report_content.append(f"フルパス: {output_path}")
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            report_content.append(f"ファイルサイズ: {file_size:,} bytes")
        report_content.append("")
        
        # 品質評価
        report_content.append("【品質評価】")
        match_ratio = stats.get('match_ratio', 0)
        if match_ratio >= 0.95:
            quality = "優秀"
        elif match_ratio >= 0.90:
            quality = "良好"
        elif match_ratio >= 0.80:
            quality = "普通"
        else:
            quality = "要確認"
        
        report_content.append(f"データ品質: {quality} (紐付け成功率 {match_ratio:.1%})")
        report_content.append("")
        
        report_content.append("=" * 60)
        report_content.append("レポート終了")
        report_content.append("=" * 60)
        
        # レポートファイル書き込み
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"処理レポート生成: {report_path}")
        
        return report_path
        
    except Exception as e:
        print(f"処理レポート生成エラー: {e}")
        return ""


def export_data_with_report(df: pd.DataFrame, stats: Dict[str, Any], custom_filename: str = None) -> Dict[str, str]:
    """
    データ出力とレポート生成の統合処理
    
    Args:
        df (pd.DataFrame): 出力データフレーム
        stats (Dict[str, Any]): 処理統計情報
        custom_filename (str, optional): カスタムファイル名
        
    Returns:
        Dict[str, str]: 出力ファイル情報
    """
    try:
        # CSV出力
        output_path = export_to_csv(df, custom_filename)
        
        # 処理レポート生成
        report_path = generate_processing_report(stats, output_path)
        
        return {
            'csv_path': output_path,
            'report_path': report_path,
            'csv_filename': os.path.basename(output_path),
            'report_filename': os.path.basename(report_path) if report_path else ""
        }
        
    except Exception as e:
        print(f"データ出力統合処理エラー: {e}")
        raise