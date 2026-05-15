#!/usr/bin/env python3
"""
Quick reindexing script for server deployment
Run this on the server to index documents for a tenant
"""

import sys
import os

def reindex_tenant(tenant_id: int):
    """Reindex all documents for a tenant"""
    
    print(f"🔄 Reindexing Tenant {tenant_id}")
    print("=" * 50)
    
    try:
        from rag_model.rag_utils import index_tenant_files
        
        print(f"🚀 Starting indexing process for tenant {tenant_id}...")
        print("⏳ This may take a few minutes depending on document count...")
        
        # Run indexing
        result = index_tenant_files(tenant_id)
        
        print(f"\n✅ Indexing Complete!")
        print(f"📊 Total vectors indexed: {result}")
        
        # Test retrieval
        print(f"\n🔍 Testing retrieval...")
        from rag_model.rag_utils import retrieve_s3_vectors
        
        test_queries = [
            "leave policy",
            "incident management",
            "earned leave"
        ]
        
        for query in test_queries:
            docs = retrieve_s3_vectors(query, tenant_id, top_k=3)
            print(f"   '{query}': {len(docs)} documents found")
        
        print(f"\n🎉 Tenant {tenant_id} successfully reindexed!")
        print(f"✅ System should now respond to queries correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Reindexing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_after_reindex(tenant_id: int):
    """Test the system after reindexing"""
    
    print(f"\n🧪 Testing System After Reindex")
    print("=" * 50)
    
    try:
        from rag_model.rag_utils import answer_question_modern
        
        test_query = "Can Earned Leave be carried forward?"
        
        print(f"📝 Test Query: '{test_query}'")
        print("⏳ Processing...")
        
        result = answer_question_modern(
            question=test_query,
            tenant_id=tenant_id,
            response_mode="detailed"
        )
        
        answer = result.get('answer', '')
        sources = result.get('sources', [])
        
        print(f"\n📄 Sources found: {len(sources)}")
        print(f"💬 Answer length: {len(answer)} characters")
        print(f"\n📖 Answer:")
        print(answer)
        
        if "I don't have enough information" in answer:
            print("\n⚠️  Still getting generic response - may need to check:")
            print("   1. Correct tenant ID")
            print("   2. Documents actually uploaded")
            print("   3. AWS credentials configured")
        else:
            print("\n✅ System is working! Specific answer provided!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Get tenant ID from command line or use default
    tenant_id = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    
    print("🔧 SERVER REINDEXING SCRIPT")
    print("=" * 60)
    print(f"Target Tenant: {tenant_id}\n")
    
    # Reindex
    success = reindex_tenant(tenant_id)
    
    if success:
        # Test
        test_after_reindex(tenant_id)
        
        print("\n\n🎯 NEXT STEPS:")
        print("1. Test via API: curl -X POST 'http://localhost:8000/chatbot/ask' \\")
        print("   -H 'Content-Type: application/json' \\")
        print(f"   -d '{{\"question\": \"leave policy\", \"tenant_id\": {tenant_id}}}'")
        print("\n2. Test via web interface with your chatbot")
        print("\n3. If still not working, run: python debug_server_deployment.py")
    else:
        print("\n\n❌ REINDEXING FAILED")
        print("🔍 Run debug script: python debug_server_deployment.py")
        print("📋 Check Docker logs: docker logs fastapi-backend")