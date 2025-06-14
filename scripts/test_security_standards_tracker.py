"""
Test script for the Security Standards Tracker.

This script tests the basic functionality of the tracker without making actual web requests.
"""
import sys
import os
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
import json

# Add project root to path for imports
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)
os.chdir(project_root)  # Change to project root directory

from scripts.security_standards_tracker import StandardsVersionManager, SecurityStandardsTracker

class TestStandardsVersionManager(unittest.TestCase):
    """Test the StandardsVersionManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temp directories for testing
        self.test_versions_path = "./test_data/standards_versions"
        self.test_changes_path = "./test_data/standards_changes" 
        
        # Create directories if they don't exist
        os.makedirs(self.test_versions_path, exist_ok=True)
        os.makedirs(self.test_changes_path, exist_ok=True)
        
        # Create a test version manager
        self.manager = StandardsVersionManager(
            versions_path=self.test_versions_path,
            changes_path=self.test_changes_path
        )
    
    def tearDown(self):
        """Clean up after test."""
        # Clean up test files
        for file in Path(self.test_versions_path).glob("*.json"):
            file.unlink()
        for file in Path(self.test_changes_path).glob("*.json"):
            file.unlink()
            
        # Delete index file
        index_file = Path(self.test_versions_path) / "standards_index.json"
        if index_file.exists():
            index_file.unlink()
    
    def test_add_standard(self):
        """Test adding a new standard."""
        name = "Test Standard"
        content = "This is a test standard content."
        source_url = "https://example.com/standard"
        
        # Add the standard
        standard_id, version_id, is_new_standard = self.manager.add_standard(
            name, content, source_url
        )
        
        # Check that it was added correctly
        self.assertTrue(is_new_standard)
        self.assertTrue(standard_id.startswith("std_"))
        self.assertTrue(version_id.startswith("v_"))
        
        # Check that standard exists in index
        self.assertIn(standard_id, self.manager.standards_index["standards"])
        self.assertEqual(self.manager.standards_index["standards"][standard_id]["name"], name)
        self.assertEqual(self.manager.standards_index["standards"][standard_id]["latest_version"], version_id)
        
        # Check that version file was created
        version_file = Path(self.test_versions_path) / f"{version_id}.json"
        self.assertTrue(version_file.exists())
        
        # Check version content
        with open(version_file, "r", encoding="utf-8") as f:
            version_data = json.load(f)
            self.assertEqual(version_data["standard_id"], standard_id)
            self.assertEqual(version_data["standard_name"], name)
            self.assertEqual(version_data["content"], content)
            self.assertEqual(version_data["source_url"], source_url)
    
    def test_add_new_version(self):
        """Test adding a new version to an existing standard."""
        # First add a standard
        name = "Test Standard"
        content1 = "This is version 1 content."
        source_url1 = "https://example.com/standard/v1"
        
        standard_id, version_id1, _ = self.manager.add_standard(
            name, content1, source_url1
        )
        
        # Now add a new version
        content2 = "This is version 2 content with new requirements."
        source_url2 = "https://example.com/standard/v2"
        
        # Mock _calculate_content_similarity to return a value below threshold
        with patch.object(self.manager, '_calculate_content_similarity', return_value=0.6):
            standard_id2, version_id2, is_new_standard = self.manager.add_standard(
                name, content2, source_url2
            )
        
        # Check that it was recognized as an update, not a new standard
        self.assertEqual(standard_id, standard_id2)
        self.assertFalse(is_new_standard)
        self.assertNotEqual(version_id1, version_id2)
        
        # Check that changes file was created
        changes = None
        for change_file in Path(self.test_changes_path).glob("*.json"):
            with open(change_file, "r", encoding="utf-8") as f:
                change_data = json.load(f)
                if change_data["previous_version_id"] == version_id1 and change_data["new_version_id"] == version_id2:
                    changes = change_data
                    break
        
        # Verify changes were recorded
        self.assertIsNotNone(changes)
        self.assertEqual(changes["standard_id"], standard_id)

class TestSecurityStandardsTracker(unittest.TestCase):
    """Test the SecurityStandardsTracker class."""
    
    @patch('scripts.security_standards_tracker.web_search')
    @patch('scripts.security_standards_tracker.RAGFactory')
    def test_fetch_security_standards_news(self, mock_rag_factory, mock_web_search):
        """Test fetching security standards news."""
        # Mock the web_search function
        mock_web_search.return_value = [
            {
                "title": "NIST Updates Cybersecurity Framework",
                "content": "The National Institute of Standards and Technology (NIST) has released an update to its Cybersecurity Framework...",
                "url": "https://example.com/nist-update"
            }
        ]
        
        # Mock the RAG system
        mock_rag_system = MagicMock()
        mock_rag_factory_instance = mock_rag_factory.return_value
        mock_rag_factory_instance.load_or_create_rag_system.return_value = mock_rag_system
        
        # Create test tracker
        tracker = SecurityStandardsTracker()
        
        # Test fetch_security_standards_news
        results = tracker.fetch_security_standards_news()
        
        # Check that web_search was called
        mock_web_search.assert_called()
        
        # Check that we got the mock results
        self.assertEqual(len(results), len(mock_web_search.return_value) * len(tracker.standard_sources))
    
    @patch('scripts.security_standards_tracker.SecurityStandardsTracker._extract_standard_info')
    @patch('scripts.security_standards_tracker.SecurityStandardsTracker._add_to_vector_db')
    @patch('scripts.security_standards_tracker.SecurityStandardsTracker._update_in_vector_db')
    def test_process_search_results(self, mock_update_db, mock_add_db, mock_extract_info):
        """Test processing search results."""
        # Mock the version manager
        mock_version_manager = MagicMock()
        
        # Configure mocks
        mock_extract_info.return_value = {
            "name": "Test Standard",
            "content": "This is test content",
            "source_url": "https://example.com/standard"
        }
        
        # Create two test results - one for a new standard, one for an update
        mock_version_manager.add_standard.side_effect = [
            ("std_1", "v_1", True),  # New standard
            ("std_2", "v_2", False)  # Updated standard
        ]
        
        # Create test tracker and replace its version manager
        tracker = SecurityStandardsTracker()
        tracker.version_manager = mock_version_manager
        
        # Test process_search_results
        results = [
            {"title": "New Standard", "content": "content1"},
            {"title": "Updated Standard", "content": "content2"}
        ]
        
        added, updated = tracker.process_search_results(results)
        
        # Check that the extract_standard_info was called for each result
        self.assertEqual(mock_extract_info.call_count, 2)
        
        # Check that add_standard was called for each result
        self.assertEqual(mock_version_manager.add_standard.call_count, 2)
        
        # Check that add_to_vector_db was called once for the new standard
        self.assertEqual(mock_add_db.call_count, 1)
        mock_add_db.assert_called_with("std_1", "v_1")
        
        # Check that update_in_vector_db was called once for the updated standard
        self.assertEqual(mock_update_db.call_count, 1)
        mock_update_db.assert_called_with("std_2", "v_2")
        
        # Check that the summary numbers are correct
        self.assertEqual(added, 1)
        self.assertEqual(updated, 1)


if __name__ == '__main__':
    unittest.main()
