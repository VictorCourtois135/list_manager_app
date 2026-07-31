import json

import streamlit as st
import streamlit.components.v1 as components

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
        "Lait", "Beurre", "Yaourts Grecque", "Crème fraîche", 
        "Parmesan", "Mozzarella", "Feta", "Gruyère"
    ],
    "🍞 Épicerie": [
        "Pain", "Pâtes", "Riz", "Farine", "Sucre", "Huile d'olive",
        "Café", "Thé", "Sel", "Conserves", "Nutella",
        "Papier alu", "Papier de cuisson",
    ],
    "🥤 Boissons": [
        "Eau", "Jus de fruits", "Soda", "Vin", "Bière", "Tonic", "Grenadine",
    ],
    "🧴 Produits ménagers": [
        "Liquide vaisselle", "Éponges", "Papier toilette", "Sacs poubelle",
        "Lessive", "Essuie-tout", "Liquide de rinçage",
        "Pastilles lave-vaisselle", "Sel lave-vaisselle", "Javel",
    ],
    "🧼 Hygiène": [
        "Shampoing", "Savon", "Dentifrice", "Déodorant", 
    ],
    "🌿 Herbes & Épices": [
        "Basilic", "Menthe", "Paprika", "Cumin", "Ail semoule",
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


def bouton_copier(texte):
    """Affiche un bouton HTML/JS qui copie `texte` dans le presse-papier,
    avec une méthode de secours si l'API clipboard est bloquée (webview mobile)."""
    texte_json = json.dumps(texte)
    html = f"""
    <button id="copy-btn" style="
        width:100%; padding:0.6em 1em; font-size:1rem; font-weight:600;
        border-radius:0.5rem; border:1px solid rgba(49,51,63,0.2);
        background:#f0f2f6; cursor:pointer;">
        📋 Copier la liste
    </button>
    <script>
    const texte = {texte_json};
    const btn = document.getElementById('copy-btn');

    function repli(text) {{
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        try {{ document.execCommand('copy'); }} catch (e) {{}}
        document.body.removeChild(ta);
    }}

    btn.addEventListener('click', function () {{
        const succes = function () {{
            btn.innerText = '✅ Copié !';
            setTimeout(function () {{ btn.innerText = '📋 Copier la liste'; }}, 1500);
        }};
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(texte).then(succes).catch(function () {{
                repli(texte);
                succes();
            }});
        }} else {{
            repli(texte);
            succes();
        }}
    }});
    </script>
    """
    components.html(html, height=50)


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

        st.caption("Aperçu de la liste :")
        st.code(generer_texte(), language=None)
        bouton_copier(generer_texte())
        st.caption("Appuie sur le bouton, puis colle (appui long → *Coller*) dans Notes.")