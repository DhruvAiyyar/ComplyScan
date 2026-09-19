import os
import re
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

# In-memory store for reports generated during runtime
SCANS_DB = {}
scan_counter = 1

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

@router.post("/scan")
async def scan_label(file: UploadFile = File(...)):
    global scan_counter
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
            extracted_text.append(item["Text"].strip())

    # Generate a presigned URL valid for 1 hour so the browser can load the image
    try:
        image_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': unique_filename},
            ExpiresIn=3600
        )
    except Exception:
        image_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"

    # =========================================================
    # DYNAMIC LEGAL METROLOGY EXTRACTION (NO HARDCODED VALUES)
    # =========================================================

    full_text = " ".join(extracted_text)

    # 1. Net Quantity: Search for standard metric weight/volume units (e.g., 7.34 g, 500 ml)
    net_match = re.search(
        r"(?:(?:net\s*(?:wt\.?|weight|qty|quantity)?[:.]?\s*)?)(\b\d+(?:\.\d+)?\s*(?:g|gm|gms|kg|ml|l|ltr|pieces|units)\b)",
        full_text,
        re.IGNORECASE
    )
    val_net_wt = f"Net Wt.: {net_match.group(1).strip()}" if net_match else None

    # 2. MRP & Unit Sale Price: Matches price line + per-unit rate (e.g., Rs. 5.00 | Rs. 0.68 per g)
    mrp_lines = []
    for line in extracted_text:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        if any(k in line_lower for k in ["m.r.p", "mrp", "rs.", "₹"]) and any(c.isdigit() for c in line_clean):
            mrp_lines.append(line_clean)
        elif any(k in line_lower for k in ["per g", "per ml", "per kg", "per unit"]):
            mrp_lines.append(line_clean)
    val_mrp = " | ".join(dict.fromkeys(mrp_lines[:2])) if mrp_lines else None

    # 3. Manufacturer / Packer Details: Target maker entity + associated address line (PIN / city / building)
    mfg_line = None
    for line in extracted_text:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        if any(k in line_lower for k in ["mkt. by", "mfd. by", "mkd. by", "manufactured by", "packed by", "marketed by"]):
            mfg_line = line_clean
            break

    if not mfg_line:
        for line in extracted_text:
            if any(k in line.lower() for k in ["private limited", "pvt. ltd", "pvt ltd", "foods limited", "industries"]):
                mfg_line = line.strip()
                break

    # Look for the address line across extracted lines (PIN code, state/city, or road/tower/center)
    address_line = next(
        (
            l.strip() for l in extracted_text 
            if re.search(r"\b\d{6}\b", l) or any(k in l.lower() for k in ["mumbai", "delhi", "bengaluru", "kolkata", "chennai", "center", "tower", "floor", "road", "marg", "sector", "estate", "nagar"])
            and not any(bad in l.lower() for k, bad in enumerate(["mkt. by", "mfd. by", "mkd. by", "ingredients", "nutrition"]))
        ),
        None
    )

    if mfg_line and address_line and address_line not in mfg_line:
        val_mfg = f"{mfg_line} {address_line}"
    elif mfg_line:
        val_mfg = mfg_line
    else:
        val_mfg = None

    # 4. Mfg / Pkg / Expiry Date: Pair date tags with detected calendar dates
    date_matches = re.findall(r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b", full_text)
    
    if date_matches:
        # Check if the line itself has both tag and date (e.g., "Pkd. 20/08/26")
        combined_dates = []
        for line in extracted_text:
            if any(k in line.lower() for k in ["pkd", "use by", "mfg", "exp"]) and re.search(r"\d{2}[/-]\d{2}", line):
                combined_dates.append(line.strip())
        
        if combined_dates:
            val_date = " | ".join(combined_dates[:2])
        else:
            # If tags and date values were split into separate blocks by OCR, pair them
            tags_found = []
            for t in ["Pkd.", "USE BY:"]:
                if any(t.lower().replace(":", "") in l.lower() for l in extracted_text):
                    tags_found.append(t)
            
            if len(tags_found) >= 2 and len(date_matches) >= 2:
                val_date = f"{tags_found[0]} {date_matches[0]} | {tags_found[1]} {date_matches[1]}"
            elif tags_found and date_matches:
                val_date = f"{tags_found[0]} {date_matches[0]}"
            else:
                val_date = " | ".join(date_matches[:2])
    else:
        val_date = None

    # 5. Consumer Care Contacts: Toll-free lines, helpline numbers, or emails
    care_findings = []
    toll_free_match = re.search(r"\b1800\s*\d{2,4}\s*\d{3,4}\b|\b\d{10,12}\b", full_text)
    if toll_free_match:
        care_findings.append(toll_free_match.group(0).strip())
    email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_text)
    if email_match:
        care_findings.append(email_match.group(0).strip())
    val_care = " | ".join(care_findings) if care_findings else None

    # Construct dynamic rule verification results
    rule_results = [
        {
            "rule": "Net Quantity",
            "status": "pass" if val_net_wt else "fail",
            "detail": "Standard metric weight/volume declaration verified" if val_net_wt else "Net quantity declaration not found on label",
            "scanned_value": val_net_wt if val_net_wt else "Not Detected"
        },
        {
            "rule": "MRP & Unit Sale Price",
            "status": "pass" if val_mrp else "fail",
            "detail": "MRP / Unit sale price declaration verified" if val_mrp else "MRP declaration missing or unreadable",
            "scanned_value": val_mrp if val_mrp else "Not Detected"
        },
        {
            "rule": "Manufacturer Details",
            "status": "pass" if val_mfg else "fail",
            "detail": "Packer / Manufacturer identifier detected" if val_mfg else "Manufacturer or packer details missing",
            "scanned_value": val_mfg if val_mfg else "Not Detected"
        },
        {
            "rule": "Mfg / Pkg Date",
            "status": "pass" if val_date else "fail",
            "detail": "Packaging or manufacturing date detected" if val_date else "Packaging / Expiry date declaration not found",
            "scanned_value": val_date if val_date else "Not Detected"
        },
        {
            "rule": "Consumer Care",
            "status": "pass" if val_care else "fail",
            "detail": "Consumer grievance helpline/email verified" if val_care else "No consumer grievance phone or email found",
            "scanned_value": val_care if val_care else "Not Detected"
        }
    ]

    all_passed = all(r["status"] == "pass" for r in rule_results)
    overall_status = "COMPLIANT" if all_passed else "NON-COMPLIANT"

    current_id = scan_counter
    scan_counter += 1

    result_payload = {
        "id": current_id,
        "scan_id": current_id,
        "image_url": image_url,
        "extracted_text": extracted_text,
        "rule_results": rule_results,
        "overall_status": overall_status
    }

    # Store for retrieval on report page
    SCANS_DB[str(current_id)] = result_payload

    return result_payload


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    """
    Returns scan results for report.html
    """
    if report_id in SCANS_DB:
        return SCANS_DB[report_id]

    # Return latest scan if matching ID wasn't found in memory
    if SCANS_DB:
        return list(SCANS_DB.values())[-1]

    raise HTTPException(status_code=404, detail="Report not found. Please run a new scan.")