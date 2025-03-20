import os
import cv2
import numpy as np
from utils import (
    create_directories,
    load_images,
    resize_to_square,
    add_logo
)

class ImageProcessor:
    def __init__(self):
        """初始化图片处理器"""
        self.item_size = 280  # 饰品图片的统一大小
        self.padding = 15     # 图片间距
        self.cols = 6        # 固定6列布局
        self.side_margin = 50  # 左右边距
        create_directories()
        
    def process_items(self):
        """处理所有饰品图片"""
        # 加载饰品图片和logo
        items = load_images('img')
        logos = load_images('logo')
        
        if not items:
            raise ValueError("No item images found in 'img' directory")
        if not logos:
            raise ValueError("No logo images found in 'logo' directory")
            
        # 使用第一个logo
        logo = logos[0][1]
        
        # 处理每个饰品图片
        processed_items = []
        for filename, item in items:
            # 调整为正方形
            item = resize_to_square(item, self.item_size)
            # 添加logo
            item = add_logo(item, logo)
            processed_items.append((filename, item))
            
        return processed_items
    
    def create_layout(self, background_path, processed_items):
        """在底图上布局饰品图片
        
        Args:
            background_path (str): 底图路径
            processed_items (list): 处理后的饰品图片列表
        """
        # 读取底图
        background = cv2.imread(background_path)
        if background is None:
            raise ValueError(f"Could not load background image: {background_path}")
            
        bg_h, bg_w = background.shape[:2]
        
        # 计算可用区域（下三分之二，并向上偏移）
        available_height = int(bg_h * 2/3)
        y_start = int(bg_h * 0.27)  # 从27%的位置开始
        
        # 计算行数（固定6列）
        rows = (len(processed_items) + self.cols - 1) // self.cols
        
        # 计算实际的图片大小（考虑间距和左右边距）
        total_padding_w = self.padding * (self.cols - 1)  # 只计算图片之间的间距
        available_width = bg_w - 2 * self.side_margin  # 减去左右边距
        item_w = (available_width - total_padding_w) // self.cols
        
        # 计算起始位置（居中）
        x_start = self.side_margin  # 使用设定的左右边距
        total_height = rows * (item_w + self.padding) + self.padding
        y_offset = y_start + (available_height - total_height) // 2
        
        # 放置图片
        for idx, (_, item) in enumerate(processed_items):
            if idx >= rows * self.cols:
                break
                
            row = idx // self.cols
            col = idx % self.cols
            
            x = x_start + col * (item_w + self.padding)
            y = y_offset + row * (item_w + self.padding)
            
            # 调整图片大小
            item_resized = cv2.resize(item, (item_w, item_w))
            
            try:
                # 放置图片
                background[y:y+item_w, x:x+item_w] = item_resized
            except ValueError as e:
                print(f"Warning: Could not place image at position {idx+1} due to size mismatch")
                continue
            
        return background

def main():
    processor = ImageProcessor()
    
    try:
        # 处理饰品图片
        processed_items = processor.process_items()
        
        # 等待用户输入底图路径
        background_path = input("请输入底图路径: ")
        if not os.path.exists(background_path):
            raise ValueError(f"Background image not found: {background_path}")
        
        # 创建布局
        result = processor.create_layout(background_path, processed_items)
        
        # 保存结果
        output_path = os.path.join('output', 'result.jpg')
        cv2.imwrite(output_path, result)
        print(f"处理完成，结果已保存至: {output_path}")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 