db = db.getSiblingDB('persistenciodb')
db.minha_colecao.insertOne({ nome: "Exemplo", valor: 123 });
db.minha_colecao.drop();