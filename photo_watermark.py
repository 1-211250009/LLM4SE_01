#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Photo Watermark Program
为图片添加基于EXIF拍摄时间的水印
"""

import os
import sys
import argparse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import glob

def get_exif_datetime(image_path):
    """
    从图片的EXIF信息中提取拍摄时间
    返回格式化的日期字符串 (YYYY-MM-DD)
    """
    try:
        with Image.open(image_path) as image:
            exifdata = image.getexif()
            
            # 查找日期时间信息
            datetime_str = None
            for tag_id in exifdata:
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                
                # 查找拍摄时间相关的标签
                if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                    if data:
                        datetime_str = data
                        break
            
            if datetime_str:
                # 解析EXIF日期格式 (YYYY:MM:DD HH:MM:SS)
                try:
                    dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    pass
            
            # 如果没有找到EXIF日期，使用文件修改时间
            file_time = os.path.getmtime(image_path)
            dt = datetime.fromtimestamp(file_time)
            return dt.strftime('%Y-%m-%d')
            
    except Exception as e:
        print(f"读取EXIF信息失败 {image_path}: {e}")
        # 使用文件修改时间作为备选
        try:
            file_time = os.path.getmtime(image_path)
            dt = datetime.fromtimestamp(file_time)
            return dt.strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')

def get_text_position(img_width, img_height, text_width, text_height, position):
    """
    根据位置参数计算文本的坐标
    """
    positions = {
        'top-left': (10, 10),
        'top-center': ((img_width - text_width) // 2, 10),
        'top-right': (img_width - text_width - 10, 10),
        'center-left': (10, (img_height - text_height) // 2),
        'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
        'center-right': (img_width - text_width - 10, (img_height - text_height) // 2),
        'bottom-left': (10, img_height - text_height - 10),
        'bottom-center': ((img_width - text_width) // 2, img_height - text_height - 10),
        'bottom-right': (img_width - text_width - 10, img_height - text_height - 10)
    }
    return positions.get(position, positions['bottom-right'])

def add_watermark(image_path, output_path, font_size=24, color='white', position='bottom-right'):
    """
    为图片添加水印
    """
    try:
        # 打开图片
        with Image.open(image_path) as image:
            # 转换为RGB模式（如果是RGBA，保持透明度）
            if image.mode != 'RGB' and image.mode != 'RGBA':
                image = image.convert('RGB')
            
            # 获取拍摄时间
            date_str = get_exif_datetime(image_path)
            
            # 创建绘图对象
            draw = ImageDraw.Draw(image)
            
            # 尝试加载字体，如果失败则使用默认字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # 获取文本尺寸
            bbox = draw.textbbox((0, 0), date_str, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 计算文本位置
            x, y = get_text_position(image.width, image.height, text_width, text_height, position)
            
            # 添加阴影效果（可选）
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), date_str, font=font, fill='black')
            
            # 绘制文本
            draw.text((x, y), date_str, font=font, fill=color)
            
            # 保存图片
            image.save(output_path, quality=95)
            print(f"✓ 已处理: {os.path.basename(image_path)} -> {os.path.basename(output_path)}")
            
    except Exception as e:
        print(f"✗ 处理失败 {image_path}: {e}")

def process_directory(input_dir, font_size=24, color='white', position='bottom-right'):
    """
    处理目录中的所有图片文件
    """
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    
    # 创建输出目录 - 在原目录名后添加_watermark
    # 如果input_dir以/结尾，去掉末尾的/
    clean_dir = input_dir.rstrip('/')
    output_dir = f"{clean_dir}_watermark"
    os.makedirs(output_dir, exist_ok=True)
    
    # 查找所有图片文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        image_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    
    if not image_files:
        print(f"在目录 {input_dir} 中没有找到支持的图片文件")
        return
    
    print(f"找到 {len(image_files)} 个图片文件")
    print(f"输出目录: {output_dir}")
    print("-" * 50)
    
    # 处理每个图片文件
    for image_path in image_files:
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}_watermark{ext}")
        add_watermark(image_path, output_path, font_size, color, position)

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='为图片添加基于EXIF拍摄时间的水印')
    parser.add_argument('input_path', help='输入图片文件或目录路径')
    parser.add_argument('-s', '--size', type=int, default=24, help='字体大小 (默认: 24)')
    parser.add_argument('-c', '--color', default='white', help='水印颜色 (默认: white)')
    parser.add_argument('-p', '--position', 
                       choices=['top-left', 'top-center', 'top-right',
                               'center-left', 'center', 'center-right',
                               'bottom-left', 'bottom-center', 'bottom-right'],
                       default='bottom-right', help='水印位置 (默认: bottom-right)')
    
    args = parser.parse_args()
    
    # 检查输入路径
    if not os.path.exists(args.input_path):
        print(f"错误: 路径 {args.input_path} 不存在")
        sys.exit(1)
    
    print("=" * 60)
    print("Photo Watermark Program")
    print("=" * 60)
    print(f"输入路径: {args.input_path}")
    print(f"字体大小: {args.size}")
    print(f"水印颜色: {args.color}")
    print(f"水印位置: {args.position}")
    print("=" * 60)
    
    if os.path.isfile(args.input_path):
        # 处理单个文件
        filename = os.path.basename(args.input_path)
        name, ext = os.path.splitext(filename)
        # 获取文件所在目录，并在目录名后添加_watermark
        file_dir = os.path.dirname(args.input_path)
        if file_dir:  # 如果文件不在当前目录
            output_dir = f"{file_dir}_watermark"
        else:  # 如果文件在当前目录
            output_dir = f"{os.path.basename(os.getcwd())}_watermark"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{name}_watermark{ext}")
        add_watermark(args.input_path, output_path, args.size, args.color, args.position)
    else:
        # 处理目录
        process_directory(args.input_path, args.size, args.color, args.position)
    
    print("=" * 60)
    print("处理完成!")

if __name__ == "__main__":
    main()
