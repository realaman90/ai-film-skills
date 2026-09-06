"""Build the aligned music bed: eras music up to the turn, a hard stop (silence + sub pulse), then the calm section.
Usage: python3 align_music.py <turn_seconds> <total_seconds>"""
import subprocess, sys, json, os
SRC=os.environ.get('MUSIC_SRC','bgmusic_eras.mp3'); OUT=os.environ.get('MUSIC_OUT','bgmusic_eras_aligned.mp3')
P='./assets/audio'
turn=float(sys.argv[1]); total=float(sys.argv[2])
src=f'{P}/'+SRC; out=f'{P}/'+OUT
CALM_FROM=float(os.environ.get('CALM_FROM','48.5'))
gap=1.6          # hard-stop hold before the groove returns
calm_len=total-turn-gap+3
CALM_TO=float(os.environ.get('CALM_TO','75.4')); seg=CALM_TO-CALM_FROM; X=2.0
n=max(1, int((calm_len + X) // (seg - X)) + 1)   # how many copies of the calm section, crossfaded, cover calm_len
calm_chain="".join(f"[0:a]atrim={CALM_FROM}:{CALM_TO},asetpts=PTS-STARTPTS[c{i}];" for i in range(n))
if n>1:
    xf=f"[c0][c1]acrossfade=d={X}:c1=tri:c2=tri[x1];" + "".join(f"[x{i-1}][c{i}]acrossfade=d={X}:c1=tri:c2=tri[x{i}];" for i in range(2,n))
    last=f"x{n-1}"
else:
    xf=""; last="c0"
fc=(f"[0:a]atrim=0:{turn:.2f},afade=t=out:st={turn-0.12:.2f}:d=0.12,asetpts=PTS-STARTPTS[a];"
    + calm_chain + xf +
    f"[{last}]atrim=0:{calm_len:.2f},afade=t=in:st=0:d=0.8,asetpts=PTS-STARTPTS[c];"
    f"anullsrc=r=44100:cl=stereo,atrim=0:{gap:.2f}[s];"
    f"[1:a]adelay=600|600,apad=whole_dur={gap:.2f}[p];[s][p]amix=inputs=2:normalize=0[gapmix];"
    f"[a][gapmix][c]concat=n=3:v=0:a=1[out]")
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,"-i",f"{P}/sub_pulse.mp3","-filter_complex",fc,"-map","[out]","-c:a","libmp3lame","-q:a","2",out],check=True)
d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",out],capture_output=True,text=True).stdout.strip())
print(f"aligned music: {d:.1f}s, stop at {turn:.2f}s, groove resumes at {turn+gap:.2f}s")
