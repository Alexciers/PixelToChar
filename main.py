import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 根据颜色深浅映射出的字符列表，共70个
ascii_char = [
    "@", "#", "8", "&", "%", "W", "M", "B", "8", "=", "*", "+", "%", "=", "-", "!",
    ";", ":", ">", "<", "I", "l", "(", ")", "/", "|", "[", "]", "{", "}", "1", "2", "3",
    "4", "5", "6", "7", "8", "9", "0", "q", "w", "e", "r", "t", "y", "u", "i", "p", "a",
    "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m", "A", "Z",
    "O", "P", "Q", "L", "C", "J", "U", "Y", "X", "V", "R", "S", "T", "W", "F", "G", "H",
    "K", "N", "o", "l", "I", ";", ":", ",", ".", "'", " ", "`", "^", "~", "-", "_", "=",
    "+", "<", ">", "?", "!", " ", ".", ",", " ", "`", ".", "^", "-", "_", "~", "~"
]



# 每个字符占据的区间为unit_length
unit_length = (256.0+1) / len(ascii_char)


def get_char_ave_height_width(char_list):
    # 加载默认字体
    font = ImageFont.load_default()

    sum_height = 0
    sum_width = 0
    for char in char_list:
        bbox = font.getbbox(char)  # 获取字符的边界框
        width = bbox[2] - bbox[0]  # 宽度
        height = bbox[3] - bbox[1]  # 高度
        sum_height += height
        sum_width += width

    ave_height = sum_height // len(char_list)
    ave_width = sum_width // len(char_list)

    return ave_height, ave_width;


# 获得字符列表的平均长宽比
ave_height, ave_width = get_char_ave_height_width(ascii_char)
char_aspect_ratio = ave_height // ave_width
ave_height_line = (ave_height + ave_width) // 2

def convert_to_pixel_image(gray_image):
    # 获取图像的宽高
    height, width = gray_image.shape

    # 根据字符的长宽比来选择是否跳过行或列
    line_skip = 1  # 默认每行都存储
    column_skip = 1  # 默认每列都存储

    if(char_aspect_ratio > 1):
        line_skip = char_aspect_ratio  # 每char_aspect_ratio行存储一次字符
    else:
        column_skip = char_aspect_ratio  # 每char_aspect_ratio列存储一次字符

    # 根据原图大小调整跳过的行列数
    column_line_skip = ave_height_line
    line_skip = line_skip * column_line_skip
    column_skip = column_skip * column_line_skip
    # 创建字符数组
    pixel_image_array = np.empty_like(gray_image[::line_skip, ::column_skip], dtype="<U1")

    # 填充字符数组
    for index_line, line in enumerate(gray_image[::line_skip, ::column_skip]):
        for index_pixel, pixel in enumerate(line):
            pixel_image_array[index_line][index_pixel] = ascii_char[int( pixel / unit_length)]

    # 获取字符图像的宽高
    height, width = pixel_image_array.shape

    # 计算字符画的宽高
    char_image_width = width * ave_height
    char_image_height = height * ave_width

    # 重新计算字符画的宽高，以确保不出现多余的空白区域
    # 适应图像的宽高比
    aspect_ratio = width / height
    new_char_image_width = int(char_image_height * aspect_ratio)

    # 创建一个空白的图像，用于绘制字符
    char_image = Image.new('L', (new_char_image_width, char_image_height), color=255)  # 使用'L'模式，表示单通道灰度图像
    draw = ImageDraw.Draw(char_image)

    # 使用默认字体绘制字符
    font = ImageFont.load_default()  # 使用默认字体
    for y in range(height):
        for x in range(width):
            char = pixel_image_array[y, x]
            # 在每个字符位置绘制字符（将每个字符填充为灰度）
            draw.text((x * ave_width, y * ave_height), char, fill=0, font=font)  # 0表示黑色字符

    # 将字符图像转换为 NumPy 数组，确保输出是灰度图像或 RGB 图像
    return char_image

def main():
    # 读取视频文件
    input_video_path = 'yuzi.mp4'
    output_video_path = 'output_video.mp4'

    reader = imageio.get_reader(input_video_path)
    fps = reader.get_meta_data()['fps']  # 获取帧率
    writer = imageio.get_writer(output_video_path, fps=fps)

    # 遍历视频帧
    # 获取视频总帧数
    frames = [frame for frame in reader]  # 将所有帧保存到列表
    total_frames = len(frames)
    for frame_idx, frame in enumerate(reader):
        print("共" + str(total_frames) + "帧，" + "正在处理第" + str(frame_idx + 1) + "帧: \n")
        # print("正在处理第" + str(frame_idx + 1) + "帧: \n")

        # 转换为灰度图像
        gray_frame = np.dot(frame[..., :3], [0.2989, 0.5870, 0.1140])

        # 生成字符画+
        pixel_image = convert_to_pixel_image(gray_frame)
        pixel_image_frame = np.array(pixel_image)

        if (frame_idx + 1) % 100 == 0:
            pixel_image.show()

        # 将处理后的帧写入输出视频
        writer.append_data(pixel_image_frame)

    # 关闭 writer
    writer.close()

# 调用主函数
main()
