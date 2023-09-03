#חבילות רלוונטיות
import _thread
import PIL.Image
import numpy as np
import tkinter.ttk
from time import time, sleep
from os import  listdir, rename
from tkinter.filedialog import askdirectory
from sys import exc_info
#Sigmoid
def sigmoid(x,deriv=False):           #יצירת פונקציית הסיגמואיד
    if (deriv==True):
        return x*(1-x)
    return 1/(1+np.exp(-x))
#Classifier
def classifer(directory,polished_data):
    syn0=np.load('syn0.npy')
    syn1=np.load('syn1.npy')
    l1=sigmoid(np.dot(polished_data,syn0))
    l2=sigmoid(np.dot(l1,syn1))
    file_names=[]
    for file_name in listdir(directory):                #בדיקה של שם הקובץ
        file_names.append(file_name)
    for a in range(len(l2)):
        if (l2[a]>=0.5):
            rename(directory+"/"+file_names[a],"tables/"+file_names[a])
        if (l2[a]<0.5):
            rename(directory+"/"+file_names[a],"rest/"+file_names[a])
#עיבוד התמונה
def processing(directory,file_name,done,polished_data):
    image=0
    image=np.asarray(PIL.Image.open(directory + "/" + file_name))
    h=len(image)
    w=len(image[1])
    if (len(image[0][0])==4):             #if the image is RGBA
        b=[]
        for l in range(h):
            a=[]
            for c in range(w):
                a.append(image[l,c][:3])
            b.append(a)
        image=b
    if (len(image[0][0])==3):
    # יוצר מטריצות נוחות לעיבוד
        trs=[]
        tgs=[]
        tbs=[]
        rs=[]
        gs=[]
        bs=[]
        for a in range(h):
            for b in range(w):
                trs.append(image[a][b][0])
                tgs.append(image[a][b][1])
                tbs.append(image[a][b][2])
        for a in range(0,int(len(trs)/w)):
            rs.append(trs[a*w:(a+1)*w])
            gs.append(tgs[a*w:(a+1)*w])
            bs.append(tbs[a*w:(a+1)*w])
        layers=np.array([rs,gs,bs])
    # יוצר היסטוגרמה בעבור כלל התמונה
        histo=[]
        groups=4
        no_zone=[]
        for a in range (0,3):
            histo=np.histogram(layers[a],bins=groups)
            maxi=np.max(histo[0])
            for b in range(0,groups):
                if (histo[0][b]==maxi):
                    no_zone.append(np.array([histo[1][b],histo[1][b+1]]))  
    # מוצא את השורות והטורים של הטבלה
        hor_ls=[]
        ver_ls=[]
        hor_ln=0
        ver_ln=0
        h=len(image)
        w=len(image[1])
        for a in range(0,3):    #עבור כל אחד מהצבעים
            l=0        #מתחיל עבור צבע מהשורה הראשונה את הבדיקה
            while (l<(h-2)):  #horizonal line detection
                while ((l in hor_ls)&(l<(h-2))):
                    l+=1
                c=0
                while (c<w):
                    if (len(hor_ls)==hor_ln):      #אם השורה הנוכחית לא התגלתה כבר בתור קו
                        if ((layers[a][l][c]<no_zone[a][0])|(layers[a][l][c]>no_zone[a][1])):
                            if (((layers[a][l][c]/255)**2>(layers[a][l+1][c]/255))|
                                ((layers[a][l][c]/255)<(layers[a][l+1][c]/255)**2)):#אם יש חשד שזה קו
                                T=c
                                pixels=[]
                                lng=0
                                while (T<w):
                                    pixels.append(layers[a][l][T])
                                    if ((np.mean((pixels-np.median(pixels))**2)>289)|
                                        (((layers[a][l][T]-np.median(pixels))**2)>5000)):   #אם זה לא קו
                                        break
                                    else:
                                        lng+=1    
                                    if ((lng>w/4)&((np.median(pixels)<no_zone[a][0])|
                                                   (np.median(pixels)>no_zone[a][1]))):   #horizonal line definition
                                        hor_ls.append(l)
                                        break
                                    T+=1   
                    else:
                        hor_ln+=1
                        break
                    c+=1
                l+=1
        for a in range(0,3):    #עבור כל אחד מהצבעים בחיפוש טורים
            c=0        #מתחיל עבור צבע מהשורה הראשונה את הבדיקה
            while (c<(w-2)):  #horizonal line detection
                while ((c in ver_ls)&(c<(w-2))):
                    c+=1
                l=0
                while (l<h):
                    if (len(ver_ls)==ver_ln):      #אם הטור הנוכחי לא התגלתה כבר בתור קו
                        if ((layers[a][l][c]<no_zone[a][0])|(layers[a][l][c]>no_zone[a][1])):
                            if (((layers[a][l][c]/255)**2>(layers[a][l][c+1]/255))|
                                ((layers[a][l][c]/255)<(layers[a][l][c+1]/255)**2)):#אם יש חשד שזה קו
                                s=l
                                pixels=[]
                                lng=0
                                while (s<h):
                                    pixels.append(layers[a][s][c])
                                    if ((np.mean((pixels-np.median(pixels))**2)>289)|
                                        (((layers[a][s][c]-np.median(pixels))**2)>5000)):   #אם זה לא קו
                                        break
                                    else:
                                        lng+=1    
                                    if ((lng>h/6)&((np.median(pixels)<no_zone[a][0])|
                                                   (np.median(pixels)>no_zone[a][1]))):   #horizonal line definition
                                        ver_ls.append(c)
                                        break
                                    s+=1   
                    else:
                        ver_ln+=1
                        break
                    l+=1
                c+=1
    # מסדר לפי גודל ומוחק כפילויות
        hor_ls=sorted(hor_ls)
        ver_ls=sorted(ver_ls)
        i=0
        while (i<(len(hor_ls)-2)):
            lng=0
            if (hor_ls[i+1]-hor_ls[i]==1):                    #אם מספרי השורות הם עוקבים   
                while (hor_ls[i+lng+1]-hor_ls[i+lng]==1):            #כל עוד מספרי השורות הם עוקבים
                    lng+=1
                    if (i+lng+2>len(hor_ls)):
                        break
                if (lng<(h/50)):                          #אם זה קו שמן
                    n=i
                    x=0
                    while (x<lng):       
                        if (n!=i+np.int(lng/2)+(lng%2)):    #אם זה לא אמצע הקו
                            hor_ls.remove(hor_ls[n])
                        else:
                            n+=1
                        x+=1
                else:                                       #אם זו שורה צבעונית עם צבע רקע
                    x=0
                    while (x<(lng-1)):
                        try:
                            hor_ls.remove(hor_ls[i+1])
                        except:
                            i+=1
                            pass
                        x+=1
            else:
                i+=1
        if (len(hor_ls)>1):
            if (hor_ls[-1]-hor_ls[-2]==1):
                hor_ls.remove(hor_ls[-2])
        i=0                                                #אותו דבר אבל על טורים
        while (i<(len(ver_ls)-2)):
            lng=0
            if (ver_ls[i+1]-ver_ls[i]==1):                    #אם מספרי הטורים הם עוקבים   
                while (ver_ls[i+lng+1]-ver_ls[i+lng]==1):            #כל עוד מספרי הטורים הם עוקבים
                    lng+=1
                    if (i+lng+2>len(ver_ls)):
                        break
                if (lng<(h/50)):                          #אם זה קו שמן
                    n=i
                    x=0
                    while (x<lng):       
                        if (n!=i+np.int(lng/2)+(lng%2)):    #אם זה לא אמצע הקו
                            ver_ls.remove(ver_ls[n])
                        else:
                            n+=1
                        x+=1
                else:                                       #אם זו שורה צבעונית עם צבע רקע
                    x=0
                    while (x<(lng-1)):
                        try:
                            hor_ls.remove(hor_ls[i+1])
                        except:
                            i+=1
                            pass
                        x+=1
            else:
                i+=1
        if (len(ver_ls)>1):
            if (ver_ls[-1]-ver_ls[-2]==1):
                ver_ls.remove(ver_ls[-2])
    # בודק אם הקו בצבע שונה מצבע תא הטבלה
        hor_box=[]
        for b in range(0,(len(hor_ls)-1)):             #בעבור כל שורה
            rbox=[]
            gbox=[]
            bbox=[]
            if (len(ver_ls)>1):
                for l in range(hor_ls[b],hor_ls[b+1]):   #בעבור כל שורות הפיקסלים שמרכיבות את השורה
                    for c in range(ver_ls[0],ver_ls[-1]):#בעבור כל הטורי הפיקסלים שמרכיבים את השורה
                        rbox.append(layers[0][l][c])
                        gbox.append(layers[1][l][c])
                        bbox.append(layers[2][l][c])
            hor_box.append(np.array([rbox,gbox,bbox]))
        hor_lines=[]
        for b in range(0,len(hor_ls)):             #בעבור כל שורה
            rl=[]
            gl=[]
            bl=[]
            if (len(ver_ls)>1):
                for c in range(ver_ls[0],ver_ls[-1]):#בעבור כל הטורי הפיקסלים שמרכיבים את השורה
                    rl.append(layers[0][hor_ls[b]][c])
                    gl.append(layers[1][hor_ls[b]][c])
                    bl.append(layers[2][hor_ls[b]][c])
            hor_lines.append(np.array([rl,gl,bl]))
        i=0
        hor_deltas=[]
        hor_lns_unis=[]
        while (i<len(hor_ls)):                   #בודק אם השורות דומות לרקע התאים
            if ((i!=0)&(i!=(len(hor_ls)-1))&(len(hor_ls)>1)):           #אם זו לא השורה הראשונה ולא השורה האחרונה תבדוק אם התא שלפני והתא שאחרי
                hor_deltas.append((np.median(hor_lines[i][0])-np.median(hor_box[i][0])/2-np.median(hor_box[i-1][0])/2)**2+
                                 (np.median(hor_lines[i][1])-np.median(hor_box[i][1])/2-np.median(hor_box[i-1][1])/2)**2+
                                 (np.median(hor_lines[i][2])-np.median(hor_box[i][2])/2-np.median(hor_box[i-1][2])/2)**2)
            elif (len(hor_ls)>1):
                if (i==0):              #אם זו השורה הראשונה
                    hor_deltas.append((np.median(hor_lines[i][0])-np.median(hor_box[i][0]))**2+
                                      (np.median(hor_lines[i][1])-np.median(hor_box[i][1]))**2+
                                      (np.median(hor_lines[i][2])-np.median(hor_box[i][2]))**2)
                else:                    #אם זו השורה האחרונה
                    hor_deltas.append((np.median(hor_lines[i][0])-np.median(hor_box[i-1][0]))**2+
                                      (np.median(hor_lines[i][1])-np.median(hor_box[i-1][1]))**2+
                                      (np.median(hor_lines[i][2])-np.median(hor_box[i-1][2]))**2)
            hor_lns_unis.append(np.median((np.median(hor_lines[i])-hor_lines)**2))                 #בודק את אחידות צבע הקוים
            i+=1
        hor_delta=np.median(hor_deltas)                #קלט ללמידת המכונה
        hor_lns_uni=np.median(hor_lns_unis)            #קלט ללמידת המכונה
        ver_box=[]
        for b in range(0,(len(ver_ls)-1)):             #בעבור כל טור
            rbox=[]
            gbox=[]
            bbox=[]
            if (len(hor_ls)>1):
                for c in range(ver_ls[b],ver_ls[b+1]):   #בעבור כל טורי הפיקסלים שמרכיבים את הטור
                    for l in range(hor_ls[0],hor_ls[-1]):#בעבור כל שורות הפיקסלים שמרכיבות את הטור
                        rbox.append(layers[0][l][c])
                        gbox.append(layers[1][l][c])
                        bbox.append(layers[2][l][c])
            ver_box.append(np.array([rbox,gbox,bbox]))
        ver_lines=[]
        for b in range(0,len(ver_ls)):             #בעבור כל טור
            rl=[]
            gl=[]
            bl=[]
            if (len(hor_ls)>1):
                for c in range(hor_ls[0],hor_ls[-1]):#בעבור כל שורות הפיקסלים שמרכיבות את הטור
                    rl.append(layers[0][c][ver_ls[b]])
                    gl.append(layers[1][c][ver_ls[b]])
                    bl.append(layers[2][c][ver_ls[b]])
            ver_lines.append(np.array([rl,gl,bl]))
        i=0
        ver_deltas=[]
        ver_lns_unis=[]
        while (i<len(ver_ls)):                       #בודק אם השורות דומות לרקע התאים
            if ((i!=0)&(i!=(len(ver_ls)-1))&(len(ver_ls)>1)):             #אם זו לא הטור הראשון ולא הטור האחרון תבדוק אם התא שמימין והתא שמשמאל
                ver_deltas.append((np.median(ver_lines[i][0])-np.median(ver_box[i][0])/2-np.median(ver_box[i-1][0])/2)**2+
                                  (np.median(ver_lines[i][1])-np.median(ver_box[i][1])/2-np.median(ver_box[i-1][1])/2)**2+
                                  (np.median(ver_lines[i][2])-np.median(ver_box[i][2])/2-np.median(ver_box[i-1][2])/2)**2)
            elif (len(ver_ls)>1):
                if (i==0):                  #אם זו הטור הראשון
                    ver_deltas.append((np.median(ver_lines[i][0])-np.median(ver_box[i][0]))**2+
                                      (np.median(ver_lines[i][1])-np.median(ver_box[i][1]))**2+
                                      (np.median(ver_lines[i][2])-np.median(ver_box[i][2]))**2)
                else:                     #אם זו הטור האחרון
                    ver_deltas.append((np.median(ver_lines[i][0])-np.median(ver_box[i-1][0]))**2+
                                     (np.median(ver_lines[i][1])-np.median(ver_box[i-1][1]))**2+
                                     (np.median(ver_lines[i][2])-np.median(ver_box[i-1][2]))**2)
            ver_lns_unis.append(np.median((np.median(ver_lines[i])-ver_lines)**2))                   #בודק את אחידות צבע הקוים
            i+=1    
        ver_delta=np.median(ver_deltas)                #קלט ללמידת המכונה
        ver_lns_uni=np.median(ver_lns_unis)            #קלט ללמידת המכונה
    # אחידות רוחב השורות והטורים
        uni_hor=[]
        for i in range (len(hor_ls)-1):
            uni_hor.append((hor_ls[i+1]-hor_ls[i])/h)
        uniform_hor=np.median((uni_hor-np.median(uni_hor))**2)                       #קלט ללמידת המכונה
        uni_ver=[]
        for i in range (len(ver_ls)-1):
            uni_ver.append((ver_ls[i+1]-ver_ls[i])/w)
        uniform_ver=np.median((uni_ver-np.median(uni_ver))**2)                       #קלט ללמידת המכונה
    # גודל הטבלה יחסית לגודל הדף 
        if ((len(hor_ls)>0)&(len(ver_ls)>0)):
            h_covarage=(hor_ls[-1]-hor_ls[0])/h           #קלט ללמידת המכונה
            w_covarage=(ver_ls[-1]-ver_ls[0])/w           #קלט ללמידת המכונה
        else:
            h_covarage=0
            w_covarage=0
    # מכין מטריצה ללמידת מכונה
        polished_data.append(np.array([len(hor_ls),len(ver_ls),hor_delta,ver_delta,
                                           hor_lns_uni,ver_lns_uni,uniform_hor,uniform_ver,h_covarage,w_covarage]))
        for i in range(len(polished_data[0])):                 #converts all the NaN to int
            if (np.isnan(polished_data[done][i])):
                if (i==2|i==3):
                    polished_data[done][i]=0
                else:
                    polished_data[done][i]=65025
        return polished_data
    
    
    
