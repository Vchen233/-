# 图片处理工具

这个项目是一个图片处理工具，主要功能包括：
1. 处理饰品图片和商标logo
2. 在底图上按规则排列饰品图片
3. 在饰品图片右上角添加logo
4. 保持图片间距和整体美观

## 项目结构
```
.
├── README.md           # 项目说明文档
├── requirements.txt    # Python依赖包
├── src/               # 源代码目录
│   ├── image_processor.py    # 图片处理核心代码
│   └── utils.py             # 工具函数
├── img/               # 饰品图片目录
├── logo/             # 商标logo目录
└── output/           # 输出图片目录
```

## 环境要求
- Python 3.8+
- OpenCV
- Pillow
- NumPy

## 安装
```bash
pip install -r requirements.txt
```

## 使用方法
1. 将饰品图片放入 `img` 目录
2. 将logo图片放入 `logo` 目录
3. 运行程序：
```bash
python src/image_processor.py
```

## 注意事项
- 输入图片支持格式：jpg, png
- 建议使用分辨率相近的图片以获得最佳效果
- 程序会自动创建所需目录 