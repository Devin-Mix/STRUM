import pygame
import unittest
from queue import Queue
from ConfigurationStateManager import ConfigurationStateManager
from Renderables import *


class RenderableTestCase(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((640, 480))
        self.config = ConfigurationStateManager(Queue(), Queue())

    def test_base_case_functionality(self):
        self.assertEqual(True, True, "Base RenderableTestCase assert failed")


class GenericDerivedTestCase(RenderableTestCase):
    def test_derived_case_functionality(self):
        self.assertEqual(True, True, "Generic derived test case assert failed")

class StringLineTest(RenderableTestCase):
    def test_width_percent_too_large(self):
        with self.assertRaises(ValueError):
            StringLine(101, 50).draw(self.display, self.config)

    def test_y_percent_too_high(self):
        with self.assertRaises(ValueError):
            StringLine(10, 101).draw(self.display, self.config)

    def test_y_percent_too_low(self):
        with self.assertRaises(ValueError):
            StringLine(10, -1).draw(self.display, self.config)

    def test_width_fills_screen(self):
        self.assertIsInstance(StringLine(100, 50).draw(self.display, self.config),
                              StringLine,
                              "StringLine did not return self when width = 100%")

    def test_y_zero(self):
        self.assertIsInstance(StringLine(50, 0).draw(self.display, self.config),
                              StringLine,
                              "StringLine did not return self when y = 0")

    def test_y_one_hundred(self):
        self.assertIsInstance(StringLine(50, 100).draw(self.display, self.config),
                              StringLine,
                              "StringLine did not return self when y = 100")


if __name__ == "__main__":
    unittest.main()