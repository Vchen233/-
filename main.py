import cv2
import numpy as np
import os
import time

def load_images(image_paths):
    """
    加载图片列表
    :param image_paths: 图片路径列表
    :return: 加载后的图片列表
    """
    return [cv2.imread(path) for path in image_paths]

def add_weight_text(image, weight):
    """
    在图片右上角添加克重文字
    :param image: 输入图片
    :param weight: 克重值
    :return: 添加文字后的图片
    """
    # 获取图片尺寸
    height, width = image.shape[:2]
    
    # 设置文字内容和格式
    text = f"{weight}g"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.0
    font_thickness = 2
    font_color = (255, 255, 255)  # 白色文字
    
    # 获取文字尺寸
    (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    
    # 计算文字位置（右上角，留出一定边距）
    padding = 10
    text_x = width - text_width - padding
    text_y = text_height + padding
    
    # 添加文字背景（半透明黑色背景）
    overlay = image.copy()
    bg_x1 = text_x - padding
    bg_y1 = text_y - text_height - padding
    bg_x2 = width - padding
    bg_y2 = text_y + padding
    cv2.rectangle(overlay, (int(bg_x1), int(bg_y1)), (int(bg_x2), int(bg_y2)), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)
    
    # 添加文字
    cv2.putText(image, text, (int(text_x), int(text_y)), font, font_scale, font_color, font_thickness)
    
    return image

def create_grid_image(images, weights):
    """
    将图片拼接成宫格布局
    :param images: 图片列表
    :param weights: 克重列表
    :return: 拼接后的图片
    """
    if len(images) != len(weights):
        raise ValueError("图片数量与克重数量不匹配")
    
    n = len(images)
    if n == 0:
        raise ValueError("没有输入图片")
    
    # 计算宫格布局的行列数
    grid_size = int(np.ceil(np.sqrt(n)))
    
    # 调整所有图片为相同大小
    max_height = max(img.shape[0] for img in images)
    max_width = max(img.shape[1] for img in images)
    
    # 设置分割线宽度
    line_width = 2
    
    # 创建空白画布（考虑分割线宽度）
    canvas_height = max_height * grid_size + line_width * (grid_size - 1)
    canvas_width = max_width * grid_size + line_width * (grid_size - 1)
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)
    
    # 填充图片
    for idx, (img, weight) in enumerate(zip(images, weights)):
        # 调整图片大小
        resized_img = cv2.resize(img, (max_width, max_height))
        # 添加克重文字
        resized_img = add_weight_text(resized_img, weight)
        
        # 计算图片在画布中的位置（考虑分割线宽度）
        row = idx // grid_size
        col = idx % grid_size
        y_start = row * (max_height + line_width)
        y_end = y_start + max_height
        x_start = col * (max_width + line_width)
        x_end = x_start + max_width
        
        # 将图片放置到画布中
        canvas[y_start:y_end, x_start:x_end] = resized_img
        
        # 绘制分割线
        if col < grid_size - 1:  # 垂直分割线
            canvas[y_start:y_end, x_end:x_end + line_width] = 0
        if row < grid_size - 1:  # 水平分割线
            canvas[y_end:y_end + line_width, x_start:x_end] = 0
    
    return canvas

def stitch_jewelry_images(image_paths, weights, output_path):
    """
    主函数：处理首饰图片拼接
    :param image_paths: 图片路径列表
    :param weights: 克重列表
    :param output_path: 输出图片路径
    """
    # 确保output文件夹存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载图片
    images = load_images(image_paths)
    
    # 创建宫格图片
    result = create_grid_image(images, weights)
    
    # 生成新的文件名：时间戳_图片数量.jpg
    timestamp = int(time.time())
    image_count = len(image_paths)
    new_filename = f"{timestamp}_{image_count}.jpg"
    output_path = os.path.join(os.path.dirname(output_path), new_filename)
    
    # 保存结果
    cv2.imwrite(output_path, result)

# 使用示例
if __name__ == "__main__":
    # 示例数据
    image_paths = ["C:\\Users\\kkx8a\\Pictures\\20200325103418_4184.jpeg", "C:\\Users\\kkx8a\\Pictures\\F219137b.jpg",
                   "C:\\Users\\kkx8a\\Pictures\\9024567221_836120467.jpg", "C:\\Users\\kkx8a\\Pictures\\OIP-C.jpg",
                   "C:\\Users\\kkx8a\\Pictures\\O1CN01OYvJGT1qZAYozIPVE_!!6000000005509-0-yinhe.avif","C:\\Users\\kkx8a\\Pictures\\9141302854_1360495613.jpg",
                   "C:\\Users\\kkx8a\\Pictures\\804559_P_1697169581383.jpg","C:\\Users\\kkx8a\\Pictures\\wKgAWGLx2LCAK3RDAAR06HNfVLI833.jpg"
                   ]
    weights = [10.5, 15.2, 8.7, 12.3, 9.6, 7.7, 8.8, 10.8]  # 克重列表（单位：克）
    output_path = os.path.join("output", "output.jpg")
    
    try:
        stitch_jewelry_images(image_paths, weights, output_path)
        print(f"拼接完成，已保存至 {output_path}")
    except Exception as e:
        print(f"处理过程中出现错误：{str(e)}")