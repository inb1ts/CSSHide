#!/usr/bin/env python

import argparse
import sys

from css_gen import CSSGenerator

def split_payload(file_name):
    with open(file_name, "rb") as payload_file:
        while chunk := payload_file.read(3):
            yield chunk

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [PAYLOAD_FILE] [ARGS]",
        description="CSSHide encodes a payload in CSS colour values. Supports either rbg or hex CSS colour formats, and minified/normal output."
    )

    parser.add_argument('payload', help="The file containing the payload you want to encode")
    parser.add_argument("-s", "--selectors", default="selectors.txt")
    parser.add_argument("-f", "--format", default="rgb", choices=["rgb", "hex"])
    parser.add_argument("-m", "--minify", default="true", choices=["true", "false"])
    parser.add_argument("-o", "--outfile", default="style.css")

    return parser

if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    
    try:
        # Setup
        output = ""
        payload_chunks = split_payload(args.payload)
        css_gen = CSSGenerator(args.selectors)

        # Output generation loop
        counter = 0
        queue_quad = False
        quad = []
        for chunk in payload_chunks:
            if (len(quad) == 4):
                output += css_gen.random_attrib_quad(*quad)
                quad = []
                queue_quad = False

            if (counter == 4):
                queue_quad = True
                counter = 0

            if (queue_quad):
                quad.append(css_gen.format_rgb_chunk(chunk))
            else:
                rbg_color = css_gen.format_rgb_chunk(chunk)
                output += css_gen.random_attrib_singular(rbg_color)
                counter += 1

    except Exception as err:
        print(f"Error encoding payload file {args.payload}: {err}")
        sys.exit(1)

    print(output)




    # try:
    #     with open(args.outfile, "w") as output_file:
    #         output_file.write(output)
    # except Exception as err:
    #     print(f"Error writing output file {args.payload}: {err}")
    #     sys.exit(1)
