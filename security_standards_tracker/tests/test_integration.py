"""
Test module for the security standards tracker.

This file contains integration tests for the security standards tracker.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from security_standards_tracker.core.tracker import SecurityStandardsTracker
from security_standards_tracker.core.web_fetcher import SecurityNewsFetcher
from security_standards_tracker.core.version_manager import StandardsVersionManager
from security_standards_tracker.config import STANDARDS_VERSIONS_PATH, STANDARDS_CHANGES_PATH

class TestSecurityStandardsTracker(unittest.TestCase):
    """Test case for the security standards tracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test directories
        self.test_versions_path = os.path.join("tests", "test_standards_versions")
        self.test_changes_path = os.path.join("tests", "test_standards_changes")
        
        os.makedirs(self.test_versions_path, exist_ok=True)
        os.makedirs(self.test_changes_path, exist_ok=True)
        
        # Create a version manager for testing
        self.version_manager = StandardsVersionManager(
            self.test_versions_path,
            self.test_changes_path
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up test files
        for file in Path(self.test_versions_path).glob("*.json"):
            file.unlink()
        
        for file in Path(self.test_changes_path).glob("*.json"):
            file.unlink()
    
    @patch.object(SecurityNewsFetcher, 'fetch_security_standards_news')
    def test_fetch_and_process_standards(self, mock_fetch):
        """Test fetching and processing standards."""
        # Mock fetch results
        mock_fetch.return_value = [
            {
                "title": "New NIST SP 800-53 Updates",
                "content": "This is a test content for NIST SP 800-53 updates. " + 
                           "The document includes new security controls and guidelines" * 10,
                "url": "https://example.com/nist-updates"
            },
            {
                "title": "ISO 27001 Revised",
                "content": "ISO 27001 has been revised with new requirements for " +
                           "information security management systems." * 10,
                "url": "https://example.com/iso-27001"
            }
        ]
        
        # Create tracker with mocked components
        with patch('security_standards_tracker.core.tracker.StandardsVersionManager', 
                  return_value=self.version_manager):
            with patch('security_standards_tracker.core.tracker.RAGFactory'):
                tracker = SecurityStandardsTracker()
                
                # Mock the _add_to_vector_db method
                tracker._add_to_vector_db = MagicMock()
                tracker._update_in_vector_db = MagicMock()
                
                # Run the fetch cycle
                tracker.run_fetch_cycle()
                
                # Verify standards were added
                standards = self.version_manager.get_all_standards()
                self.assertTrue(len(standards) > 0)
                
                # Check that the standards have the expected names
                standard_names = [std["name"] for std in standards]
                self.assertTrue(any("NIST" in name for name in standard_names) or 
                               any("ISO" in name for name in standard_names))

    def test_version_manager_add_standard(self):
        """Test adding a standard to the version manager."""
        # Add a new standard
        standard_name = "Test Standard"
        standard_content = "This is a test standard content." * 20
        
        standard_id, version_id, is_new = self.version_manager.add_standard(
            standard_name, standard_content
        )
        
        # Verify the standard was added
        self.assertTrue(is_new)
        self.assertIsNotNone(standard_id)
        self.assertIsNotNone(version_id)
        
        # Get the standard and verify its properties
        standards = self.version_manager.get_all_standards()
        self.assertEqual(len(standards), 1)
        self.assertEqual(standards[0]["name"], standard_name)
        
        # Add a new version of the same standard
        updated_content = standard_content + "\nNew addition to the standard."
        
        new_standard_id, new_version_id, is_new = self.version_manager.add_standard(
            standard_name, updated_content
        )
        
        # Verify it's recognized as an update
        self.assertFalse(is_new)
        self.assertEqual(standard_id, new_standard_id)
        self.assertNotEqual(version_id, new_version_id)
        
        # Check that we now have two versions
        versions = self.version_manager.get_standard_versions(standard_id)
        self.assertEqual(len(versions), 2)

if __name__ == "__main__":
    unittest.main()
