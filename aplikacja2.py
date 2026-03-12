import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cyberatak na Bank - Symulacja", layout="wide")

# --- STAN GRY ---
@st.cache_resource
def get_game_state():
    return {
        "round": 0, 
        "teams": {}, 
        "active_scenario": "Wariant A: Ransomware i Wyciek Danych (RODO/NIS2)" # Domyślny
    }

state = get_game_state()

# --- BAZA SCENARIUSZY ---
ALL_SCENARIOS = {
    "Wariant A: Ransomware i Wyciek Danych (RODO/NIS2)": {
        1: {
            "title": "Runda 1: Wykrycie anomalii",
            "desc": "Godzina 8:00. Omijając silne uwierzytelnianie (SCA), hakerzy masowo logują się z zagranicy. Obciążenie serwerów rośnie. Zgodnie z NIS2, bank ma 24h na tzw. 'wczesne ostrzeżenie' do CSIRT KNF.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/SOC:",
                    "options": {
                        "Izolacja ruchu zagranicznego (Downtime)": {"fin": -10, "rep": -5, "sec": +20, "comp": +5},
                        "Wzmożone monitorowanie bez przerw": {"fin": +5, "rep": +5, "sec": -20, "comp": -10},
                    }
                },
                "PR": {
                    "label": "Decyzja Compliance:",
                    "options": {
                        "Natychmiastowe Early Warning do KNF": {"fin": 0, "rep": 0, "sec": +5, "comp": +20},
                        "Czekamy na więcej danych z IT": {"fin": +5, "rep": 0, "sec": 0, "comp": -15},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu:",
                    "options": {
                        "Wprowadzenie limitów transakcji (BCP)": {"fin": -5, "rep": -5, "sec": +5, "comp": +10},
                        "Brak reakcji biznesowej, czekamy": {"fin": +10, "rep": 0, "sec": -15, "comp": -5},
                    }
                }
            }
        },
        2: {
            "title": "Runda 2: Ransomware i Szantaż",
            "desc": "Godzina 11:30. Atak szyfruje stacje robocze. Hakerzy publikują próbkę bazy klientów. Zegar RODO tyka: organizacja ma 72h na zgłoszenie wycieku do UODO.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/SOC:",
                    "options": {
                        "Odcięcie sieci banku i wezwanie ekipy Incident Response": {"fin": -25, "rep": -15, "sec": +30, "comp": +10},
                        "Próba cichego odzyskania danych z backupów": {"fin": -5, "rep": -5, "sec": -15, "comp": -5},
                    }
                },
                "PR": {
                    "label": "Decyzja Compliance:",
                    "options": {
                        "Zgłoszenie do UODO i rozesłanie SMS-ów do klientów": {"fin": -10, "rep": -15, "sec": +5, "comp": +25},
                        "Zgłoszenie tylko do UODO. Ukrywamy to przed klientami": {"fin": 0, "rep": -5, "sec": 0, "comp": -25},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu:",
                    "options": {
                        "Rozpoczęcie negocjacji z hakerami / przygotowanie okupu": {"fin": -30, "rep": -30, "sec": -10, "comp": -20},
                        "Odmowa negocjacji, współpraca z organami ścigania": {"fin": 0, "rep": +10, "sec": +10, "comp": +15},
                    }
                }
            }
        },
        3: {
            "title": "Runda 3: Stabilizacja i Audyt",
            "desc": "Dzień 3. Usługi wracają. Wkracza KNF i sprawdza zarządzanie IT. Rozpoczynają się kontrole UODO.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/SOC:",
                    "options": {
                        "Wdrożenie testów TLPT (DORA) na nowej infrastrukturze": {"fin": -20, "rep": +10, "sec": +30, "comp": +20},
                        "Powrót do starej architektury, by uciąć koszty": {"fin": +10, "rep": -10, "sec": -20, "comp": -15},
                    }
                },
                "PR": {
                    "label": "Decyzja Compliance:",
                    "options": {
                        "Darmowy monitoring BIK dla poszkodowanych klientów": {"fin": -15, "rep": +25, "sec": 0, "comp": +10},
                        "Brak specjalnych akcji dla klientów": {"fin": +5, "rep": -15, "sec": 0, "comp": -10},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu:",
                    "options": {
                        "Zarząd bierze pełną odpowiedzialność i tworzy rezerwę na kary": {"fin": -25, "rep": +15, "sec": 0, "comp": +10},
                        "Zwolnienie CISO w świetle kamer jako kozła ofiarnego": {"fin": +10, "rep": -20, "sec": -10, "comp": -15},
                    }
                }
            }
        }
    },
    
    "Wariant B: Awaria Chmury i Łańcuch Dostaw (DORA, BCP)": {
        1: {
            "title": "Runda 1: Globalny Blackout Dostawcy",
            "desc": "Godzina 9:00. Główny dostawca chmurowy (Critical ICT Third-Party Provider wg DORA) zgłasza krytyczną awarię. Padają kluczowe systemy bankowe, w tym autoryzacja kart płatniczych. Klienci są wściekli, stojąc przy kasach w sklepach.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/SOC:",
                    "options": {
                        "Rozpoczęcie procedury failover do zapasowego Data Center (wymaga 3h przerwy)": {"fin": -15, "rep": -5, "sec": +15, "comp": +10},
                        "Czekanie na naprawę ze strony dostawcy chmurowego (SLA mówi o 4h)": {"fin": +5, "rep": -15, "sec": -10, "comp": -15},
                    }
                },
                "PR": {
                    "label": "Decyzja Komunikacyjna:",
                    "options": {
                        "Otwarty komunikat o awarii u zewnętrznego dostawcy i przeprosiny": {"fin": 0, "rep": +10, "sec": 0, "comp": +5},
                        "Komunikat o 'planowanych pracach serwisowych' (kłamstwo)": {"fin": 0, "rep": -25, "sec": 0, "comp": -15},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu (BCP):",
                    "options": {
                        "Aktywacja trybu offline dla terminali (zgoda na transakcje do 100 zł bez autoryzacji)": {"fin": -10, "rep": +15, "sec": -10, "comp": 0},
                        "Twarda blokada wszystkich transakcji do czasu powrotu systemów": {"fin": +10, "rep": -20, "sec": +10, "comp": +5},
                    }
                }
            }
        },
        2: {
            "title": "Runda 2: Atak na infrastrukturę zapasową",
            "desc": "Godzina 14:00. W trakcie przenoszenia usług do zapasowego centrum danych (DRC), hakerzy uderzają potężnym atakiem DDoS. Okazuje się, że awaria chmury była dywersją. Systemy monitoringu zapasowego są ślepe.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/SOC:",
                    "options": {
                        "Zakup w trybie awaryjnym usługi anty-DDoS od globalnego operatora": {"fin": -25, "rep": +5, "sec": +25, "comp": +10},
                        "Próba odfiltrowania ruchu własnymi siłami z użyciem starych firewalli": {"fin": -5, "rep": -15, "sec": -20, "comp": -10},
                    }
                },
                "PR": {
                    "label": "Decyzja Compliance (DORA / NIS2):",
                    "options": {
                        "Powiadomienie KNF o złożonym incydencie (DDoS + awaria łańcucha dostaw)": {"fin": 0, "rep": 0, "sec": +5, "comp": +25},
                        "Ukrywanie faktu ataku DDoS, raportujemy tylko problem chmurowy": {"fin": 0, "rep": -10, "sec": -5, "comp": -30},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu:",
                    "options": {
                        "Wstrzymanie sesji rozliczeniowych Elixir (Zatrzymanie gospodarki)": {"fin": -20, "rep": -20, "sec": +20, "comp": +15},
                        "Przepuszczanie sesji Elixir na ślepo (Ryzyko fraudów)": {"fin": -30, "rep": +10, "sec": -30, "comp": -25},
                    }
                }
            }
        },
        3: {
            "title": "Runda 3: Reorganizacja Architektury (Post-Mortem)",
            "desc": "Dzień następny. KNF żąda pilnego raportu z zarządzania ryzykiem stron trzecich (Third-Party Risk Management wg DORA). Bank musi podjąć strategiczne decyzje o swojej architekturze.",
            "questions": {
                "IT": {
                    "label": "Decyzja IT/Architektura:",
                    "options": {
                        "Wdrożenie strategii Multi-Cloud (rozproszenie ryzyka na wielu dostawców)": {"fin": -30, "rep": +10, "sec": +20, "comp": +20},
                        "Pozostanie u obecnego dostawcy (wymuszenie wyższych kar umownych w SLA)": {"fin": +15, "rep": -5, "sec": -10, "comp": -5},
                    }
                },
                "PR": {
                    "label": "Decyzja Prawna:",
                    "options": {
                        "Pozew przeciwko dostawcy chmury o odszkodowanie (proces na lata)": {"fin": +5, "rep": +15, "sec": 0, "comp": 0},
                        "Ugoda pozasądowa z klauzulą poufności": {"fin": +15, "rep": -10, "sec": 0, "comp": -10},
                    }
                },
                "Board": {
                    "label": "Decyzja Zarządu:",
                    "options": {
                        "Stworzenie stanowiska Członka Zarządu ds. Technologii i Odporności (wymóg DORA)": {"fin": -10, "rep": +10, "sec": +10, "comp": +20},
                        "Utrzymanie obecnej struktury organizacyjnej (IT podległe pod Finanse)": {"fin": +10, "rep": -5, "sec": -10, "comp": -15},
                    }
                }
            }
        }
    }
}

