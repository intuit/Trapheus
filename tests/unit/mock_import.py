import sys

sys.modules['custom_exceptions'] = __import__('mock_custom_exceptions')
sys.modules['utility'] = __import__('mock_utility')
sys.modules['constants'] = __import__('mock_constants')