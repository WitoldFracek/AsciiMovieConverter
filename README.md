# AsciiMovieConverter
Simple commandline application for converting mp4 movies to videos of frames made out of ascii characters.

## Usage
Command signature:\
```python FrameConverter.py input_file output_file [-h] [-fs FONTSIZE] [-as {short,medium,long}] [-cs CUSTOMSET] [-r]```\
\
Example console command:\
```python FrameConverter.py input.mp4 output.mp4```

## Program parameters
### Positional arguments
**input_file** - path to the video to be converted.\
**output_file** - path to the location where the converted video should be saved.
### Keyword arguments
**-h** - pritns out help page.\
**-fs / --fontsize** - sets the font size for ASCII characters. For smaller characters the 'asciified' resolution of the video will be better and the conversion will take more time. Defaults to 15.\
**-as / --asciiset** - choice: short, medium, long. Specifies the buildin set of characters to use in conversion. Short set contains 11 characters, medium 35, long 71. Defaults to 'medium'.\
**-cs / --customset** - allows user to specify custom set of characters to use in conversion. The characters representing dark pixels should be at the beginning of the string. Defaults to None.\
**-r / --reverse** - reverses the ascii string (the brightest pixels will be treated as the darkest).
