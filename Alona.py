import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import date

# ==========================================
# ⚙️ IMPOSTAZIONI STUDIO DI ALONA
# Modifica questi dati con quelli reali di Alona
# ==========================================
NOME_STUDIO = "Alona ti Gyrotonica"
INDIRIZZO_STUDIO = "Via dei Castelli Romani 16, 00079 Rocca Priora (RM)"
PIVA_ALONA = "P.IVA: 01234567890 | CF: LNA..."
IBAN_ALONA = "IT00 0000 0000 0000 0000 0000 000"

# Impostazioni di base dell'app
st.set_page_config(page_title="Gestionale Gyrotonic Alona", page_icon="🧘‍♀️", layout="centered")
FILE_DATI = "clienti.json"

# --- FUNZIONI PER L'ARCHIVIO DATI ---
def carica_dati():
    if os.path.exists(FILE_DATI):
        with open(FILE_DATI, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"Privato": {}, "Partita IVA": {}}

def salva_dati(dati):
    with open(FILE_DATI, "w", encoding="utf-8") as file:
        json.dump(dati, file, indent=4)

archivio_clienti = carica_dati()

# --- CLASSE PDF PERSONALIZZATA ---
class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.set_text_color(41, 128, 185) # Colore Blu/Ottanio elegante
        self.cell(0, 10, NOME_STUDIO.upper(), align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, f"{INDIRIZZO_STUDIO} | {PIVA_ALONA}", align="C", new_x="LMARGIN", new_y="NEXT")
        
        self.set_draw_color(41, 128, 185)
        self.set_line_width(0.5)
        self.line(10, 28, 200, 28)
        self.ln(12) 

    def footer(self):
        self.set_y(-30)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        
        note_legali = (
            "Operazione in franchigia da IVA ai sensi della Legge 190/2014 art. 1 commi da 54 a 89.\n"
            "Il compenso non è soggetto a ritenute d'acconto ai sensi della legge 190/2014 art. 1 comma 67.\n"
            "Imposta di bollo da 2 euro assolta sull'originale per importi superiori a 77,47 euro."
        )
        self.multi_cell(0, 4, note_legali, align="C")

# --- TITOLO APP ---
st.title("🧘‍♀️ Studio Gyrotonic - Alona")
st.write("Gestione Clienti e Generazione Documenti (Regime Forfettario)")

tab_clienti, tab_documenti = st.tabs(["👤 1. Archivio Clienti", "📄 2. Emetti Documento"])

# ==========================================
# SCHEDA 1: ARCHIVIO E INSERIMENTO CLIENTI
# ==========================================
with tab_clienti:
    st.subheader("Inserisci un Nuovo Cliente")
    tipo_cliente = st.radio("Scegli la tipologia:", ["Privato", "Partita IVA"])
    
    with st.form("form_nuovo_cliente"):
        # Ho rimosso tutti gli asterischi come richiesto
        nome = st.text_input("Nome e Cognome / Ragione Sociale")
        telefono = st.text_input("Telefono")
        email = st.text_input("Indirizzo Email")
        indirizzo = st.text_input("Indirizzo di Residenza o Sede")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        citta = col1.text_input("Città")
        provincia = col2.text_input("Prov.")
        cap = col3.text_input("CAP")
        
        cf = st.text_input("Codice Fiscale")
        
        piva = ""
        sdi = ""
        if tipo_cliente == "Partita IVA":
            piva = st.text_input("Partita IVA")
            sdi = st.text_input("Codice Univoco (SDI)")
            
        salva_btn = st.form_submit_button("Salva nell'Archivio", type="primary")
        
        if salva_btn:
            if nome != "":
                nuovo_cliente = {
                    "tipo": tipo_cliente, "nome": nome, "telefono": telefono, "email": email,
                    "indirizzo": indirizzo, "citta": citta, "provincia": provincia, "cap": cap,
                    "cf": cf, "piva": piva, "sdi": sdi
                }
                archivio_clienti[tipo_cliente][nome] = nuovo_cliente
                salva_dati(archivio_clienti)
                st.success(f"✅ Cliente '{nome}' salvato con successo!")
            else:
                st.error("⚠️ Il Nome è obbligatorio.")

