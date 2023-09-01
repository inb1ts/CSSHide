#!/usr/bin/env python

import argparse
import sys

from css_payload_encoder import CSSPayloadEncoder
from css_generator import CSSGenerator


def split_payload(file_name):
    with open(file_name, "rb") as payload_file:
        while chunk := payload_file.read(3):
            yield chunk


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [PAYLOAD_FILE] [ARGS]",
        description="CSSHide encodes a payload in CSS colour values. Supports either rbg or hex CSS colour formats, and minified/normal output.",
    )

    parser.add_argument(
        "payload", help="The file containing the payload you want to encode"
    )
    parser.add_argument(
        "-s", "--selectors", default="selectors.txt", help="wordlist of CSS selectors"
    )
    parser.add_argument(
        "-f",
        "--format",
        default="rgb",
        choices=["rgb", "hex"],
        help="format of CSS color",
    )
    parser.add_argument(
        "--minify",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="minify output to save space",
    )
    parser.add_argument(
        "-o", "--outfile", default="style.css", help="name of output file to create"
    )

    return parser


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    # Banner
    print(
        """

 ██████╗███████╗███████╗██╗  ██╗██╗██████╗ ███████╗
██╔════╝██╔════╝██╔════╝██║  ██║██║██╔══██╗██╔════╝
██║     ███████╗███████╗███████║██║██║  ██║█████╗  
██║     ╚════██║╚════██║██╔══██║██║██║  ██║██╔══╝  
╚██████╗███████║███████║██║  ██║██║██████╔╝███████╗
 ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
                                                   
CSSHide v1.0.0 - Hiding in plain style.                                   
by inbits @ https://inbits-sec.com/
              """
    )

    css_output = ""
    payload_as_variables = []
    payload_as_random = []
    payload_encoder = CSSPayloadEncoder(args.format)
    css_generator = CSSGenerator(args.selectors)

    # Read payload file and return generator that yields 3 bytes at a time
    try:
        print(f"[i] Reading payload from {args.selectors}...")
        payload_chunks = split_payload(args.payload)
    except Exception as err:
        print(f"[!] Error loading payload file {args.payload}: {err}")
        sys.exit(1)

    # Encode payload into a list of CSS variables and a list of random CSS attributes
    print(f"[i] Encoding payload as {args.format} attributes...")
    payload_as_variables = payload_encoder.gen_css_variables_attributes(payload_chunks)
    payload_as_random = payload_encoder.gen_css_random_attributes(payload_chunks)

    # Construct full CSS contents
    print("[i] Generating full CSS contents...")
    css_output = css_generator.generate(
        payload_as_variables, payload_as_random, args.minify
    )

    # Write output to file
    print(f"[i] Writing CSS output to {args.outfile}...")
    try:
        with open(args.outfile, "w") as output_file:
            output_file.write(css_output)
    except Exception as err:
        print(f"[!] Error writing output file {args.payload}: {err}")
        sys.exit(1)
