#!/usr/bin/env python3
# generate_secret_key.py - Genera una SECRET_KEY segura para Django

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    print("=" * 50)
    print("Django SECRET_KEY Generator")
    print("=" * 50)
    print("\nGenera una nueva SECRET_KEY cada vez que ejecutes este script.")
    print("Usa esta clave en tu archivo .env.prod\n")
    print("SECRET_KEY generada:")
    print("-" * 50)
    print(get_random_secret_key())
    print("-" * 50)
    print("\n⚠️  IMPORTANTE:")
    print("  - NO compartas esta clave")
    print("  - NO la subas al repositorio")
    print("  - Úsala SOLO en .env.prod")
    print("\n")
