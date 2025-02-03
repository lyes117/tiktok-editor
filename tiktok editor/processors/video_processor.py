def _get_ffmpeg_path(self) -> str:
        """Get FFmpeg path with enhanced detection"""
        if os.name == 'nt':  # Windows
            # Liste étendue des emplacements possibles
            possible_paths = [
                # Chemin dans l'environnement virtuel
                os.path.join(os.path.dirname(sys.executable), 'tools', 'ffmpeg', 'ffmpeg.exe'),
                
                # Chemins système courants
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                r"C:\ffmpeg\bin\ffmpeg.exe",
                
                # Chemin dans le dossier du projet
                os.path.join(os.getcwd(), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.getcwd(), 'tools', 'ffmpeg', 'ffmpeg.exe'),
                
                # Chemins personnalisés
                os.path.expanduser("~/.ffmpeg/ffmpeg.exe"),
                os.path.expanduser("~/ffmpeg/ffmpeg.exe"),
            ]
            
            # Vérifier le PATH
            if which('ffmpeg') is not None:
                return which('ffmpeg')
            
            # Vérifier les chemins possibles
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            
            # Vérifier les variables d'environnement
            ffmpeg_home = os.environ.get('FFMPEG_HOME')
            if ffmpeg_home:
                ffmpeg_path = os.path.join(ffmpeg_home, 'bin', 'ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    return ffmpeg_path
            
            # Si FFmpeg n'est pas trouvé, essayer de le télécharger
            try:
                return self._download_ffmpeg()
            except Exception as e:
                self.logger.error(f"Impossible de télécharger FFmpeg: {str(e)}")
                raise Exception(
                    "FFmpeg n'est pas trouvé. Assurez-vous qu'il est installé et accessible.\n"
                    "Vous pouvez :\n"
                    "1. Installer FFmpeg via le site officiel : https://ffmpeg.org/download.html\n"
                    "2. Ajouter le chemin de FFmpeg à la variable PATH\n"
                    "3. Définir la variable d'environnement FFMPEG_HOME\n"
                    "4. Placer FFmpeg dans le dossier 'tools/ffmpeg' du projet"
                )
        
        else:  # Linux/Mac
            # Vérifier le PATH
            if which('ffmpeg') is not None:
                return which('ffmpeg')
            
            # Vérifier les emplacements courants Unix
            unix_paths = [
                '/usr/bin/ffmpeg',
                '/usr/local/bin/ffmpeg',
                '/opt/local/bin/ffmpeg',
                '/opt/homebrew/bin/ffmpeg',  # Pour macOS avec Homebrew
                os.path.expanduser('~/.local/bin/ffmpeg')
            ]
            
            for path in unix_paths:
                if os.path.exists(path):
                    return path
            
            raise Exception(
                "FFmpeg n'est pas trouvé. Installez-le avec votre gestionnaire de paquets :\n"
                "- Ubuntu/Debian : sudo apt-get install ffmpeg\n"
                "- macOS : brew install ffmpeg\n"
                "- Arch Linux : sudo pacman -S ffmpeg"
            )
    
    def _download_ffmpeg(self) -> str:
        """Download FFmpeg if not found (Windows only)"""
        if os.name != 'nt':
            raise Exception("Le téléchargement automatique n'est supporté que sous Windows")
        
        import requests
        import zipfile
        
        # Créer le dossier tools s'il n'existe pas
        tools_dir = os.path.join(os.getcwd(), 'tools')
        ffmpeg_dir = os.path.join(tools_dir, 'ffmpeg')
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        # URL de téléchargement (vous pouvez mettre à jour l'URL selon vos besoins)
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        try:
            # Télécharger FFmpeg
            self.logger.info("Téléchargement de FFmpeg...")
            response = requests.get(url, stream=True)
            zip_path = os.path.join(tools_dir, 'ffmpeg.zip')
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extraire l'archive
            self.logger.info("Extraction de FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tools_dir)
            
            # Trouver le dossier extrait
            extracted_dir = next(Path(tools_dir).glob('ffmpeg-master-*'))
            
            # Déplacer les fichiers
            bin_dir = os.path.join(extracted_dir, 'bin')
            for file in os.listdir(bin_dir):
                shutil.move(
                    os.path.join(bin_dir, file),
                    os.path.join(ffmpeg_dir, file)
                )
            
            # Nettoyer
            os.remove(zip_path)
            shutil.rmtree(extracted_dir)
            
            ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
            
            raise Exception("L'installation de FFmpeg a échoué")
            
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement de FFmpeg: {str(e)}")
