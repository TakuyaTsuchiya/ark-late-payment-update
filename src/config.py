"""
ArkLatePaymentUpdate Configuration
設定・マッピング・定数定義
"""

import os
from datetime import datetime

# ファイル名パターン
ARK_CSV_PATTERN = "【アーク継続中】②残債取込用CSV_*.csv"
CONTRACT_LIST_PATTERN = "ContractList*.csv"

# カラムマッピング - アーク残債CSV
ARK_COLUMNS = {
    'contract_number': '契約番号',
    'outstanding_amount': '未収金額合計',
    'outstanding_guarantee': '未収保証料残（顧客請求分）',
    'other_charges': 'その他請求（事務手数料残）',
    'advance_amount': '立替金額',
    'other_advance': 'その他立替金',
    'external_arrears': '外部連携滞納額',
    'late_fee': '延滞金',
    'collected_rent': '収納済家賃'
}

# カラムマッピング - ContractList
CONTRACT_COLUMNS = {
    'management_number': '管理番号',
    'inheritance_number': '引継番号',
    'contractor_name': '契約者氏名',
    'property_name': '物件名',
    'outstanding_debt': '滞納残債'
}

# 出力設定
OUTPUT_COLUMNS = ['管理番号', '管理前滞納額']
OUTPUT_ENCODING = 'cp932'

# ファイル名生成設定
def generate_output_filename():
    """出力ファイル名生成 (mmddアーク残債.csv)"""
    today = datetime.now()
    return f"{today.month:02d}{today.day:02d}アーク残債.csv"

# ディレクトリ設定
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, 'outputs')

# ログ設定
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# データ処理設定
ENCODING_CANDIDATES = ['cp932', 'shift_jis', 'utf-8', 'utf-8-sig']
MAX_FILE_SIZE_MB = 100  # 最大ファイルサイズ (MB)

# 統計・品質チェック設定
WARN_UNMATCH_RATIO = 0.1  # 紐付け失敗率10%以上で警告
ERROR_UNMATCH_RATIO = 0.3  # 紐付け失敗率30%以上でエラー