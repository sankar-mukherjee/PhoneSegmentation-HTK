# AUTHORS: SANKAR MUKHERJEE AND ALDO PASTORE


#######!!!!!!!!!####### GO TO THE MAIN AT THE END OF THIS FILE AND REPLACE PATHS WITH YOUR PATHS#######!!!!!!!!!#######

import subprocess
import shutil
from shutil import copyfile
from distutils.dir_util import copy_tree
import fileinput
import sys
import os
from  scipy import signal
import soundfile as sf



def res_wav(audio, new_rate=16000):
    cwd=os.getcwd().replace('\\','/')
    path=cwd+'/train/raw/'
    data, srate =sf.read(path+audio)
    secs = len(data)/srate
    samps = int(secs*new_rate)
    data_res = signal.resample(data, samps)
    sf.write(path.replace('raw','wav')+audio, data_res, new_rate, subtype='PCM_16')

def makedir(name):
    if os.path.exists("./HMM/"+name) == False:
        os.mkdir("./HMM/"+name)



def segmentate(raw_audio,prompts,dictionary,out_path):
    ######INITIALIZE FILES##############
    if os.path.exists('./train/raw'):
      shutil.rmtree('./train/raw')

    if os.path.exists('./train/wav'):
      shutil.rmtree('./train/wav')

    if os.path.exists('./train/mfc'):
      shutil.rmtree('./train/mfc')

    copy_tree(raw_audio, "./train/raw")
    os.mkdir('./train/wav')
    os.mkdir('./train/mfc')


    copyfile(prompts,'./train/prompts')
    copyfile(dictionary,'./train/main_dict')

    if os.path.exists('./codetrain.scp'):
        os.remove('./codetrain.scp')
    if os.path.exists('./codetrain_wav.scp'):
        os.remove('./codetrain_wav.scp')
    if os.path.exists('./dict'):
        os.remove('./dict')
    if os.path.exists('./dict-tri'):
        os.remove('./dict-tri')
    if os.path.exists('./dlog'):
        os.remove('./dlog')
    if os.path.exists('./flog'):
        os.remove('./flog')
    if os.path.exists('./fulllist'):
        os.remove('./fulllist')
    if os.path.exists('./monophones0'):
        os.remove('./monophones0')
    if os.path.exists('./monophones1'):
        os.remove('./monophones1')
    if os.path.exists('./phones0'):
        os.remove('./phones0')
    if os.path.exists('./phones1'):
        os.remove('./phones1')
    if os.path.exists('./stats'):
        os.remove('./stats')
    if os.path.exists('./T.mlf'):
        os.remove('./T.mlf')
    if os.path.exists('./T_aligned.mlf'):
        os.remove('./T_aligned.mlf')
    if os.path.exists('./Tfinal.mlf'):
        os.remove('./Tfinal.mlf')
    if os.path.exists('./tiedlist'):
        os.remove('./tiedlist')
    if os.path.exists('./train.scp'):
        os.remove('./train.scp')
    if os.path.exists('./tree.hed'):
        os.remove('./tree.hed')
    if os.path.exists('./trees'):
        os.remove('./trees')
    if os.path.exists('./triphones1'):
        os.remove('./triphones1')
    if os.path.exists('./wintri.mlf'):
        os.remove('./wintri.mlf')
    if os.path.exists('./wlist'):
        os.remove('./wlist')
    if os.path.exists('./words.mlf'):
        os.remove('./words.mlf')


    ########################################

    downsampling = 1

    if downsampling:
        if os.path.exists('conversion_list.txt'):
            os.remove('conversion_list.txt')

        cmd="""dir "./train/raw" /b >> conversion_list.txt """
        returned_value = subprocess.call(cmd, shell=True)

        fopen=open('conversion_list.txt')
        audiolist=fopen.readlines()
        N=len(audiolist)
        for i, audio_path in enumerate(audiolist):
            print('processing wav file '+str(i)+' of '+str(N))
            res_wav(audio_path.strip('\n'))


    copyfile('./train/prompts',  'prompts.new')#words in prompts must be without accents

    fopen=open('prompts.new','a')
    fopen.write('*/SYSTEM sent-end sent-start')
    fopen.close()

    cmd= "perl ./script/prompts2wlist prompts.new wlist"
    returned_value = subprocess.call(cmd, shell=True)

    os.remove('prompts.new')

    cmd = "HDMan -A -D -T 1 -m -g ./script/global.ded -w wlist -n monophones1 -i -l dlog dict ./train/main_dict"
    returned_value = subprocess.call(cmd, shell=True)  # excutes and returns the exit

    cmd= "perl ./script/prompts2mlf words.mlf ./train/prompts"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HLEd -A -D -T 1 -l * -d dict -i phones0.mlf ./script/mkphones0.led words.mlf "
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HLEd -A -D -T 1 -l * -d dict -i phones1.mlf ./script/mkphones1.led words.mlf"
    returned_value = subprocess.call(cmd, shell=True)

    if os.path.exists('./codetrain.scp'):
         os.remove('codetrain.scp')
    if os.path.exists('./codetrain_wav.scp'):
         os.remove('codetrain_wav.scp')

    cmd="""dir "./train/raw" /b >> codetrain_wav.scp""" #WAV NON CONTIENE NULLA ORA
    returned_value = subprocess.call(cmd, shell=True)

    for line in fileinput.input(['codetrain_wav.scp'], inplace=True):
         sys.stdout.write('./train/wav/{l}'.format(l=line).strip(' '))

    fi=open('codetrain_wav.scp','r')
    fo=open('codetrain.scp','w')
    fo2=open('train.scp','w')
    for line in fi.readlines():
         newl=line.strip().replace('wav','mfc')
         fo.write(line.strip()+'\t'+newl+'\n')
         fo2.write(newl+'\n')
    fi.close()
    fo.close()
    fo2.close()
    cmd="HCopy -A -D -T 1 -C ./config/wav_config -S codetrain.scp"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm0')

    cmd="HCompV -A -D -T 1 -C ./config/config -f 0.01 -m -S train.scp -M ./HMM/hmm0 ./addons/proto"
    returned_value = subprocess.call(cmd, shell=True)

    fopen=open('monophones1','r')
    phones_list=fopen.readlines()
    fout=open('monophones0','w')
    for ph in phones_list:
        ph=ph.replace('sp', '')
        if ph != '\n':
            fout.write(ph)

    fopen.close()
    fout.close()

    cmd="perl ./script/hmmdefs_create.pl"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm1')

    cmd="HERest -A -D -T 1 -C ./config/config -I phones0.mlf -t 250.0 150.0 1000.0 -S train.scp -H ./HMM/hmm0/macros -H ./HMM/hmm0/hmmdefs -M ./HMM/hmm1 monophones0"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm2')

    cmd="HERest -A -D -T 1 -C ./config/config -I phones0.mlf -t 250.0 150.0 1000.0 -S train.scp -H ./HMM/hmm1/macros -H ./HMM/hmm1/hmmdefs -M ./HMM/hmm2 monophones0"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm3')

    cmd="HERest -A -D -T 1 -C ./config/config -I phones0.mlf -t 250.0 150.0 1000.0 -S train.scp -H ./HMM/hmm2/macros -H ./HMM/hmm2/hmmdefs -M ./HMM/hmm3 monophones0"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm4')

    copyfile('./HMM/hmm3/macros',  './HMM/hmm4/macros')
    copyfile('./HMM/hmm3/hmmdefs',  './HMM/hmm4/hmmdefs')

    cmd="perl ./script/sp_Fix_HMM.pl"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm5')

    cmd="HHEd -A -D -T 1 -H ./HMM/hmm4/macros -H ./HMM/hmm4/hmmdefs -M ./HMM/hmm5 ./script/sil.hed monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm6')
    ####OK
    cmd="HERest -A -D -T 1 -C ./config/config  -I phones1.mlf -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm5/macros -H  ./HMM/hmm5/hmmdefs -M ./HMM/hmm6 monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm7')

    cmd="HERest -A -D -T 1 -C ./config/config  -I phones1.mlf -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm6/macros -H  ./HMM/hmm6/hmmdefs -M ./HMM/hmm7 monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HVite -A -D -T 1 -l * -o SWT -b sent-end -C ./config/config -H ./HMM/hmm7/macros -H ./HMM/hmm7/hmmdefs -i T_aligned.mlf -m -t 250.0 150.0 1000.0 -y lab -a -I words.mlf -S train.scp dict monophones1> HVite_log"
    returned_value = subprocess.call(cmd, shell=True) #####MAYBE SENT-END instead of sent-end??????????

    makedir('hmm8')

    cmd="HERest -A -D -T 1 -C ./config/config -I T_aligned.mlf -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm7/macros -H ./HMM/hmm7/hmmdefs -M ./HMM/hmm8 monophones1 "
    returned_value = subprocess.call(cmd, shell=True)

    ###OKOK

    makedir('hmm9')

    cmd="HERest -A -D -T 1 -C ./config/config -I T_aligned.mlf -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm8/macros -H ./HMM/hmm8/hmmdefs -M ./HMM/hmm9 monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HVite -A -D -T 1 -l * -o SW -b sent-end -C ./config/config -H ./HMM/hmm9/macros -H ./HMM/hmm9/hmmdefs -i T.mlf -m -t 250.0 150.0 1000.0 -y lab -a -I words.mlf -S train.scp dict monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HLEd -A -D -T 1 -n triphones1 -l * -i wintri.mlf ./script/mktri.led T_aligned.mlf"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="perl ./script/maketrihed monophones1 triphones1"
    returned_value = subprocess.call(cmd, shell=True)
    ###OKOK

    makedir('hmm10')

    cmd="HHEd -A -D -T 1 -H ./HMM/hmm9/macros -H ./HMM/hmm9/hmmdefs -M ./HMM/hmm10 ./script/mktri.hed monophones1"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm11')

    cmd="HERest  -A -D -T 1 -C ./config/config -I wintri.mlf -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm10/macros -H ./HMM/hmm10/hmmdefs -M ./HMM/hmm11 triphones1"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm12')

    cmd="HERest  -A -D -T 1 -C ./config/config -I wintri.mlf -t 250.0 150.0 3000.0 -s stats -S train.scp -H ./HMM/hmm11/macros -H ./HMM/hmm11/hmmdefs -M ./HMM/hmm12 triphones1"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HDMan -A -D -T 1 -b sp -n fulllist -g ./script/global.ded -l flog dict-tri ./train/main_dict"#####POSSIBILITY TO CHANGE DICT
    returned_value = subprocess.call(cmd, shell=True)

    copyfile('fulllist','fulllist1')
    fappend=open('fulllist1','a')
    fopen=open('triphones1','r')
    triph=fopen.readlines()
    fopen.close()
    for tr in triph:
        fappend.write(tr)
    fappend.close()

    cmd="perl ./script/fixfulllist.pl fulllist1 fulllist"
    returned_value = subprocess.call(cmd, shell=True)

    os.remove('fulllist1')

    copyfile('./question/question.hed','tree.hed')

    cmd="perl ./script/mkclscript.prl TB 350 monophones0 >> tree.hed"
    returned_value = subprocess.call(cmd, shell=True)

    fappend=open('tree.hed','a')
    fappend.write('TR 1\nAU "fulllist"\nCO "tiedlist"\nST "trees"')
    fappend.close()

    makedir('hmm13')

    cmd="HHEd -A -D -T 1 -H ./HMM/hmm12/macros -H ./HMM/hmm12/hmmdefs -M ./HMM/hmm13 tree.hed triphones1"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm14')

    cmd="HERest -A -D -T 1 -T 1 -C ./config/config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm13/macros -H ./HMM/hmm13/hmmdefs -M ./HMM/hmm14 tiedlist"
    returned_value = subprocess.call(cmd, shell=True)

    makedir('hmm15')

    cmd="HERest -A -D -T 1 -T 1 -C ./config/config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H ./HMM/hmm14/macros -H ./HMM/hmm14/hmmdefs -M ./HMM/hmm15 tiedlist"
    returned_value = subprocess.call(cmd, shell=True)

    cmd="HVite -A -D -T 1 -l *  -a -b sent-end -m -C ./config/config -H ./HMM/hmm15/macros -H ./HMM/hmm15/hmmdefs -m -t 250.0 150.0 1000.0 -I words.mlf  -i Tfinal.mlf -S train.scp dict tiedlist"
    returned_value = subprocess.call(cmd, shell=True)

    copyfile('Tfinal.mlf',out_path)

    shutil.rmtree('./train/raw')
    shutil.rmtree('./train/wav')
    shutil.rmtree('./train/mfc')




if __name__ == '__main__':

	xx = 'C:/Users/SMukherjee/Desktop/prova'

	#######REPLACE PATHS BELOW WITH YOUR PATHS#########
	####### WORDS IN DICTIONARY AND IN PROMPTS MUST BE WITHOUT ACCENT###### (example : change 'perchè' to 'perche')
	audio_folder=xx + '/wav'
	prompts_path=xx+'/prompts'
	dictionary_path=xx+'/main_dict'
	outpath=xx+'/segmentation.txt'
	
	segmentate(audio_folder,prompts_path,dictionary_path,outpath)
	