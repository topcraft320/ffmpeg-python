import ffmpeg
import os


TEST_DIR = os.path.dirname(__file__)
TEST_INPUT_FILE = os.path.join(TEST_DIR, 'dummy.mp4')
TEST_OUTPUT_FILE = os.path.join(TEST_DIR, 'dummy2.mp4')


def test_fluent_equality():
    base1 = ffmpeg.file_input('dummy1.mp4')
    base2 = ffmpeg.file_input('dummy1.mp4')
    base3 = ffmpeg.file_input('dummy2.mp4')
    t1 = base1.trim(10, 20)
    t2 = base1.trim(10, 20)
    t3 = base1.trim(10, 30)
    t4 = base2.trim(10, 20)
    t5 = base3.trim(10, 20)
    assert t1 == t2
    assert t1 != t3
    assert t1 == t4
    assert t1 != t5


def test_fluent_concat():
    base = ffmpeg.file_input('dummy.mp4')
    trimmed1 = base.trim(10, 20)
    trimmed2 = base.trim(30, 40)
    trimmed3 = base.trim(50, 60)
    concat1 = ffmpeg.concat(trimmed1, trimmed2, trimmed3)
    concat2 = ffmpeg.concat(trimmed1, trimmed2, trimmed3)
    concat3 = ffmpeg.concat(trimmed1, trimmed3, trimmed2)
    concat4 = ffmpeg.concat()
    concat5 = ffmpeg.concat()
    assert concat1 == concat2
    assert concat1 != concat3
    assert concat4 == concat5


def test_fluent_output():
    ffmpeg \
        .file_input('dummy.mp4') \
        .trim(10, 20) \
        .file_output('dummy2.mp4')


def test_fluent_complex_filter():
    in_file = ffmpeg.file_input('dummy.mp4')
    return ffmpeg \
        .concat(
            in_file.trim(10, 20),
            in_file.trim(30, 40),
            in_file.trim(50, 60)
        ) \
        .file_output('dummy2.mp4')


def test_repr():
    in_file = ffmpeg.file_input('dummy.mp4')
    trim1 = ffmpeg.trim(in_file, 10, 20)
    trim2 = ffmpeg.trim(in_file, 30, 40)
    trim3 = ffmpeg.trim(in_file, 50, 60)
    concatted = ffmpeg.concat(trim1, trim2, trim3)
    output = ffmpeg.file_output(concatted, 'dummy2.mp4')
    assert repr(in_file) == "file_input(filename='dummy.mp4')"
    assert repr(trim1) == "trim(end_frame=20,setpts='PTS-STARTPTS',start_frame=10)"
    assert repr(trim2) == "trim(end_frame=40,setpts='PTS-STARTPTS',start_frame=30)"
    assert repr(trim3) == "trim(end_frame=60,setpts='PTS-STARTPTS',start_frame=50)"
    assert repr(concatted) == "concat()"
    assert repr(output) == "file_output(filename='dummy2.mp4')"


def test_get_args_simple():
    out_file = ffmpeg.file_input('dummy.mp4').file_output('dummy2.mp4')
    assert out_file.get_args() == ['-i', 'dummy.mp4', 'dummy2.mp4']


def _get_complex_filter_example():
    in_file = ffmpeg.file_input(TEST_INPUT_FILE)
    concatted = ffmpeg.concat(
        ffmpeg.trim(in_file, 10, 20),
        ffmpeg.trim(in_file, 30, 40),
        ffmpeg.trim(in_file, 50, 60),
    )
    out = ffmpeg.file_output(concatted, TEST_OUTPUT_FILE)
    return ffmpeg.overwrite_output(out)


def test_get_args_complex_filter():
    out = _get_complex_filter_example()
    assert ffmpeg.get_args(out) == [
        '-i', TEST_INPUT_FILE,
        '-filter_complex', 
            '[0]trim=start_frame=10:end_frame=20,setpts=PTS-STARTPTS[v0];' \
            '[0]trim=start_frame=30:end_frame=40,setpts=PTS-STARTPTS[v1];' \
            '[0]trim=start_frame=50:end_frame=60,setpts=PTS-STARTPTS[v2];' \
            '[v0][v1][v2]concat=n=3[v3]',
        '-map', '[v3]', TEST_OUTPUT_FILE,
        '-y',
    ]


def test_run():
    ffmpeg.run(_get_complex_filter_example())
