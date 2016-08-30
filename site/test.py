import unittest
import wwwnethack

class TestZScore(unittest.TestCase):
    def test_zscore(self):
        self.assertEqual(wwwnethack.calculate_z(1), 1.0)
        self.assertEqual(wwwnethack.calculate_z(2), 1.5)
        self.assertEqual(wwwnethack.calculate_z(3), 1.75)

def run_tests():
    unittest.main()
    

if __name__ == '__main__':
    run_tests()
