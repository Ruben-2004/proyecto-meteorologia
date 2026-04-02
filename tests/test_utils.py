from weather.utils import celsius_to_fahrenheit


class TestCelsiusToFahrenheit:
    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_boiling_point(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_negative_forty_is_equal_in_both_scales(self):
        assert celsius_to_fahrenheit(-40) == -40.0
