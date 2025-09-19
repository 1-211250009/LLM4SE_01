# Photo Watermark 使用说明

## 功能描述
这是一个命令行图片水印程序，可以为图片添加基于EXIF拍摄时间的水印。

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法
```bash
# 处理单个图片文件
python photo_watermark.py /path/to/image.jpg

# 处理整个目录
python photo_watermark.py /path/to/images/
```

### 高级选项
```bash
python photo_watermark.py /path/to/images/ -s 32 -c red -p top-left
```

### 参数说明
- `input_path`: 输入图片文件或目录路径（必需）
- `-s, --size`: 字体大小（默认: 24）
- `-c, --color`: 水印颜色（默认: white）
- `-p, --position`: 水印位置，可选值：
  - `top-left`: 左上角
  - `top-center`: 顶部居中
  - `top-right`: 右上角
  - `center-left`: 左侧居中
  - `center`: 正中央
  - `center-right`: 右侧居中
  - `bottom-left`: 左下角
  - `bottom-center`: 底部居中
  - `bottom-right`: 右下角（默认）

## 支持的图片格式
- JPG/JPEG
- PNG
- BMP
- TIFF/TIF

## 输出
- 处理后的图片会保存在 `原目录名_watermark` 子目录中
- 文件名格式：`原文件名_watermark.扩展名`

## 示例
```bash
# 处理当前目录下的Img文件夹
python photo_watermark.py Img/

# 自定义水印样式
python photo_watermark.py Img/ -s 36 -c yellow -p bottom-right
```

## 注意事项
- 如果图片没有EXIF信息，程序会使用文件的修改时间作为水印
- 程序会自动创建输出目录
- 支持批量处理整个目录中的所有图片
