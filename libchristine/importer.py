import gtk, os
import time
import gtk.glade
import mutagen.mp3, mutagen.oggvorbis

class Track:
    def __init__(self, song):
        self.song = song
        self.data = open(os.path.expanduser("~/christine_songs.txt"), "a")
        
        self.title = ""
        self.artist = ""
        self.album = ""
        self.track = "" 
        self.genre = ""
        self.length = ""
        self.bitrate = ""         
        
    def write_tags(self):
        tags = {
                'title'   : self.title,
                'artist'  : self.artist,
                'album'   : self.album,
                'track'   : self.track,
                'genre'   : self.genre,
                'length'  : self.length,
                'bitrate' : self.bitrate                         
               }
        self.data.write(repr(tags) + "\n")
    
    

class MP3Track(Track):
    IDS = { "TIT2": "title",
            "TPE1": "artist",
            "TALB": "album",
            "TRCK": "track",
            "TDRC": "year",
            "TCON": "genre"
            }

    def __init__(self, *args):
        Track.__init__(self, *args)
        self.IDS = {"title":"TIT2",
                                "artist":"TPE1",
                                "album":"TALB",
                                "track-number":"TRCK",
                                "year":"TDRC",
                                "genre":"TCON"
                                }

    def get_tag(self, id3, t):
	if not self.IDS.has_key(t): return ""
        t = self.IDS[t]
        if not id3.has_key(t): return ""
        text = str(id3[t])

        # get rid of any newlines
        text = text.replace("\n", " ").replace("\r", " ")
        return text

    def read_tag(self):
        info = mutagen.mp3.MP3(self.song)
        self.length = info.info.length
        self.bitrate = info.info.bitrate
        try:
            id3 = mutagen.id3.ID3(self.song)
            self.title = self.get_tag(id3, "TIT2")
            self.artist = self.get_tag(id3, "TPE1")
            self.album = self.get_tag(id3, "TALB")
            self.genre = self.get_tag(id3, "TCON")

            try:
                # get track/disc id
                track = self.get_tag(id3, "TRCK")
                if track.find('/') > -1:
                    (self.track, self.disc_id) = track.split('/')
                    self.track = int(self.track)
                    self.disc_id = int(self.disc_id)
                else:
                    self.track = int(track)

            except ValueError:
                self.track = -1
                self.disc_id = -1

            self.year = self.get_tag(id3, "TDRC")

        except:
            pass



class OGGTrack(Track):
    def __init__(self, *args):
        Track.__init__(self, *args)

    def get_tag(self, f, tag):
        try:
            return unicode(f[tag][0])
        except:
            return ""

    def read_tag(self):
        try:
            f = mutagen.oggvorbis.OggVorbis(self.song)
        except mutagen.oggvorbis.OggVorbisHeaderError:
            return

        self.length = int(f.info.length)
        self.bitrate = int(f.info.bitrate / 1024)

        self.artist = self.get_tag(f, "artist")
        self.album = self.get_tag(f, "album")
        self.title = self.get_tag(f, "title")
        self.genre = self.get_tag(f, "genre")
        self.track = self.get_tag(f, "tracknumber")
        self.disc_id = self.get_tag(f, "tracktotal")
        self.year = self.get_tag(f, "date")  



class GUI:
    def __init__(self):
        self.wTree = gtk.glade.XML("importer.glade")
        self.wTree.signal_autoconnect(self)        
        
        self.dialogo = self.wTree.get_widget("folder")
    
    def on_open(self, w):        
        # sacamos el folder elegido
        folder = self.dialogo.get_current_folder()
        # nomas nos quedamos con los archivos que nos sirven
        gen = os.walk(folder)
        flag = True
        contenido = []
        
        while flag:
            try:
                (dirpath, dirnames, files) = gen.next()
                for fle in files:
                    contenido.append( os.path.join(dirpath, fle) )
            except:
                flag = False        
        
        
        archivos = [archivo for archivo in contenido if os.path.isfile(os.path.join(folder, archivo)) and archivo.split('.').pop().lower() in ['mp3', 'ogg']]              
        
        ## DEBUGGING INFO ###
        print "Vamos a importar %d rolas" % (len(archivos), )
        tiempo1 = time.time()        
        
        
        
        ########################
    
        for rola in archivos:
            if rola.split('.').pop().lower() == 'mp3':
                oRola = MP3Track(rola)
            elif rola.split('.').pop().lower() == 'ogg':
                oRola = OGGTrack(rola)
            
            try:            
                oRola.read_tag()
                oRola.write_tags()
            except:
                print rola

        ########################
        
        print "listo!!!"        
        print "Nos tardamos %f" % (time.time() - tiempo1, )
                
        
                
    def on_destroy(self, w):
        gtk.main_quit()
        
        
if __name__ == "__main__":
        gui = GUI()
        gtk.main()
