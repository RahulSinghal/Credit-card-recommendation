#!/usr/bin/env python3
"""
Simple LangSmith API key validation test
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_langsmith_simple():
    """Test basic LangSmith functionality"""
    
    api_key = os.getenv('LANGSMITH_API_KEY')
    project_name = os.getenv('LANGSMITH_PROJECT', 'credit-card-recommendation')
    
    print("🔑 Simple LangSmith Test")
    print("=" * 30)
    
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found")
        return False
    
    print(f"✅ API Key found (length: {len(api_key)})")
    print(f"✅ Project: {project_name}")
    
    try:
        from langsmith import Client
        
        # Test 1: Create client
        client = Client(api_key=api_key)
        print("✅ Client created successfully")
        
        # Test 2: Try to create a project (this should work even with limited permissions)
        try:
            print("\n🔍 Testing project creation...")
            project = client.create_project(
                project_name=project_name,
                description="Credit Card Recommendation System"
            )
            print(f"✅ Project created/updated: {project.name} (ID: {project.id})")
        except Exception as e:
            print(f"⚠️ Project creation failed: {e}")
            # Try to get existing project
            try:
                projects = list(client.list_projects())
                existing_project = next((p for p in projects if p.name == project_name), None)
                if existing_project:
                    print(f"✅ Found existing project: {existing_project.name} (ID: {existing_project.id})")
                else:
                    print("❌ Could not find or create project")
                    return False
            except Exception as e2:
                print(f"❌ Could not list projects: {e2}")
                return False
        
        # Test 3: Try to create a simple run (basic tracing)
        try:
            print("\n🧪 Testing basic tracing...")
            from langsmith.run_trees import RunTree
            
            run_tree = RunTree(
                name="simple_test",
                run_type="chain",
                inputs={"message": "Hello LangSmith"},
                project_name=project_name
            )
            run_tree.end(outputs={"result": "Test successful"})
            
            # Submit the run
            client.create_run_tree(run_tree)
            print("✅ Successfully created and submitted a test run")
            
        except Exception as e:
            print(f"❌ Run creation failed: {e}")
            return False
        
        print("\n🎉 Basic LangSmith functionality is working!")
        return True
        
    except ImportError:
        print("❌ LangSmith not installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_langsmith_simple()
    exit(0 if success else 1)
