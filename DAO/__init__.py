import psycopg2

def conexaodb():
    """Estabelece conexão com o banco de dados e retorna a conexão"""
    return psycopg2.connect(
        dbname="reconhecimentoFacial",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )


# Função para salvar uma pessoa e sua imagem no banco
def salvar_pessoa(nome, image_path):
    """Salva uma pessoa no banco com a imagem convertida para BYTEA."""
    try:
        conn = conexaodb()
        cursor = conn.cursor()

        with open(image_path, 'rb') as file:
            binary_image = file.read()

        query = "INSERT INTO images (name, image) VALUES (%s, %s) RETURNING id"
        cursor.execute(query, (nome, binary_image))
        pessoa_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()
        return pessoa_id
    except Exception as e:
        print(f"Erro ao salvar pessoa: {e}")
        return None


def buscar_todas_pessoas():
    """Retorna todas as pessoas e suas imagens em bytes."""
    try:
        conn = conexaodb()
        cursor = conn.cursor()
        query = "SELECT id, name, image FROM images"
        cursor.execute(query)
        pessoas = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convertendo memoryview para bytes
        return [(id, nome, bytes(imagem)) for id, nome, imagem in pessoas]
    except Exception as e:
        print(f"Erro ao buscar pessoas: {e}")
        return []


#salvar_pessoa("Layza", "C:\\Users\\joseb\\Desktop\\Catolica\\ProgramacaoParalela\\WIN_20250326_18_35_51_Pro.jpg")

#print(buscar_pessoa_por_id(7))

#print(buscar_todas_pessoas())