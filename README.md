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
| flag |     name     | arguments  | default     | description                                                                                                                                                    |
|:----:|:------------:|------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  -h  |    --help    | *none*     | -           | prints out help page                                                                                                                                           |
| -fs  |  --fontsize  | int        | 15          | sets the font size for ASCII characters. For smaller characters the 'asciified' resolution of the video will be better and the conversion will take more time. |
| -as  |  --asciiset  | choice     | medium      | choice: short, medium, long. Specifies the builtin set of characters to use in conversion. Short set contains 11 characters, medium 35, long 71.               |
| -cs  | --customset  | string     | None        | allows user to specify custom set of characters to use in conversion. The characters representing dark pixels should be at the beginning of the string.        |
|  -r  |  --reverse   | *none*     | -           | reverses the ascii string (the brightest pixels will be treated as the darkest).                                                                               |
| -fg  | --foreground | 3 ints     | 255 255 255 | allows user to specify the color for the characters used in conversion. Expects 3 integer values: red, green and blue.                                         |
| -gb  | --background | 3 ints     | 0 0 0       | allows user to specify the color for the background of the video. Expects 3 integer values: red, green and blue.                                               |
|  -   |   --fghex    | hex string | None        | allows user to specify the color for the characters used in conversion. Expects hex string.                                                                    |
|  -   |   --bghex    | hex string | None        | allows user to specify the color for the background of the video. Expects hex string.                                                                          |


#### Keyword argument strength
**Customset** is stronger than **asciiset**. If both are given, program uses custom set of characters for conversion.\
**Fghex** and **bghex** are stronger than **foreground** and **background**. If both values for the foreground or background are given, program uses hex color notation.

### Original video - Star Wars the Clone Wars (season 7)
Edit made by: *The Story Of Star Wars* \
YouTube: *https://www.youtube.com/channel/UCGtwO0A-vif_FLuT9Rn9-Aw* \
Video: *https://www.youtube.com/watch?v=JlFC8woFkTA*
![](Ahsoka_vs_Maul.gif)

### Asciified video
#### font size: 5, character set: long
![](Ahsoka_vs_Maul_ascii.gif)