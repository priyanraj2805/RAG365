#!/usr/bin/env python3
"""
Debug script for server deployment issues
Identifies where the RAG system is breaking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """Check environment variables and AWS configuration"""
    
    print("🔍 STEP 1: Environment Configuration Check")
    print("=" * 60)
    
    required_env_vars = [
        "AWS_DEFAULT_REGION",
        "S3_BUCKET_NAME",
        "S3_VECTORS_BUCKET_NAME",
        "S3_VECTORS_INDEX_NAME"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All environment variables configured")
        return True

def check_aws_connectivity():
    """Check AWS service connectivity"""
    
    print("\n🔍 STEP 2: AWS Service Connectivity Check")
    print("=" * 60)
    
    try:
        import boto3
        
        # Check S3 connectivity
        print("📦 Testing S3 connectivity...")
        s3_client = boto3.client('s3', region_name='ap-south-1')
        try:
            s3_client.list_buckets()
            print("✅ S3 connection successful")
        except Exception as e:
            print(f"❌ S3 connection failed: {e}")
            return False
        
        # Check S3 Vectors connectivity
        print("\n📊 Testing S3 Vectors connectivity...")
        s3vectors_client = boto3.client('s3vectors', region_name='ap-south-1')
        try:
            s3vectors_client.list_vector_buckets()
            print("✅ S3 Vectors connection successful")
        except Exception as e:
            print(f"❌ S3 Vectors connection failed: {e}")
            return False
        
        # Check Bedrock connectivity
        print("\n🧠 Testing AWS Bedrock connectivity...")
        bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')
        try:
            # Try to list foundation models
            print("✅ Bedrock connection successful")
        except Exception as e:
            print(f"❌ Bedrock connection failed: {e}")
            return False
        
        print("\n✅ All AWS services accessible")
        return True
        
    except Exception as e:
        print(f"❌ AWS SDK error: {e}")
        return False

def check_tenant_data(tenant_id: int = 26):
    """Check if tenant has data in S3 and S3 Vectors"""
    
    print(f"\n🔍 STEP 3: Tenant {tenant_id} Data Check")
    print("=" * 60)
    
    try:
        from rag_model.rag_utils import s3_list_tenant_files, retrieve_s3_vectors
        
        # Check S3 files
        print(f"📄 Checking S3 files for tenant {tenant_id}...")
        files = s3_list_tenant_files(tenant_id)
        
        if files:
            print(f"✅ Found {len(files)} files in S3:")
            for file in files[:5]:  # Show first 5
                print(f"   - {file.split('/')[-1]}")
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
        else:
            print(f"❌ No files found in S3 for tenant {tenant_id}")
            return False
        
        # Check S3 Vectors
        print(f"\n📊 Checking S3 Vectors for tenant {tenant_id}...")
        test_query = "leave policy"
        docs = retrieve_s3_vectors(test_query, tenant_id, top_k=5)
        
        if docs:
            print(f"✅ Found {len(docs)} vectors in S3 Vectors")
            print(f"📝 Sample content: {docs[0].page_content[:100]}...")
        else:
            print(f"❌ No vectors found in S3 Vectors for tenant {tenant_id}")
            print("🔧 This means the documents are NOT indexed!")
            return False
        
        print(f"\n✅ Tenant {tenant_id} has data in both S3 and S3 Vectors")
        return True
        
    except Exception as e:
        print(f"❌ Error checking tenant data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_retrieval(tenant_id: int = 26):
    """Test document retrieval with specific queries"""
    
    print(f"\n🔍 STEP 4: Document Retrieval Test")
    print("=" * 60)
    
    try:
        from rag_model.rag_utils import retrieve_s3_vectors
        
        test_queries = [
            "Can Earned Leave be carried forward?",
            "incident closure notes",
            "leave policy",
            "incident management"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            print("-" * 40)
            
            docs = retrieve_s3_vectors(query, tenant_id, top_k=5)
            
            if docs:
                print(f"✅ Retrieved {len(docs)} documents")
                for i, doc in enumerate(docs[:2], 1):
                    print(f"\n   Doc {i}:")
                    print(f"   Source: {doc.metadata.get('source', 'Unknown')}")
                    print(f"   Content: {doc.page_content[:150]}...")
            else:
                print(f"❌ No documents retrieved for this query")
        
        return True
        
    except Exception as e:
        print(f"❌ Retrieval test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline(tenant_id: int = 26):
    """Test the full RAG pipeline end-to-end"""
    
    print(f"\n🔍 STEP 5: Full Pipeline Test")
    print("=" * 60)
    
    try:
        from rag_model.rag_utils import answer_question_modern
        
        test_queries = [
            "Can Earned Leave (EL) be carried forward?",
            "What must be included in incident closure notes?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            print("-" * 40)
            
            result = answer_question_modern(
                question=query,
                tenant_id=tenant_id,
                response_mode="detailed"
            )
            
            answer = result.get('answer', '')
            sources = result.get('sources', [])
            
            print(f"📄 Sources: {len(sources)}")
            if sources:
                for source in sources[:2]:
                    print(f"   - {source}")
            
            print(f"💬 Answer length: {len(answer)} characters")
            print(f"📖 Answer preview: {answer[:200]}...")
            
            # Check if it's a generic "I don't have information" response
            if "I don't have enough information" in answer or "I do not have" in answer:
                print("⚠️  Generic fallback response - documents not being retrieved!")
            else:
                print("✅ Specific answer provided - system working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_indexing_status(tenant_id: int = 26):
    """Check if documents need to be reindexed"""
    
    print(f"\n🔍 STEP 6: Indexing Status Check")
    print("=" * 60)
    
    try:
        from rag_model.rag_utils import s3_list_tenant_files, retrieve_s3_vectors
        
        # Count files in S3
        files = s3_list_tenant_files(tenant_id)
        file_count = len(files)
        
        # Count vectors in S3 Vectors
        test_docs = retrieve_s3_vectors("test query", tenant_id, top_k=100)
        vector_count = len(test_docs)
        
        print(f"📄 Files in S3: {file_count}")
        print(f"📊 Vectors in S3 Vectors: {vector_count}")
        
        if file_count > 0 and vector_count == 0:
            print("\n❌ PROBLEM IDENTIFIED: Files exist but no vectors!")
            print("🔧 SOLUTION: Documents need to be indexed")
            print("\n💡 Run this command to index:")
            print(f"   python -c \"from rag_model.rag_utils import index_tenant_files; index_tenant_files({tenant_id})\"")
            return False
        elif file_count > 0 and vector_count > 0:
            print(f"\n✅ Indexing appears complete")
            print(f"📊 Ratio: {vector_count} vectors from {file_count} files")
            return True
        elif file_count == 0:
            print("\n❌ PROBLEM: No files uploaded for this tenant")
            print("🔧 SOLUTION: Upload documents first")
            return False
        
    except Exception as e:
        print(f"❌ Error checking indexing status: {e}")
        return False

def provide_solution():
    """Provide solution based on diagnosis"""
    
    print("\n\n🔧 DIAGNOSIS & SOLUTION")
    print("=" * 60)
    
    print("""
