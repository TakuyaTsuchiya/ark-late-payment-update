"""
ArcLatePaymentUpdate Data Loader
ファイル読み込み・エンコーディング自動検出機能
"""

import os
import glob
import chardet
import pandas as pd
from typing import Tuple, Optional, Dict, Any
from config import (
    ARC_CSV_PATTERN, 
    CONTRACT_LIST_PATTERN, 
    ENCODING_CANDIDATES,
    MAX_FILE_SIZE_MB
)


def detect_encoding(file_path: str) -> str:
    """
    ファイルのエンコーディングを自動検出
    
    Args:
        file_path (str): ファイルパス
        
    Returns:
        str: 検出されたエンコーディング
        
    Raises:
        Exception: エンコーディング検出失敗時
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 最初の10KB読み込み
            
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
        confidence = result['confidence']
        
        print(f"エンコーディング検出: {detected_encoding} (信頼度: {confidence:.2f})")
        
        # 信頼度が低い場合は候補から選択
        if confidence < 0.7:
            print("信頼度が低いため、候補エンコーディングを試行します...")
            for encoding in ENCODING_CANDIDATES:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1000)  # テスト読み込み
                    print(f"エンコーディング確定: {encoding}")
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            raise Exception(f"有効なエンコーディングが見つかりません: {file_path}")
        
        return detected_encoding
        
    except Exception as e:
        print(f"エンコーディング検出エラー: {e}")
        print("デフォルトエンコーディング cp932 を使用します")
        return 'cp932'


def check_file_size(file_path: str) -> bool:
    """
    ファイルサイズチェック
    
    Args:
        file_path (str): ファイルパス
        
    Returns:
        bool: サイズが適切な場合True
    """
    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            print(f"警告: ファイルサイズが大きいです ({size_mb:.1f}MB > {MAX_FILE_SIZE_MB}MB): {file_path}")
            return False
        return True
    except Exception as e:
        print(f"ファイルサイズチェックエラー: {e}")
        return True


def load_csv_file(file_path: str) -> pd.DataFrame:
    """
    CSVファイル読み込み（エンコーディング自動対応）
    
    Args:
        file_path (str): CSVファイルパス
        
    Returns:
        pd.DataFrame: 読み込まれたデータフレーム
        
    Raises:
        Exception: ファイル読み込み失敗時
    """
    try:
        print(f"ファイル読み込み開始: {os.path.basename(file_path)}")
        
        # ファイル存在チェック
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # ファイルサイズチェック
        check_file_size(file_path)
        
        # エンコーディング検出
        encoding = detect_encoding(file_path)
        
        # CSV読み込み
        df = pd.read_csv(file_path, encoding=encoding)
        
        print(f"読み込み完了: {len(df):,}行, {len(df.columns)}列")
        print(f"カラム: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        
        return df
        
    except Exception as e:
        print(f"ファイル読み込みエラー: {file_path}")
        print(f"エラー詳細: {e}")
        raise


def find_input_files(search_directory: str = ".") -> Tuple[Optional[str], Optional[str]]:
    """
    入力ファイル自動検索
    
    Args:
        search_directory (str): 検索ディレクトリ
        
    Returns:
        Tuple[Optional[str], Optional[str]]: (アーク残債CSV, ContractList) のファイルパス
    """
    try:
        print(f"ファイル検索開始: {os.path.abspath(search_directory)}")
        
        # アーク残債CSVファイル検索
        arc_pattern = os.path.join(search_directory, ARC_CSV_PATTERN)
        arc_files = glob.glob(arc_pattern)
        
        print(f"アーク残債ファイル検索パターン: {arc_pattern}")
        print(f"見つかったファイル: {len(arc_files)}件")
        
        if not arc_files:
            print(f"アーク残債ファイルが見つかりません: {ARC_CSV_PATTERN}")
            arc_file = None
        else:
            # 最新ファイルを選択（ファイル更新日時ベース）
            arc_file = max(arc_files, key=os.path.getmtime)
            print(f"アーク残債ファイル選択: {os.path.basename(arc_file)}")
        
        # ContractListファイル検索
        contract_pattern = os.path.join(search_directory, CONTRACT_LIST_PATTERN)
        contract_files = glob.glob(contract_pattern)
        
        print(f"ContractListファイル検索パターン: {contract_pattern}")
        print(f"見つかったファイル: {len(contract_files)}件")
        
        if not contract_files:
            print(f"ContractListファイルが見つかりません: {CONTRACT_LIST_PATTERN}")
            contract_file = None
        else:
            # 最新ファイルを選択
            contract_file = max(contract_files, key=os.path.getmtime)
            print(f"ContractListファイル選択: {os.path.basename(contract_file)}")
        
        return arc_file, contract_file
        
    except Exception as e:
        print(f"ファイル検索エラー: {e}")
        return None, None


def load_input_files(search_directory: str = ".") -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Dict[str, Any]]:
    """
    入力ファイル読み込み統合処理
    
    Args:
        search_directory (str): 検索ディレクトリ
        
    Returns:
        Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame], Dict[str, Any]]: 
        (アーク残債DataFrame, ContractListDataFrame, ファイル情報)
    """
    # ファイル検索
    arc_file, contract_file = find_input_files(search_directory)
    
    file_info = {
        'arc_file': arc_file,
        'contract_file': contract_file,
        'arc_df': None,
        'contract_df': None,
        'arc_rows': 0,
        'contract_rows': 0
    }
    
    arc_df = None
    contract_df = None
    
    # アーク残債CSV読み込み
    if arc_file:
        try:
            arc_df = load_csv_file(arc_file)
            file_info['arc_df'] = arc_df
            file_info['arc_rows'] = len(arc_df)
        except Exception as e:
            print(f"アーク残債ファイル読み込み失敗: {e}")
    
    # ContractList読み込み
    if contract_file:
        try:
            contract_df = load_csv_file(contract_file)
            file_info['contract_df'] = contract_df
            file_info['contract_rows'] = len(contract_df)
        except Exception as e:
            print(f"ContractListファイル読み込み失敗: {e}")
    
    return arc_df, contract_df, file_info