import asyncio
import io
import math
from typing import Generator

import PIL.ImageFont
import aiofiles as aiofiles
from PIL import Image, ImageOps
import cv2
import os
import sys
import numpy as np
import shutil
import moviepy.video.io.ImageSequenceClip
# ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '■■']
from PIL.Image import Dither
from PIL.ImageDraw import ImageDraw

# ASCII = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

ASCII = " .<c73xek#■"
CHARS = len(ASCII)
FONT_SIZE = 15
FONT_WIDTH = 16

TEMP_DIR = './temp/'
TEMP_FILE = './temp/temp.'
FRAMES_DIR = './frames/'


def copy_file(path, ext='mp4'):
    if os.path.exists(path):
        copy_path = f'{TEMP_FILE}{ext}'
        if not os.path.exists(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        if os.path.exists(copy_path):
            os.remove(copy_path)
        shutil.copy2(path, copy_path)
        return copy_path
    raise FileNotFoundError(f'No such file or directory: "{path}"')


def open_video_capture(path: str):
    if os.path.exists(path):
        return cv2.VideoCapture(path)
    raise FileNotFoundError(f'No such file or directory: "{path}"')


def get_video_details(video):
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    return fps, frame_count, duration


def frame_generator(video):
    success = 1
    while success:
        success, image = video.read()
        if success:
            yield image


def pixelate(image: Image.Image, target_x, target_y) -> Image:
    im = image.resize((target_y, target_x), Dither.NONE)
    im = im.convert('L')
    return im


def get_ascii_representation(image: Image.Image) -> list[str]:
    ret = []
    x, y = image.size
    for i in range(y):
        row = ''
        for j in range(x):
            row += ASCII[image.getpixel((j, i)) * CHARS // 256] * 2
        ret.append(row)
    return ret


def asciify(frame: np.ndarray, rows_count: int, chars_count: int) -> list[str]:
    image = Image.fromarray(frame)
    pixelated = pixelate(image, rows_count, chars_count)
    return get_ascii_representation(pixelated)


def prepare_directories(path):
    if os.path.exists(path):
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))
    else:
        os.mkdir(path)


def make_empty_image(shape: tuple[int, int, int]):
    x, y, colors = shape
    empty_arr: np.ndarray = np.full(x * y * colors, fill_value=0).reshape(shape)
    target_image: Image.Image = Image.fromarray(empty_arr.astype('uint8'), 'RGB')
    canvas: ImageDraw = ImageDraw(target_image)
    return target_image, canvas


def frame_name(number: int, total: int) -> str:
    return "0" * (int(math.log10(total)) - len(str(number)) + 1) + str(number)


def extract_audio(path):
    full_path = os.path.abspath(path)
    clip = VideoFileClip(full_path)
    clip.audio.write_audiofile(f'{TEMP_DIR}audio.mp4', codec='pcm_s32le')


async def prepare_frames(video, img_shape, frame_count, rows_count, chars_count, font):
    print(f'Preparing frames...\nTotal: {frame_count}')
    print_progress_bar(0, frame_count)
    counter = 0
    for frame in frame_generator(video):
        asciified = asciify(frame, rows_count, chars_count)
        target_image, canvas = make_empty_image(img_shape)

        for i, row in enumerate(asciified):
            canvas.text((0, i * FONT_SIZE), row, fill=(255, 255, 255), font=font)

        buffer = io.BytesIO()
        target_image.save(buffer, format='png')
        await image_save(f'{FRAMES_DIR}fr{frame_name(counter, frame_count)}.png', buffer.getbuffer())
        print_progress_bar(counter, frame_count)
        counter += 1


async def image_save(path: str, image: memoryview):
    async with aiofiles.open(path, 'wb') as file:
        await file.write(image)


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()


def main():
    prepare_directories(TEMP_DIR)
    prepare_directories(FRAMES_DIR)

    in_path = sys.argv[1]
    out_path = sys.argv[2]
    video = open_video_capture(in_path)
    fps, frame_count, duration = get_video_details(video)

    frame: np.ndarray
    x, y, c = next(frame_generator(video)).shape
    rows_count = x // FONT_SIZE
    chars_count = y // FONT_WIDTH
    font = PIL.ImageFont.truetype("consola.ttf", size=FONT_SIZE)

    # print("Extracting audio...")
    # extract_audio(in_path)

    asyncio.run(prepare_frames(video, (x, y, c), frame_count, rows_count, chars_count, font))

    images = [os.path.join(FRAMES_DIR, img) for img in os.listdir(FRAMES_DIR) if img.endswith('.png')]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(images, fps=fps)
    # clip.audio = AudioFileClip(f'{TEMP_DIR}/.audio.mp4')
    clip.write_videofile(out_path)

    prepare_directories(TEMP_DIR)
    prepare_directories(FRAMES_DIR)


if __name__ == '__main__':
    main()


