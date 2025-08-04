#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Authentication Module
Handles OAuth2 flow for Google Drive API access.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for Google Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def authenticate_google_drive():
    """
    Handles OAuth2 authentication flow for Google Drive.
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated Drive service object
    """
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    # Check if we have stored credentials
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"⚠️ Token refresh failed: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"❌ Credentials file not found at {credentials_path}\n"
                    "Please download credentials.json from Google Cloud Console"
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'❌ An error occurred: {error}')
        return None

def test_authentication():
    """
    Test function to verify authentication works.
    """
    try:
        service = authenticate_google_drive()
        if service:
            # Test with a simple API call
            results = service.files().list(pageSize=1).execute()
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed!")
            return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

if __name__ == "__main__":
    test_authentication()
