"""
パスワード検証ユーティリティ
"""
import re
from typing import Tuple


def validate_password(password: str) -> Tuple[bool, str]:
    """
    パスワード検証
    条件: 8文字以上、英大文字1文字以上、数字1文字以上、記号不要
    """
    if len(password) < 8:
        return False, "パスワードは8文字以上にしてください"
    
    if not re.search(r'[A-Z]', password):
        return False, "パスワードには大文字を1文字以上含めてください"
    
    if not re.search(r'\d', password):
        return False, "パスワードには数字を1文字以上含めてください"
    
    return True, "OK"
