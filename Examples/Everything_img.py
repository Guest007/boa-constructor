# Boa:PyImgResource:

import io

from wx import BitmapFromImage, ImageFromStream

# ----------------------------------------------------------------------


def getBoaData():
    return \
        '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\x95IDATx\x9c}\x93}\x91\x1b1\x0c\xc5\x7f{\x13\x00\x86`\x08b\xb0\n\
\x82.\x04\x97A\x8a \x1b\x04g\x08\x86P\x06\xabE\xd0\x85\xa000\x03\xf7\x8f\xfd\
\xc8%\x97\xf6\xcdhF\xf6\xf8=\xe9\xd9r\xd7Zkl8\x9fo\x00\x98\x81*L\xd3\x95\xff\
\xe1~\xbf\xd3\xb5\xd6\xda<\xcf\x94R\x80r\x90K1R*\xa4\x94\xfe)`f\x9c\xf6\x85\
\xbbo\xc4U@\xd5\xa8\xb5\xe2\xee\xdf\x88"B\xad\x15\xe0Y\xc0\x1dRRR2JQ\xc0\x08\
\xc1\x10\x11D\xe4\x10\x08!\x1c\x02\x9d\x995U\x03\xde\xf8\xd5\x19l\xaf\xfa\
\x9b\x9c\x07\x00b\x8c\xb8;f\xc6\xc7JV`\xfeBd%N=\x8c\x06\xf4,\xcb\xe7vO\xcf\
\xf8@\x01\xed\xb7\xd8\x88\xe3\x0c\xe3\xf9I\x13\xa0\x94\xf8M\xe0\xa4\n\xa6_v\
\xc6\xf3\xd6\xc5\xb4\xe6:\xc1\xc8\x1ao\xf01]\xaf\xa0\x1d\xa6\x1d\xaa\xdd\xda\
\xff8!\xf5\x17)\xc6GW\x80H}ca\xef\xda\x0c\xb3\x06\n\xa9\xfcD\xaaPbZ+\x1b\xc0\
LJo,p\xbbQE\x089\x93BAD(\xcb\xc0\xf2\xe7\x07\x9c\x1f\xe4\x9c\x97\xa7\xa7\x84\
\xf5\xe9O\\\xaf\xc4\x10\x18B \xe7\x85\xe2\x02\xb9\x87n?6#r\x01\x12\x00\xa5\
\x14\x86a\xc0\xdd)\xc5\xa1\xb5\xd6\xcc\xac].\x97\x86Y\xa3\xb5\x06{\xd8\x16k.\
ry\xd9\x1f\xdb1\x89\xcb\xb2@\xf8|q\xd8?\xe5\xcb\xd2\x03\xf3z\xb1@\x8a\xfe\
\x18\xe5a\x18\xb0:\x83\xf5\xabo\x03l?\xbc\t\x8d7r\x0e\x87d\xad\x91\xce\xdd\
\xdb>a\xeeN\x89\x11\x0cb\xf4\xbd\xd0\xf1\xa1T\x95W\xfc\x05\x9b8\xd9j\xa1\xaa\
\x82\x9a\x00\x00\x00\x00IEND\xaeB`\x82'


def getBoaBitmap():
    return BitmapFromImage(getBoaImage())


def getBoaImage():
    stream = io.StringIO(getBoaData())
    return ImageFromStream(stream)
