def parse_mp3_parameters(mp3_file):
    import mutagen.mp3

    mp3_info = mutagen.mp3.MP3(mp3_file)

    format_ = mp3_info.info.bitrate_mode
    channels = mp3_info.info.channels
    rate = mp3_info.info.sample_rate
    duration = mp3_info.info.length

    return format_, channels, rate, duration


# 示例用法
mp3_file = "demo.mp3"
print(mp3_file)
format_, channels, rate, duration = parse_mp3_parameters(mp3_file)
print("Format:", format_)
print("Channels:", channels)
print("Sample Rate:", rate)
print("Duration:", duration)

mp3_file = "recording.mp3"
print(mp3_file)
format_, channels, rate, duration = parse_mp3_parameters(mp3_file)
print("Format:", format_)
print("Channels:", channels)
print("Sample Rate:", rate)
print("Duration:", duration)
