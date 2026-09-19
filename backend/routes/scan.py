import os
import uuid
import boto3
from botocore.client import Config
from fastapi import APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv

# Ensure dotenv finds the file in the current working directory
load_dotenv(override=True)

router = APIRouter()

AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1").strip()
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "complyscan-labels-9153").strip()
AWS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
AWS_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()

# Enforce Signature Version 4
custom_config = Config(
    region_name=AWS_REGION,
    signature_version="s3v4"
)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    config=custom_config
)

textract_client = boto3.client(
    "textract",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    config=custom_config
)

@router.post("/api/scan")
async def scan_label(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    try:
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 Upload failed: {str(e)}")

    try:
        response = textract_client.detect_document_text(
            Document={
                "S3Object": {
                    "Bucket": S3_BUCKET,
                    "Name": unique_filename
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Textract processing failed: {str(e)}")

    extracted_text = []
    for item in response.get("Blocks", []):
        if item["BlockType"] == "LINE":
            extracted_text.append(item["Text"])

    image_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"

    return {
        "scan_id": 1,
        "image_url": image_url,
        "extracted_text": extracted_text,
        "rule_results": [
            {"rule": "Net Quantity", "status": "pass", "detail": "Text extracted successfully via AWS Textract"}
        ],
        "overall_status": "COMPLIANT"
    }