# --- FUNKCJE POMOCNICZE ---
def calculate_score(team_name):
    fin, rep, sec, comp = 100, 100, 100, 100
    active_scenario_data = ALL_SCENARIOS[state["active_scenario"]]
    
    for r in range(1, state["round"] + 1):
        if r in state["teams"][team_name]["decisions"]:
            for role, choice in state["teams"][team_name]["decisions"][r].items():
                impact = active_scenario_data[r]["questions"][role]["options"][choice]
                fin += impact["fin"]
                rep += impact["rep"]
                sec += impact["sec"]
                comp += impact["comp"]
    return max(0, min(150, fin)), max(0, min(150, rep)), max(0, min(150, sec)), max(0, min(150, comp))

def render_progress_bar(label, value):
    color = "green" if value > 75 else "orange" if value > 45 else "red"
    st.markdown(f"**{label}: {value}/100**")
    st.markdown(
        f"""<div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; margin-bottom: 10px;">
        <div style="width: {min(value, 100)}%; background-color: {color}; height: 20px; border-radius: 5px;"></div>
        </div>""", unsafe_allow_html=True
    )

# --- WIDOKI ---
def login_view():
    st.title("🛡️ Cyberatak na Bank - Symulacja Decyzyjna")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Wejście dla Zespołów")
        team_name = st.text_input("Podaj nazwę Twojego Banku:")
        if st.button("Dołącz do Gry"):
            if team_name:
                if team_name not in state["teams"]:
                    state["teams"][team_name] = {"decisions": {}, "ready": False}
                st.session_state["role"] = "team"
                st.session_state["team_name"] = team_name
                st.rerun()
            else:
                st.error("Wymagana nazwa zespołu!")
                
    with col2:
        st.subheader("Panel Wykładowcy")
        admin_pass = st.text_input("Hasło (domyślnie: admin):", type="password")
        if st.button("Zaloguj jako Prowadzący"):
            if admin_pass == "Dukana_2003":
                st.session_state["role"] = "admin"
                st.rerun()
            else:
                st.error("Odmowa dostępu!")

