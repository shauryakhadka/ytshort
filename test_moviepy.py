# test_moviepy.py
# Simple script to verify moviepy can be imported inside the container

try:
    from moviepy.editor import ImageClip
    print('moviepy import succeeded')
except Exception as e:
    print('moviepy import failed:', e)
