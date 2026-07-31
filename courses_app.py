import streamlit as st

st.set_page_config(page_title="Ma liste de courses", page_icon="🛒", layout="wide")

# ---------------------------------------------------------------------------
# Données : produits disponibles par catégorie
# ---------------------------------------------------------------------------
PRODUITS = {
    "🥦 Légumes": [
        "Tomates", "Oignons", "Carottes", "Pommes de terre", "Salade",
        "Courgettes", "Poivrons", "Ail", "Champignons", "Concombre",
    ],
    "🍎 Fruits": [
        "Pommes", "Bananes", "Oranges", "Fraises", "Citrons", "Raisins",
    ],
    "🥩 Protéines": [
        "Poulet", "Bœuf haché", "Saumon", "Jambon", "Œufs",
        "Steak végétal", "Tofu", "Falafels",
    ],
    "🥛 Produits laitiers": [
        "Lait", "Beurre", "Yaourts", "Fromage", "Crème fraîche",
    ],
    "🍞 Épicerie": [
        "Pain", "Pâtes", "Riz", "Farine", "Sucre", "Huile d'olive",
        "Café", "Thé", "Sel", "Conserves",
    ],
    "🥤 Boissons": [
        "Eau", "Jus de fruits", "Soda", "Vin", "Bière",
    ],
    "🧴 Produits ménagers": [
        "Liquide vaisselle", "Éponges", "Papier toilette", "Sacs poubelle",
        "Lessive", "Essuie-tout", "Lingettes"
    ],
    "🧼 Hygiène": [
        "Shampoing", "Savon", "Dentifrice", "Déodorant", "Rasoirs",
    ],
}

# table inverse : produit -> catégorie (utile pour réinitialiser les cases à cocher)
PRODUIT_TO_CAT = {
    produit: cat for cat, produits in PRODUITS.items() for produit in produits
}

# ---------------------------------------------------------------------------
# État de session
# ---------------------------------------------------------------------------
if "liste" not in st.session_state:
    st.session_state.liste = {}  # {nom_produit: quantite}


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------
def toggle_produit(cat, produit):
    key = f"chk_{cat}_{produit}"
    if st.session_state[key]:
        st.session_state.liste.setdefault(produit, 1)
    else:
        st.session_state.liste.pop(produit, None)


def update_qty(produit):
    key = f"qty_input_{produit}"
    st.session_state.liste[produit] = st.session_state[key]


def supprimer(produit):
    st.session_state.liste.pop(produit, None)

    cat = PRODUIT_TO_CAT.get(produit)
    if cat is not None:
        chk_key = f"chk_{cat}_{produit}"
        if chk_key in st.session_state:
            st.session_state[chk_key] = False

    qty_key = f"qty_input_{produit}"
    if qty_key in st.session_state:
        del st.session_state[qty_key]


def ajouter_custom():
    nom = st.session_state.custom_produit.strip()
    if nom:
        st.session_state.liste.setdefault(nom, 1)
        st.session_state.custom_produit = ""


def vider_liste():
    for produit in list(st.session_state.liste.keys()):
        supprimer(produit)


def generer_texte():
    return "\n".join(f"- {p} x{q}" for p, q in st.session_state.liste.items())


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
st.title("🛒 Ma liste de courses")

col_choix, col_liste = st.columns([1.4, 1])

with col_choix:
    st.subheader("Choisir les produits")
    tabs = st.tabs(list(PRODUITS.keys()))

    for tab, (cat, produits) in zip(tabs, PRODUITS.items()):
        with tab:
            cols = st.columns(2)
            for i, produit in enumerate(produits):
                with cols[i % 2]:
                    st.checkbox(
                        produit,
                        key=f"chk_{cat}_{produit}",
                        on_change=toggle_produit,
                        args=(cat, produit),
                    )

    st.divider()
    st.subheader("Ajouter un produit personnalisé")
    c1, c2 = st.columns([3, 1])
    c1.text_input(
        "Nom du produit",
        key="custom_produit",
        label_visibility="collapsed",
        placeholder="Ex : Papier aluminium",
    )
    c2.button("Ajouter", on_click=ajouter_custom, use_container_width=True)

with col_liste:
    nb = len(st.session_state.liste)
    st.subheader(f"📋 Liste ({nb} article{'s' if nb > 1 else ''})")

    if not st.session_state.liste:
        st.info("Ta liste est vide, coche des produits à gauche !")
    else:
        for produit, qty in list(st.session_state.liste.items()):
            c1, c2, c3 = st.columns([3, 1.3, 0.8])
            c1.write(produit)
            c2.number_input(
                "quantité",
                min_value=1,
                max_value=99,
                value=qty,
                key=f"qty_input_{produit}",
                on_change=update_qty,
                args=(produit,),
                label_visibility="collapsed",
            )
            c3.button(
                "🗑️",
                key=f"del_{produit}",
                on_click=supprimer,
                args=(produit,),
                use_container_width=True,
            )

        st.divider()
        st.button("🧹 Vider la liste", on_click=vider_liste, use_container_width=True)

        st.caption("📋 Copier la liste (icône en haut à droite du bloc), puis coller dans Notes :")
        st.code(generer_texte(), language=None)