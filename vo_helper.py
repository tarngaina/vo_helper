import os, sys, zipfile, json, subprocess, threading, shutil, urllib.request, traceback
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.font as font
from tkinter.constants import *

class FONT:
    NAME = 'Courier New'
    SIZE = 10

class COLOR:
    BG1 = '#ffffff'
    BG2 = '#f0f0f0'
    NOR1 = '#704FC2'
    NOR2 = '#0141FF'
    NOR3 = '#FF4D00'
    NOR4 = '#FF0077'
    WAR = '#FF4D00'
    ERR = '#FA0079'
    SUC = '#00B87A'

class SETTINGS:
    def default():
        FONT.NAME = 'Courier New'
        FONT.SIZE = 10
        COLOR.BG1 = '#ffffff'
        COLOR.BG2 = '#f0f0f0'
        COLOR.NOR1 = '#704FC2'
        COLOR.NOR2 = '#0141FF'
        COLOR.NOR3 = '#FF4D00'
        COLOR.NOR4 = '#FF0077'
        COLOR.WAR = '#FF4D00'
        COLOR.ERR = '#FA0079'
        COLOR.SUC = '#00B87A'

    def change(key, value):
        if key == 'FONT':
            FONT.NAME = value
        elif key == 'SIZE':
            FONT.SIZE = int(value)
        elif key == 'BG1':
            COLOR.BG1 = value
        elif key == 'BG2':
            COLOR.BG2 = value
        elif key == 'NOR1':
            COLOR.NOR1 = value
        elif key == 'NOR2':
            COLOR.NOR2 = value
        elif key == 'NOR3':
            COLOR.NOR3 = value
        elif key == 'NOR4':
            COLOR.NOR4 = value
        elif key == 'WAR':
            COLOR.WAR = value
        elif key == 'ERR':
            COLOR.ERR = value
        elif key == 'SUC':
            COLOR.SUC = value
    
class SELECTION:
    def __init__(self, path):
        self.path = path

    def is_fantome(self):
        if type(self) is FANTOME:
            return True
        return False

    def is_vo_wad(self):
        if type(self) is VOWAD:
            return True
        return False

class VORAW(SELECTION):
    def __init__(self, path):
        super().__init__(path)

    def _r(self, path):
        dirs = []
        for d in os.listdir(path):
            if os.path.isdir(os.path.join(path, d)):
                dirs.append(d)
                
        if len(dirs) == 0:
            for f in os.listdir(path):
                temp = os.path.join(path, f)
                self.infos.append('.\\assets' + '\\'.join(temp.replace('/', '\\').split('assets')[1:]))
        else:
            for d in dirs:
                self._r(os.path.join(path, d))

    def read(self, log):
        self.infos = None
        log.config(fg = COLOR.NOR1, text = f'Reading: {os.path.basename(self.path)}...')
        if os.path.exists(os.path.join(self.path, 'assets')):
            self.infos = []
            self._r(self.path)
            log.config(fg = COLOR.SUC, text = f'Loaded: {os.path.basename(self.path)}')
            return True
        else:
            log.config(fg = COLOR.ERR, text = 'Error: No child folder named "asset" found.')
            return False

    def get_infos(self):
        if self.infos == None:
            return ''
        
        return '\n'.join(self.infos)

class VOWAD(SELECTION):
    def __init__(self, path):
        super().__init__(path)
        self.name = os.path.basename(path)

class FANTOME(SELECTION):
    def __init__(self, path):
        super().__init__(path)

    def read(self, log):
        self.infos = None
        self.lang = None
        self.vo_wad = None
        self.wads = []
        log.config(fg = COLOR.NOR1, text = f'Reading: {os.path.basename(self.path)}...')
        try: 
            with zipfile.ZipFile(self.path, 'r') as z:
                self.infos = json.loads(z.read('META/info.json'))
                for p in z.namelist():
                    if p.startswith('WAD') and p.endswith('.wad.client'):
                        self.wads.append(p)
                        for item in p.split('.'):
                            if '_' in item:
                                self.lang = item
                                self.vo_wad = p.replace('WAD/', '')
                                log.config(fg = COLOR.SUC, text = f'Loaded: {os.path.basename(self.path)}')
                                return True

            log.config(fg = COLOR.WAR, text = 'Warning: No VO WAD found in this fantome.')
            return True
        except:
            
            log.config(fg = COLOR.ERR, text = f'Error: {os.path.basename(self.path)} is broken or not a fantome file.')
            return False

    def get_infos(self):
        if self.infos == None:
            return ''
        
        wads = "\n".join(self.wads)
        return (
            f'Name: {self.infos["Name"]}'
            f'\nAuthor: {self.infos["Author"]}'
            f'\nVersion: {self.infos["Version"]}'
            f'\nDescription: {self.infos["Description"]}'
            f'\nVO Language: {self.lang}'
            f'\nWADs: \n{wads}'
            )

    

class PATH:
    APP = os.path.dirname(sys.argv[0])
    CACHE = os.path.join(APP, '_cache')
    LAST = APP

