CineGraph 🎬
Sobre o Projeto
CineGraph é um projeto de banco de dados em grafo, construído com Neo4j, que modela o universo cinematográfico. O objetivo é criar um poderoso sistema de recomendações, permitindo descobrir filmes com base em conexões profundas e compartilhadas, como atores, gêneros e características temáticas em comum.

💡 O Poder do Grafo
Em um banco de dados relacional tradicional (como SQL), encontrar "filmes que um ator de 'Matrix' também fez, que compartilham a mesma característica 'Distopia'" exigiria múltiplas e complexas junções (JOINs), tornando a consulta lenta e difícil de escrever.

O Neo4j é otimizado para esse tipo de consulta de "redes". Em vez de JOINs, ele "atravessa" relações. Perguntas complexas sobre conexões e recomendações tornam-se simples, rápidas e intuitivas.

🗺️ A Estrutura do Grafo
O CineGraph modela o "DNA" dos filmes conectando 4 tipos principais de Nós:

Filme: O nó central.

Propriedades: titulo, ano, sinopse.

Pessoa: Representa os atores.

Propriedades: nome.

Gênero: As categorias do filme.

Propriedades: nome (ex: "Ficção Científica", "Drama").

Caracteristica: Os temas, conceitos ou estilos do filme.

Propriedades: nome (ex: "Inteligência Artificial", "Viagem no Tempo", "Baseado em Fatos Reais").

Esses nós são conectados através de 3 Relações:

(Pessoa)-[:ATUOU_EM]->(Filme)

(Filme)-[:É_DO_GÊNERO]->(Gênero)

(Filme)-[:POSSUI_CARACTERISTICA]->(Caracteristica)

🧠 Descobrindo Conexões Ocultas
A mágica do CineGraph não está em relações diretas (Filme A -> Filme B), mas nas conexões indiretas feitas através de nós em comum.

Exemplo 1: Conexão por Atores
Um usuário que assistiu "Matrix" pode descobrir "John Wick" através da relação compartilhada com o ator Keanu Reeves.

(Pessoa {nome: "Keanu Reeves"})-[:ATUOU_EM]->(Filme {titulo: "Matrix"})

(Pessoa {nome: "Keanu Reeves"})-[:ATUOU_EM]->(Filme {titulo: "John Wick"})

Exemplo 2: Conexão por Temas (Características)
Um usuário que gostou do tema de "Matrix" pode descobrir "Ex Machina" através da característica "Inteligência Artificial".

(Filme {titulo: "Matrix"})-[:POSSUI_CARACTERISTICA]->(Caracteristica {nome: "Inteligência Artificial"})

(Filme {titulo: "Ex Machina"})-[:POSSUI_CARACTERISTICA]->(Caracteristica {nome: "Inteligência Artificial"})


🚀 Como Executar
O projeto pode ser populado e consultado diretamente através do Neo4j Browser usando a linguagem Cypher.

Exemplo de Criação de Dados
Cypher

// Criar o filme Matrix e seus atributos
CREATE (m:Filme {titulo: "Matrix", ano: 1999, sinopse: "Um hacker descobre a verdade sobre sua realidade."})
CREATE (p:Pessoa {nome: "Keanu Reeves"})
CREATE (g:Gênero {nome: "Ficção Científica"})
CREATE (c:Caracteristica {nome: "Inteligência Artificial"})
CREATE (c2:Caracteristica {nome: "Distopia"})

// Criar as relações
MERGE (p)-[:ATUOU_EM]->(m)
MERGE (m)-[:É_DO_GÊNERO]->(g)
MERGE (m)-[:POSSUI_CARACTERISTICA]->(c)
MERGE (m)-[:POSSUI_CARACTERISTICA]->(c2)
Exemplo de Consulta (Recomendação)
Cypher

// Encontrar outros filmes do gênero "Ficção Científica" 
// que compartilham a característica "Inteligência Artificial"
MATCH (f:Filme)-[:É_DO_GÊNERO]->(g:Gênero {nome: "Ficção Científica"})
MATCH (f)-[:POSSUI_CARACTERISTICA]->(c:Caracteristica {nome: "Inteligência Artificial"})
WHERE f.titulo <> "Matrix"
RETURN f.titulo, f.ano


📝 Licença
Este projeto é um protótipo de banco de dados e pode ser usado livremente para fins educacionais e de portfólio.