"""
ArcLatePaymentUpdate Data Processor  
データ紐付け・変換処理
"""

import pandas as pd
from typing import Tuple, Dict, Any, Optional
from config import (
    ARC_COLUMNS,
    CONTRACT_COLUMNS,
    OUTPUT_COLUMNS,
    WARN_UNMATCH_RATIO,
    ERROR_UNMATCH_RATIO
)


def normalize_key_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    キー項目の正規化（空白除去、型統一）
    
    Args:
        df (pd.DataFrame): データフレーム
        column_name (str): 正規化対象のカラム名
        
    Returns:
        pd.DataFrame: 正規化後のデータフレーム
    """
    try:
        if column_name not in df.columns:
            raise KeyError(f"カラムが見つかりません: {column_name}")
        
        print(f"キー項目正規化: {column_name}")
        
        # コピーを作成
        df_normalized = df.copy()
        
        # 文字列変換
        df_normalized[column_name] = df_normalized[column_name].astype(str)
        
        # 空白除去（全角・半角）
        df_normalized[column_name] = df_normalized[column_name].str.strip()
        df_normalized[column_name] = df_normalized[column_name].str.replace('　', '', regex=False)  # 全角スペース
        
        # NaN、空文字、'nan'の処理
        df_normalized = df_normalized[
            (df_normalized[column_name] != '') & 
            (df_normalized[column_name] != 'nan') &
            (df_normalized[column_name].notna())
        ]
        
        print(f"正規化後レコード数: {len(df_normalized):,}件")
        
        return df_normalized
        
    except Exception as e:
        print(f"キー項目正規化エラー: {e}")
        return df


def validate_required_columns(df: pd.DataFrame, required_columns: Dict[str, str], file_type: str) -> bool:
    """
    必須カラムの存在確認
    
    Args:
        df (pd.DataFrame): データフレーム
        required_columns (Dict[str, str]): 必須カラムマッピング
        file_type (str): ファイル種別
        
    Returns:
        bool: 全ての必須カラムが存在する場合True
    """
    try:
        print(f"{file_type}の必須カラム確認...")
        
        missing_columns = []
        for key, column_name in required_columns.items():
            if column_name not in df.columns:
                missing_columns.append(column_name)
        
        if missing_columns:
            print(f"エラー: {file_type}に必要なカラムが見つかりません:")
            for col in missing_columns:
                print(f"  - {col}")
            print(f"利用可能なカラム: {list(df.columns)}")
            return False
        
        print(f"{file_type}の必須カラム確認完了")
        return True
        
    except Exception as e:
        print(f"カラム確認エラー: {e}")
        return False


def merge_dataframes(arc_df: pd.DataFrame, contract_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    データフレーム結合（契約番号=引継番号）
    
    Args:
        arc_df (pd.DataFrame): アーク残債データ
        contract_df (pd.DataFrame): ContractListデータ
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (結合後データフレーム, 統計情報)
    """
    try:
        print("データフレーム結合開始...")
        
        # 必須カラム確認
        arc_required = {
            'contract_number': ARC_COLUMNS['contract_number'],
            'outstanding_amount': ARC_COLUMNS['outstanding_amount']
        }
        
        contract_required = {
            'management_number': CONTRACT_COLUMNS['management_number'],
            'inheritance_number': CONTRACT_COLUMNS['inheritance_number']
        }
        
        if not validate_required_columns(arc_df, arc_required, "アーク残債CSV"):
            raise Exception("アーク残債CSVの必須カラムが不足しています")
        
        if not validate_required_columns(contract_df, contract_required, "ContractList"):
            raise Exception("ContractListの必須カラムが不足しています")
        
        # 元のレコード数記録
        original_arc_count = len(arc_df)
        original_contract_count = len(contract_df)
        
        print(f"結合前レコード数:")
        print(f"  アーク残債: {original_arc_count:,}件")
        print(f"  ContractList: {original_contract_count:,}件")
        
        # キー項目の正規化
        arc_normalized = normalize_key_column(arc_df, ARC_COLUMNS['contract_number'])
        contract_normalized = normalize_key_column(contract_df, CONTRACT_COLUMNS['inheritance_number'])
        
        # 結合実行 (Inner Join)
        merged_df = pd.merge(
            arc_normalized,
            contract_normalized,
            left_on=ARC_COLUMNS['contract_number'],
            right_on=CONTRACT_COLUMNS['inheritance_number'],
            how='inner',
            suffixes=('_arc', '_contract')
        )
        
        # 統計情報生成
        merged_count = len(merged_df)
        unmatch_arc = original_arc_count - merged_count
        unmatch_ratio = unmatch_arc / original_arc_count if original_arc_count > 0 else 0
        
        stats = {
            'original_arc_count': original_arc_count,
            'original_contract_count': original_contract_count,
            'merged_count': merged_count,
            'unmatch_count': unmatch_arc,
            'unmatch_ratio': unmatch_ratio,
            'match_ratio': 1 - unmatch_ratio
        }
        
        print(f"結合結果:")
        print(f"  結合成功: {merged_count:,}件 ({stats['match_ratio']:.1%})")
        print(f"  結合失敗: {unmatch_arc:,}件 ({unmatch_ratio:.1%})")
        
        # 品質チェック
        if unmatch_ratio >= ERROR_UNMATCH_RATIO:
            print(f"エラー: 紐付け失敗率が高すぎます ({unmatch_ratio:.1%})")
            raise Exception(f"データ品質エラー: 紐付け失敗率 {unmatch_ratio:.1%}")
        elif unmatch_ratio >= WARN_UNMATCH_RATIO:
            print(f"警告: 紐付け失敗率がやや高めです ({unmatch_ratio:.1%})")
        
        return merged_df, stats
        
    except Exception as e:
        print(f"データフレーム結合エラー: {e}")
        raise