class APP:
    regions = ['cs_cz', 'de_de', 'el_gr', 'en_us', 'es_es', 'es_mx', 'fr_fr', 'hu_hu', 'it_it', 'ja_jp', 'ko_kr', 'pl_pl', 'pt_br', 'ro_ro', 'ru_ru', 'th_th', 'tr_tr', 'vn_vn', 'zh_cn', 'zh_tw']
    selected = None

    def load_settings():
        try:
            with open(os.path.join(PATH.APP, 'data', 'gui.ini')) as f:
                lines = f.readlines()
                for line in lines:
                    if '=' in line:
                        line = line.split('\n')[0]
                        key, color = line.split('=')
                        SETTINGS.change(key, color)
        except:
            SETTINGS.default()
            
    def sync_hashes(log):
        log.config(fg = COLOR.NOR1, text = 'Syncing: hashes.game.txt...')
        log.update()
        try:
            onl = urllib.request.urlopen(
                'https://raw.githubusercontent.com/CommunityDragon/CDTB/master/cdragontoolbox/hashes.game.txt',
                timeout = 30
            )
        except:
            log.config(fg = COLOR.WAR, text = 'Warning: Couldn\'t sync hashes.game.txt...')
            log.update()
            return
            
        flag = False
        online_size = int(onl.info()['Content-Length'])
        if os.path.exists(os.path.join(PATH.APP, 'data', 'hashes.game.txt')):
            offline_size = int(os.path.getsize(os.path.join(PATH.APP, 'data', 'hashes.game.txt')))
            if online_size != offline_size:
                flag = True
        else:
            flag = True
                    
        if flag:
            with open(os.path.join(PATH.APP, 'data', 'hashes.game.txt'), 'wb+') as off:
                off.write(onl.read())

        log.config(fg = COLOR.SUC, text = 'Synced: hashes.game.txt...')
        log.update()

    def load_regions(log):
        log.config(fg = COLOR.NOR1, text = 'Reading: regions.ini...')
        log.update()
        try:
            with open(os.path.join(PATH.APP, 'data', 'regions.ini'), 'r') as f:
                APP.regions = f.read().split('\n')
                log.config(fg = COLOR.SUC, text = 'Loaded: regions.ini')
                log.update()
        except:
            log.config(fg = COLOR.WAR, text = 'Warning: Couldn\'t read regions.ini, switched to default regions.')        
            log.update()
            
    def remove_cache():
        if os.path.exists(PATH.CACHE):
            shutil.rmtree(PATH.CACHE)
            
    def raw_to_wads(vo_raw, name, destination, log):
        if not os.path.exists(os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo')):
            log.config(fg = COLOR.ERR, text = 'Error: Path not found: "assets\\sounds\\wwise2016\\vo"')
            return
        
        child = os.listdir(os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo'))[0]
        original = child
        for r in APP.regions:

            old = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)
                    
            out_wad = os.path.join(destination, f'{name}.{r}.wad.client')
            log.config(fg = COLOR.NOR1, text = f'Packing: {os.path.basename(out_wad)}...')
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), vo_raw.path, out_wad], creationflags = 0x08000000)            
            log.config(fg = COLOR.SUC, text = f'Packed: {os.path.basename(out_wad)}')

            child = r

        old = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', child)
        new = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', original)
        os.rename(old, new)
        
        log.config(fg = COLOR.SUC, text = f'All WADs created at: {destination}')

    def raw_to_fantomes(vo_raw, name, infos, ohter_wads, image, destination, log):
        APP.remove_cache()

        if not os.path.exists(os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo')):
            log.config(fg = COLOR.ERR, text = 'Error: Path not found: "assets\\sounds\\wwise2016\\vo"')
            return
        
        child = os.listdir(os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo'))[0]

        original = child
        for r in APP.regions:
            old = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)

             
            packed = os.path.join(PATH.CACHE, 'packed')
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), vo_raw.path, packed], creationflags = 0x08000000)            
           
            out_fantome = os.path.join(destination, f'({r}) {infos["Name"]} V{infos["Version"]} by {infos["Author"]}.fantome')
            log.config(fg = COLOR.NOR1, text = f'Writing: {os.path.basename(out_fantome)}')
            with open(os.path.join(PATH.CACHE, 'info.json'), 'w+', encoding = 'utf-8') as f:
                json.dump(infos, f)
            with zipfile.ZipFile(out_fantome, 'w') as z:
                z.write(os.path.join(PATH.CACHE, 'info.json'), 'META\\info.json')
                if image:
                    z.write(image, 'META\\image.png')
                if ohter_wads:
                    for f in ohter_wads:
                        z.write(f, os.path.join('WAD', os.path.basename(f)))
                z.write(packed, f'WAD\\{name}.{r}.wad.client')
            os.remove(packed)
            log.config(fg = COLOR.SUC, text = f'Created: {os.path.basename(out_fantome)}')
 
            child = r

        old = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', child)
        new = os.path.join(vo_raw.path, 'assets\\sounds\\wwise2016\\vo', original)
        os.rename(old, new)

        APP.remove_cache()  
        
        log.config(fg = COLOR.SUC, text = f'All Fantomes created at: {destination}')

    def wad_to_wads(vo_wad, name, destination, log):
        APP.remove_cache()  

        unpacked = os.path.join(PATH.CACHE, '_unpacked')

        log.config(fg = COLOR.NOR1, text = f'Unpacking: {vo_wad.name}...')
        subprocess.call([os.path.join(PATH.APP, 'data', 'wad-extract.exe'), vo_wad.path, unpacked], creationflags = 0x08000000)
        log.config(fg = COLOR.SUC, text = f'Unpacked: {vo_wad.name}')
        
        if not os.path.exists(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo')):
            log.config(fg = COLOR.ERR, text = 'Error: Path not found: "assets\\sounds\\wwise2016\\vo"')
            return
        
        child = os.listdir(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo'))[0]
        for r in APP.regions:

            old = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)
                    
            out_wad = os.path.join(destination, f'{name}.{r}.wad.client')
            log.config(fg = COLOR.NOR1, text = f'Packing: {os.path.basename(out_wad)}...')
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), unpacked, out_wad], creationflags = 0x08000000)            
            log.config(fg = COLOR.SUC, text = f'Packed: {os.path.basename(out_wad)}')

            child = r

        APP.remove_cache()
            
        log.config(fg = COLOR.SUC, text = f'All WADs created at: {destination}')

    def wad_to_fantomes(vo_wad, name, infos, ohter_wads, image, destination, log):
        APP.remove_cache()

        unpacked = os.path.join(PATH.CACHE, '_unpacked')

        log.config(fg = COLOR.NOR1, text = f'Unpacking: {vo_wad.name}...')
        subprocess.call([os.path.join(PATH.APP, 'data', 'wad-extract.exe'), vo_wad.path, unpacked], creationflags = 0x08000000)
        log.config(fg = COLOR.SUC, text = f'Unpacked: {vo_wad.name}')
        
        if not os.path.exists(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo')):
            log.config(fg = COLOR.ERR, text = 'Error: Path not found: "assets\\sounds\\wwise2016\\vo"')
            return
        
        child = os.listdir(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo'))[0]

        for r in APP.regions:
            old = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)

            packed = os.path.join(PATH.CACHE, 'packed')
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), unpacked, packed], creationflags = 0x08000000)            
           
            out_fantome = os.path.join(destination, f'({r}) {infos["Name"]} V{infos["Version"]} by {infos["Author"]}.fantome')
            log.config(fg = COLOR.NOR1, text = f'Writing: {os.path.basename(out_fantome)}')
            with open(os.path.join(PATH.CACHE, 'info.json'), 'w+', encoding = 'utf-8') as f:
                json.dump(infos, f)
            with zipfile.ZipFile(out_fantome, 'w') as z:
                z.write(os.path.join(PATH.CACHE, 'info.json'), 'META\\info.json')
                if image:
                    z.write(image, 'META\\image.png')
                if ohter_wads:
                    for f in ohter_wads:
                        z.write(f, os.path.join('WAD', os.path.basename(f)))
                z.write(packed, f'WAD\\{name}.{r}.wad.client')

            os.remove(packed)
            log.config(fg = COLOR.SUC, text = f'Created: {os.path.basename(out_fantome)}')
            
            child = r

        APP.remove_cache()  
        
        log.config(fg = COLOR.SUC, text = f'All Fantomes created at: {destination}')

    def fantome_to_wads(fantome, destination, log):
        APP.remove_cache()  
            
        log.config(fg = COLOR.NOR1, text = f'Extracting: {os.path.basename(fantome.path)}...')
        try:
            with zipfile.ZipFile(fantome.path, 'r') as z:
                z.extractall(PATH.CACHE)
                
            log.config(fg = COLOR.SUC, text = f'Extracted: {os.path.basename(fantome.path)}')
        except:
            log.config(fg = COLOR.ERR, text = f'Error: Couldn\'t extract {os.path.basename(fantome.path)}')
            return 

        if fantome.lang == None or fantome.vo_wad == None:
            log.config(fg = COLOR.ERR, text = 'Error: No VO WAD found in this fantome.')
            return 

        unpacked = os.path.join(PATH.CACHE, 'WAD', '_unpacked')
        
        log.config(fg = COLOR.NOR1, text = f'Unpacking: {fantome.vo_wad}...')
        vo_wad = os.path.join(PATH.CACHE, 'WAD', fantome.vo_wad)
        subprocess.call([os.path.join(PATH.APP, 'data', 'wad-extract.exe'), vo_wad, unpacked], creationflags = 0x08000000)
        os.remove(vo_wad)
        log.config(fg = COLOR.SUC, text = f'Unpacked: {fantome.vo_wad}')
        
        child = os.listdir(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo'))[0]
        for r in APP.regions:

            old = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)
                    
            out_wad = os.path.join(destination, f'{fantome.vo_wad.split(".")[0]}.{r}.wad.client')
            log.config(fg = COLOR.NOR1, text = f'Packing: {os.path.basename(out_wad)}...')
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), unpacked, out_wad], creationflags = 0x08000000)            
            log.config(fg = COLOR.SUC, text = f'Packed: {os.path.basename(out_wad)}')

            child = r

        APP.remove_cache()
        
        log.config(fg = COLOR.SUC, text = f'All WADs created at: {destination}')

    def fantome_to_fantomes(fantome, destination, log):
        APP.remove_cache()  
            
        log.config(fg = COLOR.NOR1, text = f'Extracting: {os.path.basename(fantome.path)}...')
        try:
            with zipfile.ZipFile(fantome.path, 'r') as z:
                z.extractall(PATH.CACHE)
                
            log.config(fg = COLOR.SUC, text = f'Extracted: {os.path.basename(fantome.path)}')
        except:
            log.config(fg = COLOR.ERR, text = f'Error: Couldn\'t extract {os.path.basename(fantome.path)}')
            return 

        if fantome.lang == None or fantome.vo_wad == None:
            log.config(fg = COLOR.ERR, text = 'Error: No VO WAD found in this fantome.')
            return 

        unpacked = os.path.join(PATH.CACHE, 'WAD', '_unpacked')
        packed = os.path.join(PATH.CACHE, 'WAD', '_packed')
        
        log.config(fg = COLOR.NOR1, text = f'Unpacking: {fantome.vo_wad}...')
        vo_wad = os.path.join(PATH.CACHE, 'WAD', fantome.vo_wad)
        subprocess.call([os.path.join(PATH.APP, 'data', 'wad-extract.exe'), vo_wad, unpacked], creationflags = 0x08000000)
        os.remove(vo_wad)
        log.config(fg = COLOR.SUC, text = f'Unpacked: {fantome.vo_wad}')
        
        child = os.listdir(os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo'))[0]
        for r in APP.regions:
            old = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', child)
            new = os.path.join(unpacked, 'assets\\sounds\\wwise2016\\vo', r)
            os.rename(old, new)
                    
            subprocess.call([os.path.join(PATH.APP, 'data', 'wad-make.exe'), unpacked, packed], creationflags = 0x08000000)
            
            out_fantome = os.path.join(destination, f'({r}) {fantome.infos["Name"]} V{fantome.infos["Version"]} by {fantome.infos["Author"]}.fantome')
            log.config(fg = COLOR.NOR1, text = f'Writing: {os.path.basename(out_fantome)}...')
            with zipfile.ZipFile(out_fantome, 'w') as z:
                z.write(os.path.join(PATH.CACHE, 'META\\info.json'), 'META\\info.json')
                if os.path.exists(os.path.join(PATH.CACHE, 'META\\image.png')):
                    z.write(os.path.join(PATH.CACHE, 'META\\image.png'), 'META\\image.png')
                for f in os.listdir(os.path.join(PATH.CACHE, 'WAD')):
                    if os.path.isfile(os.path.join(PATH.CACHE, 'WAD', f)) and f.endswith('.wad.client') and (not f.startswith('_cache')):
                        z.write(os.path.join(PATH.CACHE, 'WAD', f), os.path.join('WAD', f))
                z.write(packed, f'WAD\\{fantome.vo_wad.split(".")[0]}.{r}.wad.client')

            os.remove(packed)
            log.config(fg = COLOR.SUC, text = f'Created: {os.path.basename(out_fantome)}')

            child = r

        APP.remove_cache()  
            
        log.config(fg = COLOR.SUC, text = f'All Fantomes created at: {destination}')

class GUI(threading.Thread):
    def set_title(self, s):
        self.root.title(s)

    def set_size(self, w, h):
        self.root.geometry(f'{w}x{h}')
        self.root.resizable(False, False)

    def set_icon(self, path):
        self.root.iconphoto(True, tk.PhotoImage(file = path))

    def create_main_font(self):
        self.mainfont = font.Font(family = FONT.NAME, size = FONT.SIZE)

    def create_frames(self):
        self.mainframe = tk.Frame(
            master = self.root,
            bg = COLOR.BG1
            )
        self.mainframe.pack(fill = BOTH, expand = True)
        self.topframe = tk.Frame(
            master = self.mainframe,
            bg = COLOR.BG1
            )
        self.topframe.pack(side = TOP,  fill = X)
        self.midframe = tk.Frame(
            master = self.mainframe,
            bg = COLOR.BG1
            )
        self.midframe.pack(fill = X)
        self.botframe = tk.Frame(
            master = self.mainframe,
            bg = COLOR.BG1
        )
        self.botframe.pack(fill = X)
        self.buttonframe = tk.Frame(
            master = self.botframe,
            bg = COLOR.BG1
        )
        self.buttonframe.pack(side = TOP)
        self.buttonbotframeleft = tk.Frame(
            master = self.buttonframe,
            bg = COLOR.BG1
        )
        self.buttonbotframeleft.pack(side = LEFT)
        self.buttonbotframeright = tk.Frame(
            master = self.buttonframe,
            bg = COLOR.BG1
        )
        self.buttonbotframeright.pack(side = RIGHT)
        self.logframe = tk.Frame(
            master = self.botframe,
            bg = COLOR.BG1
        )
        self.logframe.pack(side =  BOTTOM, fill = X)

    def create_path_label(self):
        self.pathlabel = tk.Label(
            master = self.topframe,
            text = '...',
            width = 100,
            font = self.mainfont,
            anchor = W,
            fg = COLOR.NOR4,
            bg = COLOR.BG2
            )
        self.pathlabel.pack(side = TOP, padx = 10, pady = 10)

    def browse_vo_raw_button_thread(self):
        dirname = filedialog.askdirectory(
            initialdir = PATH.LAST,
            title = 'Select a VO folder',
        )

        if dirname == '':
            APP.selected = None
            self.pathlabel.config(text = '...')
            self.update_info_text(text = '')
            self.log.config(text = '')
            self.makevowadsbutton.config(state = DISABLED)
            self.makefantomesbutton.config(state = DISABLED)
        else:
            dirname = dirname.replace('/', '\\')
            PATH.LAST = os.path.dirname(dirname)
            APP.selected = VORAW(dirname)
            if not APP.selected.read(self.log):
                self.pathlabel.config(text = dirname)
                self.update_info_text(text = '')
                self.makevowadsbutton.config(state = DISABLED)
                self.makefantomesbutton.config(state = DISABLED)
            else:
                self.pathlabel.config(text = dirname)
                if (self.mainfont.measure(dirname)) > self.pathlabel.winfo_width():
                    self.pathlabel.config(anchor = E)
                else:
                    self.pathlabel.config(anchor = W)
                self.update_info_text(text = APP.selected.get_infos())
                self.makevowadsbutton.config(state = NORMAL)
                self.makefantomesbutton.config(state = NORMAL)


    def browse_vo_raw_button_command(self):
        t = threading.Thread(
            target = self.browse_vo_raw_button_thread,
            args = ()
            )
        t.start()
        
    def create_browse_vo_raw_button(self):
        self.browse_vo_raw_button = tk.Button(
            master = self.topframe,
            text = 'Select VO RAW',
            font = self.mainfont,
            width = 16,
            command = self.browse_vo_raw_button_command,
            fg = COLOR.NOR2,
            bg = COLOR.BG2
            )
        self.browse_vo_raw_button.pack(side = RIGHT, anchor = E, padx = 10)

    def browse_vo_wad_button_thread(self):
        filename = filedialog.askopenfilename(
            initialdir = PATH.LAST,
            title = 'Select a WAD file',
            filetypes = [('WAD file','*.wad.client')]
        )

        if filename == '':
            APP.selected = None
            self.pathlabel.config(text = '...', anchor = W)
            self.update_info_text(text = '')
            self.log.config(text = '')
            self.makevowadsbutton.config(state = DISABLED)
            self.makefantomesbutton.config(state = DISABLED)
        else:
            filename = filename.replace('/', '\\')
            PATH.LAST = os.path.dirname(filename)
            APP.selected = VOWAD(filename)
            self.log.config(text = f'Selected: {os.path.basename(filename)}')
            self.pathlabel.config(text = filename)
            if (self.mainfont.measure(filename)) > self.pathlabel.winfo_width():
                self.pathlabel.config(anchor = E)
            else:
                self.pathlabel.config(anchor = W)
            self.update_info_text(text = '')
            self.makevowadsbutton.config(state = NORMAL)
            self.makefantomesbutton.config(state = NORMAL)

    def browse_vo_wad_button_command(self):
        t = threading.Thread(
            target = self.browse_vo_wad_button_thread,
            args = ()
            )
        t.start()
        
    def create_browse_vo_wad_button(self):
        self.browse_vo_wad_button = tk.Button(
            master = self.topframe,
            text = 'Select VO WAD',
            font = self.mainfont,
            width = 16,
            command = self.browse_vo_wad_button_command,
            fg = COLOR.NOR2,
            bg = COLOR.BG2
            )
        self.browse_vo_wad_button.pack(side = RIGHT, anchor = E)

    def browse_fantome_button_thread(self):
        filename = filedialog.askopenfilename(
            initialdir = PATH.LAST,
            title = 'Select a Fantome file',
            filetypes = [('Fantome file','*.fantome')]
        )

        if filename == '':
            APP.selected = None
            self.pathlabel.config(text = '...', anchor = W)
            self.update_info_text(text = '')
            self.log.config(text = '')
            self.makevowadsbutton.config(state = DISABLED)
            self.makefantomesbutton.config(state = DISABLED)
        else:
            filename = filename.replace('/', '\\')
            PATH.LAST = os.path.dirname(filename)
            APP.selected = FANTOME(filename)
            if not APP.selected.read(self.log):
                self.update_info_text(text = '')
                self.makevowadsbutton.config(state = DISABLED)
                self.makefantomesbutton.config(state = DISABLED)
            else:
                self.pathlabel.config(text = filename)
                if (self.mainfont.measure(filename)) > self.pathlabel.winfo_width():
                    self.pathlabel.config(anchor = E)
                else:
                    self.pathlabel.config(anchor = W)
                self.update_info_text(text = APP.selected.get_infos())
                self.makevowadsbutton.config(state = NORMAL)
                self.makefantomesbutton.config(state = NORMAL)

    def browse_fantome_button_command(self):
        t = threading.Thread(
            target = self.browse_fantome_button_thread,
            args = ()
            )
        t.start()
        
    def create_browse_fantome_button(self):
        self.browse_fantome_button = tk.Button(
            master = self.topframe,
            text = 'Select Fantome',
            font = self.mainfont,
            width = 16,
            command = self.browse_fantome_button_command,
            fg = COLOR.NOR2,
            bg = COLOR.BG2
            )
        self.browse_fantome_button.pack(side = RIGHT, anchor = E, padx = 10)

    def create_info_text(self):
        self.infotext = tk.Text(
            master = self.midframe,
            height = 5,
            font = self.mainfont,
            bg = COLOR.BG1,
            state = DISABLED,
            relief = FLAT,
            fg = COLOR.NOR3,
            width = 100
            )
        self.infotext.pack(side = LEFT, anchor = E, padx = 10, pady = 10)
        self.infotextscrollbar = tk.Scrollbar(
            master = self.midframe,
            orient = VERTICAL,
            command = self.infotext.yview,
            width = 0
        )
        self.infotext['yscrollcommand'] = self.infotextscrollbar.set
        self.infotextscrollbar.pack()

    def update_info_text(self, text):
        self.infotext.config(state = NORMAL)
        self.infotext.delete('1.0', END)
        self.infotext.insert('1.0', text)
        self.infotext.config(state = DISABLED)

    def make_fantomes_button_thread(self):
        if self.window != None:
            self.window.destroy()
        self.window = None
        if APP.selected == None:
            return
        if APP.selected.is_fantome():
            destination = filedialog.askdirectory(
                initialdir = PATH.LAST,
                title = 'Select output folder'
                )
            if destination != '':
                PATH.LAST = os.path.dirname(destination)
                APP.fantome_to_fantomes(APP.selected, destination.replace('/', '\\'), self.log)
        elif APP.selected.is_vo_wad():
            def update_window_info_text():
                if self.window != None:
                    temp_info = ''
                    name = self.window.nameentry.get()
                    author = self.window.authorentry.get()
                    ver = self.window.verentry.get()
                    desc = self.window.descentry.get()
                    if name != '' or author != '' or ver != '' or desc != '':
                        if name != '':
                            temp_info += name
                        if ver != '':
                            temp_info += f' V{ver}'
                        if author != '':
                            temp_info += f' by {author}'
                        if temp_info != '':
                            temp_info = f'(lang) {temp_info}.fantome:\n'
                        temp_info += 'META\\info.json\n'
                    if self.window.image:
                        temp_info += 'META\\image.png\n'
                    wadname = self.window.wadnameentry.get()
                    if wadname != '':
                        temp_info += f'WAD\\{wadname}.(lang).wad.client\n'
                    if self.window.other_wads:
                        temp_other_wads = list(self.window.other_wads)
                        for i in range(0, len(temp_other_wads)):
                            temp_other_wads[i] = 'WAD\\' + os.path.basename(temp_other_wads[i])
                        temp_info += '\n'.join(temp_other_wads)
                    
                    self.window.infotext.config(state = NORMAL)
                    self.window.infotext.delete('1.0', END)
                    self.window.infotext.insert(END, temp_info)
                    self.window.infotext.config(state = DISABLED)
            
            def select_other_wads_command():
                filenames = filedialog.askopenfilenames(
                    title = 'Select all extra WADS that will be included',
                    filetypes = [('WAD file','*.wad.client')]    
                )
                self.window.other_wads = filenames
                update_window_info_text()
                self.window.focus()
            
            def select_image_command():
                filename = filedialog.askopenfilename(
                    title = 'Select a PNG file',
                    filetypes = [('PNG file','*.png')]    
                )
                self.window.image = filename
                update_window_info_text()
                self.window.focus()

                
            def confirm_thread():
                name = self.window.nameentry.get()
                author = self.window.authorentry.get()
                ver = self.window.verentry.get()
                desc = self.window.descentry.get()
                wadname = self.window.wadnameentry.get()
                other_wads = self.window.other_wads if self.window.other_wads != '' else None
                image = self.window.image if self.window.image != '' else None
                if wadname == '' or name == '' or author == '' or ver == '':
                    if wadname == '':
                        self.log.config(text = 'Error: You must type in name of VO WAD.')
                    else:
                        self.log.config(text = 'Error: You must type name, author, version.')
                else:
                    destination = filedialog.askdirectory(
                        title = 'Select output location'
                    )
                    if destination != '':
                        PATH.LAST = os.path.dirname(destination)
                        if destination.startswith(APP.selected.path):
                            self.log.config(text = 'Error: Output path must be different from input path.')
                        else:
                            self.window.destroy()
                            APP.wad_to_fantomes(
                                APP.selected,
                                wadname,
                                { 'Name': name, 'Author': author, 'Version': ver, 'Description': desc },
                                other_wads, image,
                                destination.replace('/', '\\'),
                                self.log
                            )

            def confirm_command():
                t = threading.Thread(
                    target = confirm_thread,
                    args = ()
                )
                t.start()

            def update_window():
                if self.window != None:
                    update_window_info_text()
                    self.window.update()
                    self.window.after(1000, update_window)

            self.window = tk.Toplevel(
                master = self.root
            )
            self.window.title('Enter Fantomes infos')
            self.window.maxsize(600, 380)
            self.window.resizable(False, False)
            self.window.other_wads = None
            self.window.image = None

            self.window.mainframe = tk.Frame(
                master = self.window,
                bg = COLOR.BG1
            )
            self.window.mainframe.pack(expand = True, fill = BOTH)

            self.window.topframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.topframe.pack(fill = X)
            self.window.askforwadnamelabel = tk.Label(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Enter the name of VO WAD that will be included: ',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforwadnamelabel.pack(anchor = W, pady = 5, padx = 10)

            self.window.wadnameentry = tk.Entry(
                master = self.window.topframe,
                width = 100,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.wadnameentry.pack(padx = 15)
            
            self.window.selectotherwadsbutton = tk.Button(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Add Extra WADs',
                command = select_other_wads_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectotherwadsbutton.pack(anchor = E, padx = 10, pady = 10)

            self.window.askforfantomeinfoslabel = tk.Label(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Enter the infos of Fantomes that will be created:',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforfantomeinfoslabel.pack(anchor = W, padx = 10)

            self.window.infoframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.infoframe.pack(fill = X, expand = True)
            
            self.window.namelabel = tk.Label(
                master = self.window.infoframe,
                text = 'Name: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.namelabel.grid(sticky = W, row = 0, column = 0, padx = 10, pady = 5)
            self.window.nameentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.nameentry.grid(sticky = W,row = 0, column = 1, padx = 10, pady = 5)
            
            self.window.authorlabel = tk.Label(
                master = self.window.infoframe,
                text = 'Author: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.authorlabel.grid(sticky = W, row = 1, column = 0, padx = 10, pady = 5)
            self.window.authorentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.authorentry.grid(sticky = W, row = 1, column = 1, padx = 10, pady = 5)

            self.window.verlabel = tk.Label(
                master = self.window.infoframe,
                text = 'Version: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.verlabel.grid(sticky = W, row = 2, column = 0, padx = 10, pady = 5)
            self.window.verentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.verentry.grid(sticky = W, row = 2, column = 1, padx = 10, pady = 5)

            self.window.desclabel = tk.Label(
                master = self.window.infoframe,
                text = 'Description: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.desclabel.grid(sticky = W, row = 3, column = 0, padx = 10, pady = 5)
            self.window.descentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.descentry.grid(sticky = W, row = 3, column = 1, padx = 10, pady = 5)

            
            self.window.botframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.botframe.pack(fill = X)

            self.window.botframeleft = tk.Frame(
                master = self.window.botframe,
                bg = COLOR.BG1
            )
            self.window.botframeleft.pack(side = LEFT, fill = BOTH)

            self.window.infotext = tk.Text(
                master = self.window.botframeleft,
                bg = COLOR.BG1,
                height = 6,
                width = 55,
                font = self.mainfont,
                relief = FLAT,
                state = DISABLED,
                fg = COLOR.NOR3
            )
            self.window.infotext.pack(side = LEFT, anchor = NW, padx = 10, pady = 10)
            self.window.infotextscroll = tk.Scrollbar(
                master = self.window.mainframe,
                orient = VERTICAL,
                command = self.window.infotext.yview,
                width = 0
            )
            self.window.infotext['yscrollcommand'] = self.window.infotextscroll.set
            self.window.infotextscroll.pack(side = RIGHT)
            
            self.window.botframeright = tk.Frame(
                master = self.window.botframe,
                bg = COLOR.BG1
            )
            self.window.botframeright.pack(side = RIGHT, fill = BOTH)
            
            self.window.selectimagebutton = tk.Button(
                master = self.window.botframeright,
                font = self.mainfont,
                text = 'Add Image',
                command = select_image_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectimagebutton.pack(anchor = E, padx = 10, pady = 5)

            self.window.selectoutputbutton = tk.Button(
                master = self.window.botframeright,
                font = self.mainfont,
                text = 'Select Output',
                command = confirm_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectoutputbutton.pack(anchor = E, padx = 10, pady = 10)
            self.window.t = threading.Thread(
                target = update_window,
                args = (),
            )
            self.window.t.start()
        else:
            def update_window_info_text():
                if self.window != None:
                    temp_info = ''
                    name = self.window.nameentry.get()
                    author = self.window.authorentry.get()
                    ver = self.window.verentry.get()
                    desc = self.window.descentry.get()
                    if name != '' or author != '' or ver != '' or desc != '':
                        if name != '':
                            temp_info += name
                        if ver != '':
                            temp_info += f' V{ver}'
                        if author != '':
                            temp_info += f' by {author}'
                        if temp_info != '':
                            temp_info = f'(lang) {temp_info}.fantome:\n'
                        temp_info += 'META\\info.json\n'
                    if self.window.image:
                        temp_info += 'META\\image.png\n'
                    wadname = self.window.wadnameentry.get()
                    if wadname != '':
                        temp_info += f'WAD\\{wadname}.(lang).wad.client\n'
                    if self.window.other_wads:
                        temp_other_wads = list(self.window.other_wads)
                        for i in range(0, len(temp_other_wads)):
                            temp_other_wads[i] = 'WAD\\' + os.path.basename(temp_other_wads[i])
                        temp_info += '\n'.join(temp_other_wads)
                    
                    self.window.infotext.config(state = NORMAL)
                    self.window.infotext.delete('1.0', END)
                    self.window.infotext.insert(END, temp_info)
                    self.window.infotext.config(state = DISABLED)
            
            def select_other_wads_command():
                filenames = filedialog.askopenfilenames(
                    title = 'Select all extra WADS that will be included',
                    filetypes = [('WAD file','*.wad.client')]    
                )
                self.window.other_wads = filenames
                update_window_info_text()
                self.window.focus()
            
            def select_image_command():
                filename = filedialog.askopenfilename(
                    title = 'Select a PNG file',
                    filetypes = [('PNG file','*.png')]    
                )
                self.window.image = filename
                update_window_info_text()
                self.window.focus()

                
            def confirm_thread():
                name = self.window.nameentry.get()
                author = self.window.authorentry.get()
                ver = self.window.verentry.get()
                desc = self.window.descentry.get()
                wadname = self.window.wadnameentry.get()
                other_wads = self.window.other_wads if self.window.other_wads != '' else None
                image = self.window.image if self.window.image != '' else None
                if wadname == '' or name == '' or author == '' or ver == '':
                    if wadname == '':
                        self.log.config(fg = COLOR.ERR, text = 'Error: You must type in name of VO WAD.')
                    else:
                        self.log.config(fg = COLOR.ERR, text = 'Error: You must type name, author, version.')
                else:
                    destination = filedialog.askdirectory(
                        title = 'Select output location'
                    )
                    if destination != '':
                        PATH.LAST = os.path.dirname(destination)
                        if destination.startswith(APP.selected.path):
                            self.log.config(text = 'Error: Output path must be different from input path.')
                        else:
                            self.window.destroy()
                            APP.raw_to_fantomes(
                                APP.selected,
                                wadname,
                                { 'Name': name, 'Author': author, 'Version': ver, 'Description': desc },
                                other_wads, image,
                                destination.replace('/', '\\'),
                                self.log
                            )

            def confirm_command():
                t = threading.Thread(
                    target = confirm_thread,
                    args = ()
                )
                t.start()

            def update_window():
                if self.window != None:
                    update_window_info_text()
                    self.window.update()
                    self.window.after(1000, update_window)

            self.window = tk.Toplevel(
                master = self.root
            )
            self.window.title('Enter Fantomes infos')
            self.window.maxsize(600, 380)
            self.window.resizable(False, False)
            self.window.other_wads = None
            self.window.image = None
            
            self.window.mainframe = tk.Frame(
                master = self.window,
                bg = COLOR.BG1
            )
            self.window.mainframe.pack(expand = True, fill = BOTH)

            self.window.topframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.topframe.pack(fill = X)
            self.window.askforwadnamelabel = tk.Label(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Enter the name of VO WAD that will be included: ',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforwadnamelabel.pack(anchor = W, pady = 5, padx = 10)

            self.window.wadnameentry = tk.Entry(
                master = self.window.topframe,
                width = 100,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.wadnameentry.pack(padx = 15)
            
            self.window.selectotherwadsbutton = tk.Button(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Add Extra WADs',
                command = select_other_wads_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectotherwadsbutton.pack(anchor = E, padx = 10, pady = 10)

            self.window.askforfantomeinfoslabel = tk.Label(
                master = self.window.topframe,
                font = self.mainfont,
                text = 'Enter the infos of Fantomes that will be created:',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforfantomeinfoslabel.pack(anchor = W, padx = 10)

            self.window.infoframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.infoframe.pack(fill = X, expand = True)
            
            self.window.namelabel = tk.Label(
                master = self.window.infoframe,
                text = 'Name: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.namelabel.grid(sticky = W, row = 0, column = 0, padx = 10, pady = 5)
            self.window.nameentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.nameentry.grid(sticky = W,row = 0, column = 1, padx = 10, pady = 5)
            
            self.window.authorlabel = tk.Label(
                master = self.window.infoframe,
                text = 'Author: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.authorlabel.grid(sticky = W, row = 1, column = 0, padx = 10, pady = 5)
            self.window.authorentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.authorentry.grid(sticky = W, row = 1, column = 1, padx = 10, pady = 5)

            self.window.verlabel = tk.Label(
                master = self.window.infoframe,
                text = 'Version: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.verlabel.grid(sticky = W, row = 2, column = 0, padx = 10, pady = 5)
            self.window.verentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.verentry.grid(sticky = W, row = 2, column = 1, padx = 10, pady = 5)

            self.window.desclabel = tk.Label(
                master = self.window.infoframe,
                text = 'Description: ',
                font = self.mainfont,
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.desclabel.grid(sticky = W, row = 3, column = 0, padx = 10, pady = 5)
            self.window.descentry = tk.Entry(
                master = self.window.infoframe,
                width = 55,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.descentry.grid(sticky = W, row = 3, column = 1, padx = 10, pady = 5)

            
            self.window.botframe = tk.Frame(
                master = self.window.mainframe,
                bg = COLOR.BG1
            )
            self.window.botframe.pack(side = BOTTOM, fill = X)

            self.window.botframeleft = tk.Frame(
                master = self.window.botframe,
                bg = COLOR.BG1
            )
            self.window.botframeleft.pack(side = LEFT, fill = Y)

            self.window.infotext = tk.Text(
                master = self.window.botframeleft,
                bg = COLOR.BG1,
                height = 6,
                width = 55,
                font = self.mainfont,
                relief = FLAT,
                state = DISABLED,
                fg = COLOR.NOR3
            )
            self.window.infotext.pack(side = LEFT, anchor = NW, padx = 10, pady = 10)
            self.window.infotextscroll = tk.Scrollbar(
                master = self.window.mainframe,
                orient = VERTICAL,
                command = self.window.infotext.yview,
                width = 0
            )
            self.window.infotext['yscrollcommand'] = self.window.infotextscroll.set
            self.window.infotextscroll.pack(side = RIGHT)
            
            self.window.botframeright = tk.Frame(
                master = self.window.botframe,
                bg = COLOR.BG1
            )
            self.window.botframeright.pack(side = RIGHT, fill = Y)
            
            self.window.selectimagebutton = tk.Button(
                master = self.window.botframeright,
                font = self.mainfont,
                text = 'Add Image',
                command = select_image_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectimagebutton.pack(anchor = E, padx = 10, pady = 5)

            self.window.selectoutputbutton = tk.Button(
                master = self.window.botframeright,
                font = self.mainfont,
                text = 'Select Output',
                command = confirm_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectoutputbutton.pack(anchor = E, padx = 10, pady = 10)
            self.window.t = threading.Thread(
                target = update_window,
                args = (),
            )
            self.window.t.start()
            
    def make_fantomes_button_command(self):
        t = threading.Thread(
            target = self.make_fantomes_button_thread,
            args = ()
            )
        t.start()
                            
    def create_make_fantomes_button(self):
        self.makefantomesbutton = tk.Button(
            master = self.buttonbotframeright,
            text = 'Make Fantomes',
            font = self.mainfont,
            command = self.make_fantomes_button_command,
            state = DISABLED,
            fg = COLOR.NOR2,
            bg = COLOR.BG2
        )
        self.makefantomesbutton.pack(side = LEFT, padx = 5)

    def make_vo_wads_button_thread(self):
        if self.window != None:
            self.window.destroy()
            
        if APP.selected == None:
            return
        if APP.selected.is_fantome():
            destination = filedialog.askdirectory(
                initialdir = PATH.LAST,
                title = 'Select output folder'
                )
            if destination != '':
                PATH.LAST = os.path.dirname(destination)
                APP.fantome_to_wads(APP.selected, destination.replace('/', '\\'), self.log)
        elif APP.selected.is_vo_wad():
            def confirm_thread():
                wadname = self.window.wadnameentry.get()
                if wadname == '':
                    self.log.config(text = 'Error: You must type in name of VO WADs that will be created.')
                else:
                    destination = filedialog.askdirectory(
                        initialdir = PATH.LAST,
                        title = 'Select output location'
                    )
                    if destination != '':
                        PATH.LAST = os.path.dirname(destination)
                        self.window.destroy()
                        APP.wad_to_wads(APP.selected, wadname, destination.replace('/', '\\'), self.log)

            def confirm_command():
                t = threading.Thread(
                    target = confirm_thread,
                    args = ()
                )
                t.start()

            self.window = tk.Toplevel(
                master = self.root
            )
            self.window.title('Enter WADs infos')
            self.window.maxsize(600, 235)
            self.window.resizable(False, False)
            self.window.mainframe = tk.Frame(
                master = self.window,
                bg = COLOR.BG1
            )
            self.window.mainframe.pack(fill = BOTH, expand = True)
            self.window.askforwadnamelabel = tk.Label(
                master = self.window.mainframe,
                font = self.mainfont,
                text = 'Enter the name of VO WADs that will be created:',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforwadnamelabel.pack(anchor = W, pady = 5, padx = 10)
            self.window.wadnameentry = tk.Entry(
                master = self.window.mainframe,
                width = 100,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.wadnameentry.pack(padx = 10)
                
            self.window.selectoutputbutton = tk.Button(
                master = self.window.mainframe,
                font = self.mainfont,
                text = 'Select Output',
                command = confirm_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectoutputbutton.pack(anchor = E, padx = 10, pady = 10)

        else:
            def confirm_thread():
                wadname = self.window.wadnameentry.get()
                if wadname == '':
                    self.log.config(fg = COLOR.ERR, text = 'Error: You must type in name of VO WADs that will be created.')
                else:
                    destination = filedialog.askdirectory(
                        initialdir = PATH.LAST,
                        title = 'Select output location'
                    )
                    if destination != '':
                        if destination.startswith(APP.selected.path):
                            self.log.config(fg = COLOR.ERR, text = 'Error: Output path must be different from input path.')
                        else:
                            PATH.LAST = os.path.dirname(destination)
                            self.window.destroy()
                            APP.raw_to_wads(APP.selected, wadname, destination.replace('/', '\\'), self.log)

            def confirm_command():
                t = threading.Thread(
                    target = confirm_thread,
                    args = ()
                )
                t.start()

            self.window = tk.Toplevel(
                master = self.root
            )
            self.window.title('Enter WADs infos')
            self.window.maxsize(600, 235)
            self.window.resizable(False, False)
            self.window.mainframe = tk.Frame(
                master = self.window,
                bg = COLOR.BG1
            )
            self.window.mainframe.pack(fill = BOTH, expand = True)
            self.window.askforwadnamelabel = tk.Label(
                master = self.window.mainframe,
                font = self.mainfont,
                text = 'Enter the name of VO WADs that will be created:',
                bg = COLOR.BG1,
                fg = COLOR.NOR1
            )
            self.window.askforwadnamelabel.pack(anchor = W, pady = 5, padx = 10)
            self.window.wadnameentry = tk.Entry(
                master = self.window.mainframe,
                width = 100,
                font = self.mainfont,
                bg = COLOR.BG2,
                fg = COLOR.NOR4
            )
            self.window.wadnameentry.pack(padx = 10)
                
            self.window.selectoutputbutton = tk.Button(
                master = self.window.mainframe,
                font = self.mainfont,
                text = 'Select Output',
                command = confirm_command,
                fg = COLOR.NOR2,
                bg = COLOR.BG2
            )
            self.window.selectoutputbutton.pack(anchor = E, padx = 10, pady = 10)


    def make_vo_wads_button_command(self):
        t = threading.Thread(
            target = self.make_vo_wads_button_thread,
            args = ()
            )
        t.start()
                            
    def create_make_vo_wads_button(self):
        self.makevowadsbutton = tk.Button(
            master = self.buttonbotframeleft,
            text = 'Make VO WADs',
            font = self.mainfont,
            command = self.make_vo_wads_button_command,
            state = DISABLED,
            fg = COLOR.NOR2,
            bg = COLOR.BG2
        )
        self.makevowadsbutton.pack(side = RIGHT, padx = 5)

    def create_log(self):
        self.log = tk.Label(
            master = self.logframe,
            font = self.mainfont,
            bg = COLOR.BG1,
            anchor = E
        )
        self.log.pack(pady = 5, side = LEFT)
            
    def __init__(self):
        self.window = None
        self.root = tk.Tk()
        self.set_title('bro')
        self.set_size(600, 235)
        self.set_icon(os.path.join(PATH.APP, 'data', 'icon.png'))
        APP.load_settings()
        self.create_main_font()
        self.create_frames()
        self.create_log()
        self.create_path_label()
        self.create_browse_fantome_button()
        self.create_browse_vo_wad_button()
        self.create_browse_vo_raw_button()
        self.create_info_text()
        self.create_make_vo_wads_button()
        self.create_make_fantomes_button()
        self.root.update()
        APP.sync_hashes(self.log)
        self.root.update()
        APP.load_regions(self.log)
        self.root.update()
        self.root.mainloop()
        

def main(): 
    try:
        g = GUI()
    except Exception:
        with open('error.txt', 'w+') as f:
            f.write(traceback.format_exc())
    
main()
