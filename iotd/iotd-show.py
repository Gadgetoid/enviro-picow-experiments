from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY_2
import jpegdec

graphics = PicoGraphics(DISPLAY_PICO_DISPLAY_2)

jpeg = jpegdec.JPEG(graphics)

jpeg.open_file("iotd.jpg")
jpeg.decode()

graphics.update()