import streamlit as st
from email_finder.email_finder import EmailFinder
from collections import defaultdict

# Konfiguracja strony
st.set_page_config(
    page_title="Email Finder by tiny tools",
    page_icon="📧",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .metric-card {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1E88E5;
        }
        .metric-label {
            color: #666;
            font-size: 1rem;
        }
        .email-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 0.5rem;
            border-left: 3px solid #1E88E5;
        }
        .header-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# Nagłówek
st.markdown("""
    <div class="header-container">
        <h1>📧 Email Finder</h1>
    </div>
""", unsafe_allow_html=True)

# Panel wyszukiwania
col1, col2 = st.columns([4, 1])
with col1:
    url = st.text_input('', placeholder='Wpisz adres strony do przeanalizowania...', value='https://example.com')
with col2:
    max_pages = st.number_input('Max stron:', min_value=1, value=100)

# Przycisk Start
if st.button('🔍 Rozpocznij skanowanie', use_container_width=True, type='primary'):
    with st.spinner('Trwa skanowanie strony...'):
        finder = EmailFinder(max_pages=max_pages)
        results = finder.process_website(url)
        
        if results:
            # Zbieramy statystyki
            email_stats = defaultdict(lambda: {'count': 0, 'pages': set(), 'contexts': []})
            
            for page_url, emails_data in results.items():
                for email, context in emails_data:
                    email_stats[email]['count'] += 1
                    email_stats[email]['pages'].add(page_url)
                    email_stats[email]['contexts'].append((page_url, context))
            
            # Panel metryk
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">{}</div>
                        <div class="metric-label">Unikalne emaile</div>
                    </div>
                """.format(len(email_stats)), unsafe_allow_html=True)
            
            with col2:
                total_pages = len(set().union(*[stats['pages'] for stats in email_stats.values()]))
                st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">{}</div>
                        <div class="metric-label">Przeanalizowane strony</div>
                    </div>
                """.format(total_pages), unsafe_allow_html=True)
            
            with col3:
                total_occurrences = sum(stats['count'] for stats in email_stats.values())
                st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">{}</div>
                        <div class="metric-label">Łączne wystąpienia</div>
                    </div>
                """.format(total_occurrences), unsafe_allow_html=True)
            
            # Panel wyników
            st.markdown("### 📧 Znalezione adresy email")
            for email, stats in email_stats.items():
                with st.expander(f"📧 {email} (znaleziono {stats['count']} razy na {len(stats['pages'])} stronach)"):
                    for page_url, context in stats['contexts']:
                        st.markdown(f"""
                            <div class="email-card">
                                <strong>Strona:</strong> {page_url}<br>
                                <strong>Kontekst:</strong> {context}
                            </div>
                        """, unsafe_allow_html=True)
            
            # Panel eksportu
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button('📥 Export do CSV', use_container_width=True):
                    # Tu dodaj kod eksportu do CSV
                    pass
            with col2:
                if st.button('📊 Export do Excel', use_container_width=True):
                    # Tu dodaj kod eksportu do Excel
                    pass
        else:
            st.error('Nie znaleziono żadnych adresów email.')

# Stopka
st.markdown("---")
st.markdown("Made with ❤️ by [Adrian Szufel]")
