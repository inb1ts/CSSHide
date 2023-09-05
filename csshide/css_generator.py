import random
import rcssmin
import string

class CSSGenerator:
    def __init__(self, selector_filename):
        self.selectors = []

        with open(f"./wordlists/{selector_filename}", "r") as selectors_file:
            self.selectors += [selector.rstrip() for selector in selectors_file]

        random.shuffle(self.selectors)

    def generate(self, payload_variables, payload_random, minify) -> str:
        css_output = ""

        css_output += self.generate_variable_block(payload_variables)
        css_output += self.generate_main_block(payload_random)

        if minify:
            css_output = rcssmin.cssmin(css_output)

        return css_output

    def generate_variable_block(self, payload_variables) -> str:
        variable_block = ":root {\n"

        for var in payload_variables:
            variable_block += f"\t{var};\n"

        variable_block += "}\n\n"

        return variable_block

    def generate_main_block(self, payload_random) -> str:
        main_block = ""
        dangling_value = False
        selector_index = 0
        filler_counter = 0
        rand_filler = random.randint(3, 6)

        while payload_random:
            if (selector_index >= len(self.selectors)):
                self._generate_extra_selectors()

            main_block += f"{self.selectors[selector_index]} {{\n"

            # Add multiple encoded attributes, check start of previous attributes to
            # avoid duplicate properties within the same selector
            used_attr_prefixes = []
            while True:
                if len(payload_random) == 0:
                    break

                attribute = payload_random.pop(0)

                used_in_block = attribute.startswith(tuple(used_attr_prefixes))
                if used_in_block == False:
                    main_block += f"\t{attribute};\n"

                    used_attr_prefixes.append(attribute[:3])
                    filler_counter += 1

                    if filler_counter == rand_filler:
                        for filler_attribute in self.random_css_filler():
                            main_block += f"\t{filler_attribute};\n"
                            filler_counter = 0
                            rand_filler = random.randint(1, 6)
                elif used_in_block and len(payload_random) == 0:
                    dangling_value = True
                    break
                else:
                    # Add it back to the queue to be used in the next block
                    payload_random.insert(0, attribute)
                    break

            main_block += "}\n\n"

            selector_index += 1

            # Handle the case where the last property is a duplicate in a block
            if dangling_value:
                main_block += f"{self.selectors[selector_index]} {{\n"
                main_block += f"\t{attribute};\n"
                main_block += "}\n\n"

        return main_block

    def random_css_filler(self) -> list[str]:
        method = random.choice(
            [
                self._filler_positional,
                self._filler_sizes,
                self._filler_space,
                self._filler_background,
                self._filler_font,
                self._filler_list,
                self._filler_text,
                self._filler_border,
            ]
        )
        return method()

    def _filler_positional(self) -> str:
        properties = random.choice(
            [["top", "right"], ["top", "left"], ["right", "bottom"], ["left", "bottom"]]
        )
        px_one = random.randint(0, 400)
        px_two = random.randint(0, 400)

        return [
            f"{properties[0]}: {px_one}px",
            f"{properties[1]}: {px_two}px",
        ]

    def _filler_sizes(self) -> list[str]:
        properties = random.choice(
            [
                ["width", "height"],
                ["max-width", "max-height"],
                ["min-width", "min-height"],
            ]
        )
        px_one = random.randint(0, 400)
        px_two = random.randint(0, 400)

        return [
            f"{properties[0]}: {px_one}px",
            f"{properties[1]}: {px_two}px",
        ]

    def _filler_space(self) -> list[str]:
        px_one = random.randint(1, 50)
        px_two = random.randint(1, 50)

        return [f"margin: {px_one}px", f"padding: {px_two}px"]

    def _filler_background(self) -> list[str]:
        pos = random.choice(["contain", "cover"])
        px_one = random.randint(25, 250)
        px_two = random.randint(25, 250)

        return [
            f"background-position: {px_one}px {px_two}px",
            f"background-size: {pos}",
        ]

    def _filler_font(self) -> list[str]:
        px = random.randint(1, 20)
        weight = random.choice(["normal", "bold", "lighter", "bolder"])

        return [
            f"font-size: {px}px",
            f"font-weight: {weight}",
        ]

    def _filler_list(self) -> list[str]:
        type = random.choice(["space-counter", "disc", "circle"])
        pos = random.choice(
            [
                "inside",
                "outside",
            ]
        )

        return [
            f"list-style-type: {type}",
            f"list-style-image: none",
            f"list-style-position: {pos}",
        ]

    def _filler_text(self) -> list[str]:
        align = random.choice(["centre", "left", "right", "start"])
        decoration = random.choice(["underline", "overline", "none"])

        return [
            f"text-align: {align}",
            f"text-decoration: {decoration}",
        ]

    def _filler_border(self) -> list[str]:
        px_radius = random.randint(5, 50)
        px_width = random.randint(1, 6)
        style = random.choice(["dashed", "dotted", "solid", "double", "hidden"])

        return [
            f"border-radius: {px_radius}px",
            f"border-width: {px_width}px",
            f"border-style: {style}",
        ]

    # Should only be needed for huge payloads
    def _generate_extra_selectors(self):
        randomstr_selectors = []
        random_suffix = ''.join([random.choice(string.ascii_lowercase) for _ in range(4)])

        for selector in self.selectors:
            randomstr_selectors.append(f"{selector}-{random_suffix}")

        self.selectors += randomstr_selectors