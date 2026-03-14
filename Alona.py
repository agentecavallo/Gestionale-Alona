import streamlit as st
import json
import os
from fpdf import FPDF
from datetime import date

# ==========================================
# ⚙️ IMPOSTAZIONI STUDIO DI ALONA
# ==========================================
NOME_STUDIO = "Studio Gyrotonic - Alona"
INDIRIZZO_STUDIO = "Via Roma 1, 00100 Città (PR)"
PIVA_ALONA = "P.IVA: 01234567890 | CF: LNA..."
IBAN_ALONA = "IT00 0000 0000 0000 0000 0000 000"

st.set_page_config(page_title="Gestionale Gyrotonic Alona", page_icon="🧘‍♀️", layout="centered")

FILE_CLIENTI = "clienti.json"
FILE_DOCUMENTI = "documenti.json"

# --- FUNZIONI PER L'ARCHIVIO CLIENTI ---
def carica_clienti():
    if os.path.exists(FILE_CLIENTI):
        with open(FILE_CLIENTI, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"Privato": {}, "Partita IVA": {}}

def salva_clienti(dati):
    with open(FILE_CLIENTI, "w", encoding="utf-8") as file:
        json.dump(dati, file, indent=4)

# --- FUNZIONI PER L'ARCHIVIO DOCUMENTI ---
def carica_documenti():
    if os.path.exists(FILE_DOCUMENTI):
        with open(FILE_DOCUMENTI, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def salva_documenti(dati):
    with open(FILE_DOCUMENTI, "w", encoding="utf-8") as file:
        json.dump(dati, file, indent=4)

archivio_clienti = carica_clienti()

# Callback per registrare il documento al momento del download
def registra_documento(doc_record):
    docs = carica_documenti()
    # Evita di salvare duplicati se clicca due volte lo stesso download
    gia_presente = any(d['numero'] == doc_record['numero'] and d['anno'] == doc_record['anno'] for d in docs)
    if not gia_presente:
        docs.append(doc_record)
        salva_documenti(docs)

# --- CLASSE PDF PERSONALIZZATA ---
class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 20)
        self.set_text_color(41, 128, 185) 
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

# --- INTERFACCIA APP ---
st.title("🧘‍♀️ Studio Gyrotonic - Alona")
st.write("Gestione Clienti, Fatture e Ricevute (Regime Forfettario)")

tab_clienti, tab_documenti, tab_archivio_doc = st.tabs(["👤 1. Clienti", "📄 2. Emetti Doc", "🗂️ 3. Storico Documenti"])

# ==========================================
# SCHEDA 1: ARCHIVIO E INSERIMENTO CLIENTI
# ==========================================
with tab_clienti:
    st.subheader("Inserisci un Nuovo Cliente")
    tipo_cliente = st.radio("Scegli la tipologia:", ["Privato", "Partita IVA"])
    
    with st.form("form_nuovo_cliente"):
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
                salva_clienti(archivio_clienti)
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
                tipo_doc_stampa = "Ricevuta (Copia di Cortesia)"
                tipo_doc_base = "Ricevuta"
            else:
                dati_c = archivio_clienti["Partita IVA"][cliente_scelto]
                tipo_doc_stampa = "Fattura (Copia di Cortesia)"
                tipo_doc_base = "Fattura"
            
            # Calcolo automatico Anno e Numero
            anno_corrente = date.today().year
            docs_attuali = carica_documenti()
            # Trova il numero più alto per l'anno in corso
            numeri_anno = [d['numero'] for d in docs_attuali if d['anno'] == anno_corrente]
            prossimo_numero = max(numeri_anno) + 1 if numeri_anno else 1
            
            col_num, col_anno = st.columns(2)
            numero_scelto = col_num.number_input("Numero", min_value=1, value=prossimo_numero)
            col_anno.text_input("Anno", value=str(anno_corrente), disabled=True)
            numero_completo = f"{numero_scelto}/{anno_corrente}"

            prestazione = st.text_area("Descrizione prestazione:", placeholder="Es. Pacchetto 10 lezioni di Gyrotonic")
            prezzo = st.number_input("Importo Totale (€)", min_value=0.0, format="%.2f")
            
            if prestazione == "" or prezzo == 0.0:
                st.warning("⚠️ Inserisci la prestazione e il prezzo per abilitare il download.")
            else:
                data_oggi = date.today().strftime('%d/%m/%Y')

                # Preparazione PDF
                pdf = PDF()
                pdf.add_page()
                pdf.set_text_color(0, 0, 0)
                
                pdf.set_font("helvetica", "B", 14)
                pdf.cell(0, 8, f"{tipo_doc_stampa} n° {numero_completo}", align="L", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 11)
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
                pdf.cell(0, 10, f"IMPORTO TOTALE: {prezzo:.2f} Euro", align="R", new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)
                
                pdf.ln(15)
                pdf.set_font("helvetica", "B", 10)
                pdf.cell(0, 6, "Metodo di pagamento:", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 6, f"Bonifico Bancario intestato a: {dati_c.get('nome', 'Alona')}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 6, f"IBAN: {IBAN_ALONA}", new_x="LMARGIN", new_y="NEXT")
                
                pdf_bytes = bytes(pdf.output())
                nome_file = f"{tipo_doc_base}_{numero_scelto}_{anno_corrente}_{dati_c['nome'].replace(' ', '_')}.pdf"
                
                # Dati da salvare nell'archivio al click del bottone
                doc_record = {
                    "numero": numero_scelto,
                    "anno": anno_corrente,
                    "numero_completo": numero_completo,
                    "data": data_oggi,
                    "cliente": dati_c['nome'],
                    "tipo": tipo_doc_base,
                    "prestazione": prestazione,
                    "importo": prezzo
                }

                st.download_button(
                    label="⬇️ Genera e Scarica PDF",
                    data=pdf_bytes, 
                    file_name=nome_file,
                    mime="application/pdf",
                    type="primary",
                    on_click=registra_documento,
                    args=(doc_record,)
                )

# ==========================================
# SCHEDA 3: STORICO DOCUMENTI EMESSI
# ==========================================
with tab_archivio_doc:
    st.subheader("Archivio Documenti Generati")
    docs_salvati = carica_documenti()
    
    if len(docs_salvati) == 0:
        st.info("Nessun documento emesso finora. Genera un PDF per iniziare a popolare l'archivio.")
    else:
        # Ordiniamo i documenti in modo che i più recenti siano in alto
        docs_salvati.reverse()
        
        # Creiamo una lista formattata per mostrare una bella tabella
        tabella_da_mostrare = []
        totale_incassato = 0.0
        
        for d in docs_salvati:
            tabella_da_mostrare.append({
                "Documento": f"{d['tipo']} n. {d['numero_completo']}",
                "Data": d['data'],
                "Cliente": d['cliente'],
                "Prestazione": d['prestazione'],
                "Importo": f"€ {d['importo']:.2f}"
            })
            totale_incassato += d['importo']
            
        st.table(tabella_da_mostrare)
        st.success(f"**Totale emesso:** € {totale_incassato:.2f}")
