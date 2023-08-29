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
        output = ""
        payload_chunks = split_payload(args.payload)
        generator = CSSGenerator(args.selectors)

        print(generator.selectors)
        
        # for chunk in payload_chunks:
        #     output += format_rgb_chunk(chunk)

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
