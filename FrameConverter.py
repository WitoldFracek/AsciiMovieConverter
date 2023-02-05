import asyncio
import io
import math
from pathlib import Path
import tempfile
from argparse import ArgumentParser
import PIL.ImageFont
import aiofiles as aiofiles
from PIL import Image, ImageColor
import cv2
import os
import sys
import numpy as np
import shutil
import moviepy.video.io.ImageSequenceClip
from tqdm import tqdm
# ASCII = ['  ', '..', '<<', 'cc', '77', '33', 'xx', 'ee', 'kk', '##', '■■']
from PIL.Image import Dither
from PIL.ImageDraw import ImageDraw

ASCII_LONG = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_MEDIUM = ASCII_LONG[0::2]
ASCII_SHORT = " .<c73xek#■"
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def open_video_capture(path: str):
    if os.path.exists(path):
        return cv2.VideoCapture(path)
    raise FileNotFoundError(f'No such file or directory: "{path}"')


def get_video_details(video: cv2.VideoCapture):
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


def get_ascii_representation(image: Image.Image, ascii_set: str) -> list[str]:
    ret = []
    chars = len(ascii_set)
    x, y = image.size
    for i in range(y):
        row = ''
        for j in range(x):
            row += ascii_set[image.getpixel((j, i)) * chars // 256] * 2
        ret.append(row)
    return ret


def asciify(frame: np.ndarray, rows_count: int, chars_count: int, ascii_set: str) -> list[str]:
    image = Image.fromarray(frame)
    pixelated = pixelate(image, rows_count, chars_count)
    return get_ascii_representation(pixelated, ascii_set)


def make_empty_image(shape: tuple[int, int, int], rgb: tuple[int, int, int]):
    x, y, colors = shape
    # empty_arr: np.ndarray = np.full(x * y, fill_value=np.array([r, g, b]).reshape((1, -1))).reshape((x, y, -1))
    empty_arr: np.ndarray = np.zeros((x, y, 3))
    empty_arr[:, :, :] = rgb
    target_image: Image.Image = Image.fromarray(empty_arr.astype('uint8'), 'RGB')
    canvas: ImageDraw = ImageDraw(target_image)
    return target_image, canvas


def frame_name(number: int, total: int) -> str:
    return "0" * (int(math.log10(total)) - len(str(number)) + 1) + str(number)


def extract_audio(path, temp_dir: Path):
    full_path = os.path.abspath(path)
    clip = VideoFileClip(full_path)
    clip.audio.write_audiofile(str(temp_dir/'audio.mp3'), verbose=False)


def has_audio(path) -> bool:
    full_path = os.path.abspath(path)
    clip = VideoFileClip(full_path)
    return clip.audio is not None


async def prepare_frames(video, img_shape, frame_count, rows_count, chars_count, font, font_size,
                         frames_dir: Path, ascii_set: str, text_fill: tuple[int, int, int],
                         background_fill: tuple[int, int, int]):
    print(f'Total: {frame_count}')
    print_progress_bar(0, frame_count)
    counter = 0
    for frame in frame_generator(video):
        asciified = asciify(frame, rows_count, chars_count, ascii_set)
        target_image, canvas = make_empty_image(img_shape, background_fill)

        for i, row in enumerate(asciified):
            canvas.text((0, i * font_size), row, fill=text_fill, font=font)

        buffer = io.BytesIO()
        target_image.save(buffer, format='png')
        await image_save(frames_dir/f'fr{frame_name(counter, frame_count)}.png', buffer.getbuffer())
        print_progress_bar(counter, frame_count)
        counter += 1
    print_progress_bar(frame_count, frame_count)


async def image_save(path: Path, image: memoryview):
    async with aiofiles.open(str(path), 'wb') as file:
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
    sys.stdout.flush()
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    if iteration >= total:
        sys.stdout.flush()
        sys.stdout.write(f'\r{prefix} |{fill * length}| 100% {suffix}\n')


def get_program_args():
    parser = ArgumentParser(prog='ASCII Movie Converter',
                            description='Given an mp4 file it converts it to '
                                        'a video clip made out of ASCII characters.')
    parser.add_argument('input_file')
    parser.add_argument('output_file')
    parser.add_argument('-fs', '--fontsize', type=int, required=False, default=15)
    parser.add_argument('-as', '--asciiset', type=str, choices=['short', 'medium', 'long'],
                        required=False, default='medium')
    parser.add_argument('-cs', '--customset', type=str, required=False, default=None)
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('-fg', '--foreground', type=int, nargs=3, dest='fgc', required=False)
    parser.add_argument('-bg', '--background', type=int, nargs=3, dest='bgc', required=False)
    parser.add_argument('--fghex', type=str, required=False)
    parser.add_argument('--bghex', type=str, required=False)
    return parser.parse_args()


def get_ascii_set(args):
    if args.customset:
        return args.customset
    if args.asciiset == 'short':
        return ASCII_SHORT
    if args.asciiset == 'medium':
        return ASCII_MEDIUM
    if args.asciiset == 'long':
        return ASCII_LONG
    raise Exception(f'Invalid value gor ascii set "{args.asciiset}". Should be one of those: short, medium, long')


def are_args_valid(in_path, out_path, font_size, text_fill, background_fill):
    is_ok = True
    if not os.path.exists(in_path):
        print(f'Path does not exist {in_path}')
        is_ok = False
    if os.path.exists(out_path):
        print(f'File {out_path} already exists. It\'ll be overwritten.')
    if font_size < 1:
        print('Font size cannot be less than 1.')
        is_ok = False
    if not is_color_valid(*text_fill):
        print('Invalid rgb values for foreground color. Be sure values range between 0 and 255.')
        is_ok = False
    if not is_color_valid(*background_fill):
        print('Invalid rgb values for background color. Be sure values range between 0 and 255.')
        is_ok = False
    return is_ok


def is_color_valid(r, g, b):
    return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255


def hex_to_rgb(hex_):
    return ImageColor.getcolor(hex_, 'RGB')


def get_colors(args):
    fgr, fgg, fgb = 255, 255, 255
    bgr, bgg, bgb = 0, 0, 0

    if args.fgc:  # fgc - foreground color
        fgr, fgg, fgb = args.fgc

    if args.bgc:  # bgc - background color
        bgr, bgg, bgb = args.bgc

    if args.fghex:
        hex_: str = args.fghex
        if not hex_.startswith('#'):
            hex_ = f'#{hex_}'
        fgr, fgg, fgb = hex_to_rgb(hex_)

    if args.bghex:
        hex_: str = args.bghex
        if not hex_.startswith('#'):
            hex_ = f'#{hex_}'
        bgr, bgg, bgb = hex_to_rgb(hex_)

    return (fgr, fgg, fgb), (bgr, bgg, bgb)


def main():
    working_dir = Path(tempfile.mktemp())
    working_dir.mkdir()
    temp_dir = working_dir/'temp'
    temp_dir.mkdir()
    frames_dir = working_dir/'frames'
    frames_dir.mkdir()

    args = get_program_args()

    text_fill, background_fill = get_colors(args)
    in_path = args.input_file
    out_path = args.output_file
    font_size = args.fontsize
    font_width = font_size
    ascii_set = get_ascii_set(args)
    if args.reverse:
        ascii_set = ascii_set[::-1]
    if not are_args_valid(in_path, out_path, font_size, text_fill, background_fill):
        return

    video = open_video_capture(in_path)
    fps, frame_count, duration = get_video_details(video)

    frame: np.ndarray
    x, y, c = next(frame_generator(video)).shape
    rows_count = x // font_size
    chars_count = y // font_width
    font = PIL.ImageFont.truetype("consola.ttf", size=font_size)

    has_sound = has_audio(in_path)
    if has_sound:
        print("Extracting audio...")
        extract_audio(in_path, temp_dir)

    print("Preparing frames...")
    asyncio.run(prepare_frames(video, (x, y, c), frame_count, rows_count,
                               chars_count, font, font_size, frames_dir, ascii_set, text_fill, background_fill))

    print("Loading images..")
    images = [str(frames_dir/img) for img in tqdm(os.listdir(str(frames_dir))) if img.endswith('.png')]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(images, fps=fps)
    if has_sound:
        clip.audio = AudioFileClip(str(temp_dir/f'audio.mp3'))
    clip.write_videofile(str(out_path), verbose=False)

    shutil.rmtree(str(working_dir))


if __name__ == '__main__':
    main()


