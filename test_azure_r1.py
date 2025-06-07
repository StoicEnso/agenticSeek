#!/usr/bin/env python3
"""
Test script for Azure DeepSeek R1 integration with AgenticSeek
"""

import requests
import json
import time

def test_azure_proxy():
    """Test the Azure proxy server"""
    print("🧪 Testing Azure DeepSeek R1 Proxy...")
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:3333/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to proxy: {e}")
        print("   Make sure azure_server_adapterv2.py is running")
        return False
    
    # Test setup endpoint (AgenticSeek protocol)
    try:
        setup_payload = {"model": "DeepSeek-R1"}
        response = requests.post("http://127.0.0.1:3333/setup", json=setup_payload)
        if response.status_code == 200:
            print("✅ Setup endpoint working")
        else:
            print(f"❌ Setup endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Setup endpoint error: {e}")
    
    # Test OpenAI-compatible endpoint
    try:
        openai_payload = {
            "messages": [{"role": "user", "content": "Hello! Please respond with just 'Hello back!'"}],
            "max_tokens": 50
        }
        response = requests.post("http://127.0.0.1:3333/v1/chat/completions", json=openai_payload)
        if response.status_code == 200:
            result = response.json()
            print("✅ OpenAI endpoint working")
            print(f"   Response: {result['choices'][0]['message']['content'][:100]}...")
        else:
            print(f"❌ OpenAI endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ OpenAI endpoint error: {e}")
    
    # Test AgenticSeek server protocol
    try:
        print("\n🔄 Testing AgenticSeek server protocol...")
        
        # Start generation
        generate_payload = {
            "messages": [{"role": "user", "content": "What is 2+2? Please be brief."}],
            "max_tokens": 100
        }
        response = requests.post("http://127.0.0.1:3333/generate", json=generate_payload)
        if response.status_code == 202:
            print("✅ Generation started")
        else:
            print(f"❌ Generation failed: {response.status_code} - {response.text}")
            return False
        
        # Poll for results
        max_polls = 30
        for i in range(max_polls):
            time.sleep(2)
            response = requests.get("http://127.0.0.1:3333/get_updated_sentence")
            if response.status_code == 200:
                result = response.json()
                sentence = result.get("sentence", "")
                is_complete = result.get("is_complete", False)
                
                print(f"   Poll {i+1}: {'Complete' if is_complete else 'In progress'}")
                if sentence:
                    print(f"   Current response: {sentence[:100]}...")
                
                if is_complete and sentence:
                    print("✅ AgenticSeek protocol working")
                    print(f"   Final response: {sentence}")
                    break
            else:
                print(f"❌ Polling failed: {response.status_code}")
                break
        else:
            print("❌ Polling timed out")
    
    except Exception as e:
        print(f"❌ AgenticSeek protocol error: {e}")
    
    return True

def test_agenticseek_config():
    """Test AgenticSeek configuration"""
    print("\n📋 Checking AgenticSeek configuration...")
    
    try:
        import configparser
        config = configparser.ConfigParser()
        config.read('config.ini')
        
        provider_name = config.get('MAIN', 'provider_name')
        provider_model = config.get('MAIN', 'provider_model')
        server_address = config.get('MAIN', 'provider_server_address')
        is_local = config.getboolean('MAIN', 'is_local')
        
        print(f"   Provider: {provider_name}")
        print(f"   Model: {provider_model}")
        print(f"   Server: {server_address}")
        print(f"   Is Local: {is_local}")
        
        if provider_name == "server" and not is_local and "3333" in server_address:
            print("✅ AgenticSeek configuration looks correct")
        else:
            print("⚠️  AgenticSeek configuration may need adjustment")
            print("   Expected: provider_name=server, is_local=False, server_address containing :3333")
    
    except Exception as e:
        print(f"❌ Cannot read config.ini: {e}")

def main():
    print("🚀 Azure DeepSeek R1 Integration Test")
    print("=" * 50)
    
    test_agenticseek_config()
    test_azure_proxy()
    
    print("\n" + "=" * 50)
    print("📝 Next steps:")
    print("1. If all tests pass, try running: python cli.py")
    print("2. Ask a simple question like 'Hello, how are you?'")
    print("3. If issues persist, check AZURE_R1_SETUP.md for troubleshooting")

if __name__ == "__main__":
    main() 