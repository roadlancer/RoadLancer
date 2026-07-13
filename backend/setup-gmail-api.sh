#!/bin/bash
# Gmail API Setup Helper for RoadLancer
# Run this after creating your Google Cloud project and downloading credentials

set -e

echo "=========================================="
echo "  Gmail API Setup for RoadLancer"
echo "=========================================="
echo ""

# Check if credentials file exists
if [ ! -f "credentials.json" ]; then
    echo "❌ credentials.json not found!"
    echo ""
    echo "Please download it from Google Cloud Console:"
    echo "1. Go to https://console.cloud.google.com"
    echo "2. Select your project"
    echo "3. Go to APIs & Services → Credentials"
    echo "4. Click on your OAuth2 client ID"
    echo "5. Click 'Download JSON'"
    echo "6. Save it as 'credentials.json' in this directory"
    echo ""
    exit 1
fi

echo "✅ Found credentials.json"

# Extract client ID and secret
CLIENT_ID=$(python3 -c "import json; d=json.load(open('credentials.json')); print(d['installed']['client_id'])" 2>/dev/null || python3 -c "import json; d=json.load(open('credentials.json')); print(d['web']['client_id'])")
CLIENT_SECRET=$(python3 -c "import json; d=json.load(open('credentials.json')); print(d['installed']['client_secret'])" 2>/dev/null || python3 -c "import json; d=json.load(open('credentials.json')); print(d['web']['client_secret'])")

echo "Client ID: $CLIENT_ID"
echo ""

# Step 1: Run OAuth flow
echo "Step 1: Running OAuth2 authorization flow..."
echo "A browser window will open. Sign in with support.roadlancer@gmail.com"
echo "and grant access to Gmail."
echo ""

python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]

flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=8090)

# Save token
with open('token.json', 'w') as token:
    token.write(creds.to_json())

print('✅ Authorization successful! Token saved to token.json')
"

echo ""
echo "Step 2: Converting to Railway-compatible format..."
echo ""

# Convert token to base64 for Railway env var
TOKEN_B64=$(base64 -w 0 token.json 2>/dev/null || base64 token.json)

echo "=========================================="
echo "  Railway Environment Variables"
echo "=========================================="
echo ""
echo "Set these on Railway (Backend service):"
echo ""
echo "GMAIL_USER_EMAIL=support.roadlancer@gmail.com"
echo ""
echo "GMAIL_SERVICE_ACCOUNT_JSON=<paste contents of service-account.json>"
echo ""
echo "Or for token-based auth (simpler):"
echo "GMAIL_TOKEN_JSON=$TOKEN_B64"
echo ""
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy the environment variables above"
echo "2. Go to Railway → Backend service → Variables"
echo "3. Add each variable"
echo "4. Railway will redeploy automatically"
echo ""
echo "For production with Domain-wide Delegation:"
echo "1. Create a Service Account in Google Cloud Console"
echo "2. Enable Domain-wide Delegation"
echo "3. Add Gmail API scopes"
echo "4. Download service-account.json"
echo "5. Set GMAIL_SERVICE_ACCOUNT_JSON=<contents of service-account.json>"
echo ""
