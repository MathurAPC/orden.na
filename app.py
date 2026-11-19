import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import hashlib

st.set_page_config(
    page_title="ORDEN.NA - Registro de Demandas",
    layout="wide"
)

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-color: #E9D5FF !important;
        color: #9A6700 !important;
    }
    [data-testid="stAppViewContainer"] > .main h1,
    [data-testid="stAppViewContainer"] > .main h2,
    [data-testid="stAppViewContainer"] > .main h3,
    [data-testid="stAppViewContainer"] > .main p,
    [data-testid="stAppViewContainer"] > .main span,
    [data-testid="stAppViewContainer"] > .main label,
    [data-testid="stAppViewContainer"] > .main div {
        color: #9A6700 !important;
    }

    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"] > .main {
            background-color: #130722 !important;
            color: #FFDE59 !important;
        }
        [data-testid="stAppViewContainer"] > .main h1,
        [data-testid="stAppViewContainer"] > .main h2,
        [data-testid="stAppViewContainer"] > .main h3,
        [data-testid="stAppViewContainer"] > .main p,
        [data-testid="stAppViewContainer"] > .main span,
        [data-testid="stAppViewContainer"] > .main label,
        [data-testid="stAppViewContainer"] > .main div {
            color: #FFDE59 !important;
        }
    }

    [data-testid="stSidebar"] {
        background-color: #724C99 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFDE59 !important;
    }
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def conectar():
    conn = sqlite3.connect("banco.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def criar_tabelas():
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha VARCHAR(255) NOT NULL,
            setor VARCHAR(50),
            perfil_acesso VARCHAR(30)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS demanda (
            id_demanda INTEGER PRIMARY KEY AUTOINCREMENT,
            iniciodat DATE,
            entregadat DATE,
            iniciohr TIME,
            entregahr TIME,
            tarefa_realizada TEXT NOT NULL,
            status VARCHAR(20)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id_reg INTEGER PRIMARY KEY AUTOINCREMENT,
            id_demanda INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            historico VARCHAR(500),
            FOREIGN KEY (id_demanda) REFERENCES demanda(id_demanda) ON DELETE CASCADE,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        )
    """)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuario")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO usuario (nome, email, senha, setor, perfil_acesso)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Administrador Orden.na",
            "admin@orden.na",
            criptografar_senha("123456"),
            "Gestão",
            "Administrador"
        ))
    conn.commit()
    conn.close()

def autenticar_usuario(email, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_usuario, nome, setor, perfil_acesso FROM usuario WHERE email = ? AND senha = ?",
        (email.strip(), criptografar_senha(senha))
    )
    user = cursor.fetchone()
    conn.close()
    return user

def buscar_usuarios():
    conn = conectar()
    df_users = pd.read_sql_query("SELECT * FROM usuario ORDER BY nome", conn)
    conn.close()
    return df_users

def buscar_dados():
    conn = conectar()
    query = """
        SELECT 
            r.id_reg,
            d.id_demanda,
            u.nome AS responsavel,
            u.setor,
            d.tarefa_realizada,
            d.iniciodat,
            d.entregadat,
            d.iniciohr,
            d.entregahr,
            d.status,
            r.historico
        FROM registros r
        INNER JOIN demanda d ON r.id_demanda = d.id_demanda
        INNER JOIN usuario u ON r.id_usuario = u.id_usuario
        ORDER BY d.id_demanda DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def atualizar_status_demanda(id_demanda, novo_status):
    conn = conectar()
    conn.execute(
        "UPDATE demanda SET status = ? WHERE id_demanda = ?",
        (novo_status, int(id_demanda))
    )
    conn.commit()
    conn.close()

def excluir_demanda(id_demanda):
    conn = conectar()
    conn.execute("DELETE FROM registros WHERE id_demanda = ?", (int(id_demanda),))
    conn.execute("DELETE FROM demanda WHERE id_demanda = ?", (int(id_demanda),))
    conn.commit()
    conn.close()

criar_tabelas()

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

logo_svg = """
<div style="display: flex; justify-content: flex-start; margin-top: -35px; margin-bottom: 10px;">
    <svg width="70" height="70" viewBox="0 0 100 100" xmlns="http://w3.org">
        <g fill="#FFDE59">
            <polygon points="50,6 44,18 56,18"/>
            <polygon points="50,94 44,82 56,82"/>
            <polygon points="6,50 18,44 18,56"/>
            <polygon points="94,50 82,44 82,56"/>
            <polygon points="19,19 23,31 31,23"/>
            <polygon points="81,81 77,69 69,77"/>
            <polygon points="81,19 69,23 77,31"/>
            <polygon points="19,81 31,77 23,69"/>
            <polygon points="33,10 31,22 42,19"/>
            <polygon points="67,90 69,78 58,81"/>
            <polygon points="90,33 78,31 81,42"/>
            <polygon points="10,67 22,69 19,58"/>
            <polygon points="67,10 58,19 69,22"/>
            <polygon points="33,90 42,81 31,78"/>
            <polygon points="90,67 81,58 78,69"/>
            <polygon points="10,33 19,42 22,31"/>
        </g>
        <circle cx="50" cy="50" r="26" fill="none" stroke="#FFDE59" stroke-width="5.5"/>
        <text x="50" y="57" font-family="Arial, sans-serif" font-weight="bold" font-size="21" fill="#FFDE59" text-anchor="middle">.na</text>
    </svg>
</div>
"""

if st.session_state["usuario_logado"] is None:
    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
    st.sidebar.title("ORDEN.NA")
    st.sidebar.caption("Acesso restrito ao sistema")

    col_esq, col_centro, col_dir = st.columns([1, 2, 1])
    with col_centro:
        st.title("Acesso ao ORDEN.NA")
        st.write("Entre com suas credenciais para gerenciar demandas.")
        with st.form("form_login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("Entrar", use_container_width=True)

            if entrar:
                usuario = autenticar_usuario(email_login, senha_login)
                if usuario:
                    st.session_state["usuario_logado"] = {
                        "id": usuario[0],
                        "nome": usuario[1],
                        "setor": usuario[2],
                        "perfil": usuario[3]
                    }
                    st.rerun()
                else:
                    st.error("E-mail ou senha inválidos.")
        st.caption("Acesso inicial de teste: admin@orden.na | Senha: 123456")

else:
    user_info = st.session_state["usuario_logado"]

    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)
    st.sidebar.title("ORDEN.NA")
    st.sidebar.caption(f"Olá, {user_info['nome']} ({user_info['perfil']})")

    menus = [
        "Dashboard",
        "Registrar demanda",
        "Quadro de demandas",
        "Histórico",
        "Relatórios"
    ]

    if user_info["perfil"] in ["Administrador", "Gestor"]:
        menus.insert(1, "Cadastrar usuário")

    pagina = st.sidebar.radio("Navegação", menus)

    st.sidebar.divider()
    if st.sidebar.button("Sair da conta", use_container_width=True):
        st.session_state["usuario_logado"] = None
        st.rerun()

    df = buscar_dados()
    df_usuarios = buscar_usuarios()

    if pagina == "Dashboard":

        st.title("Dashboard")
        st.write("Visão geral das demandas registradas no Orden.na.")

        total = len(df)
        concluidas = len(df[df["status"] == "Concluída"]) if total else 0
        em_andamento = len(df[df["status"] == "Em andamento"]) if total else 0
        canceladas = len(df[df["status"] == "Cancelada/Não feita"]) if total else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de demandas", total)
        c2.metric("Concluídas", concluidas)
        c3.metric("Em andamento", em_andamento)
        c4.metric("Canceladas/Não feitas", canceladas)

        st.divider()

        if total > 0:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Demandas por setor")
                fig = px.bar(
                    df.groupby("setor").size().reset_index(name="Quantidade"),
                    x="setor",
                    y="Quantidade",
                    color="setor"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Situação das demandas")
                fig = px.pie(
                    df,
                    names="status",
                    hole=0.45
                )
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Registros recentes")
            st.dataframe(
                df.head(5),
                use_container_width=True,
                hide_index=True
            ) 
       

    elif pagina == "Cadastrar usuário":
        st.title("Cadastrar Usuário")
        st.info("Página de cadastro em construção...")

    elif pagina == "Registrar demanda":
        st.title("Registrar Demanda")
        with st.form("form_nova_demanda"):
            tarefa = st.text_input("Tarefa realizada")
            tipo = st.text_input("Tipo de demanda")
            substituido = st.text_input("Substituído (opcional)")
            
            c1, c2 = st.columns(2)
            iniciodat = c1.date_input("Data de Início")
            iniciohr = c2.time_input("Hora de Início")
            
            c3, c4 = st.columns(2)
            entregadat = c3.date_input("Data de Entrega")
            entregahr = c4.time_input("Hora de Entrega")
            
            salvar = st.form_submit_button("Salvar Demanda")
            
            if salvar and tarefa:
                conn = conectar()
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO demanda (iniciodat, entregadat, iniciohr, entregahr, tarefa_realizada, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (iniciodat, entregadat, str(iniciohr), str(entregahr), tarefa, "Em andamento"))
                
          
                id_demanda_criada = cursor.lastrowid
                
                texto_historico = f"Tipo: {tipo}"
                if substituido.strip():
                    texto_historico += f" | Substituído: {substituido.strip()}"
                
                id_usuario_selecionado = user_info["id"]
                
                cursor.execute("""
                    INSERT INTO registros (id_demanda, id_usuario, historico)
                    VALUES (?, ?, ?)
                """, (
                    id_demanda_criada,
                    id_usuario_selecionado,
                    texto_historico
                ))
                conn.commit()
                conn.close()
                st.success("Demanda e registro vinculados com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

    elif pagina == "Quadro de demandas":
        st.title("Quadro de demandas")
        if not df.empty:
            colunas = st.columns(3)
            opcoes_status = ["Em andamento", "Concluída", "Cancelada/Não feita"]
            for coluna, situacao in zip(colunas, opcoes_status):
                with coluna:
                    st.subheader(situacao)
                    registros = df[df["status"] == situacao]
                    for _, item in registros.iterrows():
                        with st.container(border=True):
                            st.write(f"{item['tarefa_realizada']}")
                            st.caption(f"Responsável: {item['responsavel']} ({item['setor']})")
                            st.caption(f"Entrega: {item['entregadat']} às {item['entregahr']}")
                            st.caption(item["historico"])
                            
                            novo_status = st.selectbox(
                                "Alterar status",
                                opcoes_status,
                                index=opcoes_status.index(item["status"]),
                                key=f"status_{item['id_demanda']}"
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("Atualizar", key=f"upd_{item['id_demanda']}", use_container_width=True):
                                    atualizar_status_demanda(item["id_demanda"], novo_status)
                                    st.rerun()
                            with col_btn2:
                                if user_info["perfil"] in ["Administrador", "Gestor"]:
                                    if st.button("Excluir", key=f"del_{item['id_demanda']}", use_container_width=True):
                                        excluir_demanda(item["id_demanda"])
                                        st.rerun()
        else:
            st.info("Não existem demandas para exibir.")

    elif pagina == "Histórico":
        st.title("Histórico de registros")
        if not df.empty:
            pesquisa = st.text_input("Pesquisar responsável, setor, tarefa ou histórico")
            filtrado = df.copy()
            if pesquisa:
                mascara = filtrado.astype(str).apply(
                    lambda coluna: coluna.str.contains(
                        pesquisa,
                        case=False,
                        na=False
                    )
                ).any(axis=1)
                filtrado = filtrado[mascara]
            
            st.dataframe(
                filtrado,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhum registro encontrado.")

    elif pagina == "Relatórios":
        st.title("Relatórios")
        if not df.empty:
            st.write("Consulte e exporte os registros consolidados.")
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Exportar dados para CSV",
                data=csv,
                file_name="relatorio_orden_na.csv",
                mime="text/csv"
            )
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Não existem dados para gerar relatórios.")
