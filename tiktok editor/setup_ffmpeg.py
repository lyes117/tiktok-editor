import os
import sys
import shutil
import requests
import zipfile
from pathlib import Path
import platform

def download_ffmpeg():
    # Determine system architecture
    is_64bits = sys.maxsize > 2**32
    
    # Create tools directory in venv
    venv_path = os.path.dirname(sys.executable)
    tools_path = os.path.join(venv_path, 'tools')
    ffmpeg_path = os.path.join(tools_path, 'ffmpeg')
    
    os.makedirs(tools_path, exist_ok=True)
    os.makedirs(ffmpeg_path, exist_ok=True)
    
    # Download FFmpeg for Windows
    if platform.system() == 'Windows':
        arch = 'win64' if is_64bits else 'win32'
        url = f'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-{arch}-gpl.zip'
        
        print("Téléchargement de FFmpeg...")
        response = requests.get(url, stream=True)
        zip_path = os.path.join(tools_path, 'ffmpeg.zip')
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Extraction de FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tools_path)
        
        # Move files from extracted directory to ffmpeg directory
        extracted_dir = next(Path(tools_path).glob('ffmpeg-master-*'))
        bin_dir = os.path.join(extracted_dir, 'bin')
        
        for file in os.listdir(bin_dir):
            shutil.move(
                os.path.join(bin_dir, file),
                os.path.join(ffmpeg_path, file)
            )
        
        # Cleanup
        os.remove(zip_path)
        shutil.rmtree(extracted_dir)
        
        # Add to PATH
        if 'PATH' in os.environ:
            os.environ['PATH'] = ffmpeg_path + os.pathsep + os.environ['PATH']
        else:
            os.environ['PATH'] = ffmpeg_path
        
        # Create activation script modifications
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        deactivate_script = os.path.join(venv_path, 'Scripts', 'deactivate.bat')
        
        # Modify activate script
        with open(activate_script, 'a') as f:
            f.write(f'\nset "PATH={ffmpeg_path};%PATH%"\n')
        
        # Modify deactivate script
        with open(deactivate_script, 'a') as f:
            f.write(f'\nset "PATH=%PATH:{ffmpeg_path};=%"\n')
        
        print(f"FFmpeg installé dans: {ffmpeg_path}")
        print("FFmpeg a été ajouté au PATH de l'environnement virtuel")
        print("Redémarrez votre terminal et réactivez l'environnement virtuel pour appliquer les changements")

if __name__ == "__main__":
    download_ffmpeg()