def admin_view():
    st.title("👨‍🏫 Panel Sterowania Symulacją")
    
    if state["round"] == 0:
        st.warning("Gra w fazie przygotowań. Wybierz scenariusz przed startem.")
        selected = st.selectbox("Wybierz scenariusz dla tej sesji:", list(ALL_SCENARIOS.keys()), index=list(ALL_SCENARIOS.keys()).index(state["active_scenario"]))
        if selected != state["active_scenario"]:
            state["active_scenario"] = selected
            st.success(f"Zmieniono scenariusz na: {selected}")
    else:
        st.info(f"Aktywny scenariusz: **{state['active_scenario']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Obecna Runda", state["round"] if state["round"] < 4 else "Podsumowanie końcowe")
        if state["round"] < 4:
            if st.button("Rozpocznij / Przejdź dalej ⏩", type="primary"):
                state["round"] += 1
                for t in state["teams"]: state["teams"][t]["ready"] = False
                st.rerun()
        else:
            if st.button("Zakończ i Zresetuj grę 🔄"):
                state["round"] = 0
                state["teams"] = {}
                st.rerun()
                
    with col2:
        st.write("### Status Zespołów")
        if not state["teams"]:
            st.info("Czekamy na dołączenie studentów...")
        for t, data in state["teams"].items():
            status = "✅ Zatwierdzono" if data["ready"] else "⏳ Analizują..."
            st.write(f"- **{t}**: {status}")

    st.divider()
    st.write("### Tablica Wyników na Żywo")
    if state["teams"]:
        scores = []
        for t in state["teams"]:
            f, r, s, c = calculate_score(t)
            scores.append({"Bank": t, "Finanse": f, "Reputacja": r, "Sec IT": s, "Compliance": c})
        st.dataframe(pd.DataFrame(scores), use_container_width=True)

