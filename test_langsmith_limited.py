#!/usr/bin/env python3
"""
Test script for LangSmith API keys with limited permissions
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_limited_permissions():
    """Test what we can do with limited permissions"""
    
    api_key = os.getenv('LANGSMITH_API_KEY')
    project_name = os.getenv('LANGSMITH_PROJECT', 'credit-card-recommendation')
    
    print("🔑 LangSmith Limited Permissions Test")
    print("=" * 45)
    
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found")
        return False
    
    print(f"✅ API Key found (length: {len(api_key)})")
    print(f"✅ Project name: {project_name}")
    
    try:
        from langsmith import Client
        
        # Create client
        client = Client(api_key=api_key)
        print("✅ Client created successfully")
        
        # Test 1: Try to get project by ID if provided
        project_id = os.getenv('LANGSMITH_PROJECT_ID')
        if project_id:
            print(f"\n🔍 Testing with provided project ID: {project_id}")
            try:
                # Try to get project by ID
                project = client.read_project(project_id)
                print(f"✅ Found project: {project.name}")
                project_name = project.name
            except Exception as e:
                print(f"❌ Could not read project by ID: {e}")
                return False
        else:
            print("\n⚠️ No LANGSMITH_PROJECT_ID provided")
            print("💡 Add LANGSMITH_PROJECT_ID to your .env file if you have a project ID")
            print("💡 Or get a new API key with full permissions")
            return False
        
        # Test 2: Try to create a simple run with the project
        try:
            print("\n🧪 Testing basic tracing with existing project...")
            from langsmith.run_trees import RunTree
            
            run_tree = RunTree(
                name="limited_test",
                run_type="chain",
                inputs={"message": "Testing limited permissions"},
                project_name=project_name
            )
            run_tree.end(outputs={"result": "Limited test successful"})
            
            # Submit the run
            client.create_run_tree(run_tree)
            print("✅ Successfully created and submitted a test run!")
            
        except Exception as e:
            print(f"❌ Run creation failed: {e}")
            return False
        
        print("\n🎉 Limited LangSmith functionality is working!")
        print("💡 You can use this for basic tracing, but not project management")
        return True
        
    except ImportError:
        print("❌ LangSmith not installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_limited_permissions()
    exit(0 if success else 1)

