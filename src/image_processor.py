import os
import cv2
import numpy as np
import math
from utils import (
    create_directories,
    load_images,
    resize_to_square,
    add_logo
)

class ImageProcessor:
    def __init__(self):
        """初始化图片处理器"""
        self.padding = 15     # 图片间距
        self.side_margin = 50  # 左右边距
        self.item_logo_size = 0.3  # 饰品图片上logo的大小比例
        self.main_logo_size = 0.25  # 底图上logo的大小比例
        create_directories()
        
    def calculate_optimal_grid(self, num_images, area_width, area_height):
        """计算最佳网格布局
        
        Args:
            num_images (int): 图片数量
            area_width (int): 可用区域宽度
            area_height (int): 可用区域高度
            
        Returns:
            tuple: (行数, 列数, 图片大小)
        """
        if num_images <= 0:
            raise ValueError("图片数量必须大于0")
        if num_images > 24:
            raise ValueError("图片数量不能超过24张")
            
        # 计算理想的行列比例（基于区域的宽高比）
        area_ratio = area_width / area_height
        
        # 尝试不同的列数，找到最佳布局
        best_layout = None
        max_image_size = 0
        
        # 考虑1到6列的情况
        for cols in range(1, 7):
            rows = math.ceil(num_images / cols)
            
            # 计算这种布局下的图片大小
            available_width = area_width - 2 * self.side_margin - (cols - 1) * self.padding
            available_height = area_height - (rows - 1) * self.padding
            
            width_per_image = available_width / cols
            height_per_image = available_height / rows
            
            # 取较小值作为图片大小（保持正方形）
            image_size = min(width_per_image, height_per_image)
            
            # 如果这种布局下的图片更大，则更新最佳布局
            if image_size > max_image_size:
                max_image_size = image_size
                best_layout = (rows, cols, int(image_size))
        
        return best_layout
    
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
        for filename, item in items[:24]:  # 限制最多24张图片
            # 添加logo（左上角，较大尺寸）
            item = add_logo(item, logo, position='top-left', margin=0, size_ratio=self.item_logo_size)
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
        
        # 加载logo并添加到底图右上角
        logos = load_images('logo')
        if logos:
            background = add_logo(background, logos[0][1], 
                                position='top-right', 
                                size_ratio=self.main_logo_size,
                                margin=9)
        
        # 计算可用区域
        available_height = int(bg_h * 0.7)  # 使用固定比例的高度
        y_start = int(bg_h * 0.27)  # 从27%的位置开始
        available_width = bg_w
        
        # 计算最佳网格布局
        rows, cols, item_size = self.calculate_optimal_grid(
            len(processed_items), 
            available_width, 
            available_height
        )
        
        # 计算起始位置（居中）
        total_width = cols * item_size + (cols - 1) * self.padding
        total_height = rows * item_size + (rows - 1) * self.padding
        
        x_start = (bg_w - total_width) // 2
        y_offset = y_start + (available_height - total_height) // 2
        
        # 放置图片
        for idx, (_, item) in enumerate(processed_items):
            if idx >= rows * cols:
                break
                
            row = idx // cols
            col = idx % cols
            
            x = x_start + col * (item_size + self.padding)
            y = y_offset + row * (item_size + self.padding)
            
            # 调整图片大小
            item_resized = cv2.resize(item, (item_size, item_size))
            
            try:
                # 放置图片
                background[y:y+item_size, x:x+item_size] = item_resized
            except ValueError as e:
                print(f"Warning: Could not place image at position {idx+1} due to size mismatch")
                continue
            
        return background

def main():
    processor = ImageProcessor()
    
    try:
        # 处理饰品图片
        processed_items = processor.process_items()
        
        if len(processed_items) == 0:
            raise ValueError("没有找到可处理的图片")
        if len(processed_items) > 24:
            print("警告：图片数量超过24张，只会处理前24张")
        
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