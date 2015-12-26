import enzyme
import glob
import subprocess
import os.path


for mfile in glob.iglob("/run/user/1000/gvfs/smb-share:server=ds415plus.local,share=video/movies/*/*.mkv"):
    try:
        with open(mfile, 'rb') as f:
            mkv = enzyme.MKV(f)
        if 'AVC' not in mkv.video_tracks[0].codec_id:
            print(mfile)
            print(mkv)
            audio_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.audio_tracks, start=1)]
            audio_arg = "--audio-fallback av_aac -a {} -E {}".format(','.join(audio_tracks), ','.join(['copy' for _ in audio_tracks]))
            subtitle_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.subtitle_tracks, start=1)]
            if subtitle_tracks:
                subtitle_arg = "-s {}".format(','.join(subtitle_tracks))
            else:
                subtitle_arg = ""
            command = "HandBrakeCLI -i '{}' -o '{}' -O --preset='High Profile' --h264-level 5.2 --x264-preset slow {} {} --keep-display-aspect --cfr".format(
                mfile, os.path.basename(mfile), audio_arg, subtitle_arg)
            print(command)
            subprocess.call(command, shell=True)
    except enzyme.exceptions.MalformedMKVError:
        print("Malformed MKV: {}".format(mfile))
        raise

