"""
Moduł do wyszukiwania adresów email na stronach internetowych.
"""

import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse
import re
import time
import logging
from typing import List, Set, Dict, Tuple
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailFinder:
    """Klasa do wyszukiwania adresów email na stronach internetowych."""
    
    def __init__(self, max_pages: int = 100, timeout: int = 10):
        self.max_pages = max_pages
        self.timeout = timeout
        self.processed_urls = set()
        self.session = self._create_session()
        self.email_pattern = r'[a-zA-Z0-9._%+-]{2,}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.compiled_pattern = re.compile(self.email_pattern)

    def _create_session(self) -> requests.Session:
        """Tworzy sesję HTTP z automatycznymi ponowieniami prób"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _extract_emails_from_text(self, text: str) -> List[str]:
        """Wyciąga maile z tekstu"""
        if not text:
            return []

        matches = self.compiled_pattern.finditer(text)
        emails = []
        for match in matches:
            email = match.group().lower().strip()
            if (
                ' ' not in email and
                len(email.split('@')[0]) >= 2 and
                len(email.split('@')[1].split('.')[0]) >= 1 and
                len(email.split('.')[-1]) >= 2
            ):
                emails.append(email)
        return emails

    def find_emails_on_page(self, url: str) -> List[Tuple[str, str]]:
        """Znajduje wszystkie unikalne adresy email na stronie wraz z ich kontekstem"""
        if url in self.processed_urls:
            return []

        self.processed_urls.add(url)
        emails_with_context = []
        seen_emails = set()

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Szukaj w elementach div z klasą text-editor
            for editor in soup.find_all(class_="elementor-widget-text-editor"):
                text = editor.get_text(strip=True)
                if text:
                    emails = self._extract_emails_from_text(text)
                    for email in emails:
                        if email not in seen_emails:
                            parent_text = editor.find('p')
                            context = parent_text.get_text(strip=True) if parent_text else text[:100]
                            emails_with_context.append((email, context))
                            seen_emails.add(email)

            # 2. Szukaj w paragrafach i nagłówkach
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = tag.get_text(strip=True)
                if text:
                    emails = self._extract_emails_from_text(text)
                    for email in emails:
                        if email not in seen_emails:
                            emails_with_context.append((email, text))
                            seen_emails.add(email)

            # 3. Szukaj w linkach mailto:
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('mailto:'):
                    email = href.split('mailto:')[1].split('?')[0].lower().strip()
                    if (email not in seen_emails and
                        len(email.split('@')[0]) >= 2 and
                        len(email.split('@')[1].split('.')[0]) >= 1 and
                        len(email.split('.')[-1]) >= 2):
                        emails_with_context.append((email, f"Link mailto: {a.get_text(strip=True)}"))
                        seen_emails.add(email)

            return emails_with_context

        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania {url}: {str(e)}")
            return []

    def get_internal_links(self, url: str) -> Set[str]:
        """Pobiera wszystkie wewnętrzne linki ze strony"""
        internal_links = set()
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            base_domain = urlparse(url).netloc

            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(url, href)
                parsed_url = urlparse(full_url)

                if parsed_url.netloc == base_domain and parsed_url.scheme in ('http', 'https'):
                    internal_links.add(full_url)

        except Exception as e:
            logger.error(f"Błąd podczas pobierania linków z {url}: {str(e)}")

        return internal_links

    def process_website(self, start_url: str) -> Dict[str, List[Tuple[str, str]]]:
        """Przetwarza całą stronę internetową"""
        results = {}
        to_process = {start_url}
        processed = set()

        while to_process and len(processed) < self.max_pages:
            url = to_process.pop()

            if url not in processed:
                logger.info(f"Przetwarzanie: {url}")

                # Znajdź maile na stronie
                emails = self.find_emails_on_page(url)
                if emails:
                    results[url] = emails

                # Dodaj nowe linki do przetworzenia
                if len(processed) < self.max_pages:
                    new_links = self.get_internal_links(url)
                    to_process.update(new_links - processed)

                processed.add(url)
                time.sleep(1)  # Opóźnienie między żądaniami

        return results

    def save_results(self, results: Dict[str, List[Tuple[str, str]]], filename: str = 'emails_data.csv'):
        """Zapisuje unikalne wyniki do pliku CSV"""
        if not results:
            logger.warning("Brak danych do zapisania")
            return

        try:
            # Przygotuj unikalne wyniki
            unique_results = {}
            for url, emails_data in results.items():
                for email, context in emails_data:
                    if email not in unique_results:
                        unique_results[email] = {
                            'email': email,
                            'znaleziono_na': url,
                            'kontekst': context
                        }

            # Zapisz do CSV
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=['email', 'znaleziono_na', 'kontekst'])
                writer.writeheader()
                for data in unique_results.values():
                    writer.writerow(data)

            print(f"\nZapisano {len(unique_results)} unikalnych adresów email w pliku {filename}")
            print(f"Znalezione adresy email:")
            for email in unique_results.keys():
                print(f"- {email}")

        except Exception as e:
            logger.error(f"Błąd podczas zapisywania wyników: {str(e)}")
            print(f"\nBłąd podczas zapisywania do pliku: {str(e)}")

            # Wyświetl wyniki mimo błędu zapisu
            print("\nZnalezione adresy email:")
            for url, emails_data in results.items():
                for email, context in emails_data:
                    print(f"- {email} (znaleziono na: {url})")
                    print(f"  Kontekst: {context}\n")
