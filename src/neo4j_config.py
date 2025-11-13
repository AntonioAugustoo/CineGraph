from neo4j import GraphDatabase

# ==============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==============================================================================

class Neo4jDriver:
    # TODO: Cole aqui a "Connection URI" que você copiou do Neo4j Aura
    neo4j_host = "neo4j+s://f217f659.databases.neo4j.io"
    
   
    neo4j_user = "neo4j"
    
    
    neo4j_password = "h4KCKmkPtEpA7oxm24xufukETPSN-KQHnFDynf17mEI"    

    driver = None

    @staticmethod
    def get_driver():
        """
        Retorna uma instância única do driver do Neo4j (Singleton)
        e limpa o banco de dados para testes.
        """
        if not Neo4jDriver.driver:
            Neo4jDriver.driver = GraphDatabase.driver(
                Neo4jDriver.neo4j_host, 
                auth=(Neo4jDriver.neo4j_user, Neo4jDriver.neo4j_password)
            )
            # Limpa o banco para garantir um estado limpo a cada execução
            Neo4jDriver.driver.execute_query("MATCH (n) DETACH DELETE n")
        return Neo4jDriver.driver

# ==============================================================================
# CLASSES DE MODELO (ENTIDADES DO PROJETO CINEGRAPH)
# ==============================================================================

class Filme:
    """Representa o nó :Filme"""
    def __init__(self, titulo, ano, sinopse, generos = [], caracteristicas = []):
        self.titulo = titulo
        self.ano = ano
        self.sinopse = sinopse
        self.generos = generos
        self.caracteristicas = caracteristicas

    def to_dict(self):
        """Retorna um dicionário para os parâmetros da query Cypher"""
        return {
            "titulo": self.titulo,
            "ano": self.ano,
            "sinopse": self.sinopse,
        }

class Pessoa:
    """Representa o nó :Pessoa (Ator)"""
    def __init__(self, nome, filmes_atuados = []):
        self.nome = nome
        self.filmes_atuados = filmes_atuados # Lista de títulos de filmes

    def to_dict(self):
        """Retorna um dicionário para os parâmetros da query Cypher"""
        return {"nome": self.nome}

class Genero:
    """Representa o nó :Gênero"""
    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        """Retorna um dicionário para os parâmetros da query Cypher"""
        return {"nome": self.nome}

class Caracteristica:
    """Representa o nó :Caracteristica"""
    def __init__(self, nome):
        self.nome = nome

    def to_dict(self):
        """Retorna um dicionário para os parâmetros da query Cypher"""
        return {"nome": self.nome}

# ==============================================================================
# CLASSES DAO (DATA ACCESS OBJECTS)
# ==============================================================================

class FilmeDAO:
    """Controla todas as operações relacionadas aos Filmes"""
    def __init__(self) -> None:
        self.neo4j_driver = Neo4jDriver.get_driver()

    def add_filme(self, filme: Filme):
        """
        Cria um nó :Filme e o conecta aos seus :Genero e :Caracteristica
        """
        with self.neo4j_driver.session() as session:
            # 1. Cria o nó :Filme
            session.run("""
                MERGE (f:Filme {titulo: $titulo})
                SET f.ano = $ano, f.sinopse = $sinopse
            """, **filme.to_dict())
            
            # 2. Conecta o filme aos seus gêneros
            for genero_nome in filme.generos:
                session.run("""
                    MATCH (f:Filme {titulo: $titulo})
                    MERGE (g:Gênero {nome: $genero_nome})
                    MERGE (f)-[:É_DO_GÊNERO]->(g)
                """, titulo=filme.titulo, genero_nome=genero_nome)

            # 3. Conecta o filme às suas características
            for carac_nome in filme.caracteristicas:
                session.run("""
                    MATCH (f:Filme {titulo: $titulo})
                    MERGE (c:Caracteristica {nome: $carac_nome})
                    MERGE (f)-[:POSSUI_CARACTERISTICA]->(c)
                """, titulo=filme.titulo, carac_nome=carac_nome)

    def get_filmes_por_caracteristica(self, caracteristica_nome):
        """Busca filmes que possuem uma determinada característica"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (f:Filme)-[:POSSUI_CARACTERISTICA]->(c:Caracteristica {nome: $nome})
                RETURN f.titulo AS titulo, f.ano AS ano
            """, nome=caracteristica_nome)
            return [record.data() for record in result]

