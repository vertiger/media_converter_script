#!/usr/bin/python

import enzyme
import fnmatch
import glob
import pygtk, gtk
import shutil
import subprocess
import os

dialog = gtk.FileChooserDialog(title='Please select a directory with movies', action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))

response = dialog.run()
if response == gtk.RESPONSE_OK:
    print dialog.get_filename(), 'selected'
else:
    quit()
dirname = dialog.get_filename()
dialog.destroy()

matches = []
for root, dirnames, filenames in os.walk(dirname):
    for filename in fnmatch.filter(filenames, '*.mkv'):
        matches.append(os.path.join(root, filename))

for mfile in matches:
    try:
        with open(mfile, 'rb') as f:
            mkv = enzyme.MKV(f)
    except enzyme.exceptions.MalformedMKVError:
        print("Malformed MKV: \"{}\"".format(mfile))
        raise
    if 'AVC' in mkv.video_tracks[0].codec_id or 'HEVC' in mkv.video_tracks[0].codec_id:
        continue
    print("convert file \"{}\"".format(mfile))
    print(mkv)
    audio_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.audio_tracks, start=1)]
    audio_arg = "--audio-copy-mask aac --audio-fallback av_aac -a {} -E {}".format(','.join(audio_tracks), ','.join(['copy' for _ in audio_tracks]))
    subtitle_tracks = ['{}'.format(idx) for idx, _ in enumerate(mkv.subtitle_tracks, start=1)]
    if subtitle_tracks:
        subtitle_arg = "-s {}".format(','.join(subtitle_tracks))
    else:
        subtitle_arg = ""
    quality = 20
    if mkv.video_tracks[0].width > 700:
        quality = 21
    if mkv.video_tracks[0].width > 1200:
        quality = 22
    if mkv.video_tracks[0].width > 1800:
        quality = 23
    target_file = os.path.join('/tmp', os.path.basename(mfile))
    command = "HandBrakeCLI -i \"{}\" -o \"{}\" -O --preset=\"High Profile\" --h264-level 4.0 --x264-preset slow --quality {} {} {} --keep-display-aspect".format(
        mfile, target_file, quality, audio_arg, subtitle_arg)
    print(command)
    try:
        subprocess.call(command, shell=True)
        print("copy file \"{}\" to \"{}\"".format(target_file, mfile))
        shutil.copyfile(target_file, mfile)
    finally:
        if os.path.exists(target_file):
            print("delete file \"{}\"".format(target_file))
            os.remove(target_file)

