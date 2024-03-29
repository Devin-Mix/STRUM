import numpy as np
import unittest
from queue import Queue
from ConfigurationStateManager import ConfigurationStateManager
from os import environ
from Renderables import *


environ["SDL_VIDEODRIVER"] = "dummy"

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

    def test_average_case(self):
        self.assertIsInstance(StringLine(50, 50).draw(self.display, self.config),
                              StringLine,
                              "StringLine did not return self in average use case")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            StringLine(50, 50).draw(None, self.config)

# TODO: FallingChordTest

class FretLineTest(RenderableTestCase):
    def test_x_percent_too_large(self):
        with self.assertRaises(ValueError):
            FretLine(101, 5).draw(self.display, self.config)

    def test_x_percent_too_small(self):
        with self.assertRaises(ValueError):
            FretLine(-1, 5).draw(self.display, self.config)

    def test_x_percent_zero(self):
        self.assertIsInstance(FretLine(0, 5).draw(self.display, self.config),
                              FretLine,
                              "FretLine did not return self when x_percent = 0")

    def test_x_percent_one_hundred(self):
        self.assertIsInstance(FretLine(100, 5).draw(self.display, self.config),
                              FretLine,
                              "FretLine did not return self when x_percent = 100")

    def test_height_percent_too_large(self):
        with self.assertRaises(ValueError):
            FretLine(50, 96).draw(self.display, self.config)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            FretLine(50, -1).draw(self.display, self.config)

    def test_height_percent_max(self):
        self.assertIsInstance(FretLine(50, 10).draw(self.display, self.config),
                              FretLine,
                              "FretLine did not return self when height_percent = 10 (max)")

    def test_height_percent_min(self):
        self.assertIsInstance(FretLine(50, 0).draw(self.display, self.config),
                              FretLine,
                              "FretLine did not return self when height_percent = 0 (min)")

    def test_average_case(self):
        self.assertIsInstance(FretLine(50, 5).draw(self.display, self.config),
                              FretLine,
                              "FretLine did not return self in average use case")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            FretLine(50, 50).draw(None, self.config)

class FretMarkTest(RenderableTestCase):
    def test_x_percent_too_large(self):
        with self.assertRaises(ValueError):
            FretMark(100, 50).draw(self.display, self.config)

    def test_x_percent_too_small(self):
        with self.assertRaises(ValueError):
            FretMark(0, 50).draw(self.display, self.config)

    def test_x_percent_min(self):
        self.assertIsInstance(FretMark(0.005, 50).draw(self.display, self.config),
                              FretMark,
                              "FretMark did not return self when x_percent = 0.005 (min)")

    def test_x_percent_max(self):
        self.assertIsInstance(FretMark(99.995, 50).draw(self.display, self.config),
                              FretMark,
                              "FretMark did not return self when x_percent = 99.995 (max)")

    def test_y_percent_too_large(self):
        with self.assertRaises(ValueError):
            FretMark(50, 100).draw(self.display, self.config)

    def test_y_percent_too_small(self):
        with self.assertRaises(ValueError):
            FretMark(50, 0).draw(self.display, self.config)

    def test_y_percent_min(self):
        self.assertIsInstance(FretMark(50, 0.005).draw(self.display, self.config),
                              FretMark,
                              "FretMark did not return self when y_percent = 0.005 (min)")

    def test_y_percent_max(self):
        self.assertIsInstance(FretMark(50, 99.995).draw(self.display, self.config),
                              FretMark,
                              "FretMark did not return self when y_percent = 99.995 (max)")

    def test_average_case(self):
        self.assertIsInstance(FretMark(50, 50).draw(self.display, self.config),
                              FretMark,
                              "FretMark did not return self in average use case")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            FretMark(50, 50).draw(None, self.config)

