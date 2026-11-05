import random
import streamlit as st

# Configuración inicial de la página
st.set_page_config(page_title="Video Póker", page_icon="🃏", layout="centered")

st.title("🃏 Video Póker - Jacks or Better")

# Inicializar créditos y estado
if "creditos" not in st.session_state:
  st.session_state.creditos = 100
if "mano" not in st.session_state:
  st.session_state.mano = []
if "baraja" not in st.session_state:
  st.session_state.baraja = []
if "fase" not in st.session_state:
  st.session_state.fase = "inicio"
if "holds" not in st.session_state:
  st.session_state.holds = [False] * 5
if "mensaje" not in st.session_state:
  st.session_state.mensaje = "¡Haz clic en Repartir para comenzar!"


def crear_baraja():
  palos = ["♠", "♥", "♦", "♣"]
  valores = [
      "2",
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
      "10",
      "J",
      "Q",
      "K",
      "A",
  ]
  pesos = {v: i + 2 for i, v in enumerate(valores)}
  baraja = [{"valor": v, "palo": p, "peso": pesos[v]} for p in palos for v in valores]
  random.shuffle(baraja)
  return baraja


def evaluar_mano(mano):
  mano_ord = sorted(mano, key=lambda x: x["peso"])
  vals = [c["peso"] for c in mano_ord]
  palos = [c["palo"] for c in mano_ord]

  es_flush = len(set(palos)) == 1
  es_straight = (vals == [2, 3, 4, 5, 14]) or (
      len(set(vals)) == 5 and (vals[-1] - vals[0] == 4)
  )

  conteo = {v: vals.count(v) for v in set(vals)}
  freq = sorted(conteo.values(), reverse=True)

  if es_flush and es_straight and vals[0] == 10:
    return "Royal Flush", 250
  if es_flush and es_straight:
    return "Straight Flush", 50
  if freq == [4, 1]:
    return "Póker", 25
  if freq == [3, 2]:
    return "Full House", 9
  if es_flush:
    return "Color", 6
  if es_straight:
    return "Escalera", 4
  if freq == [3, 1, 1]:
    return "Trío", 3
  if freq == [2, 2, 1]:
    return "Doble Pareja", 2

  if freq == [2, 1, 1, 1]:
    for val, count in conteo.items():
      if count == 2 and val >= 11:
        return "Jacks o Mejor", 1

  return "Sin premio", 0


# Interfaz visual
st.write(f"### 🪙 Créditos disponibles: {st.session_state.creditos}")
apuesta = st.number_input(
    "Apuesta:",
    min_value=1,
    max_value=max(1, st.session_state.creditos),
    value=min(5, st.session_state.creditos),
)
st.markdown("---")

if st.session_state.creditos <= 0:
  st.error("Te has quedado sin créditos.")
  if st.button("Reiniciar créditos"):
    st.session_state.creditos = 100
    st.session_state.fase = "inicio"
    st.rerun()

elif st.session_state.fase == "inicio":
  if st.button("🎴 Repartir Cartas", type="primary"):
    if st.session_state.creditos < apuesta:
      st.warning("No tienes suficientes créditos para esta apuesta.")
    else:
      st.session_state.creditos -= apuesta
      st.session_state.baraja = crear_baraja()
      st.session_state.mano = [st.session_state.baraja.pop() for _ in range(5)]
      st.session_state.holds = [False] * 5
      st.session_state.fase = "juego"
      st.rerun()

elif st.session_state.fase == "juego":
  st.write("**Selecciona las cartas que deseas mantener (HOLD):**")
  cols = st.columns(5)
  nuevos_holds = []

  for i, carta in enumerate(st.session_state.mano):
    with cols[i]:
      st.markdown(f"### {carta['valor']} {carta['palo']}")
      h = st.checkbox("Hold", value=st.session_state.holds[i], key=f"h_{i}")
      nuevos_holds.append(h)

  st.session_state.holds = nuevos_holds

  if st.button("🔄 Cambiar y Evaluar", type="primary"):
    nueva_mano = []
    for i, carta in enumerate(st.session_state.mano):
      if st.session_state.holds[i]:
        nueva_mano.append(carta)
      else:
        nueva_mano.append(st.session_state.baraja.pop())

    st.session_state.mano = nueva_mano
    jugada, mult = evaluar_mano(st.session_state.mano)
    premio = apuesta * mult
    st.session_state.creditos += premio

    if premio > 0:
      st.session_state.mensaje = (
          f"Resultado: **{jugada}**. ¡Ganaste {premio} créditos!"
      )
    else:
      st.session_state.mensaje = f"Resultado: **{jugada}**. Sin premio."

    st.session_state.fase = "resultado"
    st.rerun()

elif st.session_state.fase == "resultado":
  st.write("### Tus cartas finales:")
  cols = st.columns(5)