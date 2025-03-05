"""
Test script to verify CrewAI installation
"""
import os
import dotenv

def test_crewai_imports():
    """Test importing CrewAI modules"""
    try:
        import crewai
        from crewai import Agent, Crew, Task
        from crewai.flow.flow import Flow, listen, start
        print("✅ CrewAI imports successful!")
        print(f"CrewAI version: {crewai.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Error importing CrewAI: {e}")
        return False

def test_openai_access():
    """Test OpenAI API access"""
    try:
        # Load environment variables from .env file
        dotenv.load_dotenv()
        
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your-api-key-here":
            print("❌ OPENAI_API_KEY not set or has default value")
            return False
            
        openai.api_key = api_key
        
        # Test a simple chat completion
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello world"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API access successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Error accessing OpenAI API: {e}")
        return False

if __name__ == "__main__":
    print("Testing CrewAI and dependencies...")
    crewai_ok = test_crewai_imports()
    openai_ok = test_openai_access()
    
    if crewai_ok and openai_ok:
        print("\n✅ All tests passed! Your environment is correctly set up.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")