import unittest
from unittest.mock import patch
from io import StringIO
from hardware.mock_hardware import MockHardware
from led_control.led_management import LEDManager
from operations.interfaces.command_interface import CommandInterface
from operations.commands.led_commands import OnCommand, OffCommand, FadeCommand, PatternCommand

class TestCommandInterface(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.hardware = MockHardware()
        self.led_manager = LEDManager(self.hardware)
        self.interface = CommandInterface()
        self.interface.set_context('led_manager', self.led_manager)
    
    def test_command_registration(self):
        """Test that commands are properly registered"""
        # Check that default commands are registered
        self.assertIn('on', self.interface.commands)
        self.assertIn('off', self.interface.commands)
        self.assertIn('fade', self.interface.commands)
        self.assertIn('pattern', self.interface.commands)
        
        # Check command types
        self.assertIsInstance(self.interface.commands['on'], OnCommand)
        self.assertIsInstance(self.interface.commands['off'], OffCommand)
        self.assertIsInstance(self.interface.commands['fade'], FadeCommand)
        self.assertIsInstance(self.interface.commands['pattern'], PatternCommand)
    
    def test_context_management(self):
        """Test context setting and getting"""
        # Test setting context
        self.interface.set_context('test_key', 'test_value')
        self.assertEqual(self.interface.get_context('test_key'), 'test_value')
        
        # Test getting non-existent context
        self.assertIsNone(self.interface.get_context('non_existent'))
    
    def test_help_command(self):
        """Test help text generation"""
        help_text = self.interface.get_help()
        self.assertIn('on:', help_text)
        self.assertIn('off:', help_text)
        self.assertIn('fade:', help_text)
        self.assertIn('pattern:', help_text)

class TestLEDCommands(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.hardware = MockHardware()
        self.led_manager = LEDManager(self.hardware)
        self.context = {'led_manager': self.led_manager}
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_on_command(self, mock_stdout):
        """Test the on command"""
        command = OnCommand()
        
        # Test valid command
        self.assertTrue(command.execute(['0', '1'], self.context))
        self.assertEqual(self.led_manager.get_led_state(0), 1.0)
        self.assertEqual(self.led_manager.get_led_state(1), 1.0)
        
        # Test invalid arguments
        self.assertFalse(command.execute([], self.context))
        self.assertIn('Usage: on <led_id>', mock_stdout.getvalue())
        
        # Clear stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        self.assertFalse(command.execute(['invalid'], self.context))
        self.assertIn('Error: LED IDs must be numbers', mock_stdout.getvalue())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_off_command(self, mock_stdout):
        """Test the off command"""
        command = OffCommand()
        
        # Turn on LEDs first
        self.led_manager.set_led(0, 1.0)
        self.led_manager.set_led(1, 1.0)
        
        # Test valid command
        self.assertTrue(command.execute(['0', '1'], self.context))
        self.assertEqual(self.led_manager.get_led_state(0), 0.0)
        self.assertEqual(self.led_manager.get_led_state(1), 0.0)
        
        # Test invalid arguments
        self.assertFalse(command.execute([], self.context))
        self.assertIn('Usage: off <led_id>', mock_stdout.getvalue())
        
        # Clear stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        self.assertFalse(command.execute(['invalid'], self.context))
        self.assertIn('Error: LED IDs must be numbers', mock_stdout.getvalue())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_fade_command(self, mock_stdout):
        """Test the fade command"""
        command = FadeCommand()
        
        # Test valid command
        self.assertTrue(command.execute(['0', '0.5'], self.context))
        
        # Test invalid arguments
        self.assertFalse(command.execute([], self.context))
        self.assertIn('Usage: fade <led_id>', mock_stdout.getvalue())
        
        # Clear stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        self.assertFalse(command.execute(['0'], self.context))
        self.assertIn('Usage: fade <led_id>', mock_stdout.getvalue())
        
        # Clear stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        self.assertFalse(command.execute(['invalid', '0.5'], self.context))
        self.assertIn('Error: Invalid arguments', mock_stdout.getvalue())
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_pattern_command(self, mock_stdout):
        """Test the pattern command"""
        command = PatternCommand()
        
        # Test valid command
        self.assertFalse(command.execute(['test_pattern'], self.context))
        self.assertIn('Pattern \'test_pattern\' not implemented yet', mock_stdout.getvalue())
        
        # Clear stdout
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        
        # Test invalid arguments
        self.assertFalse(command.execute([], self.context))
        self.assertIn('Usage: pattern <pattern_name>', mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main() 