import os
import cv2
import numpy as np
from PIL import Image

def create_directories():
    """创建必要的目录"""
    dirs = ['img', 'logo', 'output']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

def load_images(directory):
    """加载指定目录下的所有图片
    
    Args:
        directory (str): 图片目录路径
        
    Returns:
        list: 图片列表，每个元素为(图片名, 图片数据)元组
    """
    images = []
    valid_extensions = ['.jpg', '.jpeg', '.png']
    
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            filepath = os.path.join(directory, filename)
            try:
                img = cv2.imread(filepath)
                if img is not None:
                    images.append((filename, img))
            except Exception as e:
                print(f"Error loading image {filename}: {str(e)}")
    
    return images

def add_white_background(image, padding=20):
    """为图片添加白色背景和内边距
    
    Args:
        image (numpy.ndarray): 输入图片
        padding (int): 内边距大小
        
    Returns:
        numpy.ndarray: 添加白色背景后的图片
    """
    h, w = image.shape[:2]
    new_size = (h + 2 * padding, w + 2 * padding, 3)
    background = np.ones(new_size, dtype=np.uint8) * 255
    
    # 将原图放在白色背景中央
    background[padding:padding+h, padding:padding+w] = image
    return background

def resize_to_square(image, size, keep_aspect_ratio=True):
    """将图片调整为正方形
    
    Args:
        image (numpy.ndarray): 输入图片
        size (int): 目标尺寸
        keep_aspect_ratio (bool): 是否保持宽高比
        
    Returns:
        numpy.ndarray: 调整后的图片
    """
    h, w = image.shape[:2]
    if h == w:
        return cv2.resize(image, (size, size))
    
    if keep_aspect_ratio:
        # 创建白色背景
        background = np.ones((size, size, 3), dtype=np.uint8) * 255
        
        # 计算缩放比例
        scale = size / max(h, w)
        new_h, new_w = int(h * scale), int(w * scale)
        
        # 缩放图片
        resized = cv2.resize(image, (new_w, new_h))
        
        # 计算居中位置
        y_offset = (size - new_h) // 2
        x_offset = (size - new_w) // 2
        
        # 将图片放在白色背景中央
        background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return background
    else:
        # 直接拉伸到正方形
        return cv2.resize(image, (size, size))

def add_logo(image, logo, position='top-left', margin=0, size_ratio=0.25):
    """在图片指定位置添加logo
    
    Args:
        image (numpy.ndarray): 主图片
        logo (numpy.ndarray): logo图片
        position (str): logo位置，'top-left' 或 'top-right'
        margin (int): 边距
        size_ratio (float): logo大小比例（相对于图片宽度）
        
    Returns:
        numpy.ndarray: 添加logo后的图片
    """
    # 获取logo原始尺寸
    logo_h, logo_w = logo.shape[:2]
    target_width = int(image.shape[1] * size_ratio)
    
    # 保持原始宽高比进行缩放
    scale = target_width / logo_w
    new_w = target_width
    new_h = int(logo_h * scale)
    
    # 缩放logo
    logo = cv2.resize(logo, (new_w, new_h))
    
    # 计算logo位置（完全贴在角落）
    if position == 'top-left':
        x = margin
        y = margin
    elif position == 'top-right':
        x = image.shape[1] - new_w - margin
        y = margin
    
    # 创建logo掩码
    logo_gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(logo_gray, 250, 255, cv2.THRESH_BINARY_INV)
    
    # 在图片上添加logo
    roi = image[y:y+new_h, x:x+new_w]
    roi_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask))
    roi_fg = cv2.bitwise_and(logo, logo, mask=mask)
    image[y:y+new_h, x:x+new_w] = cv2.add(roi_bg, roi_fg)
    
    return image

def add_border(image, border_size=1, color=(220, 220, 220)):
    """为图片添加边框
    
    Args:
        image (numpy.ndarray): 输入图片
        border_size (int): 边框宽度
        color (tuple): 边框颜色 (B,G,R)
        
    Returns:
        numpy.ndarray: 添加边框后的图片
    """
    h, w = image.shape[:2]
    bordered = image.copy()
    
    # 添加边框
    bordered[0:border_size, :] = color  # 上边框
    bordered[h-border_size:h, :] = color  # 下边框
    bordered[:, 0:border_size] = color  # 左边框
    bordered[:, w-border_size:w] = color  # 右边框
    
    return bordered

def add_decorative_border(image, border_pattern=None):
    """为底图添加装饰性边框
    
    Args:
        image (numpy.ndarray): 输入图片
        border_pattern (numpy.ndarray, optional): 边框图案
        
    Returns:
        numpy.ndarray: 添加装饰边框后的图片
    """
    h, w = image.shape[:2]
    border_size = 20
    
    # 创建带边框的新图片
    bordered = image.copy()
    
    # 添加简单的灰色边框
    color = (240, 240, 240)
    thickness = 2
    
    # 绘制边框
    cv2.rectangle(bordered, (0, 0), (w-1, h-1), color, thickness)
    
    # 绘制角落的装饰
    corner_size = 30
    cv2.line(bordered, (0, 0), (corner_size, 0), color, thickness)
    cv2.line(bordered, (0, 0), (0, corner_size), color, thickness)
    
    cv2.line(bordered, (w-1, 0), (w-1-corner_size, 0), color, thickness)
    cv2.line(bordered, (w-1, 0), (w-1, corner_size), color, thickness)
    
    cv2.line(bordered, (0, h-1), (corner_size, h-1), color, thickness)
    cv2.line(bordered, (0, h-1), (0, h-1-corner_size), color, thickness)
    
    cv2.line(bordered, (w-1, h-1), (w-1-corner_size, h-1), color, thickness)
    cv2.line(bordered, (w-1, h-1), (w-1, h-1-corner_size), color, thickness)
    
    return bordered

def calculate_grid_size(num_images, aspect_ratio=1.5):
    """计算图片网格大小
    
    Args:
        num_images (int): 图片数量
        aspect_ratio (float): 底图宽高比
        
    Returns:
        tuple: (行数, 列数)
    """
    # 计算最佳网格大小
    cols = int(np.ceil(np.sqrt(num_images * aspect_ratio)))
    rows = int(np.ceil(num_images / cols))
    return rows, cols 