import streamlit as st

# --- Gestion des données ---
import pandas as pd
from pathlib import Path

# Chemin vers le fichier CSV
EXPENSES_FILE = Path("data/expenses.csv")

# Vérifier si le fichier existe, sinon le créer avec les bonnes colonnes
if not EXPENSES_FILE.exists():
    df = pd.DataFrame(columns=["date", "category", "label", "amount"])
    df.to_csv(EXPENSES_FILE, index=False)

st.set_page_config(page_title="Expense Tracker", page_icon="💸", layout="wide")

st.title("💸 Expense Tracker — Ma première app")
st.caption("Une application simple pour enregistrer et analyser mes dépenses.")

# --- Formulaire d'ajout de dépense ---
st.subheader("➕ Ajouter une dépense")

with st.form("expense_form"):
    date = st.date_input("Date de la dépense")
    category = st.selectbox("Catégorie", ["Food", "Transport", "Rent", "Fun", "Health", "Other"])
    label = st.text_input("Libellé (ex : Burger King, Uber...)")
    amount = st.number_input("Montant (€)", min_value=0.0, step=0.5, format="%.2f")

    submitted = st.form_submit_button("Ajouter")

    if submitted:
        if amount > 0 and label:
            # Relire le CSV actuel
            df_now = pd.read_csv(EXPENSES_FILE)

            # Préparer la nouvelle ligne (on cast la date en texte pour le CSV)
            new_row = {
                "date": str(date),
                "category": category,
                "label": label.strip(),
                "amount": float(amount),
            }

            # Ajouter puis sauvegarder
            df_now = pd.concat([df_now, pd.DataFrame([new_row])], ignore_index=True)
            df_now.to_csv(EXPENSES_FILE, index=False)

            st.success("✅ Dépense ajoutée avec succès !")
            st.rerun()  # recharge la page pour que le tableau se mette à jour
        else:
            st.warning("⚠️ Entre un libellé et un montant > 0.")


st.info("Hello 👋 Si tu vois ce message, Streamlit fonctionne. Étape 1 validée ✅")

# Charger les dépenses
df = pd.read_csv(EXPENSES_FILE)

# Afficher le tableau
st.subheader("📋 Données enregistrées")
st.dataframe(df, use_container_width=True)



# --- Filtres ---
st.subheader("🔍 Filtres")

if not df.empty:
    # On s'assure que la colonne 'date' est bien de type datetime
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    # Sélecteur de plage de dates
    start_date, end_date = st.date_input(
        "Choisis une période :", [min_date, max_date]
    )

    # Liste des catégories disponibles
    categories = df["category"].unique().tolist()
    selected_categories = st.multiselect(
        "Filtrer par catégorie :", categories, default=categories
    )

    # Application du filtre
    df_filtered = df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date)) &
        (df["category"].isin(selected_categories))
    ]

    st.write(f"💡 {len(df_filtered)} dépenses trouvées dans cette période et ces catégories.")
else:
    st.info("Ajoute quelques dépenses pour activer les filtres.")




# --- Statistiques globales ---
st.subheader("📊 Statistiques globales")

if not df_filtered.empty:
    total_spent = df_filtered["amount"].sum()
    avg_per_day = df_filtered.groupby("date")["amount"].sum().mean()
    top_category = df_filtered.groupby("category")["amount"].sum().idxmax()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total des dépenses", f"{total_spent:.2f} €")
    col2.metric("Moyenne / jour", f"{avg_per_day:.2f} €")
    col3.metric("Catégorie la plus dépensée", top_category)
else:
    st.info("Aucune donnée pour cette période ou ces catégories.")



st.subheader("📈 Répartition par catégorie")

if not df_filtered.empty:
    chart_data = df_filtered.groupby("category")["amount"].sum()
    st.bar_chart(chart_data)
else:
    st.info("Pas encore de dépenses à afficher pour ce filtre.")



