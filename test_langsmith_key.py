#!/usr/bin/env python3
"""
Test script to validate LangSmith API key
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_langsmith_key():
    """Test if the LangSmith API key is valid"""
    
    # Get API key
    api_key = os.getenv('LANGSMITH_API_KEY')
    project_name = os.getenv('LANGSMITH_PROJECT', 'credit-card-recommendation')
    
    print("🔑 LangSmith API Key Validation")
    print("=" * 40)
    
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found (length: {len(api_key)})")
    print(f"✅ Project name: {project_name}")
    
    try:
        from langsmith import Client
        
        # Create client
        client = Client(api_key=api_key)
        print("✅ LangSmith client created successfully")
        
        # Test API connection by listing projects
        print("\n🔍 Testing API connection...")
        projects = list(client.list_projects())
        print(f"✅ API connection successful! Found {len(projects)} projects")
        
        # Check if our project exists
        project_exists = any(p.name == project_name for p in projects)
        if project_exists:
            print(f"✅ Project '{project_name}' found in your account")
        else:
            print(f"⚠️ Project '{project_name}' not found. Creating it...")
            try:
                # Create the project if it doesn't exist
                new_project = client.create_project(
                    name=project_name,
                    description="Credit Card Recommendation System"
                )
                print(f"✅ Project '{project_name}' created successfully (ID: {new_project.id})")
            except Exception as e:
                print(f"❌ Failed to create project: {e}")
                return False
        
        # Test basic operations
        print("\n🧪 Testing basic operations...")
        
        # Test creating a simple run
        try:
            from langsmith.run_trees import RunTree
            run_tree = RunTree(
                name="test_run",
                run_type="chain",
                inputs={"test": "validation"},
                project_name=project_name
            )
            run_tree.end(outputs={"status": "success"})
            
            # Submit the run
            client.create_run_tree(run_tree)
            print("✅ Successfully created and submitted a test run")
            
        except Exception as e:
            print(f"❌ Failed to create test run: {e}")
            return False
        
        print("\n🎉 LangSmith API key is valid and working!")
        return True
        
    except ImportError:
        print("❌ LangSmith package not installed. Install with: pip install langsmith")
        return False
    except Exception as e:
        print(f"❌ API key validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_langsmith_key()
    exit(0 if success else 1)