class PessoaDAO:
    """Controla todas as operações relacionadas às Pessoas (Atores)"""
    def __init__(self) -> None:
        self.neo4j_driver = Neo4jDriver.get_driver()

    def add_pessoa(self, pessoa: Pessoa):
        """Cria um nó :Pessoa e o conecta aos filmes que atuou"""
        
        # 1. Cria o nó :Pessoa (ator)
        self.neo4j_driver.execute_query("""
            MERGE (p:Pessoa {nome: $nome})
        """, **pessoa.to_dict())
        
        # 2. Conecta a pessoa aos filmes (Relação :ATUOU_EM)
        for titulo_filme in pessoa.filmes_atuados:
            self.neo4j_driver.execute_query("""
                MATCH (p:Pessoa {nome: $nome_pessoa})
                MATCH (f:Filme {titulo: $titulo_filme})
                MERGE (p)-[:ATUOU_EM]->(f)
            """, nome_pessoa=pessoa.nome, titulo_filme=titulo_filme)

    def get_filmes_por_ator(self, nome_ator):
        """Busca todos os filmes em que um ator atuou"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (p:Pessoa {nome: $nome})-[:ATUOU_EM]->(f:Filme)
                RETURN f.titulo AS titulo, f.ano AS ano
            """, nome=nome_ator)
            return [record.data() for record in result]

class GeneroDAO:
    """Controla todas as operações relacionadas aos Gêneros"""
    def __init__(self) -> None:
        self.neo4j_driver = Neo4jDriver.get_driver()

    def add_genero(self, genero: Genero):
        """Cria um nó :Gênero"""
        self.neo4j_driver.execute_query("""
            MERGE (g:Gênero {nome: $nome})
        """, **genero.to_dict())

    def get_all_generos(self):
        """Busca todos os gêneros cadastrados"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (g:Gênero)
                RETURN g.nome AS nome
                ORDER BY g.nome
            """)
            return [record.data() for record in result]

    def get_filmes_por_genero(self, nome_genero):
        """Busca todos os filmes de um determinado gênero"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (f:Filme)-[:É_DO_GÊNERO]->(g:Gênero {nome: $nome})
                RETURN f.titulo AS titulo, f.ano AS ano
                ORDER BY f.ano DESC
            """, nome=nome_genero)
            return [record.data() for record in result]

class CaracteristicaDAO:
    """Controla todas as operações relacionadas às Características"""
    def __init__(self) -> None:
        self.neo4j_driver = Neo4jDriver.get_driver()

    def add_caracteristica(self, caracteristica: Caracteristica):
        """Cria um nó :Caracteristica"""
        self.neo4j_driver.execute_query("""
            MERGE (c:Caracteristica {nome: $nome})
        """, **caracteristica.to_dict())

    def get_all_caracteristicas(self):
        """Busca todas as características cadastradas"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (c:Caracteristica)
                RETURN c.nome AS nome
                ORDER BY c.nome
            """)
            return [record.data() for record in result]

    def get_filmes_por_caracteristica(self, nome_caracteristica):
        """Busca todos os filmes com uma determinada característica"""
        with self.neo4j_driver.session() as session:
            result = session.run("""
                MATCH (f:Filme)-[:POSSUI_CARACTERISTICA]->(c:Caracteristica {nome: $nome})
                RETURN f.titulo AS titulo, f.ano AS ano
                ORDER BY f.ano DESC
            """, nome=nome_caracteristica)
            return [record.data() for record in result]