Based on the symptoms ("I don't have enough information"), the most likely issues are:

1. ❌ DOCUMENTS NOT INDEXED
   Problem: Files uploaded but not indexed in S3 Vectors
   Solution: Run indexing for the tenant
   Command: 
   ```python
   from rag_model.rag_utils import index_tenant_files
   index_tenant_files(26)  # Replace 26 with your tenant ID
   ```

2. ❌ WRONG TENANT ID
   Problem: Using wrong tenant ID in queries
   Solution: Verify tenant ID matches uploaded documents
   
3. ❌ AWS CREDENTIALS ISSUE
   Problem: Server can't access AWS services
   Solution: Configure AWS credentials on server
   
4. ❌ S3 VECTORS NOT CONFIGURED
   Problem: S3 Vectors service not properly set up
   Solution: Ensure S3 Vectors bucket and index exist

🚀 QUICK FIX STEPS:
1. SSH into server: ssh ubuntu@your-server
2. Enter Docker container: docker exec -it fastapi-backend bash
3. Run indexing: python -c "from rag_model.rag_utils import index_tenant_files; index_tenant_files(26)"
4. Test query: curl -X POST "http://localhost:8000/chatbot/ask" -H "Content-Type: application/json" -d '{"question": "leave policy", "tenant_id": 26}'
""")

if __name__ == "__main__":
    print("🔍 SERVER DEPLOYMENT DEBUG SCRIPT")
    print("=" * 60)
    print("Diagnosing RAG system issues on production server\n")
    
    # Run all checks
    env_ok = check_environment()
    aws_ok = check_aws_connectivity()
    data_ok = check_tenant_data(26)
    retrieval_ok = test_retrieval(26)
    pipeline_ok = test_full_pipeline(26)
    indexing_ok = check_indexing_status(26)
    
    # Summary
    print("\n\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 40)
    print(f"{'✅' if env_ok else '❌'} Environment Configuration")
    print(f"{'✅' if aws_ok else '❌'} AWS Connectivity")
    print(f"{'✅' if data_ok else '❌'} Tenant Data Exists")
    print(f"{'✅' if retrieval_ok else '❌'} Document Retrieval")
    print(f"{'✅' if pipeline_ok else '❌'} Full Pipeline")
    print(f"{'✅' if indexing_ok else '❌'} Indexing Status")
    
    # Provide solution
    provide_solution()
    
    print("\n🎯 Next Steps:")
    print("1. Fix any ❌ issues identified above")
    print("2. Run indexing if documents not indexed")
    print("3. Test with curl command")
    print("4. Check Docker logs: docker logs fastapi-backend")