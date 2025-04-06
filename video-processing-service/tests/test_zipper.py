import os
import zipfile
from app import zipper


def test_zip_frames(tmp_path):
    # Cria um diretório temporário com alguns arquivos
    input_dir = tmp_path / "frames"
    input_dir.mkdir()
    # Cria arquivos dummy
    file1 = input_dir / "frame_0.jpg"
    file2 = input_dir / "frame_1.jpg"
    file1.write_text("conteudo do frame 0")
    file2.write_text("conteudo do frame 1")

    output_zip = tmp_path / "output.zip"

    # Chama a função para zipar os frames
    zipper.zip_frames(str(input_dir), str(output_zip))

    # Verifica se o arquivo zip foi criado
    assert os.path.exists(output_zip)

    # Abre o zip e verifica se os arquivos estão lá
    with zipfile.ZipFile(output_zip, "r") as zipf:
        names = zipf.namelist()
        assert "frame_0.jpg" in names
        assert "frame_1.jpg" in names
