from re import compile

# BPM marks are assumed to always be at the start of a line
bpm_re = compile(r"^\((?P<bpm>\d+[.]?\d*)\)")
length_divider_re = compile(r"^{(?P<length_divider>\d+)}")

tap_note_re = compile(r"^(?P<location>[1-8])(?P<flags>[b$x]{1,2})?$")

hold_note_re = compile(r"^(?P<location>[1-8])h(?P<break>b)?(?P<ex_note>x)?\[#(?P<duration>\d+.\d{3})]$")

slide_star_pattern = r"(?P<start_location>[1-8])(?P<break_star>b)?(?P<ex_note>x)?(?P<omit_star>\?)?"

slide_path_pattern = (
    # Grand V's are not directly supported, but can be emulated with two connected straight slides
    r"(?:-(?P<grand_v_midpoint>[1-8])-(?P<grand_v_end_location>[1-8])"
    r"|(?P<slide_pattern>pp|qq|[-<>qpszvw])(?P<end_location>[1-8]))"

    r"\[(?P<delay>\d+.\d{3})##(?P<duration>\d+.\d{3})](?P<break_slide>b)?"
)

combined_slide_path_pattern = r"(?P<slide_path>(?P<is_multi_slide>\*?)" + slide_path_pattern + r")+"

slide_path_re = compile(r"^" + slide_path_pattern + "$")

full_slide_note_re = compile(r"^" + slide_star_pattern + slide_path_pattern + "$")

combined_slide_note_re = compile(r"^" + slide_star_pattern + combined_slide_path_pattern + r"$")

slide_patterns_re = compile(r"(?P<slide_pattern>[-<>qpszvVw]|pp|qq)")