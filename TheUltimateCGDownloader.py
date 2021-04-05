import wget, requests, re, os
from mutagen.easyid3 import EasyID3
from bs4 import BeautifulSoup

CONF_URL = "https://www.churchofjesuschrist.org/study/general-conference/"

def main():
    #get user input
    lang = str(input("Download Language: "))
    start = int(input("Start Year: "))
    end = int(input("End Year: "))
    try:
        os.mkdir("discursos")
    except:
        print("Welcome")
#create General Conference Session Links
    for i in range((end-start)+1):
        for j in createSessionUrl(start+ i, lang):
            
            for k in scrapeTalks(j):
                print(k)
                talk = Discursos(k)
                talk.descargar()

def createSessionUrl(year, lang):
    return CONF_URL + str(year) + "/" + "04" + "?lang=" + lang, CONF_URL + str(year) + "/" + "10" + "?lang=" + lang

def scrapeTalks(url):
    
    talkLinks = []
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    for ul in soup.find_all('ul'):
        for url in soup.find_all('a'):
            output = url.get('href')
            if "study/general-conference" in output:
                if  "-session?" not in output:
                    if output.count("/") >= 5:
                       if output not in talkLinks:
                          talkLinks.append(output)
                          
    return talkLinks


class Discursos():
    def __init__(self, url):
        
        self.url = str("https://www.churchofjesuschrist.org" + str(url))
        print(self.url)
        self.html_text = requests.get(self.url).text
        self.soup = BeautifulSoup(self.html_text, 'html.parser')
        self.download_url = self.url_parser()
        self.name = self.get_name()
        self.speaker = self.get_speaker()
        self.editArtist()
        self.path = "discursos/" + self.speaker + "/" + self.name + ".mp3"


    def descargar(self):
        if self.download_url != None:
            try:
                wget.download(self.download_url, self.path)
                
            except:
                os.mkdir("Discursos/"+ self.speaker)
                wget.download(self.download_url, self.path)
            self.changeAlbum()
            
    def url_parser(self):
        try:
            for link in self.soup.find_all('a'):
                output = link.get('href')
                if "media2" in output:
                    return output
        except:
            return None
    def changeAlbum(self):
        year = self.url[self.url.find("conference/") + 11:self.url.find("conference/") + 15]
        month = self.url[self.url.find("conference/") + 16:self.url.find("conference/") + 18]
        print(month)
        if month == "04":
            tempAlb = "April " + str(year) + " General Conference"
        else:
            tempAlb = "October " + str(year) + " General Conference"
        try:
            audio = EasyID3(self.path)
            audio["title"] = self.name
            audio["album"] = tempAlb              
            audio.save()
        except:
            print("dang it")

       
    def get_name(self):
        try:
            for nombre in self.soup.find_all('h1'):
                nombre = self.remove_html_markup(nombre)
                self.track = nombre
                nombre = re.sub('[?,*,<,>,",:,|,\,/,-,.,~,%,$,#,@,&,;,â,¦]',"",nombre)
                self.name = nombre
                return nombre
                
        except:
            return "no title"
    def remove_html_markup(self, s):
        tag = False
        quote = False
        out = ""

        for c in s:
                if c == '<' and not quote:
                    tag = True
                elif c == '>' and not quote:
                    tag = False
                elif (c == '"' or c == "'") and tag:
                    quote = not quote
                elif not tag:
                    out = out + c

        return out
    def get_speaker(self):
        try:
            spkr = self.soup.find(id='author1')
            spkr = self.remove_html_markup(spkr)
            #nombre.replace(" ","_")
            spkr = re.sub(r"[^a-zA-Z0-9]","",spkr)
            return spkr
        except:
            try:
                spkr = self.soup.find(id='p1')
                spkr = self.remove_html_markup(spkr)
                #nombre.replace(" ","_")
                spkr = re.sub(r"[^a-zA-Z0-9]","",spkr)
                return spkr
            except:
                return "Unknown"
            
    def editArtist(self):
        if (self.speaker is None):
            self.speaker = "Unknown"
    #editedArtist = str(re.sub(r"[^a-zA-Z0-9]","", editedArtist))
        self.speaker = self.speaker.replace("Presented", "")
        self.speaker = self.speaker.replace("By", "")
        self.speaker = self.speaker.replace("by", "")
        self.speaker = self.speaker.replace("Elder", "")
        self.speaker = self.speaker.replace("President", "")
        self.speaker = self.speaker.replace("Bishop", "")
        self.speaker = self.speaker[0:40]
        self.speaker = self.addSpaces(self.speaker)
        
    def addSpaces(self, finalString):
        tempStr = ""
        for c in finalString:
            if c.isupper() == True and tempStr !="":
                tempStr = tempStr + " " + c
            else:
                tempStr = tempStr + c
        return tempStr

main()







