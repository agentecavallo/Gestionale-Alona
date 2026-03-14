import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import date

# Impostazioni di base
st.set_page_config(page_title="Gestionale Gyrotonic Alona", page_icon="🧘‍♀️", layout="centered")

# Nome del file dove salveremo l'archivio clienti in automatico
FILE_DATI = "clienti.json"

# --- FUNZIONI PER L'ARCHIVIO DATI ---
def carica_dati():
    # Se il file esiste, lo legge. Altrimenti crea un archivio vuoto.
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"Privato": {}, "Partita IVA": {}}

def salva_dati(dati):
    # Salva i dati nel file
    with open(FILE_DATI, "w", encoding="utf-8") as file:
        json.dump(dati, file, indent=4)

# Carichiamo i dati all'avvio dell'app
archivio_clienti = carica_dati()

# --- TITOLO APP ---
st.title("🧘‍♀️ Studio Gyrotonic - Alona")
st.write("Gestione Clienti e Generazione Documenti")

# Creiamo le due SCHEDE (Tabs)
tab_clienti, tab_documenti = st.tabs(["👤 1. Archivio Clienti", "📄 2. Emetti Documento"])


# ==========================================
# SCHEDA 1: ARCHIVIO E INSERIMENTO CLIENTI
# ==========================================
with tab_clienti:
    st.subheader("Inserisci un Nuovo Cliente")
    
    # Selezione tipo cliente
    tipo_cliente = st.radio("Scegli la tipologia:", ["Privato", "Partita IVA"])
    
    # Usiamo un "Form" per raggruppare i campi
    with st.form("form_nuovo_cliente"):
        nome = st.text_input("Nome e Cognome / Ragione Sociale *")
        telefono = st.text_input("Telefono")
        email = st.text_input("Indirizzo Email")
        indirizzo = st.text_input("Indirizzo di Residenza o Sede *")
        
        # Mettiamo Città, Provincia e CAP sulla stessa riga
        col1, col2, col3 = st.columns([2, 1, 1])
        citta = col1.text_input("Città *")
        provincia = col2.text_input("Prov. *")
        cap = col3.text_input("CAP *")
        
        cf = st.text_input("Codice Fiscale *")
        
        # Campi extra se è Partita IVA
        piva = ""
        sdi = ""
        if tipo_cliente == "Partita IVA":
            piva = st.text_input("Partita IVA *")
            sdi = st.text_input("Codice Univoco (SDI)")
            
        st.write("* I campi contrassegnati dall'asterisco sono consigliati per il documento.")
        
        # Bottone per salvare
        salva_btn = st.form_submit_button("Salva nell'Archivio", type="primary")
        
        if salva_btn:
            if nome != "":
                # Creiamo la "scheda" del cliente
                nuovo_cliente = {
                    "tipo": tipo_cliente, "nome": nome, "telefono": telefono, "email": email,
                    "indirizzo": indirizzo, "citta": citta, "provincia": provincia, "cap": cap,
                    "cf": cf, "piva": piva, "sdi": sdi
                }
                # Lo salviamo nell'archivio sotto la sua categoria
                archivio_clienti[tipo_cliente][nome] = nuovo_cliente
                salva_dati(archivio_clienti)
                st.success(f"✅ Cliente '{nome}' salvato in archivio con successo!")
            else:
                st.error("⚠️ Il campo Nome/Ragione Sociale è obbligatorio per salvare il cliente.")


