# AsciiMovieConverter
Simple commandline application for converting mp4 movies to videos of frames made out of ascii characters.

## Usage
Example console command:\
```python FrameConverter.py input.mp4 output.mp4```

## Program parameters
### Positional arguments
**input_file** - path to the video to be converted.\
**output_file** - path to the location where the converted video should be saved.
### Keyword arguments
| flag |     name     | default       | description                                                                                                                                                               |
|:----:|:------------:|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  -h  |    --help    | -             | prints out help page                                                                                                                                                      |
| -fs  |  --fontsize  | 15            | sets the font size for ASCII characters. For smaller characters the 'asciified' resolution of the video will be better and the conversion will take more time             |
| -as  |  --asciiset  | medium        | choice: short, medium, long. Specifies the buildin set of characters to use in conversion. Short set contains 11 characters, medium 35, long 71. Defaults to 'medium'.    |
| -cs  | --customset  | None          | allows user to specify custom set of characters to use in conversion. The characters representing dark pixels should be at the beginning of the string. Defaults to None. |
|  -r  |  --reverse   | -             | reverses the ascii string (the brightest pixels will be treated as the darkest).                                                                                          |
| -fg  | --foreground | 255, 255, 255 | allows user to specify the color for the characters used in conversion. Expects 3 intiger values: red, green and blue. Defaults to 255, 255, 255.                         |
| -gb  | --background | 0, 0, 0       | allows user to specify the color for the background of the video. Expects 3 intiger values: red, green and blue. Defaults to 0, 0, 0.                                     |
|  -   |   --fghex    | None          | allows user to specify the color for the characters used in conversion. Expects hex string. Defaults to #FFFFFF.                                                          |
|  -   |   --bghex    | None          | allows user to specify the color for the background of the video. Expects hex string. Defaults to #000000                                                                 |


#### Keyword argument strength
**Customset** is stronger than **asciiset**. If both are given, program uses custom set of characters for conversion.\
**Fghex** and **bghex** are stronger than **foreground** and **background**. If both values for the foreground or background are given, program uses hex color notation.

### Original video
![](NoAscii.gif)

### Asciified video
![](Ascii.gif)