def team_view():
    team = st.session_state["team_name"]
    st.title(f"🏦 Sztab Kryzysowy: {team}")
    
    with st.sidebar:
        st.header("KPI Banku")
        f, r, s, c = calculate_score(team)
        render_progress_bar("💰 Finanse (Płynność)", f)
        render_progress_bar("🤝 Reputacja (Klienci)", r)
        render_progress_bar("🔒 Bezpieczeństwo (IT)", s)
        render_progress_bar("⚖️ Zgodność (DORA/NIS2)", c)
        st.info("Nie dopuść, aby jakikolwiek wskaźnik spadł poniżej 40 punktów!")

    if state["round"] == 0:
        st.info("Jesteście w poczekalni. Prowadzący wybiera właśnie scenariusz incydentu. Bądźcie gotowi.")
        if st.button("Odśwież status"): st.rerun()
        
    elif 1 <= state["round"] <= 3:
        r = state["round"]
        active_scenario_data = ALL_SCENARIOS[state["active_scenario"]]
        scenario = active_scenario_data[r]
        
        st.header(scenario["title"])
        st.warning(f"**Sytuacja operacyjna:** {scenario['desc']}")
        
        if state["teams"][team]["ready"]:
            st.success("Wysłano decyzje do realizacji. Oczekujcie na rozwój wydarzeń.")
            if st.button("Odśwież ekran"): st.rerun()
        else:
            st.write("---")
            st.write("### Podejmijcie decyzje:")
            
            with st.form(f"form_r{r}"):
                choices = {}
                for role, q_data in scenario["questions"].items():
                    st.subheader(q_data["label"])
                    choices[role] = st.radio(f"Wybór {role}", list(q_data["options"].keys()), label_visibility="collapsed")
                    st.write("")
                
                if st.form_submit_button("Zatwierdź i Wykonaj 📝"):
                    if r not in state["teams"][team]["decisions"]:
                        state["teams"][team]["decisions"][r] = {}
                    state["teams"][team]["decisions"][r] = choices
                    state["teams"][team]["ready"] = True
                    st.rerun()

    elif state["round"] == 4:
        st.header("🏁 Zakończenie Symulacji - Raport Nadzoru")
        f, r, s, c = calculate_score(team)
        
        st.subheader("Wyniki końcowe Twojego Banku:")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Finanse", f)
        col2.metric("Reputacja", r)
        col3.metric("Bezpieczeństwo", s)
        col4.metric("Zgodność", c)
        
        st.write("---")
        if c < 40:
            st.error("Wyrok Regulatora: **KARA I UTRATA LICENCJI.** Zignorowaliście przepisy DORA/RODO/NIS2. KNF wprowadza zarząd komisaryczny.")
        elif s < 40:
            st.error("Wyrok Rynku: **TECHNICZNY UPADEK.** Systemy zostały nieodwracalnie zniszczone lub architektura zawiodła. Paraliż operacyjny.")
        elif r < 40:
            st.warning("Wyrok Klientów: **RUN ON THE BANK.** Fatalna komunikacja PR. Klienci uciekają z Waszego banku.")
        elif f > 50 and r > 50 and s > 50 and c > 50:
            st.success("Wyrok: **SUKCES OPERACYJNY.** Wykazaliście się cyfrową odpornością (Digital Operational Resilience). Organizacja przetrwała i zachowała zaufanie.")
        else:
            st.info("Wyrok: **PRZETRWANIE Z DUŻYMI KOSZTAMI.** Bank kontynuuje działalność, ale zarząd zostanie prawdopodobnie zwolniony.")

# --- ROUTING ---
if "role" not in st.session_state:
    login_view()
elif st.session_state["role"] == "admin":
    admin_view()
elif st.session_state["role"] == "team":
    team_view()