# ==========================================
# SCHEDA 2: EMISSIONE FATTURA O RICEVUTA
# ==========================================
with tab_documenti:
    st.subheader("Richiama Cliente e Crea Documento")
    
    # Uniamo tutti i clienti per farli selezionare ad Alona
    tutti_i_nomi = list(archivio_clienti["Privato"].keys()) + list(archivio_clienti["Partita IVA"].keys())
    
    if len(tutti_i_nomi) == 0:
        st.info("L'archivio è vuoto. Vai nella prima scheda per aggiungere i clienti.")
    else:
        # Tendina per cercare e selezionare il cliente
        cliente_scelto = st.selectbox("Cerca e seleziona un cliente dall'archivio:", [""] + tutti_i_nomi)
        
        if cliente_scelto != "":
            # Recuperiamo i dati del cliente scelto (cerchiamo se è privato o p.iva)
            if cliente_scelto in archivio_clienti["Privato"]:
                dati_c = archivio_clienti["Privato"][cliente_scelto]
                tipo_doc = "Ricevuta"
            else:
                dati_c = archivio_clienti["Partita IVA"][cliente_scelto]
                tipo_doc = "Fattura"
            
            # Mostriamo un riepilogo
            st.write(f"**Cliente selezionato:** {dati_c['nome']} ({dati_c['tipo']})")
            st.write(f"**Indirizzo:** {dati_c['indirizzo']}, {dati_c['cap']} {dati_c['citta']} ({dati_c['provincia']})")
            
            st.markdown("---")
            
            # Campi per la prestazione
            prestazione = st.text_area("Note e descrizione prestazione effettuata:", placeholder="Es. Pacchetto 5 lezioni di Gyrotonic...")
            prezzo = st.number_input("Prezzo / Importo (€)", min_value=0.0, format="%.2f")
            
            # Tasto per generare (cambia nome in base al tipo di cliente)
            if st.button(f"Genera {tipo_doc} (PDF)", type="primary"):
                if prestazione == "" or prezzo == 0.0:
                    st.error("⚠️ Inserisci la prestazione e il prezzo prima di generare il PDF.")
                else:
                    # --- CREAZIONE MATERIALE DEL PDF ---
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Intestazione Alona
                    pdf.set_font("helvetica", "B", 18)
                    pdf.cell(0, 10, "Studio Gyrotonic - Alona", align="C", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 5, f"{tipo_doc} emessa il: {date.today().strftime('%d/%m/%Y')}", align="C", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(15)
                    
                    # Dati Cliente
                    pdf.set_font("helvetica", "B", 12)
                    pdf.cell(0, 8, "Intestato a:", new_x="LMARGIN", new_y="NEXT")
                    pdf.set_font("helvetica", "", 11)
                    pdf.cell(0, 6, f"Nome / Ragione Sociale: {dati_c['nome']}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 6, f"Indirizzo: {dati_c['indirizzo']}", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 6, f"Città: {dati_c['cap']} {dati_c['citta']} ({dati_c['provincia']})", new_x="LMARGIN", new_y="NEXT")
                    pdf.cell(0, 6, f"Codice Fiscale: {dati_c['cf']}", new_x="LMARGIN", new_y="NEXT")
                    
                    if dati_c['tipo'] == "Partita IVA":
                        pdf.cell(0, 6, f"Partita IVA: {dati_c['piva']}", new_x="LMARGIN", new_y="NEXT")
                        if dati_c['sdi']:
                            pdf.cell(0, 6, f"Codice Univoco (SDI): {dati_c['sdi']}", new_x="LMARGIN", new_y="NEXT")
                            
                    if dati_c['telefono'] or dati_c['email']:
                        pdf.cell(0, 6, f"Contatti: {dati_c['telefono']} | {dati_c['email']}", new_x="LMARGIN", new_y="NEXT")
                        
                    pdf.ln(15)
                    
                    # Sezione Prestazione e Prezzo (in basso)
                    pdf.set_font("helvetica", "B", 12)
                    pdf.cell(0, 8, "Dettaglio Prestazione:", new_x="LMARGIN", new_y="NEXT")
                    
                    pdf.set_font("helvetica", "", 11)
                    # multi_cell gestisce i testi lunghi mandando a capo in automatico
                    pdf.multi_cell(0, 6, prestazione) 
                    
                    pdf.ln(10)
                    
                    # Prezzo finale
                    pdf.set_font("helvetica", "B", 14)
                    pdf.cell(0, 10, f"Importo Totale: {prezzo:.2f} Euro", new_x="LMARGIN", new_y="NEXT")
                    
                    pdf_bytes = pdf.output()
                    
                    st.success(f"✅ {tipo_doc} generata con successo!")
                    
                    nome_file = f"{tipo_doc}_{dati_c['nome'].replace(' ', '_')}.pdf"
                    
                    st.download_button(
                        label=f"⬇️ Scarica la {tipo_doc} in PDF",
                        data=pdf_bytes,
                        file_name=nome_file,
                        mime="application/pdf"
                    )
