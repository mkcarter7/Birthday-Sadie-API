#!/usr/bin/env python
"""
Generate a secure Django SECRET_KEY for production use.
Run this script and copy the output to your Heroku environment variables.
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*60)
    print("Generated SECRET_KEY for Heroku:")
    print("="*60)
    print(secret_key)
    print("="*60)
    print("\nRun this command to set it on Heroku:")
    print(f'heroku config:set SECRET_KEY="{secret_key}"')
    print("\n⚠️  Keep this key secret and never commit it to version control!\n")

