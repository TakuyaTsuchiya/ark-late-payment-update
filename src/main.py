"""
ArkLatePaymentUpdate Main Application
メインアプリケーション - アーク残債取り込み処理
"""

import sys
import os
import argparse
from typing import Optional

# プロジェクトのsrcディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import generate_output_filename
from data_loader import load_input_files
from data_processor import process_data
from data_exporter import export_data_with_report
from utils import (
    print_banner, 
    print_section, 
    handle_exception, 
    print_processing_summary,
    get_system_info
)


def main(search_directory: str = ".", custom_output_filename: Optional[str] = None) -> bool:
    """
    メイン処理
    
    Args:
        search_directory (str): 検索ディレクトリ
        custom_output_filename (Optional[str]): カスタム出力ファイル名
        
    Returns:
        bool: 処理成功時True
    """
    try:
        # システム情報表示
        print_banner("ArkLatePaymentUpdate v1.0", 60)
        print("アーク残債取り込みアプリケーション")
        
        sys_info = get_system_info()
        print(f"実行日時: {sys_info.get('timestamp', 'Unknown')}")
        print(f"作業ディレクトリ: {sys_info.get('current_directory', 'Unknown')}")
        print(f"検索ディレクトリ: {os.path.abspath(search_directory)}")
        
        # Phase 1: ファイル読み込み
        print_section("Phase 1: ファイル読み込み")
        
        arc_df, contract_df, file_info = load_input_files(search_directory)
        
        # ファイル読み込み結果確認
        if arc_df is None:
            print("エラー: アーク残債CSVファイルを読み込めませんでした")
            print("必要なファイル: 【アーク継続中】②残債取込用CSV_*.csv")
            return False
        
        if contract_df is None:
            print("エラー: ContractListファイルを読み込めませんでした")
            print("必要なファイル: ContractList*.csv")
            return False
        
        print("OK ファイル読み込み完了")
        print(f"  アーク残債: {file_info['arc_rows']:,}行")
        print(f"  ContractList: {file_info['contract_rows']:,}行")
        
        # Phase 2: データ処理
        print_section("Phase 2: データ処理・紐付け")
        
        output_df, processing_stats = process_data(arc_df, contract_df)
        
        if len(output_df) == 0:
            print("エラー: 紐付け処理の結果、出力データが0件になりました")
            print("原因: 契約番号と引継番号の値が一致していない可能性があります")
            return False
        
        print("OK データ処理完了")
        
        # Phase 3: ファイル出力
        print_section("Phase 3: ファイル出力")
        
        output_info = export_data_with_report(
            output_df, 
            processing_stats, 
            custom_output_filename
        )
        
        print("OK ファイル出力完了")
        print(f"  CSVファイル: {output_info['csv_filename']}")
        if output_info['report_filename']:
            print(f"  レポートファイル: {output_info['report_filename']}")
        
        # 処理サマリー表示
        print_processing_summary(processing_stats)
        
        print_banner("処理正常終了", 60)
        print("ミライル顧客システムに取り込みファイルをアップロードしてください")
        print(f"ファイル: {output_info['csv_path']}")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n処理がユーザーによって中断されました")
        return False
        
    except Exception as e:
        handle_exception(e, "メイン処理")
        return False


def parse_arguments():
    """
    コマンドライン引数解析
    
    Returns:
        argparse.Namespace: 解析済み引数
    """
    parser = argparse.ArgumentParser(
        description="ArkLatePaymentUpdate - アーク残債取り込みアプリケーション",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py
  python main.py --directory /path/to/files
  python main.py --output 0801アーク残債.csv
  
入力ファイル:
  - 【アーク継続中】②残債取込用CSV_*.csv
  - ContractList*.csv
  
出力ファイル:
  - mmddアーク残債.csv (管理番号, 管理前滞納額)
        """
    )
    
    parser.add_argument(
        '--directory', '-d',
        type=str,
        default=".",
        help="入力ファイル検索ディレクトリ (デフォルト: カレントディレクトリ)"
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help="出力ファイル名 (デフォルト: mmddアーク残債.csv)"
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='ArkLatePaymentUpdate v1.0'
    )
    
    return parser.parse_args()


def validate_environment() -> bool:
    """
    実行環境の検証
    
    Returns:
        bool: 環境が適切な場合True
    """
    try:
        # Python バージョンチェック
        if sys.version_info < (3, 6):
            print("エラー: Python 3.6以上が必要です")
            return False
        
        # 必要なライブラリのインポートチェック
        try:
            import pandas
            import chardet
        except ImportError as e:
            print(f"エラー: 必要なライブラリがインストールされていません: {e}")
            print("以下のコマンドでインストールしてください:")
            print("pip install -r requirements.txt")
            return False
        
        return True
        
    except Exception as e:
        print(f"環境検証エラー: {e}")
        return False


if __name__ == "__main__":
    # 環境検証
    if not validate_environment():
        sys.exit(1)
    
    # コマンドライン引数解析
    args = parse_arguments()
    
    # メイン処理実行
    success = main(
        search_directory=args.directory,
        custom_output_filename=args.output
    )
    
    # 終了コード設定
    sys.exit(0 if success else 1)