from util import FrictionAnalyzer


TEST_DATA = 'test_data.csv'
test_analyzer = FrictionAnalyzer(TEST_DATA)
test_analyzer.wave_divide()
print(test_analyzer.wave_division)

test_analyzer.wave_cut()
print(test_analyzer.cuts)

print(test_analyzer.load_force())
print(test_analyzer.friction_force())
print(test_analyzer.friction_coefficient())

print(test_analyzer.friction_trace(0, 10))
print(test_analyzer.friction_trace(10, 100, 10))