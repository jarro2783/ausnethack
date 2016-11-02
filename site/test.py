import unittest
import wwwnethack
fhr = wwwnethack.format_human_readable

class TestZScore(unittest.TestCase):
    def test_zscore(self):
        self.assertEqual(wwwnethack.calculate_z(1), 1.0)
        self.assertEqual(wwwnethack.calculate_z(2), 1.5)
        self.assertEqual(wwwnethack.calculate_z(3), 1.75)

    def test_basic_scores(self):
        ascended = [
            {'plname': 'a', 'role': 'Wizard', 'number': 1},
            {'plname': 'b', 'role': 'Ranger', 'number': 1},
        ]

        scores, roles = wwwnethack.calculate_zscores(ascended)

        self.assertEqual(scores['a']['total'], 1.0)
        self.assertEqual(scores['a']['roles']['Wizard'], 1.0)
        self.assertEqual(scores['b']['total'], 1.0)
        self.assertEqual(scores['b']['roles']['Ranger'], 1.0)

        self.assertEqual(roles[0], 'Ranger')
        self.assertEqual(roles[1], 'Wizard')

class TestFormatSeconds(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(fhr(0), '0 seconds')
        self.assertEqual(fhr(1), '1 second')
        self.assertEqual(fhr(2), '2 seconds')
        self.assertEqual(fhr(61), '1 minute 1 second')
        self.assertEqual(fhr(184), '3 minutes 4 seconds')
        self.assertEqual(fhr(3632), '1 hour 32 seconds')

def run_tests():
    unittest.main()
    

if __name__ == '__main__':
    run_tests()