#GUI
root=tkinter.Tk()
root.title("Table Recognizer")
root.geometry('800x200')
root.progress=tkinter.ttk.Progressbar(root,orient="horizontal",length=200,mode="determinate")
label1=tkinter.Label(root,text="Please choose unclassified directory")
def behind():
    sleep(0.001)
    root.update()
def update(directory):
    polished_data=[]
    done=0
    total=0
    try:
        for file_name in listdir(directory):                #בודק כמה תמונות יש בתקייה
            total+=1
        start=time()
        for file_name in listdir(directory):                #מעבד כל תמונה בתקייה
            processing(directory,file_name,done,polished_data)
            done+=1
            root.progress['value']=done/total*100
            if (((time()-start)>60)&((time()-start)<3600)):
                label1['text']="estimated time: "+str(int((time()-start)/(done/total)/60))+" minutes  & "+str(int((time()-start)/(done/total)%60))+" seconds   "
            else:
                label1['text']="estimated time: "+str((time()-start)/(done/total))+" seconds   "
            root.update_idletasks()                         #מעדכן את פלט התוכנה
        classifer(directory,polished_data)
        label1['text']="Done"
    except:
        label1['text']=exc_info()[1]
def helloCallBack():
    directory=askdirectory()
    _thread.start_new_thread(update,(directory,))
    _thread.start_new_thread(behind,())
    label1['text']="runing..."
tkinter.Button(text ="Please choose input directory", command = helloCallBack).pack()
root.progress.pack()
label1.pack()
tkinter.Label(root, text="All rights reserved to Gon Eyal©").pack()
root.mainloop()