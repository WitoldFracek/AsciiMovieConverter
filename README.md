# AsciiMovieConverter
Simple commandline application for converting mp4 movies to videos of frames made out of ascii characters

## Usage
```python FrameConverter.py input.mp4 output.mp4```

## Program parameters
### Positional arguments
input_file - path to the video to be converted.
output_file - path to the location where the converted video should be saved.
### Keyword arguments
-h - pritns out help page.
-fs / --fontsize - sets the font size for ASCII characters. For smaller characters the 'asciified' resolution of the video will be better and the conversion will take more time. Defaults to 15.
-as / --asciiset - choice: short, medium, long. Specifies the buildin set of characters to use in conversion.
  short: `" .<c73xek#■"`
  medium: `""`
  long: `" .'\`^\",:;Il!i><~+\_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao\*#MW&8%B@$"`
