"""
ArcLatePaymentUpdate Package
アーク残債取り込みアプリケーション
"""

__version__ = "1.0.0"
__author__ = "Takuya Tsuchiya"
__description__ = "アークからの残債データをミライル顧客システムに取り込み可能な形式に変換"

# パッケージレベルのインポート
from .config import (
    ARC_CSV_PATTERN,
    CONTRACT_LIST_PATTERN,
    OUTPUT_COLUMNS,
    generate_output_filename
)

from .data_loader import (
    load_input_files,
    find_input_files,
    load_csv_file
)

from .data_processor import (
    process_data,
    merge_dataframes,
    extract_required_columns
)

from .data_exporter import (
    export_to_csv,
    export_data_with_report
)

from .utils import (
    print_banner,
    print_section,
    format_number,
    format_percentage
)

__all__ = [
    # Config
    'ARC_CSV_PATTERN',
    'CONTRACT_LIST_PATTERN', 
    'OUTPUT_COLUMNS',
    'generate_output_filename',
    
    # Data Loader
    'load_input_files',
    'find_input_files',
    'load_csv_file',
    
    # Data Processor
    'process_data',
    'merge_dataframes',
    'extract_required_columns',
    
    # Data Exporter
    'export_to_csv',
    'export_data_with_report',
    
    # Utils
    'print_banner',
    'print_section',
    'format_number',
    'format_percentage'
]