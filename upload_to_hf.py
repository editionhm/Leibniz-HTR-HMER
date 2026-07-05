# ====================================================================
# Hugging Face LoRA Adapter Uploader Utility
# ====================================================================
import os
import zipfile
import shutil
import sys

ZIP_PATH = r"C:\Users\omnig\Downloads\best_clean_htr_plain_exprate.zip"
TEMP_DIR = "./temp_hmer_adapter"

def main():
    print("=====================================================")
    print("🚀 Leibniz HTR/HMER LoRA Adapter Uploader")
    print("=====================================================")
    
    # Check if local zip exists
    if not os.path.exists(ZIP_PATH):
        print(f"❌ Error: Local ZIP file not found at {ZIP_PATH}")
        print("Please verify the path or modify ZIP_PATH in this script.")
        sys.exit(1)
        
    try:
        from huggingface_hub import HfApi, create_repo
    except ImportError:
        print("❌ Error: 'huggingface_hub' library is not installed.")
        print("Please run: pip install huggingface_hub")
        sys.exit(1)

    # 1. Prompt user for credentials
    repo_id = input("\nEnter target Hugging Face repository ID\n(e.g., editionhm/Leibniz-HTR-HMER-Adapter): ").strip()
    if not repo_id:
        print("❌ Error: Repository ID cannot be empty.")
        sys.exit(1)
        
    token = input("\nEnter your Hugging Face WRITE token\n(Generate one at https://huggingface.co/settings/tokens): ").strip()
    if not token:
        print("❌ Error: Hugging Face token is required.")
        sys.exit(1)

    # 2. Extract zip file
    print(f"\n📦 Extracting checkpoint zip file to temporary folder '{TEMP_DIR}'...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(TEMP_DIR)
    except Exception as e:
        print(f"❌ Error extracting ZIP: {str(e)}")
        sys.exit(1)

    # Detect the directory contents (check if it unzipped into a subfolder)
    subdirs = os.listdir(TEMP_DIR)
    upload_source = TEMP_DIR
    if len(subdirs) == 1 and os.path.isdir(os.path.join(TEMP_DIR, subdirs[0])):
        upload_source = os.path.join(TEMP_DIR, subdirs[0])
        
    print(f"🔍 Files detected for upload: {os.listdir(upload_source)}")

    # 3. Create Hugging Face Repository & Upload
    api = HfApi()
    try:
        print(f"\n🌐 Creating/verifying Hugging Face repository '{repo_id}'...")
        create_repo(repo_id=repo_id, token=token, repo_type="model", exist_ok=True)
        
        print(f"\n📤 Uploading adapter weights to huggingface.co/{repo_id}...")
        api.upload_folder(
            folder_path=upload_source,
            repo_id=repo_id,
            repo_type="model",
            token=token
        )
        print("\n✅ Success! Your adapter is now available on Hugging Face.")
        print(f"🔗 URL: https://huggingface.co/{repo_id}")
        print("\n📝 Configuration Note:")
        print(f"You can now set LORA_ADAPTER_PATH={repo_id} in your VPS .env file.")
        print("The backend will automatically fetch it at startup!")
        
    except Exception as e:
        print(f"\n❌ Hugging Face upload failed: {str(e)}")
    finally:
        # 4. Cleanup
        print("\n🧹 Cleaning up temporary files...")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        print("Done.")

if __name__ == "__main__":
    main()
