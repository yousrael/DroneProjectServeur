#-*- coding: utf-8 -*-
import datetime
import time
import os
import errno
import sys
import gtk.gdk
import chilkat
import Image

class DronePicture:
    """
    Prise de Photos --> Transmission vers le Server Apache
    """
    def __init__(self, host = None , folder = None):
        try:
            print("Prendre et transmettre des photos ..")
            self.host = host
            self.folder = folder
        except Exception as x:
            print(x)

    """
        Fonction de Prise de photos
        Retourne une dictionnaire value qui contient le path, le nom et la date_heure dont la photo a été générée
        l'objet 'value' sera complété au moment de faire le post vers Apache
            value["position"]
            value["position_pts"]
    """
    def getPicture(self, NamePicture = "Drone", Intervention = 1, Extension = "jpeg"):
        try:
            value = {}
            print("Drone Project : Creating picture ...")
            w = gtk.gdk.get_default_root_window()
            sz = w.get_size()
            print ("The size of the window is %d x %d" % sz)
            pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
            pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
            if (pb != None):
                #Le temps actuel de la prise de photos
                datepicture = str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%Z"))
                racine = "./"
                suffix = str(Intervention)+"/"+str(NamePicture)+"_"+str(datepicture)+"."+str(Extension)
                filename = racine + suffix
                #Crée le fichier avec son arboresence même s'il n'existe pas
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                #Sauvegarde de la photo prise avec l'extension indiquée
                pb.save(filename, str(Extension))

                """
                Découpage de la photo de -10% des marges
                """
                im = Image.open(str(filename))
                im_size = im.size
                #print im_size
                # (1366, 768)
                cp_large = int(im_size[0] * 0.10)
                cp_haut = int(im_size[1] * 0.10)
                #print cp_large
                #print cp_haut
                left = cp_large
                top = cp_haut
                width = im_size[0] - cp_large
                height = im_size[1] - cp_haut
                # Create Box
                box = (left, top, left + width, top + height)
                # Crop Image
                area = im.crop(box)
                # Save Image
                #print area.size
                area.save(filename, str(Extension))
                value["path"] = 'http://148.60.11.238/projet/'+suffix
                value["date_heure"] = datepicture
                value["nom"] = NamePicture
                print "Screenshot saved to " + os.path.basename(filename)
                self.sendToTheServer(filename, suffix)
                #print(value)
                return value
            else:
                print "Unable to get the screenshot."
        except Exception as x:
            print(x)

    """
        Posting the generated picture to the Apache server
    """
    def sendToTheServer(self, localPath, suffix = None):
        #  Important: It is helpful to send the contents of the
        #  ssh.LastErrorText property when requesting support.
        ssh = chilkat.CkSsh()
        remotePath = "/var/www/html/projet/"
        if suffix == None:
            dstfolder = remotePath
        else:
            dstfolder = remotePath+str(suffix)

        #  Any string automatically begins a fully-functional 30-day trial.
        success = ssh.UnlockComponent("30-day trial")
        if (success != True):
            print(ssh.lastErrorText())
            sys.exit()
        # Connect to an SSH server:
        #  Hostname may be an IP address or hostname:
        hostname = "148.60.11.238"
        port = 22
        success = ssh.Connect(hostname, port)
        if (success != True):
            print(ssh.lastErrorText())
            sys.exit()
        # Wait a max of 5 seconds when reading responses..
        ssh.put_IdleTimeoutMs(5000)
        #  Authenticate using login/password:
        success = ssh.AuthenticatePw("sitproject", "project")
        if (success != True):
            print(ssh.lastErrorText())
            sys.exit()
        try:
            #print(os.path.dirname(dstfolder))
            ssh.quickCommand("mkdir -p "+str(os.path.dirname(dstfolder)), "utf8")
        except Exception as x:
            print(x)
        # Once the SSH object is connected and authenticated, we use it
        #  as the underlying transport in our SCP object.
        scp = chilkat.CkScp()
        success = scp.UseSsh(ssh)
        if (success != True):
            print(scp.lastErrorText())
            sys.exit()
        success = scp.UploadFile(localPath, dstfolder)
        if (success != True):
            print(scp.lastErrorText())
            sys.exit()
        print("SCP upload file success.")
        #  Disconnect
        ssh.Disconnect()

    """
        Fonction de capture du flux Vidéo - TODO
    """
    def makeVideoDrone(self, VideoName = "VideoDrone", Intervention = 1, Extension = "jpeg"):
        try:
            print("Flux vidéo ...")
            w = gtk.gdk.get_default_root_window()
            sz = w.get_size()
            print ("The size of the window is %d x %d" % sz)
            pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
            pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
            if (pb != None):
                # Le temps actuel de la prise de photos
                datepicture = str(datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%Z"))
                racine = "./"
                suffix =  str(Intervention)+"/"+str(VideoName) + "." + str(Extension)
                filename = racine + suffix
                # Crée le fichier avec son arboresence même s'il n'existe pas
                if not os.path.exists(os.path.dirname(filename)):
                    try:
                        os.makedirs(os.path.dirname(filename))
                    except OSError as exc:  # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise
                # Sauvegarde de la photo prise avec l'extension indiquée
                pb.save(filename, str(Extension))
                print "Video saved to " + os.path.basename(filename)
                """
                Découpage de la vidéo de -10% des marges
                """
                im = Image.open(str(filename))
                im_size = im.size
                #print im_size
                # (1366, 768)
                cp_large = int(im_size[0] * 0.10)
                cp_haut = int(im_size[1] * 0.10)
                #print cp_large
                #print cp_haut
                left = cp_large
                top = cp_haut
                width = im_size[0] - cp_large
                height = im_size[1] - cp_haut
                # Create Box
                box = (left, top, left + width, top + height)
                # Crop Image
                area = im.crop(box)
                # Save Image
                print area.size
                area.save(filename, str(Extension))
                self.sendToTheServer(filename, suffix)
            else:
                print "Unable to get the Video."
        except Exception as x:
            print(x)
    """

    def make_video(images, outimg=None, fps=5, size=None,
                   is_color=True, format="XVID"):
        
        
        import imread
        from cv2 import VideoWriter, VideoWriter_fourcc, resize
        fourcc = VideoWriter_fourcc(*format)
        vid = None
        for image in images:
            if not os.path.exists(image):
                raise FileNotFoundError(image)
            img = imread(image)
            if vid is None:
                if size is None:
                    size = img.shape[1], img.shape[0]
                vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)
            if size[0] != img.shape[1] and size[1] != img.shape[0]:
                img = resize(img, size)
            vid.write(img)
        vid.release()
        return vid
    """


    """
    TESTS DE NOTRE MODULE
    """

if __name__ == '__main__':
    #Création d'un objet dronepicture
    dronepic = DronePicture()
    #Génére un screeshot et l'envoi automatiquement vers le serveur apache
    #valeur = dronepic.getPicture()
    while True:
        dronepic.getPicture()
        dronepic.makeVideoDrone()
        #Pause
        time.sleep(5)
    #valeur est un objet json du Photo dans la base NodeJS
    #print(valeur)