"""
Утилитные функции для работы с изображениями и URL
"""
import re
from typing import Optional


def convert_google_drive_url(url: Optional[str]) -> Optional[str]:
    """
    Преобразует Google Drive ссылку в прямую ссылку на изображение.
    
    Args:
        url: URL для обработки (может быть None или пустой строкой)
        
    Returns:
        Прямая ссылка на изображение для Google Drive URLs,
        оригинальная ссылка для других URLs,
        None если URL пустой или None
        
    Examples:
        >>> convert_google_drive_url('https://drive.google.com/file/d/1ABC123/view')
        'https://drive.google.com/uc?export=view&id=1ABC123'
        
        >>> convert_google_drive_url('https://example.com/image.jpg')  
        'https://example.com/image.jpg'
        
        >>> convert_google_drive_url(None)
        None
    """
    if not url:
        return None
    
    # Проверяем, является ли это ссылкой Google Drive
    if 'drive.google.com' in url:
        # Извлекаем ID файла из различных форматов Google Drive ссылок
        file_id_pattern = re.compile(r'/file/d/([a-zA-Z0-9_-]+)')
        match = file_id_pattern.search(url)
        
        if match:
            file_id = match.group(1)
            # Преобразуем в прямую ссылку для просмотра
            return f'https://drive.google.com/uc?export=view&id={file_id}'
        
        # Если не удалось извлечь ID, попробуем другой способ
        if 'id=' in url:
            id_pattern = re.compile(r'id=([a-zA-Z0-9_-]+)')
            id_match = id_pattern.search(url)
            if id_match:
                file_id = id_match.group(1)
                return f'https://drive.google.com/uc?export=view&id={file_id}'
    
    # Если это не Google Drive ссылка, возвращаем как есть
    return url


def is_google_drive_url(url: Optional[str]) -> bool:
    """
    Проверяет, является ли URL ссылкой на Google Drive.
    
    Args:
        url: URL для проверки
        
    Returns:
        True если это Google Drive ссылка, False в противном случае
    """
    if not url:
        return False
    return 'drive.google.com' in url


def extract_google_drive_file_id(url: Optional[str]) -> Optional[str]:
    """
    Извлекает ID файла из Google Drive ссылки.
    
    Args:
        url: Google Drive URL
        
    Returns:
        ID файла если удалось извлечь, None в противном случае
    """
    if not url:
        return None
    
    # Пробуем разные форматы ссылок
    file_id_pattern = re.compile(r'/file/d/([a-zA-Z0-9_-]+)')
    match = file_id_pattern.search(url)
    
    if match:
        return match.group(1)
    
    if 'id=' in url:
        id_pattern = re.compile(r'id=([a-zA-Z0-9_-]+)')
        id_match = id_pattern.search(url)
        if id_match:
            return id_match.group(1)
    
    return None