def extract_required_columns(merged_df: pd.DataFrame) -> pd.DataFrame:
    """
    必要列の抽出・リネーム
    
    Args:
        merged_df (pd.DataFrame): 結合後データフレーム
        
    Returns:
        pd.DataFrame: 出力用データフレーム（管理番号, 管理前滞納額）
    """
    try:
        print("必要列の抽出開始...")
        
        # 必要なカラムの確認
        management_col = CONTRACT_COLUMNS['management_number']
        outstanding_col = ARC_COLUMNS['outstanding_amount']
        
        if management_col not in merged_df.columns:
            raise KeyError(f"管理番号カラムが見つかりません: {management_col}")
        
        if outstanding_col not in merged_df.columns:
            raise KeyError(f"未収金額合計カラムが見つかりません: {outstanding_col}")
        
        # 必要列を抽出
        output_df = merged_df[[management_col, outstanding_col]].copy()
        
        # 列名をリネーム
        output_df.columns = OUTPUT_COLUMNS
        
        # データ型の統一
        # 管理番号: 文字列
        output_df[OUTPUT_COLUMNS[0]] = output_df[OUTPUT_COLUMNS[0]].astype(str)
        
        # 管理前滞納額: 数値（カンマ区切り対応）
        try:
            if output_df[OUTPUT_COLUMNS[1]].dtype == 'object':
                # 文字列の場合、カンマを除去して数値変換
                output_df[OUTPUT_COLUMNS[1]] = output_df[OUTPUT_COLUMNS[1]].astype(str).str.replace(',', '', regex=False)
            
            output_df[OUTPUT_COLUMNS[1]] = pd.to_numeric(output_df[OUTPUT_COLUMNS[1]], errors='coerce')
        except Exception as e:
            print(f"数値変換警告: {e}")
        
        # NaN値のチェック
        nan_count = output_df[OUTPUT_COLUMNS[1]].isna().sum()
        if nan_count > 0:
            print(f"警告: 管理前滞納額に無効な値があります: {nan_count}件")
            # NaN値を0に置換
            output_df[OUTPUT_COLUMNS[1]] = output_df[OUTPUT_COLUMNS[1]].fillna(0)
        
        print(f"抽出完了: {len(output_df):,}行, {len(output_df.columns)}列")
        print(f"出力カラム: {list(output_df.columns)}")
        
        # データ概要
        print(f"管理前滞納額統計:")
        print(f"  合計: {output_df[OUTPUT_COLUMNS[1]].sum():,.0f}円")
        print(f"  平均: {output_df[OUTPUT_COLUMNS[1]].mean():,.0f}円")
        print(f"  最大: {output_df[OUTPUT_COLUMNS[1]].max():,.0f}円")
        print(f"  最小: {output_df[OUTPUT_COLUMNS[1]].min():,.0f}円")
        
        return output_df
        
    except Exception as e:
        print(f"必要列抽出エラー: {e}")
        raise


def process_data(arc_df: pd.DataFrame, contract_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    データ処理統合処理
    
    Args:
        arc_df (pd.DataFrame): アーク残債データ
        contract_df (pd.DataFrame): ContractListデータ
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: (出力用データフレーム, 処理統計)
    """
    try:
        print("=" * 50)
        print("データ処理開始")
        print("=" * 50)
        
        # データフレーム結合
        merged_df, merge_stats = merge_dataframes(arc_df, contract_df)
        
        # 必要列の抽出
        output_df = extract_required_columns(merged_df)
        
        # 最終統計
        final_stats = {
            **merge_stats,
            'output_count': len(output_df),
            'total_amount': output_df[OUTPUT_COLUMNS[1]].sum(),
            'avg_amount': output_df[OUTPUT_COLUMNS[1]].mean(),
        }
        
        print("=" * 50)
        print("データ処理完了")
        print("=" * 50)
        
        return output_df, final_stats
        
    except Exception as e:
        print(f"データ処理エラー: {e}")
        raise