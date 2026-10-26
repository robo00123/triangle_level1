"""python sync_work.py narration.mp3   (or the parts in order)  ->  work_audio.mp3 and work_cues.json"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
import sync
import work_script

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__ + "\n" + sync.__doc__)
    sync.run(work_script, sys.argv[1:], HERE, "work")
