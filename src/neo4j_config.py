from neo4j import GraphDatabase

# ==============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==============================================================================

class Neo4jDriver:
    """
    Driver Singleton para conexão com o Neo4j.
    """
    neo4j_host = "neo4j+s://f217f659.databases.neo4j.io"
    neo4j_user = "neo4j"
    neo4j_password = "h4KCKmkPtEpA7oxm24xufukETPSN-KQHnFDynf17mEI"

    driver = None

    @staticmethod
    def get_driver():
        if not Neo4jDriver.driver:
            Neo4jDriver.driver = GraphDatabase.driver(
                Neo4jDriver.neo4j_host,
                auth=(Neo4jDriver.neo4j_user, Neo4jDriver.neo4j_password)
            )
        return Neo4jDriver.driver


# ==============================================================================
# MODELOS (ENTIDADES)
# ==============================================================================

class Filme:
    def __init__(self, titulo, ano, sinopse, generos=None, caracteristicas=None):
        self.titulo = titulo
        self.ano = ano
        self.sinopse = sinopse
        self.generos = generos or []
        self.caracteristicas = caracteristicas or []

    def to_dict(self):
        return {"titulo": self.titulo, "ano": self.ano, "sinopse": self.sinopse}


class Pessoa:
    def __init__(self, nome, filmes_atuados=None):
        self.nome = nome
        self.filmes_atuados = filmes_atuados or []

    def to_dict(self):
        return {"nome": self.nome}


class Genero:
    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        return {"nome": self.nome}


class Caracteristica:
    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        return {"nome": self.nome}


# ==============================================================================
# DAOs (DATA ACCESS OBJECTS)
# ==============================================================================

class FilmeDAO:
    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    # ------------------- CREATE -----------------------
    def add_filme(self, filme: Filme):
        with self.driver.session() as session:
            # Criar filme
            session.run("""
                MERGE (f:Filme {titulo: $titulo})
                SET f.ano = $ano, f.sinopse = $sinopse
            """, **filme.to_dict())

            # Gêneros
            for genero in filme.generos:
                session.run("""
                    MATCH (f:Filme {titulo: $titulo})
                    MERGE (g:Genero {nome: $g})
                    MERGE (f)-[:TEM_GENERO]->(g)
                """, titulo=filme.titulo, g=genero)

            # Características
            for car in filme.caracteristicas:
                session.run("""
                    MATCH (f:Filme {titulo: $titulo})
                    MERGE (c:Caracteristica {nome: $c})
                    MERGE (f)-[:TEM_CARAC]->(c)
                """, titulo=filme.titulo, c=car)

    # ------------------- READ -------------------------
    def list_filmes(self):
        with self.driver.session() as session:
            result = session.run("MATCH (f:Filme) RETURN f.titulo AS titulo, f.ano AS ano")
            return [r.data() for r in result]

    def get_filme(self, titulo):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (f:Filme {titulo: $titulo})
                RETURN f
            """, titulo=titulo)
            rec = result.single()
            return rec["f"] if rec else None

    # ------------------- UPDATE -----------------------
    def update_filme(self, titulo, novo_titulo=None, ano=None, sinopse=None):
        with self.driver.session() as session:
            session.run("""
                MATCH (f:Filme {titulo: $titulo})
                SET f.titulo = COALESCE($novo_titulo, f.titulo),
                    f.ano = COALESCE($ano, f.ano),
                    f.sinopse = COALESCE($sinopse, f.sinopse)
            """, titulo=titulo, novo_titulo=novo_titulo, ano=ano, sinopse=sinopse)

    # ------------------- DELETE -----------------------
    def delete_filme(self, titulo):
        with self.driver.session() as session:
            session.run("""
                MATCH (f:Filme {titulo: $titulo})
                DETACH DELETE f
            """, titulo=titulo)


class PessoaDAO:
    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    # CREATE
    def add_pessoa(self, pessoa: Pessoa):
        with self.driver.session() as session:
            session.run("""MERGE (p:Pessoa {nome: $nome})""", **pessoa.to_dict())

            for filme in pessoa.filmes_atuados:
                session.run("""
                    MATCH (p:Pessoa {nome: $p})
                    MATCH (f:Filme {titulo: $f})
                    MERGE (p)-[:ATUOU_EM]->(f)
                """, p=pessoa.nome, f=filme)

    # READ
    def list_pessoas(self):
        with self.driver.session() as session:
            result = session.run("""MATCH (p:Pessoa) RETURN p.nome AS nome""")
            return [r.data() for r in result]

    # UPDATE
    def update_pessoa(self, nome, novo_nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (p:Pessoa {nome: $nome})
                SET p.nome = $novo_nome
            """, nome=nome, novo_nome=novo_nome)

    # DELETE
    def delete_pessoa(self, nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (p:Pessoa {nome: $nome})
                DETACH DELETE p
            """, nome=nome)


class GeneroDAO:
    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    def add_genero(self, genero: Genero):
        self.driver.execute_query("""
            MERGE (g:Genero {nome: $nome})
        """, **genero.to_dict())

    def list_generos(self):
        with self.driver.session() as session:
            result = session.run("MATCH (g:Genero) RETURN g.nome AS nome ORDER BY nome")
            return [r.data() for r in result]

    def update_genero(self, nome, novo_nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (g:Genero {nome: $nome})
                SET g.nome = $novo_nome
            """, nome=nome, novo_nome=novo_nome)

    def delete_genero(self, nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (g:Genero {nome: $nome})
                DETACH DELETE g
            """, nome=nome)


class CaracteristicaDAO:
    def __init__(self):
        self.driver = Neo4jDriver.get_driver()

    def add_caracteristica(self, caracteristica: Caracteristica):
        self.driver.execute_query("""
            MERGE (c:Caracteristica {nome: $nome})
        """, **caracteristica.to_dict())

    def list_caracteristicas(self):
        with self.driver.session() as session:
            result = session.run("MATCH (c:Caracteristica) RETURN c.nome AS nome ORDER BY nome")
            return [r.data() for r in result]

    def update_caracteristica(self, nome, novo_nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Caracteristica {nome: $nome})
                SET c.nome = $novo_nome
            """, nome=nome, novo_nome=novo_nome)

    def delete_caracteristica(self, nome):
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Caracteristica {nome: $nome})
                DETACH DELETE c
            """, nome=nome)


# ==============================================================================
# CLI (MENU DO TRABALHO)
# ==============================================================================

def menu_filmes():
    dao = FilmeDAO()

    while True:
        print("""
