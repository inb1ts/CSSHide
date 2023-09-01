import random
import sys

VARIABLE_ELEMENTS = {
    "main": ["fg", "bg"],
    "body": ["fg", "bg", "border"],
    "scrollbar": ["fg", "bg"],
    "progressBar": ["fg", "bg", "selected", "blend"],
    "toolbar": ["icon", "icon-bg", "icon-fg", "hover", "hover-bg", "border", "box"],
    "sidebar": ["narrow", "narrow-bg", "toolbar", "toolbar-bg", "border", "box"],
    "button": ["hover", "selected", "inactive", "pressed"],
    "toggled": ["btn", "btn-bg", "btn-fg"],
    "dropdown": ["btn", "btn-bg", "btn-fg"],
    "field": ["bg", "fg", "border"],
    "item": ["bg", "fg", "border", "box", "active", "inactive", "hover"],
    "treeitem": ["hover", "selected", "bg", "selected-bg"],
    "thumbnail": ["selected", "selected-bg", "border"],
    "dialog": ["btn", "btn-bg", "border", "border-active", "hover"],
    "header": ["bg", "fg", "seperator"],
    "footer": ["bg", "fg", "border"],
    "box": ["bg", "fg", "active", "inactive", "hover"],
    "container": ["bg", "fg", "active", "inactive", "hover"],
}


class CSSPayloadEncoder:
    def __init__(self, format):
        self.elements = VARIABLE_ELEMENTS
        if format == "rgb":
            self.format_func = self.format_rgb_chunk
        elif format == "hex":
            self.format_func = self.format_hex_chunk

    # Random selection methods
    def random_attrib_singular(self, color) -> str:
        method = random.choice(
            [
                self.gen_color,
                self.gen_background_color,
                self.gen_background,
                self.gen_border,
                self.gen_outline,
            ]
        )
        return method(color)

    def random_attrib_quad(self, color_one, color_two, color_three, color_four) -> str:
        method = random.choice(
            [self.gen_border_color, self.gen_linear_gradient, self.gen_radial_gradient]
        )
        return method(color_one, color_two, color_three, color_four)

    # Format payload chunk methods
    def format_rgb_chunk(self, payload_chunk) -> str:
        vals = [val for val in payload_chunk]

        # Pad the chunk to 3 if it's the last one
        if len(vals) < 3:
            vals += ["0"] * (3 - len[vals])

        return f"rgb({vals[0]} {vals[1]} {vals[2]})"

    def format_hex_chunk(self, payload_chunk) -> str:
        return f"#{payload_chunk.hex()}"

    # Main generator methods
    def gen_css_variables_attributes(self, payload_chunks) -> list[str]:
        payload_as_variables = []
        try:
            variable_colors = []
            for _ in range(random.randint(10, 50)):
                variable_colors.append(next(payload_chunks))

            payload_as_variables = self.gen_variables_section(variable_colors)
        except Exception as err:
            print(f"[!] Error generating CSS variables: {err}")
            sys.exit(1)

        return payload_as_variables

    def gen_css_random_attributes(self, payload_chunks) -> list[str]:
        payload_as_random = []
        counter = 0
        queue_quad = False
        rand_quad = random.randint(2, 8)
        quad = []

        try:
            for chunk in payload_chunks:
                if len(quad) == 4:
                    payload_as_random.append(self.random_attrib_quad(*quad))
                    quad = []
                    queue_quad = False

                if counter == rand_quad:
                    queue_quad = True
                    rand_quad = random.randint(2, 8)
                    counter = 0

                if queue_quad:
                    quad.append(self.format_func(chunk))
                else:
                    rbg_color = self.format_func(chunk)
                    payload_as_random.append(self.random_attrib_singular(rbg_color))
                    counter += 1

            # Handle chunks running out whilst queuing a quad
            if queue_quad and len(quad) != 0:
                for color in quad:
                    payload_as_random.append(self.random_attrib_singular(color))

        except Exception as err:
            print(f"[!] Error generating CSS blocks: {err}")
            sys.exit(1)

        return payload_as_random

    def gen_variables_section(self, variable_colors) -> list[str]:
        # Shuffle elements so they are different every time
        variables_output = []
        element_list = list(self.elements.items())
        random.shuffle(element_list)
        shuffled_elements = dict(element_list)
        element_names = list(shuffled_elements.keys())

        variable_counter = 0
        i = 0
        while True:
            # Failsafe against infinite loop
            if i == len(element_names):
                break

            # Because the length of payload chunks is randomised and we've shuffled the elements
            # we need a second counter to determine how many chunks are left to encode
            for attr_index in shuffled_elements[element_names[i]]:
                if variable_counter >= len(variable_colors):
                    return variables_output

                color = self.format_func(variable_colors[variable_counter])
                variables_output.append(
                    f"--{element_names[i]}-{attr_index}-color: {color}"
                )
                variable_counter += 1
            i += 1

        return variables_output

    # Format CSS attribute methods
    def gen_color(self, color):
        return f"color: {color}"

    def gen_background_color(self, color):
        return f"background-color: {color}"

    def gen_background(self, color):
        return f"background: {color}"

    def gen_border(self, color):
        style = random.choice(
            [
                "none",
                "dotted",
                "inset",
                "dashed",
                "groove",
                "outset",
                "hidden",
                "solid",
                "ridge",
            ]
        )
        width = random.choice(["thin", "medium", "thick", "1px", "2px", "3px", "4px"])
        return f"border: {style} {width} {color}"

    def gen_outline(self, color):
        style = random.choice(
            [
                "none",
                "dotted",
                "inset",
                "dashed",
                "groove",
                "outset",
                "hidden",
                "solid",
                "ridge",
            ]
        )
        width = random.choice(["thin", "medium", "thick", "1px", "2px", "3px", "4px"])
        return f"outline: {style} {width} {color}"

    def gen_border_color(self, color_one, color_two, color_three, color_four):
        return f"border-color: {color_one} {color_two} {color_three} {color_four}"

    def gen_linear_gradient(self, color_one, color_two, color_three, color_four):
        degree = random.randrange(0, 360)
        return f"background: linear-gradient({degree}deg {color_one} {color_two} {color_three} {color_four})"

    def gen_radial_gradient(self, color_one, color_two, color_three, color_four):
        return f"background: radial-gradient(circle {color_one} {color_two} {color_three} {color_four})"
