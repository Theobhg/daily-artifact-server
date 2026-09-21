"""Popula o banco com artefatos de exemplo.

Uso:
    python seed.py

O script e opcional e serve para ter um ano com conteudo ao explorar o
calendario e a listagem. Datas ja ocupadas sao ignoradas, entao ele pode ser
executado mais de uma vez sem duplicar nada.
"""

from datetime import date, timedelta

from app.database import SessionLocal, init_db
from app.exceptions import DomainError
from app.models.artifact import ArtifactType
from app.schemas.artifact import ArtifactCreate
from app.services.artifact_service import ArtifactService

# (dias atras, tipo, titulo, conteudo, url, tags)
SAMPLES: list[tuple[int, str, str | None, str | None, str | None, list[str]]] = [
    (0, "quote", "Anotado no fim da tarde", "O dia inteiro cabe em uma frase, se a frase for a certa.", None, ["memoria", "leitura"]),
    (1, "photo", "A luz das seis", "A cozinha ficou laranja por uns dez minutos.", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d", ["casa", "luz"]),
    (2, "music", "Tocou o dia inteiro", "Nao consegui ouvir outra coisa.", "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC", ["musica"]),
    (3, "text", "Conversa no corredor", "Encontrei uma pessoa que nao via ha anos e nenhum dos dois estava com pressa.", None, ["encontro"]),
    (5, "link", "Guardado para depois", "Um arquivo inteiro de capas de discos antigos.", "https://archive.org", ["arquivo", "leitura"]),
    (7, "quote", None, "Escrever e uma forma de prestar atencao.", None, ["leitura"]),
    (9, "photo", "Chuva na janela", None, "https://images.unsplash.com/photo-1519692933481-e162a57d6721", ["chuva"]),
    (12, "text", "Primeira vez que deu certo", "Levei tres tardes, mas funcionou de primeira quando parei de tentar.", None, ["trabalho"]),
    (15, "music", "Descoberta da semana", None, "https://open.spotify.com/track/7ouMYWpwJ422jRcDASZB7P", ["musica", "descoberta"]),
    (18, "quote", "De um livro emprestado", "As coisas que a gente repete viram as coisas que a gente e.", None, ["leitura"]),
    (21, "photo", "Feira de sabado", "Comprei mais do que cabia na sacola.", "https://images.unsplash.com/photo-1488459716781-31db52582fe9", ["comida", "cidade"]),
    (25, "text", "Silencio bom", "Passei a manha inteira sem falar com ninguem e foi exatamente do que eu precisava.", None, ["casa"]),
    (30, "link", "Vale reler", "Um ensaio curto sobre comecar coisas.", "https://www.gutenberg.org", ["arquivo"]),
    (36, "photo", "Caminho de volta", None, "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8", ["cidade"]),
    (42, "quote", None, "Memoria nao e o que aconteceu: e o que sobrou.", None, ["memoria"]),
    (50, "music", "Do carro, voltando", None, "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b", ["musica", "estrada"]),
    (58, "text", "Mudanca pequena", "Troquei a mesa de lugar e a casa inteira pareceu outra.", None, ["casa"]),
    (65, "photo", "Cafe da manha demorado", "Duas horas em uma mesa de padaria.", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085", ["comida"]),
    (74, "link", "Para o projeto", None, "https://fastapi.tiangolo.com", ["trabalho"]),
    (83, "quote", "Ouvido no onibus", "Ninguem avisa que a parte boa e essa.", None, ["cidade", "memoria"]),
    (95, "text", "Dia longo", "Terminou melhor do que comecou, o que ja e alguma coisa.", None, ["trabalho"]),
    (110, "photo", "Mar fora de estacao", None, "https://images.unsplash.com/photo-1505142468610-359e7d316be0", ["viagem"]),
    (124, "music", "Tocando na loja", "Perguntei o nome para o atendente.", "https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp", ["musica", "descoberta"]),
    (140, "text", "Comeco de alguma coisa", "Anotei a ideia inteira em um guardanapo e nao perdi o guardanapo.", None, ["trabalho", "memoria"]),
    (158, "quote", None, "Um dia de cada vez ainda e a unica forma que existe.", None, ["memoria"]),
    (175, "photo", "Janela do trem", None, "https://images.unsplash.com/photo-1474487548417-781cb71495f3", ["viagem", "estrada"]),
    (196, "link", "Achado do mes", "Mapas antigos digitalizados em altissima resolucao.", "https://www.loc.gov", ["arquivo"]),
    (215, "text", "Visita", "A casa cheia por um fim de semana inteiro.", None, ["familia"]),
    (240, "music", "A do verao", None, "https://open.spotify.com/track/1mea3bSkSGXuIRvnydlB5b", ["musica"]),
    (262, "quote", "Do caderno velho", "Guardar e uma forma de voltar.", None, ["memoria", "arquivo"]),
]


def main() -> None:
    init_db()
    today = date.today()
    created = 0
    skipped = 0

    with SessionLocal() as db:
        service = ArtifactService(db)

        for days_ago, artifact_type, title, content, url, tags in SAMPLES:
            payload = ArtifactCreate(
                artifact_date=today - timedelta(days=days_ago),
                type=ArtifactType(artifact_type),
                title=title,
                content=content,
                url=url,
                tags=tags,
            )
            try:
                service.create_artifact(payload)
                created += 1
            except DomainError:
                # Data ja ocupada ou fora da janela permitida: segue adiante.
                skipped += 1

    print(f"Artefatos criados: {created}")
    print(f"Ignorados (data ja ocupada): {skipped}")


if __name__ == "__main__":
    main()
