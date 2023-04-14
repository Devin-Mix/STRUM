import numpy as np
import unittest
from queue import Queue
from AnalysisStateManager import AnalysisStateManager
from ConfigurationStateManager import ConfigurationStateManager
from os import environ
from Renderables import *


environ["SDL_VIDEODRIVER"] = "dummy"

class AnalysisStateManagerTestCase(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.display = pygame.display.set_mode((640, 480))
        self.config = ConfigurationStateManager(Queue(), Queue())
        self.AnalysisStateManager = AnalysisStateManager(Queue(), Queue())

    def test_base_case_functionality(self):
        self.assertEqual(True, True, "Base AnalysisStateManagerTestCase assert failed")