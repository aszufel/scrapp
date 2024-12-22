import streamlit as st
from email_finder.email_finder import EmailFinder
from collections import defaultdict

st.title('Email Finder')

url = st.text_input('Podaj adres strony do przeanalizowania:', 'https://example.com')
max_pages = st.number_input('Maksymalna liczba stron:', min_value=1, value=100)

if st.button('Znajdź emaile'):
    with st.spinner('Przeszukiwanie strony...'):
        finder = EmailFinder(max_pages=max_pages)
        results = finder.process_website(url)
        
        if results:
            # Zbieramy statystyki
            email_stats = defaultdict(lambda: {'count': 0, 'pages': set()})
            
            for page_url, emails_data in results.items():
                for email, context in emails_data:
                    email_stats[email]['count'] += 1
                    email_stats[email]['pages'].add(page_url)
            
            # Wyświetlamy podsumowanie
            st.success(f'Znaleziono {len(email_stats)} unikalnych adresów email!')
            
            st.subheader('Szczegółowa analiza:')
            for email, stats in email_stats.items():
                st.write(f"📧 {email}")
                st.write(f"   - Znaleziono {stats['count']} razy")
                st.write(f"   - Na {len(stats['pages'])} stronach")
                
            # Dodatkowe statystyki
            total_occurrences = sum(stats['count'] for stats in email_stats.values())
            total_pages = len(set().union(*[stats['pages'] for stats in email_stats.values()]))
            
            st.subheader('Podsumowanie:')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Unikalne emaile", len(email_stats))
            with col2:
                st.metric("Łączna liczba wystąpień", total_occurrences)
            with col3:
                st.metric("Przeanalizowane strony", total_pages)
        else:
            st.warning('Nie znaleziono żadnych adresów email.')
