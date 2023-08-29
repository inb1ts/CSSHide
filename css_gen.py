import random

class CSSGenerator:

    def __init__(self, selector_filename):
        self.selectors = []

        with open(f"./wordlists/{selector_filename}", "r") as selectors_file:
            self.selectors += [selector.rstrip() for selector in selectors_file]


    def format_rgb_chunk(payload_chunk) -> str:
        vals = [val for val in payload_chunk]

        # Pad the chunk to 3 if it's the last one
        if len(vals) < 3:
            vals += ['0'] * (3 - len[vals])

        return f"rbg({vals[0]}, {vals[1]}, {vals[2]})\n"

    def format_hex_chunk(payload_chunk) -> str:
        return f"#{payload_chunk.hex()}\n"
    
    def gen_color(self, color):
        return f"color: {color}\n"
    
    def gen_background_color(color):
        return f"background-color: {color}\n"
    
    def gen_background(color):
        return f"background: {color}\n"
    
    def gen_border(color):
        style = random.choice(["none", "dotted", "inset", "dashed", "groove", "outset", "hidden", "solid", "ridge"])
        width = random.choice(["thin", "medium", "thick", "1px", "2px", "3px", "4px"])
        return f"border: {style}, {width}, {color}\n"
    
    def gen_outline(color):
        style = random.choice(["none", "dotted", "inset", "dashed", "groove", "outset", "hidden", "solid", "ridge"])
        width = random.choice(["thin", "medium", "thick", "1px", "2px", "3px", "4px"])
        return f"outline: {style}, {width}, {color}\n"
    
    def gen_border_color(color_one, color_two, color_three, color_four):
        return f"border-color: {color_one}, {color_two}, {color_three}, {color_four}\n"
    
    def gen_linear_gradient(color_one, color_two, color_three, color_four):
        degree = random.random(0, 360)
        return f"background: linear-gradient({degree}deg, {color_one}, {color_two}, {color_three}, {color_four})\n"
    
    def gen_radial_gradient(color_one, color_two, color_three, color_four):
        return f"background: radial-gradient(circle, {color_one}, {color_two}, {color_three}, {color_four})\n"