import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageOps
from inky.auto import auto

# Load Inky Impression 7.3" display
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Load Bible verses from JSON (list of strings in "Book Chapter:Verse - text" format)
BIBLE_VERSES_FILE = "bible_verses.json"


def load_verses():
    """Load Bible verses from JSON file."""
    try:
        with open(BIBLE_VERSES_FILE, "r", encoding="utf-8") as file:
            verses = json.load(file)
        return verses  # verses is a list of strings
    except Exception as e:
        print(f"Error loading Bible verses: {e}")
        return []


def get_random_verse(verses):
    """Get a random Bible verse from the loaded data."""
    if not verses:
        return "No verses found.", "Please check the JSON file."
    verse_line = random.choice(verses)
    # Expecting format: "Book Chapter:Verse - text"
    try:
        reference, verse_text = verse_line.split(" - ", 1)
    except ValueError:
        reference = ""
        verse_text = verse_line
    return reference, verse_text


def display_verse():
    """Render the Bible verse and additional graphics onto the E-Ink display."""
    # Load a random verse
    verses = load_verses()
    reference, verse_text = get_random_verse(verses)

    # Create the canvas
    img = Image.new("P", (inky_display.width, inky_display.height), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)

    # Load fonts (using DejaVu fonts; adjust paths if needed)
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    font_blessed = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    font_symbols = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)

    # ---------------------------
    # Top Middle: Display Red Dove
    # ---------------------------
    try:
        dove = Image.open("dove.png").convert("RGBA")
        dove.thumbnail((50, 50))  # Resize to approx. 50x50 pixels

        # Optional: Tint the dove red if it's not already red.
        # One approach: convert to grayscale then colorize.
        gray = ImageOps.grayscale(dove)
        # Create a red image and composite using the alpha channel of the dove.
        red_dove = ImageOps.colorize(gray, black="black", white="red")
        dove = red_dove.convert("RGBA")

        dove_x = (inky_display.width - dove.width) // 2  # Center horizontally
        dove_y = 10  # 10 pixels from the top
        img.paste(dove, (dove_x, dove_y), dove)
    except Exception as e:
        print(f"Error loading dove image: {e}")

    # ---------------------------
    # Top Right: Draw Three Cross Symbols
    # ---------------------------
    cross_text = "✝  ✝  ✝"
    cross_width, cross_height = draw.textsize(cross_text, font=font_symbols)
    cross_x = inky_display.width - cross_width - 10  # 10px from right edge
    cross_y = 10  # 10px from top
    draw.text((cross_x, cross_y), cross_text, inky_display.BLACK, font=font_symbols)

    # ---------------------------
    # Center: Bible Verse Text (Reference and Verse)
    # ---------------------------
    full_text = f"{reference}\n\n{verse_text}"
    max_text_width = inky_display.width - 40  # 20px padding on each side

    # Simple word-wrap
    lines = []
    for paragraph in full_text.split("\n"):
        words = paragraph.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width, _ = draw.textsize(test_line, font=font_body)
            if test_width <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")  # add an empty line between paragraphs
    if lines and lines[-1] == "":
        lines.pop()

    # Center the text block vertically
    line_height = font_body.getsize("Ay")[1] + 5
    text_block_height = len(lines) * line_height
    start_y = (inky_display.height - text_block_height) // 2
    for i, line in enumerate(lines):
        line_width, _ = draw.textsize(line, font=font_body)
        x = (inky_display.width - line_width) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, inky_display.BLACK, font=font_body)

    # ---------------------------
    # Bottom: "Blessed Day" Message in Bold Blue
    # ---------------------------
    blessed_message = "Blessed Day"
    # Use blue if supported; if not, you might use red or black.
    blue = (0, 0, 255)  # This is an RGB tuple for blue.
    blessed_width, blessed_height = draw.textsize(blessed_message, font=font_blessed)
    blessed_x = (inky_display.width - blessed_width) // 2
    blessed_y = inky_display.height - blessed_height - 10
    draw.text((blessed_x, blessed_y), blessed_message, blue, font=font_blessed)

    # ---------------------------
    # Update the Display
    # ---------------------------
    inky_display.set_image(img)
    inky_display.show()


if __name__ == "__main__":
    display_verse()
