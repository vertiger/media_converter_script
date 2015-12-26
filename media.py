import enzyme
import glob
import shutil
import subprocess
import os


for mfile in glob.iglob("/run/user/1000/gvfs/smb-share:server=ds415plus.local,share=video/movies/*/*.mkv"):
    try:
        with open(mfile, 'rb') as f:
            mkv = enzyme.MKV(f)
    except enzyme.exceptions.MalformedMKVError:
        print("Malformed MKV: {}".format(mfile))
        raise
    if 'AVC' in mkv.video_tracks[0].codec_id:
        continue
    print("convert file '{}'".format(mfile))
    print(mkv)
    audio_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.audio_tracks, start=1)]
    audio_arg = "--audio-fallback av_aac -a {} -E {}".format(','.join(audio_tracks), ','.join(['copy' for _ in audio_tracks]))
    subtitle_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.subtitle_tracks, start=1)]
    if subtitle_tracks:
        subtitle_arg = "-s {}".format(','.join(subtitle_tracks))
    else:
        subtitle_arg = ""
    target_file = os.path.join('/tmp', os.path.basename(mfile))
    command = "HandBrakeCLI -i '{}' -o '{}' -O --preset='High Profile' --h264-level 5.2 --x264-preset slow {} {} --keep-display-aspect --cfr".format(
        mfile, target_file, audio_arg, subtitle_arg)
    print(command)
    try:
        subprocess.call(command, shell=True)
        print("copy file '{}' to '{}'".format(target_file, mfile))
        shutil.copyfile(target_file, mfile)
    finally:
        if os.path.exists(target_file):
            print("delete file '{}'".format(target_file))
            os.remove(target_file)

