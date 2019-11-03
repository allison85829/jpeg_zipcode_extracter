import unittest
import imggps
import sys, os

# assuming all the test images are in the same folder as test.py
class TestImgZipcode(unittest.TestCase): 
    def setup(self):
        pass

    def test_disney_img(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/disney.jpg"), 92802)

    def test_slo_img(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/lunch.jpg"), 93405)

    def test_not_exif_app_marker(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/grey.jpeg"), -1)

    def test_outside_us(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/thailand.JPG"), -1)

    def test_not_jpeg(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/night.HEIC"), -1)

    def test_little_endian(self):
        self.assertEqual(imggps.getzipcode(os.getcwd() + "/beach_little_endian.jpg"), 93449)
    
if __name__ == "__main__":
    unittest.main()

