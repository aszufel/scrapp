import streamlit as st
from email_finder.email_finder import EmailFinder

st.title('Email Finder')

url = st.text_input('Podaj adres strony do przeanalizowania:', 'https://example.com')
max_pages = st.number_input('Maksymalna liczba stron:', min_value=1, value=100)

if st.button('Znajdź emaile'):
    with st.spinner('Przeszukiwanie strony...'):
        finder = EmailFinder(max_pages=max_pages)
        results = finder.process_website(url)
        
        if results:
            st.success(f'Znaleziono emaile!')
            for url, emails_data in results.items():
                st.write(f"\nStrona: {url}")
                for email, context in emails_data:
                    st.write(f"- Email: {email}")
                    st.write(f"  Kontekst: {context}")
        else:
            st.warning('Nie znaleziono żadnych adresów email.')