===== FILMES =====
1 - Cadastrar filme
2 - Listar filmes
3 - Atualizar filme
4 - Remover filme
0 - Voltar
""")
        op = input("Opção: ")

        if op == "1":
            titulo = input("Título: ")
            ano = int(input("Ano: "))
            sinopse = input("Sinopse: ")

            generos = input("Gêneros (separados por vírgula): ").split(",")
            generos = [g.strip() for g in generos if g.strip()]

            carac = input("Características (vírgula): ").split(",")
            carac = [c.strip() for c in carac if c.strip()]

            filme = Filme(titulo, ano, sinopse, generos, carac)
            dao.add_filme(filme)
            print("Filme cadastrado!")

        elif op == "2":
            for f in dao.list_filmes():
                print(f)

        elif op == "3":
            titulo = input("Filme a atualizar: ")
            novo = input("Novo título (Enter para manter): ") or None
            ano = input("Novo ano (Enter para manter): ")
            ano = int(ano) if ano else None
            sinopse = input("Nova sinopse (Enter para manter): ") or None

            dao.update_filme(titulo, novo_titulo=novo, ano=ano, sinopse=sinopse)
            print("Atualizado!")

        elif op == "4":
            titulo = input("Título do filme: ")
            dao.delete_filme(titulo)
            print("Removido!")

        elif op == "0":
            break


def menu_pessoas():
    dao = PessoaDAO()

    while True:
        print("""
===== PESSOAS =====
1 - Cadastrar pessoa
2 - Listar pessoas
3 - Atualizar pessoa
4 - Remover pessoa
0 - Voltar
""")
        op = input("Opção: ")

        if op == "1":
            nome = input("Nome: ")
            filmes = input("Filmes atuados (vírgula): ").split(",")
            filmes = [f.strip() for f in filmes if f.strip()]
            pessoa = Pessoa(nome, filmes)
            dao.add_pessoa(pessoa)
            print("Pessoa cadastrada!")

        elif op == "2":
            for p in dao.list_pessoas():
                print(p)

        elif op == "3":
            nome = input("Nome atual: ")
            novo = input("Novo nome: ")
            dao.update_pessoa(nome, novo)
            print("Atualizado!")

        elif op == "4":
            nome = input("Nome: ")
            dao.delete_pessoa(nome)
            print("Removido!")

        elif op == "0":
            break


def menu_generos():
    dao = GeneroDAO()

    while True:
        print("""
===== GÊNEROS =====
1 - Cadastrar gênero
2 - Listar gêneros
3 - Atualizar gênero
4 - Remover gênero
0 - Voltar
""")
        op = input("Opção: ")

        if op == "1":
            nome = input("Nome: ")
            dao.add_genero(Genero(nome))
            print("Cadastrado!")

        elif op == "2":
            for g in dao.list_generos():
                print(g)

        elif op == "3":
            atual = input("Nome atual: ")
            novo = input("Novo nome: ")
            dao.update_genero(atual, novo)
            print("Atualizado!")

        elif op == "4":
            nome = input("Nome: ")
            dao.delete_genero(nome)
            print("Removido!")

        elif op == "0":
            break


def menu_caracteristicas():
    dao = CaracteristicaDAO()

    while True:
        print("""
===== CARACTERÍSTICAS =====
1 - Cadastrar característica
2 - Listar características
3 - Atualizar característica
4 - Remover característica
0 - Voltar
""")
        op = input("Opção: ")

        if op == "1":
            nome = input("Nome: ")
            dao.add_caracteristica(Caracteristica(nome))
            print("Cadastrado!")

        elif op == "2":
            for c in dao.list_caracteristicas():
                print(c)

        elif op == "3":
            atual = input("Nome atual: ")
            novo = input("Novo nome: ")
            dao.update_caracteristica(atual, novo)
            print("Atualizado!")

        elif op == "4":
            nome = input("Nome: ")
            dao.delete_caracteristica(nome)
            print("Removido!")

        elif op == "0":
            break


# ==============================================================================
# MENU PRINCIPAL
# ==============================================================================

def main():
    while True:
        print("""
===== CINEGRAPH — MENU PRINCIPAL =====
1 - CRUD Filmes
2 - CRUD Pessoas
3 - CRUD Gêneros
4 - CRUD Características
0 - Sair
""")
        op = input("Opção: ")

        if op == "1":
            menu_filmes()
        elif op == "2":
            menu_pessoas()
        elif op == "3":
            menu_generos()
        elif op == "4":
            menu_caracteristicas()
        elif op == "0":
            print("Saindo...")
            break


if __name__ == "__main__":
    main()