# ==========================================
# SCHEDA 2: EMISSIONE DOCUMENTO
# ==========================================
with tab_documenti:
    st.subheader("Richiama Cliente e Crea Documento")
    
    tutti_i_nomi = list(archivio_clienti["Privato"].keys()) + list(archivio_clienti["Partita IVA"].keys())
    
    if len(tutti_i_nomi) == 0:
        st.info("L'archivio è vuoto. Aggiungi i clienti nella prima scheda.")
    else:
        cliente_scelto = st.selectbox("Seleziona cliente:", [""] + tutti_i_nomi)
        
        if cliente_scelto != "":
            if cliente_scelto in archivio_clienti["Privato"]:
                dati_c = archivio_clienti["Privato"][cliente_scelto]
                tipo_doc = "Ricevuta (Copia di Cortesia)"
                nome_file_base = "Ricevuta"
            else:
                dati_c = archivio_clienti["Partita IVA"][cliente_scelto]
                tipo_doc = "Fattura (Copia di Cortesia)"
                nome_file_base = "Fattura"
            
            numero_doc = st.text_input("Numero Documento (es. 1/2024)", "1/2024")
            prestazione = st.text_area("Descrizione prestazione:", placeholder="Es. Pacchetto 10 lezioni di Gyrotonic")
            prezzo = st.number_input("Importo Totale (€)", min_value=0.0, format="%.2f")
            
            if prestazione == "" or prezzo == 0.0:
                st.warning("⚠️ Inserisci la prestazione e il prezzo per abilitare il download.")
            else:
                pdf = PDF()
                pdf.add_page()
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("helvetica", "B", 14)
                pdf.cell(0, 8, f"{tipo_doc} n° {numero_doc}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 11)
                data_oggi = date.today().strftime('%d/%m/%Y')
                pdf.cell(0, 6, f"Data emissione: {data_oggi}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(8)
                
                pdf.set_fill_color(245, 245, 245) 
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 8, " INTESTATO A:", fill=True, new_x="LMARGIN", new_y="NEXT")
                
                pdf.set_font("helvetica", "", 11)
                pdf.cell(0, 6, f" Nome / Ragione Sociale: {dati_c['nome']}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 6, f" Indirizzo: {dati_c['indirizzo']} - {dati_c['cap']} {dati_c['citta']} ({dati_c['provincia']})", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 6, f" Codice Fiscale: {dati_c['cf']}", new_x="LMARGIN", new_y="NEXT")
                
                if dati_c['tipo'] == "Partita IVA":
                    pdf.cell(0, 6, f" Partita IVA: {dati_c['piva']}", new_x="LMARGIN", new_y="NEXT")
                    if dati_c['sdi']:
                        pdf.cell(0, 6, f" Codice Univoco (SDI): {dati_c['sdi']}", new_x="LMARGIN", new_y="NEXT")
                
                pdf.ln(10)
                
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 8, " DESCRIZIONE DELLA PRESTAZIONE:", fill=True, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 11)
                pdf.multi_cell(0, 6, f" {prestazione}") 
                pdf.ln(10)
                
                pdf.set_font("helvetica", "B", 14)
                pdf.set_text_color(41, 128, 185) 
                
                # --- ECCO LA CORREZIONE: ho tolto il simbolo € e scritto "Euro" ---
                pdf.cell(0, 10, f"IMPORTO TOTALE: {prezzo:.2f} Euro", align="R", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                
                pdf.ln(15)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Metodo di pagamento:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, f"Bonifico Bancario intestato a: {dati_c.get('nome', 'Alona')}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 6, f"IBAN: {IBAN_ALONA}", new_x="LMARGIN", new_y="NEXT")
                
                # Sicurezza extra per la trasformazione in bytes per Streamlit
                pdf_bytes = bytes(pdf.output())
                nome_file = f"{nome_file_base}_{dati_c['nome'].replace(' ', '_')}.pdf"
                
                st.download_button(
                    label="⬇️ Genera e Scarica PDF",
                    data=pdf_bytes, 
                    file_name=nome_file,
                    mime="application/pdf",
                    type="primary"
                )