class FadingFretMarkTest(RenderableTestCase):
    def test_x_percent_too_large(self):
        with self.assertRaises(ValueError):
            FadingFretMark(100, 50, 0, 2, 1).draw(self.display, self.config)

    def test_x_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadingFretMark(0, 50, 0, 2, 1).draw(self.display, self.config)

    def test_x_percent_min(self):
        self.assertIsInstance(FadingFretMark(0.005, 50, 0, 2, 1).draw(self.display, self.config),
                              FadingFretMark,
                              "FadingFretMark did not return self when x_percent = 0.005 (min)")

    def test_x_percent_max(self):
        self.assertIsInstance(FadingFretMark(99.995, 50, 0, 2, 1).draw(self.display, self.config),
                              FadingFretMark,
                              "FadingFretMark did not return self when x_percent = 99.995 (max)")

    def test_y_percent_too_large(self):
        with self.assertRaises(ValueError):
            FadingFretMark(50, 100, 0, 2, 1).draw(self.display, self.config)

    def test_y_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadingFretMark(50, 0, 0, 2, 1).draw(self.display, self.config)

    def test_y_percent_min(self):
        self.assertIsInstance(FadingFretMark(50, 0.005, 0, 2, 1).draw(self.display, self.config),
                              FadingFretMark,
                              "FadingFretMark did not return self when y_percent = 0.005 (min)")

    def test_y_percent_max(self):
        self.assertIsInstance(FadingFretMark(50, 99.995, 0, 2, 1).draw(self.display, self.config),
                              FadingFretMark,
                              "FadingFretMark did not return self when y_percent = 99.995 (max)")

    def test_birth_time_future(self):
        with self.assertRaises(ValueError):
            FadingFretMark(50, 50, 1, 2, 0).draw(self.display, self.config)

    def test_time_to_live_exceeded(self):
        with self.assertRaises(ValueError):
            FadingFretMark(50, 50, 0, 2, 2).draw(self.display, self.config)

    def test_average_case(self):
        self.assertIsInstance(FadingFretMark(50, 50, 0, 2, 1).draw(self.display, self.config),
                              FadingFretMark,
                              "FadingFretMark did not return self in average use case")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            FadingFretMark(50, 50, 0, 1, 0.5).draw(None, self.config)

    def test_is_alive(self):
        self.assertEquals(FadingFretMark(50, 50, 0, 1, 0.5).is_alive(), True)

    def test_update_time(self):
        self.assertIsInstance(FadingFretMark(50, 50, 0, 1, 0.5).update_time(0.75),
                              FadingFretMark,
                              "FadingFretMark does not return self after updating time")

class LoadBarTest(RenderableTestCase):
    def test_y_percent_too_large(self):
        with self.assertRaises(ValueError):
            LoadBar(101, 50, 50, 50).draw(self.display, self.config)

    def test_y_percent_too_small(self):
        with self.assertRaises(ValueError):
            LoadBar(-1, 50, 50, 50).draw(self.display, self.config)

    def test_height_percent_too_large(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 50, 101, 50).draw(self.display, self.config)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 50, 0, 50).draw(self.display, self.config)

    def test_height_percent_max(self):
        self.assertIsInstance(LoadBar(50, 50, 100, 50).draw(self.display, self.config),
                              LoadBar,
                              "LoadBar did not return self when height_percent = 100 (max)")

    def test_width_percent_too_large(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 101, 50, 50).draw(self.display, self.config)

    def test_width_percent_too_small(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 0, 50, 50).draw(self.display, self.config)

    def test_width_percent_max(self):
        self.assertIsInstance(LoadBar(50, 100, 50, 50).draw(self.display, self.config),
                              LoadBar,
                              "LoadBar did not return self when width_percent = 100 (max)")

    def test_load_percent_too_low(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 50, 50, -1).draw(self.display, self.config)

    def test_load_percent_too_high(self):
        with self.assertRaises(ValueError):
            LoadBar(50, 50, 50, 101).draw(self.display, self.config)

    def test_average_case(self):
        self.assertIsInstance(LoadBar(50, 50, 50, 50).draw(self.display, self.config),
                              LoadBar,
                              "LoadBar did not return self for average case")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            LoadBar(50, 50, 50, 50).draw(None, self.config)

class TextTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(Text(50, 50, 50, 50, "Hello World!", self.config.regular, align_center=True),
                              Text,
                              "Text did not return self in average use case")

    def test_left_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Text(1, 50, 50, 50, "Hello World!", self.config.regular, align_center=True).draw(self.display, self.config)

    def test_right_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Text(99, 50, 50, 50, "Hello World!", self.config.regular, align_center=True).draw(self.display, self.config)

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Text(50, 1, 50, 50, "Hello World!", self.config.regular, align_center=True).draw(self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Text(50, 99, 50, 50, "Hello World!", self.config.regular, align_center=True).draw(self.display, self.config)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            Text(50, 50, 101, 50, "Hello World!", self.config.regular, align_center=True)\
                .draw(self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            Text(50, 50, 0, 50, "Hello World!", self.config.regular, align_center=True).draw(self.display, self.config)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            Text(50, 50, 50, 101, "Hello World!", self.config.regular, align_center=True)\
                .draw(self.display, self.config)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            Text(50, 50, 50, 0, "Hello World!", self.config.regular, align_center=True)\
                .draw(self.display, self.config)

    def test_bad_x_percent(self):
        with self.assertRaises(ValueError):
            Text(-1, 50, 50, 50, "Hello World!", self.config.regular)

    def test_bad_y_percent(self):
        with self.assertRaises(ValueError):
            Text(50, -1, 50, 50, "Hello World!", self.config.regular)

    def test_bad_align_center_arg(self):
        with self.assertRaises(TypeError):
            Text(50, 50, 50, 50, "Hello World!", self.config.regular, align_center="ASDF")

    def test_bad_font_arg(self):
        with self.assertRaises(TypeError):
            Text(50, 50, 50, 50, "Hello World!", "ASDF")

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            Text(50, 50, 50, 50, "Hello World!").draw(None, self.config)

    def test_very_small_text(self):
        self.assertIsInstance(Text(50, 50, 0.001, 0.001, "Hello World!", self.config.regular).draw(self.display, self.config),
                              Text,
                              "Text did not return self with very small width and height arguments")

    def test_top_left_align_draw(self):
        self.assertIsInstance(
            Text(50, 50, 25, 25, "Hello World!", self.config.regular, align_center=False).draw(self.display, self.config),
            Text,
            "Text did not return self with align_center=False")


class AnalysisGraphTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(AnalysisGraph(50, 50, 50, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10).draw(self.display, self.config),
                              AnalysisGraph,
                              "AnalysisGraph does not return self in average use case")

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(1, 50, 50, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10).draw(
                self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(99, 50, 50, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10).draw(
                self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(50, 0, 50, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(50, 101, 50, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(50, 50, 0, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            AnalysisGraph(50, 50, 101, np.arange(0, 1, 0.01), self.config.regular, self.config.italic, 10)

    def test_bad_regular_font(self):
        with self.assertRaises(TypeError):
            AnalysisGraph(50, 50, 50, np.arange(0, 1, 0.01), 0, self.config.italic, 10)
    def test_bad_italic_font(self):
        with self.assertRaises(TypeError):
            AnalysisGraph(50, 50, 50, np.arange(0, 1, 0.01), self.config.regular, 0, 10)



class ButtonTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(Button(50, 50, 50, 50, "Hello World!", self.config.regular, no_function),
                              Button,
                              "Button did not return self for average case")

    def test_left_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Button(1, 50, 50, 50, "Hello World!", self.config.regular, no_function)

    def test_right_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Button(99, 50, 50, 50, "Hello World!", self.config.regular, no_function)

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Button(50, 1, 50, 50, "Hello World!", self.config.regular, no_function)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Button(50, 99, 50, 50, "Hello World!", self.config.regular, no_function)

    def test_width_percent_too_small(self):
        with self.assertRaises(ValueError):
            Button(50, 50, 0, 50, "Hello World!", self.config.regular, no_function)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            Button(50, 50, 50, 0, "Hello World!", self.config.regular, no_function)

    def test_bad_font(self):
        with self.assertRaises(TypeError):
            Button(50, 50, 50, 50, "Hello World!", 0, no_function)

class ArrowButtonTest(RenderableTestCase):
    def test_average_case_up(self):
        self.assertIsInstance(ArrowButton(50, 50, 50, 50, no_function, 0).draw(self.display, self.config),
                              ArrowButton,
                              "ArrowButton did not return self for average case")
    def test_average_case_right(self):
        self.assertIsInstance(ArrowButton(50, 50, 50, 50, no_function, 1).draw(self.display, self.config),
                              ArrowButton,
                              "ArrowButton did not return self for average case")
    def test_average_case_down(self):
        self.assertIsInstance(ArrowButton(50, 50, 50, 50, no_function, 2).draw(self.display, self.config),
                              ArrowButton,
                              "ArrowButton did not return self for average case")
    def test_average_case_left(self):
        self.assertIsInstance(ArrowButton(50, 50, 50, 50, no_function, 3).draw(self.display, self.config),
                              ArrowButton,
                              "ArrowButton did not return self for average case")

    def test_left_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            ArrowButton(1, 50, 50, 50, no_function, 0)

    def test_right_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            ArrowButton(99, 50, 50, 50, no_function, 0)

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            ArrowButton(50, 1, 50, 50, no_function, 0)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            ArrowButton(50, 99, 50, 50, no_function, 0)

    def test_width_percent_too_small(self):
        with self.assertRaises(ValueError):
            ArrowButton(50, 50, 0, 50, no_function, 0)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            ArrowButton(50, 50, 50, 0, no_function, 0)

    def test_bad_direction(self):
        with self.assertRaises(ValueError):
            ArrowButton(50, 50, 50, 50, no_function, 5001)


            
class FadeInButtonTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(FadeInButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)
                              .draw(self.display, self.config),
                              FadeInButton,
                              "FadeInButton did not return self for average case")

    def test_left_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeInButton(1, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_right_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeInButton(99, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 1, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 99, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_width_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 50, 0, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 50, 50, 0, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_lifespan_exceeded(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 10, 10)

    def test_nothing_to_draw(self):
        with self.assertRaises(ValueError):
            FadeInButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 0, 10)

    def test_bad_font(self):
        with self.assertRaises(TypeError):
            FadeInButton(50, 50, 50, 50, "Hello World!", 0, no_function, 5, 10)

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            FadeInButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10).draw(None, self.config)
            
class FadeOutButtonTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(FadeOutButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)
                              .draw(self.display, self.config),
                              FadeOutButton,
                              "FadeOutButton did not return self for average case")

    def test_left_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeOutButton(1, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_right_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeOutButton(99, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 1, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 99, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_width_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 50, 0, 50, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_height_percent_too_small(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 50, 50, 0, "Hello World!", self.config.regular, no_function, 5, 10)

    def test_nothing_to_draw(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 10, 10)

    def test_lifespan_exceeded(self):
        with self.assertRaises(ValueError):
            FadeOutButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 11, 10)

    def test_bad_font(self):
        with self.assertRaises(TypeError):
            FadeOutButton(50, 50, 50, 50, "Hello World!", 0, no_function, 5, 10)

    def test_bad_screen(self):
        with self.assertRaises(TypeError):
            FadeOutButton(50, 50, 50, 50, "Hello World!", self.config.regular, no_function, 5, 10).draw(None,
                                                                                                       self.config)

class BackgroundBoxTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(BackgroundBox(50, 50, 50, 50),
                              BackgroundBox,
                              "BackgroundBox does not return self in average use case")

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 1, 50, 50).draw(
                self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 99, 50, 50).draw(
                self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 50, 0, 50)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 50, 101, 50)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 50, 50, 0)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            BackgroundBox(50, 50, 50, 101)

class BlackoutTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(Blackout(50, 100).draw(self.display, self.config),
                              Blackout,
                              "Blackout did not return self in average case")

    def test_average_case_fade_in(self):
        self.assertIsInstance(Blackout(50, 100, fade_out=False).draw(self.display, self.config),
                              Blackout,
                              "Blackout did not return self in average case")

    def test_full_blackout(self):
        self.assertIsInstance(Blackout().draw(self.display, self.config),
                              Blackout,
                              "Blackout did not return self in full blackout case")

    def test_nothing_to_draw_fade_out(self):
        with self.assertRaises(ValueError):
            Blackout(5, 5, fade_out=True)

    def test_nothing_to_draw_fade_in(self):
        with self.assertRaises(ValueError):
            Blackout(0, 5, fade_out=False)

    def test_lifespan_exceeded(self):
        with self.assertRaises(ValueError):
            Blackout(6, 5)

class TitleTextTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(TitleText(0.5).draw(self.display, self.config),
                              TitleText,
                              "TitleText did not return self in average case")

    def test_fade_percent_too_low(self):
        with self.assertRaises(ValueError):
            TitleText(-0.1)

    def fade_percent_too_high(self):
        with self.assertRaises(ValueError):
            TitleText(1.1)

class LogoTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(Logo(50, 50, 50, 50, 0).draw(self.display, self.config),
                              Logo,
                              "Logo does not return self in average use case")

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Logo(50, 1, 50, 50, 0).draw(
                self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            Logo(50, 99, 50, 50, 0).draw(
                self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            Logo(50, 50, 0, 50, 0)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            Logo(50, 50, 101, 50, 0)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            Logo(50, 50, 50, 0, 0)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            Logo(50, 50, 50, 101, 0)

    def test_very_thin(self):
        self.assertIsInstance(Logo(50, 50, 1, 99, 0).draw(self.display, self.config),
                              Logo,
                              "Logo did not return self when very thin")

    def test_very_wide(self):
        self.assertIsInstance(Logo(50, 50, 99, 1, 0).draw(self.display, self.config),
                              Logo,
                              "Logo did not return self when very wide")

class CheckBoxTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(CheckBox(50, 50, 50, 50, no_function, True).draw(self.display, self.config),
                              CheckBox,
                              "CheckBox does not return self in average use case")
        
    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 1, 50, 50, no_function, True).draw(
                self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 99, 50, 50, no_function, True).draw(
                self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 50, 0, 50, no_function, True)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 50, 101, 50, no_function, True)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 50, 50, 0, no_function, True)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            CheckBox(50, 50, 50, 101, no_function, True)

    def test_bad_set_arg(self):
        with self.assertRaises(TypeError):
            CheckBox(50, 50, 50, 50, no_function, "ASDF")

class SlideBarTest(RenderableTestCase):
    def test_average_case(self):
        self.assertIsInstance(SlideBar(50, 50, 50, 50, no_function, 50).draw(self.display, self.config),
                              SlideBar,
                              "SlideBar does not return self in average use case")

    def test_top_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 1, 50, 50, no_function, 50).draw(
                self.display, self.config)

    def test_bottom_side_out_of_bounds(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 99, 50, 50, no_function, 50).draw(
                self.display, self.config)

    def test_width_too_small(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 0, 50, no_function, 50)

    def test_width_too_large(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 101, 50, no_function, 50)

    def test_height_too_small(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 50, 0, no_function, 50)

    def test_height_too_large(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 50, 101, no_function, 50)

    def test_cursor_percent_too_low(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 50, 50, no_function, -1)

    def test_cursor_percent_too_high(self):
        with self.assertRaises(ValueError):
            SlideBar(50, 50, 50, 50, no_function, 101)

class NoFunctionTest(RenderableTestCase):
    def test_no_function(self):
        self.assertIsInstance(no_function(None, BackgroundBox),
                              type(None),
                              "no_function does not return None")

if __name__ == "__main__":
    unittest.main()