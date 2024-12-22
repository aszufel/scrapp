#!/usr/bin/env python3
"""
Główny moduł programu Email Finder.
"""

import argparse
import json
from pathlib import Path
from .email_finder import EmailFinder
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_finder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parsowanie argumentów wiersza poleceń."""
    parser = argparse.ArgumentParser(description='Email Finder')
    parser.add_argument(
        '--url', '-u',
        required=True,
        help='URL strony do przeanalizowania'
    )
    parser.add_argument(
        '--max-pages', '-m',
        type=int,
        default=100,
        help='Maksymalna liczba stron do przeanalizowania'
    )
    parser.add_argument(
        '--output', '-o',
        default='emails_data.csv',
        help='Nazwa pliku wyjściowego'
    )
    return parser.parse_args()

def main():
    """Główna funkcja programu."""
    args = parse_args()
    logger.info(f"Rozpoczynam przeszukiwanie strony {args.url}")
    
    try:
        finder = EmailFinder(max_pages=args.max_pages)
        results = finder.process_website(args.url)
        
        if results:
            total_emails = sum(len(emails) for emails in results.values())
            logger.info(f"Znaleziono {total_emails} adresów email")
            finder.save_results(results, args.output)
        else:
            logger.warning("Nie znaleziono żadnych adresów email")
            
    except Exception as e:
        logger.error(f"Wystąpił błąd: {str(e)}")
        raise

if __name__ == "__main__":
    main()
